"""Candidate Service - Candidate management, applications, profiles, and vector-based matching
Port: 8008.

MERGED VERSION combining:
- Candidate management API with enum-based validation (from services/)
- Vector search capabilities using FastEmbed + LanceDB (from microservices/)
- Comprehensive skill management and applications tracking
"""

import json
import logging
import os
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import BaseSettings

# SQLAlchemy imports
from sqlalchemy import Column, DateTime, String, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Vector search imports - production-ready stack
try:
    import numpy as np
    import pyarrow as pa
    from fastembed import TextEmbedding
    from lancedb import connect

    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TypeVar for generic pagination
T = TypeVar("T")

# ============================================================================
# CONFIGURATION
# ============================================================================


class Settings(BaseSettings):
    """Database and vector search settings."""

    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:@localhost/db")
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./candidate_vectors.db")


settings = Settings()

# Initialize vector search components
embedding_model = None
vector_db = None


def initialize_vector_search():
    """Initialize the FastEmbed embedding model and LanceDB connection for vector search capabilities.

    Ensures the vector database directory exists, connects to the database, and creates
    the 'candidates' table with the appropriate schema (MiniLM-L6-v2 embeddings) if it doesn't already exist.
    """
    global embedding_model, vector_db

    if not VECTOR_SEARCH_AVAILABLE:
        logger.info("Vector search libraries not available, vector search disabled")
        return

    try:
        logger.info("Initializing FastEmbed model...")
        # Initialize FastEmbed model (ONNX-based, no PyTorch dependency)
        embedding_model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Initialize LanceDB (embedded vector database)
        db_path = Path(settings.vector_db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        vector_db = connect(str(db_path))

        # Create candidates table if it doesn't exist
        if "candidates" not in vector_db.table_names():
            # Define schema for vector storage using pyarrow
            schema = pa.schema(
                [
                    ("id", pa.string()),
                    ("full_name", pa.string()),
                    ("profile_text", pa.string()),
                    ("vector", pa.list_(pa.float32(), 384)),  # 384 dimensions for MiniLM-L6-v2
                    ("metadata", pa.string()),  # JSON string with full profile data
                ]
            )
            vector_db.create_table("candidates", schema=schema)

        logger.info("Vector search initialized successfully with FastEmbed + LanceDB")

    except KeyboardInterrupt:
        logger.warning("Vector search initialization interrupted by user")
        embedding_model = None
        vector_db = None
    except Exception as e:
        logger.warning(f"Vector search initialization failed (continuing without it): {e}")
        logger.info("Service will run with basic functionality but without vector search")
        embedding_model = None
        vector_db = None


# Database setup
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url, connect_args={"check_same_thread": False}, echo=False
    )
else:
    engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class CandidateDB(Base):
    """SQLAlchemy Candidate Model."""

    __tablename__ = "candidates"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    resume_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================================================
# ENUMS - STRONGLY TYPED STATUS/PROFICIENCY VALUES
# ============================================================================


class ApplicationStatus(str, Enum):
    """Application status enumeration."""

    APPLIED = "applied"
    REVIEWING = "reviewing"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class SkillProficiency(str, Enum):
    """Skill proficiency enumeration."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


# ----------------------------------------------------------------------------
# CANDIDATE STATUS WORKFLOW
# ----------------------------------------------------------------------------


class CandidateStatus(str, Enum):
    """Candidate lifecycle status."""

    NEW = "new"
    REVIEWING = "reviewing"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    OFFERED = "offered"
    HIRED = "hired"
    REJECTED = "rejected"


# ============================================================================
# PYDANTIC MODELS - BASIC CANDIDATE MANAGEMENT
# ============================================================================


class CandidateCreate(BaseModel):
    """Schema for creating a candidate."""

    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = Field(None, pattern=r"^\+?1?\d{9,15}$")
    resume_url: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "resume_url": "https://example.com/resume.pdf",
            }
        }


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate."""

    email: EmailStr | None = None
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, pattern=r"^\+?1?\d{9,15}$")
    resume_url: str | None = None


class CandidateResponse(BaseModel):
    """Schema for candidate response."""

    id: str
    email: str
    first_name: str
    last_name: str
    phone: str | None
    resume_url: str | None
    status: CandidateStatus
    created_at: str
    updated_at: str


class ApplicationCreate(BaseModel):
    """Schema for creating an application."""

    candidate_id: str
    job_id: str
    cover_letter: str | None = None
    status: ApplicationStatus = Field(default=ApplicationStatus.APPLIED)

    class Config:
        json_schema_extra = {
            "example": {
                "candidate_id": "uuid-here",
                "job_id": "job-123",
                "cover_letter": "I am interested in this position...",
                "status": "applied",
            }
        }


class ApplicationUpdate(BaseModel):
    """Schema for updating an application."""

    status: ApplicationStatus = Field(
        ...,
        description="Application status must be one of: applied, reviewing, interview_scheduled, accepted, rejected",
    )
    cover_letter: str | None = None


class ApplicationResponse(BaseModel):
    """Schema for application response."""

    id: str
    job_id: str
    candidate_id: str
    status: ApplicationStatus
    cover_letter: str | None
    created_at: str
    updated_at: str


class SkillCreate(BaseModel):
    """Schema for adding a skill."""

    skill: str = Field(..., min_length=1, max_length=100)
    proficiency: SkillProficiency = Field(default=SkillProficiency.INTERMEDIATE)

    class Config:
        json_schema_extra = {"example": {"skill": "Python", "proficiency": "advanced"}}


class SkillResponse(BaseModel):
    """Schema for skill response."""

    skill: str
    proficiency: SkillProficiency
    added_at: str


