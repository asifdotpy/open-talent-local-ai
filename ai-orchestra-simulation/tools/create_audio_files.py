#!/usr/bin/env python3
"""
Create speech.mp3 and speech.json files for AI Orchestra demonstration
Downloads a sample audio file and creates timing data
"""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path


def create_speech_files():
    """Create speech.mp3 and speech.json files"""

    # Create directories if they don't exist
    audio_dir = Path("assets/audio")
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Text for the AI Orchestra demonstration
    speech_text = "Welcome to the AI Orchestra demonstration. This prototype showcases real-time facial animation using mathematical precision."

    # Word-level breakdown with timing
    words_data = [
        {"word": "Welcome", "start": 0.0, "end": 0.8, "confidence": 0.95},
        {"word": "to", "start": 0.8, "end": 1.0, "confidence": 0.98},
        {"word": "the", "start": 1.0, "end": 1.2, "confidence": 0.97},
        {"word": "AI", "start": 1.2, "end": 1.6, "confidence": 0.99},
        {"word": "Orchestra", "start": 1.6, "end": 2.4, "confidence": 0.96},
        {"word": "demonstration", "start": 2.4, "end": 3.8, "confidence": 0.94},
        {"word": "This", "start": 4.2, "end": 4.5, "confidence": 0.98},
        {"word": "prototype", "start": 4.5, "end": 5.2, "confidence": 0.96},
        {"word": "showcases", "start": 5.2, "end": 6.0, "confidence": 0.97},
        {"word": "real-time", "start": 6.0, "end": 6.8, "confidence": 0.95},
        {"word": "facial", "start": 6.8, "end": 7.3, "confidence": 0.98},
        {"word": "animation", "start": 7.3, "end": 8.2, "confidence": 0.97},
        {"word": "using", "start": 8.5, "end": 8.9, "confidence": 0.99},
        {"word": "mathematical", "start": 8.9, "end": 10.0, "confidence": 0.96},
        {"word": "precision", "start": 10.0, "end": 10.8, "confidence": 0.98},
    ]

    # Create speech.json with timing data
    speech_data = {
        "words": words_data,
        "duration": 11.0,
        "sampleRate": 22050,
        "format": "word-level-timing",
        "version": "1.0",
        "text": speech_text,
        "generated": True,
        "source": "sample_audio",
    }

    json_path = audio_dir / "speech.json"
    print(f"Creating speech timing data: {json_path}")

    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(speech_data, f, indent=2, ensure_ascii=False)
        print("✅ Speech timing data created successfully")
    except Exception as e:
        print(f"❌ Error creating speech.json: {e}")
        return False

    # Try to download a sample audio file
    mp3_path = audio_dir / "speech.mp3"

    # List of sample audio URLs to try
    sample_urls = [
        "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
        "https://file-examples.com/storage/fe68c1b7c1a9d3b2b8b8b8b/2017/11/file_example_MP3_700KB.mp3",
        "https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3",
    ]

    for i, url in enumerate(sample_urls):
        try:
            print(f"Attempting to download sample audio from source {i+1}...")
            urllib.request.urlretrieve(url, mp3_path)
            print(f"✅ Sample audio downloaded successfully from source {i+1}")
            break
        except Exception as e:
            print(f"❌ Failed to download from source {i+1}: {e}")
            if i == len(sample_urls) - 1:
                # If all downloads fail, create a simple placeholder
                print("Creating placeholder audio file...")
                create_placeholder_audio(mp3_path)

    print("\n🎉 Audio files created successfully!")
    print(f"📁 Audio file: {mp3_path}")
    print(f"📁 Timing data: {json_path}")
    print("\n💡 Tips:")
    print("   - The audio file is a placeholder/sample")
    print("   - The timing data matches the expected speech text")
    print("   - You can replace the audio file with your own recording")
    print("   - Adjust timing in speech.json if needed for better lip sync")

    return True


def create_placeholder_audio(mp3_path):
    """Create a simple placeholder audio file"""
    try:
        # Create a simple sine wave audio file using Python
        import math
        import struct
        import wave

        # Audio parameters
        sample_rate = 22050
        duration = 11.0  # seconds
        frequency = 440  # Hz (A4 note)

        # Generate sine wave
        frames = []
        for i in range(int(sample_rate * duration)):
            # Create a simple tone that fades in and out
            t = i / sample_rate
            fade = min(t, duration - t, 1.0)  # Fade in/out over 1 second
            amplitude = 0.3 * fade  # Quiet volume
            value = int(32767 * amplitude * math.sin(2 * math.pi * frequency * t))
            frames.append(struct.pack("<h", value))

        # Write WAV file first
        wav_path = str(mp3_path).replace(".mp3", ".wav")
        with wave.open(wav_path, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b"".join(frames))

        # Rename to mp3 (it's actually a WAV file, but browsers can handle it)
        os.rename(wav_path, mp3_path)
        print("✅ Placeholder audio file created")

    except Exception as e:
        print(f"❌ Error creating placeholder audio: {e}")
        # Create an empty file as last resort
        mp3_path.touch()
        print("⚠️  Created empty audio file placeholder")


if __name__ == "__main__":
    print("🎵 AI Orchestra Audio File Creator")
    print("=" * 40)

    success = create_speech_files()

    if success:
        print("\n✅ Setup complete! You can now run the AI Orchestra application.")
    else:
        print("\n❌ Failed to create audio files.")
        print("   Please check the error messages above and try again.")
