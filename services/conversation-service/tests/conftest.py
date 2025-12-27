"""Shared fixtures for Conversation Service tests.

Sets env flags to force mock LLM and disable DB writes, then exposes a
FastAPI TestClient bound to the app for in-process testing.
"""
import os

import pytest
from fastapi.testclient import TestClient

# Set env before importing the app so globals pick them up
os.environ.setdefault("USE_MOCK_OLLAMA", "true")
os.environ.setdefault("USE_DATABASE", "false")
os.environ.setdefault("OLLAMA_MODEL", "granite4:350m-h")

from app.services.conversation_service import conversation_service
from main import app


@pytest.fixture
def test_client():
    """In-process FastAPI client."""
    client = TestClient(app)
    # Clear conversation state between tests
    conversation_service.active_conversations.clear()
    yield client
    conversation_service.active_conversations.clear()
