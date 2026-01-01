from fastapi.testclient import TestClient

from app.main import app
from app.models import JobDetails

client = TestClient(app)


def test_get_job_details():
    """Tests the GET /jobs/{project_id} endpoint."""
    project_id = "project-001"
    response = client.get(f"/jobs/{project_id}")

    # Assert the status code is 200 OK
    assert response.status_code == 200

    # Assert the response body matches the JobDetails schema
    job_details = JobDetails(**response.json())
    assert job_details.title == "Senior AI Architect"
    assert (
        "Lead the design and implementation of large-scale agentic AI systems"
        in job_details.description
    )
    assert "Architect multi-agent orchestration layers" in job_details.key_responsibilities
    assert "Python" in job_details.required_skills
    assert "PyTorch" in job_details.required_skills
