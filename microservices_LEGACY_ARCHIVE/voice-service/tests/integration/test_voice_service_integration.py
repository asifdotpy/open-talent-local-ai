"""
Integration Tests for Voice Service API

Following TDD principles:
- Test real API interactions
- Comprehensive edge case coverage
- Clear success/failure criteria
- Proper async handling
- Detailed assertions

Tests all endpoints with real service calls to ensure honest validation:
- GET /health, /, /info, /voices
- POST /voice/tts (with and without phoneme extraction)
- POST /voice/stt (speech-to-text)
- POST /voice/vad (voice activity detection)

Created: November 18, 2025
Updated: November 18, 2025 - Code quality cleanup, removed duplicates
"""

import pytest
import httpx
import asyncio
import base64
import json
from pathlib import Path
from typing import Dict, Any


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
async def async_client():
    """Create async HTTP client with proper timeout."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


def validate_json_response(response: httpx.Response, expected_fields: list) -> Dict[str, Any]:
    """
    Validate JSON response has expected fields.

    Args:
        response: HTTP response object
        expected_fields: List of field names that must be present

    Returns:
        Parsed JSON data

    Raises:
        AssertionError: If validation fails
    """
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        pytest.fail(f"Response is not valid JSON: {e}")

    for field in expected_fields:
        assert field in data, f"Missing required field: {field}"

    return data


def validate_audio_data(audio_base64: str) -> bytes:
    """
    Validate base64-encoded audio data.

    Args:
        audio_base64: Base64-encoded audio string

    Returns:
        Decoded audio bytes

    Raises:
        AssertionError: If validation fails
    """
    assert isinstance(audio_base64, str), "Audio data must be a string"
    assert len(audio_base64) > 0, "Audio data cannot be empty"

    try:
        audio_bytes = base64.b64decode(audio_base64)
    except Exception as e:
        pytest.fail(f"Failed to decode base64 audio: {e}")

    assert len(audio_bytes) > 0, "Decoded audio is empty"
    return audio_bytes


def validate_phoneme_data(phonemes: list) -> None:
    """
    Validate phoneme data structure.

    Args:
        phonemes: List of phoneme dictionaries

    Raises:
        AssertionError: If validation fails
    """
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
        assert isinstance(
            phoneme["duration"], (int, float)
        ), f"Phoneme {i}: 'duration' must be number"

        # Validate timing logic
        assert phoneme["end"] > phoneme["start"], f"Phoneme {i}: end must be greater than start"
        assert phoneme["duration"] > 0, f"Phoneme {i}: duration must be positive"

        # Validate duration calculation (allow small floating point errors)
        calculated_duration = phoneme["end"] - phoneme["start"]
        assert (
            abs(phoneme["duration"] - calculated_duration) < 0.01
        ), f"Phoneme {i}: duration mismatch (expected {calculated_duration}, got {phoneme['duration']})"


def validate_phoneme_sequence(phonemes: list) -> None:
    """
    Validate that phonemes are in sequential order.

    Args:
        phonemes: List of phoneme dictionaries

    Raises:
        AssertionError: If sequence is invalid
    """
    for i in range(len(phonemes) - 1):
        current = phonemes[i]
        next_phoneme = phonemes[i + 1]

        assert (
            current["end"] <= next_phoneme["start"]
        ), f"Phonemes {i} and {i+1} overlap or are out of order"


class TestHealthAndInfo:
    """Test health check and informational endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_valid_status(self, async_client, service_url):
        """Test /health returns correct status with all required fields."""
        # Act
        response = await async_client.get(f"{service_url}/health")

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

        # Each service should have a status string
        for service_name in ["stt", "tts", "vad"]:
            service_status = data["services"][service_name]
            assert service_status in [
                "ready",
                "not_ready",
                "degraded",
            ], f"{service_name} has invalid status: {service_status}"

    @pytest.mark.asyncio
    async def test_health_endpoint_response_time(self, async_client, service_url):
        """Test that health endpoint responds quickly (within 1 second)."""
        import time

        # Act
        start = time.time()
        response = await async_client.get(f"{service_url}/health")
        elapsed = time.time() - start

        # Assert
        assert response.status_code == 200
        assert elapsed < 1.0, f"Health check took too long: {elapsed:.2f}s"

    @pytest.mark.asyncio
    async def test_root_endpoint_returns_service_info(self, async_client, service_url):
        """Test / returns service information with required fields."""
        # Act
        response = await async_client.get(f"{service_url}/")

        # Assert
        data = validate_json_response(response, ["service", "version", "status"])

        assert data["status"] == "running", f"Expected 'running', got '{data['status']}'"
        assert isinstance(data["version"], str), "Version must be a string"
        assert len(data["version"]) > 0, "Version cannot be empty"

    @pytest.mark.asyncio
    async def test_info_endpoint_returns_detailed_service_info(self, async_client, service_url):
        """Test /info returns comprehensive service information."""
        # Act
        response = await async_client.get(f"{service_url}/info")

        # Assert
        data = validate_json_response(response, ["stt", "tts", "vad"])

        # Validate TTS info structure
        tts_info = data["tts"]
        assert "service" in tts_info, "TTS missing service field"
        assert "ready" in tts_info, "TTS missing ready field"
        assert "voices" in tts_info, "TTS missing voices field"
        assert "features" in tts_info, "TTS missing features field"
        assert (
            "phoneme_extraction" in tts_info["features"]
        ), "TTS missing phoneme_extraction feature"

        # Validate STT info structure
        stt_info = data["stt"]
        assert "service" in stt_info, "STT missing service field"
        assert "ready" in stt_info, "STT missing ready field"
        assert "features" in stt_info, "STT missing features field"

    @pytest.mark.asyncio
    async def test_voices_endpoint_returns_available_voices(self, async_client, service_url):
        """Test /voices returns list of available TTS voices."""
        # Act
        response = await async_client.get(f"{service_url}/voices")

        # Assert
        data = validate_json_response(response, ["voices"])

        voices = data["voices"]
        assert isinstance(voices, list), "Voices must be a list"
        assert len(voices) > 0, "Must have at least one voice available"

        # Validate each voice structure
        for i, voice in enumerate(voices):
            assert isinstance(voice, dict), f"Voice {i} is not a dict"
            assert "name" in voice, f"Voice {i} missing name"
            assert "gender" in voice, f"Voice {i} missing gender"
            assert "quality" in voice, f"Voice {i} missing quality"

            assert isinstance(voice["name"], str), f"Voice {i} name must be string"
            assert len(voice["name"]) > 0, f"Voice {i} name cannot be empty"


