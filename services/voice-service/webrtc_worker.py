# aiortc-based WebRTC worker for Voice Service
# Connects to interview-service signaling server and handles audio streams

import asyncio
import json
import logging
import os
import tempfile
import time
from fractions import Fraction
from typing import Annotated

import aiohttp
import httpx
import numpy as np
import soundfile as sf
from aiortc import (
    MediaStreamTrack,
    RTCConfiguration,
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.codecs.opus import OpusEncoder
from aiortc.contrib.media import MediaBlackhole, MediaStreamError
from av import AudioFrame
from fastapi import Body, FastAPI, status

# --- Constants ---
HTTP_OK = status.HTTP_200_OK
HTTP_BAD_REQUEST = status.HTTP_400_BAD_REQUEST
HTTP_NOT_FOUND = status.HTTP_404_NOT_FOUND
HTTP_INTERNAL_SERVER_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR

DEFAULT_SAMPLE_RATE = 16000
VOSK_MODEL_SAMPLE_RATE = 16000
SILERO_MODEL_SAMPLE_RATE = 16000
WEBRTC_AUDIO_SAMPLE_RATE = 48000
OPUS_PREFERRED_SAMPLE_RATE = 48000
AUDIO_CHUNK_DURATION_MS = 200

# Import voice services
try:
    from services.audio_processing_service import RNNoiseTrack
    from services.piper_tts_service import PiperTTSService
    from services.silero_vad_service import SileroVADService
    from services.vosk_stt_service import VoskSTTService

    STT_TTS_AVAILABLE = True
except ImportError:
    STT_TTS_AVAILABLE = False
    SileroVADService = None
    RNNoiseTrack = None
    logging.warning("Voice services not available. Using mock implementation.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuration
SIGNALING_URL = os.getenv("SIGNALING_URL", "ws://localhost:8005/webrtc/signal")
CONVERSATION_SERVICE_URL = os.getenv("CONVERSATION_SERVICE_URL", "http://localhost:8003")
INTERVIEW_SERVICE_URL = os.getenv("INTERVIEW_SERVICE_URL", "http://localhost:8004")
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

# Audio Pipeline Configuration
OPUS_BITRATE = int(os.getenv("OPUS_BITRATE", "64000"))  # 64kbps default (32-128kbps range)
OPUS_COMPLEXITY = int(os.getenv("OPUS_COMPLEXITY", "8"))  # 0-10, higher = better quality
ENABLE_AEC = os.getenv("ENABLE_AEC", "false").lower() == "true"
AUDIO_SAMPLE_RATE = WEBRTC_AUDIO_SAMPLE_RATE  # Opus optimal sample rate
AUDIO_CHANNELS = 1  # Mono for voice processing

# Performance monitoring
audio_pipeline_stats = {
    "rnnoise_frames_processed": 0,
    "opus_frames_encoded": 0,
    "total_latency_ms": 0,
    "avg_latency_ms": 0,
    "last_snr_improvement": 0.0,
}

# Initialize STT/TTS services
if STT_TTS_AVAILABLE and not USE_MOCK:
    stt_service = VoskSTTService(
        model_path=os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15"),
        sample_rate=VOSK_MODEL_SAMPLE_RATE,
    )
    tts_service = PiperTTSService(
        model_path=os.getenv("PIPER_MODEL_PATH", "models/en_US-lessac-medium.onnx"),
        config_path=os.getenv("PIPER_CONFIG_PATH", "models/en_US-lessac-medium.onnx.json"),
    )
    vad_service = SileroVADService(
        model_path=os.getenv("SILERO_MODEL_PATH", "models/silero_vad.onnx"),
        sample_rate=SILERO_MODEL_SAMPLE_RATE,
        threshold=0.5,
    )
else:
    stt_service = None
    tts_service = None
    vad_service = None
    logger.warning("Running in mock mode or services not available")

# Active peer connections by session_id
active_connections: dict[str, RTCPeerConnection] = {}
active_workers: dict[str, "VoiceServiceWorker"] = {}


class ConversationClient:
    """Client for communicating with the conversation service."""

    def __init__(self, base_url: str = CONVERSATION_SERVICE_URL):
        """Initialize the ConversationClient."""
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def send_transcript(self, session_id: str, transcript: str, metadata: dict | None = None) -> dict | None:
        """Send a transcript to the conversation service for processing."""
        try:
            response = await self.client.post(
                f"{self.base_url}/conversation/message",
                json={
                    "session_id": session_id,
                    "message": transcript,
                    "message_type": "transcript",
                    "metadata": metadata or {},
                },
            )

            if response.status_code == HTTP_OK:
                return response.json()
            else:
                logger.error(f"Conversation service error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Failed to send transcript to conversation service: {e}")
            return None

    async def start_conversation(self, session_id: str, job_description: str) -> bool:
        """Start a conversation session."""
        try:
            response = await self.client.post(
                f"{self.base_url}/conversation/start",
                json={
                    "session_id": session_id,
                    "job_description": job_description,
                    "interview_type": "technical",
                    "tone": "professional",
                },
            )

            return response.status_code == HTTP_OK

        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class InterviewServiceClient:
    """Client for communicating with the interview service for live transcription."""

    def __init__(self, base_url: str = INTERVIEW_SERVICE_URL):
        """Initialize the InterviewServiceClient."""
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=5.0)

    async def send_transcription_segment(
        self,
        room_id: str,
        session_id: str,
        participant_id: str,
        text: str,
        start_time: float,
        end_time: float,
        confidence: float,
        is_final: bool = False,
        words: list | None = None,
    ) -> bool:
        """Send transcription segment to interview service for live display."""
        try:
            segment_data = {
                "text": text,
                "start_time": start_time,
                "end_time": end_time,
                "confidence": confidence,
                "is_final": is_final,
                "words": words or [],
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/rooms/{room_id}/transcription",
                json={"segment": segment_data, "session_id": session_id, "participant_id": participant_id},
            )

            if response.status_code == HTTP_OK:
                logger.debug(f"Sent transcription segment to interview service: '{text[:30]}...'")
                return True
            else:
                logger.error(
                    f"Failed to send transcription to interview service: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"Error sending transcription to interview service: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global clients
conversation_client = ConversationClient()
interview_client = InterviewServiceClient()


class EnhancedAudioPipeline(MediaStreamTrack):
    """Enhanced audio processing pipeline: RNNoise → Opus Encoder → AEC (future).

    Provides optimized audio quality for WebRTC voice processing.
    """

    kind = "audio"

    def __init__(self, track: MediaStreamTrack):
        """Initialize the EnhancedAudioPipeline."""
        super().__init__()
        self.track = track
        self.opus_encoder = None
        self.sample_rate = AUDIO_SAMPLE_RATE
        self.channels = AUDIO_CHANNELS
        self.pts_counter = 0

        # Initialize Opus encoder
        try:
            self.opus_encoder = OpusEncoder()
            self.opus_encoder.sample_rate = self.sample_rate
            self.opus_encoder.channels = self.channels
            self.opus_encoder.bitrate = OPUS_BITRATE
            self.opus_encoder.complexity = OPUS_COMPLEXITY
            logger.info(f"Opus encoder initialized: {OPUS_BITRATE}bps, complexity {OPUS_COMPLEXITY}")
        except Exception as e:
            logger.error(f"Failed to initialize Opus encoder: {e}")
            self.opus_encoder = None

        # Initialize RNNoise if available
        self.rnnoise_track = None
        if RNNoiseTrack:
            self.rnnoise_track = RNNoiseTrack(track)
            logger.info("RNNoise noise suppression enabled")
        else:
            logger.warning("RNNoise not available, using raw audio")

    async def recv(self):
        """Process audio through enhanced pipeline: RNNoise → Opus → AEC."""
        start_time = time.time()

        try:
            # Get audio frame (from RNNoise if available, otherwise raw)
            if self.rnnoise_track:
                frame = await self.rnnoise_track.recv()
                audio_pipeline_stats["rnnoise_frames_processed"] += 1
            else:
                frame = await self.track.recv()

            # Convert to numpy array for processing
            audio_data = frame.to_ndarray()

            # Ensure proper format (mono, correct sample rate)
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=0)  # Convert to mono

            # Resample if needed (Opus works best at 48kHz)
            if frame.sample_rate != self.sample_rate:
                # Simple resampling (in production, use better resampling)
                ratio = self.sample_rate / frame.sample_rate
                new_length = int(len(audio_data) * ratio)
                audio_data = np.interp(
                    np.linspace(0, len(audio_data), new_length), np.arange(len(audio_data)), audio_data
                )

            # Apply Opus encoding if available
            if self.opus_encoder:
                try:
                    # Convert to int16 for Opus
                    audio_int16 = (audio_data * 32767).astype(np.int16)

                    # Encode with Opus
                    encoded_data = self.opus_encoder.encode(audio_int16.tobytes())

                    # Decode back to PCM for WebRTC (Opus is not directly supported in aiortc tracks)
                    # For now, keep as PCM but log the compression ratio
                    compression_ratio = len(encoded_data) / len(audio_int16.tobytes())
                    audio_pipeline_stats["opus_frames_encoded"] += 1

                    logger.debug(f"Opus compression ratio: {compression_ratio:.2f}")

                except Exception as e:
                    logger.error(f"Opus encoding error: {e}")
                    # Fallback to original audio

            # Create new frame with processed audio
            new_frame = AudioFrame.from_ndarray(audio_data.reshape(1, -1), format="flt", layout="mono")
            new_frame.sample_rate = self.sample_rate
            new_frame.pts = self.pts_counter
            new_frame.time_base = Fraction(1, self.sample_rate)
            self.pts_counter += len(audio_data)

            # Track latency
            latency_ms = (time.time() - start_time) * 1000
            audio_pipeline_stats["total_latency_ms"] += latency_ms
            audio_pipeline_stats["avg_latency_ms"] = audio_pipeline_stats["total_latency_ms"] / max(
                1, audio_pipeline_stats["rnnoise_frames_processed"]
            )

            return new_frame

        except Exception as e:
            logger.error(f"Enhanced audio pipeline error: {e}")
            # Fallback to original frame
            return await self.track.recv()


class AudioStreamTrack(MediaStreamTrack):
    """Audio track that processes incoming audio chunks for STT."""

    kind = "audio"

    def __init__(
        self, track: MediaStreamTrack, datachannel, session_id: str, room_id: str = None, participant_id: str = None
    ):
        super().__init__()
        # Use enhanced audio pipeline instead of direct RNNoise
        self.track = EnhancedAudioPipeline(track)
        self.datachannel = datachannel
        self.session_id = session_id
        self.room_id = room_id or session_id  # Use session_id as fallback
        self.participant_id = participant_id or "candidate"  # Default participant
        self.conversation_client = conversation_client
        self.interview_client = interview_client
        self.buffer = bytearray()
        self.sample_rate = DEFAULT_SAMPLE_RATE
        self.chunk_duration_ms = AUDIO_CHUNK_DURATION_MS  # Process every 200ms
        self.bytes_per_chunk = int(self.sample_rate * 2 * self.chunk_duration_ms / 1000)

        # Note: Echo Cancellation (AEC) is handled client-side in the browser WebRTC implementation
        # For server-side AEC fallback, consider integrating SpeexDSP if client-side AEC is insufficient

        if stt_service:
            stt_service.reset_recognizer()

    async def recv(self):
        """Receive and process audio frame."""
        try:
            frame = await self.track.recv()

            # Convert frame to numpy array (16-bit PCM)
            audio_data = frame.to_ndarray()

            # Ensure mono and correct sample rate
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=0)

            # Convert to int16 bytes for Vosk
            audio_int16 = (audio_data * 32767).astype(np.int16)
            audio_bytes = audio_int16.tobytes()

            # Add to buffer
            self.buffer.extend(audio_bytes)

            # Process when we have enough data
            if len(self.buffer) >= self.bytes_per_chunk:
                chunk = bytes(self.buffer[: self.bytes_per_chunk])
                self.buffer = self.buffer[self.bytes_per_chunk :]

                # Run STT on chunk
                asyncio.create_task(self._process_stt_chunk(chunk))

            return frame

        except MediaStreamError:
            raise

    async def _process_stt_chunk(self, audio_chunk: bytes):
        """Process audio chunk through STT and send results via DataChannel and to interview service."""
        if not stt_service or not self.datachannel:
            return

        try:
            # Check if audio contains speech using VAD
            if vad_service and not vad_service.is_speech(audio_chunk):
                # Skip STT processing for silence
                logger.debug("VAD: Silence detected, skipping STT processing")
                return

            # Process speech with STT
            result = stt_service.transcribe_streaming(audio_chunk)

            if result:
                current_time = asyncio.get_event_loop().time()

                if result.get("partial"):
                    # Send partial transcript to interview service for live display
                    await self.interview_client.send_transcription_segment(
                        room_id=self.room_id,
                        session_id=self.session_id,
                        participant_id=self.participant_id,
                        text=result["text"],
                        start_time=current_time,
                        end_time=current_time + 0.2,  # 200ms chunk
                        confidence=result.get("confidence", 0.5),
                        is_final=False,
                        words=result.get("words", []),
                    )

                    # Send partial transcript via DataChannel
                    message = {
                        "type": "transcript.partial",
                        "text": result["text"],
                        "session_id": self.session_id,
                        "timestamp": current_time,
                    }
                    self.datachannel.send(json.dumps(message))
                else:
                    # Send final transcript to conversation service and interview service
                    await self._send_to_conversation_service(result, current_time)

        except Exception as e:
            logger.error(f"STT processing error: {e}")

    async def _send_to_conversation_service(self, stt_result: dict, current_time: float):
        """Send final transcript to conversation service for adaptive response and to interview service for display."""
        try:
            # Send final transcription to interview service
            await self.interview_client.send_transcription_segment(
                room_id=self.room_id,
                session_id=self.session_id,
                participant_id=self.participant_id,
                text=stt_result["text"],
                start_time=current_time - 1.0,  # Estimate start time (last 1 second)
                end_time=current_time,
                confidence=stt_result.get("confidence", 0.8),
                is_final=True,
                words=stt_result.get("words", []),
            )

            # Send transcript to conversation service
            response = await self.conversation_client.send_transcript(
                session_id=self.session_id,
                transcript=stt_result["text"],
                metadata={
                    "confidence": stt_result.get("confidence", 0.0),
                    "words": stt_result.get("words", []),
                    "timestamp": current_time,
                },
            )

            # Send transcript to browser via DataChannel
            message = {
                "type": "transcript.final",
                "text": stt_result["text"],
                "words": stt_result.get("words", []),
                "confidence": stt_result.get("confidence", 0.0),
                "session_id": self.session_id,
                "timestamp": current_time,
            }
            self.datachannel.send(json.dumps(message))

            # If conversation service provided a response, generate TTS
            if response and response.get("should_speak", True):
                await self._generate_tts_response(response["response_text"])

            logger.info(f"STT final: {stt_result['text'][:50]}...")

        except Exception as e:
            logger.error(f"Failed to send transcript to services: {e}")

    async def _generate_tts_response(self, text: str):
        """Generate TTS response for conversation service output."""
        try:
            # Send TTS request to our own service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8002/webrtc/tts", json={"session_id": self.session_id, "text": text}, timeout=5.0
                )

                if response.status_code == 200:
                    logger.info(f"TTS response generated: {text[:50]}...")
                else:
                    logger.error(f"TTS request failed: {response.status_code}")

        except Exception as e:
            logger.error(f"TTS generation error: {e}")


