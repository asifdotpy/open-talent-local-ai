#!/usr/bin/env python3
"""
Safe Development Tests for Voice Service
Tests basic functionality without system-crashing stress tests
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Any

import httpx
import pytest
import numpy as np
import soundfile as sf


class SafeVoiceServiceTester:
    """Safe tester for voice service development validation."""

    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            result = response.json()
            result["success"] = response.status_code == 200 and result.get("status") in ["healthy", "degraded"]
            return result
        except Exception as e:
            return {"success": False, "error": str(e), "status": "unreachable"}

    async def test_stt_basic(self, audio_file: str = None) -> Dict[str, Any]:
        """Test STT by generating audio with TTS first."""
        try:
            # Generate test audio using TTS if none provided
            if audio_file is None:
                test_text = "Hello, this is a test of the speech to text system."
                tts_payload = {"text": test_text, "voice": "lessac"}

                tts_response = await self.client.post(
                    f"{self.base_url}/voice/tts",
                    json=tts_payload
                )

                if tts_response.status_code != 200:
                    return {"success": False, "error": f"TTS failed: {tts_response.status_code}"}

                # Save TTS audio temporarily
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(tts_response.content)
                    audio_file = tmp.name

                cleanup_audio = True
            else:
                cleanup_audio = False

            try:
                # Test STT with the audio
                with open(audio_file, "rb") as f:
                    files = {"audio_file": ("test.wav", f, "audio/wav")}
                    stt_response = await self.client.post(
                        f"{self.base_url}/voice/stt",
                        files=files
                    )

                if stt_response.status_code == 200:
                    result = stt_response.json()
                    text = result.get("text", "").strip()
                    confidence = result.get("confidence", 0)

                    # Check if transcription is reasonable (contains key words)
                    expected_words = ["hello", "test", "speech", "text", "system"]
                    transcribed_words = text.lower().split()
                    matched_words = sum(1 for word in expected_words if word in transcribed_words)

                    return {
                        "success": True,
                        "status_code": stt_response.status_code,
                        "text": text,
                        "confidence": confidence,
                        "duration": result.get("duration", 0),
                        "accuracy": matched_words / len(expected_words),
                        "expected_text": test_text if audio_file is None else None
                    }
                else:
                    return {
                        "success": False,
                        "status_code": stt_response.status_code,
                        "error": stt_response.text
                    }

            finally:
                # Cleanup if we generated the audio
                if cleanup_audio and audio_file and os.path.exists(audio_file):
                    os.unlink(audio_file)

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_tts_basic(self, text: str = "Hello, this is a test.") -> Dict[str, Any]:
        """Test basic TTS functionality."""
        try:
            payload = {"text": text, "voice": "lessac"}
            response = await self.client.post(
                f"{self.base_url}/voice/tts",
                json=payload
            )

            if response.status_code == 200:
                # Save audio for analysis
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(response.content)
                    audio_file = tmp.name

                # Analyze audio
                audio_info = await self._analyze_audio(audio_file)

                # Cleanup
                os.unlink(audio_file)

                return {
                    "success": True,
                    "status_code": response.status_code,
                    "audio_size": len(response.content),
                    **audio_info
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_voices_endpoint(self) -> Dict[str, Any]:
        """Test voices endpoint."""
        try:
            response = await self.client.get(f"{self.base_url}/voices")
            result = response.json()
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "voices_count": len(result.get("voices", [])),
                "voices": result.get("voices", [])
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_service_info(self) -> Dict[str, Any]:
        """Test service info endpoint."""
        try:
            response = await self.client.get(f"{self.base_url}/info")
            result = response.json()
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "service_info": result
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _analyze_audio(self, audio_file: str) -> Dict[str, Any]:
        """Analyze generated audio file."""
        try:
            audio_data, sample_rate = sf.read(audio_file)

            return {
                "sample_rate": sample_rate,
                "duration": len(audio_data) / sample_rate,
                "channels": audio_data.shape[1] if len(audio_data.shape) > 1 else 1,
                "dtype": str(audio_data.dtype),
                "has_audio": np.max(np.abs(audio_data)) > 0.001
            }
        except Exception as e:
            return {"audio_analysis_error": str(e)}


async def run_safe_tests():
    """Run all safe development tests."""
    print("🧪 Safe Voice Service Development Tests")
    print("=" * 50)

    async with SafeVoiceServiceTester() as tester:
        results = {}

        # 1. Health Check
        print("\n1. Health Check...")
        health = await tester.health_check()
        results["health"] = health
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   STT: {health.get('services', {}).get('stt', 'unknown')}")
        print(f"   TTS: {health.get('services', {}).get('tts', 'unknown')}")
        print(f"   VAD: {health.get('services', {}).get('vad', 'unknown')}")

        # 2. Service Info
        print("\n2. Service Info...")
        info = await tester.test_service_info()
        results["info"] = info
        if info["success"]:
            print("   ✓ Service info retrieved")
        else:
            print(f"   ✗ Failed: {info.get('error', 'unknown')}")

        # 3. Basic STT Test
        print("\n3. Basic STT Test...")
        stt_result = await tester.test_stt_basic()
        results["stt"] = stt_result
        if stt_result["success"]:
            confidence = stt_result.get("confidence", 0)
            accuracy = stt_result.get("accuracy", 0)
            print(f"   ✓ STT Success: {confidence:.1%} confidence, {accuracy:.1%} accuracy")
            if stt_result.get("expected_text"):
                print(f"   📝 Expected: '{stt_result['expected_text']}'")
                print(f"   🎤 Got: '{stt_result['text']}'")
        else:
            print(f"   ✗ STT Failed: {stt_result.get('error', 'unknown')}")

        # 4. Basic TTS Test
        print("\n4. Basic TTS Test...")
        tts_result = await tester.test_tts_basic("Hello, this is a safe development test.")
        results["tts"] = tts_result
        if tts_result["success"]:
            duration = tts_result.get("duration", 0)
            sample_rate = tts_result.get("sample_rate", 0)
            print(f"   ✓ TTS Success: {duration:.2f}s audio at {sample_rate}Hz")
        else:
            print(f"   ✗ TTS Failed: {tts_result.get('error', 'unknown')}")

        # 5. Voices Endpoint
        print("\n5. Voices Endpoint...")
        voices_result = await tester.test_voices_endpoint()
        results["voices"] = voices_result
        if voices_result["success"]:
            count = voices_result.get("voices_count", 0)
            print(f"   ✓ {count} voices available")
        else:
            print(f"   ✗ Voices failed: {voices_result.get('error', 'unknown')}")

        # 6. Summary
        print("\n" + "=" * 50)
        print("📊 Test Summary:")

        success_count = sum(1 for r in results.values() if r.get("success", False))
        total_tests = len(results)
        skipped_count = sum(1 for r in results.values() if r.get("skipped", False))

        print(f"   Passed: {success_count}/{total_tests} (Skipped: {skipped_count})")

        if success_count == total_tests:
            print("   🎉 All tests passed! Voice service is ready for development.")
        elif success_count == total_tests - skipped_count:
            print("   🎉 All active tests passed! Voice service is ready for development.")
        else:
            print("   ⚠️  Some tests failed. Check service logs for details.")

        return results


async def test_basic_functionality():
    """Test just the core functionality."""
    print("🧪 Basic Functionality Test")

    async with SafeVoiceServiceTester() as tester:
        # Quick health check
        health = await tester.health_check()
        if not health.get("success", False):
            print("❌ Service not healthy")
            return False

        # Quick TTS test
        tts = await tester.test_tts_basic("Test")
        if not tts["success"]:
            print("❌ TTS not working")
            return False

        print("✅ Basic functionality OK")
        return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--basic":
        # Run only basic functionality test
        result = asyncio.run(test_basic_functionality())
        sys.exit(0 if result else 1)
    else:
        # Run full safe test suite
        results = asyncio.run(run_safe_tests())
        success = all(r.get("success", False) for r in results.values())
        sys.exit(0 if success else 1)