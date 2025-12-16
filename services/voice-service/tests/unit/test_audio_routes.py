import os
import io
import sys
import types
import importlib.util
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure mocks before importing app
os.environ.setdefault("USE_MOCK_SERVICES", "true")
os.environ.setdefault("RATE_LIMIT_BURST", "100")  # avoid flakiness in tests
os.environ.setdefault("RATE_LIMIT_RATE", "100")
os.environ.setdefault("MAX_AUDIO_DURATION_MS", str(60_000))

ROOT = Path(__file__).resolve().parents[2]
main_path = ROOT / "main.py"

# Load main.py as submodule voice_service.main, with package context voice_service
spec = importlib.util.spec_from_file_location(
    "voice_service.main",
    main_path,
    submodule_search_locations=[str(ROOT)],
)
voice_pkg = types.ModuleType("voice_service")
voice_pkg.__path__ = [str(ROOT)]  # allow voice_service.* imports
sys.modules.setdefault("voice_service", voice_pkg)
module = importlib.util.module_from_spec(spec)
module.__package__ = "voice_service"
sys.modules["voice_service.main"] = module
spec.loader.exec_module(module)

app = module.app  # noqa: E402
client = TestClient(app)


def make_wav_bytes(duration_ms=200, freq=440, sample_rate=16000):
    import numpy as np
    import wave

    t = np.linspace(0, duration_ms / 1000.0, int(sample_rate * duration_ms / 1000.0), False)
    audio = (0.3 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        # convert to int16
        audio_int16 = (audio * 32767).astype(np.int16)
        wav_file.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return buf


def test_normalize():
    wav = make_wav_bytes()
    files = {"audio_file": ("test.wav", wav, "audio/wav")}
    resp = client.post("/voice/normalize", files=files)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("audio/")


def test_format():
    wav = make_wav_bytes()
    files = {"audio_file": ("test.wav", wav, "audio/wav")}
    resp = client.post("/voice/format?target_format=wav", files=files)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("audio/")


def test_split():
    wav = make_wav_bytes()
    files = {"audio_file": ("test.wav", wav, "audio/wav")}
    resp = client.post("/voice/split", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "segments" in data


def test_join():
    wav1 = make_wav_bytes()
    wav2 = make_wav_bytes()
    files = [
        ("files", ("a.wav", wav1, "audio/wav")),
        ("files", ("b.wav", wav2, "audio/wav")),
    ]
    resp = client.post("/voice/join", files=files)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("audio/")


def test_trim():
    wav = make_wav_bytes()
    files = {"audio_file": ("test.wav", wav, "audio/wav")}
    resp = client.post("/voice/trim?start_ms=0&end_ms=100", files=files)
    assert resp.status_code == 200


def test_resample():
    wav = make_wav_bytes()
    files = {"audio_file": ("test.wav", wav, "audio/wav")}
    resp = client.post("/voice/resample?target_sample_rate=8000", files=files)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("audio/")


def test_metadata():
    wav = make_wav_bytes()
    files = {"audio_file": ("test.wav", wav, "audio/wav")}
    resp = client.post("/voice/metadata", files=files)
    assert resp.status_code == 200
    data = resp.json()["metadata"]
    assert data["duration_ms"] > 0
    assert data["channels"] == 1


def test_channels():
    wav = make_wav_bytes()
    files = {"audio_file": ("test.wav", wav, "audio/wav")}
    resp = client.post("/voice/channels?target_channels=1", files=files)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("audio/")


def test_phonemes():
    resp = client.post("/voice/phonemes", json={"text": "Hello", "duration": 0.5})
    assert resp.status_code == 200
    data = resp.json()
    assert "phonemes" in data


def test_batch_tts():
    payload = {"requests": [{"text": "Hi", "voice": "lessac", "speed": 1.0, "extract_phonemes": False}, {"text": "Bye", "voice": "lessac", "speed": 1.0, "extract_phonemes": False}]}
    resp = client.post("/voice/batch-tts", json=payload["requests"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 2
    assert len(data["results"]) == 2