class TTSAudioTrack(MediaStreamTrack):
    """Generate audio track from TTS synthesis."""

    kind = "audio"

    def __init__(self, text: str, session_id: str):
        super().__init__()
        self.session_id = session_id
        self.audio_frames = []
        self.frame_index = 0
        self.sample_rate = DEFAULT_SAMPLE_RATE  # Mock TTS default
        self.generating = False

        # Generate TTS audio in background
        asyncio.create_task(self._generate_audio(text))

    async def _generate_audio(self, text: str):
        """Generate audio using Piper TTS."""
        if not tts_service:
            logger.warning("TTS service not available")
            return

        try:
            self.generating = True

            # Create temporary file for TTS output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                output_path = tmp.name

            # Synthesize speech
            tts_service.synthesize_speech(
                text=text,
                output_path=output_path,
                extract_phonemes=False,  # Skip phonemes for speed
            )

            # Read generated audio and convert to frames
            audio_data, sr = sf.read(output_path)

            # Convert to frames (20ms each)
            samples_per_frame = int(sr * 0.02)
            for i in range(0, len(audio_data), samples_per_frame):
                chunk = audio_data[i : i + samples_per_frame]
                if len(chunk) > 0:
                    self.audio_frames.append(chunk)

            # Cleanup
            os.unlink(output_path)
            self.generating = False

            logger.info(f"TTS generated {len(self.audio_frames)} frames for: {text[:50]}...")

        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            self.generating = False

    async def recv(self):
        """Send next audio frame."""
        # Wait for generation to start
        while self.generating and len(self.audio_frames) == 0:
            await asyncio.sleep(0.01)

        # Return frames
        if self.frame_index < len(self.audio_frames):
            frame_data = self.audio_frames[self.frame_index]
            self.frame_index += 1

            # Create AudioFrame
            frame = AudioFrame.from_ndarray(frame_data.reshape(1, -1), format="flt", layout="mono")
            frame.sample_rate = self.sample_rate
            frame.pts = self.frame_index * 480  # 20ms at 24kHz
            frame.time_base = Fraction(1, 24000)

            return frame
        else:
            # End of audio, return silence
            await asyncio.sleep(0.02)
            raise MediaStreamError


