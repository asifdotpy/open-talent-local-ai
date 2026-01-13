from fastapi.testclient import TestClient
from app.main import app
from app.models import JobDetails

client = TestClient(app)


def test_get_job_details():
    """
    Tests the GET /jobs/{project_id} endpoint.
    """
    project_id = "test-project-123"
    response = client.get(f"/jobs/{project_id}")

    # Assert the status code is 200 OK
    assert response.status_code == 200

    # Assert the response body matches the JobDetails schema
    job_details = JobDetails(**response.json())
    assert job_details.title == "Senior Software Engineer"
    assert "Develop and maintain web applications" in job_details.description
    assert "Design and implement new features" in job_details.key_responsibilities
    assert "Python" in job_details.required_skills
    assert "FastAPI" in job_details.required_skills
