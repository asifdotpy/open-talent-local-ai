# Deprecated: audio-service

This directory was temporarily scaffolded but is now deprecated. The canonical implementation for STT, TTS, VAD, WebRTC, and audio processing lives under `services/voice-service` and is consolidated to port 8015.

Actions taken:
- Consolidated Voice Service to port 8015 across configs and scripts.
- Retained voice-service WebRTC and testing tooling.

Next:
- Use `services/voice-service` only. This folder will be removed once pending references are cleaned up.
