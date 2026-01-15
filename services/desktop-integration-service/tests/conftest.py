import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add the service root directory to sys.path
# Note: For desktop-integration-service, the app is in 'app' subfolder
service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if service_root not in sys.path:
    sys.path.insert(0, service_root)


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}
