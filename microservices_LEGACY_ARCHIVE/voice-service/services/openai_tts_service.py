"""
OpenAI Text-to-Speech Service
Production TTS using OpenAI's gpt-4o-mini-tts model
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
import io

import numpy as np
import soundfile as sf
from openai import OpenAI

from .phoneme_extractor import PhonemeExtractor


class OpenAITTSService:
    """
    OpenAI Text-to-Speech service using gpt-4o-mini-tts model

    Features:
    - Cost-effective: $0.015 per minute
    - High quality: Natural-sounding speech
    - Phoneme extraction for lip-sync
    - Multiple voice options
    - Production-ready API integration
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini-tts",
        voice: str = "alloy",
        base_url: Optional[str] = None,
    ):
        """
        Initialize OpenAI TTS service.

        Args:
            api_key: OpenAI API key
            model: TTS model to use (default: gpt-4o-mini-tts)
            voice: Default voice (alloy, echo, fable, onyx, nova, shimmer)
            base_url: Custom API base URL (optional)
        """
        self.api_key = api_key
        self.model = model
        self.default_voice = voice
        self.logger = logging.getLogger(__name__)

        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key, base_url=base_url)

        # Initialize phoneme extractor for lip-sync
        self.phoneme_extractor = PhonemeExtractor(self.logger)

        # Available voices
        self.voices = {
            "alloy": {"gender": "neutral", "description": "Balanced, clear voice"},
            "echo": {"gender": "male", "description": "Warm, resonant male voice"},
            "fable": {"gender": "female", "description": "Expressive female voice"},
            "onyx": {"gender": "male", "description": "Deep, authoritative male voice"},
            "nova": {"gender": "female", "description": "Youthful, energetic female voice"},
            "shimmer": {"gender": "female", "description": "Bright, confident female voice"},
        }

        # Test connection
        self._test_connection()

    def _test_connection(self):
        """Test OpenAI API connection."""
        try:
            # Simple API test (list models)
            models = self.client.models.list()
            self.logger.info(f"OpenAI API connected. Available models: {len(models.data)}")
        except Exception as e:
            self.logger.error(f"OpenAI API connection failed: {e}")
            raise

    def synthesize_speech(
        self,
        text: str,
        output_path: str,
        voice: str = "alloy",
        speed: float = 1.0,
        extract_phonemes: bool = True,
    ) -> Dict:
        """
        Synthesize speech from text using OpenAI TTS API.

        Args:
            text: Text to synthesize
            output_path: Path to save WAV file
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed (0.25-4.0, default: 1.0)
            extract_phonemes: Extract phoneme timing for lip-sync

        Returns:
            Dictionary with synthesis results:
            {
                "audio_file": "output.wav",
                "duration": 3.5,
                "phonemes": [{"phoneme": "HH", "start": 0.0, "end": 0.1}, ...],
                "words": [{"word": "hello", "start": 0.0, "end": 0.5}, ...],
                "sample_rate": 24000,
                "cost_estimate": 0.001  # Cost in USD
            }
        """
        start_time = time.time()

        try:
            # Validate voice
            if voice not in self.voices:
                self.logger.warning(
                    f"Unknown voice '{voice}', using default '{self.default_voice}'"
                )
                voice = self.default_voice

            # Validate speed
            speed = max(0.25, min(4.0, speed))

            self.logger.info(
                f"Synthesizing with OpenAI TTS: '{text[:50]}...' (voice: {voice}, speed: {speed})"
            )

            # Call OpenAI TTS API
            response = self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="wav",  # WAV format for compatibility
            )

            # Save audio to file
            audio_bytes = b""
            for chunk in response.iter_bytes():
                audio_bytes += chunk

            with open(output_path, "wb") as f:
                f.write(audio_bytes)

            # Load audio to get metadata
            audio_data, sample_rate = sf.read(output_path)
            duration = len(audio_data) / sample_rate

            # Extract phonemes for lip-sync
            phonemes = []
            words = []

            if extract_phonemes:
                phoneme_result = self.phoneme_extractor.extract_phonemes(text, duration)
                phonemes = phoneme_result.get("phonemes", [])
                words = phoneme_result.get("words", [])

            # Calculate cost estimate ($0.015 per minute)
            cost_estimate = (duration / 60) * 0.015

            synthesis_result = {
                "audio_file": output_path,
                "duration": duration,
                "sample_rate": sample_rate,
                "phonemes": phonemes,
                "words": words,
                "text": text,
                "voice": voice,
                "speed": speed,
                "cost_estimate": round(cost_estimate, 4),
                "model": self.model,
            }

            processing_time = time.time() - start_time
            self.logger.info(
                f"OpenAI TTS completed in {processing_time:.2f}s: "
                f"{duration:.2f}s audio (${cost_estimate:.4f}) - '{text[:50]}...'"
            )

            return synthesis_result

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"OpenAI TTS failed after {processing_time:.2f}s: {e}")
            raise

    def synthesize_streaming(
        self, text: str, chunk_size: int = 4096, voice: str = "alloy"
    ) -> List[bytes]:
        """
        Synthesize speech in chunks for streaming.

        Args:
            text: Text to synthesize
            chunk_size: Audio chunk size in bytes
            voice: Voice name

        Returns:
            List of audio chunks (bytes)
        """
        try:
            # Generate full audio first
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                result = self.synthesize_speech(text, tmp.name, voice=voice, extract_phonemes=False)

                # Read audio and split into chunks
                audio_data, sample_rate = sf.read(result["audio_file"])
                audio_int16 = (audio_data * 32767).astype(np.int16)
                audio_bytes = audio_int16.tobytes()

                # Split into chunks
                chunks = [
                    audio_bytes[i : i + chunk_size] for i in range(0, len(audio_bytes), chunk_size)
                ]

                self.logger.info(f"Generated {len(chunks)} audio chunks")
                return chunks

        except Exception as e:
            self.logger.error(f"Streaming synthesis failed: {e}")
            raise

    def get_available_voices(self) -> List[Dict]:
        """Get list of available OpenAI TTS voices."""
        return [
            {
                "name": name,
                "gender": info["gender"],
                "description": info["description"],
                "provider": "OpenAI",
            }
            for name, info in self.voices.items()
        ]

    def health_check(self) -> bool:
        """Check if OpenAI TTS service is ready."""
        try:
            # Test API connectivity
            models = self.client.models.list()
            return len(models.data) > 0
        except Exception as e:
            self.logger.error(f"OpenAI TTS health check failed: {e}")
            return False

    def get_info(self) -> Dict:
        """Get service information."""
        return {
            "service": "OpenAI TTS",
            "model": self.model,
            "default_voice": self.default_voice,
            "ready": self.health_check(),
            "voices": self.get_available_voices(),
            "pricing": {"per_minute": 0.015, "currency": "USD"},
            "features": {
                "streaming": True,
                "phoneme_extraction": True,
                "word_timing": True,
                "language": "en-US",
                "speed_control": True,
            },
        }


