from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel, Field, constr, validator

try:
    from rules import RULES  # when loaded as a module without package context
    KNOWN_RULE_IDS: ClassVar[set[str]] = set(RULES.keys())
except Exception:
    # Fallback for import contexts where rules cannot be imported
    KNOWN_RULE_IDS: ClassVar[set[str]] = {"enum_validation", "secret_detection"}


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditRule(BaseModel):
    id: constr(strip_whitespace=True, min_length=1)
    name: constr(strip_whitespace=True, min_length=1)
    description: str | None = None
    severity: Severity = Field(default=Severity.MEDIUM)
    enabled: bool = True


class AuditRunRequest(BaseModel):
    target: constr(strip_whitespace=True, min_length=1)  # repo/path/service identifier
    ruleset: list[str] | None = None  # list of rule ids to apply (None => default set)
    config_overrides: dict[str, Any] | None = None


class AuditJobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AuditFinding(BaseModel):
    rule_id: constr(strip_whitespace=True, min_length=1)
    message: constr(strip_whitespace=True, min_length=1)
    severity: Severity
    file: str | None = None
    line: int | None = None
    remediation: str | None = None


class AuditJobStatusResponse(BaseModel):
    job_id: constr(strip_whitespace=True, min_length=1)
    status: AuditJobStatus
    started_at: str | None = None
    finished_at: str | None = None
    progress: float | None = Field(default=0.0, ge=0.0, le=100.0)


class AuditReportResponse(BaseModel):
    job_id: constr(strip_whitespace=True, min_length=1)
    target: str
    findings: list[AuditFinding]
    summary: dict[str, Any]  # counts by severity, files scanned, duration


# Known rule IDs for validation, sourced from central registry or fallback

class AuditConfig(BaseModel):
    default_ruleset: list[str] = Field(default_factory=list)
    fail_on_severity: Severity = Field(default=Severity.HIGH)
    max_findings: int = Field(default=1000, ge=1)

    @validator("default_ruleset")
    def validate_default_ruleset(self, v):
        unknown = [rid for rid in v if rid not in KNOWN_RULE_IDS]
        if unknown:
            raise ValueError(f"Unknown rule IDs in default_ruleset: {unknown}")
        return v


class AuditHistoryItem(BaseModel):
    job_id: str
    target: str
    status: AuditJobStatus
    created_at: str
    finished_at: str | None = None
    summary: dict[str, Any] | None = None
