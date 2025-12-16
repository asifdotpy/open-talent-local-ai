import logging
import os

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from sqlalchemy import Column, DateTime, Integer, String, create_engine, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Database settings."""

    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost/db"
    )


settings = Settings()

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """SQLAlchemy User Model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# --- Pydantic Models ---


class UserProfileCreate(BaseModel):
    """Pydantic model for creating user profiles."""

    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique username"
    )
    email: str = Field(..., description="User's email address")
    full_name: str | None = Field(None, max_length=100, description="User's full name")


class UserProfileResponse(BaseModel):
    """Pydantic model for user profile responses."""

    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: str | None = Field(None, description="Full name")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        """Configuration for Pydantic model."""

        from_attributes = True


app = FastAPI()


def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    """Create database tables on startup."""
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "User Service is running!"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database_connection": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed") from e


@app.post(
    "/users/profile",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_profile(
    profile: UserProfileCreate, db: Session = Depends(get_db)
):
    """Create a new user profile.

    This endpoint allows creation of new user profiles with validation
    for unique username and email constraints.
    """
    logger.info(f"Creating user profile for username: {profile.username}")

    try:
        # Check for existing username
        existing_username = (
            db.query(User).filter(User.username == profile.username).first()
        )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{profile.username}' already exists",
            )

        # Check for existing email
        existing_email = db.query(User).filter(User.email == profile.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{profile.email}' already exists",
            )

        # Create new user
        db_user = User(
            username=profile.username, email=profile.email, full_name=profile.full_name
        )

        # Save to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)  # Get updated record with ID and timestamps

        # Build response
        response = UserProfileResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            created_at=db_user.created_at.isoformat(),
        )

        logger.info(f"Successfully created user profile with ID: {db_user.id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user profile: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating user profile",
        ) from e
