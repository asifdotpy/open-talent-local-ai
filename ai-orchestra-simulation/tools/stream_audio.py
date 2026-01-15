#!/usr/bin/env python3
"""
Stream audio data for AI Orchestra live demonstration
Provides real-time WebSocket streaming for live avatar interviews
Compatible with the ai-orchestra-simulation streaming architecture
"""

import argparse
import asyncio
import json
import math
import os
import random
import struct
import sys

import websockets

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("⚠️  NumPy not available. Install with: pip install numpy websockets")


class StreamingWAVGenerator:
    """Generate streaming WAV audio data compatible with WebSocket streaming"""

    def __init__(self, sample_rate=44100, channels=1, bits_per_sample=16):
        self.sample_rate = sample_rate
        self.channels = channels
        self.bits_per_sample = bits_per_sample
        self.bytes_per_sample = bits_per_sample // 8

    def create_wav_header(self, data_size):
        """Create proper WAV file header"""
        return struct.pack(
            "<4sL4s4sLHHLLHH4sL",
            b"RIFF",
            36 + data_size,  # File size
            b"WAVE",
            b"fmt ",
            16,  # Format chunk size
            1,  # Audio format (PCM)
            self.channels,
            self.sample_rate,
            self.sample_rate * self.channels * self.bytes_per_sample,  # Byte rate
            self.channels * self.bytes_per_sample,  # Block align
            self.bits_per_sample,
            b"data",
            data_size,
        )

    def generate_sine_wave(self, frequency, duration, amplitude=0.8):
        """Generate sine wave audio data"""
        if HAS_NUMPY:
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            wave = amplitude * np.sin(2 * np.pi * frequency * t)
            # Convert to 16-bit PCM
            return (wave * 32767).astype(np.int16).tobytes()
        else:
            # Fallback without numpy
            audio_data = b""
            num_samples = int(self.sample_rate * duration)
            for i in range(num_samples):
                sample = int(
                    amplitude * 32767 * math.sin(2 * math.pi * frequency * i / self.sample_rate)
                )
                audio_data += struct.pack("<h", sample)
            return audio_data

    def generate_speech_like_audio(self, text, base_frequency=180):
        """Generate speech-like audio with varying frequencies"""
        words = text.split()
        audio_chunks = []

        for word in words:
            # Vary frequency slightly for each word (speech-like)
            frequency = base_frequency + random.randint(-50, 50)
            duration = max(0.3, len(word) * 0.1)  # Word length affects duration

            # Add some amplitude variation
            amplitude = 0.6 + random.random() * 0.3

            chunk = self.generate_sine_wave(frequency, duration, amplitude)
            audio_chunks.append(chunk)

            # Add small pause between words
            pause_samples = int(self.sample_rate * 0.05)  # 50ms pause
            pause_data = b"\x00\x00" * pause_samples
            audio_chunks.append(pause_data)

        return b"".join(audio_chunks)

    def create_streaming_chunks(self, audio_data, chunk_size_ms=100):
        """Break audio data into streaming chunks for WebSocket"""
        chunk_size_samples = int(self.sample_rate * chunk_size_ms / 1000)
        chunk_size_bytes = chunk_size_samples * self.channels * self.bytes_per_sample

        chunks = []
        for i in range(0, len(audio_data), chunk_size_bytes):
            chunk = audio_data[i : i + chunk_size_bytes]
            if len(chunk) > 0:
                chunks.append(chunk)

        return chunks


