"""Voice Activity Detection (VAD) service for optimized STT processing.
Reduces unnecessary transcription during silence using webrtcvad.
"""

import logging
import os

import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# VAD configuration
USE_VAD = os.getenv("USE_VAD", "true").lower() == "true"
VAD_AGGRESSIVENESS = int(os.getenv("VAD_AGGRESSIVENESS", "2"))  # 0-3, higher = more aggressive
VAD_FRAME_DURATION_MS = int(os.getenv("VAD_FRAME_DURATION_MS", "30"))  # 10, 20, or 30 ms
VAD_SAMPLE_RATE = int(os.getenv("VAD_SAMPLE_RATE", "16000"))  # 8000, 16000, 32000, or 48000
VAD_SPEECH_THRESHOLD = float(os.getenv("VAD_SPEECH_THRESHOLD", "0.5"))  # 0.0-1.0


class VoiceActivityDetector:
    """Voice Activity Detection service using webrtcvad."""

    def __init__(self):
        self.use_vad = USE_VAD
        self.aggressiveness = VAD_AGGRESSIVENESS
        self.frame_duration_ms = VAD_FRAME_DURATION_MS
        self.sample_rate = VAD_SAMPLE_RATE
        self.speech_threshold = VAD_SPEECH_THRESHOLD

        self.vad = None
        self.speech_frames_buffer = []
        self.max_buffer_size = 10  # Keep last 10 frames for context

        if self.use_vad:
            self._initialize_vad()

    def _initialize_vad(self):
        """Initialize webrtcvad library."""
        try:
            import webrtcvad

            self.vad = webrtcvad.Vad(self.aggressiveness)
            logger.info(
                f"VAD initialized: aggressiveness={self.aggressiveness}, "
                f"frame_duration={self.frame_duration_ms}ms, "
                f"sample_rate={self.sample_rate}Hz"
            )
            return True
        except ImportError:
            logger.warning("webrtcvad not installed. Install with: pip install webrtcvad")
            logger.warning("Falling back to processing all audio (no VAD filtering)")
            self.use_vad = False
            self.vad = None
            return False
        except Exception as e:
            logger.error(f"Failed to initialize VAD: {e}")
            self.use_vad = False
            self.vad = None
            return False

    def is_speech(self, audio_chunk: bytes) -> bool:
        """Detect if audio chunk contains speech.

        Args:
            audio_chunk: Raw PCM audio bytes (16-bit signed integers)

        Returns:
            True if speech detected, False otherwise
        """
        if not self.use_vad or not self.vad:
            # No VAD available, assume all audio is speech
            return True

        try:
            # Ensure audio chunk is correct size for frame duration
            expected_samples = int(self.sample_rate * self.frame_duration_ms / 1000)
            expected_bytes = expected_samples * 2  # 16-bit = 2 bytes per sample

            # Pad or truncate to expected size
            if len(audio_chunk) < expected_bytes:
                audio_chunk = audio_chunk + b"\x00" * (expected_bytes - len(audio_chunk))
            elif len(audio_chunk) > expected_bytes:
                audio_chunk = audio_chunk[:expected_bytes]

            # Check VAD
            is_speech = self.vad.is_speech(audio_chunk, self.sample_rate)

            # Update buffer with sliding window
            self.speech_frames_buffer.append(is_speech)
            if len(self.speech_frames_buffer) > self.max_buffer_size:
                self.speech_frames_buffer.pop(0)

            # Calculate speech ratio in recent frames
            if len(self.speech_frames_buffer) >= 3:
                speech_ratio = sum(self.speech_frames_buffer) / len(self.speech_frames_buffer)
                return speech_ratio >= self.speech_threshold

            return is_speech

        except Exception as e:
            logger.warning(f"VAD error: {e}. Processing audio anyway.")
            return True

    def is_speech_numpy(self, audio_array: np.ndarray) -> bool:
        """Detect speech from numpy array.

        Args:
            audio_array: Numpy array of audio samples (float32 or int16)

        Returns:
            True if speech detected, False otherwise
        """
        if not self.use_vad:
            return True

        try:
            # Convert to 16-bit PCM bytes
            if audio_array.dtype in (np.float32, np.float64):
                # Convert float to int16
                audio_array = (audio_array * 32767).astype(np.int16)
            elif audio_array.dtype != np.int16:
                audio_array = audio_array.astype(np.int16)

            audio_bytes = audio_array.tobytes()
            return self.is_speech(audio_bytes)

        except Exception as e:
            logger.warning(f"VAD numpy conversion error: {e}")
            return True

    def reset_buffer(self):
        """Reset the speech frames buffer (useful for new sessions)."""
        self.speech_frames_buffer = []
        logger.debug("VAD buffer reset")

    def get_stats(self) -> dict:
        """Get VAD statistics."""
        if not self.speech_frames_buffer:
            return {
                "enabled": self.use_vad,
                "aggressiveness": self.aggressiveness,
                "frames_analyzed": 0,
                "speech_ratio": 0.0,
            }

        speech_count = sum(self.speech_frames_buffer)
        total_count = len(self.speech_frames_buffer)

        return {
            "enabled": self.use_vad,
            "aggressiveness": self.aggressiveness,
            "frames_analyzed": total_count,
            "speech_frames": speech_count,
            "speech_ratio": speech_count / total_count if total_count > 0 else 0.0,
            "sample_rate": self.sample_rate,
            "frame_duration_ms": self.frame_duration_ms,
        }

    def set_aggressiveness(self, level: int):
        """Adjust VAD aggressiveness level.

        Args:
            level: 0-3 (0 = least aggressive, 3 = most aggressive)
        """
        if level not in [0, 1, 2, 3]:
            logger.warning(f"Invalid VAD aggressiveness level: {level}. Must be 0-3.")
            return

        self.aggressiveness = level
        if self.vad:
            try:
                import webrtcvad

                self.vad = webrtcvad.Vad(level)
                logger.info(f"VAD aggressiveness updated to {level}")
            except Exception as e:
                logger.error(f"Failed to update VAD aggressiveness: {e}")


# Global VAD instance
vad_service = VoiceActivityDetector()
