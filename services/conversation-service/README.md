# Conversation Service

AI-powered conversation management for interview automation. Provides endpoints for starting and managing interview conversations, adaptive question generation, follow-up questions, and interview strategy adaptation.

## Environment Flags

- `USE_MOCK_OLLAMA` (default: `true`)
  - When `true`, uses mock generation for LLM calls. Fast and deterministic for tests.
  - Set to `false` to use the configured LLM provider (Ollama).
- `OLLAMA_MODEL` (default: `granite4:350m-h`)
  - Model name used by the Ollama provider. You can switch personas via endpoint which maps to alternate model names.
- `OLLAMA_HOST` (default: `http://localhost:11434`)
  - Base URL for the local Ollama server.
- `ENABLE_STREAMING_LLM` (default: `true`)
  - Enables streaming responses for certain generation flows when supported.
- `LLM_PROVIDER` (default: `ollama`)
  - Primary LLM provider. Supported values include `ollama`, `mock` (for development).

## Quick Run

### Run Tests

```bash
# Activate venv
source .venv-1/bin/activate

# Recommended: keep mock mode enabled for tests
export USE_MOCK_OLLAMA=true
export OLLAMA_MODEL=granite4:350m-h

# Run the conversation-service tests
python -m pytest services/conversation-service/tests -q
```

### Start the Service (Dev)

```bash
# Activate venv
source .venv-1/bin/activate

# Use mock by default; switch to Ollama by setting USE_MOCK_OLLAMA=false
export USE_MOCK_OLLAMA=true
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=granite4:350m-h

# Run dev server
python services/conversation-service/main.py
# or
uvicorn services.conversation-service.main:app --host 0.0.0.0 --port 8003
```

### Persona Switching

The service supports interviewer persona switching when using the Ollama provider.

```bash
# Switch persona
curl -X POST http://localhost:8003/api/v1/persona/switch \
  -H 'Content-Type: application/json' \
  -d '{"persona":"technical"}'

# Get current persona
curl http://localhost:8003/api/v1/persona/current
```

## Endpoints Overview

- `POST /conversation/start` – Start a conversation
- `POST /conversation/message` – Send a message (transcript/user_input/system)
- `GET  /conversation/status/{session_id}` – Get status
- `POST /conversation/end/{session_id}` – End conversation
- `POST /conversation/generate-questions` – Generate interview questions via LLM
- `POST /api/v1/conversation/generate-adaptive-question` – Adaptive next question
- `POST /api/v1/conversation/generate-followup` – Follow-up questions
- `POST /api/v1/conversation/adapt-interview` – Strategy adaptation

## Notes

- Tests set environment defaults in `tests/conftest.py` to ensure mock behavior and fast runs.
- When integrating with Ollama, ensure the model is pulled and the server is running: `ollama pull granite4:350m-h` then `ollama serve`.
