"""
Interview Service - Comprehensive Pydantic V2 Schemas
Generated: December 17, 2025
Coverage: 49 endpoints with full type safety
"""

from pydantic import BaseModel, Field, EmailStr, HttpUrl, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# ============================================================================
# ENUMS - Type-Safe Status Fields
# ============================================================================

class InterviewStatus(str, Enum):
    """Interview status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class InterviewType(str, Enum):
    """Interview type"""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    CODING_CHALLENGE = "coding_challenge"
    HR_SCREENING = "hr_screening"
    FINAL_ROUND = "final_round"
    CULTURAL_FIT = "cultural_fit"


class InterviewMode(str, Enum):
    """Interview mode"""
    VIDEO = "video"
    PHONE = "phone"
    IN_PERSON = "in_person"
    ONLINE_ASSESSMENT = "online_assessment"


class RoomStatus(str, Enum):
    """Interview room status"""
    ACTIVE = "active"
    WAITING = "waiting"
    CLOSED = "closed"
    PAUSED = "paused"
    ERROR = "error"


class ParticipantRole(str, Enum):
    """Participant role"""
    CANDIDATE = "candidate"
    INTERVIEWER = "interviewer"
    OBSERVER = "observer"
    MODERATOR = "moderator"


class QuestionDifficulty(str, Enum):
    """Question difficulty level"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class QuestionType(str, Enum):
    """Question type"""
    CODING = "coding"
    ALGORITHM = "algorithm"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"
    TECHNICAL_CONCEPT = "technical_concept"
    CASE_STUDY = "case_study"


class FeedbackSentiment(str, Enum):
    """Feedback sentiment"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


# ============================================================================
# INTERVIEW ROOM SCHEMAS
# ============================================================================

class RoomBase(BaseModel):
    """Base room model"""
    interview_id: Optional[str] = None
    candidate_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    interview_type: InterviewType
    scheduled_start: datetime
    scheduled_end: datetime
    status: RoomStatus = RoomStatus.WAITING


class RoomCreate(RoomBase):
    """Create room request"""
    interviewer_ids: Optional[List[str]] = None
    question_ids: Optional[List[str]] = None


class RoomUpdate(BaseModel):
    """Update room request"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    status: Optional[RoomStatus] = None


class RoomResponse(RoomBase):
    """Room response with metadata"""
    id: str
    room_id: str  # External room ID (WebRTC/video platform)
    created_at: datetime
    updated_at: datetime
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    recording_url: Optional[HttpUrl] = None
    
    model_config = ConfigDict(from_attributes=True)


