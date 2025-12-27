"""Voice generation API routes."""

from fastapi import APIRouter

from app.models.voice import VoiceListResponse, VoiceRequest, VoiceResponse
from app.services.voice_service import voice_service

router = APIRouter()


@router.post("/api/v1/generate-voice", response_model=VoiceResponse, tags=["Voice"])
async def generate_us_voice(request: VoiceRequest):
    """Generate US English female voice from text using local AI Voice (planned)."""
    return await voice_service.generate_us_voice(request)


@router.get("/api/v1/voices", response_model=VoiceListResponse, tags=["Voice"])
async def list_available_voices():
    """List available local AI voices (US English planned)."""
    return await voice_service.list_available_voices()
