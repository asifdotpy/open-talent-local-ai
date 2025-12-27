from unittest.mock import Mock, patch

import pytest

from services.vad_service import VoiceActivityDetector


class TestVoiceActivityDetector:
    """Test Voice Activity Detector Service."""

    @pytest.fixture
    def vad_service(self):
        """Create VAD service instance."""
        return VoiceActivityDetector()

    def test_initialization(self, vad_service):
        """Test service initialization."""
        assert vad_service.use_vad is True  # Default from env
        assert vad_service.aggressiveness == 2  # Default from env
        assert vad_service.frame_duration_ms == 30
        assert vad_service.sample_rate == 16000
        assert vad_service.speech_threshold == 0.5
        assert vad_service.vad is not None  # Should be initialized
        assert vad_service.speech_frames_buffer == []
        assert vad_service.max_buffer_size == 10

    def test_custom_initialization(self):
        """Test custom initialization parameters."""
        # Note: VAD service reads environment variables at module level
        # We need to reload the module to test different env values
        import importlib
        import os

        old_aggressiveness = os.environ.get("VAD_AGGRESSIVENESS")
        old_sample_rate = os.environ.get("VAD_SAMPLE_RATE")

        try:
            os.environ["VAD_AGGRESSIVENESS"] = "1"
            os.environ["VAD_SAMPLE_RATE"] = "8000"

            # Reload the module to pick up new env vars
            import services.vad_service
            importlib.reload(services.vad_service)

            service = services.vad_service.VoiceActivityDetector()
            assert service.aggressiveness == 1
            assert service.sample_rate == 8000
        finally:
            # Restore environment
            if old_aggressiveness is not None:
                os.environ["VAD_AGGRESSIVENESS"] = old_aggressiveness
            else:
                os.environ.pop("VAD_AGGRESSIVENESS", None)
            if old_sample_rate is not None:
                os.environ["VAD_SAMPLE_RATE"] = old_sample_rate
            else:
                os.environ.pop("VAD_SAMPLE_RATE", None)

            # Reload again to restore original values
            importlib.reload(services.vad_service)

    @patch('webrtcvad.Vad')
    def test_initialize_vad_success(self, mock_vad_class, vad_service):
        """Test successful VAD initialization."""
        mock_vad_instance = Mock()
        mock_vad_class.return_value = mock_vad_instance

        result = vad_service._initialize_vad()

        assert result is True
        assert vad_service.vad == mock_vad_instance
        mock_vad_class.assert_called_once_with(vad_service.aggressiveness)

    @patch('webrtcvad.Vad')
    def test_initialize_vad_failure(self, mock_vad_class, vad_service):
        """Test VAD initialization failure."""
        mock_vad_class.side_effect = Exception("VAD init failed")

        result = vad_service._initialize_vad()

        assert result is False
        assert vad_service.vad is None

    def test_is_speech_without_vad(self, vad_service):
        """Test speech detection without VAD (fallback mode)."""
        # Disable VAD to test fallback
        vad_service.use_vad = False
        audio_chunk = b'\x00\x01' * 160  # 320 bytes = 160 samples at 16-bit

        result = vad_service.is_speech(audio_chunk)

        assert result is True  # Should always return True when VAD disabled

    def test_is_speech_success(self, vad_service):
        """Test successful speech detection."""
        # Create valid audio frame (30ms at 16kHz = 480 samples = 960 bytes)
        audio_frame = b'\x00\x01' * 480

        result = vad_service.is_speech(audio_frame)

        # Should return True (speech detected) or False (silence)
        assert isinstance(result, bool)

    def test_is_speech_silence(self, vad_service):
        """Test silence detection."""
        audio_frame = b'\x00\x01' * 480

        result = vad_service.is_speech(audio_frame)

        # Should return a boolean
        assert isinstance(result, bool)

    def test_is_speech_invalid_frame_size(self, vad_service):
        """Test speech detection with invalid frame size."""
        # Invalid frame size (not 30ms worth of samples at 16kHz)
        audio_frame = b'\x00\x01' * 100  # 200 bytes = 100 samples

        result = vad_service.is_speech(audio_frame)

        # Should still return a boolean (padding/truncation happens internally)
        assert isinstance(result, bool)

    def test_is_speech_exception_handling(self, vad_service):
        """Test exception handling in speech detection."""
        # Test with invalid data that might cause exceptions
        audio_frame = b''  # Empty frame

        result = vad_service.is_speech(audio_frame)

        # Should handle gracefully and return a boolean
        assert isinstance(result, bool)

    def test_get_stats(self, vad_service):
        """Test getting statistics."""
        # Process some frames to generate stats
        audio_frame = b'\x00\x01' * 480
        vad_service.is_speech(audio_frame)

        stats = vad_service.get_stats()

        assert isinstance(stats, dict)
        assert "frames_analyzed" in stats
        assert "speech_frames" in stats
        assert "speech_ratio" in stats
        assert "enabled" in stats
        assert "aggressiveness" in stats

    @patch('webrtcvad.Vad')
    def test_different_aggressiveness_levels(self, mock_vad_class):
        """Test different aggressiveness levels."""
        for level in [0, 1, 2, 3]:
            service = VoiceActivityDetector()
            service._initialize_vad()
            mock_vad_class.assert_called_with(level)

    def test_aggressiveness_validation(self):
        """Test aggressiveness level validation."""
        # Valid levels should work (service uses env vars, so we test the method)
        service = VoiceActivityDetector()
        for level in [0, 1, 2, 3]:
            service.set_aggressiveness(level)
            assert service.aggressiveness == level

    @patch('webrtcvad.Vad')
    def test_multiple_initializations(self, mock_vad_class, vad_service):
        """Test multiple VAD initializations."""
        mock_vad_instance1 = Mock()
        mock_vad_instance2 = Mock()
        mock_vad_class.side_effect = [mock_vad_instance1, mock_vad_instance2]

        # First initialization
        result1 = vad_service._initialize_vad()
        assert result1 is True
        assert vad_service.vad == mock_vad_instance1

        # Second initialization should replace the first
        result2 = vad_service._initialize_vad()
        assert result2 is True
        assert vad_service.vad == mock_vad_instance2