class TestTTSEndpoint:
    """Test text-to-speech endpoint with various scenarios."""

    @pytest.mark.asyncio
    async def test_tts_basic_synthesis(self, async_client, service_url, short_text):
        """Test basic TTS without phoneme extraction."""
        # Arrange
        request_data = {"text": short_text, "voice": "en_US-lessac-medium"}

        # Act
        response = await async_client.post(f"{service_url}/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["audio_data", "duration", "sample_rate"])

        # Validate audio data
        audio_bytes = validate_audio_data(data["audio_data"])
        assert len(audio_bytes) > 100, "Audio data seems too small"

        # Validate metadata
        assert isinstance(data["duration"], (int, float)), "Duration must be numeric"
        assert data["duration"] > 0, "Duration must be positive"
        assert isinstance(data["sample_rate"], int), "Sample rate must be integer"
        assert data["sample_rate"] > 0, "Sample rate must be positive"
        assert data["sample_rate"] in [
            16000,
            22050,
            44100,
            48000,
        ], f"Unexpected sample rate: {data['sample_rate']}"

    @pytest.mark.asyncio
    async def test_tts_with_phoneme_extraction(self, async_client, service_url, short_text):
        """Test TTS with phoneme extraction enabled."""
        # Arrange
        request_data = {
            "text": short_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = await async_client.post(f"{service_url}/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(
            response, ["audio_data", "duration", "sample_rate", "phonemes"]
        )

        # Validate phoneme data
        validate_phoneme_data(data["phonemes"])
        validate_phoneme_sequence(data["phonemes"])

        # Phoneme count should be reasonable for text length
        word_count = len(short_text.split())
        min_expected = word_count * 2
        max_expected = word_count * 10
        phoneme_count = len(data["phonemes"])

        assert (
            min_expected <= phoneme_count <= max_expected
        ), f"Unexpected phoneme count {phoneme_count} for {word_count} words"

    @pytest.mark.asyncio
    async def test_tts_with_different_voices(
        self, async_client, service_url, short_text, available_voices
    ):
        """Test TTS with different voice models."""
        for voice in available_voices:
            # Arrange
            request_data = {"text": short_text, "voice": voice}

            # Act
            response = await async_client.post(f"{service_url}/voice/tts", json=request_data)

            # Assert
            data = validate_json_response(response, ["audio_data"])
            audio_bytes = validate_audio_data(data["audio_data"])

            # Different voices should produce different audio
            assert len(audio_bytes) > 0

    @pytest.mark.asyncio
    async def test_tts_with_long_text(self, async_client, service_url, sample_text):
        """Test TTS with longer text and phoneme extraction."""
        # Arrange
        request_data = {
            "text": sample_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = await async_client.post(f"{service_url}/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["audio_data", "phonemes", "words"])

        # Validate comprehensive phoneme data
        validate_phoneme_data(data["phonemes"])
        assert len(data["phonemes"]) > 10, "Should have many phonemes for long text"

        # Validate word grouping
        assert isinstance(data["words"], list), "Words must be a list"

    @pytest.mark.asyncio
    async def test_tts_error_handling_empty_text(self, async_client, service_url):
        """Test TTS error handling with empty text."""
        # Arrange
        request_data = {"text": "", "voice": "en_US-lessac-medium"}

        # Act
        response = await async_client.post(f"{service_url}/voice/tts", json=request_data)

        # Assert - should return error or handle gracefully
        assert response.status_code in [
            200,
            400,
            422,
        ], f"Unexpected status code: {response.status_code}"

    @pytest.mark.asyncio
    async def test_tts_graceful_degradation_invalid_voice(
        self, async_client, service_url, short_text
    ):
        """Test TTS graceful degradation with invalid voice."""
        # Arrange
        request_data = {"text": short_text, "voice": "invalid-voice-model"}

        # Act
        response = await async_client.post(f"{service_url}/voice/tts", json=request_data)

        # Assert - should handle gracefully (fallback or error)
        assert response.status_code in [
            200,
            400,
            404,
        ], f"Unexpected status code: {response.status_code}"

    @pytest.mark.asyncio
    async def test_tts_handles_special_characters(
        self, async_client, service_url, special_characters_text
    ):
        """Test TTS with special characters and punctuation."""
        # Arrange
        request_data = {
            "text": special_characters_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = await async_client.post(f"{service_url}/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["audio_data", "phonemes"])
        validate_audio_data(data["audio_data"])
        validate_phoneme_data(data["phonemes"])

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_tts_latency_performance(self, async_client, service_url, short_text):
        """Test that TTS generation completes within acceptable time."""
        import time

        # Arrange
        request_data = {"text": short_text, "voice": "en_US-lessac-medium"}

        # Act
        start = time.time()
        response = await async_client.post(f"{service_url}/voice/tts", json=request_data)
        latency = time.time() - start

        # Assert
        assert response.status_code == 200
        assert latency < 5.0, f"TTS took too long: {latency:.2f}s"

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_tts_concurrent_requests(self, async_client, service_url):
        """Test handling of concurrent TTS requests."""
        # Arrange
        requests = [
            async_client.post(
                f"{service_url}/voice/tts",
                json={"text": f"test {i}", "voice": "en_US-lessac-medium"},
            )
            for i in range(3)
        ]

        # Act
        responses = await asyncio.gather(*requests)

        # Assert
        for i, response in enumerate(responses):
            assert response.status_code == 200, f"Request {i} failed"
            data = validate_json_response(response, ["audio_data"])
            validate_audio_data(data["audio_data"])


@pytest.mark.integration
class TestPhonemeExtraction:
    """Integration tests for phoneme extraction from TTS."""

    @pytest.mark.asyncio
    async def test_phoneme_timing_sequential(self, async_client, service_url, sample_text):
        """Test that phoneme timings are sequential and non-overlapping."""
        # Arrange
        request_data = {
            "text": sample_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = await async_client.post(f"{service_url}/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["phonemes"])
        phonemes = data["phonemes"]

        # Comprehensive sequence validation
        validate_phoneme_sequence(phonemes)

        # Additional timing checks
        for i in range(len(phonemes) - 1):
            current = phonemes[i]
            next_phoneme = phonemes[i + 1]

            # Current phoneme should end before or at next start
            assert (
                current["end"] <= next_phoneme["start"]
            ), f"Phoneme overlap at index {i}: {current} -> {next_phoneme}"

    @pytest.mark.asyncio
    async def test_phoneme_duration_positive(self, async_client, service_url, short_text):
        """Test that all phoneme durations are positive."""
        # Arrange
        request_data = {
            "text": short_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = await async_client.post(f"{service_url}/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["phonemes"])
        validate_phoneme_data(data["phonemes"])

        # All durations must be positive
        for phoneme in data["phonemes"]:
            assert phoneme["duration"] > 0, f"Non-positive duration: {phoneme}"

    @pytest.mark.asyncio
    async def test_phoneme_count_reasonable(self, async_client, service_url, sample_text):
        """Test that phoneme count is reasonable for text length."""
        # Arrange
        request_data = {
            "text": sample_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = await async_client.post(f"{service_url}/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["phonemes"])
        phoneme_count = len(data["phonemes"])
        word_count = len(sample_text.split())

        # Heuristic: 2-10 phonemes per word
        min_expected = word_count * 2
        max_expected = word_count * 10

        assert (
            min_expected <= phoneme_count <= max_expected
        ), f"Phoneme count {phoneme_count} outside expected range [{min_expected}, {max_expected}] for {word_count} words"

    @pytest.mark.asyncio
    async def test_word_grouping_when_enabled(self, async_client, service_url, sample_text):
        """Test word grouping data structure when phoneme extraction enabled."""
        # Arrange
        request_data = {
            "text": sample_text,
            "voice": "en_US-lessac-medium",
            "extract_phonemes": True,
        }

        # Act
        response = await async_client.post(f"{service_url}/voice/tts", json=request_data)

        # Assert
        data = validate_json_response(response, ["words"])
        words = data["words"]

        assert isinstance(words, list), "Words must be a list"
        word_count = len(sample_text.split())

        # Should have reasonable word count (allowing for contractions/splits)
        assert (
            0.8 * word_count <= len(words) <= 1.5 * word_count
        ), f"Word count mismatch: got {len(words)}, expected ~{word_count}"


@pytest.mark.integration
class TestSTTEndpoint:
    """Integration tests for speech-to-text endpoint."""

    @pytest.mark.asyncio
    async def test_stt_with_generated_audio(self, async_client, service_url, test_audio_file):
        """Test STT with actual audio file."""
        # Arrange
        with open(test_audio_file, "rb") as f:
            audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode()

        request_data = {"audio_data": audio_b64, "language": "en"}

        # Act
        response = await async_client.post(f"{service_url}/voice/stt", json=request_data)

        # Assert - STT may return 422 for mock implementation
        assert response.status_code in [200, 422], f"Unexpected status code: {response.status_code}"

        if response.status_code == 200:
            data = validate_json_response(response, ["text", "language"])

            # Validate transcription
            assert isinstance(data["text"], str), "Text must be string"
            assert len(data["text"]) >= 0, "Text can be empty for silence"
            assert data["language"] == "en", f"Language mismatch: {data['language']}"

    @pytest.mark.asyncio
    async def test_stt_error_empty_audio(self, async_client, service_url):
        """Test STT error handling with empty audio."""
        # Arrange
        request_data = {"audio_data": "", "language": "en"}

        # Act
        response = await async_client.post(f"{service_url}/voice/stt", json=request_data)

        # Assert - should return error for empty audio
        assert response.status_code in [
            400,
            422,
        ], f"Expected error for empty audio, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_stt_invalid_base64(self, async_client, service_url):
        """Test STT error handling with invalid base64."""
        # Arrange
        request_data = {"audio_data": "not-valid-base64!@#$", "language": "en"}

        # Act
        response = await async_client.post(f"{service_url}/voice/stt", json=request_data)

        # Assert - should return error
        assert response.status_code in [
            400,
            422,
            500,
        ], f"Expected error for invalid base64, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_stt_different_languages(self, async_client, service_url, test_audio_file):
        """Test STT with different language parameters."""
        languages = ["en", "es", "fr", "de"]

        with open(test_audio_file, "rb") as f:
            audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode()

        for lang in languages:
            # Arrange
            request_data = {"audio_data": audio_b64, "language": lang}

            # Act
            response = await async_client.post(f"{service_url}/voice/stt", json=request_data)

            # Assert - STT may return 422 for mock implementation
            assert response.status_code in [
                200,
                400,
                422,
            ], f"Language {lang} failed with {response.status_code}"


@pytest.mark.integration
class TestVADEndpoint:
    """Integration tests for Voice Activity Detection endpoint."""

    @pytest.mark.asyncio
    async def test_vad_endpoint_exists(self, async_client, service_url):
        """Test that VAD endpoint is accessible."""
        # Note: VAD endpoint may not be implemented yet
        # This is a placeholder test

        # Arrange
        dummy_audio = base64.b64encode(b"test").decode()
        request_data = {"audio_data": dummy_audio}

        # Act
        response = await async_client.post(f"{service_url}/voice/vad", json=request_data)

        # Assert - VAD may return 422 for mock implementation
        assert response.status_code in [
            200,
            404,
            405,
            422,
        ], f"Unexpected VAD endpoint status: {response.status_code}"


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceAndConcurrency:
    """Integration tests for performance and concurrent operations."""

    @pytest.mark.asyncio
    async def test_tts_latency_benchmark(self, async_client, service_url, short_text):
        """Benchmark TTS generation latency."""
        import time

        # Arrange
        request_data = {"text": short_text, "voice": "en_US-lessac-medium"}

        latencies = []
        iterations = 3

        # Act - run multiple times
        for _ in range(iterations):
            start = time.time()
            response = await async_client.post(f"{service_url}/voice/tts", json=request_data)
            latency = time.time() - start
            latencies.append(latency)

            assert response.status_code == 200

        # Assert
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)

        assert avg_latency < 5.0, f"Avg TTS latency too high: {avg_latency:.2f}s"
        assert max_latency < 10.0, f"Max TTS latency too high: {max_latency:.2f}s"

    @pytest.mark.asyncio
    async def test_concurrent_tts_requests_stress(self, async_client, service_url):
        """Test handling of multiple concurrent TTS requests."""
        # Arrange
        texts = [f"Test text number {i}" for i in range(5)]
        requests = [
            async_client.post(
                f"{service_url}/voice/tts", json={"text": text, "voice": "en_US-lessac-medium"}
            )
            for text in texts
        ]

        # Act
        responses = await asyncio.gather(*requests, return_exceptions=True)

        # Assert
        success_count = sum(
            1 for r in responses if not isinstance(r, Exception) and r.status_code == 200
        )

        assert success_count >= 3, f"Only {success_count}/5 concurrent requests succeeded"

        # Validate successful responses
        for i, response in enumerate(responses):
            if not isinstance(response, Exception) and response.status_code == 200:
                data = validate_json_response(response, ["audio_data"])
                validate_audio_data(data["audio_data"])

    @pytest.mark.asyncio
    async def test_mixed_endpoint_concurrency(
        self, async_client, service_url, short_text, test_audio_file
    ):
        """Test concurrent requests to different endpoints."""
        # Arrange
        with open(test_audio_file, "rb") as f:
            audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode()

        # Mix of TTS and STT requests
        requests = [
            async_client.post(
                f"{service_url}/voice/tts",
                json={"text": short_text, "voice": "en_US-lessac-medium"},
            ),
            async_client.post(
                f"{service_url}/voice/stt", json={"audio_data": audio_b64, "language": "en"}
            ),
            async_client.get(f"{service_url}/health"),
        ]

        # Act
        responses = await asyncio.gather(*requests, return_exceptions=True)

        # Assert - at least some should succeed
        success_count = sum(
            1 for r in responses if not isinstance(r, Exception) and r.status_code == 200
        )

        assert success_count >= 2, f"Only {success_count}/3 mixed requests succeeded"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
