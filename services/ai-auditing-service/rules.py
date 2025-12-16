from typing import Dict, Set
from schemas import AuditRule, Severity

# Central rule registry to keep RULES and validation aligned
RULES: Dict[str, AuditRule] = {
    "enum_validation": AuditRule(
        id="enum_validation",
        name="Enum Validation",
        description="Detects loose string enums.",
        severity=Severity.HIGH,
        enabled=True,
    ),
    "secret_detection": AuditRule(
        id="secret_detection",
        name="Secret Detection",
        description="Detects hardcoded secrets.",
        severity=Severity.CRITICAL,
        enabled=True,
    ),
}

KNOWN_RULE_IDS: Set[str] = set(RULES.keys())
