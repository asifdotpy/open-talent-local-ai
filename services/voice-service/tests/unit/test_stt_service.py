"""Unit Tests for Whisper STT Service.

Following TDD principles:
- Red-Green-Refactor cycle
- Behavior-driven test design
- Proper mocking and isolation
- Comprehensive edge case coverage
- Clear test documentation

Created: November 13, 2025
"""

import sys
from unittest.mock import Mock, patch

import pytest

# Mock torch and whisper before importing the service
sys.modules['torch'] = Mock()
sys.modules['torch.cuda'] = Mock()
sys.modules['whisper'] = Mock()

from services.stt_service import WhisperSTTService


@pytest.fixture
def stt_service():
    """Create STT service instance with base model."""
    return WhisperSTTService(model_size="base")


@pytest.fixture
def mock_whisper_model():
    """Create mock Whisper model."""
    model = Mock()
    model.transcribe = Mock()
    return model


class TestWhisperSTTServiceInitialization:
    """Test service initialization and configuration."""

class TestWhisperSTTServiceInitialization:
    """Test service initialization and configuration."""

    def test_initialization_with_default_model(self):
        """Test that service initializes with base model by default."""
        service = WhisperSTTService()

        assert service.model_size == "base"

    def test_initialization_with_custom_model_size(self):
        """Test that service initializes with custom model size."""
        service = WhisperSTTService(model_size="large")

        assert service.model_size == "large"

    def test_initialization_sets_model_to_none(self, stt_service):
        """Test that model is None until explicitly loaded."""
        assert stt_service.model is None

    @patch('torch.cuda.is_available', return_value=True)
    def test_initialization_selects_cuda_when_available(self, mock_cuda):
        """Test that service uses CUDA when available."""
        service = WhisperSTTService()

        assert service.device == "cuda"

    @patch('torch.cuda.is_available', return_value=False)
    def test_initialization_falls_back_to_cpu(self, mock_cuda):
        """Test that service falls back to CPU when CUDA unavailable."""
        service = WhisperSTTService()

        assert service.device == "cpu"

    def test_initialization_with_custom_device(self):
        """Test that service accepts custom device specification."""
        service = WhisperSTTService(device="cuda:1")

        assert service.device == "cuda:1"

    def test_initialization_with_all_model_sizes(self):
        """Test that service accepts all valid model sizes."""
        model_sizes = ["tiny", "base", "small", "medium", "large"]

        for size in model_sizes:
            service = WhisperSTTService(model_size=size)
            assert service.model_size == size


class TestModelLoading:
    """Test Whisper model loading functionality."""

    @patch('whisper.load_model')
    def test_load_model_succeeds_with_valid_configuration(
        self, mock_load, stt_service, mock_whisper_model
    ):
        """Test that model loads successfully with valid configuration."""
        # Arrange
        mock_load.return_value = mock_whisper_model

        # Act
        result = stt_service.load_model()

        # Assert
        assert result is True
        assert stt_service.model == mock_whisper_model
        mock_load.assert_called_once_with("base", device=stt_service.device)

    @patch('whisper.load_model')
    def test_load_model_fails_when_model_not_found(
        self, mock_load, stt_service
    ):
        """Test that model loading fails gracefully when model not found."""
        # Arrange
        mock_load.side_effect = FileNotFoundError("Model not found")

        # Act
        result = stt_service.load_model()

        # Assert
        assert result is False
        assert stt_service.model is None

    @patch('whisper.load_model')
    def test_load_model_fails_on_exception(
        self, mock_load, stt_service
    ):
        """Test that model loading handles exceptions gracefully."""
        # Arrange
        mock_load.side_effect = Exception("Model load failed")

        # Act
        result = stt_service.load_model()

        # Assert
        assert result is False
        assert stt_service.model is None

    @patch('whisper.load_model')
    def test_load_model_with_different_model_sizes(self, mock_load, mock_whisper_model):
        """Test that different model sizes load correctly."""
        # Arrange
        mock_load.return_value = mock_whisper_model
        model_sizes = ["tiny", "base", "small", "medium", "large"]

        for size in model_sizes:
            # Act
            service = WhisperSTTService(model_size=size)
            result = service.load_model()

            # Assert
            assert result is True
            mock_load.assert_called_with(size, device=service.device)

    @patch('whisper.load_model')
    def test_load_model_multiple_times_replaces_old_model(
        self, mock_load, stt_service, mock_whisper_model
    ):
        """Test that loading model multiple times replaces the old one."""
        # Arrange
        mock_load.return_value = mock_whisper_model

        # Act
        first_load = stt_service.load_model()
        second_load = stt_service.load_model()

        # Assert
        assert first_load is True
        assert second_load is True
        assert mock_load.call_count == 2


