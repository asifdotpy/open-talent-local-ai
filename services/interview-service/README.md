# Interview Service

Manages interview rooms, participants, WebRTC signaling, transcription, and AI intelligence operations.

## Environment Flags

- `ALLOW_ORIGINS` (CORS; optional)
  - Comma-separated allowed origins; defaults include local dev ports.
- `TIMEOUT_CONFIG` (internal)
  - Tunable timeouts for health, room ops, and service integration.
- `USE_MOCK_OLLAMA` (optional; default varies by service)
  - When integrating with conversation-service for AI questions, set `USE_MOCK_OLLAMA=true` on conversation-service for local tests.
- `OLLAMA_HOST` (optional)
  - Base URL for Ollama when conversation-service uses Ollama.

## Quick Run

### Run Tests

```bash
# Activate venv
source .venv-1/bin/activate

# Run interview-service tests (unit + integration)
python -m pytest services/interview-service/tests -q
```

### Start the Service (Dev)

```bash
# Activate venv
source .venv-1/bin/activate

# Start dev server
python services/interview-service/main.py
# or
uvicorn services.interview-service.main:app --host 0.0.0.0 --port 8004
```

### Minimal Endpoint Examples

```bash
# Create a room
curl -X POST http://localhost:8004/api/v1/rooms/create \
  -H 'Content-Type: application/json' \
  -d '{
    "interview_session_id": "sess-1",
    "participants": [
      {"user_id":"candidate-1","role":"candidate","display_name":"Jane Candidate"},
      {"user_id":"interviewer-1","role":"interviewer","display_name":"John Interviewer"}
    ],
    "duration_minutes": 30
  }'

# Get next question (minimal payload)
curl -X POST http://localhost:8004/api/v1/rooms/<room_id>/next-question -H 'Content-Type: application/json' -d '{}'

# Analyze response (minimal required fields)
curl -X POST http://localhost:8004/api/v1/rooms/<room_id>/analyze-response \
  -H 'Content-Type: application/json' \
  -d '{
    "question_id": "q-1",
    "response_text": "Brief answer",
    "question_context": "General",
    "participant_id": "candidate-1"
  }'

# Adapt interview (minimal required fields)
curl -X POST http://localhost:8004/api/v1/rooms/<room_id>/adapt-interview \
  -H 'Content-Type: application/json' \
  -d '{
    "current_phase": "technical",
    "time_remaining_minutes": 10
  }'
```

## Notes

- For AI question generation, the service calls conversation-service (`/conversation/generate-adaptive-question`). If conversation-service is not running, the endpoint falls back to a generated default question.
- WebRTC and WebSocket endpoints are present; refer to source for signaling and streaming message formats.
