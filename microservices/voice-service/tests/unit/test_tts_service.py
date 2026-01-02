"""Unit Tests for Piper TTS Service

Following TDD principles:
- Test behavior, not implementation
- Arrange, Act, Assert pattern
- Clear test names describing expected behavior
- Comprehensive edge case coverage
- Proper mocking and isolation

Created: November 13, 2025
"""

import subprocess
from unittest.mock import Mock, patch

import pytest

from services.tts_service import PiperTTSService


@pytest.fixture
def tts_service(mock_piper_path, mock_model_path):
    """Create TTS service instance with mocked paths."""
    return PiperTTSService(piper_path=mock_piper_path, model_path=mock_model_path)


class TestPiperTTSServiceInitialization:
    """Test service initialization and configuration."""

    def test_initialization_stores_piper_path(self, mock_piper_path, mock_model_path):
        """Test that initialization stores the piper executable path."""
        service = PiperTTSService(piper_path=mock_piper_path, model_path=mock_model_path)

        assert service.piper_path == mock_piper_path

    def test_initialization_stores_model_path(self, mock_piper_path, mock_model_path):
        """Test that initialization stores the model file path."""
        service = PiperTTSService(piper_path=mock_piper_path, model_path=mock_model_path)

        assert service.model_path == mock_model_path

    def test_initialization_stores_model_path(self, mock_piper_path, mock_model_path):
        """Test that initialization stores the model file path."""
        service = PiperTTSService(piper_path=mock_piper_path, model_path=mock_model_path)

        assert service.model_path == mock_model_path

    def test_initialization_with_custom_paths(self, tmp_path):
        """Test initialization with custom piper and model paths."""
        custom_piper = str(tmp_path / "custom_piper")
        custom_model = str(tmp_path / "custom_model.onnx")

        service = PiperTTSService(piper_path=custom_piper, model_path=custom_model)

        assert service.piper_path == custom_piper
        assert service.model_path == custom_model


class TestPiperInstallationCheck:
    """Test Piper installation verification."""

    @patch("subprocess.run")
    def test_check_installation_succeeds_when_piper_found(
        self, mock_run, tts_service, mock_piper_path, mock_model_path
    ):
        """Test that installation check passes when Piper is properly installed."""
        # Arrange
        mock_run.return_value = Mock(returncode=0, stdout="0.0.2", stderr="")

        # Act
        result = tts_service.check_installation()

        # Assert
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == mock_piper_path
        assert "--version" in args

    @patch("subprocess.run")
    def test_check_installation_fails_when_piper_not_found(self, mock_run, tts_service):
        """Test that installation check fails when Piper executable is missing."""
        # Arrange
        mock_run.side_effect = FileNotFoundError("Piper not found")

        # Act
        result = tts_service.check_installation()

        # Assert
        assert result is False

    @patch("subprocess.run")
    def test_check_installation_fails_when_piper_returns_error(self, mock_run, tts_service):
        """Test that installation check fails when Piper returns non-zero exit code."""
        # Arrange
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Command not found")

        # Act
        result = tts_service.check_installation()

        # Assert
        assert result is False

    @patch("subprocess.run")
    def test_check_installation_fails_when_model_missing(self, mock_run, mock_piper_path, tmp_path):
        """Test that installation check fails when model file doesn't exist."""
        # Arrange
        mock_run.return_value = Mock(returncode=0, stdout="0.0.2", stderr="")
        missing_model = str(tmp_path / "missing_model.onnx")
        service = PiperTTSService(piper_path=mock_piper_path, model_path=missing_model)

        # Act
        result = service.check_installation()

        # Assert
        assert result is False

    @patch("subprocess.run")
    def test_check_installation_fails_when_model_config_missing(
        self, mock_run, mock_piper_path, tmp_path
    ):
        """Test that installation check fails when model .json config is missing."""
        # Arrange
        mock_run.return_value = Mock(returncode=0, stdout="0.0.2", stderr="")

        # Create model file without .json config
        model_path = tmp_path / "model.onnx"
        model_path.write_bytes(b"model data")

        service = PiperTTSService(piper_path=mock_piper_path, model_path=str(model_path))

        # Act
        result = service.check_installation()

        # Assert
        assert result is False

    @patch("subprocess.run")
    def test_check_installation_times_out_gracefully(self, mock_run, tts_service):
        """Test that installation check handles timeout gracefully."""
        # Arrange
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=5)

        # Act
        result = tts_service.check_installation()

        # Assert
        assert result is False


