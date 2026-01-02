# AI Auditing Service

Planned auditing endpoints for code quality, security, and compliance checks.

## Endpoints

- `GET /` — Service root
- `GET /health` — Health check
- `POST /api/v1/audit/run` — Trigger an audit job
- `GET /api/v1/audit/status/{job_id}` — Check audit job status
- `GET /api/v1/audit/report/{job_id}` — Fetch audit results
- `GET /api/v1/audit/rules` — List audit rules
- `GET /api/v1/audit/config` — Get audit configuration
- `PUT /api/v1/audit/config` — Update audit configuration
- `GET /api/v1/audit/history` — List recent audit jobs

## Models

- `AuditRunRequest` — `{ target, ruleset?, config_overrides? }`
- `AuditJobStatusResponse` — `{ job_id, status, started_at?, finished_at?, progress }`
- `AuditReportResponse` — `{ job_id, target, findings[], summary }`
- `AuditRule` — `{ id, name, description?, severity, enabled }`
- `AuditConfig` — `{ default_ruleset[], fail_on_severity, max_findings }`
- `AuditHistoryItem` — `{ job_id, target, status, created_at, finished_at?, summary? }`

## Quick Run

```bash
cd services/ai-auditing-service
uvicorn main:app --port 8012 --reload
```

## Tests

```bash
pytest services/ai-auditing-service/tests/test_planned_endpoints.py -v
```

## Notes

- This is a scaffold with in-memory stores for jobs, rules, and config.
- Replace with queue/DB for production use.

## Rule Registry

- Centralized in `services/ai-auditing-service/rules.py`.
- Exposes:
  - `RULES`: dict of rule-id → `AuditRule` (source of truth for available rules).
  - `KNOWN_RULE_IDS`: set of valid rule IDs derived from `RULES`.
- `main.py` initializes `AuditConfig.default_ruleset` from `RULES.keys()` to avoid drift.
- `schemas.py` validates `AuditConfig.default_ruleset` against `KNOWN_RULE_IDS` and enforces `max_findings >= 1`.

### Adding a New Rule

- Edit `services/ai-auditing-service/rules.py` and add a new entry to `RULES`:

```python
RULES["your_new_rule"] = AuditRule(
  id="your_new_rule",
  name="Your New Rule",
  description="What the rule detects.",
  severity=Severity.MEDIUM,
  enabled=True,
)
```

- `KNOWN_RULE_IDS` updates automatically from `RULES.keys()`.
- Optionally update `CONFIG.default_ruleset` or use `/api/v1/audit/config` to include the new rule.
- Tests will fail with `422` on invalid configs if unknown rule IDs are used.
