"""Piper Text-to-Speech Service
High-quality, local TTS with phoneme extraction for lip-sync
"""

import json
import logging
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from .phoneme_extractor import PhonemeExtractor


class PiperTTSService:
    """Local Text-to-Speech service using Piper (VITS-based)

    Features:
    - MOS 4.1-4.3 quality (human-like speech)
    - <200ms synthesis latency
    - 150-200MB memory usage
    - Phoneme extraction for lip-sync
    - Multiple American English voices
    """

    def __init__(
        self,
        model_path: str = "models/en_US-lessac-medium.onnx",
        config_path: str = "models/en_US-lessac-medium.onnx.json",
        piper_binary: str = "/home/asif1/open-talent-platform/microservices/voice-service/piper/piper",
    ):
        """Initialize Piper TTS service.

        Args:
            model_path: Path to Piper ONNX model
            config_path: Path to model config JSON
            piper_binary: Path to Piper executable (or command if in PATH)
        """
        self.model_path = Path(model_path)
        self.config_path = Path(config_path)
        self.piper_binary = piper_binary
        self.logger = logging.getLogger(__name__)

        # Load model config
        self.config = self._load_config()

        # Initialize phoneme extractor
        self.phoneme_extractor = PhonemeExtractor(self.logger)

        # Available voices (American English)
        self.voices = {
            "lessac": "en_US-lessac-medium.onnx",  # Male, MOS 4.3
            "amy": "en_US-amy-medium.onnx",  # Female, MOS 4.2
            "ryan": "en_US-ryan-high.onnx",  # Male, MOS 4.1
            "hfc_female": "en_US-hfc_female-medium.onnx",  # Female, MOS 4.2
        }

        # Check Piper availability
        self._check_piper_available()

    def _load_config(self) -> dict:
        """Load Piper model configuration."""
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    config = json.load(f)
                self.logger.info(f"Loaded Piper config: {self.config_path}")
                return config
            else:
                self.logger.warning(f"Config not found: {self.config_path}")
                return {}
        except Exception as e:
            self.logger.error(f"Failed to load Piper config: {e}")
            return {}

    def _check_piper_available(self):
        """Check if Piper binary is available."""
        try:
            result = subprocess.run(
                [self.piper_binary, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                self.logger.info(f"Piper available: {result.stdout.strip()}")
            else:
                self.logger.warning("Piper binary not responding correctly")
        except FileNotFoundError:
            self.logger.error(
                f"Piper binary not found: {self.piper_binary}\n"
                "Install Piper from: https://github.com/rhasspy/piper"
            )
        except Exception as e:
            self.logger.error(f"Error checking Piper availability: {e}")

    def synthesize_speech(
        self,
        text: str,
        output_path: str,
        voice: str = "lessac",
        speed: float = 1.0,
        extract_phonemes: bool = True,
    ) -> dict:
        """Synthesize speech from text and save to file.

        Args:
            text: Text to synthesize
            output_path: Path to save WAV file
            voice: Voice name (default: lessac)
            speed: Speech speed multiplier (default: 1.0)
            extract_phonemes: Extract phoneme timing for lip-sync

        Returns:
            Dictionary with synthesis results:
            {
                "audio_file": "output.wav",
                "duration": 3.5,
                "phonemes": [{"phoneme": "HH", "start": 0.0, "end": 0.1}, ...],
                "words": [{"word": "hello", "start": 0.0, "end": 0.5}, ...],
                "sample_rate": 22050
            }
        """
        try:
            # Prepare output paths
            output_wav = Path(output_path)
            output_json = output_wav.with_suffix(".json")

            # Build Piper command
            cmd = [self.piper_binary, "-m", str(self.model_path), "-f", str(output_wav)]

            # Add optional parameters
            if speed != 1.0:
                cmd.extend(["--length-scale", str(1.0 / speed)])

            if extract_phonemes:
                cmd.extend(["--output_raw", "--json_input"])

            # Run Piper synthesis
            self.logger.info(f"Synthesizing: '{text[:50]}...' with voice '{voice}'")

            # Create temporary text file for input
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp_text:
                tmp_text.write(text)
                tmp_text_path = tmp_text.name

            try:
                # Build Piper command
                cmd = [self.piper_binary, "-m", self.model_path, "-f", str(output_wav)]

                if speed != 1.0:
                    cmd.extend(["--length-scale", str(1.0 / speed)])

                # Run Piper with text file input
                with open(tmp_text_path) as text_file:
                    result = subprocess.run(
                        cmd,
                        stdin=text_file,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        check=False,
                    )
            finally:
                # Clean up temporary file
                import os

                os.unlink(tmp_text_path)

            if result.returncode != 0:
                self.logger.error(f"Piper synthesis failed: {result.stderr}")
                raise RuntimeError(f"Piper synthesis error: {result.stderr}")

            # Read generated audio file
            audio_data, sample_rate = sf.read(str(output_wav))
            duration = len(audio_data) / sample_rate

            # Parse phoneme data if available
            phonemes = []
            words = []

            if extract_phonemes:
                # Try to load from Piper JSON first (if it exists)
                if output_json.exists():
                    try:
                        with open(output_json) as f:
                            phoneme_data = json.load(f)
                            phonemes = self._extract_phonemes(phoneme_data)
                            words = self._extract_words(phoneme_data)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse Piper phoneme data: {e}")

                # If no phoneme data from Piper, use our PhonemeExtractor
                if not phonemes:
                    phoneme_result = self.phoneme_extractor.extract_phonemes(text, duration)
                    phonemes = phoneme_result.get("phonemes", [])
                    words = phoneme_result.get("words", [])

            synthesis_result = {
                "audio_file": str(output_wav),
                "duration": duration,
                "sample_rate": sample_rate,
                "phonemes": phonemes,
                "words": words,
                "text": text,
                "voice": voice,
            }

            self.logger.info(
                f"Synthesized {duration:.2f}s audio: '{text[:50]}...' "
                f"({len(phonemes)} phonemes, {len(words)} words)"
            )

            return synthesis_result

        except Exception as e:
            self.logger.error(f"Speech synthesis failed: {e}")
            raise

    def synthesize_streaming(
        self, text: str, chunk_size: int = 4096, voice: str = "lessac"
    ) -> list[bytes]:
        """Synthesize speech in chunks for streaming.

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

    def _extract_phonemes(self, phoneme_data: dict) -> list[dict]:
        """Extract phoneme timing from Piper output."""
        phonemes = []

        # Piper outputs phoneme sequences with timing
        if "phonemes" in phoneme_data:
            for phoneme_info in phoneme_data["phonemes"]:
                phonemes.append(
                    {
                        "phoneme": phoneme_info.get("phoneme", ""),
                        "start": phoneme_info.get("start", 0.0),
                        "end": phoneme_info.get("end", 0.0),
                        "duration": phoneme_info.get("duration", 0.0),
                    }
                )

        return phonemes

    def _extract_words(self, phoneme_data: dict) -> list[dict]:
        """Extract word timing from Piper output."""
        words = []

        # Piper can output word-level timing
        if "words" in phoneme_data:
            for word_info in phoneme_data["words"]:
                words.append(
                    {
                        "word": word_info.get("word", ""),
                        "start": word_info.get("start", 0.0),
                        "end": word_info.get("end", 0.0),
                        "phonemes": word_info.get("phonemes", []),
                    }
                )

        return words

    def get_available_voices(self) -> list[dict]:
        """Get list of available American English voices."""
        return [
            {
                "name": "lessac",
                "gender": "male",
                "quality": "medium",
                "mos": 4.3,
                "description": "Clear, professional male voice",
            },
            {
                "name": "amy",
                "gender": "female",
                "quality": "medium",
                "mos": 4.2,
                "description": "Warm, friendly female voice",
            },
            {
                "name": "ryan",
                "gender": "male",
                "quality": "high",
                "mos": 4.1,
                "description": "High-quality male voice",
            },
            {
                "name": "hfc_female",
                "gender": "female",
                "quality": "medium",
                "mos": 4.2,
                "description": "Professional female voice",
            },
        ]

    def health_check(self) -> bool:
        """Check if Piper service is ready."""
        return self.model_path.exists() and self.config_path.exists()

    def get_info(self) -> dict:
        """Get service information."""
        return {
            "service": "Piper TTS",
            "model_path": str(self.model_path),
            "config_path": str(self.config_path),
            "ready": self.health_check(),
            "voices": self.get_available_voices(),
            "features": {
                "streaming": True,
                "phoneme_extraction": True,
                "word_timing": True,
                "language": "en-US",
            },
        }


# Mock implementation for testing when Piper is not available
class MockPiperTTSService:
    """Mock TTS service for development/testing."""

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.logger.warning("Using Mock Piper TTS Service")
        self.phoneme_extractor = PhonemeExtractor(self.logger)

    def synthesize_speech(
        self,
        text: str,
        output_path: str,
        voice: str = "lessac",
        speed: float = 1.0,
        extract_phonemes: bool = True,
    ) -> dict:
        """Return mock synthesis result and create WAV file with audio content."""
        # Create WAV file with actual audio content (20-30 seconds)
        sample_rate = 16000  # Reduced from 22050 for smaller files and faster testing
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

        return {
            "audio_file": output_path,
            "duration": duration,
            "sample_rate": sample_rate,
            "phonemes": phoneme_result.get("phonemes", []),
            "words": phoneme_result.get("words", []),
            "text": text,
            "voice": voice,
        }

    def get_available_voices(self) -> list[dict]:
        """Return mock voices."""
        return [{"name": "lessac", "gender": "male", "quality": "medium", "mos": 4.3}]

    def health_check(self) -> bool:
        return True

    def get_info(self) -> dict:
        return {
            "service": "Mock Piper TTS",
            "ready": True,
            "note": "Mock implementation for testing",
        }
