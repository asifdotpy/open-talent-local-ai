"""Scout Service - Pydantic V2 Schemas
Generated: December 17, 2025
Coverage: ~15 schemas for search, candidates, enrichment, and handoff.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")
    location: str = Field("Ireland", description="Location to search in")
    max_results: int = Field(20, ge=1, le=100, description="Maximum number of results to return")
    use_ai_formatting: bool = Field(True, description="Whether to use AI for query formatting")


class CandidateResponse(BaseModel):
    name: str
    location: str | None = None
    profile_url: HttpUrl
    platform: str
    bio: str | None = None
    email: EmailStr | None = None
    linkedin_url: HttpUrl | None = None
    twitter_url: HttpUrl | None = None
    website_url: HttpUrl | None = None
    company: str | None = None
    confidence_score: float | None = Field(None, ge=0.0, le=1.0)
    linkedin_enriched: dict[str, Any] | None = None
    work_emails: list[EmailStr] | None = None
    personal_emails: list[EmailStr] | None = None
    phone_numbers: list[str] | None = None
    linkedin_headline: str | None = None
    linkedin_industry: str | None = None
    linkedin_summary: str | None = None
    linkedin_experience: list[dict[str, Any]] | None = None
    linkedin_education: list[dict[str, Any]] | None = None
    linkedin_skills: list[str] | None = None
    linkedin_followers: int | None = None

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    candidates: list[CandidateResponse]
    total_found: int
    search_query: str
    location: str


class SearchCriteria(BaseModel):
    jobTitle: str = Field(..., description="The target job title")
    requiredSkills: list[str] = Field(..., description="Mandatory skills")
    niceToHaveSkills: list[str] = Field(..., description="Optional skills")
    companyCulture: list[str] = Field(..., description="Culture keywords")
    experienceLevel: str = Field(..., description="Seniority (e.g., Senior)")


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
    question: str
    reasoning: str


class CandidateProfile(BaseModel):
    fullName: str
    sourceUrl: HttpUrl
    summary: str
    workExperience: list[WorkExperience]
    education: list[Education]
    skills: Skills
    alignmentScore: float = Field(..., ge=0.0, le=1.0)
    initialQuestions: list[InitialQuestion]


class HandoffPayload(BaseModel):
    searchCriteria: SearchCriteria
    candidateProfile: CandidateProfile


class AgentInfo(BaseModel):
    name: str
    description: str | None = None
    capabilities: list[str] = []
    average_latency_ms: int | None = None


class AgentSearchRequest(BaseModel):
    query: str
    agent: str
    location: str | None = None
    max_results: int = Field(10, ge=1, le=50)


class AgentSearchResult(BaseModel):
    agent: str
    candidates: list[CandidateResponse]
    latency_ms: int | None = None
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
