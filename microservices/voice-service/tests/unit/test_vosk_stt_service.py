"""Unit Tests for Vosk STT Service

Following TDD principles with comprehensive test coverage for production-ready
speech-to-text service using Vosk (Kaldi-based, CPU-only inference).

Created: November 13, 2025
"""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pytest

# Mock vosk before importing the service
sys.modules["vosk"] = Mock()

from services.vosk_stt_service import VoskSTTService


@pytest.fixture
def vosk_service():
    """Create VoskSTTService instance for testing."""
    with patch("services.vosk_stt_service.VOSK_AVAILABLE", True):
        with patch.object(VoskSTTService, "load_model"):
            service = VoskSTTService(
                model_path="models/vosk-model-small-en-us-0.15", sample_rate=16000
            )
            return service


@pytest.fixture
def mock_vosk_model():
    """Create mock Vosk model."""
    mock_model = Mock()
    return mock_model


@pytest.fixture
def mock_vosk_recognizer():
    """Create mock Vosk recognizer."""
    mock_recognizer = Mock()
    mock_recognizer.AcceptWaveform = Mock(return_value=True)
    mock_recognizer.FinalResult = Mock(
        return_value=json.dumps(
            {
                "text": "hello world",
                "result": [
                    {"word": "hello", "start": 0.0, "end": 0.5, "conf": 0.95},
                    {"word": "world", "start": 0.5, "end": 1.0, "conf": 0.93},
                ],
            }
        )
    )
    return mock_recognizer


@pytest.mark.unit
class TestVoskSTTServiceInitialization:
    """Test Vosk STT service initialization and configuration."""

    def test_initialization_with_default_model(self):
        """Test that service initializes with default model path."""
        # Arrange & Act
        with patch.object(VoskSTTService, "load_model"):
            service = VoskSTTService()

        # Assert
        assert service.model_path == Path("models/vosk-model-small-en-us-0.15")
        assert service.sample_rate == 16000

    def test_initialization_with_custom_model_path(self):
        """Test initialization with custom model path."""
        # Arrange
        custom_path = "custom/vosk-model"

        # Act
        with patch.object(VoskSTTService, "load_model"):
            service = VoskSTTService(model_path=custom_path)

        # Assert
        assert service.model_path == Path(custom_path)

    def test_initialization_with_custom_sample_rate(self):
        """Test initialization with custom sample rate."""
        # Arrange & Act
        with patch.object(VoskSTTService, "load_model"):
            service = VoskSTTService(sample_rate=8000)

        # Assert
        assert service.sample_rate == 8000

    def test_initialization_sets_model_to_none(self):
        """Test that model is initially None before loading."""
        # Arrange & Act
        with patch.object(VoskSTTService, "load_model"):
            service = VoskSTTService()

        # Assert
        assert service.model is None
        assert service.recognizer is None


@pytest.mark.unit
class TestVoskModelLoading:
    """Test Vosk model loading and initialization."""

    @patch("services.vosk_stt_service.Model")
    @patch("services.vosk_stt_service.KaldiRecognizer")
    def test_load_model_succeeds_with_valid_configuration(
        self, mock_recognizer_class, mock_model_class, vosk_service
    ):
        """Test successful model loading with valid configuration."""
        # Arrange
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        mock_recognizer = Mock()
        mock_recognizer_class.return_value = mock_recognizer

        # Act
        with patch("pathlib.Path.exists", return_value=True):
            result = vosk_service.load_model()

        # Assert
        assert result is True
        assert vosk_service.model == mock_model
        assert vosk_service.recognizer == mock_recognizer

    @patch("services.vosk_stt_service.Model")
    def test_load_model_fails_when_model_not_found(self, mock_model_class, vosk_service):
        """Test that model loading fails gracefully when model directory not found."""
        # Arrange
        mock_model_class.side_effect = Exception("Model not found")

        # Act
        with patch("pathlib.Path.exists", return_value=False):
            result = vosk_service.load_model()

        # Assert
        assert result is False
        assert vosk_service.model is None

    @patch("services.vosk_stt_service.Model")
    def test_load_model_fails_on_exception(self, mock_model_class, vosk_service):
        """Test that model loading handles exceptions properly."""
        # Arrange
        mock_model_class.side_effect = RuntimeError("Model loading failed")

        # Act
        result = vosk_service.load_model()

        # Assert
        assert result is False
        assert vosk_service.model is None


