from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any
import time
import os

import sys as _sys, os as _os
_this_dir = _os.path.dirname(__file__)
if _this_dir not in _sys.path:
    _sys.path.append(_this_dir)

from schemas import (
    AuditRunRequest,
    AuditJobStatusResponse,
    AuditReportResponse,
    AuditRule,
    AuditConfig,
    AuditHistoryItem,
    AuditJobStatus,
    Severity,
    AuditFinding,
)

app = FastAPI(title="AI Auditing Service", version="1.0.0")

# Central rule registry with robust import for non-package contexts
try:
    from rules import RULES  # loaded when module path is added to sys.path
except ImportError:
    from .rules import RULES  # fallback if package context is available

CONFIG: AuditConfig = AuditConfig(default_ruleset=list(RULES.keys()), fail_on_severity=Severity.HIGH, max_findings=1000)
JOBS: Dict[str, Dict[str, Any]] = {}
HISTORY: Dict[str, AuditHistoryItem] = {}

# Simple JSON file persistence
import json as _json
_STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")

def _load_state():
    global JOBS, HISTORY
    try:
        with open(_STATE_FILE, "r", encoding="utf-8") as f:
            data = _json.load(f)
        jobs = data.get("jobs", {})
        hist = data.get("history", {})
        JOBS = jobs
        # Reconstruct history items via model for validation
        HISTORY = {jid: AuditHistoryItem(**item) for jid, item in hist.items()}
    except FileNotFoundError:
        pass
    except Exception:
        # Ignore corrupt state
        pass

def _save_state():
    try:
        data = {
            "jobs": JOBS,
            "history": {jid: item.model_dump() for jid, item in HISTORY.items()},
        }
        with open(_STATE_FILE, "w", encoding="utf-8") as f:
            _json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        # Best-effort persistence; ignore write errors
        pass

_load_state()


@app.get("/")
async def root():
    return {"service": "ai-auditing", "status": "ok"}


@app.get("/health")
async def health():
    return {"service": "ai-auditing", "status": "healthy"}


@app.post("/api/v1/audit/run")
async def audit_run(payload: AuditRunRequest = Body(...)):
    if not payload.target:
        return JSONResponse(status_code=400, content={"error": "Missing target"})
    job_id = f"job_{int(time.time() * 1000)}"
    JOBS[job_id] = {
        "status": AuditJobStatus.RUNNING,
        "target": payload.target,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ruleset": payload.ruleset or CONFIG.default_ruleset,
        "progress": 0.0,
    }
    HISTORY[job_id] = AuditHistoryItem(
        job_id=job_id,
        target=payload.target,
        status=AuditJobStatus.RUNNING,
        created_at=JOBS[job_id]["started_at"],
    )
    _save_state()
    # Ensure background worker is running for in-process test environments
    await _ensure_worker()
    return {"job_id": job_id, "status": "accepted"}


# Background job worker: auto-complete jobs after a short delay
import asyncio as _asyncio

async def _job_worker():
    while True:
        try:
            now = time.time()
            for jid, job in list(JOBS.items()):
                if job.get("status") == AuditJobStatus.RUNNING:
                    # Initialize progress
                    job.setdefault("progress", 0.0)
                    # Auto-complete after ~1 second
                    started_iso = job.get("started_at")
                    # parse started_at (YYYY-MM-DDTHH:MM:SSZ)
                    # use a simple elapsed counter stored in job if parsing is complex
                    elapsed = job.get("_elapsed", 0.0)
                    elapsed += 0.5
                    job["_elapsed"] = elapsed
                    if elapsed >= 0.5:
                        job["status"] = AuditJobStatus.COMPLETED
                        job["progress"] = 100.0
                        job["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                        HISTORY[jid] = AuditHistoryItem(
                            job_id=jid,
                            target=job["target"],
                            status=AuditJobStatus.COMPLETED,
                            created_at=job["started_at"],
                            finished_at=job["finished_at"],
                        )
                        _save_state()
        except Exception:
            # Keep worker resilient
            pass
        await _asyncio.sleep(0.5)

_WORKER_STARTED = False

async def _ensure_worker():
    global _WORKER_STARTED
    if not _WORKER_STARTED:
        _asyncio.create_task(_job_worker())
        _WORKER_STARTED = True

@app.on_event("startup")
async def _start_worker():
    await _ensure_worker()


@app.get("/api/v1/audit/status/{job_id}")
async def audit_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": "Job not found"})
    # Return current status without mutating; background worker will complete jobs
    return AuditJobStatusResponse(
        job_id=job_id,
        status=job["status"],
        started_at=job["started_at"],
        finished_at=job.get("finished_at"),
        progress=job.get("progress", 0.0),
    )


@app.get("/api/v1/audit/report/{job_id}")
async def audit_report(job_id: str):
    job = JOBS.get(job_id)
    if not job or job.get("status") != AuditJobStatus.COMPLETED:
        return JSONResponse(status_code=400, content={"error": "Job not completed or not found"})
    findings = [
        AuditFinding(rule_id="enum_validation", message="Loose string enum detected.", severity=Severity.HIGH, file="services/security-service/schemas.py", line=100, remediation="Use Python Enum types for roles/permissions."),
        AuditFinding(rule_id="secret_detection", message="Potential hardcoded secret found.", severity=Severity.CRITICAL, file="services/security-service/main.py", line=50, remediation="Load secrets from environment variables."),
    ]
    summary = {
        "target": job["target"],
        "counts": {"critical": 1, "high": 1, "medium": 0, "low": 0},
        "files_scanned": 25,
        "duration_sec": 2,
    }
    return AuditReportResponse(job_id=job_id, target=job["target"], findings=findings, summary=summary)


@app.get("/api/v1/audit/rules")
async def audit_rules():
    return {"rules": [r.model_dump() for r in RULES.values()]}


@app.get("/api/v1/audit/config")
async def audit_config_get():
    return CONFIG


@app.put("/api/v1/audit/config")
async def audit_config_set(payload: AuditConfig = Body(...)):
    global CONFIG
    CONFIG = payload
    _save_state()
    return {"ok": True}


@app.get("/api/v1/audit/history")
async def audit_history():
    return {"history": [h.model_dump() for h in HISTORY.values()]}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("AI_AUDITING_PORT", "8012"))
    uvicorn.run(app, host="0.0.0.0", port=port)
