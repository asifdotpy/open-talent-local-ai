# Service Audit Results: conversation-service

**Location**: `/home/asif1/open-talent/services/conversation-service`
**Type**: FastAPI

## Endpoints

### Conversation Management

| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/conversation/start` | Start new interview session |
| `POST` | `/conversation/message` | Send message / Get AI response |
| `GET` | `/conversation/status/{session_id}` | Get session status |
| `POST` | `/conversation/end/{session_id}` | End session |

### Adaptive Intelligence

| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/conversation/generate-questions` | Generate questions (Ollama) |
| `POST` | `/api/v1/conversation/generate-adaptive-question` | Generate next context-aware question |
| `POST` | `/api/v1/conversation/generate-followup` | Generate follow-up questions |
| `POST` | `/api/v1/conversation/adapt-interview` | Strategy adaptation |

### Persona Management

| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/persona/switch` | Switch interviewer persona |
| `GET` | `/api/v1/persona/current` | Get current persona |

## Mock Data / Simulation Findings

1. **Persistence**: Unlike other services, this service uses **REAL** persistence via `DatabaseService`. It defaults to SQLite (`conversations.db`) but supports PostgreSQL.
2. **LLM Integration**: Uses `OllamaService` and `ModularLLMService` for real AI generation, not hardcoded strings.
3. **Real Logic**: Implements complex states, adaptive questioning logic, and persona management.
