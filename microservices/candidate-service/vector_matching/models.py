"""Pydantic models for vector matching.
These are used for API request/response, not database models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CandidateEmbedding(BaseModel):
    """Candidate profile embedding for vector search."""

    candidate_id: str
    full_name: str
    email: str
    profile_text: str = Field(..., description="Concatenated profile text for embedding")
    embedding: Optional[list[float]] = Field(None, description="384-dim embedding vector")
    skills: list[str] = Field(default_factory=list)
    experience_years: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class JobEmbedding(BaseModel):
    """Job description embedding for vector search."""

    job_id: str
    title: str
    description: str = Field(..., description="Full job description text")
    embedding: Optional[list[float]] = Field(None, description="384-dim embedding vector")
    required_skills: list[str] = Field(default_factory=list)
    experience_required: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MatchResult(BaseModel):
    """Result of a candidate-job match."""

    candidate_id: str
    job_id: str
    similarity_score: float = Field(..., ge=0, le=1, description="Cosine similarity score")
    skill_match_score: float = Field(..., ge=0, le=1, description="Skill overlap score")
    experience_match: bool = Field(..., description="Whether experience requirement is met")
    overall_score: float = Field(..., ge=0, le=100, description="Weighted overall match score")
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)


class MatchRequest(BaseModel):
    """Request to find matching candidates for a job."""

    job_id: str
    top_k: int = Field(default=10, ge=1, le=100, description="Number of top matches to return")
    min_similarity: float = Field(
        default=0.5, ge=0, le=1, description="Minimum similarity threshold"
    )
    require_skill_match: bool = Field(
        default=False, description="Whether to enforce skill requirements"
    )


class MatchResponse(BaseModel):
    """Response with candidate matches for a job."""

    job_id: str
    total_candidates_searched: int
    matches: list[MatchResult]
    search_time_ms: float
