

# Test the root endpoint
def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "Voice Service"
    assert response.json()["status"] == "running"


# Test the health check endpoint
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# Test the STT endpoint with invalid file type
def test_stt_invalid_file(client):
    response = client.post(
        "/voice/stt", files={"audio_file": ("test.txt", b"dummy content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid audio file type" in response.json()["detail"]


# Test the TTS endpoint with empty text
def test_tts_empty_text(client):
    response = client.post("/voice/tts", json={"text": ""})
    assert response.status_code == 400
    assert "Text cannot be empty" in response.json()["detail"]