class TestSpeechSynthesis:
    """Test speech synthesis functionality."""

    @patch("subprocess.Popen")
    @patch("os.path.exists")
    def test_synthesize_creates_audio_file(
        self, mock_exists, mock_popen, tts_service, short_text, test_audio_dir
    ):
        """Test that synthesize creates an audio file from text."""
        # Arrange
        output_file = str(test_audio_dir / "output.wav")
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_exists.return_value = True

        # Act
        result = tts_service.synthesize(short_text, output_file)

        # Assert
        assert result == output_file
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        assert tts_service.piper_path in args
        assert "--model" in args
        assert "--output_file" in args
        assert output_file in args

    @patch("subprocess.Popen")
    def test_synthesize_sends_text_to_piper_stdin(
        self, mock_popen, tts_service, sample_text, test_audio_dir
    ):
        """Test that text is sent to Piper via stdin."""
        # Arrange
        output_file = str(test_audio_dir / "output.wav")
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Act
        with patch("os.path.exists", return_value=True):
            tts_service.synthesize(sample_text, output_file)

        # Assert
        mock_process.communicate.assert_called_once_with(input=sample_text, timeout=30)

    @patch("subprocess.Popen")
    def test_synthesize_fails_when_piper_returns_error(
        self, mock_popen, tts_service, short_text, test_audio_dir
    ):
        """Test that synthesize returns None when Piper process fails."""
        # Arrange
        output_file = str(test_audio_dir / "output.wav")
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "Synthesis failed")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        # Act
        result = tts_service.synthesize(short_text, output_file)

        # Assert
        assert result is None

    @patch("subprocess.Popen")
    def test_synthesize_fails_when_output_file_not_created(
        self, mock_popen, tts_service, short_text, test_audio_dir
    ):
        """Test that synthesize returns None when output file is not created."""
        # Arrange
        output_file = str(test_audio_dir / "output.wav")
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Act
        with patch("os.path.exists", return_value=False):
            result = tts_service.synthesize(short_text, output_file)

        # Assert
        assert result is None

    @patch("subprocess.Popen")
    def test_synthesize_handles_timeout(self, mock_popen, tts_service, long_text, test_audio_dir):
        """Test that synthesize handles process timeout gracefully."""
        # Arrange
        output_file = str(test_audio_dir / "output.wav")
        mock_process = Mock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=30)
        mock_popen.return_value = mock_process

        # Act
        result = tts_service.synthesize(long_text, output_file)

        # Assert
        assert result is None

    @patch("subprocess.Popen")
    def test_synthesize_handles_empty_text(
        self, mock_popen, tts_service, empty_text, test_audio_dir
    ):
        """Test that synthesize handles empty text input."""
        # Arrange
        output_file = str(test_audio_dir / "output.wav")
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Act
        with patch("os.path.exists", return_value=True):
            result = tts_service.synthesize(empty_text, output_file)

        # Assert - should still attempt synthesis, Piper will handle it
        assert mock_popen.called

    @patch("subprocess.Popen")
    def test_synthesize_handles_special_characters(
        self, mock_popen, tts_service, special_characters_text, test_audio_dir
    ):
        """Test that synthesize correctly handles text with special characters."""
        # Arrange
        output_file = str(test_audio_dir / "output.wav")
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Act
        with patch("os.path.exists", return_value=True):
            result = tts_service.synthesize(special_characters_text, output_file)

        # Assert
        mock_process.communicate.assert_called_once()
        call_args = mock_process.communicate.call_args
        assert special_characters_text in call_args[1]["input"]

    @patch("subprocess.Popen")
    @patch("os.path.exists")
    def test_synthesize_with_long_text(
        self, mock_exists, mock_popen, tts_service, long_text, test_audio_dir
    ):
        """Test that synthesize can handle long text input."""
        # Arrange
        output_file = str(test_audio_dir / "output.wav")
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_exists.return_value = True

        # Act
        result = tts_service.synthesize(long_text, output_file)

        # Assert
        assert result == output_file

    @patch("subprocess.Popen")
    def test_synthesize_handles_process_exception(
        self, mock_popen, tts_service, short_text, test_audio_dir
    ):
        """Test that synthesize handles unexpected exceptions gracefully."""
        # Arrange
        output_file = str(test_audio_dir / "output.wav")
        mock_popen.side_effect = Exception("Unexpected error")

        # Act
        result = tts_service.synthesize(short_text, output_file)

        # Assert
        assert result is None


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""

    def test_synthesize_with_unicode_text(self, tts_service, test_audio_dir):
        """Test that synthesize handles unicode characters."""
        # Arrange
        unicode_text = "Hello 你好 مرحبا Привет"
        output_file = str(test_audio_dir / "output.wav")

        # Act & Assert
        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.communicate.return_value = ("", "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            with patch("os.path.exists", return_value=True):
                result = tts_service.synthesize(unicode_text, output_file)

            # Should attempt to process (actual handling depends on Piper)
            assert mock_popen.called

    def test_synthesize_with_very_long_output_path(self, tts_service, short_text, tmp_path):
        """Test that synthesize handles very long output file paths."""
        # Arrange
        long_path = str(tmp_path / ("a" * 200) / "output.wav")

        # Act
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.side_effect = OSError("Path too long")
            result = tts_service.synthesize(short_text, long_path)

        # Assert
        assert result is None

    @patch("subprocess.Popen")
    def test_synthesize_with_nonexistent_output_directory(
        self, mock_popen, tts_service, short_text
    ):
        """Test that synthesize handles nonexistent output directory."""
        # Arrange
        output_file = "/nonexistent/directory/output.wav"
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Act
        with patch("os.path.exists", return_value=False):
            result = tts_service.synthesize(short_text, output_file)

        # Assert
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
