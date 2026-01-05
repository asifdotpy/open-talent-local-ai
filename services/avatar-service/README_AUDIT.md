# Service Audit Results: avatar-service

**Location**: `/home/asif1/open-talent/services/avatar-service`
**Type**: FastAPI (with Node.js renderer)

## Endpoints

### Base / System

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service info |
| `GET` | `/health` | Health check |
| `GET` | `/ping` | Heartbeat |
| `GET` | `/doc`, `/api-docs` | Documentation helpers |
| `POST` | `/render/lipsync` | Direct render call (invokes Node.js) |

### Avatar V1 API (`/api/v1/avatars`)

*Extensive scaffold API for avatar management*
| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/render`, `/render/sequence` | Render requests |
| `POST` | `/lipsync`, `/lipsync/preview` | Lipsync operations |
| `GET/POST` | `/presets` | Preset management |
| `POST` | `/customize` | Customize avatar traits |
| `GET/PATCH` | `/{avatar_id}/state` | Avatar state management |
| `POST` | `/phonemes`, `/phonemes/timing` | Phoneme calculation |
| `GET/PATCH` | `/{avatar_id}/emotions` | Emotion control |
| `GET/PUT` | `/config` | Service configuration |
| `GET` | `/performance` | Performance metrics |
| `GET/POST` | `/{avatar_id}/snapshot` | Screenshot generation |
| `GET/POST` | `/assets` | Asset management |
| `GET/POST` | `/models` | Model selection |
| `POST/DEL` | `/session` | Session management |
| `POST/DEL` | `/voice/attach`, `/voice/detach` | Voice integration |
| `WS` | `/{avatar_id}/stream` | Avatar streaming WebSocket |

### Legacy/Direct Routes (Root)

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/src/{path}`, `/assets/{path}` | Serve static assets |
| `POST` | `/generate` | Generate video from text |
| `POST` | `/generate-from-audio` | Generate from audio file |
| `GET/POST` | `/phonemes`, `/set-phonemes` | Session phoneme data |
| `GET` | `/info` | Avatar service info |

### Voice Routes (`/api/v1`)

| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/generate-voice` | Generate voice (US English) |
| `GET` | `/voices` | List voices |

## Mock Data / Simulation Findings

1. **In-Memory Scaffolding**: `avatar_v1.py` relies entirely on in-memory dictionaries (`avatars`, `presets`, `sessions`) which reset on restart.
2. **Mock Renderer Mode**: `renderer/render.js` checks `process.env.SKIP_RENDERING` to return mock video metadata without rendering.
3. **Hardcoded Responses**:
    - `/performance` returns constant FPS/GPU load.
    - `/phonemes` returns hardcoded phoneme sequences.
    - `health_check` reports "healthy" with static component status.
