"""
Avatar Routes for TalentAI Platform.

Endpoints for avatar video generation and management.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
import logging
import io
import httpx
import os
from pathlib import Path

from app.services.avatar_rendering_service import AvatarRenderingService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize service
avatar_service = AvatarRenderingService()

class AvatarRequest(BaseModel):
    """Request model for avatar generation."""
    text: str
    voice: Optional[str] = "en_US-lessac-medium"
    avatar_id: Optional[str] = "default"

class PhonemeData(BaseModel):
    """Phoneme timing data."""
    phoneme: str
    start_time: float
    end_time: float

# Global storage for current session phonemes and audio
current_session = {
    "audio_url": None,
    "phonemes": None
}

@router.get("/src/{path:path}")
async def serve_src_files(path: str):
    """Serve JavaScript source files from shared ai-orchestra-simulation library."""
    # Security: Check for null bytes and path traversal attempts
    if '\x00' in path or '..' in path or path.startswith('/'):
        logger.warning(f"Blocked malicious src request: {path}")
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Use shared library from ai-orchestra-simulation
        orchestra_path = Path(__file__).parent.parent.parent.parent.parent / "ai-orchestra-simulation" / "src" / path
        
        # Verify the resolved path is still within the src directory
        base_src = Path(__file__).parent.parent.parent.parent.parent / "ai-orchestra-simulation" / "src"
        try:
            orchestra_path.resolve().relative_to(base_src.resolve())
        except ValueError:
            logger.warning(f"Path traversal attempt detected in /src: {path}")
            raise HTTPException(status_code=404, detail="File not found")
        
        if orchestra_path.exists() and orchestra_path.is_file():
            return FileResponse(orchestra_path)
        else:
            raise HTTPException(status_code=404, detail=f"File not found: {path}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve file {path}: {e}")
        raise HTTPException(status_code=404, detail="File not found")

@router.get("/assets/{path:path}")
async def serve_asset_files(path: str):
    """Serve asset files (models, audio, textures) from shared ai-orchestra-simulation library."""
    # Security: Check for null bytes and path traversal attempts
    if '\x00' in path or '..' in path or path.startswith('/'):
        logger.warning(f"Blocked malicious asset request: {path}")
        raise HTTPException(status_code=404, detail="Asset not found")
    
    try:
        # Use shared assets from ai-orchestra-simulation
        orchestra_assets = Path(__file__).parent.parent.parent.parent.parent / "ai-orchestra-simulation" / "assets" / path
        
        # Verify the resolved path is still within the assets directory
        base_assets = Path(__file__).parent.parent.parent.parent.parent / "ai-orchestra-simulation" / "assets"
        try:
            orchestra_assets.resolve().relative_to(base_assets.resolve())
        except ValueError:
            logger.warning(f"Path traversal attempt detected: {path}")
            raise HTTPException(status_code=404, detail="Asset not found")
        
        if orchestra_assets.exists() and orchestra_assets.is_file():
            return FileResponse(orchestra_assets)
        else:
            raise HTTPException(status_code=404, detail=f"Asset not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve asset {path}: {e}")
        raise HTTPException(status_code=404, detail="Asset not found")

@router.post("/generate")
async def generate_avatar_video(request: AvatarRequest):
    """
    Generate avatar video from text.

    This endpoint:
    1. Calls voice service to generate audio and phonemes
    2. Generates avatar video with lip-sync
    3. Returns the video file
    """
    try:
        logger.info(f"Generating avatar video for text: {request.text[:50]}...")

        # Call voice service for TTS
        async with httpx.AsyncClient(timeout=30.0) as client:
            voice_response = await client.post(
                "http://localhost:8002/voice/tts",
                json={
                    "text": request.text,
                    "voice": request.voice,
                    "extract_phonemes": True
                }
            )
            voice_response.raise_for_status()
            
            # Parse JSON response
            voice_data = voice_response.json()
            audio_data = voice_data.get("audio_data")
            duration = voice_data.get("duration", 5.0)
            phonemes = voice_data.get("phonemes", [])
            words = voice_data.get("words", [])

        if not audio_data:
            raise HTTPException(status_code=500, detail="No audio data from voice service")

        logger.info(f"Received audio: {len(audio_data)} bytes, duration: {duration:.2f}s, phonemes: {len(phonemes)}")

        # Convert audio_data from base64
        if isinstance(audio_data, str):
            import base64
            audio_data = base64.b64decode(audio_data)

        # Generate avatar video with phonemes
        video_bytes = await avatar_service.generate_avatar_video(
            audio_data=audio_data,
            phonemes=phonemes,
            duration=duration,
            model=request.avatar_id or "face"
        )

        # Return video as streaming response
        return StreamingResponse(
            io.BytesIO(video_bytes),
            media_type="video/webm",
            headers={"Content-Disposition": "attachment; filename=avatar_video.webm"}
        )

    except httpx.RequestError as e:
        logger.error(f"Voice service error: {e}")
        raise HTTPException(status_code=503, detail="Voice service unavailable")
    except Exception as e:
        logger.error(f"Avatar generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-phonemes")
async def set_phonemes(request: Request):
    """Set phoneme data and audio URL for the current session."""
    try:
        data = await request.json()
        audio_url = data.get("audio_url")
        phonemes = data.get("phonemes")

        if not audio_url or not phonemes:
            raise HTTPException(status_code=400, detail="Missing audio_url or phonemes")

        # Update global session
        current_session["audio_url"] = audio_url
        current_session["phonemes"] = phonemes

        logger.info(f"Set phonemes for session: {len(phonemes)} phonemes")
        return {"status": "success", "phoneme_count": len(phonemes)}

    except Exception as e:
        logger.error(f"Failed to set phonemes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/phonemes")
async def get_phonemes():
    """Get current phoneme data for the avatar."""
    try:
        return {
            "audio_url": current_session.get("audio_url"),
            "phonemes": current_session.get("phonemes", [])
        }
    except Exception as e:
        logger.error(f"Failed to get phonemes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-from-audio")
async def generate_avatar_from_audio(
    audio_file: UploadFile = File(...),
    phonemes: Optional[str] = Form(None)  # JSON string of phonemes
):
    """
    Generate avatar video from uploaded audio file.

    Args:
        audio_file: Audio file upload
        phonemes: Optional phoneme timing data as JSON string
    """
    try:
        logger.info(f"Generating avatar video from uploaded audio: {audio_file.filename}")

        # Read audio data
        audio_data = await audio_file.read()

        # Parse phonemes if provided
        phoneme_data = None
        if phonemes:
            import json
            phoneme_data = json.loads(phonemes)

        # Generate video
        video_bytes = await avatar_service.generate_avatar_video(
            audio_data=audio_data,
            phonemes=phoneme_data
        )

        return StreamingResponse(
            io.BytesIO(video_bytes),
            media_type="video/mp4",
            headers={"Content-Disposition": "attachment; filename=avatar_video.mp4"}
        )

    except Exception as e:
        logger.error(f"Avatar generation from audio failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info")
async def get_avatar_info():
    """Get avatar service information."""
    try:
        info = await avatar_service.get_avatar_info()
        return {
            "status": "ready",
            "service": "avatar-rendering",
            "info": info
        }
    except Exception as e:
        logger.error(f"Failed to get avatar info: {e}")
        raise HTTPException(status_code=500, detail=str(e))