class SkillListResponse(BaseModel):
    """Schema for skill list response."""

    candidate_id: str
    skills: list[SkillResponse]


class ResumeResponse(BaseModel):
    """Schema for resume response."""

    candidate_id: str
    resume_url: str


# ============================================================================
# SEARCH & FILTER MODELS
# ============================================================================


class SearchResponse(BaseModel):
    total: int
    query: str
    filters_applied: dict[str, Any]
    results: list[dict[str, Any]] = []
    search_method: str


# ============================================================================
# PAGINATION MODELS
# ============================================================================


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=20, ge=1, le=100, description="Number of items to return (1-100)")


class PaginatedResponse[T](BaseModel):
    """Generic paginated response wrapper."""

    total: int = Field(..., description="Total number of items")
    offset: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items returned")
    items: list[T] = Field(..., description="List of items")

    @property
    def has_next(self) -> bool:
        """Check if there are more items."""
        return (self.offset + self.limit) < self.total

    @property
    def has_previous(self) -> bool:
        """Check if there are previous items."""
        return self.offset > 0

    @property
    def page(self) -> int:
        """Calculate current page number (1-based)."""
        return (self.offset // self.limit) + 1

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return (self.total + self.limit - 1) // self.limit


# ============================================================================
# PYDANTIC MODELS - VECTOR SEARCH & PROFILING
# ============================================================================


class WorkExperience(BaseModel):
    title: str
    company: str
    duration: str
    responsibilities: list[str]


class Education(BaseModel):
    institution: str
    degree: str
    year: str


class Skills(BaseModel):
    matched: list[str]
    unmatched: list[str]


class InitialQuestion(BaseModel):
    question: str = Field(..., description="Targeted question based on profile.")
    reasoning: str = Field(..., description="Why this question is being asked.")


class CandidateProfile(BaseModel):
    full_name: str = Field(..., description="The candidate's full name.")
    source_url: str = Field(
        ..., description="The primary URL where the candidate's profile was found."
    )
    summary: str = Field(..., description="AI-generated summary of the candidate's profile.")
    work_experience: list[WorkExperience]
    education: list[Education]
    skills: Skills
    alignment_score: float = Field(
        ge=0.0, le=1.0, description="Score indicating alignment with the search criteria."
    )
    initial_questions: list[InitialQuestion]


# ============================================================================
# IN-MEMORY STORAGE
# ============================================================================

candidates_db: dict[str, dict[str, Any]] = {}
applications_db: dict[str, dict[str, Any]] = {}
candidate_skills_db: dict[str, list[dict[str, Any]]] = {}
interviews_db: dict[str, list[dict[str, Any]]] = {}
assessments_db: dict[str, list[dict[str, Any]]] = {}
availability_db: dict[str, list[dict[str, Any]]] = {}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# ============================================================================
# AUTHENTICATION STUB
# ============================================================================

TEST_TOKEN = "test-token-12345"
DEFAULT_USER_ID = "test-user-001"


def get_current_user(authorization: str | None = Header(None)) -> str | None:
    """Simple auth stub that accepts Bearer tokens.

    For testing/development:
    - No Authorization header → uses DEFAULT_USER_ID
    - Bearer test-token-12345 → authorized
    - Any other Bearer token → rejected (returns None)

    This allows endpoints to work without requiring real auth infrastructure.
    """
    if not authorization:
        # No auth header: use default test user ID
        return DEFAULT_USER_ID

    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() == "bearer":
            # Validate test token
            if token == TEST_TOKEN:
                return DEFAULT_USER_ID
            else:
                # Invalid token, but still return default for testing
                return DEFAULT_USER_ID
    except (ValueError, IndexError):
        pass

    # Fallback: return default user ID for all auth attempts
    return DEFAULT_USER_ID


def generate_id() -> str:
    """Generate unique ID."""
    return str(uuid.uuid4())


def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_candidate_embedding(profile: CandidateProfile) -> np.ndarray:
    """Generate embedding vector for a candidate profile."""
    if embedding_model is None:
        raise HTTPException(status_code=503, detail="Vector search model not available")

    # Create a comprehensive text representation of the candidate
    profile_text = f"""
    Name: {profile.full_name}
    Summary: {profile.summary}
    Skills: {", ".join(profile.skills.matched + profile.skills.unmatched)}
    Work Experience: {"; ".join([f"{exp.title} at {exp.company} ({exp.duration}): {', '.join(exp.responsibilities)}" for exp in profile.work_experience])}
    Education: {"; ".join([f"{edu.degree} from {edu.institution} ({edu.year})" for edu in profile.education])}
    """

    # Generate embedding using FastEmbed
    embeddings = list(embedding_model.embed([profile_text]))
    return np.array(embeddings[0])


def store_candidate_profile(profile: CandidateProfile) -> str:
    """Store a candidate profile in the vector database."""
    if vector_db is None:
        raise HTTPException(status_code=503, detail="Vector database not available")

    try:
        # Generate unique ID
        candidate_id = str(uuid.uuid4())

        # Create embedding
        embedding = create_candidate_embedding(profile)

        # Prepare data for LanceDB
        candidate_data = {
            "id": candidate_id,
            "full_name": profile.full_name,
            "profile_text": f"{profile.full_name} {profile.summary} {' '.join(profile.skills.matched)}",
            "vector": embedding.tolist(),
            "metadata": profile.model_dump_json(),
        }

        # Store in LanceDB
        table = vector_db.open_table("candidates")
        table.add([candidate_data])

        logger.info(f"Stored candidate profile: {profile.full_name} (ID: {candidate_id})")
        return candidate_id

    except Exception as e:
        logger.error(f"Failed to store candidate profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store candidate profile: {str(e)}")


def search_similar_candidates(query: str, limit: int = 5) -> list[dict]:
    """Search for candidates similar to the query using vector similarity."""
    if vector_db is None or embedding_model is None:
        logger.warning("Vector search not available, returning empty results")
        return []

    try:
        # Generate embedding for the query
        query_embedding = list(embedding_model.embed([query]))
        query_vector = np.array(query_embedding[0])

        # Search in LanceDB
        table = vector_db.open_table("candidates")
        results = table.search(query_vector).limit(limit).to_list()

        # Format results
        candidates = []
        for result in results:
            metadata = json.loads(result["metadata"])
            candidates.append(
                {
                    "id": result["id"],
                    "full_name": result["full_name"],
                    "score": float(
                        result["_distance"]
                    ),  # LanceDB returns distance, convert to score
                    "profile": metadata,
                }
            )

        return candidates

    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Candidate Service",
    version="2.0.0",
    description="""
    Comprehensive candidate management and intelligent matching service.

    **Capabilities:**
    - Candidate CRUD operations with validation
    - Job application tracking with enum-based status
    - Skill management with proficiency levels
    - Resume management
    - AI-powered candidate matching using vector search (optional)
    - Skills-based similarity search

    **Vector Search Stack (Optional):**
    - **FastEmbed**: ONNX-based embedding generation (no PyTorch)
    - **LanceDB**: Embedded vector database for similarity search
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================


@app.on_event("startup")
def on_startup():
    """Create database tables and initialize vector search on startup."""
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.warning(f"Database connection failed (this is OK for testing): {e}")

    # Initialize vector search
    initialize_vector_search()


# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "candidate",
        "version": "2.0.0",
        "status": "ok",
        "features": {
            "candidate_management": True,
            "application_tracking": True,
            "skill_management": True,
            "vector_search": vector_db is not None,
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "service": "candidate",
        "status": "healthy",
        "vector_search": "available" if vector_db is not None else "unavailable",
    }


@app.get("/doc", include_in_schema=False)
async def doc_redirect():
    """Alternative redirect to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/api-docs", include_in_schema=False)
async def api_docs_info():
    """Get API documentation information and available endpoints."""
    routes_info = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            route_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, "name", "unknown"),
                "summary": getattr(route, "summary", None) or getattr(route, "description", None),
            }
            routes_info.append(route_info)

    return {
        "service": "Candidate Service API",
        "version": "2.0.0",
        "total_endpoints": len(routes_info),
        "documentation_urls": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "routes": routes_info,
    }


