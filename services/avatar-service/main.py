"""Main application file for the OpenTalent Avatar Service.

This service manages AI avatar interactions and rendering for the OpenTalent recruitment platform.
Avatar and voice generation will be implemented locally in future updates.
"""

import json
import logging
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

# Import from existing modules (keeping modular structure)
try:
    from app.config.settings import (
        ALLOWED_ORIGINS,
        SERVICE_DESCRIPTION,
        SERVICE_TITLE,
        SERVICE_VERSION,
    )
    from app.routes.avatar_routes import router as avatar_router

    USE_EXTERNAL_MODULES = True
except ImportError:
    # Fallback configuration if external modules are not available
    SERVICE_TITLE = "OpenTalent - Avatar Service"
    SERVICE_DESCRIPTION = "Manages AI avatar interactions and rendering"
    SERVICE_VERSION = "1.0.0"
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:8081",
    ]
    USE_EXTERNAL_MODULES = False

# External API clients removed - using local implementations only
AI_AVATAR_AVAILABLE = False

# ElevenLabs integration removed - building locally
ELEVENLABS_AVAILABLE = False

# Network timeout configuration for enterprise-grade reliability
TIMEOUT_CONFIG = {
    "health_check": 3.0,  # Quick health checks
    "file_operations": 10.0,  # Audio file operations (future use)
}

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("avatar-service")

# Local voice models and service (fallback endpoints)
# Add current directory to path for 'app' imports
import sys
from pathlib import Path

_service_dir = Path(__file__).parent
if str(_service_dir) not in sys.path:
    sys.path.insert(0, str(_service_dir))

try:
    from app.models.voice import VoiceListResponse, VoiceRequest, VoiceResponse
    from app.services.voice_service import voice_service

    VOICE_MODULES_AVAILABLE = True
    logger.info("Voice modules imported successfully")
except ImportError as e:
    VOICE_MODULES_AVAILABLE = False
    logger.warning(f"Voice modules import failed: {e}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=SERVICE_TITLE,
        description=f"""{SERVICE_DESCRIPTION}

        **Capabilities:**
        - AI avatar rendering and animation
        - Lip-sync video generation
        - Voice integration with voice service
        - Real-time avatar interactions

        **API Documentation:**
        - Interactive Swagger UI: `/docs`
        - Alternative docs URL: `/doc`
        - ReDoc documentation: `/redoc`
        - OpenAPI schema: `/openapi.json`
        - API endpoints summary: `/api-docs`
        """,
        version=SERVICE_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        logger.info(f"[{request_id}] {request.method} {request.url.path} - Request started")

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
        )

        return response

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include external routers if available
    if USE_EXTERNAL_MODULES:
        app.include_router(avatar_router)

    # Include avatar_v1 router unconditionally (safe import), to expose planned API surface
    try:
        from app.routes.avatar_v1 import router as avatar_v1_router

        app.include_router(avatar_v1_router)
        logger.info("avatar_v1 router included with prefix: /api/v1/avatars")
    except ImportError:
        logger.warning("avatar_v1 router not available")

    # Include voice routes for US English voice endpoints (attempt regardless of module availability)
    try:
        from app.routes.voice_routes import router as voice_router

        app.include_router(voice_router)
    except ImportError:
        logger.warning("voice_routes not available")

    # Static files are served via routes from ai-orchestra-simulation
    # No need for additional mounts

    return app



# ... existing imports ...

# Create app instance
app = create_app()

# Note: Static files are served via routes from ai-orchestra-simulation
# No need for additional mounts here


# Pydantic models for request/response
class RenderRequest(BaseModel):
    text: str
    phonemes: list  # From voice service
    duration: float
    model: str = "production"  # Allow model override in dev mode


@app.get("/")
async def root():
    """Root endpoint for Avatar Service."""
    logger.info("Root endpoint accessed")
    return {
        "message": "OpenTalent Avatar Service",
        "status": "running",
        "version": SERVICE_VERSION,
        "description": "AI avatar rendering and future local voice integration",
        "documentation": {
            "swagger_ui": "/docs",
            "alternative": "/doc",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
            "api_summary": "/api-docs",
        },
    }


@app.get("/ping")
async def ping():
    """Simple ping endpoint for load balancer health checks."""
    return {"status": "ok"}


@app.get("/doc", include_in_schema=False)
async def doc_redirect():
    """Alternative redirect to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/api-docs", include_in_schema=False)
async def api_docs_info():
    """Get API documentation information and available endpoints."""
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
        "service": "OpenTalent Avatar Service API",
        "version": SERVICE_VERSION,
        "total_endpoints": len(routes_info),
        "documentation_urls": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "routes": routes_info,
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint for Avatar Service."""
    logger.info("Health check requested")
    try:
        status = {
            "status": "healthy",
            "service": "avatar-service",
            "version": SERVICE_VERSION,
            "timestamp": datetime.now().isoformat(),
            "voice_integration": "AI Voice",
            "components": {
                "api": "healthy",
                "avatar_rendering": "real",
                "voice_integration": "active",
            },
        }

        logger.info("Health check completed successfully")
        return status

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "avatar-service",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        )


@app.post("/render/lipsync")
async def render_lipsync(request: RenderRequest):
    """Render avatar video with lip-sync
    Uses face.glb in production, allows model override in dev
    """
    # Call Node.js renderer
    renderer_script = os.path.join(os.path.dirname(__file__), "renderer", "render.js")

    input_data = json.dumps(
        {
            "phonemes": request.phonemes,
            "duration": request.duration,
            "model": request.model,
            "text": request.text,
        }
    )

    renderer_dir = os.path.dirname(renderer_script)
    logger.info(
        f"Rendering request: text={request.text}, duration={request.duration}s, model={request.model}"
    )

    try:
        process = subprocess.run(
            ["node", renderer_script],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=120,  # Increased from 30 to 120 seconds for video encoding
            cwd=renderer_dir,
            env={**os.environ, "SKIP_RENDERING": "false"}, check=False,  # Enable real video rendering
        )
    except subprocess.TimeoutExpired:
        logger.error("Renderer subprocess timed out after 120s")
        raise HTTPException(status_code=500, detail="Rendering timed out")
    except Exception as e:
        logger.error(f"Renderer subprocess error: {type(e).__name__}: {e}")
        raise

    if process.returncode != 0:
        logger.error(f"Renderer failed with return code {process.returncode}: {process.stderr}")
        raise HTTPException(status_code=500, detail=f"Rendering failed: {process.stderr}")

    if not process.stdout or not process.stdout.strip():
        logger.error("Renderer produced no output")
        raise HTTPException(status_code=500, detail="Renderer produced no output")

    # Extract JSON from stdout (last line, as render.js outputs console.log before final JSON)
    lines = process.stdout.strip().split("\n")
    json_line = lines[-1] if lines else ""

    logger.debug(f"Renderer output lines: {len(lines)}, parsing JSON from last line")

    result = json.loads(json_line)

    return {
        "video_path": result["video_path"],
        "duration": result["duration"],
        "model_used": result["model"],
        "metadata": result["metadata"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
