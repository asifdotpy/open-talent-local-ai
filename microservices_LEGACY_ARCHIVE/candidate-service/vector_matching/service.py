"""Vector matching service using Neo4j for semantic search.
Handles candidate-job matching using vector similarity.
"""

import logging
import os
import time

from neo4j import Driver, GraphDatabase

from .embeddings import EmbeddingGenerator
from .models import CandidateEmbedding, JobEmbedding, MatchRequest, MatchResponse, MatchResult

logger = logging.getLogger(__name__)


class VectorMatchingService:
    """Service for matching candidates to jobs using vector similarity.
    Uses Neo4j vector index for fast semantic search.
    """

    def __init__(
        self,
        neo4j_uri: str = None,
        neo4j_username: str = None,
        neo4j_password: str = None,
        neo4j_database: str = "neo4j",
    ):
        """Initialize the vector matching service.

        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_username: Neo4j username
            neo4j_password: Neo4j password
            neo4j_database: Neo4j database name
        """
        self.uri = neo4j_uri or os.getenv("NEO4J_URI", "neo4j+s://4b63e239.databases.neo4j.io")
        self.username = neo4j_username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = neo4j_password or os.getenv("NEO4J_PASSWORD")
        self.database = neo4j_database

        self.driver: Driver | None = None
        self.embedding_gen = EmbeddingGenerator()

        logger.info(f"Initializing Neo4j connection to {self.uri}")
        self._connect()

    def _connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            # Verify connection
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j")

            # Ensure vector indexes exist
            self._ensure_vector_indexes()
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def _ensure_vector_indexes(self):
        """Create vector indexes for candidates and jobs if they don't exist."""
        with self.driver.session(database=self.database) as session:
            try:
                # Create vector index for candidates
                session.run(
                    """
                    CREATE VECTOR INDEX candidate_embeddings IF NOT EXISTS
                    FOR (c:Candidate)
                    ON c.embedding
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: 384,
                        `vector.similarity_function`: 'cosine'
                    }}
                """
                )

                # Create vector index for jobs
                session.run(
                    """
                    CREATE VECTOR INDEX job_embeddings IF NOT EXISTS
                    FOR (j:Job)
                    ON j.embedding
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: 384,
                        `vector.similarity_function`: 'cosine'
                    }}
                """
                )

                logger.info("Vector indexes created/verified successfully")
            except Exception as e:
                logger.warning(f"Error creating vector indexes (may already exist): {e}")

    def store_candidate_embedding(self, candidate: CandidateEmbedding) -> bool:
        """Store candidate embedding in Neo4j.

        Args:
            candidate: CandidateEmbedding object with embedding vector

        Returns:
            True if successful, False otherwise
        """
        if not candidate.embedding:
            logger.error("Candidate embedding is None")
            return False

        with self.driver.session(database=self.database) as session:
            try:
                session.run(
                    """
                    MERGE (c:Candidate {candidate_id: $candidate_id})
                    SET c.full_name = $full_name,
                        c.email = $email,
                        c.profile_text = $profile_text,
                        c.embedding = $embedding,
                        c.skills = $skills,
                        c.experience_years = $experience_years,
                        c.updated_at = datetime()
                """,
                    {
                        "candidate_id": candidate.candidate_id,
                        "full_name": candidate.full_name,
                        "email": candidate.email,
                        "profile_text": candidate.profile_text,
                        "embedding": candidate.embedding,
                        "skills": candidate.skills,
                        "experience_years": candidate.experience_years,
                    },
                )

                logger.info(f"Stored embedding for candidate {candidate.candidate_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to store candidate embedding: {e}")
                return False

    def store_job_embedding(self, job: JobEmbedding) -> bool:
        """Store job embedding in Neo4j.

        Args:
            job: JobEmbedding object with embedding vector

        Returns:
            True if successful, False otherwise
        """
        if not job.embedding:
            logger.error("Job embedding is None")
            return False

        with self.driver.session(database=self.database) as session:
            try:
                session.run(
                    """
                    MERGE (j:Job {job_id: $job_id})
                    SET j.title = $title,
                        j.description = $description,
                        j.embedding = $embedding,
                        j.required_skills = $required_skills,
                        j.experience_required = $experience_required,
                        j.updated_at = datetime()
                """,
                    {
                        "job_id": job.job_id,
                        "title": job.title,
                        "description": job.description,
                        "embedding": job.embedding,
                        "required_skills": job.required_skills,
                        "experience_required": job.experience_required,
                    },
                )

                logger.info(f"Stored embedding for job {job.job_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to store job embedding: {e}")
                return False

    def find_matching_candidates(self, request: MatchRequest) -> MatchResponse:
        """Find candidates that match a job description using vector similarity.

        Args:
            request: MatchRequest with job_id and search parameters

        Returns:
            MatchResponse with list of matching candidates
        """
        start_time = time.time()

        # Get job embedding
        job = self._get_job_embedding(request.job_id)
        if not job or not job.embedding:
            logger.error(f"Job {request.job_id} not found or has no embedding")
            return MatchResponse(job_id=request.job_id, total_candidates_searched=0, matches=[], search_time_ms=0)

        # Perform vector search
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                CALL db.index.vector.queryNodes('candidate_embeddings', $top_k, $job_embedding)
                YIELD node, score
                WHERE score >= $min_similarity
                RETURN node.candidate_id as candidate_id,
                       node.full_name as full_name,
                       node.skills as skills,
                       node.experience_years as experience_years,
                       score
                ORDER BY score DESC
            """,
                {
                    "top_k": request.top_k,
                    "job_embedding": job.embedding,
                    "min_similarity": request.min_similarity,
                },
            )

            matches = []
            for record in result:
                # Calculate skill match
                candidate_skills = set(record["skills"] or [])
                required_skills = set(job.required_skills or [])
                matched_skills = list(candidate_skills & required_skills)
                missing_skills = list(required_skills - candidate_skills)

                skill_match_score = len(matched_skills) / len(required_skills) if required_skills else 1.0

                # Check experience requirement
                experience_match = True
                if job.experience_required and record["experience_years"]:
                    experience_match = record["experience_years"] >= job.experience_required

                # Skip if skill match required but not met
                if request.require_skill_match and skill_match_score < 0.5:
                    continue

                # Calculate overall score (weighted combination)
                similarity_score = record["score"]
                overall_score = (
                    similarity_score * 60
                    + skill_match_score * 30  # 60% semantic similarity
                    + (10 if experience_match else 0)  # 30% skill match  # 10% experience
                )

                match = MatchResult(
                    candidate_id=record["candidate_id"],
                    job_id=request.job_id,
                    similarity_score=similarity_score,
                    skill_match_score=skill_match_score,
                    experience_match=experience_match,
                    overall_score=overall_score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                )
                matches.append(match)

        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        return MatchResponse(
            job_id=request.job_id,
            total_candidates_searched=len(matches),
            matches=matches,
            search_time_ms=round(search_time, 2),
        )

    def _get_job_embedding(self, job_id: str) -> JobEmbedding | None:
        """Retrieve job embedding from Neo4j."""
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                MATCH (j:Job {job_id: $job_id})
                RETURN j.job_id as job_id,
                       j.title as title,
                       j.description as description,
                       j.embedding as embedding,
                       j.required_skills as required_skills,
                       j.experience_required as experience_required
            """,
                {"job_id": job_id},
            )

            record = result.single()
            if not record:
                return None

            return JobEmbedding(
                job_id=record["job_id"],
                title=record["title"],
                description=record["description"],
                embedding=record["embedding"],
                required_skills=record["required_skills"] or [],
                experience_required=record["experience_required"],
            )

    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
