"""
Legacy Whisper STT Service - DEPRECATED

This module is deprecated and should not be used in production.
Use services.vosk_stt_service.VoskSTTService instead.

Reason: PyTorch and CUDA dependencies are not suitable for production environments.
Vosk provides lightweight, CPU-only inference with comparable accuracy.

Migration Path:
    from services.vosk_stt_service import VoskSTTService

    # Old:
    # stt = WhisperSTTService(model_size="base")
    # stt.load_model()
    # text = stt.transcribe_audio("audio.wav", language="en")

    # New:
    stt = VoskSTTService(
        model_path="models/vosk-model-small-en-us-0.15",
        sample_rate=16000
    )
    result = stt.transcribe_audio("audio.wav")
    text = result["text"]
    words = result["words"]  # Bonus: word-level timing!
"""

from loguru import logger
from typing import Optional
import warnings

warnings.warn(
    "WhisperSTTService is deprecated. Use VoskSTTService for production deployments.",
    DeprecationWarning,
    stacklevel=2,
)


class WhisperSTTService:
    """
    DEPRECATED: Whisper Speech-to-Text Service

    This service requires PyTorch and CUDA, which are not suitable for production.
    Use VoskSTTService instead for lightweight, CPU-only inference.
    """

    def __init__(self, model_size="base", device=None):
        logger.warning(
            "WhisperSTTService is deprecated. Use VoskSTTService for production. "
            "See services.vosk_stt_service for migration guide."
        )
        self.model_size = model_size
        self.model = None
        self.device = device or "cpu"
        logger.info(
            f"Initializing DEPRECATED Whisper STT (model: {model_size}, device: {self.device})"
        )

    def load_model(self):
        """Load Whisper model - DEPRECATED"""
        logger.error(
            "WhisperSTTService.load_model() is deprecated. "
            "PyTorch/Whisper dependencies are not installed in production. "
            "Use VoskSTTService instead."
        )
        return False

    def transcribe_audio(self, audio_file_path: str, language="en") -> Optional[str]:
        """Transcribe audio file to text - DEPRECATED"""
        logger.error(
            "WhisperSTTService.transcribe_audio() is deprecated. "
            "Use VoskSTTService.transcribe_audio() instead."
        )
        return None