class VoiceServiceWorker:
    """WebRTC worker that connects to signaling server and handles voice processing."""

    def __init__(
        self, session_id: str, signaling_url: str = SIGNALING_URL, room_id: str = None, participant_id: str = None
    ):
        self.session_id = session_id
        self.room_id = room_id or session_id  # Use session_id as fallback
        self.participant_id = participant_id or "candidate"  # Default participant
        self.signaling_url = signaling_url
        self.pc: RTCPeerConnection | None = None
        self.ws: aiohttp.ClientWebSocketResponse | None = None
        self.datachannel = None
        self.recorder = MediaBlackhole()

    async def start(self):
        """Connect to signaling server and initialize peer connection."""
        try:
            session = aiohttp.ClientSession()
            self.ws = await session.ws_connect(self.signaling_url)

            # Register as voice service peer
            await self.ws.send_json(
                {
                    "type": "register",
                    "peer_type": "voice",
                    "session_id": self.session_id,
                    "metadata": {"service": "voice-processing"},
                }
            )

            # Wait for registration acknowledgment
            reg_resp = await self.ws.receive_json()
            if reg_resp.get("type") != "registered":
                raise Exception(f"Registration failed: {reg_resp}")

            logger.info(f"Voice worker registered for session {self.session_id}")

            # Initialize peer connection without ICE servers for localhost testing
            config = RTCConfiguration(iceServers=[])
            self.pc = RTCPeerConnection(configuration=config)
            active_connections[self.session_id] = self.pc
            active_workers[self.session_id] = self

            # Setup peer connection handlers
            self._setup_pc_handlers()

            # Start signaling message loop
            await self._signaling_loop()

        except Exception as e:
            logger.error(f"Voice worker error: {e}")
            await self.stop()

    def _setup_pc_handlers(self):
        """Setup RTCPeerConnection event handlers."""

        @self.pc.on("track")
        async def on_track(track: MediaStreamTrack):
            logger.info(f"Received {track.kind} track")

            if track.kind == "audio":
                # Wrap track with STT processor
                stt_track = AudioStreamTrack(
                    track, self.datachannel, self.session_id, self.room_id, self.participant_id
                )
                self.recorder.addTrack(stt_track)
                logger.info("STT processing started for incoming audio")

        @self.pc.on("datachannel")
        def on_datachannel(channel):
            logger.info(f"DataChannel opened: {channel.label}")
            self.datachannel = channel

            @channel.on("message")
            def on_message(message):
                logger.info(f"DataChannel message: {message}")
                # TODO: Handle control messages (pause, resume, etc.)

        @self.pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate and self.ws:
                await self.ws.send_json(
                    {
                        "type": "ice_candidate",
                        "candidate": {
                            "candidate": candidate.candidate,
                            "sdpMid": candidate.sdpMid,
                            "sdpMLineIndex": candidate.sdpMLineIndex,
                        },
                    }
                )

    async def _signaling_loop(self):
        """Handle incoming signaling messages."""
        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                await self._handle_signaling_message(data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"WebSocket error: {self.ws.exception()}")
                break

    async def _handle_signaling_message(self, message: dict):
        """Process signaling messages from interview-service."""
        msg_type = message.get("type")

        if msg_type == "offer":
            # Receive offer from client (via interview-service)
            offer = RTCSessionDescription(sdp=message["sdp"], type="offer")
            await self.pc.setRemoteDescription(offer)

            # Create and send answer
            answer = await self.pc.createAnswer()
            await self.pc.setLocalDescription(answer)

            await self.ws.send_json({"type": "answer", "sdp": self.pc.localDescription.sdp})

            logger.info("Sent answer to client")

        elif msg_type == "ice_candidate":
            # Add ICE candidate from client
            candidate_data = message["candidate"]
            candidate = RTCIceCandidate(
                candidate=candidate_data["candidate"],
                sdpMid=candidate_data["sdpMid"],
                sdpMLineIndex=candidate_data["sdpMLineIndex"],
            )
            await self.pc.addIceCandidate(candidate)

    async def send_tts_response(self, text: str):
        """Generate TTS audio and add as outbound track."""
        if not self.pc:
            logger.warning("Cannot send TTS: peer connection not active")
            return

        try:
            # Create TTS audio track
            tts_track = TTSAudioTrack(text, self.session_id)

            # Add track to peer connection
            self.pc.addTrack(tts_track)

            logger.info(f"TTS track added for: {text[:50]}...")

        except Exception as e:
            logger.error(f"Failed to add TTS track: {e}")

    async def stop(self):
        """Clean up resources."""
        if self.pc:
            await self.pc.close()
            active_connections.pop(self.session_id, None)
            active_workers.pop(self.session_id, None)
        if self.ws:
            await self.ws.close()
        logger.info(f"Voice worker stopped for session {self.session_id}")