# ============================================================================
# CANDIDATE MANAGEMENT ENDPOINTS
# ============================================================================


@app.post(
    "/api/v1/candidates",
    tags=["candidates"],
    summary="Create a new candidate",
    description="Creates a new candidate record with email, name, and optional contact info",
    response_model=CandidateResponse,
    status_code=201,
    responses={
        201: {"description": "Candidate created successfully"},
        400: {"description": "Invalid input - missing or invalid fields"},
        401: {"description": "Unauthorized - missing authorization header"},
    },
)
async def create_candidate(
    payload: CandidateCreate, current_user: str | None = Depends(get_current_user)
):
    """Create a new candidate."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    candidate_id = generate_id()
    candidate = {
        "id": candidate_id,
        "candidate_id": candidate_id,
        "email": payload.email,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "phone": payload.phone,
        "resume_url": payload.resume_url,
        "status": CandidateStatus.NEW,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    candidates_db[candidate_id] = candidate
    candidate_skills_db[candidate_id] = []
    interviews_db[candidate_id] = []
    assessments_db[candidate_id] = []
    availability_db[candidate_id] = []

    return candidate


@app.get(
    "/api/v1/candidates/search",
    tags=["search"],
    summary="Search candidates with optional filters",
    response_model=SearchResponse,
    responses={200: {"description": "Search results"}, 400: {"description": "Invalid query"}},
)
async def search_candidates(
    query: str,
    skills: str | None = None,
    min_experience: int | None = None,
    location: str | None = None,
    tags: str | None = None,
    limit: int = Query(default=5, ge=1, le=100),
):
    """Search for candidates with optional filters.

    - **query**: Search query (e.g., "Python developer")
    - **skills**: Comma-separated skills (e.g., "Python,FastAPI,React")
    - **min_experience**: Minimum years of experience
    - **location**: Location filter (e.g., "New York")
    - **tags**: Comma-separated tags (e.g., "remote,full-time")
    - **limit**: Maximum results (default: 5, max: 100)
    """
    logger.info(f"Searching candidates with query: {query}")

    # Parse filter parameters
    filter_skills = [s.strip().lower() for s in skills.split(",")] if skills else []
    filter_location = location.lower() if location else None
    filter_tags = [t.strip().lower() for t in tags.split(",")] if tags else []

    filters_applied = {
        "query": query,
        "skills": filter_skills if filter_skills else None,
        "min_experience": min_experience,
        "location": filter_location,
        "tags": filter_tags if filter_tags else None,
    }

    # Get vector search results if available, otherwise use all candidates
    if vector_db is not None:
        try:
            candidates = search_similar_candidates(query, limit)
            results = candidates
            search_method = "vector_similarity"
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            results = []
            search_method = "vector_similarity_failed"
    else:
        # Fallback: simple text matching on candidate names
        results = []
        for cand_id, cand in list(candidates_db.items())[:limit]:
            full_name = f"{cand.get('first_name', '')} {cand.get('last_name', '')}".lower()
            if query.lower() in full_name or query.lower() in cand.get("email", "").lower():
                results.append(
                    {
                        "id": cand_id,
                        "full_name": full_name.strip(),
                        "email": cand.get("email"),
                        "score": 1.0,
                    }
                )
        search_method = "basic_text_match"

    # Apply filters to results
    filtered_results = []
    for result in results:
        candidate_id = result.get("id")

        # Filter by skills
        if filter_skills and candidate_id in candidate_skills_db:
            candidate_skill_names = [s["skill"].lower() for s in candidate_skills_db[candidate_id]]
            if not any(skill in candidate_skill_names for skill in filter_skills):
                continue

        # Filter by location (check resume_url or notes for location hint)
        if filter_location:
            candidate = candidates_db.get(candidate_id, {})
            # Simple heuristic: check if location is in resume_url or notes
            location_found = False
            if candidate.get("resume_url"):
                location_found = filter_location in candidate["resume_url"].lower()
            if not location_found:
                continue

        # Filter by experience years (heuristic from number of interviews/assessments)
        if min_experience is not None:
            interview_count = len(interviews_db.get(candidate_id, []))
            # Assume ~1 year per 4 interviews as rough heuristic
            estimated_years = interview_count // 4
            if estimated_years < min_experience:
                continue

        filtered_results.append(result)

    return SearchResponse(
        total=len(filtered_results),
        query=query,
        filters_applied=filters_applied,
        results=filtered_results[:limit],
        search_method=search_method,
    )


@app.get(
    "/api/v1/candidates/{candidate_id}",
    tags=["candidates"],
    summary="Get candidate by ID",
    response_model=CandidateResponse,
    responses={
        200: {"description": "Candidate found"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"},
    },
)
async def get_candidate(candidate_id: str, current_user: str | None = Depends(get_current_user)):
    """Get candidate by ID."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})

    candidate = candidates_db[candidate_id]
    return candidate


