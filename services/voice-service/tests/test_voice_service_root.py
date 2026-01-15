"""Tests for Voice Service
Following TDD principles - tests written before implementation
Port: 8015
Purpose: Text-to-speech, voice synthesis, audio processing.
"""

from typing import Any

import httpx
import pytest


@pytest.fixture
def voice_service_url():
    return "http://localhost:8003"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=5.0)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def synthesis_data() -> dict[str, Any]:
    return {
        "text": "Hello, this is a test message",
        "voice_id": "default",
        "speaking_rate": 1.0,
        "pitch": 0.0,
        "volume_gain_db": 0.0,
    }


import pytest


class TestVoiceServiceBasics:
    def test_service_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["service"] == "Voice Service"


class TestTextToSpeech:
    def test_synthesize_speech(self, client):
        payload = {"text": "Hello, this is a test message", "voice": "en_US-lessac-medium"}
        response = client.post("/voice/tts", json=payload)
        assert response.status_code == 200
        assert "audio_data" in response.json()

    def test_get_available_voices(self, client):
        response = client.get("/voices")
        assert response.status_code == 200
        assert "voices" in response.json()


class TestAudioProcessing:
    def test_vad_functionality(self, client, test_audio_file):
        with open(test_audio_file, "rb") as f:
            response = client.post("/voice/vad", files={"audio_file": ("test.wav", f, "audio/wav")})
        assert response.status_code == 200
        assert "num_segments" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
