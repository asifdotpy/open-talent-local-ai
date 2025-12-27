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

"""
Pytest configuration and shared fixtures for User Service tests.
"""

from datetime import datetime, timedelta

import jwt
import pytest
from app.config import settings
from app.main import app
from app.utils import JWTClaims
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    return TestClient(app)


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
