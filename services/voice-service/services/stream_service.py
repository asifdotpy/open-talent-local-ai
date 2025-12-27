"""Unified Streaming Service for Voice Service
Provides WebSocket-based real-time audio processing.
"""

import asyncio
import builtins
import contextlib
import logging
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class UnifiedStreamService:
    """Unified streaming service for real-time voice processing.

    Handles WebSocket connections for STT and TTS streaming.
    """

    def __init__(self, stt_service, tts_service, vad_service=None):
        self.stt_service = stt_service
        self.tts_service = tts_service
        self.vad_service = vad_service
        self.active_connections = set()
        self.logger = logging.getLogger(__name__)

    async def handle_stt_stream(self, websocket: WebSocket, use_vad: bool = True):
        """Processes real-time audio streams from a WebSocket for Speech-to-Text (STT).

        Uses optional Voice Activity Detection (VAD) to skip silence and sends
        transcription results (partial or final) back to the client.

        Args:
            websocket: The active WebSocket connection to manage.
            use_vad: Whether to apply VAD to the incoming audio stream.
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        self.logger.info("STT streaming connection established")

        try:
            while True:
                # Receive audio chunk
                audio_chunk = await websocket.receive_bytes()

                # Apply VAD if enabled and available
                if use_vad and self.vad_service and hasattr(self.vad_service, "is_speech"):
                    if not self.vad_service.is_speech(audio_chunk):
                        continue  # Skip silence

                # Process with STT
                if hasattr(self.stt_service, "transcribe_streaming"):
                    result = self.stt_service.transcribe_streaming(audio_chunk)
                    if result:
                        await websocket.send_json(
                            {
                                "type": "partial" if result.get("partial") else "final",
                                "text": result.get("text", ""),
                                "confidence": result.get("confidence", 0.0),
                                "words": result.get("words", []),
                            }
                        )
                # Fallback to file-based processing for large chunks
                elif len(audio_chunk) > 16000:  # ~1 second
                    import os
                    import tempfile

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp.write(audio_chunk)
                        tmp_path = tmp.name

                    try:
                        result = self.stt_service.transcribe_audio(tmp_path)
                        await websocket.send_json(
                            {
                                "type": "transcription",
                                "text": result.get("text", ""),
                                "confidence": result.get("confidence", 0.0),
                                "words": result.get("words", []),
                            }
                        )
                    finally:
                        os.unlink(tmp_path)

        except WebSocketDisconnect:
            self.logger.info("STT streaming connection closed")
        except Exception as e:
            self.logger.error(f"STT streaming error: {e}")
            with contextlib.suppress(builtins.BaseException):
                await websocket.send_json({"error": str(e)})
        finally:
            self.active_connections.discard(websocket)

    async def handle_tts_stream(self, websocket: WebSocket):
        """Processes real-time text requests from a WebSocket for Text-to-Speech (TTS).

        Synthesizes speech from incoming text data and streams the resulting audio
        chunks back to the client in real-time.

        Args:
            websocket: The active WebSocket connection to manage.
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        self.logger.info("TTS streaming connection established")

        try:
            while True:
                # Receive text data
                text_data = await websocket.receive_json()
                text = text_data.get("text", "")
                voice = text_data.get("voice", "lessac")

                if not text:
                    continue

                # Generate and stream audio
                import os
                import tempfile

                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    output_path = tmp.name

                try:
                    # Generate TTS
                    result = self.tts_service.synthesize_speech(
                        text=text,
                        output_path=output_path,
                        voice=voice,
                        extract_phonemes=False,  # Skip for speed
                    )

                    # Read and stream audio in chunks
                    with open(output_path, "rb") as f:
                        while True:
                            chunk = f.read(4096)  # 4KB chunks
                            if not chunk:
                                break
                            await websocket.send_bytes(chunk)
                            await asyncio.sleep(0.01)  # Small delay to prevent flooding

                    # Send end marker
                    await websocket.send_json({"type": "end", "duration": result["duration"]})

                finally:
                    if os.path.exists(output_path):
                        os.unlink(output_path)

        except WebSocketDisconnect:
            self.logger.info("TTS streaming connection closed")
        except Exception as e:
            self.logger.error(f"TTS streaming error: {e}")
            with contextlib.suppress(builtins.BaseException):
                await websocket.send_json({"error": str(e)})
        finally:
            self.active_connections.discard(websocket)

    def get_connection_count(self) -> int:
        """Get number of active streaming connections."""
        return len(self.active_connections)

    async def broadcast_status(self, message: dict[str, Any]):
        """Broadcast status message to all active connections."""
        disconnected = set()
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except:
                disconnected.add(ws)

        # Clean up disconnected clients
        self.active_connections -= disconnected
