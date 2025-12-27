# User-related API routes
from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
def read_users_me():
    return {"username": "current_user"}

@router.get("/{user_id}")
def read_user(user_id: int):
    return {"user_id": user_id}
