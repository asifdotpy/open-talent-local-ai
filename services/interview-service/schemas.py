"""Interview Service - Comprehensive Pydantic V2 Schemas
Generated: December 17, 2025
Coverage: 49 endpoints with full type safety.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

# ============================================================================
# ENUMS - Type-Safe Status Fields
# ============================================================================

class InterviewStatus(str, Enum):
    """Interview status."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class InterviewType(str, Enum):
    """Interview type."""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    CODING_CHALLENGE = "coding_challenge"
    HR_SCREENING = "hr_screening"
    FINAL_ROUND = "final_round"
    CULTURAL_FIT = "cultural_fit"


class InterviewMode(str, Enum):
    """Interview mode."""
    VIDEO = "video"
    PHONE = "phone"
    IN_PERSON = "in_person"
    ONLINE_ASSESSMENT = "online_assessment"


class RoomStatus(str, Enum):
    """Interview room status."""
    ACTIVE = "active"
    WAITING = "waiting"
    CLOSED = "closed"
    PAUSED = "paused"
    ERROR = "error"


class ParticipantRole(str, Enum):
    """Participant role."""
    CANDIDATE = "candidate"
    INTERVIEWER = "interviewer"
    OBSERVER = "observer"
    MODERATOR = "moderator"


class QuestionDifficulty(str, Enum):
    """Question difficulty level."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class QuestionType(str, Enum):
    """Question type."""
    CODING = "coding"
    ALGORITHM = "algorithm"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"
    TECHNICAL_CONCEPT = "technical_concept"
    CASE_STUDY = "case_study"


class FeedbackSentiment(str, Enum):
    """Feedback sentiment."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


# ============================================================================
# INTERVIEW ROOM SCHEMAS
# ============================================================================

class RoomBase(BaseModel):
    """Base room model."""
    interview_id: str | None = None
    candidate_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    interview_type: InterviewType
    scheduled_start: datetime
    scheduled_end: datetime
    status: RoomStatus = RoomStatus.WAITING


class RoomCreate(RoomBase):
    """Create room request."""
    interviewer_ids: list[str] | None = None
    question_ids: list[str] | None = None


class RoomUpdate(BaseModel):
    """Update room request."""
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    status: RoomStatus | None = None


class RoomResponse(RoomBase):
    """Room response with metadata."""
    id: str
    room_id: str  # External room ID (WebRTC/video platform)
    created_at: datetime
    updated_at: datetime
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    duration_minutes: int | None = None
    recording_url: HttpUrl | None = None

    model_config = ConfigDict(from_attributes=True)