@app.post("/webrtc/start")
async def start_session(payload: Annotated[dict, Body(...)]):
    """Start a new WebRTC session for voice processing.
    Called by interview-service when a new interview begins.
    """
    session_id = payload.get("session_id")
    room_id = payload.get("room_id")
    participant_id = payload.get("participant_id")
    job_description = payload.get("job_description", "General software engineering position")

    if not session_id:
        return {"error": "Missing session_id"}, 400

    # Start conversation session
    conversation_started = await conversation_client.start_conversation(session_id, job_description)
    if not conversation_started:
        logger.warning(f"Failed to start conversation for session {session_id}")

    # Start worker in background with room and participant info
    worker = VoiceServiceWorker(session_id, room_id=room_id, participant_id=participant_id)
    asyncio.create_task(worker.start())

    return {
        "status": "started",
        "session_id": session_id,
        "room_id": room_id,
        "participant_id": participant_id,
        "conversation_started": conversation_started,
    }


@app.post("/webrtc/stop")
async def stop_session(payload: Annotated[dict, Body(...)]):
    """Stop an active WebRTC session."""
    session_id = payload.get("session_id")

    if session_id in active_connections:
        pc = active_connections[session_id]
        await pc.close()
        active_connections.pop(session_id)
        return {"status": "stopped", "session_id": session_id}

    return {"error": "Session not found"}, 404