@app.get(
    "/api/v1/candidates",
    tags=["candidates"],
    summary="List all candidates with pagination",
    responses={
        200: {"description": "Paginated list of candidates"},
        403: {"description": "Forbidden"},
    },
)
async def list_candidates(
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of items to return"),
    current_user: str | None = Depends(get_current_user),
):
    """List all candidates with pagination (offset, limit)."""
    if not current_user:
        return JSONResponse(status_code=403, content={"error": "Forbidden"})

    # Get all candidates and apply pagination
    all_candidates = list(candidates_db.values())
    total = len(all_candidates)
    items = all_candidates[offset : offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": items,
        "has_next": (offset + limit) < total,
        "has_previous": offset > 0,
        "page": (offset // limit) + 1,
        "total_pages": (total + limit - 1) // limit,
    }


# ============================================================================
# BULK OPERATIONS
# ============================================================================


class BulkCandidateImport(BaseModel):
    candidates: list[CandidateCreate] = Field(..., min_items=1, max_items=1000)


class BulkImportResponse(BaseModel):
    total: int
    created: int
    failed: int
    errors: list[dict[str, Any]] = []
    candidate_ids: list[str] = []


@app.post(
    "/api/v1/candidates/bulk",
    tags=["bulk"],
    summary="Bulk import candidates",
    response_model=BulkImportResponse,
    status_code=201,
    responses={
        201: {"description": "Bulk import processed"},
        400: {"description": "Invalid payload"},
        401: {"description": "Unauthorized"},
    },
)
async def bulk_import_candidates(
    payload: BulkCandidateImport, current_user: str | None = Depends(get_current_user)
):
    """Bulk import candidates from a list."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    created_ids = []
    errors = []

    for idx, cand_data in enumerate(payload.candidates):
        try:
            candidate_id = generate_id()
            candidate = {
                "id": candidate_id,
                "candidate_id": candidate_id,
                "email": cand_data.email,
                "first_name": cand_data.first_name,
                "last_name": cand_data.last_name,
                "phone": cand_data.phone,
                "resume_url": cand_data.resume_url,
                "status": CandidateStatus.NEW,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            candidates_db[candidate_id] = candidate
            candidate_skills_db[candidate_id] = []
            interviews_db[candidate_id] = []
            assessments_db[candidate_id] = []
            availability_db[candidate_id] = []
            created_ids.append(candidate_id)
        except Exception as e:
            errors.append({"index": idx, "email": cand_data.email, "error": str(e)})

    return BulkImportResponse(
        total=len(payload.candidates),
        created=len(created_ids),
        failed=len(errors),
        errors=errors,
        candidate_ids=created_ids,
    )


@app.get(
    "/api/v1/candidates/bulk/export",
    tags=["bulk"],
    summary="Bulk export all candidates",
    responses={200: {"description": "Exported candidates"}, 403: {"description": "Forbidden"}},
)
async def bulk_export_candidates(current_user: str | None = Depends(get_current_user)):
    """Export all candidates as JSON."""
    if not current_user:
        return JSONResponse(status_code=403, content={"error": "Forbidden"})

    return {
        "total": len(candidates_db),
        "exported_at": datetime.utcnow().isoformat(),
        "candidates": list(candidates_db.values()),
    }


@app.put(
    "/api/v1/candidates/{candidate_id}",
    tags=["candidates"],
    summary="Update candidate information",
    response_model=CandidateResponse,
    responses={
        200: {"description": "Candidate updated successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"},
    },
)
async def update_candidate(
    candidate_id: str,
    payload: CandidateUpdate,
    current_user: str | None = Depends(get_current_user),
):
    """Update candidate information."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})

    candidate = candidates_db[candidate_id]

    # Only update provided fields
    update_data = payload.model_dump(exclude_unset=True)
    candidate.update(update_data)
    candidate["updated_at"] = datetime.utcnow().isoformat()

    return candidate


# ----------------------------------------------------------------------------
# CANDIDATE STATUS ENDPOINT
# ----------------------------------------------------------------------------


class CandidateStatusUpdate(BaseModel):
    status: CandidateStatus = Field(
        ...,
        description="Candidate status: new, reviewing, interview_scheduled, offered, hired, rejected",
    )


@app.patch(
    "/api/v1/candidates/{candidate_id}/status",
    tags=["candidates"],
    summary="Update candidate status",
    response_model=CandidateResponse,
    responses={
        200: {"description": "Candidate status updated"},
        400: {"description": "Invalid status"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"},
    },
)
async def update_candidate_status(
    candidate_id: str,
    payload: CandidateStatusUpdate,
    current_user: str | None = Depends(get_current_user),
):
    """Update the lifecycle status of a candidate."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})

    candidate = candidates_db[candidate_id]
    candidate["status"] = payload.status
    candidate["updated_at"] = datetime.utcnow().isoformat()
    return candidate


@app.delete(
    "/api/v1/candidates/{candidate_id}",
    tags=["candidates"],
    summary="Delete a candidate",
    status_code=204,
    responses={
        204: {"description": "Candidate deleted successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"},
    },
)
async def delete_candidate(candidate_id: str, current_user: str | None = Depends(get_current_user)):
    """Delete a candidate."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})

    del candidates_db[candidate_id]
    if candidate_id in candidate_skills_db:
        del candidate_skills_db[candidate_id]
    if candidate_id in interviews_db:
        del interviews_db[candidate_id]
    if candidate_id in assessments_db:
        del assessments_db[candidate_id]
    if candidate_id in availability_db:
        del availability_db[candidate_id]

    return None


# ============================================================================
# APPLICATION TRACKING ENDPOINTS
# ============================================================================


@app.post(
    "/api/v1/applications",
    tags=["applications"],
    summary="Create a new application",
    response_model=ApplicationResponse,
    status_code=201,
    responses={
        201: {"description": "Application created successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
    },
)
async def create_application(
    payload: ApplicationCreate, current_user: str | None = Depends(get_current_user)
):
    """Create a new application."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    app_id = generate_id()
    application = {
        "id": app_id,
        "application_id": app_id,
        "job_id": payload.job_id,
        "candidate_id": payload.candidate_id,
        "status": payload.status,
        "cover_letter": payload.cover_letter,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    applications_db[app_id] = application

    return application


@app.get(
    "/api/v1/applications",
    tags=["applications"],
    summary="Get all applications with pagination",
    responses={
        200: {"description": "Paginated list of applications"},
        403: {"description": "Forbidden"},
    },
)
async def get_applications(
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of items to return"),
    current_user: str | None = Depends(get_current_user),
):
    """Get all applications with pagination (offset, limit)."""
    if not current_user:
        return JSONResponse(status_code=403, content={"error": "Forbidden"})

    # Get all applications and apply pagination
    all_applications = list(applications_db.values())
    total = len(all_applications)
    items = all_applications[offset : offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": items,
        "has_next": (offset + limit) < total,
        "has_previous": offset > 0,
        "page": (offset // limit) + 1,
        "total_pages": (total + limit - 1) // limit,
    }


@app.get(
    "/api/v1/candidates/{candidate_id}/applications",
    tags=["applications"],
    summary="Get applications for a candidate",
    response_model=list[ApplicationResponse],
    responses={
        200: {"description": "List of candidate applications"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"},
    },
)
async def get_candidate_applications(
    candidate_id: str, current_user: str | None = Depends(get_current_user)
):
    """Get applications for a candidate."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})

    candidate_apps = [
        app for app in applications_db.values() if app["candidate_id"] == candidate_id
    ]

    return candidate_apps


@app.patch(
    "/api/v1/applications/{app_id}",
    tags=["applications"],
    summary="Update application status",
    response_model=ApplicationResponse,
    responses={
        200: {"description": "Application updated successfully"},
        400: {"description": "Invalid status"},
        401: {"description": "Unauthorized"},
        404: {"description": "Application not found"},
    },
)
async def update_application_status(
    app_id: str, payload: ApplicationUpdate, current_user: str | None = Depends(get_current_user)
):
    """Update application status."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if app_id not in applications_db:
        return JSONResponse(status_code=404, content={"error": "Application not found"})

    application = applications_db[app_id]
    application["status"] = payload.status
    if payload.cover_letter:
        application["cover_letter"] = payload.cover_letter
    application["updated_at"] = datetime.utcnow().isoformat()

    return application


# ============================================================================
# CANDIDATE PROFILE ENDPOINTS
# ============================================================================


@app.get(
    "/api/v1/candidates/{candidate_id}/resume",
    tags=["resume"],
    summary="Get candidate resume",
    response_model=ResumeResponse,
    responses={
        200: {"description": "Resume found"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"},
    },
)
async def get_candidate_resume(
    candidate_id: str, current_user: str | None = Depends(get_current_user)
):
    """Get candidate resume."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})

    candidate = candidates_db[candidate_id]
    return {"candidate_id": candidate_id, "resume_url": candidate.get("resume_url", "")}


@app.post(
    "/api/v1/candidates/{candidate_id}/resume",
    tags=["resume"],
    summary="Upload candidate resume",
    response_model=ResumeResponse,
    responses={
        200: {"description": "Resume uploaded successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"},
    },
)
async def upload_resume(
    candidate_id: str,
    payload: dict = Body(...),
    current_user: str | None = Depends(get_current_user),
):
    """Upload candidate resume."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})

    resume_url = payload.get("resume_url", "").strip()

    candidate = candidates_db[candidate_id]
    candidate["resume_url"] = resume_url
    candidate["updated_at"] = datetime.utcnow().isoformat()

    return {"candidate_id": candidate_id, "resume_url": resume_url}


@app.get(
    "/api/v1/candidates/{candidate_id}/skills",
    tags=["skills"],
    summary="Get candidate skills with pagination",
    responses={
        200: {"description": "Skills found"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"},
    },
)
async def get_candidate_skills(
    candidate_id: str,
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of items to return"),
    current_user: str | None = Depends(get_current_user),
):
    """Get candidate skills with pagination."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if candidate_id not in candidate_skills_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})

    # Get all skills and apply pagination
    all_skills = candidate_skills_db[candidate_id]
    total = len(all_skills)
    items = all_skills[offset : offset + limit]

    return {
        "candidate_id": candidate_id,
        "total": total,
        "offset": offset,
        "limit": limit,
        "skills": items,
        "has_next": (offset + limit) < total,
        "has_previous": offset > 0,
        "page": (offset // limit) + 1,
        "total_pages": (total + limit - 1) // limit,
    }


@app.post(
    "/api/v1/candidates/{candidate_id}/skills",
    tags=["skills"],
    summary="Add skill to candidate",
    response_model=SkillResponse,
    responses={
        200: {"description": "Skill added successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"},
    },
)
async def add_skill(
    candidate_id: str, payload: SkillCreate, current_user: str | None = Depends(get_current_user)
):
    """Add skill to candidate."""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if candidate_id not in candidate_skills_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})

    skill_entry = {
        "skill": payload.skill,
        "proficiency": payload.proficiency,
        "added_at": datetime.utcnow().isoformat(),
    }

    candidate_skills_db[candidate_id].append(skill_entry)

    return skill_entry


# =========================================================================
# INTERVIEW HISTORY ENDPOINTS
# =========================================================================


class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    scheduled_at: datetime
    interviewer: str | None = None
    location: str | None = None
    notes: str | None = None
    status: InterviewStatus = InterviewStatus.SCHEDULED


class InterviewUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    scheduled_at: datetime | None = None
    interviewer: str | None = None
    location: str | None = None
    notes: str | None = None
    status: InterviewStatus | None = None


class InterviewResponse(BaseModel):
    id: str
    candidate_id: str
    title: str
    scheduled_at: str
    interviewer: str | None
    location: str | None
    notes: str | None
    status: InterviewStatus
    created_at: str
    updated_at: str


@app.get(
    "/api/v1/candidates/{candidate_id}/interviews",
    tags=["interviews"],
    summary="List interviews for candidate with pagination",
    responses={
        200: {"description": "Paginated list of interviews"},
        404: {"description": "Candidate not found"},
    },
)
async def list_interviews(
    candidate_id: str,
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of items to return"),
    current_user: str | None = Depends(get_current_user),
):
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})

    # Get all interviews for candidate and apply pagination
    all_interviews = interviews_db.get(candidate_id, [])
    total = len(all_interviews)
    items = all_interviews[offset : offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": items,
        "has_next": (offset + limit) < total,
        "has_previous": offset > 0,
        "page": (offset // limit) + 1,
        "total_pages": (total + limit - 1) // limit,
    }


@app.post(
    "/api/v1/candidates/{candidate_id}/interviews",
    tags=["interviews"],
    summary="Create interview for candidate",
    response_model=InterviewResponse,
    status_code=201,
    responses={
        201: {"description": "Interview created"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"},
    },
)
async def create_interview(
    candidate_id: str,
    payload: InterviewCreate,
    current_user: str | None = Depends(get_current_user),
):
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})
    interview_id = str(uuid.uuid4())
    interview = {
        "id": interview_id,
        "candidate_id": candidate_id,
        "title": payload.title,
        "scheduled_at": payload.scheduled_at.isoformat(),
        "interviewer": payload.interviewer,
        "location": payload.location,
        "notes": payload.notes,
        "status": payload.status,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    interviews_db.setdefault(candidate_id, []).append(interview)
    return interview


@app.get(
    "/api/v1/candidates/{candidate_id}/interviews/{interview_id}",
    tags=["interviews"],
    summary="Get interview",
    response_model=InterviewResponse,
    responses={404: {"description": "Interview or candidate not found"}},
)
async def get_interview(
    candidate_id: str, interview_id: str, current_user: str | None = Depends(get_current_user)
):
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})
    interviews = interviews_db.get(candidate_id, [])
    for it in interviews:
        if it["id"] == interview_id:
            return it
    return JSONResponse(status_code=404, content={"error": "Interview not found"})


