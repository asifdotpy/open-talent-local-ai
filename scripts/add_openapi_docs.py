#!/usr/bin/env python3
"""
Script to add OpenAPI documentation endpoints to all services and agents.
Adds /docs, /doc, /api-docs, /openapi.json endpoints with proper configuration.
"""

import re
from pathlib import Path

OPENAPI_ENDPOINTS = '''

@app.get("/doc", include_in_schema=False)
async def doc_redirect():
    """Alternative redirect to API documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


@app.get("/api-docs", include_in_schema=False)
async def api_docs_info():
    """Get API documentation information and available endpoints."""
    routes_info = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            route_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unknown'),
                "summary": getattr(route, 'summary', None) or getattr(route, 'description', None)
            }
            routes_info.append(route_info)

    return {
        "service": "{service_name}",
        "version": "{version}",
        "total_endpoints": len(routes_info),
        "documentation_urls": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "routes": routes_info
    }
'''


def update_fastapi_config(content: str, service_name: str) -> str:
    """Update FastAPI() initialization to include OpenAPI URLs"""

    # Pattern to match FastAPI initialization
    pattern = r'(app\s*=\s*FastAPI\s*\(\s*title\s*=\s*["\']([^"\']+)["\'])'

    def replacer(match):
        title = match.group(2)
        # Build enhanced FastAPI config
        return f'''app = FastAPI(
    title="{title}",
    description="""
    {service_name} - OpenTalent Platform

    **API Documentation:**
    - Interactive Swagger UI: `/docs`
    - Alternative docs URL: `/doc`
    - ReDoc documentation: `/redoc`
    - OpenAPI schema: `/openapi.json`
    - API endpoints summary: `/api-docs`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"'''

    return re.sub(pattern, replacer, content, count=1)


def update_root_endpoint(content: str) -> str:
    """Add documentation links to root endpoint"""

    # Find root endpoint and add documentation section
    pattern = r'(@app\.get\(["\']\/["\']\)[^}]+return\s*\{[^}]+)(\})'

    def replacer(match):
        before_close = match.group(1)
        # Check if documentation already exists
        if "documentation" in before_close:
            return match.group(0)

        # Add documentation section before closing brace
        return (
            before_close
            + """,
        "documentation": {
            "swagger_ui": "/docs",
            "alternative": "/doc",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
            "api_summary": "/api-docs"
        }"""
            + match.group(2)
        )

    return re.sub(pattern, replacer, content, flags=re.DOTALL)


def add_openapi_endpoints(content: str, service_name: str, version: str) -> str:
    """Add OpenAPI documentation endpoints if not present"""

    # Check if endpoints already exist
    if "/api-docs" in content and "api_docs_info" in content:
        return content

    # Find the first @app.get after root to insert endpoints
    # Look for health endpoint or first endpoint after root
    pattern = r'(@app\.get\(["\']\/["\']\)[^\n]+\n[^@]+)(@app\.get\(["\']\/health["\']\))'

    endpoints = OPENAPI_ENDPOINTS.format(service_name=service_name, version=version)

    def replacer(match):
        return match.group(1) + endpoints + "\n\n" + match.group(2)

    result = re.sub(pattern, replacer, content, count=1, flags=re.DOTALL)

    # If health endpoint not found, try to find any second endpoint
    if result == content:
        pattern = r'(@app\.get\(["\']\/["\']\)[^\n]+\n(?:.*?\n)*?.*?async def[^\n]+\n(?:.*?\n)*?.*?return[^\n]+\n[^\n]+\n)(@app\.(get|post|put|delete|patch)\()'
        result = re.sub(pattern, replacer, content, count=1, flags=re.DOTALL)

    return result


def process_file(file_path: Path, service_name: str):
    """Process a single file to add OpenAPI documentation"""
    print(f"Processing {file_path}...")

    try:
        content = file_path.read_text()

        # Skip if already has api-docs endpoint
        if "api_docs_info" in content and "/api-docs" in content:
            print("  ✓ Already has OpenAPI endpoints, skipping")
            return True

        # Extract version if possible
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        version = version_match.group(1) if version_match else "1.0.0"

        # Apply transformations
        original_content = content
        content = update_fastapi_config(content, service_name)
        content = update_root_endpoint(content)
        content = add_openapi_endpoints(content, service_name, version)

        # Only write if changes were made
        if content != original_content:
            file_path.write_text(content)
            print("  ✓ Updated with OpenAPI documentation")
            return True
        else:
            print("  ℹ No changes needed")
            return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Main execution"""
    base_path = Path(__file__).parent.parent

    # Define services to update
    services = [
        # Agents
        ("agents/proactive-scanning-agent/main.py", "Proactive Scanning Agent"),
        ("agents/boolean-mastery-agent/main.py", "Boolean Mastery Agent"),
        ("agents/personalized-engagement-agent/main.py", "Personalized Engagement Agent"),
        ("agents/market-intelligence-agent/main.py", "Market Intelligence Agent"),
        ("agents/tool-leverage-agent/main.py", "Tool Leverage Agent"),
        ("agents/quality-focused-agent/main.py", "Quality-Focused Agent"),
        ("agents/interviewer-agent/main.py", "Interviewer Agent"),
        # Microservices
        ("microservices/interview-service/main.py", "Interview Service"),
        ("microservices/sourcer-service/main.py", "Sourcer Service"),
        ("microservices/analytics-service/main.py", "Analytics Service"),
        ("microservices/notification-service/main.py", "Notification Service"),
        ("microservices/candidate-service/main.py", "Candidate Service"),
        ("microservices/user-service/main.py", "User Service"),
        ("microservices/security-service/main.py", "Security Service"),
        ("microservices/ai-auditing-service/main.py", "AI Auditing Service"),
        ("microservices/explainability-service/main.py", "Explainability Service"),
    ]

    print("Adding OpenAPI documentation endpoints to services...\n")

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for relative_path, service_name in services:
        file_path = base_path / relative_path

        if not file_path.exists():
            print(f"⚠ {file_path} not found, skipping")
            skipped_count += 1
            continue

        result = process_file(file_path, service_name)
        if result:
            updated_count += 1
        elif result is False:
            error_count += 1
        else:
            skipped_count += 1

    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors: {error_count}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
