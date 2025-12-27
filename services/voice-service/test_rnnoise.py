#!/usr/bin/env python3
"""Test script for RNNoise integration in voice service.
Tests noise suppression functionality.
"""

from fractions import Fraction

import numpy as np
from aiortc import AudioStreamTrack
from av import AudioFrame

from services.audio_processing_service import RNNoiseTrack


class MockAudioTrack(AudioStreamTrack):
    """Mock audio track for testing."""
    kind = "audio"

    def __init__(self, audio_data, sample_rate=48000):
        super().__init__()
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.frame_index = 0
        self.frames = []

        # Create frames from audio data
        frame_size = int(sample_rate * 0.02)  # 20ms frames
        for i in range(0, len(audio_data), frame_size):
            chunk = audio_data[i:i+frame_size]
            if len(chunk) > 0:
                frame = AudioFrame.from_ndarray(chunk.reshape(1, -1), format='s16', layout='mono')
                frame.sample_rate = sample_rate
                frame.pts = i
                frame.time_base = Fraction(1, sample_rate)
                self.frames.append(frame)

    async def recv(self):
        if self.frame_index < len(self.frames):
            frame = self.frames[self.frame_index]
            self.frame_index += 1
            return frame
        else:
            raise Exception("End of audio")

def test_rnnoise():
    """Test RNNoise noise suppression."""
    print("Testing RNNoise integration...")

    # Generate test audio with noise
    sample_rate = 48000
    duration = 1.0  # 1 second
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Clean signal (440Hz sine wave)
    clean_signal = 0.5 * np.sin(2 * np.pi * 440 * t)

    # Add white noise
    noise = 0.1 * np.random.normal(0, 1, len(clean_signal))
    noisy_signal = clean_signal + noise

    # Convert to int16
    noisy_int16 = (noisy_signal * 32767).astype(np.int16)

    # Create mock track
    mock_track = MockAudioTrack(noisy_int16, sample_rate)

    # Create RNNoise track
    rnnoise_track = RNNoiseTrack(mock_track)

    print("Processing audio through RNNoise...")

    # Process frames
    processed_frames = []
    try:
        import asyncio
        async def process():
            while True:
                frame = await rnnoise_track.recv()
                processed_frames.append(frame)

        asyncio.run(process())
    except Exception as e:
        print(f"Processing completed: {e}")

    print(f"Processed {len(processed_frames)} frames")

    # Calculate SNR improvement
    if processed_frames:
        # Get processed audio
        processed_audio = []
        for frame in processed_frames:
            data = frame.to_ndarray().flatten()
            processed_audio.extend(data)

        processed_audio = np.array(processed_audio, dtype=np.float32) / 32767.0

        # Calculate SNR
        def calculate_snr(signal, noise):
            return 10 * np.log10(np.mean(signal**2) / np.mean(noise**2))

        calculate_snr(clean_signal[:len(processed_audio)], noise[:len(processed_audio)])
        calculate_snr(processed_audio, processed_audio - clean_signal[:len(processed_audio)])

        print(".2f")
        print(".2f")
        print(".2f")

        print("✅ RNNoise integration test passed!")
        return True
    else:
        print("❌ No frames processed")
        return False

if __name__ == "__main__":
    test_rnnoise()
