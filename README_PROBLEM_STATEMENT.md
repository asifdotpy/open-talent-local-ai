# OpenTalent Platform: End-to-End Problem Statement & Audit

This document identifies the critical architectural and operational gaps preventing the OpenTalent platform from attaining production-level stability. It provides specific reproduction commands and technical evidence of existing failures.

## 1. Orchestration: Fragile Startup & Inaccurate Monitoring

### Current State

The `manage.sh` script relies on a "blind startup" model using PID tracking via `kill -0`. It does not verify service readiness at the application layer.

### Reproduction Command

```bash
./manage.sh start
```

### Observed failure (False Negative)

```text
⏳ Starting user-service on port 8001...
❌ user-service failed to start
...
⚠️ user-service health check timed out
```

**The Paradox**: Despite the `❌` indicator, a manual check often reveals the service is perfectly healthy:

```bash
curl -i http://localhost:8001/health
# Result: HTTP/1.1 200 OK
```

**Conclusion**: The health check interval and PID verification are out of sync with actual service initialization times, causing a "phantom failure" state that confuses developers and triggers unnecessary restarts.

---

## 2. Data Integrity: The "Mock Architecture" Barrier

### Problem Statement

Core services (`project-service`, `candidate-service`, `scout-service`) frequently bypass database logic and return hardcoded "sample data" to the client. This makes the platform look functional but prevents real-world usage.

### Reproduction: Project Service Mocks

```bash
curl http://localhost:8015/jobs/ANY_ID
```

**Response (Hardcoded)**:

```json
{
  "title": "Senior Software Engineer",
  "description": "Develop and maintain web applications.",
  "required_skills": ["Python", "FastAPI", "SQL", "Docker"]
}
```

*Note: This data is static in `services/project-service/app/main.py:40-49` and never queries a storage layer.*

### Reproduction: Candidate Service Mocks

```bash
grep -n "mock_candidate_ids" services/candidate-service/main.py
```

*Evidence of hardcoded logic path:*

```python
mock_candidate_ids = ["mock-id", "test-candidate", "demo-profile"]
if candidate_id in mock_candidate_ids:
    return mock_candidate_profile
```

---

## 3. Environment: Hardcoded Paths & Broken Dependencies

### Problem Statement

Services are built with rigid environmental assumptions that lead to total failure when deployed outside of a specific root directory structure.

### Detailed failure in Granite Interview Service

**Command**:

```bash
source .venv-1/bin/activate
cd services/granite-interview-service && python main.py
```

**Fatal Exception**:

```text
PermissionError: [Errno 13] Permission denied: '/app'
```

*Cause: `app/config/settings.py` expects a root `/app` directory, which exists in Docker but fails in standard Linux environments.*

---

## 4. Synthesis of Impact

| Layer | Issue | Impact |
| :--- | :--- | :--- |
| **Control** | Fragile `manage.sh` | Orchestration instability and false alarms. |
| **Content** | Mock-heavy controllers | Platform cannot be used for actual recruitment. |
| **Integrity** | Schema Inconsistency | Cross-service calls (e.g., Scout to User) fail on attribute errors. |

## 5. End-to-End Resolution Strategy

1. **Refactor `manage.sh`**: Implement a blocking `wait-for-it.sh` style health check that only returns "✅ Success" when HTTP 200 is reached.
2. **Unify Service Environment**: Replace all instances of `Path('/app/...')` with `Path(__file__).parent` based relative paths.
3. **Establish Data Persistence**: Transition `project-service` to a SQLite backend and ensure `candidate-service` strictly uses LanceDB/PostgreSQL.
4. **Standardize Pydantic**: Force all services to use a unified `BaseSettings` object with required `VERSION` and `PROJECT_NAME`.

---
> [!IMPORTANT]
> Until these foundational issues are resolved, "API Extraction" is merely documenting a simulation. We must stabilize the environment to document a platform.
