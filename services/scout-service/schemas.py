"""
Scout Service - Pydantic V2 Schemas
Generated: December 17, 2025
Coverage: ~15 schemas for search, candidates, enrichment, and handoff.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, EmailStr, ConfigDict
from datetime import datetime


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")
    location: str = Field("Ireland", description="Location to search in")
    max_results: int = Field(20, ge=1, le=100, description="Maximum number of results to return")
    use_ai_formatting: bool = Field(True, description="Whether to use AI for query formatting")


class CandidateResponse(BaseModel):
    name: str
    location: Optional[str] = None
    profile_url: HttpUrl
    platform: str
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    linkedin_url: Optional[HttpUrl] = None
    twitter_url: Optional[HttpUrl] = None
    website_url: Optional[HttpUrl] = None
    company: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    linkedin_enriched: Optional[Dict[str, Any]] = None
    work_emails: Optional[List[EmailStr]] = None
    personal_emails: Optional[List[EmailStr]] = None
    phone_numbers: Optional[List[str]] = None
    linkedin_headline: Optional[str] = None
    linkedin_industry: Optional[str] = None
    linkedin_summary: Optional[str] = None
    linkedin_experience: Optional[List[Dict[str, Any]]] = None
    linkedin_education: Optional[List[Dict[str, Any]]] = None
    linkedin_skills: Optional[List[str]] = None
    linkedin_followers: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    candidates: List[CandidateResponse]
    total_found: int
    search_query: str
    location: str


class SearchCriteria(BaseModel):
    jobTitle: str = Field(..., description="The target job title")
    requiredSkills: List[str] = Field(..., description="Mandatory skills")
    niceToHaveSkills: List[str] = Field(..., description="Optional skills")
    companyCulture: List[str] = Field(..., description="Culture keywords")
    experienceLevel: str = Field(..., description="Seniority (e.g., Senior)")


class WorkExperience(BaseModel):
    title: str
    company: str
    duration: str
    responsibilities: List[str]


class Education(BaseModel):
    institution: str
    degree: str
    year: str


class Skills(BaseModel):
    matched: List[str]
    unmatched: List[str]


class InitialQuestion(BaseModel):
    question: str
    reasoning: str


class CandidateProfile(BaseModel):
    fullName: str
    sourceUrl: HttpUrl
    summary: str
    workExperience: List[WorkExperience]
    education: List[Education]
    skills: Skills
    alignmentScore: float = Field(..., ge=0.0, le=1.0)
    initialQuestions: List[InitialQuestion]


class HandoffPayload(BaseModel):
    searchCriteria: SearchCriteria
    candidateProfile: CandidateProfile


class AgentInfo(BaseModel):
    name: str
    description: Optional[str] = None
    capabilities: List[str] = []
    average_latency_ms: Optional[int] = None


class AgentSearchRequest(BaseModel):
    query: str
    agent: str
    location: Optional[str] = None
    max_results: int = Field(10, ge=1, le=50)


class AgentSearchResult(BaseModel):
    agent: str
    candidates: List[CandidateResponse]
    latency_ms: Optional[int] = None
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
