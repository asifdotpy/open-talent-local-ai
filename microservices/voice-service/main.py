"""Voice Service - Local Speech Processing
Powered by Vosk (STT), Piper (TTS), and Silero (VAD)
"""

import asyncio
import logging
import os
import tempfile
from typing import Optional

from fastapi import (
    Body,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    WebSocket,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.modular_tts_service import MockModularTTSService, ModularTTSService
from services.silero_vad_service import MockSileroVADService, SileroVADService
from services.stream_service import UnifiedStreamService
from services.vosk_stt_service import MockVoskSTTService, VoskSTTService

# Configure logging BEFORE importing WebRTC (which uses logger)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Service Initialization ---
USE_MOCK = os.getenv("USE_MOCK_SERVICES", "false").lower() == "true"
ENABLE_WEBRTC = os.getenv("ENABLE_WEBRTC", "true").lower() == "true"

# WebRTC imports (optional)
try:
    if not USE_MOCK and ENABLE_WEBRTC:
        from webrtc_worker import VoiceServiceWorker, start_webrtc_worker

        WEBRTC_AVAILABLE = True
    else:
        WEBRTC_AVAILABLE = False
        VoiceServiceWorker = None
        start_webrtc_worker = None
        logger.info("WebRTC disabled in mock mode or via configuration")
except ImportError:
    WEBRTC_AVAILABLE = False
    VoiceServiceWorker = None
    start_webrtc_worker = None
    logger.warning("WebRTC worker not available. Install aiortc for WebRTC support.")

app = FastAPI(
    title="Voice Service API",
    description="""
    Local Speech Processing Service for OpenTalent Platform

    **Capabilities:**
    - **Speech-to-Text (STT)**: Real-time transcription using Vosk
    - **Text-to-Speech (TTS)**: High-quality synthesis using Piper (local) or OpenAI API
    - **Voice Activity Detection (VAD)**: Silence filtering using Silero
    - **WebRTC Integration**: Real-time audio streaming for interviews
    - **WebSocket Streaming**: Bidirectional audio streaming

    **API Documentation:**
    - Interactive Swagger UI: `/docs`
    - Alternative docs URL: `/doc`
    - ReDoc documentation: `/redoc`
    - OpenAPI schema: `/openapi.json`
    - API endpoints summary: `/api-docs`

    **Service Stack:** Vosk + Modular TTS (Piper/OpenAI) + Silero + WebRTC + FastAPI

    **Quick Start with Docker:**
    ```bash
    # Build image
    docker build -t voice-service:latest .

    # Run container
    docker run -d -p 8002:8002 \
      -e OPENAI_API_KEY=your_key_here \
      --name voice-service \
      voice-service:latest

    # Or use docker-compose
    docker-compose up -d
    ```

    **Environment Variables:**
    - `USE_MOCK_SERVICES`: Use mock services for testing (default: false)
    - `OPENAI_API_KEY`: OpenAI API key for TTS (required for production)
    - `OPENAI_TTS_MODEL`: TTS model (default: gpt-4o-mini-tts)
    - `OPENAI_TTS_VOICE`: Default voice (default: alloy)
    """,
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "OpenTalent Platform Team",
        "url": "https://github.com/asifdotpy/open-talent-platform",
        "email": "support@OpenTalent.platform",
    },
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=[
        {"name": "health", "description": "Health checks and service status endpoints"},
        {
            "name": "voice-processing",
            "description": "Speech-to-text, text-to-speech, and voice activity detection",
        },
        {"name": "streaming", "description": "WebSocket-based real-time audio streaming"},
        {"name": "webrtc", "description": "WebRTC integration for interview sessions"},
        {"name": "documentation", "description": "API documentation and schema endpoints"},
    ],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:8080",
        "http://localhost:8081",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- Service Initialization ---

if USE_MOCK:
    logger.warning("Using MOCK services for development")
    stt_service = MockVoskSTTService()
    tts_service = MockModularTTSService()
    vad_service = MockSileroVADService()
else:
    logger.info("Initializing PRODUCTION speech processing services")
    stt_service = VoskSTTService(
        model_path=os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15"),
        sample_rate=16000,
    )

    # Initialize modular TTS service (can use local Piper or OpenAI API)
    tts_provider = os.getenv("TTS_PROVIDER", "local").lower()  # "local" or "openai"
    if tts_provider == "openai":
        logger.info("Using OpenAI TTS API for production")
        tts_service = ModularTTSService(
            provider="openai",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
            openai_voice=os.getenv("OPENAI_TTS_VOICE", "alloy"),
        )
    else:
        logger.info("Using local Piper TTS for production")
        tts_service = ModularTTSService(
            provider="local",
            piper_model_path=os.getenv("PIPER_MODEL_PATH", "models/en_US-lessac-medium.onnx"),
            piper_config_path=os.getenv(
                "PIPER_CONFIG_PATH", "models/en_US-lessac-medium.onnx.json"
            ),
            piper_binary=os.getenv(
                "PIPER_BINARY",
                "/home/asif1/open-talent-platform/microservices/voice-service/piper/piper",
            ),
        )

    vad_service = SileroVADService(
        model_path=os.getenv("SILERO_MODEL_PATH", "models/silero_vad.onnx"),
        sample_rate=16000,
        threshold=0.5,
    )

# Initialize unified streaming service
stream_service = UnifiedStreamService(
    stt_service=stt_service, tts_service=tts_service, vad_service=vad_service
)

# Initialize WebRTC worker if available and enabled
webrtc_task = None

if WEBRTC_AVAILABLE and ENABLE_WEBRTC and not USE_MOCK:
    logger.info("WebRTC support enabled - will start worker on app startup")
else:
    if not WEBRTC_AVAILABLE:
        logger.warning("WebRTC support disabled - aiortc not installed")
    elif USE_MOCK:
        logger.info("WebRTC support disabled in mock mode")
    else:
        logger.info("WebRTC support disabled via ENABLE_WEBRTC=false")


@app.on_event("startup")
async def startup_event():
    """Validate services on startup."""
    logger.info("Voice Service starting up...")

    stt_health = stt_service.health_check()
    tts_health = tts_service.health_check()
    vad_health = vad_service.health_check()

    logger.info(f"STT Service: {'✓' if stt_health else '✗'}")
    logger.info(f"TTS Service: {'✓' if tts_health else '✗'}")
    logger.info(f"VAD Service: {'✓' if vad_health else '✗'}")
    logger.info("Streaming Service: ✓ (initialized)")

    if not USE_MOCK and not all([stt_health, tts_health]):
        logger.warning(
            "Core services (STT/TTS) not ready. Run download_models.py to fetch required models."
        )
        if not vad_health:
            logger.warning(
                "VAD service degraded - this is non-critical and won't prevent service startup"
            )

    # Start WebRTC worker if enabled
    global webrtc_task
    if WEBRTC_AVAILABLE and ENABLE_WEBRTC and not USE_MOCK:
        logger.info("Starting WebRTC worker...")
        try:
            webrtc_task = asyncio.create_task(start_webrtc_worker())
            logger.info("WebRTC worker started successfully")
        except Exception as e:
            logger.error(f"Failed to start WebRTC worker: {e}")
            webrtc_task = None


# --- Request and Response Models ---
class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None  # Will default to provider-specific voice
    speed: Optional[float] = 1.0
    extract_phonemes: Optional[bool] = True


class STTResponse(BaseModel):
    text: str
    words: list[dict]
    duration: float
    confidence: float


class TTSResponse(BaseModel):
    audio_file: str
    duration: float
    sample_rate: int
    phonemes: list[dict]
    words: list[dict]


class VADRequest(BaseModel):
    remove_silence: Optional[bool] = False


# --- API Endpoints ---
@app.get("/", tags=["health"], summary="Service root endpoint")
async def root():
    """Root endpoint for the Voice Service."""
    return {
        "service": "Voice Service",
        "version": "2.1.0",
        "status": "running",
        "stack": "Vosk + Modular TTS (Piper/OpenAI) + Silero + WebSocket Streaming",
        "mode": "mock" if USE_MOCK else "production",
        "capabilities": {
            "rest_api": ["stt", "tts", "vad"],
            "websocket": ["stt_streaming", "tts_streaming"],
            "realtime": True,
        },
        "documentation": {
            "openapi_ui": "/docs",
            "openapi_schema": "/openapi.json",
            "redoc": "/redoc",
        },
    }


@app.get("/docs", include_in_schema=False)
async def docs_redirect():
    """Redirect to FastAPI interactive API documentation.
    This endpoint provides Swagger UI documentation for all API routes.
    """
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/docs")


@app.get("/doc", include_in_schema=False)
async def doc_redirect():
    """Alternative redirect to API documentation.
    Same as /docs but shorter URL for convenience.
    """
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/docs")


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    """Get the OpenAPI schema for the Voice Service API.
    Returns the complete OpenAPI 3.0 specification in JSON format.
    """
    return app.openapi()


@app.get("/api-docs", include_in_schema=False)
async def api_docs_info():
    """Get API documentation information and available endpoints.
    Provides a summary of all available API routes and their purposes.
    """
    routes_info = []

    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            route_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, "name", "unknown"),
                "summary": getattr(route, "summary", None) or getattr(route, "description", None),
            }
            routes_info.append(route_info)

    return {
        "service": "Voice Service API",
        "version": "2.0.0",
        "total_endpoints": len(routes_info),
        "documentation_urls": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "routes": routes_info,
        "categories": {
            "health": ["GET /", "GET /health", "GET /info"],
            "voice_processing": ["POST /voice/stt", "POST /voice/tts", "POST /voice/vad"],
            "streaming": ["WebSocket /voice/ws/stt", "WebSocket /voice/ws/tts"],
            "webrtc": [
                "POST /webrtc/start",
                "POST /webrtc/stop",
                "POST /webrtc/tts",
                "GET /webrtc/status",
            ]
            if WEBRTC_AVAILABLE
            else [],
            "documentation": ["GET /docs", "GET /doc", "GET /api-docs", "GET /openapi.json"],
        },
    }


