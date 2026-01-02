"""
Pytest configuration and shared fixtures for all microservices
Located at: /services/conftest.py
"""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator

import httpx
import pytest

# ============================================================================
# ASYNCIO CONFIGURATION
# ============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# HTTP CLIENT FIXTURES
# ============================================================================


@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client for making requests to services"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        yield client


# ============================================================================
# SERVICE URL FIXTURES
# ============================================================================


@pytest.fixture
def base_service_url() -> str:
    """Base URL for services"""
    return os.getenv("SERVICE_BASE_URL", "http://localhost")


@pytest.fixture
def notification_service_url(base_service_url) -> str:
    return f"{base_service_url}:8011"


@pytest.fixture
def security_service_url(base_service_url) -> str:
    return f"{base_service_url}:8010"


@pytest.fixture
def user_service_url(base_service_url) -> str:
    return f"{base_service_url}:8007"


@pytest.fixture
def candidate_service_url(base_service_url) -> str:
    return f"{base_service_url}:8008"


@pytest.fixture
def interview_service_url(base_service_url) -> str:
    return f"{base_service_url}:8006"


@pytest.fixture
def granite_interview_service_url(base_service_url) -> str:
    return f"{base_service_url}:8005"


@pytest.fixture
def conversation_service_url(base_service_url) -> str:
    return f"{base_service_url}:8014"


@pytest.fixture
def voice_service_url(base_service_url) -> str:
    return f"{base_service_url}:8015"


@pytest.fixture
def avatar_service_url(base_service_url) -> str:
    return f"{base_service_url}:8016"


@pytest.fixture
def analytics_service_url(base_service_url) -> str:
    return f"{base_service_url}:8017"


@pytest.fixture
def scout_service_url(base_service_url) -> str:
    return f"{base_service_url}:8010"


@pytest.fixture
def ai_auditing_service_url(base_service_url) -> str:
    return f"{base_service_url}:8012"


@pytest.fixture
def explainability_service_url(base_service_url) -> str:
    return f"{base_service_url}:8013"


@pytest.fixture
def desktop_service_url(base_service_url) -> str:
    return f"{base_service_url}:8009"


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================


@pytest.fixture
def test_token() -> str:
    """Test JWT token for authenticated requests"""
    return "test_jwt_token_xyz"


@pytest.fixture
def auth_headers(test_token) -> dict:
    """Authorization headers with Bearer token"""
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture
def admin_headers(test_token) -> dict:
    """Authorization headers for admin user"""
    return {"Authorization": f"Bearer {test_token}", "X-User-Role": "admin"}


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================


@pytest.fixture
def valid_credentials() -> dict:
    """Valid login credentials for testing"""
    return {"email": "testuser@example.com", "password": "TestPassword123!"}


@pytest.fixture
def invalid_credentials() -> dict:
    """Invalid login credentials for testing"""
    return {"email": "testuser@example.com", "password": "wrongpassword"}


@pytest.fixture
def new_user_data() -> dict:
    """New user registration data"""
    return {
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def user_update_data() -> dict:
    """User update data"""
    return {"first_name": "Updated", "last_name": "Name", "phone": "+1987654321"}


@pytest.fixture
def email_notification_data() -> dict:
    """Email notification data"""
    return {
        "to": "user@example.com",
        "subject": "Test Subject",
        "html": "<h1>Test Email</h1>",
        "text": "Test Email",
    }


@pytest.fixture
def sms_notification_data() -> dict:
    """SMS notification data"""
    return {"to": "+1234567890", "text": "Test SMS message"}


@pytest.fixture
def push_notification_data() -> dict:
    """Push notification data"""
    return {
        "to": "device_token_123",
        "title": "Test Notification",
        "body": "This is a test notification",
    }


@pytest.fixture
def interview_data() -> dict:
    """Interview scheduling data"""
    return {
        "candidate_id": "candidate123",
        "job_id": "job123",
        "interview_type": "technical",
        "scheduled_time": "2024-12-20T14:00:00Z",
        "interviewer_id": "interviewer123",
        "duration_minutes": 60,
    }


@pytest.fixture
def interview_feedback_data() -> dict:
    """Interview feedback data"""
    return {
        "rating": 4,
        "technical_skills": 4,
        "communication": 4,
        "comments": "Good candidate",
        "recommendation": "hire",
    }


@pytest.fixture
def candidate_data() -> dict:
    """Candidate profile data"""
    return {
        "email": "candidate@example.com",
        "first_name": "John",
        "last_name": "Candidate",
        "phone": "+1234567890",
        "resume_url": "https://example.com/resume.pdf",
    }


@pytest.fixture
def avatar_data() -> dict:
    """Avatar customization data"""
    return {
        "name": "TestAvatar",
        "model": "default_humanoid",
        "skin_tone": "medium",
        "hair_style": "style1",
    }


@pytest.fixture
def synthesis_data() -> dict:
    """Voice synthesis data"""
    return {"text": "Hello, this is a test message", "voice": "default", "speed": 1.0, "pitch": 1.0}


# ============================================================================
# PYTEST HOOKS
# ============================================================================


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "asyncio: mark test as async")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add asyncio marker automatically"""
    for item in items:
        if "async_client" in item.fixturenames:
            item.add_marker(pytest.mark.asyncio)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


async def make_authenticated_request(
    client: httpx.AsyncClient, method: str, url: str, auth_headers: dict, **kwargs
) -> httpx.Response:
    """Helper function to make authenticated HTTP requests"""
    kwargs.setdefault("headers", {})
    kwargs["headers"].update(auth_headers)

    if method.upper() == "GET":
        return await client.get(url, **kwargs)
    elif method.upper() == "POST":
        return await client.post(url, **kwargs)
    elif method.upper() == "PUT":
        return await client.put(url, **kwargs)
    elif method.upper() == "PATCH":
        return await client.patch(url, **kwargs)
    elif method.upper() == "DELETE":
        return await client.delete(url, **kwargs)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")


# ============================================================================
# SERVICE HEALTH CHECK
# ============================================================================


async def check_service_health(client: httpx.AsyncClient, service_url: str) -> bool:
    """Check if a service is healthy"""
    try:
        response = await client.get(f"{service_url}/health", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="session", autouse=True)
async def health_check(event_loop):
    """Health check for all services before running tests"""
    # This is a no-op if services aren't running, tests will skip gracefully
    pass