# Mock implementation for testing when OpenAI API is not available
class MockOpenAITTSService:
    """Mock OpenAI TTS service for development/testing."""

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.logger.warning("Using Mock OpenAI TTS Service")
        self.phoneme_extractor = PhonemeExtractor(self.logger)

    def synthesize_speech(
        self,
        text: str,
        output_path: str,
        voice: str = "alloy",
        speed: float = 1.0,
        extract_phonemes: bool = True,
    ) -> Dict:
        """Return mock synthesis result and create WAV file with audio content."""
        # Create WAV file with actual audio content (20-30 seconds)
        sample_rate = 24000  # OpenAI uses 24kHz
        # Generate duration based on text length, minimum 2 seconds, maximum 30 seconds
        word_count = len(text.split())
        base_duration = word_count * 0.5  # 0.5s per word
        duration = min(max(base_duration, 2.0), 30.0)  # min 2s, max 30s

        # Generate a simple sine wave instead of silence for testing
        import numpy as np

        t = np.linspace(0, duration, int(sample_rate * duration), False)
        # Create a 440Hz sine wave (A note) with some amplitude variation
        frequency = 440.0
        audio_data = 0.3 * np.sin(frequency * 2 * np.pi * t) * (0.8 + 0.2 * np.sin(2 * np.pi * t))

        sf.write(output_path, audio_data, sample_rate)

        # Extract phonemes using PhonemeExtractor
        phoneme_result = self.phoneme_extractor.extract_phonemes(text, duration)

        # Mock cost estimate ($0.015 per minute)
        cost_estimate = (duration / 60) * 0.015

        return {
            "audio_file": output_path,
            "duration": duration,
            "sample_rate": sample_rate,
            "phonemes": phoneme_result.get("phonemes", []),
            "words": phoneme_result.get("words", []),
            "text": text,
            "voice": voice,
            "speed": speed,
            "cost_estimate": round(cost_estimate, 4),
            "model": "gpt-4o-mini-tts",
        }

    def get_available_voices(self) -> List[Dict]:
        """Return mock voices."""
        return [
            {
                "name": "alloy",
                "gender": "neutral",
                "description": "Balanced voice",
                "provider": "OpenAI",
            }
        ]

    def health_check(self) -> bool:
        return True

    def get_info(self) -> Dict:
        return {
            "service": "Mock OpenAI TTS",
            "ready": True,
            "note": "Mock implementation for testing",
        }