class RoomListResponse(BaseModel):
    """Paginated room list"""
    items: List[RoomResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RoomJoinRequest(BaseModel):
    """Join room request"""
    room_id: str
    participant_id: str
    role: ParticipantRole


class RoomJoinResponse(BaseModel):
    """Join room response"""
    room_id: str
    join_token: str
    webrtc_config: Dict[str, Any]
    expires_at: datetime


# ============================================================================
# PARTICIPANT SCHEMAS
# ============================================================================

class ParticipantBase(BaseModel):
    """Base participant model"""
    user_id: str
    role: ParticipantRole
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None


class ParticipantCreate(ParticipantBase):
    """Create participant request"""
    room_id: str


class ParticipantResponse(ParticipantBase):
    """Participant response with metadata"""
    id: str
    room_id: str
    is_connected: bool
    connection_quality: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ParticipantListResponse(BaseModel):
    """Participant list"""
    items: List[ParticipantResponse]
    total: int


# ============================================================================
# QUESTION SCHEMAS
# ============================================================================

class QuestionBase(BaseModel):
    """Base question model"""
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    question_type: QuestionType
    difficulty: QuestionDifficulty
    tags: Optional[List[str]] = None
    estimated_time_minutes: Optional[int] = Field(None, ge=1, le=180)


class QuestionCreate(QuestionBase):
    """Create question request"""
    correct_answer: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    hints: Optional[List[str]] = None


class QuestionUpdate(BaseModel):
    """Update question request"""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    question_type: Optional[QuestionType] = None
    difficulty: Optional[QuestionDifficulty] = None
    tags: Optional[List[str]] = None
    estimated_time_minutes: Optional[int] = Field(None, ge=1, le=180)


class QuestionResponse(QuestionBase):
    """Question response with metadata"""
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    average_score: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class QuestionListResponse(BaseModel):
    """Paginated question list"""
    items: List[QuestionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# ANSWER/RESPONSE SCHEMAS
# ============================================================================

class CandidateAnswerBase(BaseModel):
    """Base candidate answer model"""
    question_id: str
    answer_text: Optional[str] = None
    code_submission: Optional[str] = None
    time_taken_minutes: Optional[int] = Field(None, ge=0)


class CandidateAnswerCreate(CandidateAnswerBase):
    """Create candidate answer request"""
    room_id: str
    candidate_id: str


class CandidateAnswerResponse(CandidateAnswerBase):
    """Candidate answer response with metadata"""
    id: str
    room_id: str
    candidate_id: str
    submitted_at: datetime
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    is_correct: Optional[bool] = None
    feedback: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# FEEDBACK SCHEMAS
# ============================================================================

class FeedbackBase(BaseModel):
    """Base feedback model"""
    rating: int = Field(..., ge=1, le=5)
    technical_skills: Optional[int] = Field(None, ge=1, le=5)
    communication_skills: Optional[int] = Field(None, ge=1, le=5)
    problem_solving: Optional[int] = Field(None, ge=1, le=5)
    cultural_fit: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=2000)
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    recommendation: Optional[str] = Field(None, max_length=500)
    sentiment: Optional[FeedbackSentiment] = None


class FeedbackCreate(FeedbackBase):
    """Create feedback request"""
    room_id: str
    candidate_id: str
    interviewer_id: str


class FeedbackResponse(FeedbackBase):
    """Feedback response with metadata"""
    id: str
    room_id: str
    candidate_id: str
    interviewer_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackListResponse(BaseModel):
    """Paginated feedback list"""
    items: List[FeedbackResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# SCHEDULING SCHEMAS
# ============================================================================

class ScheduleSlotRequest(BaseModel):
    """Schedule slot request"""
    interviewer_id: str
    start_time: datetime
    end_time: datetime


class ScheduleSlotResponse(BaseModel):
    """Available schedule slot"""
    interviewer_id: str
    start_time: datetime
    end_time: datetime
    is_available: bool


class AvailabilityCheckRequest(BaseModel):
    """Check availability request"""
    interviewer_ids: List[str] = Field(..., min_length=1, max_length=10)
    start_date: datetime
    end_date: datetime
    duration_minutes: int = Field(..., ge=15, le=480)


class AvailabilityCheckResponse(BaseModel):
    """Availability check response"""
    available_slots: List[ScheduleSlotResponse]
    total_slots: int


class RescheduleRequest(BaseModel):
    """Reschedule interview request"""
    room_id: str
    new_start_time: datetime
    new_end_time: datetime
    reason: Optional[str] = Field(None, max_length=500)


class RescheduleResponse(BaseModel):
    """Reschedule response"""
    room_id: str
    old_start_time: datetime
    new_start_time: datetime
    notification_sent: bool


# ============================================================================
# RECORDING SCHEMAS
# ============================================================================

class RecordingBase(BaseModel):
    """Base recording model"""
    room_id: str
    file_url: HttpUrl
    file_size_bytes: int = Field(..., ge=0)
    duration_seconds: int = Field(..., ge=0)
    format: str = Field(..., pattern=r'^(mp4|webm|mkv)$')


class RecordingCreate(RecordingBase):
    """Create recording request"""
    pass


class RecordingResponse(RecordingBase):
    """Recording response with metadata"""
    id: str
    created_at: datetime
    transcript_url: Optional[HttpUrl] = None
    thumbnail_url: Optional[HttpUrl] = None
    
    model_config = ConfigDict(from_attributes=True)


class RecordingListResponse(BaseModel):
    """Paginated recording list"""
    items: List[RecordingResponse]
    total: int


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================

class InterviewAnalyticsRequest(BaseModel):
    """Interview analytics request"""
    start_date: datetime
    end_date: datetime
    interviewer_ids: Optional[List[str]] = None
    interview_types: Optional[List[InterviewType]] = None


class InterviewAnalyticsResponse(BaseModel):
    """Interview analytics response"""
    total_interviews: int
    completed_interviews: int
    cancelled_interviews: int
    no_show_count: int
    average_duration_minutes: Optional[float] = None
    average_rating: Optional[float] = None
    interviews_by_type: Dict[str, int]
    interviews_by_status: Dict[str, int]
    top_performers: List[Dict[str, Any]]


class CandidatePerformanceRequest(BaseModel):
    """Candidate performance request"""
    candidate_id: str
    include_answers: bool = False
    include_feedback: bool = False


class CandidatePerformanceResponse(BaseModel):
    """Candidate performance response"""
    candidate_id: str
    total_interviews: int
    average_rating: Optional[float] = None
    average_technical_score: Optional[float] = None
    average_communication_score: Optional[float] = None
    strengths: List[str]
    areas_for_improvement: List[str]
    recent_interviews: List[RoomResponse]


# ============================================================================
# NOTIFICATION SCHEMAS
# ============================================================================

class InterviewNotificationRequest(BaseModel):
    """Interview notification request"""
    room_id: str
    recipient_ids: List[str] = Field(..., min_length=1)
    notification_type: str = Field(..., pattern=r'^(scheduled|reminder|cancelled|rescheduled|feedback)$')
    message: Optional[str] = Field(None, max_length=500)


class InterviewNotificationResponse(BaseModel):
    """Notification response"""
    room_id: str
    sent_count: int
    failed_count: int
    failed_recipients: List[str]


# ============================================================================
# SEARCH & FILTER SCHEMAS
# ============================================================================

class InterviewSearchRequest(BaseModel):
    """Interview search request"""
    query: Optional[str] = Field(None, max_length=200)
    status: Optional[List[InterviewStatus]] = None
    interview_type: Optional[List[InterviewType]] = None
    candidate_ids: Optional[List[str]] = None
    interviewer_ids: Optional[List[str]] = None
    scheduled_after: Optional[datetime] = None
    scheduled_before: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = Field(None, pattern=r'^(created_at|scheduled_start|actual_start|duration_minutes)$')
    sort_order: Optional[str] = Field("desc", pattern=r'^(asc|desc)$')


# ============================================================================
# HEALTH & SERVICE INFO
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Service health check"""
    status: str
    timestamp: datetime
    version: str
    database_connected: bool
    active_rooms: int


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime


class InterviewServiceInfo(BaseModel):
    """Service information"""
    name: str = "Interview Service"
    version: str
    endpoints_count: int
    active_rooms: int
    total_interviews_today: int
