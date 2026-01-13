import asyncio
import logging
from aiortc import AudioStreamTrack
from av import AudioFrame
import numpy as np
from pyrnnoise import RNNoise

logger = logging.getLogger(__name__)


class RNNoiseTrack(AudioStreamTrack):
    """
    AudioStreamTrack that applies RNNoise noise suppression to incoming audio frames.
    Buffers audio to ensure 10ms (480 sample) frames for RNNoise processing.
    """

    def __init__(self, track):
        super().__init__()
        self.track = track
        self.rnnoise = RNNoise(sample_rate=48000)
        self.rnnoise.channels = 1  # Mono audio
        self.rnnoise.dtype = np.int16
        self.sample_rate = 48000
        self.frame_size = 480  # 10ms at 48kHz
        self.buffer = np.array([], dtype=np.int16)
        self.pts_counter = 0

    async def recv(self):
        frame = await self.track.recv()

        # Convert frame to numpy array
        audio_data = frame.to_ndarray()
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=0)  # Convert to mono if stereo

        # Convert to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)

        # Add to buffer
        self.buffer = np.concatenate([self.buffer, audio_int16])

        # Process complete frames
        if len(self.buffer) >= self.frame_size:
            # Take one frame
            frame_chunk = self.buffer[: self.frame_size]
            self.buffer = self.buffer[self.frame_size :]

            # Apply RNNoise
            try:
                # denoise_frame returns (speech_probs, denoised_frame)
                frame_2d = frame_chunk.reshape(1, -1)  # Add channel dimension
                speech_probs, denoised_2d = self.rnnoise.denoise_frame(frame_2d)

                # Extract the denoised audio (remove channel dimension)
                denoised = denoised_2d.flatten()

            except Exception as e:
                logger.error(f"RNNoise processing error: {e}")
                denoised = frame_chunk  # Fallback to original

            # Create new frame
            new_frame = AudioFrame.from_ndarray(
                denoised.reshape(1, -1), format="s16", layout="mono"
            )
            new_frame.sample_rate = self.sample_rate
            new_frame.pts = self.pts_counter
            new_frame.time_base = frame.time_base
            self.pts_counter += self.frame_size

            return new_frame
        else:
            # Not enough data, return silence or wait
            # For now, return a silence frame
            silence = np.zeros(self.frame_size, dtype=np.int16)
            silence_frame = AudioFrame.from_ndarray(
                silence.reshape(1, -1), format="s16", layout="mono"
            )
            silence_frame.sample_rate = self.sample_rate
            silence_frame.pts = self.pts_counter
            silence_frame.time_base = frame.time_base
            self.pts_counter += self.frame_size
            return silence_frame
