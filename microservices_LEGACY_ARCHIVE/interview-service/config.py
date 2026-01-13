"""Configuration, constants, and logging setup for Interview service.
"""

import logging
import os
import sys


def setup_logging():
    """Configure structured logging for the service."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


logger = logging.getLogger("interview-service")

# Network timeout configuration
TIMEOUT_CONFIG = {
    "avatar_service": 15.0,  # Avatar service calls (rendering can take time)
    "voice_service": 10.0,  # Voice service calls
    "conversation_service": 5.0,  # Conversation service calls
    "health_check": 3.0,  # Health check calls (fast)
    "service_integration": 5.0,  # Inter-service calls
    "default": 10.0,  # Default timeout for other calls
}

# Local service configurations (no external APIs required)
OLLAMA_API_KEY = os.getenv(
    "OLLAMA_API_KEY", "1b55ff79559b4c218d015c0b7f3ddf8e.3peDt-lWL1ue6evEKFFxjQqk"
)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Define the static persona configuration for Interview (Local Implementation)
# Using local LLM and mock avatar/voice services for MVP
INTERVIEW_PERSONA_CONFIG = {
    "name": "Interview",
    "avatar_id": "local-avatar-001",  # Local avatar identifier
    "voice_id": "american-voice-001",  # American accent voice (local TTS planned)
    "llm_model": "granite4:350m-h",  # Local Ollama model
    "system_prompt": "You are Interview, an AI recruiter with OpenTalent. Always start by saying: 'Hi, I'm Interview, an AI recruiter with OpenTalent. I'm here to guide you through the interview process. This will be a competency-based interview, where you will also have the opportunity to ask questions.' Then conduct a professional competency-based interview with relevant technical and behavioral questions. Maintain a warm but professional tone throughout.",
    "max_session_length_seconds": 900,  # 15 minutes for a demo interview
}
