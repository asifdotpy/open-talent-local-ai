"""Test configuration for the current Interview Service implementation.

Provides fixtures and setup for testing the standalone FastAPI application.
"""

import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from app.core.config import settings
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine


@pytest.fixture(scope="session")
def engine():
    """Create a test database engine."""
    # The `echo=True` will log all SQL statements, which is useful for debugging
    return create_engine(str(settings.TEST_DATABASE_URI), echo=False)


@pytest.fixture(scope="function")
def db(engine):
    """Create a new database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_voice_service():
    """Mock voice service responses."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ready",
            "connection_id": "voice-conn-123",
            "session_id": "voice-session-123",
        }
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_conversation_service():
    """Mock conversation service responses."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "question": "Can you describe your experience with Python?",
            "difficulty": "medium",
            "bias_score": 0.1,
            "sentiment_context": "neutral",
        }
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_avatar_service():
    """Mock avatar service responses."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ready",
            "avatar_id": "avatar-123",
            "session_id": "avatar-session-123",
        }
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        yield mock_client


@pytest.fixture
def sample_interview_session() -> dict[str, Any]:
    """Sample interview session data."""
    return {
        "interview_session_id": "session-123",
        "participants": [
            {
                "user_id": "interviewer-1",
                "name": "John Interviewer",
                "email": "john@example.com",
                "role": "interviewer",
            },
            {
                "user_id": "candidate-1",
                "name": "Jane Candidate",
                "email": "jane@example.com",
                "role": "candidate",
            },
        ],
        "duration_minutes": 45,
        "job_id": "job-123",
        "job_description": "Senior Python Developer position",
    }


@pytest.fixture
def sample_transcription_segment() -> dict[str, Any]:
    """Sample transcription segment data."""
    return {
        "text": "I have extensive experience with Python and Django.",
        "start_time": 0.0,
        "end_time": 3.2,
        "confidence": 0.95,
        "speaker_id": "candidate-1",
        "is_final": True,
        "words": [
            {"word": "I", "start": 0.0, "end": 0.2, "confidence": 0.98},
            {"word": "have", "start": 0.2, "end": 0.5, "confidence": 0.97},
            {"word": "extensive", "start": 0.5, "end": 1.0, "confidence": 0.96},
        ],
    }


@pytest.fixture
def sample_response_analysis() -> dict[str, Any]:
    """Sample response analysis data."""
    return {
        "question_id": "q-123",
        "response_text": "I have 5 years of experience with Python and Django.",
        "question_context": "Tell me about your Python experience.",
        "participant_id": "candidate-1",
    }


@pytest.fixture
def sample_webrtc_offer() -> dict[str, Any]:
    """Sample WebRTC offer data."""
    return {
        "type": "offer",
        "session_id": "session-123",
        "participant_id": "candidate-1",
        "data": {
            "sdp": "v=0\r\no=- 123456789 123456789 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n...",
            "type": "offer",
        },
    }


@pytest.fixture
def sample_webrtc_answer() -> dict[str, Any]:
    """Sample WebRTC answer data."""
    return {
        "type": "answer",
        "session_id": "session-123",
        "participant_id": "candidate-1",
        "data": {
            "sdp": "v=0\r\no=- 987654321 987654321 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n...",
            "type": "answer",
        },
    }


@pytest.fixture
def sample_candidate_response() -> dict[str, Any]:
    """Sample candidate response for AI analysis."""
    return {
        "question_id": "q-123",
        "response_text": "I have been working with Python for 5 years, primarily building web applications with Django and Flask. I've also worked with data science libraries like pandas and numpy.",
        "question_context": "Can you tell me about your experience with Python?",
        "participant_id": "candidate-1",
    }


@pytest.fixture
def sample_interview_adaptation() -> dict[str, Any]:
    """Sample interview adaptation data."""
    return {
        "current_phase": "technical",
        "time_remaining_minutes": 25,
        "performance_indicators": {
            "sentiment_trend": "positive",
            "quality_score": 8.5,
            "expertise_level": "senior",
            "bias_flags": [],
        },
    }


@pytest.fixture(autouse=True)
def clear_room_storage():
    """Clear room storage before each test."""
    from main import (
        rooms_store,
        transcription_history,
        webrtc_connections,
        websocket_connections,
    )

    rooms_store.clear()
    transcription_history.clear()
    webrtc_connections.clear()
    websocket_connections.clear()
    yield


@pytest.fixture
def test_client():
    """Create test client for the structured API app."""
    from app.main import app

    return TestClient(app)


@pytest.fixture
def test_client_rooms():
    """Create test client for the rooms/WebRTC app."""
    from main import app

    return TestClient(app)


# Custom test markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "ai: mark test as AI intelligence test")
    config.addinivalue_line("markers", "webrtc: mark test as WebRTC test")
    config.addinivalue_line("markers", "transcription: mark test as transcription test")
