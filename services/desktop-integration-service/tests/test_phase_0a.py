"""
Phase 0A Tests - Desktop Integration Service Foundation

Tests for:
- Settings configuration
- Service discovery
- Pydantic models
- Main FastAPI app structure
"""

import asyncio

# Add path for imports
import sys
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, "/home/asif1/open-talent/microservices/desktop-integration-service")

from app.config.settings import settings
from app.core.service_discovery import ServiceDiscovery, ServiceHealthCache
from app.models.schemas import (
    HealthResponse,
    InterviewConfig,
    InterviewSession,
    Message,
    ModelInfo,
    StartInterviewRequest,
)

# ============================================================================
# Settings Tests
# ============================================================================


def test_settings_loaded():
    """Test that settings load correctly from environment."""
    assert settings.port == 8009
    assert settings.host == "0.0.0.0"
    assert settings.service_timeout > 0
    assert settings.health_cache_ttl > 0


def test_settings_service_urls():
    """Test that service URLs are configured."""
    assert settings.granite_interview_url
    assert settings.conversation_service_url
    assert settings.voice_service_url
    assert settings.avatar_service_url
    assert settings.interview_service_url
    assert settings.analytics_service_url
    assert settings.ollama_url


# ============================================================================
# Service Discovery Tests
# ============================================================================


def test_service_health_cache():
    """Test service health caching mechanism."""
    cache = ServiceHealthCache(ttl_seconds=5)

    test_data = {"status": "online", "services": {}}

    # Set cache
    cache.set(test_data)
    assert cache.is_valid()
    assert cache.get() == test_data

    # Manually expire cache
    cache.set_time = datetime.now().timestamp() - 10
    assert not cache.is_valid()
    assert cache.get() is None


async def test_service_discovery_initialization():
    """Test service discovery module initializes."""
    discovery = ServiceDiscovery()
    assert discovery is not None
    assert discovery.health_cache is not None
    assert len(discovery.services) == 7  # 7 services configured


# ============================================================================
# Pydantic Model Tests
# ============================================================================


def test_message_model():
    """Test Message pydantic model."""
    msg = Message(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"

    # Test serialization
    msg_dict = msg.dict()
    assert msg_dict["role"] == "user"


def test_interview_config_model():
    """Test InterviewConfig model."""
    config = InterviewConfig(role="Software Engineer", model="granite-2b", totalQuestions=5)
    assert config.role == "Software Engineer"
    assert config.totalQuestions == 5


def test_interview_session_model():
    """Test InterviewSession model - CRITICAL for desktop app contract."""
    config = InterviewConfig(role="Software Engineer", model="granite-2b", totalQuestions=5)

    messages = [
        Message(role="system", content="You are an interviewer"),
        Message(role="assistant", content="Hello, let's begin!"),
    ]

    session = InterviewSession(
        config=config, messages=messages, currentQuestion=1, isComplete=False
    )

    # Verify contract matches desktop app expectations
    assert session.config.role == "Software Engineer"
    assert len(session.messages) == 2
    assert session.currentQuestion == 1
    assert not session.isComplete

    # Test serialization
    session_dict = session.dict()
    assert "config" in session_dict
    assert "messages" in session_dict
    assert "currentQuestion" in session_dict


def test_start_interview_request_model():
    """Test StartInterviewRequest model."""
    request = StartInterviewRequest(role="Software Engineer", model="granite-2b", totalQuestions=5)
    assert request.role == "Software Engineer"


def test_model_info_model():
    """Test ModelInfo pydantic model."""
    model = ModelInfo(
        id="granite-2b",
        name="Granite 2B",
        paramCount="2B",
        ramRequired="8GB",
        downloadSize="1.2GB",
        description="Trained model",
        dataset="interviews",
        source="granite-interview-service",
    )
    assert model.id == "granite-2b"
    assert model.paramCount == "2B"


def test_health_response_model():
    """Test HealthResponse model."""
    health = HealthResponse(
        status="online",
        timestamp=datetime.now(),
        services={},
        summary={"online": 7, "total": 7, "percentage": 100},
    )
    assert health.status == "online"
    assert health.summary["total"] == 7


# ============================================================================
# Main App Structure Tests
# ============================================================================


def test_app_imports():
    """Test that main app can be imported without errors."""
    try:
        from app.main import app

        assert app is not None
    except Exception as e:
        pytest.fail(f"Failed to import main app: {e}")


def test_app_endpoints_exist():
    """Test that all required endpoints are registered."""
    from app.main import app

    # Get all registered routes
    routes = [route.path for route in app.routes]

    # Verify critical endpoints exist
    assert "/" in routes, "Root endpoint missing"
    assert "/health" in routes, "Health endpoint missing"
    assert "/api/v1/models" in routes, "Models endpoint missing"
    assert "/api/v1/interviews/start" in routes, "Start interview endpoint missing"
    assert "/api/v1/interviews/respond" in routes, "Respond interview endpoint missing"
    assert "/api/v1/interviews/summary" in routes, "Interview summary endpoint missing"
    assert "/api/v1/dashboard" in routes, "Dashboard endpoint missing"


def test_app_cors_configured():
    """Test that CORS is configured."""
    from app.main import app

    # Check for CORS middleware
    cors_middleware = [m for m in app.user_middleware if "CORSMiddleware" in str(m)]
    assert len(cors_middleware) > 0, "CORS middleware not configured"


# ============================================================================
# Integration Tests
# ============================================================================


def test_client_can_connect():
    """Test that TestClient can connect to app."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["service"] == "OpenTalent Desktop Integration Service"


def test_root_endpoint():
    """Test root endpoint returns proper info."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.1.0"
    assert "endpoints" in data


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    try:
        # Settings Tests
        test_settings_loaded()
        test_settings_service_urls()

        # Service Discovery Tests
        test_service_health_cache()
        asyncio.run(test_service_discovery_initialization())

        # Model Tests
        test_message_model()
        test_interview_config_model()
        test_interview_session_model()
        test_start_interview_request_model()
        test_model_info_model()
        test_health_response_model()

        # App Tests
        test_app_imports()
        test_app_endpoints_exist()
        test_app_cors_configured()

        # Integration Tests
        test_client_can_connect()
        test_root_endpoint()

    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