@app.post("/webrtc/tts")
async def send_tts_audio(payload: Annotated[dict, Body(...)]):
    """Generate and send TTS audio to active session.

    Args:
        payload (dict): The request payload containing the session_id and text.
        session_id: Active session ID
        text: Text to synthesize
    """
    session_id = payload.get("session_id")
    text = payload.get("text")

    if not session_id or not text:
        return {"error": "Missing session_id or text"}, 400

    # Find active worker (stored in a registry we'll need to add)
    if session_id not in active_workers:
        return {"error": "Session not found or not active"}, 404

    worker = active_workers[session_id]
    await worker.send_tts_response(text)

    return {"status": "tts_sent", "session_id": session_id, "text": text[:50]}


@app.get("/webrtc/audio/stats")
async def get_audio_pipeline_stats():
    """Get audio pipeline performance statistics."""
    return {
        "pipeline_stats": audio_pipeline_stats,
        "configuration": {
            "opus_bitrate": OPUS_BITRATE,
            "opus_complexity": OPUS_COMPLEXITY,
            "enable_aec": ENABLE_AEC,
            "sample_rate": AUDIO_SAMPLE_RATE,
            "channels": AUDIO_CHANNELS,
        },
        "rnnoise_available": RNNoiseTrack is not None,
        "opus_available": OpusEncoder is not None,
    }


