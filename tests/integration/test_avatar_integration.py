"""
Integration Tests for Avatar Service with Voice Service Integration

Tests the complete pipeline:
1. Phase 1: Voice Service Phoneme Extraction
2. Phase 2: Avatar Service Real Rendering
3. End-to-end text-to-video generation

Created: November 11, 2025
Last Updated: November 11, 2025
"""

import pytest
import httpx
import asyncio
import base64
import os
from pathlib import Path
from typing import Dict, Any


@pytest.fixture
def voice_service_url():
    """Voice service endpoint."""
    return os.getenv("VOICE_SERVICE_URL", "http://localhost:8002")


@pytest.fixture
def avatar_service_url():
    """Avatar service endpoint."""
    return os.getenv("AVATAR_SERVICE_URL", "http://localhost:8001")


@pytest.fixture
def renderer_service_url():
    """Avatar renderer endpoint."""
    return os.getenv("RENDERER_SERVICE_URL", "http://localhost:3001")


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "Hello, I am your AI interviewer. Let us begin the interview."


@pytest.fixture
def short_text():
    """Short text for quick tests."""
    return "Hello world"


class TestPhase1VoiceServicePhonemeExtraction:
    """Test Phase 1: Voice Service Phoneme Extraction implementation."""

    @pytest.mark.asyncio
    async def test_voice_service_health(self, voice_service_url):
        """Test that voice service is running and healthy."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{voice_service_url}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["healthy", "degraded"]
            assert "services" in data
            assert "tts" in data["services"]

    @pytest.mark.asyncio
    async def test_phoneme_extraction_endpoint(self, voice_service_url, sample_text):
        """Test that TTS endpoint returns phonemes when requested."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{voice_service_url}/voice/tts",
                json={
                    "text": sample_text,
                    "voice": "en_US-lessac-medium",
                    "extract_phonemes": True
                }
            )
            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "audio_data" in data
            assert "phonemes" in data
            assert "duration" in data
            assert isinstance(data["phonemes"], list)
            assert len(data["phonemes"]) > 0

            # Verify duration is at least 2 seconds (mock generates 0.5s per word, min 2s)
            duration = data["duration"]
            assert duration >= 2.0, f"Duration {duration} should be at least 2 seconds"

    @pytest.mark.asyncio
    async def test_phoneme_data_structure(self, voice_service_url, short_text):
        """Test that phoneme data has correct structure."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{voice_service_url}/voice/tts",
                json={
                    "text": short_text,
                    "voice": "en_US-lessac-medium",
                    "extract_phonemes": True
                }
            )
            data = response.json()
            phonemes = data["phonemes"]

            # Verify each phoneme has required fields
            for phoneme in phonemes:
                assert "phoneme" in phoneme
                assert "start" in phoneme
                assert "end" in phoneme
                assert isinstance(phoneme["phoneme"], str)
                assert isinstance(phoneme["start"], (int, float))
                assert isinstance(phoneme["end"], (int, float))
                assert phoneme["end"] > phoneme["start"]

    @pytest.mark.asyncio
    async def test_phoneme_timing_accuracy(self, voice_service_url, short_text):
        """Test that phoneme timings are accurate relative to audio duration."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{voice_service_url}/voice/tts",
                json={
                    "text": short_text,
                    "voice": "en_US-lessac-medium",
                    "extract_phonemes": True
                }
            )
            data = response.json()
            phonemes = data["phonemes"]
            duration = data["duration"]

            # Last phoneme should end at or before duration
            last_phoneme = max(phonemes, key=lambda p: p["end"])
            assert last_phoneme["end"] <= duration * 1.1  # Allow 10% tolerance

    @pytest.mark.asyncio
    async def test_audio_data_base64_encoding(self, voice_service_url, short_text):
        """Test that audio data is properly base64 encoded."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{voice_service_url}/voice/tts",
                json={
                    "text": short_text,
                    "voice": "en_US-lessac-medium",
                    "extract_phonemes": True
                }
            )
            data = response.json()
            audio_data = data["audio_data"]

            # Should be able to decode base64
            try:
                decoded = base64.b64decode(audio_data)
                assert len(decoded) > 0
            except Exception as e:
                pytest.fail(f"Failed to decode base64 audio data: {e}")


class TestPhase2AvatarServiceRealRendering:
    """Test Phase 2: Avatar Service Real Rendering implementation."""

    @pytest.mark.asyncio
    async def test_avatar_service_health(self, avatar_service_url):
        """Test that avatar service is running and healthy."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{avatar_service_url}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            # Check for either 'components' or 'component' field
            assert "components" in data or "component" in data

    @pytest.mark.asyncio
    async def test_renderer_service_health(self, renderer_service_url):
        """Test that avatar renderer is running."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{renderer_service_url}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_avatar_video_generation(self, avatar_service_url, short_text):
        """Test basic avatar video generation."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{avatar_service_url}/generate",
                json={
                    "text": short_text,
                    "voice": "en_US-lessac-medium",
                    "avatar_id": "face"
                }
            )
            assert response.status_code == 200
            assert response.headers["content-type"] == "video/webm"
            video_data = response.content
            assert len(video_data) > 1000  # Should be at least 1KB

    @pytest.mark.asyncio
    async def test_avatar_video_is_valid_webm(self, avatar_service_url, short_text):
        """Test that generated video is valid WebM format."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{avatar_service_url}/generate",
                json={
                    "text": short_text,
                    "voice": "en_US-lessac-medium"
                }
            )
            video_data = response.content

            # Check WebM signature (first 4 bytes should be 0x1A 0x45 0xDF 0xA3)
            assert video_data[:4] == b'\x1a\x45\xdf\xa3'

    @pytest.mark.asyncio
    async def test_renderer_lipsync_endpoint(self, renderer_service_url):
        """Test that renderer accepts phoneme data."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{renderer_service_url}/render/lipsync",
                json={
                    "phonemes": [
                        {"phoneme": "HH", "start": 0.0, "end": 0.1},
                        {"phoneme": "EH", "start": 0.1, "end": 0.2},
                        {"phoneme": "L", "start": 0.2, "end": 0.3},
                        {"phoneme": "OW", "start": 0.3, "end": 0.5}
                    ],
                    "model": "face",
                    "duration": 0.5
                }
            )
            assert response.status_code == 200
            assert response.headers["content-type"] == "video/webm"
            video_data = response.content
            assert len(video_data) > 1000

    @pytest.mark.asyncio
    async def test_avatar_info_endpoint(self, avatar_service_url):
        """Test avatar info endpoint returns correct configuration."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{avatar_service_url}/info")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert "info" in data
            info = data["info"]
            assert "renderer_url" in info
            assert "rendering_engine" in info
            assert "supported_models" in info


class TestEndToEndIntegration:
    """Test complete end-to-end pipeline."""

    @pytest.mark.asyncio
    async def test_complete_text_to_video_pipeline(
        self, voice_service_url, avatar_service_url, sample_text
    ):
        """Test complete pipeline from text to avatar video."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Step 1: Generate avatar video (internally calls voice service)
            response = await client.post(
                f"{avatar_service_url}/generate",
                json={
                    "text": sample_text,
                    "voice": "en_US-lessac-medium",
                    "avatar_id": "face"
                }
            )

            assert response.status_code == 200
            video_data = response.content

            # Verify we got a valid video
            assert len(video_data) > 5000  # Should be substantial
            assert video_data[:4] == b'\x1a\x45\xdf\xa3'  # WebM signature

    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self, avatar_service_url):
        """Test that service handles multiple concurrent requests."""
        async with httpx.AsyncClient(timeout=180.0) as client:
            texts = [
                "Hello world",
                "Welcome to the interview",
                "Tell me about yourself"
            ]

            tasks = [
                client.post(
                    f"{avatar_service_url}/generate",
                    json={"text": text, "voice": "en_US-lessac-medium"}
                )
                for text in texts
            ]

            responses = await asyncio.gather(*tasks)

            for response in responses:
                assert response.status_code == 200
                assert len(response.content) > 1000

    @pytest.mark.asyncio
    async def test_different_voice_models(self, avatar_service_url, short_text):
        """Test video generation with different voice models."""
        voices = [
            "en_US-lessac-medium",
            "en_US-amy-medium",
            "en_US-ryan-high"
        ]

        async with httpx.AsyncClient(timeout=120.0) as client:
            for voice in voices:
                response = await client.post(
                    f"{avatar_service_url}/generate",
                    json={
                        "text": short_text,
                        "voice": voice,
                        "avatar_id": "face"
                    }
                )
                assert response.status_code == 200
                assert len(response.content) > 1000

    @pytest.mark.asyncio
    async def test_phoneme_to_video_consistency(
        self, voice_service_url, renderer_service_url, short_text
    ):
        """Test that phonemes from voice service work with renderer."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Get phonemes from voice service
            voice_response = await client.post(
                f"{voice_service_url}/voice/tts",
                json={
                    "text": short_text,
                    "voice": "en_US-lessac-medium",
                    "extract_phonemes": True
                }
            )
            voice_data = voice_response.json()

            # Send phonemes to renderer
            render_response = await client.post(
                f"{renderer_service_url}/render/lipsync",
                json={
                    "phonemes": voice_data["phonemes"],
                    "model": "face",
                    "duration": voice_data["duration"]
                }
            )

            assert render_response.status_code == 200
            video_data = render_response.content
            assert len(video_data) > 1000


class TestPerformanceAndReliability:
    """Test performance and reliability requirements."""

    @pytest.mark.asyncio
    async def test_video_generation_latency(self, avatar_service_url, short_text):
        """Test that video generation completes within reasonable time."""
        import time

        async with httpx.AsyncClient(timeout=120.0) as client:
            start_time = time.time()

            response = await client.post(
                f"{avatar_service_url}/generate",
                json={
                    "text": short_text,
                    "voice": "en_US-lessac-medium"
                }
            )

            latency = time.time() - start_time

            assert response.status_code == 200
            # Should complete in under 2 minutes for short text
            assert latency < 120.0

    @pytest.mark.asyncio
    async def test_service_error_handling(self, avatar_service_url):
        """Test that service handles errors gracefully."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test with missing required field
            response = await client.post(
                f"{avatar_service_url}/generate",
                json={"voice": "en_US-lessac-medium"}  # Missing 'text'
            )
            assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_empty_text_handling(self, avatar_service_url):
        """Test handling of empty text input."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{avatar_service_url}/generate",
                json={
                    "text": "",
                    "voice": "en_US-lessac-medium"
                }
            )
            # Should either reject or handle gracefully
            assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_long_text_handling(self, avatar_service_url):
        """Test handling of longer text inputs."""
        long_text = " ".join([
            "Hello, I am your AI interviewer.",
            "Today we will discuss your experience and qualifications.",
            "Please take your time to answer each question thoroughly.",
            "Let us begin with your background and experience."
        ])

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{avatar_service_url}/generate",
                json={
                    "text": long_text,
                    "voice": "en_US-lessac-medium"
                }
            )
            assert response.status_code == 200
            assert len(response.content) > 10000  # Longer video


class TestPhonemeAccuracy:
    """Test phoneme extraction accuracy and quality."""

    @pytest.mark.asyncio
    async def test_common_phonemes_extracted(self, voice_service_url):
        """Test that common phonemes are properly extracted."""
        test_cases = {
            "Hello": ["HH", "EH", "L", "OW"],
            "World": ["W", "ER", "L", "D"],
            "Interview": ["IH", "N", "T", "ER", "V", "Y", "UW"]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            for text, expected_phonemes in test_cases.items():
                response = await client.post(
                    f"{voice_service_url}/voice/tts",
                    json={
                        "text": text,
                        "voice": "en_US-lessac-medium",
                        "extract_phonemes": True
                    }
                )
                data = response.json()
                extracted = [p["phoneme"] for p in data["phonemes"]]

                # Check that at least some expected phonemes are present
                found = sum(1 for ep in expected_phonemes if ep in extracted)
                assert found >= len(expected_phonemes) * 0.5  # At least 50% match

    @pytest.mark.asyncio
    async def test_phoneme_count_reasonable(self, voice_service_url, sample_text):
        """Test that phoneme count is reasonable for given text."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{voice_service_url}/voice/tts",
                json={
                    "text": sample_text,
                    "voice": "en_US-lessac-medium",
                    "extract_phonemes": True
                }
            )
            data = response.json()
            phonemes = data["phonemes"]

            # Rough estimate: 2-5 phonemes per word
            word_count = len(sample_text.split())
            min_expected = word_count * 2
            max_expected = word_count * 5

            assert min_expected <= len(phonemes) <= max_expected


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