@app.get("/health", tags=["health"], summary="Health check endpoint")
async def health_check():
    """Health check endpoint with service status."""
    stt_health = stt_service.health_check()
    tts_health = tts_service.health_check()
    vad_health = vad_service.health_check()

    # Core services (STT/TTS) must be healthy, VAD is optional
    core_healthy = stt_health and tts_health
    all_healthy = core_healthy and vad_health

    return {
        "status": "healthy" if core_healthy else "unhealthy",
        "services": {
            "stt": "ready" if stt_health else "not_ready",
            "tts": "ready" if tts_health else "not_ready",
            "vad": "ready" if vad_health else "degraded",
            "streaming": "ready",
        },
        "active_connections": stream_service.get_connection_count(),
        "mode": "mock" if USE_MOCK else "local",
        "note": "VAD degradation doesn't affect core functionality"
        if core_healthy and not vad_health
        else None,
    }


@app.get("/voices", tags=["voice-processing"], summary="Get available TTS voices")
async def get_available_voices():
    """Get list of available TTS voices.

    Returns:
        List of available voice configurations
    """
    voices = tts_service.get_available_voices()
    return {"voices": voices}


@app.get("/info", tags=["health"], summary="Get detailed service information")
async def get_service_info():
    """Get comprehensive information about all voice services.

    Returns:
        Detailed status and capabilities of STT, TTS, and VAD services
    """
    return {
        "stt": stt_service.get_info(),
        "tts": tts_service.get_info(),
        "vad": vad_service.get_info(),
    }


