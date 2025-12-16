"""
Modular Text-to-Speech Service
Supports both local Piper TTS and OpenAI API TTS with unified interface
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import os

from .piper_tts_service import PiperTTSService, MockPiperTTSService

# Optional OpenAI import
try:
    from .openai_tts_service import OpenAITTSService, MockOpenAITTSService
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAITTSService = None
    MockOpenAITTSService = None


class ModularTTSService:
    """
    Modular TTS service that can use either local Piper or OpenAI API

    Features:
    - Unified interface for both local and API TTS
    - Automatic provider switching based on configuration
    - Cost tracking and performance monitoring
    - Phoneme extraction for lip-sync
    - Multiple voice options per provider
    """

    def __init__(
        self,
        provider: str = "local",  # "local" or "openai"
        # Piper (local) parameters
        piper_model_path: Optional[str] = None,
        piper_config_path: Optional[str] = None,
        piper_binary: Optional[str] = None,
        # OpenAI API parameters
        openai_api_key: Optional[str] = None,
        openai_model: Optional[str] = None,
        openai_voice: Optional[str] = None,
        openai_base_url: Optional[str] = None
    ):
        """
        Initialize modular TTS service.

        Args:
            provider: TTS provider ("local" for Piper, "openai" for OpenAI API)
            piper_model_path: Path to Piper ONNX model (for local provider)
            piper_config_path: Path to Piper config JSON (for local provider)
            piper_binary: Path to Piper executable (for local provider)
            openai_api_key: OpenAI API key (for openai provider)
            openai_model: OpenAI TTS model (for openai provider)
            openai_voice: OpenAI voice name (for openai provider)
            openai_base_url: Custom OpenAI API base URL (for openai provider)
        """
        self.logger = logging.getLogger(__name__)
        self.provider = provider.lower()

        # Initialize the appropriate TTS service
        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI TTS requested but openai package not installed. Install with: pip install openai")
            self.logger.info("Initializing OpenAI TTS service")
            self._tts_service = OpenAITTSService(
                api_key=openai_api_key,
                model=openai_model or "gpt-4o-mini-tts",
                voice=openai_voice or "alloy",
                base_url=openai_base_url
            )
        elif self.provider == "local":
            self.logger.info("Initializing local Piper TTS service")
            self._tts_service = PiperTTSService(
                model_path=piper_model_path or "models/en_US-lessac-medium.onnx",
                config_path=piper_config_path or "models/en_US-lessac-medium.onnx.json",
                piper_binary=piper_binary or "/home/asif1/talent-ai-platform/microservices/voice-service/piper/piper"
            )
        else:
            raise ValueError(f"Unsupported TTS provider: {provider}. Use 'local' or 'openai'")

        # Track usage for cost monitoring
        self.usage_stats = {
            "total_requests": 0,
            "total_characters": 0,
            "total_cost": 0.0,
            "provider": self.provider
        }

    def synthesize_speech(
        self,
        text: str,
        output_path: str,
        voice: str = None,
        speed: float = 1.0,
        extract_phonemes: bool = True
    ) -> Dict:
        """
        Synthesize speech from text using the configured provider.

        Args:
            text: Text to synthesize
            output_path: Path to save WAV file
            voice: Voice name (provider-specific)
            speed: Speech speed multiplier
            extract_phonemes: Extract phoneme timing for lip-sync

        Returns:
            Dictionary with synthesis results
        """
        # Update usage stats
        self.usage_stats["total_requests"] += 1
        self.usage_stats["total_characters"] += len(text)

        # Use provider-specific default voice if none specified
        if voice is None:
            if self.provider == "openai":
                voice = "alloy"
            else:  # local
                voice = "lessac"

        # Synthesize using the underlying service
        result = self._tts_service.synthesize_speech(
            text=text,
            output_path=output_path,
            voice=voice,
            speed=speed,
            extract_phonemes=extract_phonemes
        )

        # Track cost if available
        if "cost_estimate" in result:
            self.usage_stats["total_cost"] += result["cost_estimate"]

        self.logger.info(
            f"Modular TTS ({self.provider}): {result['duration']:.2f}s audio, "
            f"cost: ${result.get('cost_estimate', 0):.4f}"
        )

        return result

    def synthesize_streaming(
        self,
        text: str,
        chunk_size: int = 4096,
        voice: str = None
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
        # Use provider-specific default voice if none specified
        if voice is None:
            if self.provider == "openai":
                voice = "alloy"
            else:  # local
                voice = "lessac"

        return self._tts_service.synthesize_streaming(
            text=text,
            chunk_size=chunk_size,
            voice=voice
        )

    def get_available_voices(self) -> List[Dict]:
        """Get list of available voices for the current provider."""
        voices = self._tts_service.get_available_voices()

        # Add provider information to each voice
        for voice in voices:
            voice["provider"] = self.provider

        return voices

    def health_check(self) -> bool:
        """Check if the TTS service is ready."""
        return self._tts_service.health_check()

    def get_info(self) -> Dict:
        """Get service information."""
        base_info = self._tts_service.get_info()

        # Add modular service information
        modular_info = {
            "modular_service": "ModularTTSService",
            "provider": self.provider,
            "usage_stats": self.usage_stats.copy(),
            "supported_providers": ["local", "openai"],
            **base_info
        }

        return modular_info

    def get_usage_stats(self) -> Dict:
        """Get usage statistics for cost monitoring."""
        return self.usage_stats.copy()

    def reset_usage_stats(self):
        """Reset usage statistics."""
        self.usage_stats = {
            "total_requests": 0,
            "total_characters": 0,
            "total_cost": 0.0,
            "provider": self.provider
        }


# Mock implementation for testing
class MockModularTTSService:
    """Mock modular TTS service for development/testing."""

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.logger.warning("Using Mock Modular TTS Service")
        self._mock_service = MockPiperTTSService()  # Use Piper mock as base

        self.usage_stats = {
            "total_requests": 0,
            "total_characters": 0,
            "total_cost": 0.0,
            "provider": "mock"
        }

    def synthesize_speech(
        self,
        text: str,
        output_path: str,
        voice: str = "lessac",
        speed: float = 1.0,
        extract_phonemes: bool = True
    ) -> Dict:
        """Return mock synthesis result."""
        self.usage_stats["total_requests"] += 1
        self.usage_stats["total_characters"] += len(text)

        result = self._mock_service.synthesize_speech(
            text=text,
            output_path=output_path,
            voice=voice,
            speed=speed,
            extract_phonemes=extract_phonemes
        )

        # Add mock cost estimate
        result["cost_estimate"] = 0.0

        return result

    def synthesize_streaming(
        self,
        text: str,
        chunk_size: int = 4096,
        voice: str = "lessac"
    ) -> List[bytes]:
        """Return mock streaming chunks."""
        return self._mock_service.synthesize_streaming(
            text=text,
            chunk_size=chunk_size,
            voice=voice
        )

    def get_available_voices(self) -> List[Dict]:
        """Return mock voices."""
        voices = self._mock_service.get_available_voices()
        for voice in voices:
            voice["provider"] = "mock"
        return voices

    def health_check(self) -> bool:
        return True

    def get_info(self) -> Dict:
        base_info = self._mock_service.get_info()
        return {
            "modular_service": "MockModularTTSService",
            "provider": "mock",
            "usage_stats": self.usage_stats.copy(),
            **base_info
        }

    def get_usage_stats(self) -> Dict:
        return self.usage_stats.copy()

    def reset_usage_stats(self):
        self.usage_stats = {
            "total_requests": 0,
            "total_characters": 0,
            "total_cost": 0.0,
            "provider": "mock"
        }