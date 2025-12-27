#!/usr/bin/env python3
"""
Simple GEMINI.md Generator for OpenTalent Services

Generates basic documentation files for services.
"""

import sys
from pathlib import Path


def generate_gemini_doc(service_name):
    """Generate a basic GEMINI.md file for a service"""
    content = f"""# {service_name.upper()}

## Overview
{service_name} is a service in the OpenTalent platform.

## Architecture
- Language: Python
- Framework: FastAPI
- Database: PostgreSQL/Redis

## API Endpoints
- GET /health - Health check
- POST /api/v1/process - Main processing endpoint

## Configuration
Environment variables:
- SERVICE_PORT - Port to run on (default: 8000)
- DATABASE_URL - Database connection string
- REDIS_URL - Redis connection string

## Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python main.py
```

## Deployment
Deployed via Docker containers in the platform infrastructure.
"""

    return content


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python generate_gemini_md.py <service_name>")
        sys.exit(1)

    service_name = sys.argv[1]

    try:
        print(f"Generating GEMINI.md for {service_name}...")

        # Generate content
        content = generate_gemini_doc(service_name)

        # Write file
        output_path = Path(f"{service_name}/GEMINI.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(content)

        print(f"Generated {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
