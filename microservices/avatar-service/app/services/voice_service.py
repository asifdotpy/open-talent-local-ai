"""Voice generation service - Local implementation planned.

Currently provides mock responses. Local TTS/STT research and implementation
will be added in future updates.
"""


from app.models.voice import VoiceListResponse, VoiceRequest, VoiceResponse


class VoiceService:
    """Service for handling voice generation and management (local implementation planned)."""

    def __init__(self):
        """Initialize with mock implementation."""
        self.mock_available = True

    async def generate_irish_voice(self, request: VoiceRequest) -> VoiceResponse:
        """Mock voice generation - local implementation planned."""
        return VoiceResponse(
            success=False, error="Local voice generation not yet implemented. Research in progress."
        )

    async def list_available_voices(self) -> VoiceListResponse:
        """Mock voice listing - local implementation planned."""
        return VoiceListResponse(
            primary_irish_voice="Local TTS (planned)",
            irish_voices=[],
            total_voices=0,
            note="Local voice synthesis research in progress",
        )


# Global service instance
voice_service = VoiceService()
