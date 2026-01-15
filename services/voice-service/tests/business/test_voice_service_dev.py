def test_basic_functionality(client):
    """Test just the core functionality."""
    # Health check
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    # TTS check
    payload = {"text": "Test", "voice": "en_US-lessac-medium"}
    response = client.post("/voice/tts", json=payload)
    assert response.status_code == 200
    assert "audio_data" in response.json()


def test_voices_list(client):
    """Test voices list."""
    response = client.get("/voices")
    assert response.status_code == 200
    assert "voices" in response.json()


def test_service_info_dev(client):
    """Test service info."""
    response = client.get("/info")
    assert response.status_code == 200
    assert "stt" in response.json()
