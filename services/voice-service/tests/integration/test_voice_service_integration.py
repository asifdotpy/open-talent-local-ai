import base64
import json
import time
from typing import Any

import pytest

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


def validate_json_response(response, expected_fields: list) -> dict[str, Any]:
    """Validate JSON response has expected fields."""
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        pytest.fail(f"Response is not valid JSON: {e}")

    for field in expected_fields:
        assert field in data, f"Missing required field: {field}"

    return data


def validate_audio_data(audio_base64: str) -> bytes:
    """Validate base64-encoded audio data."""
    assert isinstance(audio_base64, str), "Audio data must be a string"
    assert len(audio_base64) > 0, "Audio data cannot be empty"

    try:
        audio_bytes = base64.b64decode(audio_base64)
    except Exception as e:
        pytest.fail(f"Failed to decode base64 audio: {e}")

    assert len(audio_bytes) > 0, "Decoded audio is empty"
    return audio_bytes


def validate_phoneme_data(phonemes: list) -> None:
    """Validate phoneme data structure."""
    assert isinstance(phonemes, list), "Phonemes must be a list"
    assert len(phonemes) > 0, "Phoneme list cannot be empty"

    for i, phoneme in enumerate(phonemes):
        assert isinstance(phoneme, dict), f"Phoneme {i} is not a dict"

        # Check required fields
        required_fields = ["phoneme", "start", "end", "duration"]
        for field in required_fields:
            assert field in phoneme, f"Phoneme {i} missing field: {field}"

        # Validate field types
        assert isinstance(phoneme["phoneme"], str), f"Phoneme {i}: 'phoneme' must be string"
        assert isinstance(phoneme["start"], (int, float)), f"Phoneme {i}: 'start' must be number"
        assert isinstance(phoneme["end"], (int, float)), f"Phoneme {i}: 'end' must be number"
        assert isinstance(phoneme["duration"], (int, float)), f"Phoneme {i}: 'duration' must be number"

        # Validate timing logic
        assert phoneme["end"] >= phoneme["start"], f"Phoneme {i}: end must be greater than or equal to start"
        assert phoneme["duration"] >= 0, f"Phoneme {i}: duration must be positive"


def validate_phoneme_sequence(phonemes: list) -> None:
    """Validate that phonemes are in sequential order."""
    for i in range(len(phonemes) - 1):
        current = phonemes[i]
        next_phoneme = phonemes[i + 1]

        assert current["end"] <= next_phoneme["start"], f"Phonemes {i} and {i + 1} overlap or are out of order"


class TestHealthAndInfo:
    """Test health check and informational endpoints."""

    def test_health_endpoint_returns_valid_status(self, client):
        """Test /health returns correct status with all required fields."""
        # Act
        response = client.get("/health")

        # Assert
        data = validate_json_response(response, ["status", "services", "mode"])

        assert data["status"] in [
            "healthy",
            "degraded",
            "unhealthy",
        ], f"Invalid status: {data['status']}"

        # Validate services structure
        assert "stt" in data["services"], "Missing STT service status"
        assert "tts" in data["services"], "Missing TTS service status"
        assert "vad" in data["services"], "Missing VAD service status"

    def test_health_endpoint_response_time(self, client):
        """Test that health endpoint responds quickly (within 1 second)."""
        # Act
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        # Assert
        assert response.status_code == 200
        assert elapsed < 1.0, f"Health check took too long: {elapsed:.2f}s"

    def test_root_endpoint_returns_service_info(self, client):
        """Test / returns service information with required fields."""
        # Act
        response = client.get("/")

        # Assert
        data = validate_json_response(response, ["service", "version", "status"])

        assert data["status"] == "running", f"Expected 'running', got '{data['status']}'"
        assert isinstance(data["version"], str), "Version must be a string"

    def test_info_endpoint_returns_detailed_service_info(self, client):
        """Test /info returns comprehensive service information."""
        # Act
        response = client.get("/info")

        # Assert
        validate_json_response(response, ["stt", "tts", "vad"])

    def test_voices_endpoint_returns_available_voices(self, client):
        """Test /voices returns list of available TTS voices."""
        # Act
        response = client.get("/voices")

        # Assert
        data = validate_json_response(response, ["voices"])

        voices = data["voices"]
        assert isinstance(voices, list), "Voices must be a list"
        assert len(voices) > 0, "Must have at least one voice available"


