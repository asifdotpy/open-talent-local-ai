"""
Configuration settings for the Avatar Service.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# CORS Origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080", 
    "http://localhost:8081",
    "http://localhost:5173"
]

# Audio Settings (for future local implementation)
AUDIO_OUTPUT_FORMAT = "mp3_44100_128"
TEMP_AUDIO_PATH = "/tmp"

# Service Information
SERVICE_TITLE = "TalentAI - Avatar Service"
SERVICE_DESCRIPTION = "Manages AI avatar interactions and rendering"
SERVICE_VERSION = "0.1.0"