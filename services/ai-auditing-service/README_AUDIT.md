# Service Audit Results: ai-auditing-service

**Location**: `/home/asif1/open-talent/services/ai-auditing-service`
**Type**: FastAPI

## Endpoints

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service identification |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/audit/run` | Start audit job |
| `GET` | `/api/v1/audit/status/{job_id}` | Check job status |
| `GET` | `/api/v1/audit/report/{job_id}` | Get audit report |
| `GET` | `/api/v1/audit/rules` | List available rules |
| `GET` | `/api/v1/audit/config` | Get configuration |
| `PUT` | `/api/v1/audit/config` | Update configuration |
| `GET` | `/api/v1/audit/history` | View audit history |

## Mock Data / Simulation Findings

1. **Hardcoded Findings**: In `audit_report` endpoint, findings are hardcoded (High/Critical severity).
2. **Simulated Worker**: `_job_worker` function simulates processing time (0.5s) and auto-completes jobs.
3. **Persistence**: Uses `state.json` for simple file-based persistence of jobs and history.
