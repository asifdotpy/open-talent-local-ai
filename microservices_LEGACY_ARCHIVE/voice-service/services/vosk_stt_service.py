"""Vosk Speech-to-Text Service
Lightweight, local SST with streaming support and word-level timing.
"""

import json
import logging
from pathlib import Path

try:
    from vosk import KaldiRecognizer, Model

    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logging.warning("Vosk not installed. Install with: pip install vosk")

import numpy as np
import soundfile as sf


class VoskSTTService:
    """Local Speech-to-Text service using Vosk (Kaldi-based).

    Features:
    - 5-8% WER on American English
    - <100ms latency per 80ms chunk
    - 450-550MB memory usage
    - Word-level timing and confidence scores
    - Streaming support for real-time transcription
    """

    def __init__(self, model_path: str = "models/vosk-model-small-en-us-0.15", sample_rate: int = 16000):
        """Initialize Vosk SST service.

        Args:
            model_path: Path to Vosk model directory
            sample_rate: Audio sample rate (default: 16000 Hz)
        """
        self.model_path = Path(model_path)
        self.sample_rate = sample_rate
        self.model = None
        self.recognizer = None
        self.logger = logging.getLogger(__name__)

        if not VOSK_AVAILABLE:
            self.logger.error("Vosk not available. Please install: pip install vosk")
            raise ImportError("Vosk package not installed")

        # Load model on initialization
        self.load_model()

    def load_model(self):
        """Load Vosk model into memory."""
        try:
            if not self.model_path.exists():
                self.logger.error(f"Vosk model not found at: {self.model_path}")
                raise FileNotFoundError(
                    f"Vosk model not found. Please download from: "
                    f"https://alphacephei.com/vosk/models and extract to {self.model_path}"
                )

            self.logger.info(f"Loading Vosk model from: {self.model_path}")
            self.model = Model(str(self.model_path))
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)  # Enable word-level timing
            self.logger.info("Vosk model loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load Vosk model: {e}")
            return False

    def transcribe_audio(self, audio_file_path: str) -> dict:
        """Transcribe audio file to text with word-level timing.

        Args:
            audio_file_path: Path to audio file (WAV, MP3, etc.)

        Returns:
            Dictionary with transcription results:
            {
                "text": "full transcription",
                "words": [{"word": "hello", "start": 0.0, "end": 0.5, "conf": 0.95}, ...],
                "duration": 3.5,
                "confidence": 0.91
            }
        """
        try:
            # Read audio file and convert to 16kHz mono if needed
            audio_data, original_sr = sf.read(audio_file_path)

            # Convert stereo to mono if needed
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            # Resample if needed
            if original_sr != self.sample_rate:
                audio_data = self._resample_audio(audio_data, original_sr, self.sample_rate)

            # Convert to int16 format (Vosk expects this)
            audio_int16 = (audio_data * 32767).astype(np.int16)
            audio_bytes = audio_int16.tobytes()

            # Process audio through Vosk
            self.recognizer.AcceptWaveform(audio_bytes)
            result = json.loads(self.recognizer.FinalResult())

            # Extract text and word-level data
            transcription = {
                "text": result.get("text", ""),
                "words": [],
                "duration": len(audio_data) / self.sample_rate,
                "confidence": 0.0,
            }

            # Process word-level results
            if "result" in result:
                words_data = result["result"]
                total_confidence = 0.0

                for word_info in words_data:
                    word_entry = {
                        "word": word_info.get("word", ""),
                        "start": word_info.get("start", 0.0),
                        "end": word_info.get("end", 0.0),
                        "confidence": word_info.get("conf", 1.0),
                    }
                    transcription["words"].append(word_entry)
                    total_confidence += word_entry["confidence"]

                # Calculate average confidence
                if len(words_data) > 0:
                    transcription["confidence"] = total_confidence / len(words_data)

            self.logger.info(
                f"Transcribed {transcription['duration']:.2f}s audio: "
                f"'{transcription['text'][:50]}...' (confidence: {transcription['confidence']:.2f})"
            )

            return transcription

        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            raise

    def transcribe_streaming(self, audio_chunk: bytes) -> dict | None:
        """Process streaming audio chunk for real-time transcription.

        Args:
            audio_chunk: Audio data as bytes (int16 format)

        Returns:
            Partial transcription result or None if no words detected
        """
        try:
            if self.recognizer.AcceptWaveform(audio_chunk):
                result = json.loads(self.recognizer.Result())
                return self._format_result(result)
            else:
                # Partial result (word being spoken)
                partial = json.loads(self.recognizer.PartialResult())
                return {"text": partial.get("partial", ""), "partial": True}

        except Exception as e:
            self.logger.error(f"Streaming transcription failed: {e}")
            return None

    def reset_recognizer(self):
        """Reset recognizer state for new audio stream."""
        if self.recognizer:
            self.recognizer.Reset()

    def _format_result(self, result: dict) -> dict:
        """Format Vosk result into standardized output."""
        formatted = {"text": result.get("text", ""), "words": [], "partial": False}

        if "result" in result:
            for word_info in result["result"]:
                formatted["words"].append(
                    {
                        "word": word_info.get("word", ""),
                        "start": word_info.get("start", 0.0),
                        "end": word_info.get("end", 0.0),
                        "confidence": word_info.get("conf", 1.0),
                    }
                )

        return formatted

    def _resample_audio(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate.
        Simple linear interpolation for basic resampling.
        """
        if orig_sr == target_sr:
            return audio

        # Calculate resampling ratio
        duration = len(audio) / orig_sr
        target_length = int(duration * target_sr)

        # Linear interpolation
        indices = np.linspace(0, len(audio) - 1, target_length)
        resampled = np.interp(indices, np.arange(len(audio)), audio)

        return resampled

    def health_check(self) -> bool:
        """Check if Vosk service is ready."""
        return self.model is not None and self.recognizer is not None

    def get_info(self) -> dict:
        """Get service information."""
        return {
            "service": "Vosk STT",
            "model_path": str(self.model_path),
            "sample_rate": self.sample_rate,
            "ready": self.health_check(),
            "status": "ready" if self.health_check() else "not ready",
            "features": {
                "streaming": True,
                "word_timing": True,
                "confidence_scores": True,
                "language": "en-US",
            },
        }


# Mock implementation for testing when Vosk is not available
class MockVoskSTTService:
    """Mock SST service for development/testing."""

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.logger.warning("Using Mock Vosk STT Service")

    def transcribe_audio(self, audio_file_path: str) -> dict:
        """Return mock transcription."""
        return {
            "text": "This is a mock transcription for testing purposes",
            "words": [
                {"word": "This", "start": 0.0, "end": 0.2, "confidence": 0.95},
                {"word": "is", "start": 0.2, "end": 0.3, "confidence": 0.93},
                {"word": "a", "start": 0.3, "end": 0.4, "confidence": 0.92},
                {"word": "mock", "start": 0.4, "end": 0.6, "confidence": 0.94},
                {"word": "transcription", "start": 0.6, "end": 1.0, "confidence": 0.91},
            ],
            "duration": 2.0,
            "confidence": 0.93,
        }

    def health_check(self) -> bool:
        return True

    def get_info(self) -> dict:
        return {
            "service": "Mock Vosk STT",
            "ready": True,
            "note": "Mock implementation for testing",
        }
