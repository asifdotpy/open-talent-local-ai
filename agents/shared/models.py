"""
Shared data models for TalentAI agents.
Pydantic schemas for inter-agent communication and data exchange.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CandidateSource(str, Enum):
    """Source of candidate discovery"""
    LINKEDIN = "linkedin"
    GITHUB = "github"
    STACKOVERFLOW = "stackoverflow"
    ANGELLIST = "angellist"
    REFERRAL = "referral"
    DIRECT_APPLICATION = "direct_application"
    CONTACTOUT = "contactout"
    SALESQL = "salesql"


class CandidateStatus(str, Enum):
    """Candidate pipeline status"""
    NEW = "new"
    SOURCED = "sourced"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    SCREENING = "screening"
    INTERVIEWED = "interviewed"
    ASSESSMENT = "assessment"
    OFFER_PENDING = "offer_pending"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class SkillProficiency(str, Enum):
    """Skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Skill(BaseModel):
    """Skill representation"""
    name: str
    proficiency_level: Optional[SkillProficiency] = None
    years_experience: Optional[int] = None
    verified: bool = False


class WorkExperience(BaseModel):
    """Work experience entry"""
    company: str
    title: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: bool = False
    description: Optional[str] = None
    location: Optional[str] = None


class Education(BaseModel):
    """Education entry"""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    grade: Optional[str] = None


class SocialProfile(BaseModel):
    """Social media profile"""
    platform: str
    url: str
    username: Optional[str] = None
    verified: bool = False


class CandidateProfile(BaseModel):
    """Comprehensive candidate profile"""
    # Basic Information
    id: Optional[str] = None
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    
    # Professional Data
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    experience_years: Optional[int] = None
    experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    
    # Social & Portfolio
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    social_profiles: List[SocialProfile] = Field(default_factory=list)
    
    # AI-Generated Insights
    ai_summary: Optional[str] = None
    match_score: Optional[float] = Field(None, ge=0, le=100)
    quality_score: Optional[float] = Field(None, ge=0, le=100)
    
    # Process Tracking
    status: CandidateStatus = CandidateStatus.NEW
    source: Optional[CandidateSource] = None
    source_notes: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OutreachChannel(str, Enum):
    """Communication channels for outreach"""
    EMAIL = "email"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"
    PHONE = "phone"


class OutreachStatus(str, Enum):
    """Outreach attempt status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    REPLIED = "replied"
    BOUNCED = "bounced"
    FAILED = "failed"


class OutreachAttempt(BaseModel):
    """Single outreach attempt"""
    id: Optional[str] = None
    channel: OutreachChannel
    subject: Optional[str] = None
    message: str
    sent_at: Optional[datetime] = None
    status: OutreachStatus = OutreachStatus.PENDING
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    response_text: Optional[str] = None


class EngagementHistory(BaseModel):
    """Complete engagement history for a candidate"""
    candidate_id: str
    project_id: str
    total_attempts: int = 0
    channels_used: List[OutreachChannel] = Field(default_factory=list)
    outreach_attempts: List[OutreachAttempt] = Field(default_factory=list)
    response_rate: float = Field(0.0, ge=0, le=1)
    engagement_score: Optional[float] = Field(None, ge=0, le=100)
    last_contact_date: Optional[datetime] = None
    next_followup_date: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class SalaryTrend(BaseModel):
    """Salary trend data"""
    job_title: str
    location: str
    min_salary: float
    max_salary: float
    median_salary: float
    currency: str = "USD"
    sample_size: int
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class SkillDemand(BaseModel):
    """Skill demand data"""
    skill_name: str
    job_title: str
    demand_level: str  # "low", "medium", "high"
    growth_rate: float  # percentage
    avg_salary_impact: float
    trending_frameworks: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class CompetitorIntel(BaseModel):
    """Competitor intelligence data"""
    company_name: str
    location: str
    open_positions: int = 0
    hiring_rate: str = "unknown"  # "low", "medium", "high"
    avg_tenure_months: Optional[float] = None
    benefits_score: Optional[float] = Field(None, ge=0, le=10)
    culture_rating: Optional[float] = Field(None, ge=0, le=5)
    data_source: str = "unknown"


class MarketInsight(BaseModel):
    """Market intelligence aggregation"""
    job_title: str
    location: Optional[str] = None
    industry: Optional[str] = None
    salary_trends: List[SalaryTrend] = Field(default_factory=list)
    competitor_data: List[CompetitorIntel] = Field(default_factory=list)
    in_demand_skills: List[str] = Field(default_factory=list)
    talent_availability: Optional[str] = None  # "high", "medium", "low"
    market_saturation: Optional[float] = Field(None, ge=0, le=1)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class MessageType(str, Enum):
    """Agent message types"""
    CANDIDATE_FOUND = "candidate_found"
    CANDIDATE_SCORED = "candidate_scored"
    OUTREACH_SENT = "outreach_sent"
    OUTREACH_RESPONSE = "outreach_response"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    PIPELINE_UPDATE = "pipeline_update"
    MARKET_INSIGHT = "market_insight"
    ERROR = "error"
    # Data Enrichment Agent messages
    CANDIDATE_SEARCH_PROGRESS = "candidate_search_progress"
    CANDIDATE_SEARCH_COMPLETE = "candidate_search_complete"
    CANDIDATE_SEARCH_FAILED = "candidate_search_failed"
    ENRICHMENT_COMPLETE = "enrichment_complete"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AgentMessage(BaseModel):
    """Inter-agent communication message"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_agent: str
    target_agent: Optional[str] = None  # None = broadcast
    message_type: MessageType
    payload: Dict[str, Any]
    priority: MessagePriority = MessagePriority.MEDIUM
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    
    class Config:
        use_enum_values = True


class PipelineState(str, Enum):
    """Sourcing pipeline states"""
    INITIATED = "initiated"
    SCANNING = "scanning"
    SCORING = "scoring"
    ENGAGING = "engaging"
    INTERVIEWING = "interviewing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class SourcingPipeline(BaseModel):
    """Sourcing pipeline state"""
    id: str
    project_id: str
    job_description: str
    state: PipelineState = PipelineState.INITIATED
    active_agents: List[str] = Field(default_factory=list)
    candidates_found: int = 0
    candidates_contacted: int = 0
    candidates_responded: int = 0
    interviews_scheduled: int = 0
    interviews_completed: int = 0
    started_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class InterviewResult(BaseModel):
    """Interview results from Vetta AI"""
    session_id: str
    candidate_id: str
    project_id: str
    questions: List[Dict[str, Any]]
    responses: List[Dict[str, Any]]
    overall_score: float = Field(..., ge=0, le=100)
    technical_score: Optional[float] = Field(None, ge=0, le=100)
    communication_score: Optional[float] = Field(None, ge=0, le=100)
    cultural_fit_score: Optional[float] = Field(None, ge=0, le=100)
    recommendation: str  # "hire", "maybe", "reject"
    key_insights: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    conducted_at: datetime = Field(default_factory=datetime.utcnow)
