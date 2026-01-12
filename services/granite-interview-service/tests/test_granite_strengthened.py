import httpx
import pytest


@pytest.fixture
def granite_url():
    return "http://localhost:8005"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=30.0)


class TestGraniteStrengthened:
    @pytest.mark.asyncio
    async def test_get_gpu_status(self, granite_url, async_client):
        response = await async_client.get(f"{granite_url}/api/v1/system/gpu")
        assert response.status_code == 200
        data = response.json()
        assert "cuda_available" in data

    @pytest.mark.asyncio
    async def test_get_model_status(self, granite_url, async_client):
        # Check status of the default loaded model
        response = await async_client.get(f"{granite_url}/api/v1/models/granite4:350m-h/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["loaded", "not_loaded"]

    @pytest.mark.asyncio
    async def test_model_load_unload_cycle(self, granite_url, async_client):
        # We won't actually trigger a heavy load/unload of the 5.5GB model to avoid instability,
        # but we can test the endpoint validation and status checks.

        # Test loading a non-existent model (should fail or return 404/400)
        response = await async_client.post(
            f"{granite_url}/api/v1/models/load",
            json={"model_name": "non_existent_model", "quantization": "4bit"},
        )
        assert response.status_code in [400, 404, 500]

    @pytest.mark.asyncio
    async def test_training_endpoints(self, granite_url, async_client):
        # Test starting a fine-tuning job (mock logic)
        response = await async_client.post(
            f"{granite_url}/api/v1/training/fine-tune",
            json={
                "base_model": "granite4:350m-h",
                "training_data": "test_dataset",
                "config": {"epochs": 1, "learning_rate": 0.0001, "output_dir": "./models/test_ft"},
            },
        )
        if response.status_code != 200:
            pass
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        job_id = data["job_id"]

        # Test getting job status
        status_response = await async_client.get(f"{granite_url}/api/v1/training/jobs/{job_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "status" in status_data

        # Test cancelling job
        cancel_response = await async_client.delete(f"{granite_url}/api/v1/training/jobs/{job_id}")
        assert cancel_response.status_code == 200
        assert "cancelled" in cancel_response.json()["message"]
