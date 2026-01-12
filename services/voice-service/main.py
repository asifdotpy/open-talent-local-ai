"""Voice Service - Local Speech Processing
Powered by Vosk (STT), Piper (TTS), and Silero (VAD).
"""

import asyncio
import base64
import logging
import os
import tempfile
from datetime import datetime

import uvicorn
from fastapi import Body, FastAPI, File, HTTPException, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydub import AudioSegment
from pydub.silence import split_on_silence

from services.modular_tts_service import MockModularTTSService, ModularTTSService
from services.phoneme_extractor import PhonemeExtractor
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

from app.core.constants import (
    DEFAULT_OPENAI_TTS_MODEL,
    DEFAULT_OPENAI_TTS_VOICE,
    SERVICE_DESCRIPTION,
    SERVICE_NAME,
    SERVICE_VERSION,
)

app = FastAPI(
    title=f"{SERVICE_NAME} API",
    description=SERVICE_DESCRIPTION,
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "OpenTalent Platform Team",
        "url": "https://github.com/asifdotpy/open-talent",
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

# Add security headers middleware
from app.security import (
    RateLimitMiddleware,
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
)

app.add_middleware(SecurityHeadersMiddleware)
# Configure request size limit via env var (bytes), default 10MB
try:
    MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", str(10 * 1024 * 1024)))
except ValueError:
    MAX_REQUEST_SIZE = 10 * 1024 * 1024
app.add_middleware(RequestSizeLimitMiddleware, max_bytes=MAX_REQUEST_SIZE)

# Configure rate limiting (token bucket) via env
try:
    RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "10"))
except ValueError:
    RATE_LIMIT_BURST = 10

try:
    RATE_LIMIT_RATE = int(os.getenv("RATE_LIMIT_RATE", "5"))  # tokens per second
except ValueError:
    RATE_LIMIT_RATE = 5

ALLOWLIST_PATHS = (
    "/",
    "/health",
    "/info",
    "/docs",
    "/doc",
    "/openapi.json",
    "/api-docs",
    "/redoc",
)

app.add_middleware(
    RateLimitMiddleware,
    burst=RATE_LIMIT_BURST,
    rate_per_sec=RATE_LIMIT_RATE,
    allowlist=ALLOWLIST_PATHS,
)

try:
    MAX_AUDIO_DURATION_MS = int(os.getenv("MAX_AUDIO_DURATION_MS", str(5 * 60 * 1000)))  # 5 minutes
except ValueError:
    MAX_AUDIO_DURATION_MS = 5 * 60 * 1000

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
            openai_model=os.getenv("OPENAI_TTS_MODEL", DEFAULT_OPENAI_TTS_MODEL),
            openai_voice=os.getenv("OPENAI_TTS_VOICE", DEFAULT_OPENAI_TTS_VOICE),
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
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "piper", "piper"),
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

# Phoneme extractor
phoneme_extractor = PhonemeExtractor(logger=logger)

# Initialize WebRTC worker if available and enabled
webrtc_task = None

if WEBRTC_AVAILABLE and ENABLE_WEBRTC and not USE_MOCK:
    logger.info("WebRTC support enabled - will start worker on app startup")
elif not WEBRTC_AVAILABLE:
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


# Keep legacy imports from app/schemas for backward compatibility

# --- Request and Response Models ---
# Import from root schemas.py (comprehensive schema definitions)
from schemas import (  # TTS Schemas; STT Schemas; VAD Schemas (using base models from app/schemas for backward compatibility); Audio Processing; WebRTC; Phonemes; Voice Analytics; Voice Info; Batch Processing; Service Info
    HealthCheckResponse,
    STTResponse,
    TTSRequest,
)


# --- API Endpoints ---
@app.get("/", tags=["health"], summary="Service root endpoint")
async def root():
    """Service identification endpoint for the Voice Service.

    Returns:
        A dictionary confirming the service name, version, and documentation links.
    """
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