async def stream_audio_to_websocket(
    generator, text, websocket_url="ws://localhost:8051/ws/session_123", session_id="demo"
):
    """Stream generated audio via WebSocket to avatar animation service"""
    try:
        # Replace session_id placeholder in URL
        ws_url = websocket_url.replace("{session_id}", session_id)

        async with websockets.connect(ws_url) as websocket:
            print(f"🔗 Connected to WebSocket: {ws_url}")

            # Generate audio data
            audio_data = generator.generate_speech_like_audio(text)
            chunks = generator.create_streaming_chunks(audio_data)

            print(f"🎵 Streaming {len(chunks)} audio chunks...")

            # Send session start metadata
            start_metadata = {
                "type": "session_start",
                "session_id": session_id,
                "audio_format": "wav",
                "sample_rate": generator.sample_rate,
                "total_chunks": len(chunks),
                "text": text,
            }
            await websocket.send(json.dumps(start_metadata))

            for i, chunk in enumerate(chunks):
                # Send audio chunk as binary data
                await websocket.send(chunk)

                # Send chunk metadata for timing
                metadata = {
                    "type": "audio_chunk",
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "timestamp": i * 0.1,  # 100ms per chunk
                    "session_id": session_id,
                }
                await websocket.send(json.dumps(metadata))

                # Small delay to simulate real-time streaming
                await asyncio.sleep(0.1)

            # Send session end metadata
            end_metadata = {
                "type": "session_end",
                "session_id": session_id,
                "total_chunks": len(chunks),
                "duration": len(chunks) * 0.1,
            }
            await websocket.send(json.dumps(end_metadata))

            print("✅ Audio streaming complete")

    except Exception as e:
        print(f"❌ WebSocket streaming failed: {e}")
        print("💡 Make sure the avatar animation service is running on the specified WebSocket URL")


def load_text_from_file():
    """Load text from prompt.txt or use default"""
    prompt_file = "prompt.txt"
    if os.path.exists(prompt_file):
        with open(prompt_file, encoding="utf-8") as f:
            return f.read().strip()
    else:
        return "Welcome to the AI Orchestra live streaming demonstration. This showcases real-time facial animation with WebSocket audio streaming."


async def demo_streaming(args):
    """Demonstrate WebSocket streaming capability"""
    print("🌐 Starting WebSocket audio streaming demo...")
    print(f"🎯 Target URL: {args.websocket_url}")
    print(f"🆔 Session ID: {args.session_id}")

    # Load text
    text = load_text_from_file()
    print(f"📝 Streaming text: {text[:50]}...")

    # Initialize generator
    generator = StreamingWAVGenerator()

    # Start streaming
    await stream_audio_to_websocket(generator, text, args.websocket_url, args.session_id)


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Stream audio data for AI Orchestra live demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stream_audio.py --websocket-url ws://localhost:8051/ws/demo_session
  python stream_audio.py --session-id interview_001 --text "Hello, welcome to your interview"
  python stream_audio.py --demo  # Use default settings
        """,
    )

    parser.add_argument(
        "--websocket-url",
        default="ws://localhost:8051/ws/{session_id}",
        help="WebSocket URL for streaming (default: ws://localhost:8051/ws/{session_id})",
    )

    parser.add_argument(
        "--session-id", default="demo", help="Session ID for the streaming session (default: demo)"
    )

    parser.add_argument(
        "--text", help="Text to stream (default: load from prompt.txt or use demo text)"
    )

    parser.add_argument("--demo", action="store_true", help="Run demo with default settings")

    args = parser.parse_args()

    # Check dependencies
    if not HAS_NUMPY:
        print("❌ NumPy is required for audio streaming. Install with:")
        print("   pip install numpy websockets")
        sys.exit(1)

    print("🎵 AI Orchestra Audio Streaming Service")
    print("=" * 45)
    print("🌐 WebSocket-based real-time audio streaming")
    print("🎙️  WAV format for superior lip-sync quality")
    print("🔴 Compatible with live avatar animation")
    print()

    if args.demo or (len(sys.argv) == 1):
        # Run demo mode
        asyncio.run(demo_streaming(args))
    else:
        # Custom streaming
        text = args.text or load_text_from_file()
        generator = StreamingWAVGenerator()
        asyncio.run(stream_audio_to_websocket(generator, text, args.websocket_url, args.session_id))


if __name__ == "__main__":
    main()
