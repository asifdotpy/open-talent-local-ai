#!/usr/bin/env python3
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    ROOT / "API_ENDPOINTS_QUICK_REFERENCE_DEC15.md",
    ROOT / "API_ENDPOINTS_SCHEMA_AUDIT_DEC15.md",
    ROOT / "AUDIT_INDEX_DEC15.md",
]
SCAN_SCRIPT = ROOT / "scripts/scan_endpoints.py"

TABLE_RE = re.compile(r"\|\s*(?P<service>[a-zA-Z0-9\-]+-service)\s*\|\s*(?P<count>\d+)\s*\|")


def run_scan():
    import subprocess
    res = subprocess.run([sys.executable, str(SCAN_SCRIPT)], capture_output=True, text=True)
    res.check_returncode()
    return res.stdout


def parse_scan(output: str):
    counts = {}
    for m in TABLE_RE.finditer(output):
        counts[m.group("service")] = int(m.group("count"))
    return counts


def parse_docs_counts():
    # Aggregate counts from any verification tables present in the docs
    counts = {}
    for doc in DOCS:
        if not doc.exists():
            continue
        text = doc.read_text(encoding="utf-8", errors="ignore")
        for m in TABLE_RE.finditer(text):
            counts[m.group("service")] = int(m.group("count"))
    return counts


def main():
    # Optional: allow excluding services from drift report
    exclude = set()
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a in ("-x", "--exclude"):
            # support multiple --exclude occurrences and comma-separated lists
            if i + 1 < len(args):
                for item in args[i + 1].split(","):
                    exclude.add(item.strip())

    scan_out = run_scan()
    scan_counts = parse_scan(scan_out)
    doc_counts = parse_docs_counts()

    drift = []
    for service, scan_val in scan_counts.items():
        if service in exclude:
            continue
        doc_val = doc_counts.get(service)
        if doc_val is None:
            drift.append((service, scan_val, None, 100.0))
            continue
        if doc_val == 0 and scan_val > 0:
            pct = 100.0
        else:
            pct = abs(scan_val - doc_val) / max(doc_val, 1) * 100.0
        if pct > 10.0:
            drift.append((service, scan_val, doc_val, pct))

    if drift:
        print("Doc drift detected (>10%):")
        print("Service, scan_count, doc_count, drift%")
        for s, sc, dc, p in drift:
            print(f"{s},{sc},{dc if dc is not None else 'N/A'},{p:.1f}")
        sys.exit(1)
    else:
        print("No doc drift >10% detected.")


if __name__ == "__main__":
    main()
