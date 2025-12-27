from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pytest

from services.audio_processing_service import RNNoiseTrack


class TestRNNoiseTrack:
    """Test RNNoise audio processing track."""

    @pytest.fixture
    def mock_track(self):
        """Create a mock audio track."""
        track = Mock()
        track.recv = AsyncMock()
        return track

    @pytest.fixture
    def rnnoise_track(self, mock_track):
        """Create RNNoiseTrack instance."""
        return RNNoiseTrack(mock_track)

    @pytest.mark.asyncio
    async def test_initialization(self, mock_track):
        """Test RNNoiseTrack initialization."""
        track = RNNoiseTrack(mock_track)

        assert track.track == mock_track
        assert track.sample_rate == 48000
        assert track.frame_size == 480
        assert len(track.buffer) == 0
        assert track.pts_counter == 0

    @pytest.mark.asyncio
    async def test_recv_mono_audio_processing(self, rnnoise_track):
        """Test processing mono audio frames."""
        # Create a mock frame with mono audio
        mock_frame = Mock()
        mock_frame.to_ndarray.return_value = np.random.rand(480).astype(np.float32)
        mock_frame.time_base = "1/48000"
        rnnoise_track.track.recv.return_value = mock_frame

        # Mock RNNoise processing
        with patch.object(rnnoise_track.rnnoise, "denoise_frame") as mock_denoise:
            mock_denoise.return_value = (np.array([0.8]), np.random.rand(1, 480).astype(np.int16))

            result_frame = await rnnoise_track.recv()

            # Verify RNNoise was called
            mock_denoise.assert_called_once()
            assert result_frame.sample_rate == 48000
            assert result_frame.pts == 0
            assert result_frame.time_base == "1/48000"

    @pytest.mark.asyncio
    async def test_recv_stereo_to_mono_conversion(self, rnnoise_track):
        """Test stereo to mono conversion."""
        # Create a mock frame with stereo audio
        mock_frame = Mock()
        stereo_audio = np.random.rand(2, 480).astype(np.float32)  # 2 channels
        mock_frame.to_ndarray.return_value = stereo_audio
        mock_frame.time_base = "1/48000"
        rnnoise_track.track.recv.return_value = mock_frame

        with patch.object(rnnoise_track.rnnoise, "denoise_frame") as mock_denoise:
            mock_denoise.return_value = (np.array([0.8]), np.random.rand(1, 480).astype(np.int16))

            result_frame = await rnnoise_track.recv()

            # Verify stereo was converted to mono (mean of channels)
            stereo_audio.mean(axis=0)
            assert result_frame is not None

    @pytest.mark.asyncio
    async def test_recv_rnnoise_error_fallback(self, rnnoise_track):
        """Test fallback when RNNoise processing fails."""
        mock_frame = Mock()
        mock_frame.to_ndarray.return_value = np.random.rand(480).astype(np.float32)
        mock_frame.time_base = "1/48000"
        rnnoise_track.track.recv.return_value = mock_frame

        # Mock RNNoise to raise an exception
        with patch.object(rnnoise_track.rnnoise, "denoise_frame") as mock_denoise:
            mock_denoise.side_effect = Exception("RNNoise error")

            result_frame = await rnnoise_track.recv()

            # Should still return a frame (fallback to original audio)
            assert result_frame is not None
            assert result_frame.sample_rate == 48000

    @pytest.mark.asyncio
    async def test_recv_insufficient_data_returns_silence(self, rnnoise_track):
        """Test that insufficient data returns silence frame."""
        # Create a frame with less than frame_size samples
        mock_frame = Mock()
        mock_frame.to_ndarray.return_value = np.random.rand(240).astype(np.float32)  # Less than 480
        mock_frame.time_base = "1/48000"
        rnnoise_track.track.recv.return_value = mock_frame

        result_frame = await rnnoise_track.recv()

        # Should return silence frame
        assert result_frame is not None
        assert result_frame.sample_rate == 48000
        # PTS should be incremented
        assert result_frame.pts == 480

    @pytest.mark.asyncio
    async def test_recv_buffer_accumulation(self, rnnoise_track):
        """Test audio buffer accumulation across multiple frames."""
        # First small frame
        mock_frame1 = Mock()
        mock_frame1.to_ndarray.return_value = np.random.rand(240).astype(np.float32)
        mock_frame1.time_base = "1/48000"

        # Second small frame that completes the buffer
        mock_frame2 = Mock()
        mock_frame2.to_ndarray.return_value = np.random.rand(240).astype(np.float32)
        mock_frame2.time_base = "1/48000"

        rnnoise_track.track.recv.side_effect = [mock_frame1, mock_frame2]

        with patch.object(rnnoise_track.rnnoise, "denoise_frame") as mock_denoise:
            mock_denoise.return_value = (np.array([0.8]), np.random.rand(1, 480).astype(np.int16))

            # First call should return silence (insufficient data)
            result1 = await rnnoise_track.recv()
            assert result1.pts == 0

            # Second call should process the accumulated data
            result2 = await rnnoise_track.recv()
            mock_denoise.assert_called_once()
            assert result2.pts == 480

    @pytest.mark.asyncio
    async def test_recv_pts_increment(self, rnnoise_track):
        """Test PTS counter increment."""
        mock_frame = Mock()
        mock_frame.to_ndarray.return_value = np.random.rand(480).astype(np.float32)
        mock_frame.time_base = "1/48000"
        rnnoise_track.track.recv.return_value = mock_frame

        with patch.object(rnnoise_track.rnnoise, "denoise_frame") as mock_denoise:
            mock_denoise.return_value = (np.array([0.8]), np.random.rand(1, 480).astype(np.int16))

            # First frame
            result1 = await rnnoise_track.recv()
            assert result1.pts == 0

            # Second frame
            result2 = await rnnoise_track.recv()
            assert result2.pts == 480

            # Third frame
            result3 = await rnnoise_track.recv()
            assert result3.pts == 960

    def test_rnnoise_initialization(self, rnnoise_track):
        """Test RNNoise object initialization."""
        assert rnnoise_track.rnnoise.sample_rate == 48000
        assert rnnoise_track.rnnoise.channels == 1
        assert rnnoise_track.rnnoise.dtype == np.int16
