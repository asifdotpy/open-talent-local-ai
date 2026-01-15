"""
Shared data models for OpenTalent agents.
Pydantic schemas for inter-agent communication and data exchange.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field


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
    proficiency_level: SkillProficiency | None = None
    years_experience: int | None = None
    verified: bool = False


class WorkExperience(BaseModel):
    """Work experience entry"""

    company: str
    title: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_current: bool = False
    description: str | None = None
    location: str | None = None


class Education(BaseModel):
    """Education entry"""

    institution: str
    degree: str
    field_of_study: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    grade: str | None = None


class SocialProfile(BaseModel):
    """Social media profile"""

    platform: str
    url: str
    username: str | None = None
    verified: bool = False


class CandidateProfile(BaseModel):
    """Comprehensive candidate profile"""

    # Basic Information
    id: str | None = None
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    location: str | None = None

    # Professional Data
    current_role: str | None = None
    current_company: str | None = None
    experience_years: int | None = None
    experience: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)

    # Social & Portfolio
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    social_profiles: list[SocialProfile] = Field(default_factory=list)

    # AI-Generated Insights
    ai_summary: str | None = None
    match_score: float | None = Field(None, ge=0, le=100)
    quality_score: float | None = Field(None, ge=0, le=100)

    # Process Tracking
    status: CandidateStatus = CandidateStatus.NEW
    source: CandidateSource | None = None
    source_notes: str | None = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat()}


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

    id: str | None = None
    channel: OutreachChannel
    subject: str | None = None
    message: str
    sent_at: datetime | None = None
    status: OutreachStatus = OutreachStatus.PENDING
    opened_at: datetime | None = None
    replied_at: datetime | None = None
    response_text: str | None = None


class EngagementHistory(BaseModel):
    """Complete engagement history for a candidate"""

    candidate_id: str
    project_id: str
    total_attempts: int = 0
    channels_used: list[OutreachChannel] = Field(default_factory=list)
    outreach_attempts: list[OutreachAttempt] = Field(default_factory=list)
    response_rate: float = Field(0.0, ge=0, le=1)
    engagement_score: float | None = Field(None, ge=0, le=100)
    last_contact_date: datetime | None = None
    next_followup_date: datetime | None = None

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
    trending_frameworks: list[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class CompetitorIntel(BaseModel):
    """Competitor intelligence data"""

    company_name: str
    location: str
    open_positions: int = 0
    hiring_rate: str = "unknown"  # "low", "medium", "high"
    avg_tenure_months: float | None = None
    benefits_score: float | None = Field(None, ge=0, le=10)
    culture_rating: float | None = Field(None, ge=0, le=5)
    data_source: str = "unknown"


class MarketInsight(BaseModel):
    """Market intelligence aggregation"""

    job_title: str
    location: str | None = None
    industry: str | None = None
    salary_trends: list[SalaryTrend] = Field(default_factory=list)
    competitor_data: list[CompetitorIntel] = Field(default_factory=list)
    in_demand_skills: list[str] = Field(default_factory=list)
    talent_availability: str | None = None  # "high", "medium", "low"
    market_saturation: float | None = Field(None, ge=0, le=1)
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
    target_agent: str | None = None  # None = broadcast
    message_type: MessageType
    payload: dict[str, Any]
    priority: MessagePriority = MessagePriority.MEDIUM
    correlation_id: str | None = None
    trace_id: str | None = None

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
    active_agents: list[str] = Field(default_factory=list)
    candidates_found: int = 0
    candidates_contacted: int = 0
    candidates_responded: int = 0
    interviews_scheduled: int = 0
    interviews_completed: int = 0
    started_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    class Config:
        use_enum_values = True


class InterviewResult(BaseModel):
    """Interview results from Vetta AI"""

    session_id: str
    candidate_id: str
    project_id: str
    questions: list[dict[str, Any]]
    responses: list[dict[str, Any]]
    overall_score: float = Field(..., ge=0, le=100)
    technical_score: float | None = Field(None, ge=0, le=100)
    communication_score: float | None = Field(None, ge=0, le=100)
    cultural_fit_score: float | None = Field(None, ge=0, le=100)
    recommendation: str  # "hire", "maybe", "reject"
    key_insights: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    conducted_at: datetime = Field(default_factory=datetime.utcnow)
