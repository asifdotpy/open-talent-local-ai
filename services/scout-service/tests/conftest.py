import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add the service root directory and project root to sys.path
# This helps with core.constants and schemas imports
service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
project_root = os.path.abspath(os.path.join(service_root, "..", ".."))

if service_root not in sys.path:
    sys.path.insert(0, service_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def client():
    # Set dummy env vars for lifespan
    os.environ["GITHUB_TOKEN"] = "test_token"
    os.environ["CONTACTOUT_API_TOKEN"] = "test_token"
    os.environ["AGENT_DISCOVERY_PATH"] = os.path.join(project_root, "agents")

    from main import app

    # Use TestClient as a context manager to trigger lifespan
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}
