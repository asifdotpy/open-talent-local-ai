"""
Pytest configuration and shared fixtures for User Service tests.

Fixtures:
- test_db: Database session for integration tests
- test_client: FastAPI TestClient
- jwt_token: Valid JWT token for authenticated requests
- admin_claims: Admin JWT claims
- recruiter_claims: Recruiter JWT claims
- candidate_claims: Candidate JWT claims
"""

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta

import jwt
import pytest
from app.config import settings
from app.database import Base, get_session
from app.main import app
from app.utils import JWTClaims
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Test database URL (use same compose DB or separate test DB)
TEST_DATABASE_URL = settings.database_url.replace("/user_service", "/user_service_test")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create test database if not exists
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session with RLS context."""
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Set default RLS context for tests
        await session.execute(text("SET app.user_email = 'test@example.com'"))
        await session.execute(text("SET app.user_role = 'admin'"))
        await session.execute(text("SET app.tenant_id = 'test-tenant'"))

        yield session

        # Rollback after each test
        await session.rollback()


@pytest.fixture(scope="function")
async def test_client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create FastAPI test client with database override."""

    async def override_get_session():
        yield test_db

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


def create_jwt_token(
    email: str,
    user_id: str = "test-user-id",
    role: str = "admin",
    tenant_id: str = "test-tenant",
    exp_minutes: int = 30,
) -> str:
    """Create JWT token for testing."""
    payload = {
        "email": email,
        "user_id": user_id,
        "role": role,
        "tenant_id": tenant_id,
        "exp": datetime.utcnow() + timedelta(minutes=exp_minutes),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


@pytest.fixture
def admin_token() -> str:
    """Valid JWT token for admin user."""
    return create_jwt_token(
        email="admin@example.com",
        role="admin",
        tenant_id="tenant1",
    )


@pytest.fixture
def recruiter_token() -> str:
    """Valid JWT token for recruiter user."""
    return create_jwt_token(
        email="recruiter@example.com",
        role="recruiter",
        tenant_id="tenant1",
    )


@pytest.fixture
def candidate_token() -> str:
    """Valid JWT token for candidate user."""
    return create_jwt_token(
        email="candidate@example.com",
        role="candidate",
        tenant_id="tenant1",
    )


@pytest.fixture
def admin_claims() -> JWTClaims:
    """Admin JWT claims."""
    return JWTClaims(
        email="admin@example.com",
        user_id="admin-id",
        role="admin",
        tenant_id="tenant1",
    )


@pytest.fixture
def recruiter_claims() -> JWTClaims:
    """Recruiter JWT claims."""
    return JWTClaims(
        email="recruiter@example.com",
        user_id="recruiter-id",
        role="recruiter",
        tenant_id="tenant1",
    )


@pytest.fixture
def candidate_claims() -> JWTClaims:
    """Candidate JWT claims."""
    return JWTClaims(
        email="candidate@example.com",
        user_id="candidate-id",
        role="candidate",
        tenant_id="tenant1",
    )


@pytest.fixture
def auth_headers_admin(admin_token: str) -> dict:
    """Authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def auth_headers_recruiter(recruiter_token: str) -> dict:
    """Authorization headers with recruiter token."""
    return {"Authorization": f"Bearer {recruiter_token}"}


@pytest.fixture
def auth_headers_candidate(candidate_token: str) -> dict:
    """Authorization headers with candidate token."""
    return {"Authorization": f"Bearer {candidate_token}"}


# Sample test data fixtures
@pytest.fixture
def sample_user_data() -> dict:
    """Sample user creation data."""
    return {
        "email": "newuser@example.com",
        "full_name": "New User",
        "role": "candidate",
        "status": "active",
        "tenant_id": "tenant1",
    }


@pytest.fixture
def sample_profile_data() -> dict:
    """Sample user profile data."""
    return {
        "phone": "+1234567890",
        "location": "San Francisco, CA",
        "bio": "Experienced software engineer",
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience_years": 5,
    }


@pytest.fixture
def sample_preferences_data() -> dict:
    """Sample user preferences data."""
    return {
        "email_notifications": True,
        "push_notifications": False,
        "language": "en",
        "timezone": "America/Los_Angeles",
        "theme": "dark",
    }
