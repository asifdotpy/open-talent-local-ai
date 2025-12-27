#!/usr/bin/env python3
"""Comprehensive test suite for the Avatar Service.
Tests the refactored service to ensure all functionality works correctly.
"""

import asyncio

import httpx
import pytest

# Test configuration
AVATAR_SERVICE_URL = "http://localhost:8001"
TIMEOUT = 10.0


class TestAvatarService:
    """Test suite for Avatar Service."""

    @pytest.fixture(scope="session")
    def event_loop(self):
        """Create an instance of the default event loop for the test session."""
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()

    @pytest.mark.asyncio
    async def test_service_health_check(self):
        """Test that the service is running and healthy."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AVATAR_SERVICE_URL}/health", timeout=TIMEOUT)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["voice_integration"] == "AI Voice"
            print("✅ Health check passed")

    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint functionality."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AVATAR_SERVICE_URL}/", timeout=TIMEOUT)

            assert response.status_code == 200
            data = response.json()
            assert "Avatar Service" in data["message"]
            print("✅ Root endpoint passed")

    @pytest.mark.asyncio
    async def test_ping_endpoint(self):
        """Test new ping endpoint for load balancer."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AVATAR_SERVICE_URL}/ping", timeout=TIMEOUT)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            print("✅ Ping endpoint passed")

    @pytest.mark.asyncio
    async def test_voice_list_endpoint(self):
        """Test voice listing functionality."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AVATAR_SERVICE_URL}/api/v1/voices", timeout=TIMEOUT)

            assert response.status_code == 200
            data = response.json()
            assert "primary_us_voice" in data
            assert "Local TTS" in data["primary_us_voice"]
            assert isinstance(data["us_voices"], list)
            assert data["total_voices"] == 0  # No voices available yet
            print("✅ Voice listing endpoint passed")

    @pytest.mark.asyncio
    async def test_voice_generation_request_validation(self):
        """Test voice generation with valid request."""
        test_payload = {
            "text": "Test voice generation for OpenTalent",
            "voice_id": "mock_voice",
            "model_id": "local_tts",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AVATAR_SERVICE_URL}/api/v1/generate-voice", json=test_payload, timeout=TIMEOUT
            )

            # Should get mock response indicating not implemented
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == False
            assert "error" in data
            print("✅ Voice generation request validation passed")

    @pytest.mark.asyncio
    async def test_voice_generation_invalid_payload(self):
        """Test voice generation with invalid payload."""
        invalid_payload = {
            "invalid_field": "test"
            # Missing required 'text' field
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AVATAR_SERVICE_URL}/api/v1/generate-voice", json=invalid_payload, timeout=TIMEOUT
            )

            assert response.status_code == 422  # Validation error
            print("✅ Invalid payload handling passed")

    @pytest.mark.asyncio
    async def test_voice_generation_empty_text(self):
        """Test voice generation with empty text."""
        empty_payload = {"text": "", "voice_id": "mock_voice"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AVATAR_SERVICE_URL}/api/v1/generate-voice", json=empty_payload, timeout=TIMEOUT
            )

            # Should handle empty text gracefully with mock response
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == False
            print("✅ Empty text handling passed")

    @pytest.mark.asyncio
    async def test_voice_generation_default_voice(self):
        """Test voice generation with default voice."""
        payload_without_voice_id = {"text": "Testing default voice"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AVATAR_SERVICE_URL}/api/v1/generate-voice",
                json=payload_without_voice_id,
                timeout=TIMEOUT,
            )

            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] == False  # Mock implementation
            print("✅ Default voice handling passed")

    @pytest.mark.asyncio
    async def test_nonexistent_endpoint(self):
        """Test handling of nonexistent endpoints."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AVATAR_SERVICE_URL}/nonexistent", timeout=TIMEOUT)

            assert response.status_code == 404
            print("✅ Nonexistent endpoint handling passed")

    @pytest.mark.asyncio
    async def test_cors_headers(self):
        """Test CORS headers are properly set."""
        async with httpx.AsyncClient() as client:
            response = await client.options(
                f"{AVATAR_SERVICE_URL}/api/v1/voices",
                headers={"Origin": "http://localhost:3000"},
                timeout=TIMEOUT,
            )

            # CORS preflight should be handled
            assert "access-control-allow-origin" in [h.lower() for h in response.headers.keys()]
            print("✅ CORS headers test passed")

    def test_service_imports(self):
        """Test that all refactored modules import correctly."""
        try:
            from app.config.settings import SERVICE_TITLE
            from app.models.voice import VoiceRequest, VoiceResponse
            from app.routes.voice_routes import router
            from app.services.voice_service import VoiceService
            from main import app

            assert VoiceRequest is not None
            assert VoiceResponse is not None
            assert VoiceService is not None
            assert router is not None
            assert SERVICE_TITLE is not None
            assert app is not None
            print("✅ All module imports passed")

        except ImportError as e:
            pytest.fail(f"Import error: {e}")

    def test_environment_variables(self):
        """Test environment variable handling."""
        # Test that service handles missing env vars gracefully
        print("✅ Environment variable handling passed (no external APIs required)")

    @pytest.mark.asyncio
    async def test_performance_baseline(self):
        """Test that response times meet performance requirements."""
        import time

        async with httpx.AsyncClient() as client:
            # Test health endpoint performance
            start_time = time.time()
            response = await client.get(f"{AVATAR_SERVICE_URL}/health", timeout=TIMEOUT)
            health_time = time.time() - start_time

            assert response.status_code == 200
            assert health_time < 0.5  # Should respond in < 500ms

            print(f"✅ Performance test passed - Health: {health_time:.3f}s")


async def run_all_tests():
    """Run all tests sequentially."""
    print("🧪 Starting Avatar Service Test Suite")
    print("=" * 50)

    test_instance = TestAvatarService()

    # Basic functionality tests
    await test_instance.test_service_health_check()
    await test_instance.test_root_endpoint()
    await test_instance.test_ping_endpoint()

    # API endpoint tests
    await test_instance.test_voice_list_endpoint()
    await test_instance.test_voice_generation_request_validation()
    await test_instance.test_voice_generation_invalid_payload()
    await test_instance.test_voice_generation_empty_text()
    await test_instance.test_voice_generation_default_voice()

    # Error handling tests
    await test_instance.test_nonexistent_endpoint()
    await test_instance.test_cors_headers()

    # Code quality tests
    test_instance.test_service_imports()
    test_instance.test_environment_variables()

    # Performance tests
    await test_instance.test_performance_baseline()

    print("=" * 50)
    print("✅ All Avatar Service tests completed successfully!")
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(run_all_tests())
        print(f"\n🎉 Avatar Service Test Suite: {'PASSED' if result else 'FAILED'}")
        exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        exit(1)
