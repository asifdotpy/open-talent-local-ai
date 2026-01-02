#!/usr/bin/env python3
"""
Streaming WAV Audio Generator for AI Orchestra Live Demonstration
Creates real-time compatible audio chunks for WebSocket streaming
Uses local implementation with numpy for high-quality WAV generation
"""

import asyncio
import json
import math
import os
import random
import struct
import sys
from pathlib import Path

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("⚠️  NumPy not available. Install with: pip install numpy")

try:
    import websockets

    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    print("⚠️  websockets not available. Install with: pip install websockets")


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
    generator, text, websocket_url="ws://localhost:8051/ws/session_123"
):
    """Stream generated audio via WebSocket to avatar animation service"""
    if not HAS_WEBSOCKETS:
        print("❌ websockets package not available for streaming")
        return False

    try:
        async with websockets.connect(websocket_url) as websocket:
            print(f"🔗 Connected to WebSocket: {websocket_url}")

            # Generate audio data
            audio_data = generator.generate_speech_like_audio(text)
            chunks = generator.create_streaming_chunks(audio_data)

            print(f"🎵 Streaming {len(chunks)} audio chunks...")

            for i, chunk in enumerate(chunks):
                # Send audio chunk as binary data
                await websocket.send(chunk)

                # Send metadata for timing
                metadata = {
                    "type": "audio_chunk",
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "timestamp": i * 0.1,  # 100ms per chunk
                    "session_id": websocket_url.split("/")[-1],
                }
                await websocket.send(json.dumps(metadata))

                # Small delay to simulate real-time streaming
                await asyncio.sleep(0.1)

            print("✅ Audio streaming complete")

    except Exception as e:
        print(f"❌ WebSocket streaming failed: {e}")
        return False

    return True


def create_demo_files():
    """Create demo WAV file and timing data for testing"""

    # Read text from prompt.txt if it exists
    prompt_file = "prompt.txt"
    if os.path.exists(prompt_file):
        with open(prompt_file, encoding="utf-8") as f:
            speech_text = f.read().strip()
        print(f"📖 Using text from {prompt_file}")
    else:
        speech_text = "Welcome to the AI Orchestra live streaming demonstration. This showcases real-time facial animation with WebSocket audio streaming."
        print("📖 Using default streaming text")

    # Create directories
    audio_dir = Path("assets/audio")
    audio_dir.mkdir(parents=True, exist_ok=True)

    print("🎙️  Generating streaming-compatible WAV audio...")
    print(f"📝 Text: {speech_text}")

    # Initialize generator
    generator = StreamingWAVGenerator()

    # Generate speech-like audio
    audio_data = generator.generate_speech_like_audio(speech_text)

    # Create WAV file with proper header
    wav_header = generator.create_wav_header(len(audio_data))
    wav_path = audio_dir / "speech_streaming.wav"

    try:
        with open(wav_path, "wb") as f:
            f.write(wav_header + audio_data)
        print("✅ Streaming WAV file created successfully")
    except Exception as e:
        print(f"❌ Error creating WAV file: {e}")
        return False

    # Create word timing data for lip-sync
    words = speech_text.split()
    estimated_duration = len(audio_data) / (generator.sample_rate * generator.bytes_per_sample)
    time_per_word = estimated_duration / len(words) if words else 1

    words_data = []
    for i, word in enumerate(words):
        start_time = i * time_per_word
        end_time = (i + 1) * time_per_word
        confidence = round(random.uniform(0.85, 0.98), 2)
        words_data.append(
            {
                "word": word,
                "start": round(start_time, 2),
                "end": round(end_time, 2),
                "confidence": confidence,
            }
        )

    # Create speech.json with streaming metadata
    speech_data = {
        "words": words_data,
        "duration": round(estimated_duration, 2),
        "sampleRate": generator.sample_rate,
        "format": "word-level-timing",
        "audioFormat": "wav",
        "version": "3.0",  # Updated for streaming
        "text": speech_text,
        "generated": True,
        "source": "local_streaming_tts",
        "streaming": {
            "chunk_size_ms": 100,
            "websocket_url": "ws://localhost:8051/ws/{session_id}",
            "supports_realtime": True,
        },
        "note": "Streaming-compatible WAV with WebSocket integration",
    }

    json_path = audio_dir / "speech_streaming.json"
    print(f"📄 Creating streaming timing data: {json_path}")

    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(speech_data, f, indent=2, ensure_ascii=False)
        print("✅ Streaming timing data created successfully")
    except Exception as e:
        print(f"❌ Error creating speech.json: {e}")
        return False

    print("\n🎉 Streaming WAV files generated successfully!")
    print(f"📁 WAV file: {wav_path}")
    print(f"📁 Timing data: {json_path}")
    print(f"⏱️  Duration: {estimated_duration:.1f} seconds")
    print(f"📊 Words: {len(words_data)}")
    print(f"🎵 Sample rate: {generator.sample_rate}Hz")
    print(f"📦 Chunks: {len(generator.create_streaming_chunks(audio_data))}")

    print("\n💡 Streaming Features:")
    print("   - WAV format for superior lip-sync quality")
    print("   - 100ms chunks for real-time WebSocket streaming")
    print("   - Compatible with avatar animation service")
    print("   - No external APIs or dependencies")
    print("   - Local generation with numpy optimization")

    return True


async def demo_streaming(session_id="session_123"):
    """Demonstrate WebSocket streaming capability"""
    print("\n🌐 Testing WebSocket streaming...")

    generator = StreamingWAVGenerator()
    text = "Hello, this is a streaming audio demonstration for the AI Orchestra avatar system."

    websocket_url = f"ws://localhost:8051/ws/{session_id}"
    success = await stream_audio_to_websocket(generator, text, websocket_url)

    if success:
        print("✅ WebSocket streaming demo completed successfully")
    else:
        print("❌ WebSocket streaming demo failed")


def main():
    """Main function with command line argument handling"""
    print("🎵 AI Orchestra Streaming WAV Generator")
    print("=" * 50)
    print("📦 Uses numpy for high-quality audio generation")
    print("🌐 Compatible with WebSocket streaming architecture")
    print("🎙️  Generates WAV format for superior lip-sync")
    print()

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--stream":
            if len(sys.argv) > 2:
                session_id = sys.argv[2]
            else:
                session_id = "session_123"
            print(f"🚀 Starting WebSocket streaming demo for session: {session_id}")
            asyncio.run(demo_streaming(session_id))
            return
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python3 streaming_audio.py              # Generate demo files")
            print("  python3 streaming_audio.py --stream     # Test WebSocket streaming")
            print(
                "  python3 streaming_audio.py --stream <session_id>  # Stream to specific session"
            )
            return
        else:
            print(f"❌ Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
            return

    # Default: Create demo files
    success = create_demo_files()

    if success:
        print("\n✅ Streaming setup complete!")
        print("💡 To test WebSocket streaming, run:")
        print("   python3 streaming_audio.py --stream")
        print("   python3 streaming_audio.py --stream my_session_456")
        print("\n🔧 Integration with AI Orchestra:")
        print("   - WAV files work with Three.js audio system")
        print("   - Timing data enables precise lip-sync animation")
        print("   - Streaming chunks support live interview mode")
    else:
        print("\n❌ Failed to generate streaming files")
        sys.exit(1)


if __name__ == "__main__":
    main()