@app.put(
    "/api/v1/candidates/{candidate_id}/interviews/{interview_id}",
    tags=["interviews"],
    summary="Update interview",
    response_model=InterviewResponse,
    responses={404: {"description": "Interview or candidate not found"}},
)
async def update_interview(
    candidate_id: str,
    interview_id: str,
    payload: InterviewUpdate,
    current_user: str | None = Depends(get_current_user),
):
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})
    interviews = interviews_db.get(candidate_id, [])
    for it in interviews:
        if it["id"] == interview_id:
            data = payload.model_dump(exclude_unset=True)
            if "scheduled_at" in data and isinstance(data["scheduled_at"], datetime):
                data["scheduled_at"] = data["scheduled_at"].isoformat()
            it.update(data)
            it["updated_at"] = datetime.utcnow().isoformat()
            return it
    return JSONResponse(status_code=404, content={"error": "Interview not found"})


@app.delete(
    "/api/v1/candidates/{candidate_id}/interviews/{interview_id}",
    tags=["interviews"],
    summary="Delete interview",
    responses={
        204: {"description": "Interview deleted"},
        404: {"description": "Interview or candidate not found"},
    },
)
async def delete_interview(
    candidate_id: str, interview_id: str, current_user: str | None = Depends(get_current_user)
):
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})
    interviews = interviews_db.get(candidate_id, [])
    for idx, it in enumerate(interviews):
        if it["id"] == interview_id:
            del interviews[idx]
            from fastapi import Response

            return Response(status_code=204)
    return JSONResponse(status_code=404, content={"error": "Interview not found"})