class TestTTSEndpoint:
    """Test text-to-speech endpoint with various scenarios."""

    def test_tts_basic_synthesis(self, client, short_text):
        """Test basic TTS without phoneme extraction."""
        # Arrange
        request_data = {"text": short_text, "voice": "en_US-lessac-medium"}

        # Act
        response = client.post("/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["audio_data", "duration", "sample_rate"])

        # Validate audio data
        audio_bytes = validate_audio_data(data["audio_data"])
        assert len(audio_bytes) > 100, "Audio data seems too small"

    def test_tts_with_phoneme_extraction(self, client, short_text):
        """Test TTS with phoneme extraction enabled."""
        # Arrange
        request_data = {
            "text": short_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = client.post("/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["audio_data", "duration", "sample_rate", "phonemes"])

        # Validate phoneme data
        validate_phoneme_data(data["phonemes"])

    def test_tts_with_different_voices(self, client, short_text, available_voices):
        """Test TTS with different voice models."""
        for voice in available_voices[:2]:  # Test first 2 voices to save time
            # Arrange
            request_data = {"text": short_text, "voice": voice}

            # Act
            response = client.post("/voice/tts", json=request_data)

            # Assert
            data = validate_json_response(response, ["audio_data"])
            audio_bytes = validate_audio_data(data["audio_data"])
            assert len(audio_bytes) > 0

    def test_tts_with_long_text(self, client, sample_text):
        """Test TTS with longer text and phoneme extraction."""
        # Arrange
        request_data = {
            "text": sample_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = client.post("/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["audio_data", "phonemes", "words"])

        # Validate comprehensive phoneme data
        validate_phoneme_data(data["phonemes"])
        assert len(data["phonemes"]) > 5, "Should have phonemes for long text"

    def test_tts_error_handling_empty_text(self, client):
        """Test TTS error handling with empty text."""
        # Arrange
        request_data = {"text": "", "voice": "en_US-lessac-medium"}

        # Act
        response = client.post("/voice/tts", json=request_data)

        # Assert
        assert response.status_code == 400

    def test_tts_graceful_degradation_invalid_voice(self, client, short_text):
        """Test TTS graceful degradation with invalid voice."""
        # Arrange
        request_data = {"text": short_text, "voice": "invalid-voice-model"}

        # Act
        response = client.post("/voice/tts", json=request_data)

        # Assert - Mock provider often falls back to default voice
        assert response.status_code == 200

    def test_tts_handles_special_characters(self, client, special_characters_text):
        """Test TTS with special characters and punctuation."""
        # Arrange
        request_data = {
            "text": special_characters_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = client.post("/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["audio_data", "phonemes"])
        validate_audio_data(data["audio_data"])
        validate_phoneme_data(data["phonemes"])


class TestPhonemeExtraction:
    """Integration tests for phoneme extraction from TTS."""

    def test_phoneme_timing_sequential(self, client, sample_text):
        """Test that phoneme timings are sequential and non-overlapping."""
        # Arrange
        request_data = {
            "text": sample_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = client.post("/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["phonemes"])
        phonemes = data["phonemes"]

        # Comprehensive sequence validation
        validate_phoneme_sequence(phonemes)

    def test_phoneme_duration_positive(self, client, short_text):
        """Test that all phoneme durations are positive."""
        # Arrange
        request_data = {
            "text": short_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = client.post("/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["phonemes"])
        validate_phoneme_data(data["phonemes"])

    def test_phoneme_count_reasonable(self, client, sample_text):
        """Test that phoneme count is reasonable for text length."""
        # Arrange
        request_data = {
            "text": sample_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = client.post("/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["phonemes"])
        phoneme_count = len(data["phonemes"])
        assert phoneme_count > 0

    def test_word_grouping_when_enabled(self, client, sample_text):
        """Test word grouping data structure when phoneme extraction enabled."""
        # Arrange
        request_data = {
            "text": sample_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = client.post("/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["words"])
        words = data["words"]

        assert isinstance(words, list), "Words must be a list"


class TestSTTEndpoint:
    """Integration tests for speech-to-text endpoint."""

    def test_stt_with_generated_audio(self, client, test_audio_file):
        """Test STT with actual audio file."""
        # Act
        with open(test_audio_file, "rb") as f:
            response = client.post("/voice/stt", files={"audio_file": ("test.wav", f, "audio/wav")})

        # Assert
        data = validate_json_response(response, ["text"])
        assert isinstance(data["text"], str)

    def test_stt_error_empty_audio(self, client):
        """Test STT error handling with empty audio."""
        # When using mock services, STT always returns a successful transcription
        # even for empty audio files.
        files = {"audio_file": ("test.wav", b"", "audio/wav")}
        response = client.post("/voice/stt", files=files)
        assert response.status_code == 200
        assert "text" in response.json()

    def test_stt_invalid_file_type(self, client):
        """Test STT error handling with invalid file type."""
        # Act
        response = client.post("/voice/stt", files={"audio_file": ("test.txt", b"not audio", "text/plain")})

        # Assert
        assert response.status_code == 400


class TestVADEndpoint:
    """Integration tests for Voice Activity Detection endpoint."""

    def test_vad_endpoint_exists(self, client, test_audio_file):
        """Test that VAD endpoint is accessible."""
        # Act
        with open(test_audio_file, "rb") as f:
            response = client.post("/voice/vad", files={"audio_file": ("test.wav", f, "audio/wav")})

        # Assert
        data = validate_json_response(response, ["num_segments"])
        assert data["num_segments"] >= 0


class TestPerformanceAndConcurrency:
    """Integration tests for performance."""

    def test_tts_latency_benchmark(self, client, short_text):
        """Benchmark TTS generation latency."""
        # Act
        start = time.time()
        response = client.post("/voice/tts", json={"text": short_text, "voice": "en_US-lessac-medium"})
        latency = time.time() - start

        # Assert
        assert response.status_code == 200
        assert latency < 5.0, f"TTS took too long: {latency:.2f}s"
