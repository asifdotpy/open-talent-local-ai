from fastapi import FastAPI

from .config import settings
from .database import init_db
from .routers import router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.include_router(router)

    @app.on_event("startup")
    async def on_startup() -> None:
        await init_db()

    return app


app = create_app()