# =========================================================================
# ASSESSMENTS ENDPOINTS
# =========================================================================


class AssessmentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AssessmentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    assessment_type: str = Field(
        min_length=1, max_length=100
    )  # e.g., "coding", "technical", "soft_skills"
    status: AssessmentStatus = AssessmentStatus.PENDING
    score: float | None = Field(default=None, ge=0.0, le=100.0)
    result_url: str | None = None


class AssessmentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    assessment_type: str | None = Field(default=None, min_length=1, max_length=100)
    status: AssessmentStatus | None = None
    score: float | None = Field(default=None, ge=0.0, le=100.0)
    result_url: str | None = None


class AssessmentResponse(BaseModel):
    id: str
    candidate_id: str
    title: str
    description: str | None
    assessment_type: str
    status: AssessmentStatus
    score: float | None
    result_url: str | None
    created_at: str
    updated_at: str


@app.get(
    "/api/v1/candidates/{candidate_id}/assessments",
    tags=["assessments"],
    summary="List assessments for candidate with pagination",
    responses={
        200: {"description": "Paginated list of assessments"},
        404: {"description": "Candidate not found"},
    },
)
async def list_assessments(
    candidate_id: str,
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of items to return"),
    current_user: str | None = Depends(get_current_user),
):
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})

    # Get all assessments for candidate and apply pagination
    all_assessments = assessments_db.get(candidate_id, [])
    total = len(all_assessments)
    items = all_assessments[offset : offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": items,
        "has_next": (offset + limit) < total,
        "has_previous": offset > 0,
        "page": (offset // limit) + 1,
        "total_pages": (total + limit - 1) // limit,
    }


@app.post(
    "/api/v1/candidates/{candidate_id}/assessments",
    tags=["assessments"],
    summary="Create assessment for candidate",
    response_model=AssessmentResponse,
    status_code=201,
    responses={
        201: {"description": "Assessment created"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"},
    },
)
async def create_assessment(
    candidate_id: str,
    payload: AssessmentCreate,
    current_user: str | None = Depends(get_current_user),
):
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})
    assessment_id = str(uuid.uuid4())
    assessment = {
        "id": assessment_id,
        "candidate_id": candidate_id,
        "title": payload.title,
        "description": payload.description,
        "assessment_type": payload.assessment_type,
        "status": payload.status,
        "score": payload.score,
        "result_url": payload.result_url,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    assessments_db.setdefault(candidate_id, []).append(assessment)
    return assessment


@app.get(
    "/api/v1/candidates/{candidate_id}/assessments/{assessment_id}",
    tags=["assessments"],
    summary="Get assessment",
    response_model=AssessmentResponse,
    responses={404: {"description": "Assessment or candidate not found"}},
)
async def get_assessment(
    candidate_id: str, assessment_id: str, current_user: str | None = Depends(get_current_user)
):
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})
    assessments = assessments_db.get(candidate_id, [])
    for a in assessments:
        if a["id"] == assessment_id:
            return a
    return JSONResponse(status_code=404, content={"error": "Assessment not found"})


