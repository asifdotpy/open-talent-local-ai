import os
import re
from pathlib import Path


def extract_endpoints_from_file(file_path):
    """Extract FastAPI endpoints from a main.py file using regex."""
    endpoints = []
    # Match patterns like @app.get("/path"), @router.post("/path"), etc.
    pattern = r'@(?:app|router)\.(get|post|put|delete|patch|options|head)\(\s*["\']([^"\']+)["\']'

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            matches = re.finditer(pattern, content)
            for match in matches:
                method, path = match.groups()
                endpoints.append({"method": method.upper(), "path": path, "file": str(file_path)})
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return endpoints


def find_test_calls(test_dir, endpoints):
    """Search for test calls matching discovered endpoints."""
    results = {
        f"{e['method']} {e['path']}": {"tested": False, "files": [], "endpoint": e}
        for e in endpoints
    }

    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                        for key, info in results.items():
                            method = info["endpoint"]["method"].lower()
                            path = info["endpoint"]["path"]

                            # Clean path for regex (handle variables like {id})
                            regex_path = re.escape(path).replace(r"\{", r"\{").replace(r"\}", r"\}")
                            # Match patterns like client.get("/path"), httpx.post(f"url/path"), etc.
                            # We are looking for the path string appearing in strings
                            if path in content:
                                info["tested"] = True
                                info["files"].append(str(file_path))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return results


def main():
    repo_root = Path("/home/asif1/open-talent")
    services_dir = repo_root / "services"

    all_coverage = {}

    for service_path in services_dir.iterdir():
        if not service_path.is_dir() or service_path.name.startswith("__"):
            continue

        main_py = service_path / "main.py"
        if not main_py.exists():
            # Check for app/main.py (some services use this structure)
            main_py = service_path / "app" / "main.py"

        if not main_py.exists():
            continue

        print(f"Analyzing {service_path.name}...")
        endpoints = extract_endpoints_from_file(main_py)

        test_dir = service_path / "tests"
        if not test_dir.exists():
            test_dir = service_path / "app" / "tests"

        if test_dir.exists():
            coverage = find_test_calls(test_dir, endpoints)
        else:
            coverage = {
                f"{e['method']} {e['path']}": {"tested": False, "files": [], "endpoint": e}
                for e in endpoints
            }

        all_coverage[service_path.name] = {
            "total": len(endpoints),
            "tested": sum(1 for c in coverage.values() if c["tested"]),
            "details": coverage,
        }

    # Generate Report
    report_path = repo_root / "COVERAGE_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# OpenTalent Test Coverage Analysis Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        total_endpoints = 0
        total_tested = 0

        for service, data in all_coverage.items():
            total_endpoints += data["total"]
            total_tested += data["tested"]

        f.write("## Global Statistics\n")
        f.write(f"- **Total Endpoints:** {total_endpoints}\n")
        f.write(f"- **Tested Endpoints:** {total_tested}\n")
        percentage = (total_tested / total_endpoints * 100) if total_endpoints > 0 else 0
        f.write(f"- **Overall Coverage:** {percentage:.2f}%\n\n")

        f.write("## Service Breakdown\n\n")
        f.write("| Service | Total | Tested | Coverage |\n")
        f.write("| --- | --- | --- | --- |\n")

        for service, data in sorted(all_coverage.items()):
            cov = (data["tested"] / data["total"] * 100) if data["total"] > 0 else 0
            f.write(f"| {service} | {data['total']} | {data['tested']} | {cov:.2f}% |\n")

        f.write("\n## Untested Endpoints\n\n")
        for service, data in sorted(all_coverage.items()):
            untested = [k for k, v in data["details"].items() if not v["tested"]]
            if untested:
                f.write(f"### {service}\n")
                for u in untested:
                    f.write(f"- [ ] {u}\n")
                f.write("\n")

    print(f"Coverage report generated at {report_path}")


if __name__ == "__main__":
    from datetime import datetime

    main()