class TestAudioTranscription:
    """Test audio transcription functionality."""

    def test_transcribe_fails_without_loaded_model(self, stt_service, test_audio_file):
        """Test that transcription fails when model is not loaded."""
        # Act
        result = stt_service.transcribe_audio(test_audio_file)

        # Assert
        assert result is None

    @patch('whisper.load_model')
    def test_transcribe_succeeds_with_valid_audio(
        self, mock_load, stt_service, test_audio_file, mock_whisper_model
    ):
        """Test that transcription succeeds with valid audio file."""
        # Arrange
        mock_whisper_model.transcribe.return_value = {"text": "Hello world"}
        mock_load.return_value = mock_whisper_model
        stt_service.load_model()

        # Act
        result = stt_service.transcribe_audio(test_audio_file)

        # Assert
        assert result == "Hello world"
        mock_whisper_model.transcribe.assert_called_once_with(
            test_audio_file,
            language="en",
            fp16=False,
            verbose=False
        )

    @patch('whisper.load_model')
    def test_transcribe_strips_whitespace_from_result(
        self, mock_load, stt_service, test_audio_file, mock_whisper_model
    ):
        """Test that transcription result is stripped of surrounding whitespace."""
        # Arrange
        mock_whisper_model.transcribe.return_value = {"text": "  Hello world  \n\t"}
        mock_load.return_value = mock_whisper_model
        stt_service.load_model()

        # Act
        result = stt_service.transcribe_audio(test_audio_file)

        # Assert
        assert result == "Hello world"

    @patch('whisper.load_model')
    def test_transcribe_with_different_languages(
        self, mock_load, stt_service, test_audio_file, mock_whisper_model
    ):
        """Test that transcription supports different languages."""
        # Arrange
        mock_whisper_model.transcribe.return_value = {"text": "Hola mundo"}
        mock_load.return_value = mock_whisper_model
        stt_service.load_model()

        # Act
        result = stt_service.transcribe_audio(test_audio_file, language="es")

        # Assert
        assert result == "Hola mundo"
        mock_whisper_model.transcribe.assert_called_once_with(
            test_audio_file,
            language="es",
            fp16=False,
            verbose=False
        )

    @patch('whisper.load_model')
    def test_transcribe_fails_gracefully_on_exception(
        self, mock_load, stt_service, test_audio_file, mock_whisper_model
    ):
        """Test that transcription handles exceptions gracefully."""
        # Arrange
        mock_whisper_model.transcribe.side_effect = Exception("Transcription failed")
        mock_load.return_value = mock_whisper_model
        stt_service.load_model()

        # Act
        result = stt_service.transcribe_audio(test_audio_file)

        # Assert
        assert result is None

    @patch('whisper.load_model')
    def test_transcribe_with_nonexistent_file(
        self, mock_load, stt_service, mock_whisper_model
    ):
        """Test that transcription handles nonexistent files gracefully."""
        # Arrange
        mock_whisper_model.transcribe.side_effect = FileNotFoundError("File not found")
        mock_load.return_value = mock_whisper_model
        stt_service.load_model()

        # Act
        result = stt_service.transcribe_audio("/nonexistent/file.wav")

        # Assert
        assert result is None

    @patch('whisper.load_model')
    def test_transcribe_with_empty_result(
        self, mock_load, stt_service, test_audio_file, mock_whisper_model
    ):
        """Test that transcription handles empty transcription results."""
        # Arrange
        mock_whisper_model.transcribe.return_value = {"text": ""}
        mock_load.return_value = mock_whisper_model
        stt_service.load_model()

        # Act
        result = stt_service.transcribe_audio(test_audio_file)

        # Assert
        assert result == ""

    @patch('whisper.load_model')
    def test_transcribe_multiple_files_sequentially(
        self, mock_load, stt_service, test_audio_file, short_audio_file, mock_whisper_model
    ):
        """Test that multiple files can be transcribed sequentially."""
        # Arrange
        mock_whisper_model.transcribe.side_effect = [
            {"text": "First transcription"},
            {"text": "Second transcription"}
        ]
        mock_load.return_value = mock_whisper_model
        stt_service.load_model()

        # Act
        result1 = stt_service.transcribe_audio(test_audio_file)
        result2 = stt_service.transcribe_audio(short_audio_file)

        # Assert
        assert result1 == "First transcription"
        assert result2 == "Second transcription"
        assert mock_whisper_model.transcribe.call_count == 2


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""

    @patch('whisper.load_model')
    def test_transcribe_with_corrupted_audio_file(
        self, mock_load, stt_service, invalid_audio_file, mock_whisper_model
    ):
        """Test that transcription handles corrupted audio files."""
        # Arrange
        mock_whisper_model.transcribe.side_effect = RuntimeError("Invalid audio format")
        mock_load.return_value = mock_whisper_model
        stt_service.load_model()

        # Act
        result = stt_service.transcribe_audio(invalid_audio_file)

        # Assert
        assert result is None

    @patch('whisper.load_model')
    def test_transcribe_with_very_long_audio(
        self, mock_load, stt_service, long_audio_file, mock_whisper_model
    ):
        """Test that transcription handles long audio files."""
        # Arrange
        long_transcription = "This is a very long transcription " * 50
        mock_whisper_model.transcribe.return_value = {"text": long_transcription}
        mock_load.return_value = mock_whisper_model
        stt_service.load_model()

        # Act
        result = stt_service.transcribe_audio(long_audio_file)

        # Assert
        assert result == long_transcription.strip()

    @patch('whisper.load_model')
    def test_transcribe_with_silent_audio(
        self, mock_load, stt_service, silent_audio_file, mock_whisper_model
    ):
        """Test that transcription handles silent audio."""
        # Arrange
        mock_whisper_model.transcribe.return_value = {"text": ""}
        mock_load.return_value = mock_whisper_model
        stt_service.load_model()

        # Act
        result = stt_service.transcribe_audio(silent_audio_file)

        # Assert
        assert result == ""

    def test_transcribe_with_invalid_language_code(self, stt_service, test_audio_file):
        """Test that transcription handles invalid language codes."""
        # Note: Whisper may accept or reject invalid codes
        # This test ensures the service doesn't crash
        with patch('whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.side_effect = ValueError("Invalid language")
            mock_load.return_value = mock_model
            stt_service.load_model()

            result = stt_service.transcribe_audio(test_audio_file, language="invalid")

            assert result is None

    @patch('whisper.load_model')
    def test_transcribe_preserves_punctuation(
        self, mock_load, stt_service, test_audio_file, mock_whisper_model
    ):
        """Test that transcription preserves punctuation in results."""
        # Arrange
        text_with_punctuation = "Hello! How are you? I'm fine, thank you."
        mock_whisper_model.transcribe.return_value = {"text": text_with_punctuation}
        mock_load.return_value = mock_whisper_model
        stt_service.load_model()

        # Act
        result = stt_service.transcribe_audio(test_audio_file)

        # Assert
        assert result == text_with_punctuation

    @patch('whisper.load_model')
    def test_transcribe_handles_numbers_in_text(
        self, mock_load, stt_service, test_audio_file, mock_whisper_model
    ):
        """Test that transcription handles numbers in transcribed text."""
        # Arrange
        text_with_numbers = "The year is 2025 and the time is 3:45 PM"
        mock_whisper_model.transcribe.return_value = {"text": text_with_numbers}
        mock_load.return_value = mock_whisper_model
        stt_service.load_model()

        # Act
        result = stt_service.transcribe_audio(test_audio_file)

        # Assert
        assert result == text_with_numbers


class TestDeviceManagement:
    """Test device selection and management."""

    @patch('torch.cuda.is_available', return_value=False)
    @patch('whisper.load_model')
    def test_model_loads_on_cpu_when_cuda_unavailable(
        self, mock_load, mock_cuda, mock_whisper_model
    ):
        """Test that model loads on CPU when CUDA is unavailable."""
        # Arrange
        mock_load.return_value = mock_whisper_model
        service = WhisperSTTService()

        # Act
        result = service.load_model()

        # Assert
        assert result is True
        mock_load.assert_called_once_with("base", device="cpu")

    @patch('torch.cuda.is_available', return_value=True)
    @patch('whisper.load_model')
    def test_model_loads_on_cuda_when_available(
        self, mock_load, mock_cuda, mock_whisper_model
    ):
        """Test that model loads on CUDA when available."""
        # Arrange
        mock_load.return_value = mock_whisper_model
        service = WhisperSTTService()

        # Act
        result = service.load_model()

        # Assert
        assert result is True
        mock_load.assert_called_once_with("base", device="cuda")

    @patch('whisper.load_model')
    def test_custom_device_is_respected(
        self, mock_load, mock_whisper_model
    ):
        """Test that custom device specification is respected."""
        # Arrange
        mock_load.return_value = mock_whisper_model
        service = WhisperSTTService(device="cuda:2")

        # Act
        result = service.load_model()

        # Assert
        assert result is True
        mock_load.assert_called_once_with("base", device="cuda:2")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
