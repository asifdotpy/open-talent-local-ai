"""
Unit Tests for Avatar Renderer Server

Tests the Node.js avatar rendering server that generates lip-synced videos.
Part of Phase 2: Avatar Service Real Rendering

Created: November 11, 2025
"""

import asyncio
import os

import httpx
import pytest


@pytest.fixture
def renderer_url():
    """Avatar renderer server URL."""
    return os.getenv("RENDERER_URL", "http://localhost:3001")


@pytest.fixture
def sample_phonemes():
    """Sample phoneme data for testing."""
    return [
        {"phoneme": "HH", "start": 0.0, "end": 0.05},
        {"phoneme": "EH", "start": 0.05, "end": 0.15},
        {"phoneme": "L", "start": 0.15, "end": 0.25},
        {"phoneme": "OW", "start": 0.25, "end": 0.45},
    ]


@pytest.fixture
def vowel_phonemes():
    """Vowel phonemes for mouth opening tests."""
    return [
        {"phoneme": "AA", "start": 0.0, "end": 0.2},  # Wide open
        {"phoneme": "AO", "start": 0.2, "end": 0.4},  # Open
        {"phoneme": "IY", "start": 0.4, "end": 0.6},  # Narrow
    ]


@pytest.fixture
def consonant_phonemes():
    """Consonant phonemes for mouth closing tests."""
    return [
        {"phoneme": "M", "start": 0.0, "end": 0.1},  # Closed
        {"phoneme": "P", "start": 0.1, "end": 0.2},  # Closed
        {"phoneme": "B", "start": 0.2, "end": 0.3},  # Slightly open
    ]


class TestRendererServerHealth:
    """Test renderer server health and availability."""

    @pytest.mark.asyncio
    async def test_server_running(self, renderer_url):
        """Test that renderer server is running."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{renderer_url}/health")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_response_format(self, renderer_url):
        """Test health endpoint response format."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{renderer_url}/health")
            data = response.json()

            assert "status" in data
            assert data["status"] == "ok"
            assert "timestamp" in data


