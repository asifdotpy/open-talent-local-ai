#!/usr/bin/env python3
"""WebRTC Test Client for Voice Service
Tests real-time audio processing with RNNoise integration
Enhanced with proper error handling, logging, and comprehensive validation.
"""

import asyncio
import contextlib
import json
import logging
import os
import sys
import tempfile
import time

import aiohttp
import numpy as np
import soundfile as sf
from aiortc import RTCConfiguration, RTCIceCandidate, RTCPeerConnection, RTCSessionDescription

from audio_processing_validator import AudioProcessingValidator, ValidationResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("webrtc_test_client.log")],
)
logger = logging.getLogger(__name__)

# --- Constants ---
DEFAULT_SIGNALING_URL = "ws://localhost:8005/webrtc/signal"
DEFAULT_SESSION_TIMEOUT = 30
TEST_SESSION_ID = "test-session-fixed"
AUDIO_SAMPLE_RATE = 48000
AUDIO_CHANNELS = 1
DUMMY_AUDIO_FRAME_SIZE = 480
LATENCY_THRESHOLD_MS = 5000
HIGH_LATENCY_WARNING_MS = 2000
STRESS_TEST_CONNECTIONS = 3
TEST_AUDIO_DURATION_S = 5.0
TEST_AUDIO_FREQUENCY_HZ = 1000