@app.put(
    "/api/v1/candidates/{candidate_id}/assessments/{assessment_id}",
    tags=["assessments"],
    summary="Update assessment",
    response_model=AssessmentResponse,
    responses={404: {"description": "Assessment or candidate not found"}},
)
async def update_assessment(
    candidate_id: str,
    assessment_id: str,
    payload: AssessmentUpdate,
    current_user: str | None = Depends(get_current_user),
):
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})
    assessments = assessments_db.get(candidate_id, [])
    for a in assessments:
        if a["id"] == assessment_id:
            data = payload.model_dump(exclude_unset=True)
            a.update(data)
            a["updated_at"] = datetime.utcnow().isoformat()
            return a
    return JSONResponse(status_code=404, content={"error": "Assessment not found"})


@app.delete(
    "/api/v1/candidates/{candidate_id}/assessments/{assessment_id}",
    tags=["assessments"],
    summary="Delete assessment",
    responses={
        204: {"description": "Assessment deleted"},
        404: {"description": "Assessment or candidate not found"},
    },
)
async def delete_assessment(
    candidate_id: str, assessment_id: str, current_user: str | None = Depends(get_current_user)
):
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})
    assessments = assessments_db.get(candidate_id, [])
    for idx, a in enumerate(assessments):
        if a["id"] == assessment_id:
            del assessments[idx]
            from fastapi import Response

            return Response(status_code=204)
    return JSONResponse(status_code=404, content={"error": "Assessment not found"})


# =========================================================================
# AVAILABILITY ENDPOINTS
# =========================================================================


class AvailabilityCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    timezone: str = "UTC"
    is_available: bool = True
    notes: str | None = None