@pytest.mark.unit
class TestVoskAudioTranscription:
    """Test audio transcription functionality."""

    def test_transcribe_fails_without_loaded_model(self, vosk_service, test_audio_file):
        """Test that transcription fails if model is not loaded."""
        # Arrange
        vosk_service.model = None

        # Act
        result = vosk_service.transcribe_audio(str(test_audio_file))

        # Assert
        assert result is None

    @patch("services.vosk_stt_service.sf.read")
    def test_transcribe_succeeds_with_valid_audio(
        self, mock_sf_read, vosk_service, mock_vosk_recognizer, test_audio_file
    ):
        """Test successful transcription with valid audio."""
        # Arrange
        vosk_service.model = Mock()
        vosk_service.recognizer = mock_vosk_recognizer

        # Mock audio data
        audio_data = np.random.randn(16000).astype(np.float32)
        mock_sf_read.return_value = (audio_data, 16000)

        # Act
        result = vosk_service.transcribe_audio(str(test_audio_file))

        # Assert
        assert result is not None
        assert "text" in result
        assert "words" in result
        assert "duration" in result
        assert "confidence" in result

    @patch("services.vosk_stt_service.sf.read")
    def test_transcribe_handles_stereo_to_mono_conversion(
        self, mock_sf_read, vosk_service, mock_vosk_recognizer
    ):
        """Test that stereo audio is converted to mono."""
        # Arrange
        vosk_service.model = Mock()
        vosk_service.recognizer = mock_vosk_recognizer

        # Mock stereo audio data
        stereo_audio = np.random.randn(16000, 2).astype(np.float32)
        mock_sf_read.return_value = (stereo_audio, 16000)

        # Act
        result = vosk_service.transcribe_audio("test.wav")

        # Assert
        assert result is not None
        mock_vosk_recognizer.AcceptWaveform.assert_called_once()

    @patch("services.vosk_stt_service.sf.read")
    def test_transcribe_handles_sample_rate_conversion(
        self, mock_sf_read, vosk_service, mock_vosk_recognizer
    ):
        """Test that audio is resampled to target sample rate."""
        # Arrange
        vosk_service.model = Mock()
        vosk_service.recognizer = mock_vosk_recognizer

        # Mock audio with different sample rate
        audio_data = np.random.randn(44100).astype(np.float32)
        mock_sf_read.return_value = (audio_data, 44100)

        with patch.object(vosk_service, "_resample_audio") as mock_resample:
            mock_resample.return_value = np.random.randn(16000).astype(np.float32)

            # Act
            result = vosk_service.transcribe_audio("test.wav")

            # Assert
            assert result is not None
            mock_resample.assert_called_once()

    @patch("services.vosk_stt_service.sf.read")
    def test_transcribe_calculates_word_confidence(
        self, mock_sf_read, vosk_service, mock_vosk_recognizer
    ):
        """Test that average confidence is calculated from word confidences."""
        # Arrange
        vosk_service.model = Mock()
        vosk_service.recognizer = mock_vosk_recognizer

        audio_data = np.random.randn(16000).astype(np.float32)
        mock_sf_read.return_value = (audio_data, 16000)

        # Act
        result = vosk_service.transcribe_audio("test.wav")

        # Assert
        assert result["confidence"] > 0.0
        # Average of 0.95 and 0.93 should be 0.94
        assert abs(result["confidence"] - 0.94) < 0.01

    @patch("services.vosk_stt_service.sf.read")
    def test_transcribe_fails_gracefully_on_exception(self, mock_sf_read, vosk_service):
        """Test that transcription handles exceptions gracefully."""
        # Arrange
        vosk_service.model = Mock()
        mock_sf_read.side_effect = Exception("Audio read failed")

        # Act
        result = vosk_service.transcribe_audio("test.wav")

        # Assert
        assert result is None


