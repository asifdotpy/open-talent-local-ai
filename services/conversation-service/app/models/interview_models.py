from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class Question(BaseModel):
    """Data model for a single interview question."""

    id: int
    text: str
    category: str
    expected_duration_seconds: int


class GenerateQuestionsRequest(BaseModel):
    """Data model for the request body of the /conversation/generate-questions endpoint."""

    job_description: str
    job_title: Optional[str] = None
    num_questions: int = Field(default=10, gt=0, le=20)  # Greater than 0, less than or equal to 20
    difficulty: str = Field(default="medium")


class GenerateQuestionsResponse(BaseModel):
    """Data model for the response body of the /conversation/generate-questions endpoint."""

    questions: list[Question]


class StartConversationRequest(BaseModel):
    """Request to start a new interview conversation."""

    session_id: str
    job_description: str
    candidate_profile: Optional[dict[str, Any]] = None
    interview_type: str = "technical"
    tone: str = "professional"


class StartConversationResponse(BaseModel):
    """Response when starting a conversation."""

    conversation_id: str
    session_id: str
    initial_message: str
    status: str = "started"


class SendMessageRequest(BaseModel):
    """Request to send a message in an active conversation."""

    session_id: str
    message: str
    message_type: str = "transcript"  # transcript, user_input, system
    metadata: Optional[dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Response from the conversation service."""

    conversation_id: str
    session_id: str
    response_text: str
    response_type: str  # question, feedback, instruction, conclusion
    should_speak: bool = True
    metadata: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationStatus(BaseModel):
    """Status of an active conversation."""

    conversation_id: str
    session_id: str
    status: str  # active, paused, completed
    message_count: int
    last_activity: datetime
    current_topic: Optional[str] = None


# --- New Models for Adaptive Question Generation ---
class AdaptiveQuestionRequest(BaseModel):
    """Request for generating adaptive interview questions."""

    room_id: str
    session_id: str
    previous_responses: list[dict[str, Any]] = []
    expertise_level: str = "intermediate"
    job_requirements: str = ""
    question_number: int = 1
    interview_phase: str = "technical"
    bias_mitigation: bool = True


class InterviewQuestion(BaseModel):
    """Model for an interview question."""

    id: str
    text: str
    order: int
    generated_at: str
    ai_metadata: dict[str, Any] = {}


class QuestionGenerationResponse(BaseModel):
    """Response for adaptive question generation."""

    question: InterviewQuestion
    question_number: int
    ai_metadata: dict[str, Any] = {}
    estimated_difficulty: str = "medium"
    bias_mitigation_applied: bool = False


class FollowupQuestion(BaseModel):
    """Model for a follow-up question."""

    question: str
    priority: int = 1
    reasoning: str = ""
    expected_outcome: str = ""


class FollowupRequest(BaseModel):
    """Request for generating follow-up questions."""

    response_text: str
    question_context: str
    sentiment: dict[str, Any] = {}
    quality: dict[str, Any] = {}


class FollowupResponse(BaseModel):
    """Response for follow-up question generation."""

    questions: list[FollowupQuestion] = []


class InterviewAdaptationRequest(BaseModel):
    """Request for interview adaptation recommendations."""

    current_phase: str
    time_remaining_minutes: int
    performance_indicators: dict[str, Any] = {}


class InterviewAdaptation(BaseModel):
    """Model for interview adaptation recommendations."""

    question_difficulty: str = "medium"
    focus_areas: list[str] = ["technical_skills", "problem_solving"]
    time_adjustments: dict[str, Any] = {}
    immediate_actions: list[str] = []
    strategy_changes: list[str] = []


class AdaptationResponse(BaseModel):
    """Response for interview adaptation."""

    adaptations: InterviewAdaptation
    recommendations: list[str] = []
