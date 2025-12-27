"""Constants for the Voice Service.

Centralizes configuration, magic values, and static data used across the service.
"""

# Vosk Configuration
DEFAULT_VOSK_MODEL_PATH = "models/vosk-model-small-en-us-0.15"
DEFAULT_SAMPLE_RATE = 16000

# OpenAI TTS Configuration
DEFAULT_OPENAI_TTS_MODEL = "gpt-4o-mini-tts"
DEFAULT_OPENAI_TTS_VOICE = "alloy"

# Service Configuration
SERVICE_NAME = "Voice Service"
SERVICE_VERSION = "2.1.0"
SERVICE_DESCRIPTION = """
    Local Speech Processing Service for OpenTalent Platform

    **Capabilities:**
    - **Speech-to-Text (STT)**: Real-time transcription using Vosk
    - **Text-to-Speech (TTS)**: High-quality synthesis using Piper (local) or OpenAI API
    - **Voice Activity Detection (VAD)**: Silence filtering using Silero
    - **WebRTC Integration**: Real-time audio streaming for interviews
    - **WebSocket Streaming**: Bidirectional audio streaming

    **Service Stack:** Vosk + Modular TTS (Piper/OpenAI) + Silero + WebRTC + FastAPI
"""