@pytest.mark.unit
class TestVoskStreamingTranscription:
    """Test streaming transcription functionality."""

    def test_streaming_requires_loaded_model(self, vosk_service):
        """Test that streaming transcription requires loaded model."""
        # Arrange
        vosk_service.model = None
        audio_chunk = b"test audio data"

        # Act
        result = vosk_service.transcribe_streaming(audio_chunk)

        # Assert
        assert result is None

    def test_streaming_accepts_audio_chunks(self, vosk_service, mock_vosk_recognizer):
        """Test that streaming accepts audio chunks."""
        # Arrange
        vosk_service.model = Mock()
        vosk_service.recognizer = mock_vosk_recognizer
        mock_vosk_recognizer.AcceptWaveform.return_value = False
        mock_vosk_recognizer.PartialResult.return_value = json.dumps({"partial": "hello"})

        audio_chunk = b"test audio data"

        # Act
        result = vosk_service.transcribe_streaming(audio_chunk)

        # Assert
        mock_vosk_recognizer.AcceptWaveform.assert_called_once_with(audio_chunk)

    def test_reset_recognizer_recreates_instance(self, vosk_service):
        """Test that reset_recognizer creates new recognizer instance."""
        # Arrange
        vosk_service.model = Mock()
        old_recognizer = Mock()
        vosk_service.recognizer = old_recognizer

        with patch("services.vosk_stt_service.KaldiRecognizer") as mock_recognizer_class:
            new_recognizer = Mock()
            mock_recognizer_class.return_value = new_recognizer

            # Act
            vosk_service.reset_recognizer()

            # Assert
            assert vosk_service.recognizer == new_recognizer
            assert vosk_service.recognizer != old_recognizer


@pytest.mark.unit
class TestVoskEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""

    @patch("services.vosk_stt_service.sf.read")
    def test_transcribe_with_corrupted_audio_file(self, mock_sf_read, vosk_service):
        """Test handling of corrupted audio files."""
        # Arrange
        vosk_service.model = Mock()
        mock_sf_read.side_effect = RuntimeError("Invalid audio format")

        # Act
        result = vosk_service.transcribe_audio("corrupted.wav")

        # Assert
        assert result is None

    @patch("services.vosk_stt_service.sf.read")
    def test_transcribe_with_empty_result(self, mock_sf_read, vosk_service, mock_vosk_recognizer):
        """Test transcription with empty/silent audio."""
        # Arrange
        vosk_service.model = Mock()
        vosk_service.recognizer = mock_vosk_recognizer
        mock_vosk_recognizer.FinalResult.return_value = json.dumps({"text": ""})

        audio_data = np.zeros(16000).astype(np.float32)
        mock_sf_read.return_value = (audio_data, 16000)

        # Act
        result = vosk_service.transcribe_audio("silent.wav")

        # Assert
        assert result is not None
        assert result["text"] == ""

    def test_health_check_succeeds_with_loaded_model(self, vosk_service):
        """Test health check returns True when model is loaded."""
        # Arrange
        vosk_service.model = Mock()
        vosk_service.recognizer = Mock()

        # Act
        result = vosk_service.health_check()

        # Assert
        assert result is True

    def test_health_check_fails_without_model(self, vosk_service):
        """Test health check returns False when model is not loaded."""
        # Arrange
        vosk_service.model = None

        # Act
        result = vosk_service.health_check()

        # Assert
        assert result is False

    def test_get_info_returns_service_metadata(self, vosk_service):
        """Test that get_info returns service information."""
        # Arrange & Act
        info = vosk_service.get_info()

        # Assert
        assert "service" in info
        assert "model_path" in info
        assert "sample_rate" in info
        assert "status" in info
