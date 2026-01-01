from dotenv import load_dotenv

load_dotenv()


# CORS Origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:5173",
]

# Audio Settings (for future local implementation)
AUDIO_OUTPUT_FORMAT = "mp3_44100_128"
TEMP_AUDIO_PATH = "/tmp"

# Service Information
PROJECT_NAME = "OpenTalent - Avatar Service"
SERVICE_TITLE = PROJECT_NAME
SERVICE_DESCRIPTION = "Manages AI avatar interactions and rendering"
VERSION = "0.1.0"
SERVICE_VERSION = VERSION
