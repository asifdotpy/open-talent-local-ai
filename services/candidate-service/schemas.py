"""Candidate Service - Comprehensive Pydantic V2 Schemas
Generated: December 17, 2025
Coverage: 76 endpoints with full type safety.
"""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

# ============================================================================
# ENUMS - Type-Safe Status Fields
# ============================================================================

class CandidateStatus(str, Enum):
    """Candidate application status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    INTERVIEWING = "interviewing"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ApplicationStatus(str, Enum):
    """Application lifecycle status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    SCREENING = "screening"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWING = "interviewing"
    OFFER_PENDING = "offer_pending"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_REJECTED = "offer_rejected"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class SkillLevel(str, Enum):
    """Skill proficiency level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class EducationLevel(str, Enum):
    """Education degree level."""
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"
    BOOTCAMP = "bootcamp"
    CERTIFICATION = "certification"


class EmploymentType(str, Enum):
    """Employment type."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


# ============================================================================
# LEGACY MODELS (keep for backward compatibility)
# ============================================================================

class ProfileSource(BaseModel):
    """Records the origin of the candidate data."""
    source_name: Literal['ContactOut', 'SalesQL', 'LinkedIn', 'Manual']
    source_id: str | None = None # The record ID from the external system
    retrieved_at: date

class WorkExperience(BaseModel):
    """Represents a single position in a candidate's work history."""
    position: str
    company: str
    start_date: date
    end_date: date | None = None
    description: str | None = None

class Education(BaseModel):
    """Represents an entry in a candidate's education history."""
    institution: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: date | None = None

class SocialProfile(BaseModel):
    """Links to social and professional profiles."""
    network: Literal['LinkedIn', 'GitHub', 'Twitter', 'Portfolio']
    url: HttpUrl

class EnrichedProfile(BaseModel):
    """A universal data model to accommodate data from ContactOut and other
    sourcing tools, designed to be compatible with the Agent-Interview bridge.
    """
    source: ProfileSource
    work_history: list[WorkExperience] = []
    education_history: list[Education] = []
    social_profiles: list[SocialProfile] = []
    contact_email: str | None = None
    contact_phone: str | None = None


# ============================================================================
# CORE CANDIDATE SCHEMAS
# ============================================================================

class CandidateBase(BaseModel):
    """Base candidate model."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')  # E.164 format
    linkedin_url: HttpUrl | None = None
    github_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None
    location: str | None = Field(None, max_length=200)
    status: CandidateStatus = CandidateStatus.ACTIVE
    bio: str | None = Field(None, max_length=2000)
    years_of_experience: int | None = Field(None, ge=0, le=50)
    current_title: str | None = Field(None, max_length=200)
    current_company: str | None = Field(None, max_length=200)


class CandidateCreate(CandidateBase):
    """Create candidate request."""
    user_id: str | None = None
    source: str | None = Field(None, max_length=100)  # Referral, job board, etc.
    referred_by: str | None = None  # User ID of referrer


class CandidateUpdate(BaseModel):
    """Update candidate request."""
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    linkedin_url: HttpUrl | None = None
    github_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None
    location: str | None = Field(None, max_length=200)
    status: CandidateStatus | None = None
    bio: str | None = Field(None, max_length=2000)
    years_of_experience: int | None = Field(None, ge=0, le=50)
    current_title: str | None = Field(None, max_length=200)
    current_company: str | None = Field(None, max_length=200)


class CandidateResponse(CandidateBase):
    """Candidate response with metadata."""
    id: str
    user_id: str | None
    created_at: datetime
    updated_at: datetime
    last_activity: datetime | None = None
    applications_count: int = 0
    interviews_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class CandidateListResponse(BaseModel):
    """Paginated candidate list."""
    items: list[CandidateResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# SKILLS SCHEMAS
# ============================================================================

class SkillBase(BaseModel):
    """Base skill model."""
    name: str = Field(..., min_length=1, max_length=100)
    level: SkillLevel
    years_of_experience: int | None = Field(None, ge=0, le=50)
    category: str | None = Field(None, max_length=100)  # e.g., "Programming", "Framework"


class SkillCreate(SkillBase):
    """Create skill request."""
    pass


class SkillResponse(SkillBase):
    """Skill response with metadata."""
    id: str
    candidate_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# APPLICATION SCHEMAS
# ============================================================================

class ApplicationBase(BaseModel):
    """Base application model."""
    job_id: str
    cover_letter: str | None = Field(None, max_length=5000)
    status: ApplicationStatus = ApplicationStatus.DRAFT
    expected_salary: int | None = Field(None, ge=0)
    available_start_date: date | None = None
    notes: str | None = Field(None, max_length=2000)


class ApplicationCreate(ApplicationBase):
    """Create application request."""
    candidate_id: str | None = None  # Auto-detected from auth if not provided


class ApplicationUpdate(BaseModel):
    """Update application request."""
    cover_letter: str | None = Field(None, max_length=5000)
    status: ApplicationStatus | None = None
    expected_salary: int | None = Field(None, ge=0)
    available_start_date: date | None = None
    notes: str | None = Field(None, max_length=2000)


class ApplicationResponse(ApplicationBase):
    """Application response with metadata."""
    id: str
    candidate_id: str
    created_at: datetime
    updated_at: datetime
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None  # Recruiter ID

    model_config = ConfigDict(from_attributes=True)


class ApplicationListResponse(BaseModel):
    """Paginated application list."""
    items: list[ApplicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# SEARCH & ANALYTICS SCHEMAS
# ============================================================================

class CandidateSearchRequest(BaseModel):
    """Candidate search request."""
    query: str | None = Field(None, max_length=200)
    status: list[CandidateStatus] | None = None
    skills: list[str] | None = None
    min_years_experience: int | None = Field(None, ge=0)
    max_years_experience: int | None = Field(None, le=50)
    location: str | None = Field(None, max_length=200)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str | None = Field(None, pattern=r'^(created_at|updated_at|last_activity|years_of_experience)$')
    sort_order: str | None = Field("desc", pattern=r'^(asc|desc)$')


class BulkApplicationUpdateRequest(BaseModel):
    """Bulk application status update."""
    application_ids: list[str] = Field(..., min_length=1, max_length=100)
    status: ApplicationStatus
    notes: str | None = Field(None, max_length=500)


class BulkApplicationUpdateResponse(BaseModel):
    """Bulk update response."""
    updated_count: int
    failed_count: int
    failed_ids: list[str]


# ============================================================================
# HEALTH & SERVICE INFO
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Service health check."""
    status: str
    timestamp: datetime
    version: str
    database_connected: bool


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: str | None = None
    timestamp: datetime

