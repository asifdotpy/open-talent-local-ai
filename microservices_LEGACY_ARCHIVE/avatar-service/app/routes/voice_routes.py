"""
Voice generation API routes.
"""

from fastapi import APIRouter

from app.models.voice import VoiceRequest, VoiceResponse, HealthResponse, VoiceListResponse
from app.services.voice_service import voice_service

router = APIRouter()


@router.get("/", response_model=dict, tags=["Status"])
async def read_root():
    """Root endpoint for the Avatar Service."""
    return {"message": "Avatar Service with Irish Voice is running!"}


@router.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """Health check endpoint for the Avatar Service."""
    return HealthResponse(status="healthy", voice_integration="AI Voice")


@router.post("/api/v1/generate-voice", response_model=VoiceResponse, tags=["Voice"])
async def generate_irish_voice(request: VoiceRequest):
    """Generate Irish female voice from text using AI Voice API."""
    return await voice_service.generate_irish_voice(request)


@router.get("/api/v1/voices", response_model=VoiceListResponse, tags=["Voice"])
async def list_available_voices():
    """List available AI Voice voices including Labhaoise (Irish)."""
    return await voice_service.list_available_voices()