@app.options("/voice/tts", tags=["voice-processing"], summary="CORS preflight for TTS endpoint")
async def tts_options():
    """Handle CORS preflight requests for TTS endpoint."""
    return {"message": "CORS preflight OK"}


@app.options("/voice/stt", tags=["voice-processing"], summary="CORS preflight for STT endpoint")
async def stt_options():
    """Handle CORS preflight requests for STT endpoint."""
    return {"message": "CORS preflight OK"}


@app.options("/health", tags=["health"], summary="CORS preflight for health endpoint")
async def health_options():
    """Handle CORS preflight requests for health endpoint."""
    return {"message": "CORS preflight OK"}


@app.post(
    "/voice/stt",
    response_model=STTResponse,
    tags=["voice-processing"],
    summary="Speech-to-Text transcription",
)
async def speech_to_text(
    audio_file: UploadFile = File(..., description="Audio file to transcribe (WAV, MP3, etc.)"),
    use_vad: bool = False,
):
    """Convert speech to text using Vosk.

    Args:
        audio_file: Audio file (WAV, MP3, etc.)
        use_vad: Apply voice activity detection to filter silence

    Returns:
        Transcription with word-level timing and confidence scores
    """
    logger.info(f"STT request received: {audio_file.filename}")

    # Validate file type
    if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid audio file type")

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio_file:
        content = await audio_file.read()
        tmp_audio_file.write(content)
        tmp_audio_file_path = tmp_audio_file.name

    try:
        # Apply VAD if requested
        if use_vad and not USE_MOCK:
            logger.info("Applying VAD to filter silence")
            filtered_path = tmp_audio_file_path + "_filtered.wav"
            vad_result = vad_service.filter_silence(tmp_audio_file_path, filtered_path)
            logger.info(f"VAD: {vad_result['reduction_percentage']:.1f}% silence removed")
            os.unlink(tmp_audio_file_path)
            tmp_audio_file_path = filtered_path

        # Transcribe audio
        transcription = stt_service.transcribe_audio(tmp_audio_file_path)

        if not transcription or not transcription.get("text"):
            raise HTTPException(status_code=500, detail="Transcription failed")

        logger.info(f"Transcription successful: '{transcription['text'][:50]}...'")

        return STTResponse(**transcription)

    except Exception as e:
        logger.error(f"STT failed: {e}")
        raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {str(e)}")
    finally:
        # Cleanup temporary file
        if os.path.exists(tmp_audio_file_path):
            os.unlink(tmp_audio_file_path)