def _audiosegment_from_upload(upload_file: UploadFile) -> AudioSegment:
    """Load UploadFile into a pydub AudioSegment with validation."""
    if upload_file.content_type and not upload_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid audio file type")
    suffix = os.path.splitext(upload_file.filename or "audio.wav")[-1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = upload_file.file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        seg = AudioSegment.from_file(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    if len(seg) > MAX_AUDIO_DURATION_MS:
        raise HTTPException(status_code=413, detail="Audio too long")
    return seg


def _export_audiosegment(seg: AudioSegment, format_: str = "wav") -> str:
    """Export AudioSegment to temp file and return path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format_}") as tmp_out:
        out_path = tmp_out.name
    seg.export(out_path, format=format_)
    return out_path


@app.get("/docs", include_in_schema=False)
async def docs_redirect():
    """Redirect to the principal Swagger UI documentation.

    Returns:
        A RedirectResponse to the /docs endpoint.
    """
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/docs")


@app.get("/doc", include_in_schema=False)
async def doc_redirect():
    """Alternative redirect path for principal Swagger UI documentation.

    Returns:
        A RedirectResponse to the /docs endpoint.
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
            "voice_processing": [
                "POST /voice/stt",
                "POST /voice/tts",
                "POST /voice/vad",
                "POST /voice/normalize",
                "POST /voice/format",
                "POST /voice/split",
                "POST /voice/join",
                "GET /voices",
                "POST /voice/phonemes",
                "POST /voice/trim",
                "POST /voice/resample",
                "POST /voice/metadata",
                "POST /voice/channels",
                "POST /voice/latency-test",
                "POST /voice/batch-tts",
            ],
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
        "counts": {
            "health": 3,
            "voice_processing": 16,
            "streaming": 2,
            "webrtc": 4 if WEBRTC_AVAILABLE else 0,
            "documentation": 4,
        },
    }


@app.get(
    "/health", tags=["health"], summary="Health check endpoint", response_model=HealthCheckResponse
)
async def health_check() -> HealthCheckResponse:
    """Comprehensive health check endpoint for the Voice Service.

    Verifies the operational status of STT, TTS, and VAD components.

    Returns:
        A HealthCheckResponse containing granular status and availability flags.
    """
    stt_health = stt_service.health_check()
    tts_health = tts_service.health_check()
    vad_service.health_check()

    # Core services (STT/TTS) must be healthy, VAD is optional
    core_healthy = stt_health and tts_health

    return HealthCheckResponse(
        status="healthy" if core_healthy else "unhealthy",
        timestamp=datetime.utcnow(),
        tts_available=tts_health,
        stt_available=stt_health,
        webrtc_available=WEBRTC_AVAILABLE and ENABLE_WEBRTC,
        audio_processing_available=True,
        uptime_seconds=0.0,  # TODO: Track actual uptime
    )


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
    logger.info(f"TTS request: '{request.text[:50]}...' (voice: {request.voice_id})")

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
            voice=request.voice_id,
            speed=request.speaking_rate,
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


# --- Audio Processing Helpers (stubs) ---


# TODO: Implement with services/audio_processing_service.py normalize pipeline
@app.post("/voice/normalize", tags=["voice-processing"], summary="Normalize audio levels")
async def normalize_audio(audio_file: UploadFile = File(...), target_dbfs: float = -20.0):
    seg = _audiosegment_from_upload(audio_file)
    change = target_dbfs - seg.dBFS
    normalized = seg.apply_gain(change)
    out_path = _export_audiosegment(normalized)
    return FileResponse(out_path, media_type="audio/wav", filename="normalized.wav")


# TODO: Implement with services/audio_processing_service.py format conversion
@app.post("/voice/format", tags=["voice-processing"], summary="Convert audio format")
async def convert_audio_format(audio_file: UploadFile = File(...), target_format: str = "wav"):
    seg = _audiosegment_from_upload(audio_file)
    out_path = _export_audiosegment(seg, format_=target_format)
    return FileResponse(
        out_path, media_type=f"audio/{target_format}", filename=f"converted.{target_format}"
    )


# TODO: Implement with services/audio_processing_service.py silence-based splitting
@app.post("/voice/split", tags=["voice-processing"], summary="Split audio by silence")
async def split_audio(
    audio_file: UploadFile = File(...),
    min_silence_len: int = 500,
    silence_thresh_delta: int = 16,
    keep_silence: int = 200,
):
    seg = _audiosegment_from_upload(audio_file)
    silence_thresh = seg.dBFS - silence_thresh_delta
    chunks = split_on_silence(
        seg,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence,
    )
    metadata = []
    for idx, chunk in enumerate(chunks):
        metadata.append({"index": idx, "duration_ms": len(chunk)})
    return {"status": "ok", "segments": metadata, "count": len(chunks)}


# TODO: Implement with services/audio_processing_service.py join pipeline
@app.post("/voice/join", tags=["voice-processing"], summary="Join audio segments")
async def join_audio(files: list[UploadFile] = File(...)):
    combined = None
    for f in files:
        seg = _audiosegment_from_upload(f)
        combined = seg if combined is None else combined + seg
    if combined is None:
        raise HTTPException(status_code=400, detail="No files provided")
    if len(combined) > MAX_AUDIO_DURATION_MS:
        raise HTTPException(status_code=413, detail="Audio too long")
    out_path = _export_audiosegment(combined)
    return FileResponse(out_path, media_type="audio/wav", filename="joined.wav")


# TODO: Implement with services/phoneme_extractor.py using TTS backend
@app.post("/voice/phonemes", tags=["voice-processing"], summary="Extract phonemes from text")
async def extract_phonemes_api(text: str = Body(..., embed=True), duration: float = 0.0):
    result = phoneme_extractor.extract_phonemes(text, duration=duration)
    return result


@app.post("/voice/trim", tags=["voice-processing"], summary="Trim audio by start/end")
async def trim_audio(
    audio_file: UploadFile = File(...), start_ms: int = 0, end_ms: int | None = None
):
    seg = _audiosegment_from_upload(audio_file)
    if end_ms is None or end_ms <= 0 or end_ms > len(seg):
        end_ms = len(seg)
    trimmed = seg[start_ms:end_ms]
    out_path = _export_audiosegment(trimmed)
    return FileResponse(out_path, media_type="audio/wav", filename="trimmed.wav")


@app.post("/voice/resample", tags=["voice-processing"], summary="Resample audio sample rate")
async def resample_audio(audio_file: UploadFile = File(...), target_sample_rate: int = 16000):
    seg = _audiosegment_from_upload(audio_file)
    resampled = seg.set_frame_rate(target_sample_rate)
    out_path = _export_audiosegment(resampled)
    return FileResponse(out_path, media_type="audio/wav", filename="resampled.wav")


@app.post("/voice/metadata", tags=["voice-processing"], summary="Extract audio metadata")
async def audio_metadata(audio_file: UploadFile = File(...)):
    seg = _audiosegment_from_upload(audio_file)
    return {
        "status": "ok",
        "metadata": {
            "duration_ms": len(seg),
            "frame_rate": seg.frame_rate,
            "channels": seg.channels,
            "sample_width": seg.sample_width,
            "dBFS": seg.dBFS,
        },
    }


@app.post("/voice/channels", tags=["voice-processing"], summary="Convert channels (mono/stereo)")
async def audio_channels(audio_file: UploadFile = File(...), target_channels: int = 1):
    seg = _audiosegment_from_upload(audio_file)
    converted = seg.set_channels(target_channels)
    out_path = _export_audiosegment(converted)
    return FileResponse(out_path, media_type="audio/wav", filename="channels.wav")


@app.post("/voice/latency-test", tags=["voice-processing"], summary="Latency test for pipeline")
async def latency_test(text: str = Body("ping", embed=True)):
    import time

    t0 = time.time()
    # Minimal pipeline: phoneme extraction as proxy
    _ = phoneme_extractor.extract_phonemes(text, duration=0.0)
    t1 = time.time()
    return {
        "status": "ok",
        "input": text,
        "start": t0,
        "end": t1,
        "latency_ms": int((t1 - t0) * 1000),
    }


@app.post("/voice/batch-tts", tags=["voice-processing"], summary="Batch TTS for multiple texts")
async def batch_tts(requests: list[TTSRequest]):
    results = []
    for req in requests:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio_file:
            output_path = tmp_audio_file.name
        try:
            synthesis_result = tts_service.synthesize_speech(
                text=req.text,
                output_path=output_path,
                voice=req.voice_id,
                speed=req.speaking_rate,
                extract_phonemes=req.extract_phonemes,
            )
            with open(output_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode("utf-8")
            results.append(
                {
                    "text": req.text,
                    "audio_data": audio_b64,
                    "duration": synthesis_result.get("duration"),
                    "sample_rate": synthesis_result.get("sample_rate"),
                    "phonemes": synthesis_result.get("phonemes"),
                    "words": synthesis_result.get("words"),
                }
            )
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    return {"status": "ok", "count": len(results), "results": results}


@app.websocket("/voice/ws/stt")
async def websocket_stt_stream(websocket: WebSocket, use_vad: bool = True):
    """Real-time STT streaming via WebSocket.

    Client sends audio chunks as bytes, server responds with transcription results.
    """
    await stream_service.handle_stt_stream(websocket, use_vad)


@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    """Bidirectional WebSocket endpoint for real-time audio streaming.

    Handles audio chunks (PCM16), performs real-time transcription using Vosk,
    and returns text responses or status updates.

    Args:
        websocket: The active WebSocket connection.
    """


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
        payload.get("job_description", "General software engineering position")

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
        """Stop an active WebRTC session."""
        session_id = payload.get("session_id")

        if not session_id:
            return {"error": "Missing session_id"}, 400

        # Stop WebRTC worker for this session (placeholder)
        logger.info(f"Stopping WebRTC session {session_id}")
        return {"status": "stopped", "session_id": session_id}

    @app.post("/webrtc/tts", tags=["webrtc"], summary="Send TTS to WebRTC session")
    async def send_webrtc_tts(payload: dict = Body(...)):
        """Generate and send TTS audio to active WebRTC session.

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
        """Get status of WebRTC functionality."""
        return {
            "webrtc_enabled": ENABLE_WEBRTC,
            "webrtc_available": WEBRTC_AVAILABLE,
            "status": "active" if webrtc_task and not webrtc_task.done() else "inactive",
        }


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8015))
    uvicorn.run(app, host=host, port=port)