@app.post("/webrtc/audio/benchmark")
async def run_audio_benchmark(payload: Annotated[dict, Body(...)]):
    """Run audio pipeline benchmark test.

    Args:
        payload (dict): The request payload containing the duration_seconds and sample_rate.
        duration_seconds: Test duration (default: 5)
        sample_rate: Audio sample rate (default: 48000)
    """
    duration = payload.get("duration_seconds", 5)
    sample_rate = payload.get("sample_rate", 48000)

    try:
        # Generate test audio (sine wave with noise)
        start_time = time.time()

        # Create test audio: 1kHz sine wave + white noise
        t = np.linspace(0, duration, int(sample_rate * duration))
        clean_signal = 0.5 * np.sin(2 * np.pi * 1000 * t)
        noise = 0.1 * np.random.normal(0, 1, len(clean_signal))
        noisy_signal = clean_signal + noise

        # Calculate input SNR
        signal_power = np.mean(clean_signal**2)
        noise_power = np.mean(noise**2)
        input_snr = 10 * np.log10(signal_power / noise_power)

        # Test RNNoise if available
        rnnoise_output = None
        rnnoise_snr = None
        if RNNoiseTrack:
            # Create a mock track for testing
            class MockTrack:
                def __init__(self, audio_data):
                    self.audio_data = audio_data
                    self.index = 0

                async def recv(self):
                    if self.index >= len(self.audio_data):
                        raise MediaStreamError

                    # Return 10ms chunks (480 samples at 48kHz)
                    chunk_size = 480
                    start_idx = self.index
                    end_idx = min(start_idx + chunk_size, len(self.audio_data))

                    chunk = self.audio_data[start_idx:end_idx]
                    self.index = end_idx

                    # Create AudioFrame
                    frame = AudioFrame.from_ndarray(chunk.reshape(1, -1), format="flt", layout="mono")
                    frame.sample_rate = sample_rate
                    frame.pts = start_idx
                    frame.time_base = Fraction(1, sample_rate)

                    return frame

            mock_track = MockTrack(noisy_signal.astype(np.float32))
            rnnoise_track = RNNoiseTrack(mock_track)

            # Process through RNNoise
            processed_frames = []
            try:
                while True:
                    frame = await rnnoise_track.recv()
                    processed_frames.append(frame.to_ndarray().flatten())
            except MediaStreamError:
                pass

            if processed_frames:
                rnnoise_output = np.concatenate(processed_frames)

                # Calculate output SNR
                output_signal_power = np.mean(rnnoise_output**2)
                output_noise_power = np.mean((rnnoise_output - clean_signal[: len(rnnoise_output)]) ** 2)
                rnnoise_snr = 10 * np.log10(output_signal_power / output_noise_power)

        processing_time = time.time() - start_time

        return {
            "benchmark_results": {
                "duration_seconds": duration,
                "sample_rate": sample_rate,
                "input_snr_db": float(input_snr),
                "rnnoise_snr_db": float(rnnoise_snr) if rnnoise_snr else None,
                "snr_improvement_db": float(rnnoise_snr - input_snr) if rnnoise_snr else None,
                "processing_time_seconds": processing_time,
                "realtime_factor": processing_time / duration,
            },
            "rnnoise_available": RNNoiseTrack is not None,
            "opus_available": OpusEncoder is not None,
        }

    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        return {"error": str(e)}, 500



async def start_webrtc_worker():
    """Start the WebRTC worker service."""
    logger.info("Starting WebRTC worker service on port 8006")
    # The worker runs as a separate FastAPI app
    # This function is called from main.py to start the worker in background
    pass


@app.get("/webrtc/status")
def get_status():
    """Get status of all active sessions."""
    return {"active_sessions": list(active_connections.keys()), "count": len(active_connections)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8006)  # nosec B104
