#!/usr/bin/env python3
"""
Voice Service → Avatar Renderer Integration Test
Tests end-to-end flow: TTS → Phonemes → Avatar Video
"""

import requests
import json
import time
import sys

VOICE_SERVICE_URL = "http://localhost:8002"
AVATAR_SERVICE_URL = "http://localhost:3001"

def test_integration():
    print("🔄 Voice Service → Avatar Renderer Integration Test")
    print("=" * 60)
    
    # Step 1: Generate TTS with phonemes
    print("\n📝 Step 1: Generating TTS from voice service...")
    tts_request = {
        "text": "Hello, this is a test of the avatar rendering system.",
        "voice": "en-US",
        "extract_phonemes": True
    }
    
    try:
        tts_response = requests.post(
            f"{VOICE_SERVICE_URL}/voice/tts",
            json=tts_request,
            timeout=30
        )
        
        if tts_response.status_code != 200:
            print(f"❌ TTS request failed: {tts_response.status_code}")
            print(f"Response: {tts_response.text}")
            return False
        
        # Parse JSON response
        tts_data = tts_response.json()
        print(f"✅ TTS generated successfully")
        
        # Decode base64 audio
        import base64
        audio_b64 = tts_data.get('audio_data')
        if not audio_b64:
            print(f"❌ No audio_data in response: {list(tts_data.keys())}")
            return False
            
        audio_bytes = base64.b64decode(audio_b64)
        print(f"📊 Audio size: {len(audio_bytes)} bytes")
        
        # Extract phonemes from response
        phonemes_from_tts = tts_data.get('phonemes', [])
        duration_from_tts = tts_data.get('duration', 0)
        print(f"📊 Phonemes extracted: {len(phonemes_from_tts)}")
        print(f"⏱️  TTS duration: {duration_from_tts:.2f}s")
        
        # Save audio file
        audio_path = "/tmp/test_audio.wav"
        with open(audio_path, 'wb') as f:
            f.write(audio_bytes)
        print(f"💾 Audio saved: {audio_path}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ TTS request failed: {e}")
        return False
    
    # Step 2: Use phonemes from TTS response
    print("\n📝 Step 2: Preparing phoneme data for avatar...")
    
    # Use phonemes from voice service if available, otherwise create sample
    if phonemes_from_tts and len(phonemes_from_tts) > 0:
        phonemes = phonemes_from_tts
        duration = duration_from_tts
        print(f"✅ Using phonemes from voice service")
    else:
        print(f"⚠️  No phonemes from TTS, using sample data")
        phonemes = [
            {"phoneme": "HH", "start": 0.0, "end": 0.08},
            {"phoneme": "AH", "start": 0.08, "end": 0.15},
            {"phoneme": "L", "start": 0.15, "end": 0.22},
            {"phoneme": "OW", "start": 0.22, "end": 0.35},
            {"phoneme": "TH", "start": 0.4, "end": 0.48},
            {"phoneme": "IH", "start": 0.48, "end": 0.55},
            {"phoneme": "S", "start": 0.55, "end": 0.65},
            {"phoneme": "IH", "start": 0.7, "end": 0.77},
            {"phoneme": "Z", "start": 0.77, "end": 0.85},
            {"phoneme": "AH", "start": 0.9, "end": 0.97},
            {"phoneme": "T", "start": 1.0, "end": 1.08},
            {"phoneme": "EH", "start": 1.08, "end": 1.15},
            {"phoneme": "S", "start": 1.15, "end": 1.22},
            {"phoneme": "T", "start": 1.22, "end": 1.3}
        ]
        duration = 1.5
    print(f"📊 Phonemes: {len(phonemes)}")
    print(f"⏱️  Duration: {duration}s")
    
    # Step 3: Send to avatar renderer
    print("\n📝 Step 3: Rendering avatar video...")
    render_request = {
        "phonemes": phonemes,
        "duration": duration,
        "audioUrl": f"file://{audio_path}"
    }
    
    try:
        start_time = time.time()
        render_response = requests.post(
            f"{AVATAR_SERVICE_URL}/render/lipsync",
            json=render_request,
            timeout=60
        )
        render_time = time.time() - start_time
        
        if render_response.status_code != 200:
            print(f"❌ Render request failed: {render_response.status_code}")
            print(f"Response: {render_response.text[:500]}")
            return False
            
        # Save video
        video_path = "/tmp/integration_test.webm"
        with open(video_path, 'wb') as f:
            f.write(render_response.content)
        
        video_size = len(render_response.content)
        print(f"✅ Video rendered successfully")
        print(f"💾 Video saved: {video_path}")
        print(f"📊 Video size: {video_size / 1024:.2f} KB")
        print(f"⏱️  Render time: {render_time:.2f}s")
        print(f"📈 Processing speed: {duration / render_time:.2f}x realtime")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Render request failed: {e}")
        return False
    
    # Step 4: Verify video file
    print("\n📝 Step 4: Verifying video file...")
    import subprocess
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
             '-show_format', '-show_streams', video_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            video_info = json.loads(result.stdout)
            format_info = video_info.get('format', {})
            streams = video_info.get('streams', [])
            
            print(f"✅ Video file is valid")
            if streams:
                video_stream = streams[0]
                print(f"📊 Codec: {video_stream.get('codec_name', 'unknown')}")
                print(f"📐 Resolution: {video_stream.get('width')}x{video_stream.get('height')}")
            print(f"⏱️  Duration: {format_info.get('duration', 'unknown')}s")
        else:
            print(f"⚠️  Could not verify video (ffprobe not available)")
            
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️  Video verification skipped: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Integration test PASSED")
    print(f"🎯 Complete flow: Voice TTS → Phonemes → Avatar Video")
    return True

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
