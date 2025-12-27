"""Pydantic models for request/response validation."""

from datetime import datetime
from typing import Any, Optional

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

    sessionId: Optional[str] = Field(None, description="Session ID (optional)")
    message: str = Field(..., description="User's response message")
    session: Optional[InterviewSession] = Field(
        None, description="Full session (client can send entire session)"
    )


class ServiceHealth(BaseModel):
    """Service health status."""

    name: str
    status: str  # "online" | "degraded" | "offline"
    latencyMs: Optional[float] = None
    error: Optional[str] = None
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
    dataset: Optional[str] = Field(None, description="Training dataset")
    source: Optional[str] = Field(None, description="Model source")


class ModelsResponse(BaseModel):
    """Response with list of models."""

    models: list[ModelInfo]


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error message")
    timestamp: datetime
    details: Optional[dict[str, Any]] = None
