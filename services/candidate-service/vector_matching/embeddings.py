"""Embedding generation using sentence-transformers.
Generates 384-dimensional embeddings for semantic search.
"""

import logging

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for candidate profiles and job descriptions.
    Uses 'all-MiniLM-L6-v2' model (384 dimensions, fast and efficient).
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedding generator.

        Args:
            model_name: Name of the sentence-transformer model to use
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")

    def generate_candidate_embedding(
        self,
        full_name: str,
        skills: list[str],
        experience: list[str],
        education: list[str],
        summary: str = "",
    ) -> list[float]:
        """Generate embedding for a candidate profile.

        Args:
            full_name: Candidate's full name
            skills: List of skills
            experience: List of work experience descriptions
            education: List of education descriptions
            summary: Optional profile summary

        Returns:
            List of floats representing the embedding vector
        """
        # Construct profile text
        profile_parts = [
            f"Name: {full_name}",
            f"Skills: {', '.join(skills)}",
            f"Experience: {' | '.join(experience)}",
            f"Education: {' | '.join(education)}",
        ]

        if summary:
            profile_parts.insert(0, f"Summary: {summary}")

        profile_text = " ".join(profile_parts)

        # Generate embedding
        embedding = self.model.encode(profile_text, convert_to_numpy=True)

        return embedding.tolist()

    def generate_job_embedding(
        self,
        title: str,
        description: str,
        required_skills: list[str],
        responsibilities: list[str] = None,
    ) -> list[float]:
        """Generate embedding for a job description.

        Args:
            title: Job title
            description: Full job description
            required_skills: List of required skills
            responsibilities: Optional list of responsibilities

        Returns:
            List of floats representing the embedding vector
        """
        # Construct job text
        job_parts = [
            f"Title: {title}",
            f"Description: {description}",
            f"Required Skills: {', '.join(required_skills)}",
        ]

        if responsibilities:
            job_parts.append(f"Responsibilities: {' | '.join(responsibilities)}")

        job_text = " ".join(job_parts)

        # Generate embedding
        embedding = self.model.encode(job_text, convert_to_numpy=True)

        return embedding.tolist()

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for arbitrary text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def calculate_similarity(
        self, embedding1: list[float] | np.ndarray, embedding2: list[float] | np.ndarray
    ) -> float:
        """Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0 to 1)
        """
        # Convert to numpy arrays if needed
        vec1 = np.array(embedding1) if isinstance(embedding1, list) else embedding1
        vec2 = np.array(embedding2) if isinstance(embedding2, list) else embedding2

        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        # Ensure value is between 0 and 1
        return max(0.0, min(1.0, float(similarity)))