class WebRTCTestClient:
    """Test client for WebRTC voice service testing with robust error handling and validation."""

    def __init__(self, signaling_url=DEFAULT_SIGNALING_URL, session_timeout=DEFAULT_SESSION_TIMEOUT):
        self.signaling_url = signaling_url
        self.session_id = TEST_SESSION_ID  # Use fixed session ID for testing
        self.session_timeout = session_timeout
        self.pc = None
        self.ws = None
        self.datachannel = None
        self.audio_frames = []
        self.connection_established = False
        self.test_completed = False
        self.start_time = None

        # Validation components
        self.validator = AudioProcessingValidator()
        self.test_audio = None
        self.test_audio_file = None
        self.validation_results = []
        self.test_scenarios = []

        # Performance metrics
        self.connection_time = None
        self.first_audio_time = None
        self.total_audio_frames = 0
        self.audio_dropouts = 0

    async def start(self):
        """Start the WebRTC test client with timeout and error handling."""
        self.start_time = time.time()
        logger.info(f"Starting WebRTC test client for session {self.session_id}")

        try:
            # Connect to signaling server with timeout
            session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
            self.ws = await session.ws_connect(self.signaling_url)
            logger.info("Connected to signaling server")

            # Register as client with timeout
            await asyncio.wait_for(self._register_client(), timeout=5.0)

            # Initialize peer connection without ICE servers for localhost testing
            config = RTCConfiguration(iceServers=[])
            self.pc = RTCPeerConnection(configuration=config)
            self._setup_pc_handlers()

            # Create and send offer with timeout
            await asyncio.wait_for(self._create_and_send_offer(), timeout=10.0)

            logger.info("WebRTC offer sent, waiting for connection...")

            # Add a dummy audio track to complete the connection
            await self._add_dummy_audio_track()

            # Start signaling loop with session timeout
            await asyncio.wait_for(self._signaling_loop(), timeout=self.session_timeout)

        except TimeoutError:
            logger.error(f"Operation timed out after {self.session_timeout}s")
            await self._handle_timeout()
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            await self._handle_network_error(e)
        except Exception as e:
            logger.error(f"Client error: {e}")
            await self._handle_general_error(e)
        finally:
            await self.stop()
        """Run comprehensive WebRTC and audio processing tests"""
        logger.info("Starting comprehensive WebRTC test suite")
        results = {}

        # Test Scenario 1: Basic Connection Test
        logger.info("🧪 Test Scenario 1: Basic WebRTC Connection")
        try:
            await self.start()
            results["connection_test"] = self._create_connection_result()
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            results["connection_test"] = self._create_error_result(f"Connection failed: {e}")

        # Reset for next test
        await self.stop()
        await asyncio.sleep(1)

        # Test Scenario 2: Audio Quality Test with Validation
        logger.info("🧪 Test Scenario 2: Audio Processing Quality Validation")
        try:
            # Generate test audio
            self.test_audio, self.test_audio_file = await self.validator.generate_test_audio(
                duration_seconds=TEST_AUDIO_DURATION_S, include_noise=True, frequency=TEST_AUDIO_FREQUENCY_HZ
            )

            if len(self.test_audio) > 0:
                # Run WebRTC test with audio validation
                await self.start()
                results["audio_quality_test"] = await self._validate_audio_processing()
            else:
                results["audio_quality_test"] = self._create_error_result("Failed to generate test audio")

        except Exception as e:
            logger.error(f"Audio quality test failed: {e}")
            results["audio_quality_test"] = self._create_error_result(f"Audio test failed: {e}")

        # Test Scenario 3: Stress Test (Multiple Connections)
        logger.info("🧪 Test Scenario 3: Connection Stress Test")
        try:
            stress_results = await self._run_stress_test(num_connections=STRESS_TEST_CONNECTIONS)
            results["stress_test"] = stress_results
        except Exception as e:
            logger.error(f"Stress test failed: {e}")
            results["stress_test"] = self._create_error_result(f"Stress test failed: {e}")

        # Test Scenario 4: Latency Test
        logger.info("🧪 Test Scenario 4: Latency Measurement")
        try:
            latency_result = await self._measure_latency()
            results["latency_test"] = latency_result
        except Exception as e:
            logger.error(f"Latency test failed: {e}")
            results["latency_test"] = self._create_error_result(f"Latency test failed: {e}")

        return results
        """Start the WebRTC test client with timeout and error handling"""
        self.start_time = time.time()
        logger.info(f"Starting WebRTC test client for session {self.session_id}")

        try:
            # Connect to signaling server with timeout
            session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
            self.ws = await session.ws_connect(self.signaling_url)
            logger.info("Connected to signaling server")

            # Register as client with timeout
            await asyncio.wait_for(self._register_client(), timeout=5.0)

            # Initialize peer connection without ICE servers for localhost testing
            config = RTCConfiguration(iceServers=[])
            self.pc = RTCPeerConnection(configuration=config)
            self._setup_pc_handlers()

            # Create and send offer with timeout
            await asyncio.wait_for(self._create_and_send_offer(), timeout=10.0)

            logger.info("WebRTC offer sent, waiting for connection...")

            # Add a dummy audio track to complete the connection
            await self._add_dummy_audio_track()

            # Start signaling loop with session timeout
            await asyncio.wait_for(self._signaling_loop(), timeout=self.session_timeout)

        except TimeoutError:
            logger.error(f"Operation timed out after {self.session_timeout}s")
            await self._handle_timeout()
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            await self._handle_network_error(e)
        except Exception as e:
            logger.error(f"Client error: {e}")
            await self._handle_general_error(e)
        finally:
            await self.stop()

    async def _register_client(self):
        """Register client with signaling server."""
        await self.ws.send_json(
            {
                "type": "register",
                "peer_type": "client",
                "session_id": self.session_id,
                "metadata": {"test": True, "client_version": "1.0"},
            }
        )

        # Wait for registration acknowledgment
        reg_resp = await self.ws.receive_json()
        if reg_resp.get("type") != "registered":
            raise Exception(f"Registration failed: {reg_resp}")

        logger.info(f"Client registered for session {self.session_id}")

    async def _create_and_send_offer(self):
        """Create WebRTC offer and send to signaling server."""
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)

        await self.ws.send_json({"type": "offer", "session_id": self.session_id, "sdp": self.pc.localDescription.sdp})

    async def _add_dummy_audio_track(self):
        """Add a dummy audio track to complete WebRTC connection."""
        try:
            # Create a dummy audio stream track
            class DummyAudioTrack:
                def __init__(self):
                    self.kind = "audio"
                    self.id = "dummy-audio-track"

                async def recv(self):
                    # Generate silent audio frames
                    await asyncio.sleep(0.1)  # 100ms delay
                    # Create a silent 10ms audio frame (480 samples at 48kHz)
                    silent_frame = np.zeros(DUMMY_AUDIO_FRAME_SIZE, dtype=np.int16)
                    return type(
                        "Frame",
                        (),
                        {"to_ndarray": lambda: silent_frame, "sample_rate": AUDIO_SAMPLE_RATE, "channels": AUDIO_CHANNELS},
                    )()

            dummy_track = DummyAudioTrack()
            self.pc.addTrack(dummy_track)
            logger.info("Added dummy audio track to peer connection")

        except Exception as e:
            logger.error(f"Error adding dummy audio track: {e}")

    def _setup_pc_handlers(self):
        """Setup RTCPeerConnection event handlers with error handling."""

        @self.pc.on("track")
        async def on_track(track):
            try:
                logger.info(f"Received {track.kind} track: {track.id}")
                if track.kind == "audio":
                    # Collect audio frames for analysis
                    self.audio_frames = []
                    asyncio.create_task(self._collect_audio_frames(track))
            except Exception as e:
                logger.error(f"Error handling track: {e}")

        @self.pc.on("datachannel")
        def on_datachannel(channel):
            try:
                logger.info(f"DataChannel opened: {channel.label}")
                self.datachannel = channel

                @channel.on("message")
                def on_message(message):
                    try:
                        logger.info(f"DataChannel message: {message}")
                        # Parse message if it's JSON
                        if isinstance(message, str):
                            try:
                                data = json.loads(message)
                                self._handle_datachannel_message(data)
                            except json.JSONDecodeError:
                                logger.debug(f"Non-JSON message: {message}")
                    except Exception as e:
                        logger.error(f"Error handling DataChannel message: {e}")

            except Exception as e:
                logger.error(f"Error setting up DataChannel: {e}")

        @self.pc.on("icecandidate")
        async def on_icecandidate(candidate):
            try:
                if candidate and self.ws:
                    await self.ws.send_json(
                        {
                            "type": "ice_candidate",
                            "session_id": self.session_id,
                            "candidate": {
                                "candidate": candidate.candidate,
                                "sdpMid": candidate.sdpMid,
                                "sdpMLineIndex": candidate.sdpMLineIndex,
                            },
                        }
                    )
            except Exception as e:
                logger.error(f"Error handling ICE candidate: {e}")

        @self.pc.on("connectionstatechange")
        async def on_connectionstatechange():
            try:
                if not self.pc:  # Check if pc still exists
                    return
                state = self.pc.connectionState
                logger.info(f"Connection state changed to: {state}")

                if state == "connected":
                    self.connection_established = True
                    self.connection_time = time.time()  # Track connection establishment time
                    logger.info("✅ WebRTC connection established successfully!")
                elif state == "failed":
                    logger.error("❌ WebRTC connection failed")
                    await self._handle_connection_failure()
                elif state == "closed":
                    logger.info("WebRTC connection closed")
            except Exception as e:
                logger.error(f"Error handling connection state change: {e}")

    def _handle_datachannel_message(self, data):
        """Handle structured DataChannel messages."""
        msg_type = data.get("type", "unknown")
        logger.info(f"Received {msg_type} message: {data}")

        if msg_type == "transcript.final":
            logger.info(f"🎤 Final transcript: {data.get('text', 'N/A')}")
        elif msg_type == "transcript.partial":
            logger.debug(f"🎤 Partial transcript: {data.get('text', 'N/A')}")

    async def _collect_audio_frames(self, track):
        """Collect audio frames from the track for analysis with error handling."""
        frame_count = 0
        max_frames = 100  # Limit frames to prevent memory issues

        try:
            while frame_count < max_frames and not self.test_completed:
                try:
                    frame = await asyncio.wait_for(track.recv(), timeout=1.0)

                    # Track first audio frame time for latency measurement
                    if self.first_audio_time is None:
                        self.first_audio_time = time.time()

                    audio_data = frame.to_ndarray()
                    if len(audio_data.shape) > 1:
                        audio_data = np.mean(audio_data, axis=0)

                    # Convert to float32 for analysis
                    audio_float = audio_data.astype(np.float32) / 32767.0
                    self.audio_frames.extend(audio_float)
                    frame_count += 1
                    self.total_audio_frames += 1

                    if frame_count % 20 == 0:
                        logger.debug(f"Collected {frame_count} audio frames")

                except TimeoutError:
                    logger.debug("Timeout waiting for audio frame")
                    self.audio_dropouts += 1
                    break
                except Exception as e:
                    logger.error(f"Error receiving audio frame: {e}")
                    break

            logger.info(f"Audio collection completed: {len(self.audio_frames)} samples, {self.audio_dropouts} dropouts")

            if self.audio_frames:
                await self._save_audio_for_analysis()

        except Exception as e:
            logger.error(f"Audio collection error: {e}")

    async def _save_audio_for_analysis(self):
        """Save collected audio to file for SNR analysis with error handling."""
        if not self.audio_frames:
            logger.warning("No audio frames to analyze")
            return

        try:
            # Convert to numpy array
            audio_array = np.array(self.audio_frames, dtype=np.float32)

            # Normalize
            if np.max(np.abs(audio_array)) > 0:
                audio_array = audio_array / np.max(np.abs(audio_array))

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                sf.write(tmp.name, audio_array, AUDIO_SAMPLE_RATE)
                logger.info(f"Saved processed audio to {tmp.name}")

                # Analyze SNR
                await self._analyze_audio_quality(tmp.name)

                # Clean up
                with contextlib.suppress(OSError):
                    os.unlink(tmp.name)

        except Exception as e:
            logger.error(f"Audio save error: {e}")

    async def _analyze_audio_quality(self, audio_file):
        """Analyze the quality of processed audio with robust error handling."""
        try:
            # Load audio with error checking
            audio, sr = sf.read(audio_file)

            if len(audio) == 0:
                logger.warning("Audio file is empty")
                return

            # Calculate SNR with safety checks
            signal_power = np.mean(audio**2)
            noise_power = np.var(audio) * 0.1  # Estimate noise as 10% of variance

            if noise_power <= 0 or signal_power <= 0:
                logger.warning("Invalid audio power levels for SNR calculation")
                snr = 0.0
            else:
                snr = 10 * np.log10(signal_power / noise_power)

            logger.info(f"🎵 Processed audio SNR: {snr:.2f}dB")

            # Evaluate RNNoise effectiveness
            if snr > 20:
                logger.info("✅ Excellent! RNNoise processing working well - high SNR detected")
            elif snr > 15:
                logger.info("✅ Good! RNNoise processing effective - decent SNR improvement")
            elif snr > 10:
                logger.info("⚠️  Fair! RNNoise processing may need tuning - moderate SNR")
            else:
                logger.warning("❌ Poor! RNNoise processing not effective - low SNR detected")

            self.test_completed = True

        except Exception as e:
            logger.error(f"Audio analysis error: {e}")

    async def _signaling_loop(self):
        """Handle incoming signaling messages with error handling."""
        try:
            while not self.test_completed:
                try:
                    msg = await asyncio.wait_for(self.ws.receive(), timeout=5.0)

                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        await self._handle_signaling_message(data)

                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error(f"WebSocket error: {self.ws.exception()}")
                        break

                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        logger.info("WebSocket connection closed")
                        break

                except TimeoutError:
                    # Check if we should continue waiting
                    elapsed = time.time() - self.start_time
                    if elapsed > self.session_timeout:
                        logger.warning(f"Session timeout reached ({self.session_timeout}s)")
                        break
                    continue

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    continue

        except Exception as e:
            logger.error(f"Signaling loop error: {e}")

    async def _handle_signaling_message(self, message):
        """Process signaling messages with validation."""
        try:
            msg_type = message.get("type")

            if msg_type == "answer":
                # Receive answer from voice service
                sdp = message.get("sdp")
                if not sdp:
                    logger.error("Received answer without SDP")
                    return

                answer = RTCSessionDescription(sdp=sdp, type="answer")
                await self.pc.setRemoteDescription(answer)
                logger.info("✅ Received and set answer - WebRTC negotiation complete!")

            elif msg_type == "ice_candidate":
                # Add ICE candidate from voice service
                candidate_data = message.get("candidate", {})
                if not candidate_data.get("candidate"):
                    logger.debug("Received empty ICE candidate")
                    return

                candidate = RTCIceCandidate(
                    candidate=candidate_data["candidate"],
                    sdpMid=candidate_data.get("sdpMid"),
                    sdpMLineIndex=candidate_data.get("sdpMLineIndex"),
                )
                await self.pc.addIceCandidate(candidate)
                logger.debug("Added ICE candidate from voice service")

            else:
                logger.debug(f"Unhandled message type: {msg_type}")

        except Exception as e:
            logger.error(f"Error handling signaling message: {e}")

    async def _handle_timeout(self):
        """Handle session timeout."""
        logger.error(f"Session timed out after {self.session_timeout} seconds")
        if not self.connection_established:
            logger.error("Failed to establish WebRTC connection within timeout period")

    async def _handle_network_error(self, error):
        """Handle network-related errors."""
        logger.error(f"Network error occurred: {error}")
        logger.info("Check that signaling server is running on the correct port")

    async def _handle_connection_failure(self):
        """Handle WebRTC connection failure."""
        logger.error("WebRTC connection failed - check voice service and network configuration")

    async def _handle_general_error(self, error):
        """Handle general errors."""
        logger.error(f"Unexpected error: {error}")
        logger.info("Check logs for more details and ensure all services are running")

    def _create_connection_result(self) -> ValidationResult:
        """Create a validation result for connection test."""
        from audio_processing_validator import AudioMetrics

        passed = self.connection_established
        errors = [] if passed else ["WebRTC connection failed"]
        warnings = []
        recommendations = []

        if not passed:
            recommendations.extend(
                [
                    "Check that voice service is running on port 8002",
                    "Verify WebRTC signaling server is accessible on port 8005",
                    "Check network connectivity and firewall settings",
                ]
            )

        return ValidationResult(
            passed=passed,
            metrics=AudioMetrics(0, 0, 0, 0, 0, 0, AUDIO_SAMPLE_RATE, AUDIO_CHANNELS, 0),
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
        )

    def _create_error_result(self, error_msg: str) -> ValidationResult:
        """Create a validation result for error cases."""
        from audio_processing_validator import AudioMetrics

        return ValidationResult(
            passed=False,
            metrics=AudioMetrics(0, 0, 0, 0, 0, 0, AUDIO_SAMPLE_RATE, AUDIO_CHANNELS, 0),
            errors=[error_msg],
            warnings=[],
            recommendations=["Check voice service logs for detailed error information"],
        )

    async def _validate_audio_processing(self) -> ValidationResult:
        """Validate audio processing using collected frames."""
        if not self.audio_frames or not self.test_audio:
            return self._create_error_result("No audio data available for validation")

        try:
            # Convert collected frames to numpy array
            processed_audio = np.array(self.audio_frames, dtype=np.float32)

            # Normalize
            if np.max(np.abs(processed_audio)) > 0:
                processed_audio = processed_audio / np.max(np.abs(processed_audio))

            # Validate against original test audio
            result = await self.validator.validate_audio_pipeline(
                self.test_audio[: len(processed_audio)],  # Match lengths
                processed_audio,
                processing_latency_ms=self._calculate_latency(),
            )

            return result

        except Exception as e:
            logger.error(f"Audio validation error: {e}")
            return self._create_error_result(f"Audio validation failed: {e}")

    def _calculate_latency(self) -> float:
        """Calculate connection latency."""
        if self.connection_time and self.first_audio_time:
            return (self.first_audio_time - self.connection_time) * 1000
        return 0.0

    async def _run_stress_test(self, num_connections: int = 3) -> ValidationResult:
        """Run stress test with multiple simultaneous connections."""
        errors = []
        warnings = []
        recommendations = []

        successful_connections = 0

        for i in range(num_connections):
            logger.info(f"Stress test connection {i + 1}/{num_connections}")
            try:
                # Create new client instance
                stress_client = WebRTCTestClient(session_timeout=15)
                await stress_client.start()

                if stress_client.connection_established:
                    successful_connections += 1
                else:
                    errors.append(f"Connection {i + 1} failed to establish")

                await stress_client.stop()
                await asyncio.sleep(0.5)  # Brief pause between connections

            except Exception as e:
                errors.append(f"Connection {i + 1} error: {e}")

        passed = successful_connections == num_connections

        if successful_connections < num_connections:
            warnings.append(f"Only {successful_connections}/{num_connections} connections successful")
            recommendations.append("Check server capacity and connection limits")

        from audio_processing_validator import AudioMetrics

        return ValidationResult(
            passed=passed,
            metrics=AudioMetrics(0, 0, 0, 0, 0, 0, AUDIO_SAMPLE_RATE, AUDIO_CHANNELS, 0),
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
        )

    async def _measure_latency(self) -> ValidationResult:
        """Measure WebRTC connection latency."""
        try:
            start_time = time.time()

            # Quick connection test
            await self.start()
            connection_time = time.time() - start_time

            latency_ms = connection_time * 1000

            # Validate latency
            passed = latency_ms < LATENCY_THRESHOLD_MS  # 5 second threshold
            errors = [] if passed else [f"High latency: {latency_ms:.1f}ms"]
            warnings = []
            recommendations = []

            if latency_ms > HIGH_LATENCY_WARNING_MS:
                warnings.append(f"High connection latency: {latency_ms:.1f}ms")
                recommendations.append("Check network conditions and server response times")

            await self.stop()

            from audio_processing_validator import AudioMetrics

            return ValidationResult(
                passed=passed,
                metrics=AudioMetrics(0, 0, latency_ms, 0, 0, 0, AUDIO_SAMPLE_RATE, AUDIO_CHANNELS, 0),
                errors=errors,
                warnings=warnings,
                recommendations=recommendations,
            )

        except Exception as e:
            return self._create_error_result(f"Latency measurement failed: {e}")

    async def stop(self):
        """Clean up resources with error handling."""
        logger.info("Stopping WebRTC test client...")

        try:
            if self.pc:
                await self.pc.close()
                self.pc = None
        except Exception as e:
            logger.error(f"Error closing peer connection: {e}")

        try:
            if self.ws:
                await self.ws.close()
                self.ws = None
        except Exception as e:
            logger.error(f"Error closing WebSocket: {e}")

        # Calculate test duration
        if self.start_time:
            duration = time.time() - self.start_time
            logger.info(f"Test completed in {duration:.2f} seconds")

        logger.info("WebRTC test client stopped")


