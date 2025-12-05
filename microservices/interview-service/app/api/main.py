from fastapi import APIRouter

from app.api.routes import users, system, interview, question_routes
from app.core.config import settings


api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(interview.router, prefix="/interview", tags=["Interview"])
api_router.include_router(question_routes.router, prefix="/questions", tags=["Questions"])


# if settings.ENVIRONMENT == "local":
#     api_router.include_router(private.router)