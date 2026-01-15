"""Real Piper TTS service for avatar-service.
Generates actual audio with phoneme timing from text.
"""

from __future__ import annotations

import struct
import subprocess
import tempfile
from pathlib import Path


class PiperTTSService:
    """Local Piper text-to-speech service.

    Piper is a fast, offline, neural TTS system.
    Model: en_US-glow-tts (100M parameters, ONNX)

    Installation:
        pip install piper-tts onnxruntime librosa

        # Download model (auto on first use)
        echo "hello world" | piper --model en_US-glow-tts --output_file output.wav
    """

    def __init__(self, model_id: str = "en_US-glow-tts", use_gpu: bool = False):
        """Initialize Piper TTS service.

        Args:
            model_id: Piper model identifier (default: en_US-glow-tts)
            use_gpu: Use GPU if available (experimental)
        """
        self.model_id = model_id
        self.use_gpu = use_gpu
        self.sample_rate = 22050  # Piper default
        self._verify_piper_available()

    def _verify_piper_available(self) -> None:
        """Verify piper CLI is installed and accessible."""
        try:
            result = subprocess.run(["piper", "--version"], check=False, capture_output=True, timeout=5)
            if result.returncode != 0:
                raise RuntimeError("Piper CLI not found")
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            raise RuntimeError("Piper TTS not installed. Run: pip install piper-tts") from e

    def synthesize(self, text: str) -> tuple[bytes, int]:
        """Synthesize text to speech.

        Args:
            text: Text to synthesize

        Returns:
            (wav_bytes, sample_rate)

        Raises:
            ValueError: If text is empty
            RuntimeError: If piper subprocess fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        text = text[:1000]  # Cap at 1000 chars

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name

        try:
            # Call piper CLI
            cmd = [
                "piper",
                "--model",
                self.model_id,
                "--output_file",
                output_path,
            ]

            if self.use_gpu:
                cmd.append("--cuda")

            result = subprocess.run(cmd, check=False, input=text.encode("utf-8"), capture_output=True, timeout=30)

            if result.returncode != 0:
                raise RuntimeError(f"Piper failed: {result.stderr.decode()}")

            # Read generated WAV
            wav_bytes = Path(output_path).read_bytes()
            return wav_bytes, self.sample_rate

        finally:
            Path(output_path).unlink(missing_ok=True)

    def extract_phonemes(self, text: str) -> list[dict[str, any]]:
        """Extract phonemes from text without audio.

        Uses grapheme-to-phoneme (G2P) conversion.

        Args:
            text: Text to extract phonemes from

        Returns:
            List of {phoneme, duration_ms}
        """
        # Simple phoneme extraction using character-level approximation
        # For production, integrate proper G2P model
        phoneme_map = {
            "a": ("AE", 80),
            "e": ("EH", 80),
            "i": ("IH", 80),
            "o": ("AO", 80),
            "u": ("UH", 80),
            "s": ("S", 60),
            "t": ("T", 50),
            "n": ("N", 70),
            "r": ("R", 80),
            "l": ("L", 80),
        }

        phonemes = []
        for char in text.lower():
            if char in phoneme_map:
                phoneme, duration = phoneme_map[char]
                phonemes.append({"phoneme": phoneme, "duration_ms": duration})

        return phonemes if phonemes else [{"phoneme": "SILENCE", "duration_ms": 100}]

    def align_phonemes_with_audio(self, wav_bytes: bytes, text: str) -> list[dict[str, any]]:
        """Align phonemes with audio duration.

        Args:
            wav_bytes: WAV file bytes
            text: Original text

        Returns:
            List of {phoneme, start_ms, end_ms}
        """
        # Calculate total duration
        duration_ms = self._get_wav_duration_ms(wav_bytes)

        # Get phonemes
        phonemes = self.extract_phonemes(text)

        # Distribute phonemes evenly across duration
        if not phonemes:
            return []

        total_phoneme_duration = sum(p["duration_ms"] for p in phonemes)
        time_scale = duration_ms / max(total_phoneme_duration, 1)

        aligned = []
        current_time = 0

        for phoneme_data in phonemes:
            duration = phoneme_data["duration_ms"] * time_scale
            aligned.append(
                {
                    "phoneme": phoneme_data["phoneme"],
                    "start_ms": int(current_time),
                    "end_ms": int(current_time + duration),
                    "start_s": current_time / 1000,
                    "end_s": (current_time + duration) / 1000,
                }
            )
            current_time += duration

        return aligned

    @staticmethod
    def _get_wav_duration_ms(wav_bytes: bytes) -> float:
        """Extract duration from WAV file bytes.

        Parses WAV header to get sample count and sample rate.
        """
        try:
            # Read sample rate from WAV header (bytes 24-27, little-endian)
            struct.unpack("<I", wav_bytes[24:28])[0]

            # Read byte rate (bytes 28-31)
            byte_rate = struct.unpack("<I", wav_bytes[28:32])[0]

            # Read data chunk size (bytes 40-43, after "data" marker)
            # Find "data" chunk
            data_idx = wav_bytes.find(b"data") + 8
            data_size = struct.unpack("<I", wav_bytes[data_idx : data_idx + 4])[0]

            # Duration in seconds
            duration_s = data_size / byte_rate
            return duration_s * 1000  # Convert to milliseconds
        except (struct.error, IndexError, ZeroDivisionError):
            # Fallback: assume 22050 Hz sample rate, estimate from file size
            return (len(wav_bytes) / 88200) * 1000  # ~4 bytes per sample


class PhonemeService:
    """Phoneme extraction and alignment service.
    Uses Piper TTS for actual synthesis + alignment.
    """

    def __init__(self, tts_service: PiperTTSService | None = None):
        self.tts = tts_service or PiperTTSService()

    def synthesize_and_extract_phonemes(self, text: str) -> tuple[bytes, list[dict]]:
        """Synthesize text and extract aligned phonemes.

        Returns:
            (wav_bytes, aligned_phonemes)
        """
        # Generate audio
        wav_bytes, sample_rate = self.tts.synthesize(text)

        # Extract and align phonemes
        aligned_phonemes = self.tts.align_phonemes_with_audio(wav_bytes, text)

        return wav_bytes, aligned_phonemes

    def get_viseme_map(self) -> dict[str, str]:
        """Get phoneme-to-viseme mapping for lip-sync.

        Visemes are visual representations of phonemes.
        Multiple phonemes can map to same viseme.
        """
        return {
            # Vowels
            "AE": "viseme_A",  # /æ/ as in "cat"
            "EH": "viseme_E",  # /ɛ/ as in "bed"
            "IH": "viseme_I",  # /ɪ/ as in "bit"
            "AO": "viseme_O",  # /ɔ/ as in "dog"
            "UH": "viseme_U",  # /ʊ/ as in "book"
            "AA": "viseme_A",  # /ɑ/ as in "palm"
            "ER": "viseme_E",  # /ɜ/ as in "bird"
            "IY": "viseme_I",  # /i/ as in "beet"
            "OW": "viseme_O",  # /oʊ/ as in "go"
            "UW": "viseme_U",  # /u/ as in "boot"
            # Bilabial (both lips)
            "P": "viseme_P",  # /p/
            "B": "viseme_B",  # /b/
            "M": "viseme_M",  # /m/
            # Labiodental (lower lip + upper teeth)
            "F": "viseme_F",  # /f/
            "V": "viseme_V",  # /v/
            # Alveolar
            "T": "viseme_T",  # /t/
            "D": "viseme_D",  # /d/
            "N": "viseme_N",  # /n/
            "S": "viseme_S",  # /s/
            "Z": "viseme_Z",  # /z/
            "L": "viseme_L",  # /l/
            # Postalveolar
            "SH": "viseme_S",  # /ʃ/
            "ZH": "viseme_Z",  # /ʒ/
            "CH": "viseme_T",  # /tʃ/
            "JH": "viseme_D",  # /dʒ/
            # Velar
            "K": "viseme_K",  # /k/
            "G": "viseme_G",  # /ɡ/
            "NG": "viseme_N",  # /ŋ/
            # Glottals
            "HH": "viseme_A",  # /h/
            # Other
            "R": "viseme_R",  # /ɹ/
            "W": "viseme_U",  # /w/
            "Y": "viseme_I",  # /j/
            # Silence
            "SILENCE": "viseme_rest",
        }
