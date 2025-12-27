"""Avatar Rendering Service for OpenTalent Platform.

This service handles AI avatar video generation with lip-sync capabilities.
"""

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import aiohttp
import requests

logger = logging.getLogger(__name__)


class AvatarRenderingService:
    """Service for rendering AI avatar videos with audio."""

    def __init__(self, renderer_url: str = "http://localhost:3001"):
        self.renderer_url = renderer_url
        self.temp_dir = Path(tempfile.gettempdir()) / "OpenTalent_avatars"
        self.temp_dir.mkdir(exist_ok=True)

        # Test connection to renderer server
        self._test_renderer_connection()

    def _test_renderer_connection(self):
        """Test connection to avatar renderer server."""
        try:
            response = requests.get(urljoin(self.renderer_url, "/health"), timeout=5)
            if response.status_code == 200:
                logger.info(f"Connected to avatar renderer server at {self.renderer_url}")
            else:
                logger.warning(f"Avatar renderer server returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not connect to avatar renderer server: {e}")
            logger.info("Falling back to mock rendering mode")

    async def generate_avatar_video(
        self,
        audio_data: bytes,
        phonemes: list | None = None,
        duration: float | None = None,
        model: str = "face",
    ) -> bytes:
        """Generate avatar video with audio using Node.js renderer.

        Args:
            audio_data: Raw audio bytes
            phonemes: Phoneme timing data for lip-sync (optional)
            duration: Audio duration in seconds
            model: Avatar model preset ('face', 'metahuman', 'conductor')

        Returns:
            Video file as bytes
        """
        try:
            # If no phonemes provided, return mock video
            if not phonemes:
                logger.warning("No phonemes provided, using mock video generation")
                return await self._generate_mock_video(audio_data, duration)

            # Upload audio to temporary accessible URL
            audio_url = await self._upload_audio_temp(audio_data)

            # Prepare request data for Node.js renderer
            request_data = {
                "phonemes": phonemes,
                "audioUrl": audio_url,
                "model": model,
                "duration": duration,
            }

            # Call Node.js avatar renderer
            async with aiohttp.ClientSession() as session, session.post(
                urljoin(self.renderer_url, "/render/lipsync"),
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=300),  # 5 minute timeout
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Avatar renderer failed: {response.status} - {error_text}")
                    return await self._generate_mock_video(audio_data, duration)

                # Get video data
                video_data = await response.read()

                # Log processing info
                processing_time = response.headers.get("X-Processing-Time", "unknown")
                video_duration = response.headers.get("X-Video-Duration", "unknown")
                logger.info(
                    f"Avatar video rendered: {len(video_data)} bytes, "
                    f"duration: {video_duration}, processing: {processing_time}"
                )

                return video_data

        except Exception as e:
            logger.error(f"Failed to generate avatar video: {e}")
            # Fallback to mock video
            return await self._generate_mock_video(audio_data, duration)

    async def _upload_audio_temp(self, audio_data: bytes) -> str:
        """Upload audio to temporary accessible location."""
        # For now, save to local temp file and return file:// URL
        # In production, upload to cloud storage (S3, etc.)
        audio_file = self.temp_dir / f"temp_audio_{os.urandom(8).hex()}.wav"
        with open(audio_file, "wb") as f:
            f.write(audio_data)

        # Return file:// URL (Node.js can handle this)
        audio_url = f"file://{audio_file.absolute()}"

        # Schedule cleanup after some time
        asyncio.create_task(self._cleanup_file_later(audio_file, 300))  # 5 minutes

        return audio_url

    async def _cleanup_file_later(self, file_path: Path, delay_seconds: int):
        """Clean up temporary file after delay."""
        await asyncio.sleep(delay_seconds)
        try:
            file_path.unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")

    async def _generate_mock_video(self, audio_data: bytes, duration: float | None = None) -> bytes:
        """Generate a simple mock video when renderer is unavailable."""
        try:
            import numpy as np
            from moviepy import AudioFileClip, CompositeVideoClip, ImageClip
            from PIL import Image, ImageDraw

            # Create simple avatar image
            img = Image.new("RGB", (400, 600), color="lightblue")
            draw = ImageDraw.Draw(img)
            draw.rectangle([50, 200, 350, 400], fill="white")  # Face
            draw.ellipse([150, 250, 200, 300], fill="black")  # Left eye
            draw.ellipse([250, 250, 300, 300], fill="black")  # Right eye
            draw.arc([175, 325, 275, 375], start=0, end=180, fill="black", width=3)  # Mouth

            # Save audio to temp file
            audio_file = self.temp_dir / f"mock_audio_{os.urandom(8).hex()}.wav"
            with open(audio_file, "wb") as f:
                f.write(audio_data)

            # Create video clip
            image_clip = ImageClip(np.array(img), duration=duration or 5.0)
            audio_clip = AudioFileClip(str(audio_file))
            video = CompositeVideoClip([image_clip]).with_audio(audio_clip)

            # Export to temp file
            video_file = self.temp_dir / f"mock_video_{os.urandom(8).hex()}.mp4"
            video.write_videofile(str(video_file), fps=24, codec="libx264", audio_codec="aac")

            # Read video bytes
            with open(video_file, "rb") as f:
                video_bytes = f.read()

            # Cleanup
            audio_file.unlink(missing_ok=True)
            video_file.unlink(missing_ok=True)

            logger.info(f"Generated mock avatar video: {len(video_bytes)} bytes")
            return video_bytes

        except Exception as e:
            logger.error(f"Failed to generate mock video: {e}")
            raise

    async def get_avatar_info(self) -> dict[str, Any]:
        """Get avatar service information."""
        renderer_status = "unknown"
        try:
            response = requests.get(urljoin(self.renderer_url, "/health"), timeout=5)
            renderer_status = (
                "connected" if response.status_code == 200 else f"error_{response.status_code}"
            )
        except:
            renderer_status = "disconnected"

        return {
            "renderer_url": self.renderer_url,
            "renderer_status": renderer_status,
            "rendering_engine": "node.js + three.js + ai-orchestra-simulation",
            "lip_sync": "morph-target-based",
            "supported_formats": ["webm", "mp4"],
            "supported_models": ["face", "metahuman", "conductor"],
            "temp_dir": str(self.temp_dir),
        }