class RoomListResponse(BaseModel):
    """Paginated room list."""
    items: list[RoomResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RoomJoinRequest(BaseModel):
    """Join room request."""
    room_id: str
    participant_id: str
    role: ParticipantRole


class RoomJoinResponse(BaseModel):
    """Join room response."""
    room_id: str
    join_token: str
    webrtc_config: dict[str, Any]
    expires_at: datetime


# ============================================================================
# PARTICIPANT SCHEMAS
# ============================================================================

class ParticipantBase(BaseModel):
    """Base participant model."""
    user_id: str
    role: ParticipantRole
    joined_at: datetime | None = None
    left_at: datetime | None = None


class ParticipantCreate(ParticipantBase):
    """Create participant request."""
    room_id: str


class ParticipantResponse(ParticipantBase):
    """Participant response with metadata."""
    id: str
    room_id: str
    is_connected: bool
    connection_quality: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ParticipantListResponse(BaseModel):
    """Participant list."""
    items: list[ParticipantResponse]
    total: int


# ============================================================================
# QUESTION SCHEMAS
# ============================================================================

class QuestionBase(BaseModel):
    """Base question model."""
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    question_type: QuestionType
    difficulty: QuestionDifficulty
    tags: list[str] | None = None
    estimated_time_minutes: int | None = Field(None, ge=1, le=180)


class QuestionCreate(QuestionBase):
    """Create question request."""
    correct_answer: str | None = None
    test_cases: list[dict[str, Any]] | None = None
    hints: list[str] | None = None


class QuestionUpdate(BaseModel):
    """Update question request."""
    title: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = None
    question_type: QuestionType | None = None
    difficulty: QuestionDifficulty | None = None
    tags: list[str] | None = None
    estimated_time_minutes: int | None = Field(None, ge=1, le=180)


class QuestionResponse(QuestionBase):
    """Question response with metadata."""
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    average_score: float | None = None

    model_config = ConfigDict(from_attributes=True)


class QuestionListResponse(BaseModel):
    """Paginated question list."""
    items: list[QuestionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# ANSWER/RESPONSE SCHEMAS
# ============================================================================

class CandidateAnswerBase(BaseModel):
    """Base candidate answer model."""
    question_id: str
    answer_text: str | None = None
    code_submission: str | None = None
    time_taken_minutes: int | None = Field(None, ge=0)


class CandidateAnswerCreate(CandidateAnswerBase):
    """Create candidate answer request."""
    room_id: str
    candidate_id: str


class CandidateAnswerResponse(CandidateAnswerBase):
    """Candidate answer response with metadata."""
    id: str
    room_id: str
    candidate_id: str
    submitted_at: datetime
    score: float | None = Field(None, ge=0.0, le=100.0)
    is_correct: bool | None = None
    feedback: str | None = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# FEEDBACK SCHEMAS
# ============================================================================

class FeedbackBase(BaseModel):
    """Base feedback model."""
    rating: int = Field(..., ge=1, le=5)
    technical_skills: int | None = Field(None, ge=1, le=5)
    communication_skills: int | None = Field(None, ge=1, le=5)
    problem_solving: int | None = Field(None, ge=1, le=5)
    cultural_fit: int | None = Field(None, ge=1, le=5)
    comments: str | None = Field(None, max_length=2000)
    strengths: list[str] | None = None
    weaknesses: list[str] | None = None
    recommendation: str | None = Field(None, max_length=500)
    sentiment: FeedbackSentiment | None = None


class FeedbackCreate(FeedbackBase):
    """Create feedback request."""
    room_id: str
    candidate_id: str
    interviewer_id: str


class FeedbackResponse(FeedbackBase):
    """Feedback response with metadata."""
    id: str
    room_id: str
    candidate_id: str
    interviewer_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackListResponse(BaseModel):
    """Paginated feedback list."""
    items: list[FeedbackResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# SCHEDULING SCHEMAS
# ============================================================================

class ScheduleSlotRequest(BaseModel):
    """Schedule slot request."""
    interviewer_id: str
    start_time: datetime
    end_time: datetime


class ScheduleSlotResponse(BaseModel):
    """Available schedule slot."""
    interviewer_id: str
    start_time: datetime
    end_time: datetime
    is_available: bool


class AvailabilityCheckRequest(BaseModel):
    """Check availability request."""
    interviewer_ids: list[str] = Field(..., min_length=1, max_length=10)
    start_date: datetime
    end_date: datetime
    duration_minutes: int = Field(..., ge=15, le=480)


class AvailabilityCheckResponse(BaseModel):
    """Availability check response."""
    available_slots: list[ScheduleSlotResponse]
    total_slots: int


class RescheduleRequest(BaseModel):
    """Reschedule interview request."""
    room_id: str
    new_start_time: datetime
    new_end_time: datetime
    reason: str | None = Field(None, max_length=500)


class RescheduleResponse(BaseModel):
    """Reschedule response."""
    room_id: str
    old_start_time: datetime
    new_start_time: datetime
    notification_sent: bool


# ============================================================================
# RECORDING SCHEMAS
# ============================================================================

class RecordingBase(BaseModel):
    """Base recording model."""
    room_id: str
    file_url: HttpUrl
    file_size_bytes: int = Field(..., ge=0)
    duration_seconds: int = Field(..., ge=0)
    format: str = Field(..., pattern=r'^(mp4|webm|mkv)$')


class RecordingCreate(RecordingBase):
    """Create recording request."""
    pass


class RecordingResponse(RecordingBase):
    """Recording response with metadata."""
    id: str
    created_at: datetime
    transcript_url: HttpUrl | None = None
    thumbnail_url: HttpUrl | None = None

    model_config = ConfigDict(from_attributes=True)


class RecordingListResponse(BaseModel):
    """Paginated recording list."""
    items: list[RecordingResponse]
    total: int


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================

class InterviewAnalyticsRequest(BaseModel):
    """Interview analytics request."""
    start_date: datetime
    end_date: datetime
    interviewer_ids: list[str] | None = None
    interview_types: list[InterviewType] | None = None


class InterviewAnalyticsResponse(BaseModel):
    """Interview analytics response."""
    total_interviews: int
    completed_interviews: int
    cancelled_interviews: int
    no_show_count: int
    average_duration_minutes: float | None = None
    average_rating: float | None = None
    interviews_by_type: dict[str, int]
    interviews_by_status: dict[str, int]
    top_performers: list[dict[str, Any]]


class CandidatePerformanceRequest(BaseModel):
    """Candidate performance request."""
    candidate_id: str
    include_answers: bool = False
    include_feedback: bool = False


class CandidatePerformanceResponse(BaseModel):
    """Candidate performance response."""
    candidate_id: str
    total_interviews: int
    average_rating: float | None = None
    average_technical_score: float | None = None
    average_communication_score: float | None = None
    strengths: list[str]
    areas_for_improvement: list[str]
    recent_interviews: list[RoomResponse]


# ============================================================================
# NOTIFICATION SCHEMAS
# ============================================================================

class InterviewNotificationRequest(BaseModel):
    """Interview notification request."""
    room_id: str
    recipient_ids: list[str] = Field(..., min_length=1)
    notification_type: str = Field(..., pattern=r'^(scheduled|reminder|cancelled|rescheduled|feedback)$')
    message: str | None = Field(None, max_length=500)


class InterviewNotificationResponse(BaseModel):
    """Notification response."""
    room_id: str
    sent_count: int
    failed_count: int
    failed_recipients: list[str]


# ============================================================================
# SEARCH & FILTER SCHEMAS
# ============================================================================

class InterviewSearchRequest(BaseModel):
    """Interview search request."""
    query: str | None = Field(None, max_length=200)
    status: list[InterviewStatus] | None = None
    interview_type: list[InterviewType] | None = None
    candidate_ids: list[str] | None = None
    interviewer_ids: list[str] | None = None
    scheduled_after: datetime | None = None
    scheduled_before: datetime | None = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str | None = Field(None, pattern=r'^(created_at|scheduled_start|actual_start|duration_minutes)$')
    sort_order: str | None = Field("desc", pattern=r'^(asc|desc)$')


# ============================================================================
# HEALTH & SERVICE INFO
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Service health check."""
    status: str
    timestamp: datetime
    version: str
    database_connected: bool
    active_rooms: int


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: str | None = None
    timestamp: datetime


class InterviewServiceInfo(BaseModel):
    """Service information."""
    name: str = "Interview Service"
    version: str
    endpoints_count: int
    active_rooms: int
    total_interviews_today: int
