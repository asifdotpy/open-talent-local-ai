"""Pydantic models for request/response validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Message in interview conversation."""

    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class InterviewConfig(BaseModel):
    """Interview configuration."""

    role: str = Field(..., description="Interview role")
    model: str = Field(..., description="Model to use")
    totalQuestions: int = Field(5, description="Total questions in interview")


class InterviewSession(BaseModel):
    """Interview session data matching desktop app contract."""

    config: InterviewConfig
    messages: list[Message]
    currentQuestion: int
    isComplete: bool


class StartInterviewRequest(BaseModel):
    """Request to start an interview."""

    role: str = Field(
        ..., description="Interview role (Software Engineer, Product Manager, Data Analyst)"
    )
    model: str = Field("vetta-granite-2b-gguf-v4", description="Model to use")
    totalQuestions: int = Field(5, description="Total questions")


class InterviewResponseRequest(BaseModel):
    """Request to respond to interview question."""

    sessionId: str | None = Field(None, description="Session ID (optional)")
    message: str = Field(..., description="User's response message")
    session: InterviewSession | None = Field(
        None, description="Full session (client can send entire session)"
    )


class ServiceHealth(BaseModel):
    """Service health status."""

    name: str
    status: str  # "online" | "degraded" | "offline"
    latencyMs: float | None = None
    error: str | None = None
    lastChecked: datetime


class HealthResponse(BaseModel):
    """Health check response."""

    status: str  # "online" | "degraded" | "offline"
    timestamp: datetime
    services: dict[str, Any]
    summary: dict[str, Any]


class ModelInfo(BaseModel):
    """Model information."""

    id: str = Field(..., description="Model ID")
    name: str = Field(..., description="Human-readable name")
    paramCount: str = Field(..., description="Parameter count (350M, 2B, 8B, etc.)")
    ramRequired: str = Field(..., description="RAM required")
    downloadSize: str = Field(..., description="Download size")
    description: str = Field(..., description="Model description")
    dataset: str | None = Field(None, description="Training dataset")
    source: str | None = Field(None, description="Model source")


class ModelsResponse(BaseModel):
    """Response with list of models."""

    models: list[ModelInfo]


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error message")
    timestamp: datetime
    details: dict[str, Any] | None = None


class SynthesizeSpeechRequest(BaseModel):
    """Request to synthesize speech from text."""

    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    voice: str = Field(
        "en-US-Neural2-C", description="Voice identifier (e.g., en-US-Neural2-C, en-GB-Neural2-A)"
    )
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)")
    pitch: int = Field(0, ge=-20, le=20, description="Pitch adjustment (-20 to 20)")


class SynthesizeSpeechResponse(BaseModel):
    """Response with synthesized audio."""

    audioUrl: str | None = Field(None, description="URL to audio file")
    audioBase64: str | None = Field(None, description="Base64-encoded audio")
    duration: float | None = Field(None, description="Audio duration in seconds")
    format: str = Field("mp3", description="Audio format (mp3, wav, ogg)")
    text: str = Field(..., description="Text that was synthesized")
    voice: str = Field(..., description="Voice used")


class AnalyzeSentimentRequest(BaseModel):
    """Request to analyze sentiment of text."""

    text: str = Field(..., min_length=1, max_length=5000, description="Text to analyze")
    context: str | None = Field(
        None, description="Context for analysis (e.g., 'interview_response', 'general')"
    )


class SentimentScore(BaseModel):
    """Sentiment analysis result."""

    score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score (-1.0 to 1.0)")
    magnitude: float = Field(..., ge=0.0, le=1.0, description="Sentiment magnitude (0.0 to 1.0)")
    label: str = Field(..., description="Sentiment label (positive, negative, neutral)")


class AnalyzeSentimentResponse(BaseModel):
    """Response with sentiment analysis."""

    sentiment: SentimentScore = Field(..., description="Sentiment analysis")
    text: str = Field(..., description="Text that was analyzed")
    context: str | None = Field(None, description="Analysis context")
    sentences: list[dict[str, Any]] | None = Field(None, description="Per-sentence analysis")
