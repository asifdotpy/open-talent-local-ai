"""Voice models for the Avatar Service.
"""

from typing import Optional

from pydantic import BaseModel


class VoiceRequest(BaseModel):
    """Request model for voice generation."""

    text: str
    voice_id: Optional[str] = None
    model_id: str = "piper_en_us"

    model_config = {"protected_namespaces": ()}


class VoiceResponse(BaseModel):
    """Response model for voice generation."""

    success: bool
    audio_url: Optional[str] = None
    error: Optional[str] = None


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

    primary_us_voice: str
    us_voices: list[VoiceInfo]
    total_voices: int
