#!/usr/bin/env python3
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICES_DIR = ROOT / "services"

DECORATOR_RE = re.compile(r"@(?:(?:app|router)\.(get|post|put|delete|patch|options)|app\.websocket)")
ROUTE_CALL_RE = re.compile(r"\b(?:app|router)\.(?:get|post|put|delete|patch|options|add_api_route)\(\s*['\"]/")
APP_INCLUDE_ROUTER_RE = re.compile(r"\bapp\.include_router\(\s*([a-zA-Z_][a-zA-Z0-9_\.]*)")
PORT_RE = re.compile(r"uvicorn\.run\(app, host=.*port=([0-9]+)\)")

def count_decorators(text: str) -> int:
    # Count direct decorators on app/router and websocket
    return len(DECORATOR_RE.findall(text))

def count_route_calls(text: str) -> int:
    # Count explicit app/router get/post/... and add_api_route calls
    return len(ROUTE_CALL_RE.findall(text))

def scan_service(service_path: Path):
    endpoint_count = 0
    ports = set()
    router_files = set()

    # First pass: find main.py files, count endpoints, detect include_router imports
    for p in service_path.rglob("main.py"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        endpoint_count += count_decorators(text)
        endpoint_count += count_route_calls(text)
        for m in PORT_RE.finditer(text):
            ports.add(m.group(1))

        # Collect potential router modules referenced in include_router
        for m in APP_INCLUDE_ROUTER_RE.finditer(text):
            module_ref = m.group(1)
            # Attempt to resolve local router files heuristically
            # Common patterns: `router`, `routes`, `api`, `routers.something`
            candidates = []
            parts = module_ref.split('.')
            # Build relative paths under service_path for each part chain
            for i in range(len(parts)):
                rel = parts[:i+1]
                candidates.append(service_path / '/'.join(rel))
            # Also try common filenames
            candidates += [
                service_path / "router.py",
                service_path / "routes.py",
                service_path / "api.py",
                service_path / "routers",
                service_path / "app/routers",
                service_path / "app/routes",
                service_path / "routers/api",
                service_path / "api/routers",
            ]
            for c in candidates:
                if c.is_dir():
                    for py in c.rglob("*.py"):
                        router_files.add(py)
                elif c.is_file() and c.suffix == ".py":
                    router_files.add(c)

    # Second pass: scan router files for router.* calls and decorators
    for rf in router_files:
        try:
            text = rf.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        endpoint_count += count_decorators(text)
        endpoint_count += count_route_calls(text)

    # Fallback: scan all *.py under service for router.* calls if include_router not found
    if endpoint_count == 0:
        for py in service_path.rglob("*.py"):
            text = py.read_text(encoding="utf-8", errors="ignore")
            endpoint_count += count_decorators(text)
            endpoint_count += count_route_calls(text)

    return endpoint_count, sorted(ports)

def main():
    results = []
    for service in sorted(d.name for d in SERVICES_DIR.iterdir() if d.is_dir() and d.name.endswith("-service")):
        count, ports = scan_service(SERVICES_DIR / service)
        results.append((service, count, ",".join(ports) or ""))
    # Print markdown table
    print("| Service | Endpoints | Ports |")
    print("|---------|-----------|-------|")
    for s, c, pt in results:
        print(f"| {s} | {c} | {pt} |")

if __name__ == "__main__":
    main()
