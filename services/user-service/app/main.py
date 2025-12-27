from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for the User Service.

    Handles database initialization on startup and cleanup on shutdown.

    Args:
        app: The FastAPI application instance.
    """
    # Startup: Attempt to initialize the database
    with suppress(Exception):
        await init_db()
        # Continue startup even if DB init fails (in dev/test mode)

    yield

    # Shutdown
    pass


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance for the User Service.

    Includes middleware configuration, router setup, and lifespan management.
    Initializes the app with the centralized settings metadata.

    Returns:
        The configured FastAPI application instance.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include the main router
    app.include_router(router)

    return app


app = create_app()
