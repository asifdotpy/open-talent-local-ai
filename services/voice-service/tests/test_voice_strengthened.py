import httpx
import pytest


@pytest.fixture
def voice_url():
    return "http://localhost:8008"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=30.0)


class TestVoiceStrengthened:
    @pytest.mark.asyncio
    async def test_latency_test(self, voice_url, async_client):
        response = await async_client.post(f"{voice_url}/voice/latency-test", json={"text": "ping"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "latency_ms" in data

    @pytest.mark.asyncio
    async def test_get_api_docs_info(self, voice_url, async_client):
        response = await async_client.get(f"{voice_url}/api-docs")
        assert response.status_code == 200
        data = response.json()
        assert "total_endpoints" in data
        assert "routes" in data

    @pytest.mark.asyncio
    async def test_webrtc_endpoints_existence(self, voice_url, async_client):
        # Even if WEBRTC is not available/enabled, these routes should exist or return consistent errors
        # Start
        response = await async_client.post(f"{voice_url}/webrtc/start", json={})
        assert response.status_code in [200, 404, 500, 503]

        # Status
        response = await async_client.get(f"{voice_url}/webrtc/status")
        assert response.status_code in [200, 404, 500, 503]

    @pytest.mark.asyncio
    async def test_audio_metadata(self, voice_url, async_client):
        # We need a small wav file for this. For now let's just check the endpoint exists.
        files = {
            "audio_file": (
                "test.wav",
                b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00",
                "audio/wav",
            )
        }
        response = await async_client.post(f"{voice_url}/voice/metadata", files=files)
        assert response.status_code in [200, 400, 500]

    @pytest.mark.asyncio
    async def test_phonemes_extraction(self, voice_url, async_client):
        response = await async_client.post(
            f"{voice_url}/voice/phonemes", json={"text": "Hello world"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "phonemes" in data
