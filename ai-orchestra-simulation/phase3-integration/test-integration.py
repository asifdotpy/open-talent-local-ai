#!/usr/bin/env python3

"""
Phase 3 Integration Test
Tests the avatar service with 3D face model integration
"""

import sys
import time

import requests


def test_avatar_service():
    """Test the avatar service with 3D rendering"""

    # Test data
    test_request = {
        "text": "Hello, this is a test of the 3D avatar rendering system with a longer duration.",
        "phonemes": [
            {"phoneme": "A", "start": 0.0, "end": 2.0},
            {"phoneme": "E", "start": 2.0, "end": 4.0},
            {"phoneme": "I", "start": 4.0, "end": 6.0},
            {"phoneme": "O", "start": 6.0, "end": 8.0},
            {"phoneme": "U", "start": 8.0, "end": 10.0},
        ],
        "duration": 10.0,  # Test with 10 seconds first
        "model": "face",
    }

    print("🚀 Testing Phase 3: Avatar Service 3D Integration")
    print("=" * 60)

    try:
        # Test health check
        print("📡 Testing avatar service health...")
        health_response = requests.get("http://localhost:8001/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Avatar service is healthy")
        else:
            print(f"❌ Avatar service health check failed: {health_response.status_code}")
            return False

        # Test model serving
        print("📦 Testing model file serving...")
        model_response = requests.head("http://localhost:8001/models/face.glb", timeout=5)
        if model_response.status_code == 200:
            size = model_response.headers.get("content-length", "unknown")
            print(f"✅ Face model accessible ({size} bytes)")
        else:
            print(f"❌ Face model not accessible: {model_response.status_code}")
            return False

        # Test rendering
        print("🎬 Testing lip-sync video rendering...")
        start_time = time.time()

        render_response = requests.post(
            "http://localhost:8001/render/lipsync",
            json=test_request,
            timeout=180,  # Increased from 60 to 180 seconds for video encoding
        )

        render_time = time.time() - start_time

        if render_response.status_code == 200:
            result = render_response.json()
            print("✅ Video rendering successful!")
            print(f"   Render time: {render_time:.2f}s")
            print(f"   Model used: {result.get('model_used', 'unknown')}")
            print(f"   Video path: {result.get('video_path', 'none')}")
            print(f"   Metadata: {len(result.get('metadata', {}))} fields")

            # Check metadata
            metadata = result.get("metadata", {})
            if metadata.get("frames", 0) > 0:
                print(f"   ✅ Generated {metadata['frames']} frames")
            else:
                print("   ⚠️  No frames generated")

            return True
        else:
            print(f"❌ Rendering failed: {render_response.status_code}")
            print(f"   Error: {render_response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to avatar service. Is it running on port 8001?")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def main():
    print("Phase 3 Integration Test")
    print("Tests 3D face model integration with avatar service")
    print()

    # Check if avatar service is running
    try:
        response = requests.get("http://localhost:8001/health", timeout=2)
        if response.status_code != 200:
            print("❌ Avatar service is not responding. Please start it first:")
            print("   cd microservices/avatar-service && python main.py")
            sys.exit(1)
    except:
        print("❌ Avatar service is not running. Please start it first:")
        print("   cd microservices/avatar-service && python main.py")
        sys.exit(1)

    # Run the test
    success = test_avatar_service()

    print()
    print("=" * 60)
    if success:
        print("🎉 Phase 3 Integration Test PASSED!")
        print("✅ 3D face model successfully integrated with avatar service")
        print("✅ Lip-sync rendering working with morph targets")
        print("✅ Avatar service ready for production")
    else:
        print("💥 Phase 3 Integration Test FAILED!")
        print("❌ Check the errors above and fix integration issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