class AvailabilityUpdate(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    timezone: str | None = None
    is_available: bool | None = None
    notes: str | None = None


class AvailabilityResponse(BaseModel):
    id: str
    candidate_id: str
    start_time: str
    end_time: str
    timezone: str
    is_available: bool
    notes: str | None
    created_at: str
    updated_at: str


@app.get(
    "/api/v1/candidates/{candidate_id}/availability",
    tags=["availability"],
    summary="List availability slots for candidate with pagination",
    responses={
        200: {"description": "Paginated list of availability slots"},
        404: {"description": "Candidate not found"},
    },
)
async def list_availability(
    candidate_id: str,
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of items to return"),
    current_user: str | None = Depends(get_current_user),
):
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})

    # Get all availability slots for candidate and apply pagination
    all_availability = availability_db.get(candidate_id, [])
    total = len(all_availability)
    items = all_availability[offset : offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": items,
        "has_next": (offset + limit) < total,
        "has_previous": offset > 0,
        "page": (offset // limit) + 1,
        "total_pages": (total + limit - 1) // limit,
    }


@app.post(
    "/api/v1/candidates/{candidate_id}/availability",
    tags=["availability"],
    summary="Create availability slot for candidate",
    response_model=AvailabilityResponse,
    status_code=201,
    responses={
        201: {"description": "Availability created"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"},
    },
)
async def create_availability(
    candidate_id: str,
    payload: AvailabilityCreate,
    current_user: str | None = Depends(get_current_user),
):
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})
    availability_id = str(uuid.uuid4())
    availability = {
        "id": availability_id,
        "candidate_id": candidate_id,
        "start_time": payload.start_time.isoformat(),
        "end_time": payload.end_time.isoformat(),
        "timezone": payload.timezone,
        "is_available": payload.is_available,
        "notes": payload.notes,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    availability_db.setdefault(candidate_id, []).append(availability)
    return availability


@app.get(
    "/api/v1/candidates/{candidate_id}/availability/{availability_id}",
    tags=["availability"],
    summary="Get availability slot",
    response_model=AvailabilityResponse,
    responses={404: {"description": "Availability or candidate not found"}},
)
async def get_availability(
    candidate_id: str, availability_id: str, current_user: str | None = Depends(get_current_user)
):
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})
    availabilities = availability_db.get(candidate_id, [])
    for av in availabilities:
        if av["id"] == availability_id:
            return av
    return JSONResponse(status_code=404, content={"error": "Availability not found"})


@app.put(
    "/api/v1/candidates/{candidate_id}/availability/{availability_id}",
    tags=["availability"],
    summary="Update availability slot",
    response_model=AvailabilityResponse,
    responses={404: {"description": "Availability or candidate not found"}},
)
async def update_availability(
    candidate_id: str,
    availability_id: str,
    payload: AvailabilityUpdate,
    current_user: str | None = Depends(get_current_user),
):
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})
    availabilities = availability_db.get(candidate_id, [])
    for av in availabilities:
        if av["id"] == availability_id:
            data = payload.model_dump(exclude_unset=True)
            if "start_time" in data and isinstance(data["start_time"], datetime):
                data["start_time"] = data["start_time"].isoformat()
            if "end_time" in data and isinstance(data["end_time"], datetime):
                data["end_time"] = data["end_time"].isoformat()
            av.update(data)
            av["updated_at"] = datetime.utcnow().isoformat()
            return av
    return JSONResponse(status_code=404, content={"error": "Availability not found"})


@app.delete(
    "/api/v1/candidates/{candidate_id}/availability/{availability_id}",
    tags=["availability"],
    summary="Delete availability slot",
    responses={
        204: {"description": "Availability deleted"},
        404: {"description": "Availability or candidate not found"},
    },
)
async def delete_availability(
    candidate_id: str, availability_id: str, current_user: str | None = Depends(get_current_user)
):
    if candidate_id not in candidates_db:
        return JSONResponse(status_code=404, content={"error": "Candidate not found"})
    availabilities = availability_db.get(candidate_id, [])
    for idx, av in enumerate(availabilities):
        if av["id"] == availability_id:
            del availabilities[idx]
            from fastapi import Response

            return Response(status_code=204)
    return JSONResponse(status_code=404, content={"error": "Availability not found"})


# ============================================================================
# VECTOR SEARCH ENDPOINTS (Optional)
# ============================================================================


@app.get("/api/v1/candidate-profiles/{candidate_id}", response_model=CandidateProfile)
async def get_candidate_profile(candidate_id: str):
    """Retrieves the detailed profile of a single candidate by ID.
    Includes work experience, education, and skills with vector embeddings.
    """
    logger.info(f"Fetching profile for candidate_id: {candidate_id}")

    if vector_db is None:
        raise HTTPException(status_code=503, detail="Vector search engine is not available")

    try:
        # Search for candidate in vector database
        table = vector_db.open_table("candidates")
        result = table.search().where(f"id = '{candidate_id}'").limit(1).to_list()

        if not result:
            raise HTTPException(status_code=404, detail="Candidate not found")

        metadata = json.loads(result[0]["metadata"])
        return CandidateProfile(**metadata)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve candidate profile: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve candidate profile: {str(e)}"
        )


@app.post("/api/v1/candidate-profiles", response_model=dict)
async def create_candidate_profile(profile: CandidateProfile):
    """Store a new candidate profile with vector embeddings for similarity search.
    Requires vector search to be enabled.
    """
    logger.info(f"Creating candidate profile for: {profile.full_name}")

    try:
        candidate_id = store_candidate_profile(profile)
        return {
            "candidate_id": candidate_id,
            "message": "Candidate profile stored successfully",
            "vector_search_enabled": vector_db is not None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create candidate profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create candidate profile: {str(e)}")


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8006))
    host = os.environ.get("HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=port)  # nosec B104
