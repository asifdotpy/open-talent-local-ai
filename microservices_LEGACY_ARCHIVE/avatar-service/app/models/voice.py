"""Voice models for the Avatar Service."""

from pydantic import BaseModel


class VoiceRequest(BaseModel):
    """Request model for voice generation."""

    text: str
    voice_id: str | None = None
    model_id: str = "eleven_multilingual_v2"


class VoiceResponse(BaseModel):
    """Response model for voice generation."""

    success: bool
    audio_url: str | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    voice_integration: str


class VoiceInfo(BaseModel):
    """Voice information model."""

    voice_id: str
    name: str
    category: str
    description: str
    is_primary: bool


class VoiceListResponse(BaseModel):
    """Response model for voice listing."""

    primary_irish_voice: str
    irish_voices: list[VoiceInfo]
    total_voices: int
