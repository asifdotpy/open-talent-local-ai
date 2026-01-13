"""
Shared pytest fixtures for voice service tests.

This module provides reusable test fixtures for all voice service tests,
following TDD best practices and DRY principles.
"""

import asyncio
import base64
import os
import struct
import tempfile
import wave
from pathlib import Path
from typing import AsyncGenerator, Generator

import httpx
import pytest
import pytest_asyncio


# ============================================================================
# Service Configuration Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def service_url() -> str:
    """Get the voice service URL from environment or default."""
    return os.getenv("VOICE_SERVICE_URL", "http://localhost:8002")


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an async HTTP client for integration tests."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================


@pytest.fixture
def test_audio_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test audio files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_text() -> str:
    """Standard sample text for TTS testing."""
    return "Hello, this is a test of the voice service."


@pytest.fixture
def short_text() -> str:
    """Short text for quick tests."""
    return "Hello world"


@pytest.fixture
def empty_text() -> str:
    """Empty text for edge case testing."""
    return ""


@pytest.fixture
def long_text() -> str:
    """Long text for stress testing."""
    return " ".join(
        [
            "The quick brown fox jumps over the lazy dog.",
            "This is a longer text sample designed to test the voice service",
            "with multiple sentences and various phonetic patterns.",
            "It includes numbers like 123 and punctuation marks!",
        ]
    )


@pytest.fixture
def special_characters_text() -> str:
    """Text with special characters for edge case testing."""
    return "Hello! How are you? I'm fine, thank you. Let's test: 1, 2, 3."


def create_test_wav_file(
    filepath: str,
    duration: float = 1.0,
    frequency: int = 440,
    sample_rate: int = 16000,
    channels: int = 1,
) -> str:
    """
    Create a test WAV file with sine wave audio.

    Args:
        filepath: Path to output WAV file
        duration: Duration in seconds
        frequency: Tone frequency in Hz
        sample_rate: Audio sample rate
        channels: Number of audio channels (1=mono, 2=stereo)

    Returns:
        Path to created WAV file
    """
    import math

    num_samples = int(duration * sample_rate)

    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)  # 16-bit audio
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            # Generate sine wave
            value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            data = struct.pack("<h", value)

            # Write for each channel
            for _ in range(channels):
                wav_file.writeframes(data)

    return filepath


@pytest.fixture
def test_audio_file(test_audio_dir) -> str:
    """Create a test WAV file with 1 second of 440Hz tone."""
    filepath = str(test_audio_dir / "test_audio.wav")
    return create_test_wav_file(filepath, duration=1.0, frequency=440)


@pytest.fixture
def short_audio_file(test_audio_dir) -> str:
    """Create a short test WAV file (0.5 seconds)."""
    filepath = str(test_audio_dir / "short_audio.wav")
    return create_test_wav_file(filepath, duration=0.5, frequency=440)


@pytest.fixture
def long_audio_file(test_audio_dir) -> str:
    """Create a long test WAV file (5 seconds)."""
    filepath = str(test_audio_dir / "long_audio.wav")
    return create_test_wav_file(filepath, duration=5.0, frequency=440)


@pytest.fixture
def silent_audio_file(test_audio_dir) -> str:
    """Create a silent audio file (1 second of silence)."""
    filepath = str(test_audio_dir / "silent_audio.wav")

    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)

        # Write 1 second of silence
        for _ in range(16000):
            wav_file.writeframes(struct.pack("<h", 0))

    return filepath


@pytest.fixture
def invalid_audio_file(test_audio_dir) -> str:
    """Create an invalid audio file (not a WAV)."""
    filepath = str(test_audio_dir / "invalid.wav")
    with open(filepath, "w") as f:
        f.write("This is not a valid WAV file")
    return filepath


@pytest.fixture
def audio_data_base64(test_audio_file) -> str:
    """Read test audio file and return as base64 string."""
    with open(test_audio_file, "rb") as f:
        audio_bytes = f.read()
    return base64.b64encode(audio_bytes).decode("utf-8")


@pytest.fixture
def empty_audio_data() -> str:
    """Empty audio data for edge case testing."""
    return ""


@pytest.fixture
def invalid_base64() -> str:
    """Invalid base64 string for error testing."""
    return "not-valid-base64!@#$"


@pytest.fixture
def service_url() -> str:
    """Voice service base URL for integration tests."""
    return "http://localhost:8002"


@pytest.fixture
def available_voices() -> list:
    """List of available TTS voices for testing."""
    return ["en_US-lessac-medium", "en_US-amy-medium", "en_US-ryan-high", "en_US-hfc_female-medium"]


@pytest.fixture
def tts_request_basic(short_text, available_voices) -> dict:
    """Basic TTS request payload."""
    return {"text": short_text, "voice": available_voices[0]}


@pytest.fixture
def tts_request_with_phonemes(sample_text, available_voices) -> dict:
    """TTS request with phoneme extraction enabled."""
    return {"text": sample_text, "voice": available_voices[0], "extract_phonemes": True}


@pytest.fixture
def stt_request(audio_data_base64) -> dict:
    """Basic STT request payload."""
    return {"audio_data": audio_data_base64}


@pytest.fixture
def mock_piper_path(tmp_path) -> str:
    """Create a mock piper executable path."""
    piper_path = tmp_path / "piper"
    piper_path.write_text("#!/bin/bash\necho 'mock piper'")
    piper_path.chmod(0o755)
    return str(piper_path)


@pytest.fixture
def mock_model_path(tmp_path) -> str:
    """Create a mock model file path."""
    model_path = tmp_path / "en_US-lessac-medium.onnx"
    model_path.write_bytes(b"mock model data")

    # Create accompanying .json config
    json_path = tmp_path / "en_US-lessac-medium.onnx.json"
    json_path.write_text('{"sample_rate": 16000}')

    return str(model_path)


class AudioFileFactory:
    """Factory for creating test audio files with various properties."""

    @staticmethod
    def create_wav(
        output_path: str,
        duration: float = 1.0,
        sample_rate: int = 16000,
        channels: int = 1,
        frequency: int = 440,
    ) -> str:
        """Create WAV file with specified parameters."""
        return create_test_wav_file(
            output_path,
            duration=duration,
            frequency=frequency,
            sample_rate=sample_rate,
            channels=channels,
        )

    @staticmethod
    def create_corrupt_wav(output_path: str) -> str:
        """Create a corrupted WAV file."""
        with open(output_path, "wb") as f:
            # Write invalid WAV header
            f.write(b"INVALID")
        return output_path

    @staticmethod
    def create_empty_wav(output_path: str) -> str:
        """Create an empty WAV file."""
        open(output_path, "w").close()
        return output_path


@pytest.fixture
def audio_factory() -> AudioFileFactory:
    """Audio file factory for tests."""
    return AudioFileFactory()


# Markers for test categorization
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components (fast, isolated, 90%+ coverage)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests requiring running services (80%+ coverage)"
    )
    config.addinivalue_line(
        "markers", "business: Business value tests validating user outcomes (100% critical paths)"
    )
    config.addinivalue_line("markers", "slow: Tests that take longer to run (>5 seconds)")
    config.addinivalue_line("markers", "requires_models: Tests requiring downloaded models")
    config.addinivalue_line("markers", "webrtc: WebRTC-specific tests")