@app.post("/voice/tts", tags=["voice-processing"], summary="Text-to-Speech synthesis")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using Piper (local) or OpenAI API.

    Args:
        request: TTS request with text, voice, speed, and phoneme extraction options

    Returns:
        Audio file (WAV) with word timing and phoneme data, or JSON with phonemes if return_json=True
    """
    logger.info(f"TTS request: '{request.text[:50]}...' (voice: {request.voice})")

    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Create temporary output file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio_file:
        output_path = tmp_audio_file.name

    try:
        # Synthesize speech
        synthesis_result = tts_service.synthesize_speech(
            text=request.text,
            output_path=output_path,
            voice=request.voice,
            speed=request.speed,
            extract_phonemes=request.extract_phonemes,
        )

        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="TTS synthesis failed")

        logger.info(f"TTS successful: {synthesis_result['duration']:.2f}s audio generated")

        # Read audio data and encode as base64
        with open(output_path, "rb") as f:
            audio_data = f.read()

        import base64

        audio_b64 = base64.b64encode(audio_data).decode("utf-8")

        # Return JSON response with audio data and phonemes
        return {
            "audio_data": audio_b64,  # Base64 encoded audio data
            "duration": synthesis_result["duration"],
            "sample_rate": synthesis_result["sample_rate"],
            "phonemes": synthesis_result["phonemes"],
            "words": synthesis_result["words"],
        }

    except Exception as e:
        logger.error(f"TTS failed: {e}")
        # Cleanup on error
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {str(e)}")
    finally:
        # Cleanup temp file
        if os.path.exists(output_path):
            os.unlink(output_path)


@app.post("/voice/vad", tags=["voice-processing"], summary="Voice Activity Detection")
async def voice_activity_detection(
    audio_file: UploadFile = File(..., description="Audio file to analyze"),
    remove_silence: bool = False,
):
    """Detect voice activity in audio file.

    Args:
        audio_file: Audio file to analyze
        remove_silence: If True, return audio with silence removed

    Returns:
        VAD analysis or filtered audio file
    """
    logger.info(f"VAD request received: {audio_file.filename}")

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio_file:
        content = await audio_file.read()
        tmp_audio_file.write(content)
        tmp_audio_file_path = tmp_audio_file.name

    try:
        if remove_silence:
            # Filter silence and return audio
            output_path = tmp_audio_file_path + "_filtered.wav"
            result = vad_service.filter_silence(tmp_audio_file_path, output_path)

            logger.info(f"Silence removed: {result['reduction_percentage']:.1f}%")

            # Return filtered audio
            return FileResponse(
                output_path,
                media_type="audio/wav",
                filename=f"filtered_{audio_file.filename}",
                headers={
                    "X-Original-Duration": str(result["original_duration"]),
                    "X-Filtered-Duration": str(result["filtered_duration"]),
                    "X-Reduction-Percentage": str(result["reduction_percentage"]),
                },
            )
        else:
            # Return VAD analysis
            result = vad_service.detect_voice_activity(tmp_audio_file_path)
            logger.info(f"VAD analysis: {result['num_segments']} segments detected")
            return result

    except Exception as e:
        logger.error(f"VAD failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice activity detection failed: {str(e)}")
    finally:
        # Cleanup temporary file
        if os.path.exists(tmp_audio_file_path):
            os.unlink(tmp_audio_file_path)


@app.websocket("/voice/ws/stt")
async def websocket_stt_stream(websocket: WebSocket, use_vad: bool = True):
    """Real-time STT streaming via WebSocket.

    Client sends audio chunks as bytes, server responds with transcription results.
    """
    await stream_service.handle_stt_stream(websocket, use_vad)


@app.websocket("/voice/ws/tts")
async def websocket_tts_stream(websocket: WebSocket):
    """Real-time TTS streaming via WebSocket.

    Client sends text data as JSON, server streams audio chunks back.
    """
    await stream_service.handle_tts_stream(websocket)


# WebRTC Endpoints (if available)
if WEBRTC_AVAILABLE:

    @app.post("/webrtc/start", tags=["webrtc"], summary="Start WebRTC session")
    async def start_webrtc_session(payload: dict = Body(...)):
        """Start a new WebRTC session for voice processing.
        Called by interview-service when a new interview begins.
        """
        session_id = payload.get("session_id")
        job_description = payload.get("job_description", "General software engineering position")

        if not session_id:
            return {"error": "Missing session_id"}, 400

        # Start conversation session (placeholder - integrate with conversation service)
        logger.info(f"Starting WebRTC session {session_id}")

        # Start WebRTC worker for this session
        try:
            worker = VoiceServiceWorker(session_id)
            asyncio.create_task(worker.start())
            return {"status": "started", "session_id": session_id}
        except Exception as e:
            logger.error(f"Failed to start WebRTC session: {e}")
            return {"error": str(e)}, 500

    @app.post("/webrtc/stop", tags=["webrtc"], summary="Stop WebRTC session")
    async def stop_webrtc_session(payload: dict = Body(...)):
        """Stop an active WebRTC session"""
        session_id = payload.get("session_id")

        if not session_id:
            return {"error": "Missing session_id"}, 400

        # Stop WebRTC worker for this session (placeholder)
        logger.info(f"Stopping WebRTC session {session_id}")
        return {"status": "stopped", "session_id": session_id}

    @app.post("/webrtc/tts", tags=["webrtc"], summary="Send TTS to WebRTC session")
    async def send_webrtc_tts(payload: dict = Body(...)):
        """Generate and send TTS audio to active WebRTC session

        Args:
            session_id: Active session ID
            text: Text to synthesize
        """
        session_id = payload.get("session_id")
        text = payload.get("text")

        if not session_id or not text:
            return {"error": "Missing session_id or text"}, 400

        # Send TTS to WebRTC session (placeholder)
        logger.info(f"Sending TTS to WebRTC session {session_id}: {text[:50]}...")
        return {"status": "tts_sent", "session_id": session_id, "text": text[:50]}

    @app.get("/webrtc/status", tags=["webrtc"], summary="Get WebRTC status")
    async def get_webrtc_status():
        """Get status of WebRTC functionality"""
        return {
            "webrtc_enabled": ENABLE_WEBRTC,
            "webrtc_available": WEBRTC_AVAILABLE,
            "status": "active" if webrtc_task and not webrtc_task.done() else "inactive",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
