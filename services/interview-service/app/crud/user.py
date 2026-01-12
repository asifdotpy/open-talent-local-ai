from app.db.models.user import User
from app.schemas.user import UserCreate
from sqlmodel import Session


def create_user(session: Session, user_create: UserCreate) -> User:
    db_obj = User(
        email=user_create.email,
        hashed_password=user_create.password,  # In a real app, hash this!
        is_active=user_create.is_active,
        is_superuser=user_create.is_superuser,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