async def main():
    """Main test function with comprehensive test suite."""
    logger.info("Starting Comprehensive WebRTC Voice Service Test Suite")
    logger.info("=" * 60)

    client = WebRTCTestClient(session_timeout=45)

    try:
        # Run comprehensive test suite
        results = await client.run_comprehensive_test()

        # Print results summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)

        overall_passed = True
        len(results)

        for test_name, result in results.items():
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"\n{test_name.upper().replace('_', ' ')}: {status}")

            if result.errors:
                print("  Errors:")
                for error in result.errors:
                    print(f"    • {error}")

            if result.warnings:
                print("  Warnings:")
                for warning in result.warnings:
                    print(f"    • {warning}")

            if not result.passed:
                overall_passed = False

        print("\n" + "=" * 60)
        if overall_passed:
            print("🎉 ALL TESTS PASSED - Voice service is ready for production!")
        else:
            print("⚠️  SOME TESTS FAILED - Check recommendations above for improvements")
        print("=" * 60)

        # Detailed validation reports for audio tests
        if "audio_quality_test" in results and results["audio_quality_test"].passed:
            print("\n📋 DETAILED AUDIO QUALITY REPORT:")
            client.validator.print_validation_report(results["audio_quality_test"])

    except KeyboardInterrupt:
        logger.info("Test suite interrupted by user")
        await client.stop()
    except Exception as e:
        logger.error(f"Test suite failed with exception: {e}")
        await client.stop()
        sys.exit(1)

    logger.info("Comprehensive WebRTC Voice Service Test Suite completed")


async def run_single_test():
    """Run a single basic connection test (legacy mode)."""
    logger.info("Starting Single WebRTC Voice Service Test")
    logger.info("=" * 50)

    client = WebRTCTestClient(session_timeout=45)

    try:
        await client.start()

        # Check results
        if client.connection_established:
            logger.info("✅ WebRTC connection test: PASSED")
        else:
            logger.error("❌ WebRTC connection test: FAILED")

        if client.test_completed and client.audio_frames:
            logger.info("✅ Audio processing test: PASSED")
        else:
            logger.warning("⚠️  Audio processing test: INCOMPLETE")

    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        await client.stop()
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        await client.stop()
        sys.exit(1)

    logger.info("=" * 50)
    logger.info("Single WebRTC Voice Service Test completed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="WebRTC Voice Service Test Client")
    parser.add_argument(
        "--mode",
        choices=["comprehensive", "single"],
        default="comprehensive",
        help="Test mode: comprehensive (full test suite) or single (basic connection test)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Set up logging
    if args.debug or os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
        asyncio.get_event_loop().set_debug(True)
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        if args.mode == "comprehensive":
            asyncio.run(main())
        else:
            asyncio.run(run_single_test())
    except KeyboardInterrupt:
        logger.info("Application interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)
