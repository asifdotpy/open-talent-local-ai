# Service Audit Results: candidate-service

**Location**: `/home/asif1/open-talent/services/candidate-service`
**Type**: FastAPI

## Endpoints

### Candidate Management

| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/candidates` | Create candidate |
| `GET` | `/api/v1/candidates` | List candidates (Pagination) |
| `GET` | `/api/v1/candidates/{id}` | Get candidate details |
| `PUT` | `/api/v1/candidates/{id}` | Update candidate |
| `DELETE` | `/api/v1/candidates/{id}` | Delete candidate |
| `PATCH` | `/api/v1/candidates/{id}/status` | Update candidate status |
| `GET` | `/api/v1/candidates/search` | Search (Vector or Text) |
| `POST` | `/api/v1/candidates/bulk` | Bulk import |
| `GET` | `/api/v1/candidates/bulk/export` | Bulk export |

### Applications

| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/applications` | Create application |
| `GET` | `/api/v1/applications` | List applications |
| `GET` | `/api/v1/candidates/{id}/applications` | Get candidate apps |
| `PATCH` | `/api/v1/applications/{id}` | Update application status |

### Profile Components

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET/POST` | `/api/v1/candidates/{id}/resume` | Resume management |
| `GET/POST` | `/api/v1/candidates/{id}/skills` | Skill management |
| `GET/POST` | `/api/v1/candidates/{id}/interviews` | Interview scheduling |
| `PUT/DELETE` | `/api/v1/candidates/{id}/interviews/{id}` | Interview management |
| `GET/POST` | `/api/v1/candidates/{id}/assessments` | Assessment tracking |

## Mock Data / Simulation Findings

1. **In-Memory Storage**: The service relies heavily on global dictionaries (`candidates_db`, `applications_db`, `interviews_db`, etc.) for storage. Data is lost on restart.
2. **Vector Search Fallback**: While `LanceDB` is implemented, the service gracefully degrades to "basic text match" identifying candidates by name loop if vector search is unavailable.
3. **Auth Stub**: `get_current_user` accepts any token matching `test-token-12345` or defaults to `test-user-001`.
4. **Heuristics**: Search filtering uses heuristics (e.g., estimating experience years from number of interviews).
