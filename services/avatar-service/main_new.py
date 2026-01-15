"""Main application file for the OpenTalent Avatar Service.

This service manages AI avatar interactions with Irish voice integration
using AI Voice API. It provides voice generation capabilities for the
OpenTalent recruitment platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import (
    ALLOWED_ORIGINS,
    SERVICE_DESCRIPTION,
    SERVICE_TITLE,
    SERVICE_VERSION,
)
from app.routes.voice_routes import router as voice_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=SERVICE_TITLE,
        description=SERVICE_DESCRIPTION,
        version=SERVICE_VERSION,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(voice_router)

    return app


# Create app instance
app = create_app()


# Health check for backwards compatibility
@app.get("/ping")
async def ping():
    """Simple ping endpoint for load balancer health checks."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)  # nosec B104