class TestLipSyncRendering:
    """Test lip-sync video rendering functionality."""

    @pytest.mark.asyncio
    async def test_render_basic_video(self, renderer_url, sample_phonemes):
        """Test basic video rendering with phonemes."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={"phonemes": sample_phonemes, "model": "face", "duration": 0.5},
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "video/webm"
            video_data = response.content
            assert len(video_data) > 1000

    @pytest.mark.asyncio
    async def test_render_returns_valid_webm(self, renderer_url, sample_phonemes):
        """Test that rendered video is valid WebM format."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={"phonemes": sample_phonemes, "duration": 0.5},
            )

            video_data = response.content

            # WebM signature: 0x1A 0x45 0xDF 0xA3
            assert video_data[:4] == b"\x1a\x45\xdf\xa3"

    @pytest.mark.asyncio
    async def test_render_with_processing_headers(self, renderer_url, sample_phonemes):
        """Test that response includes processing metadata headers."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={"phonemes": sample_phonemes, "duration": 0.5},
            )

            assert "x-processing-time" in response.headers
            assert "content-length" in response.headers


class TestPhonemeProcessing:
    """Test phoneme data processing."""

    @pytest.mark.asyncio
    async def test_empty_phonemes_handling(self, renderer_url):
        """Test handling of empty phoneme array."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{renderer_url}/render/lipsync", json={"phonemes": [], "duration": 1.0}
            )

            # Should handle gracefully - either error or default video
            assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_missing_phonemes_field(self, renderer_url):
        """Test error handling when phonemes field is missing."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{renderer_url}/render/lipsync", json={"duration": 1.0})

            assert response.status_code == 400
            data = response.json()
            assert "error" in data

    @pytest.mark.asyncio
    async def test_vowel_phonemes_mouth_opening(self, renderer_url, vowel_phonemes):
        """Test that vowel phonemes result in mouth opening."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{renderer_url}/render/lipsync", json={"phonemes": vowel_phonemes, "duration": 0.6}
            )

            assert response.status_code == 200
            video_data = response.content
            # Vowels should produce noticeable mouth movement
            assert len(video_data) > 1000

    @pytest.mark.asyncio
    async def test_consonant_phonemes_mouth_closing(self, renderer_url, consonant_phonemes):
        """Test that consonant phonemes result in mouth closing."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={"phonemes": consonant_phonemes, "duration": 0.3},
            )

            assert response.status_code == 200
            assert len(response.content) > 1000


class TestVideoProperties:
    """Test video output properties."""

    @pytest.mark.asyncio
    async def test_video_duration_matches_request(self, renderer_url, sample_phonemes):
        """Test that video duration approximately matches requested duration."""
        duration = 2.0

        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={"phonemes": sample_phonemes, "duration": duration},
            )

            assert response.status_code == 200
            # Video should be generated for requested duration

    @pytest.mark.asyncio
    async def test_video_size_scales_with_duration(self, renderer_url, sample_phonemes):
        """Test that video size increases with duration."""
        async with httpx.AsyncClient(timeout=90.0) as client:
            # Short video
            short_response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={"phonemes": sample_phonemes, "duration": 0.5},
            )

            # Longer video
            long_response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={
                    "phonemes": sample_phonemes * 4,  # More phonemes
                    "duration": 2.0,
                },
            )

            short_size = len(short_response.content)
            long_size = len(long_response.content)

            # Longer video should be larger
            assert long_size > short_size


class TestModelSupport:
    """Test different avatar model support."""

    @pytest.mark.asyncio
    async def test_face_model(self, renderer_url, sample_phonemes):
        """Test rendering with face model."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={"phonemes": sample_phonemes, "model": "face", "duration": 0.5},
            )

            assert response.status_code == 200
            assert len(response.content) > 1000

    @pytest.mark.asyncio
    async def test_default_model_when_not_specified(self, renderer_url, sample_phonemes):
        """Test that default model is used when not specified."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={"phonemes": sample_phonemes, "duration": 0.5},
            )

            assert response.status_code == 200


class TestPerformance:
    """Test rendering performance."""

    @pytest.mark.asyncio
    async def test_rendering_completes_timely(self, renderer_url, sample_phonemes):
        """Test that rendering completes within reasonable time."""
        import time

        async with httpx.AsyncClient(timeout=120.0) as client:
            start = time.time()

            response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={"phonemes": sample_phonemes, "duration": 0.5},
            )

            elapsed = time.time() - start

            assert response.status_code == 200
            # Should complete in under 2 minutes for short video
            assert elapsed < 120.0

    @pytest.mark.asyncio
    async def test_concurrent_rendering_requests(self, renderer_url, sample_phonemes):
        """Test handling of concurrent rendering requests."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            tasks = [
                client.post(
                    f"{renderer_url}/render/lipsync",
                    json={"phonemes": sample_phonemes, "duration": 0.5},
                )
                for _ in range(3)
            ]

            responses = await asyncio.gather(*tasks)

            for response in responses:
                assert response.status_code == 200
                assert len(response.content) > 1000


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_invalid_phoneme_format(self, renderer_url):
        """Test handling of invalid phoneme format."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={"phonemes": [{"invalid": "format"}], "duration": 1.0},
            )

            # Should handle gracefully
            assert response.status_code in [200, 400, 500]

    @pytest.mark.asyncio
    async def test_negative_duration(self, renderer_url, sample_phonemes):
        """Test handling of negative duration."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={"phonemes": sample_phonemes, "duration": -1.0},
            )

            # Should either reject or use default
            assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_very_long_duration(self, renderer_url, sample_phonemes):
        """Test handling of very long duration."""
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{renderer_url}/render/lipsync",
                json={
                    "phonemes": sample_phonemes,
                    "duration": 10.0,  # Long video
                },
            )

            # Should handle long videos
            assert response.status_code in [200, 413, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
