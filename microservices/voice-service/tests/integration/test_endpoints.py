from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# Test the root endpoint
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Voice Service is running!"}


# Test the health check endpoint
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# Test the STT endpoint with invalid file type
def test_stt_invalid_file():
    response = client.post(
        "/voice/stt", files={"audio_file": ("test.txt", b"dummy content", "text/plain")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid audio file type."


# Test the TTS endpoint with empty text
def test_tts_empty_text():
    response = client.post("/voice/tts", json={"text": ""})
    assert response.status_code == 500
    assert response.json()["detail"] == "TTS synthesis failed."
