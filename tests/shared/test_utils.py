# tests/shared/test_utils.py
import time
from typing import Dict, Any, Optional
import pytest


class TestHelper:
    """Simple test helper for the platform"""

    def __init__(self):
        self.test_data: Dict[str, Any] = {}

    def set_test_data(self, key: str, value: Any) -> None:
        """Store test data"""
        self.test_data[key] = value

    def get_test_data(self, key: str) -> Any:
        """Retrieve test data"""
        return self.test_data.get(key)

    def measure_time(self, func) -> tuple:
        """Measure execution time of a function"""
        start = time.time()
        result = func()
        duration = time.time() - start
        return result, duration


def assert_response_status(response, expected_status: int) -> None:
    """Assert HTTP response status"""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"


def create_mock_service_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a mock service response"""
    return {
        "status": "success",
        "data": data,
        "timestamp": time.time()
    }


# Test fixtures
@pytest.fixture
def sample_user():
    return {
        "id": "user-123",
        "email": "test@example.com",
        "role": "recruiter",
        "permissions": ["read", "write"]
    }

@pytest.fixture
def mock_candidate_profile():
    return {
        "id": "candidate-456",
        "name": "John Doe",
        "skills": ["Python", "React", "AWS"],
        "experience_years": 5
    }

@pytest.fixture
def mock_job_requirement():
    return {
        "id": "job-789",
        "title": "Senior Software Engineer",
        "required_skills": ["Python", "React", "AWS"],
        "experience_level": "Senior"
    }


# Actual test functions
def test_test_helper_initialization():
    """Test that TestHelper initializes correctly"""
    helper = TestHelper()
    assert isinstance(helper.test_data, dict)
    assert len(helper.test_data) == 0


def test_test_helper_set_get_data():
    """Test setting and getting test data"""
    helper = TestHelper()
    helper.set_test_data("key1", "value1")
    assert helper.get_test_data("key1") == "value1"
    assert helper.get_test_data("nonexistent") is None


def test_measure_time():
    """Test time measurement functionality"""
    helper = TestHelper()

    def sample_function():
        time.sleep(0.01)  # Small delay
        return "result"

    result, duration = helper.measure_time(sample_function)
    assert result == "result"
    assert duration >= 0.01  # Should take at least the sleep time


def test_create_mock_service_response():
    """Test mock service response creation"""
    data = {"test": "data"}
    response = create_mock_service_response(data)

    assert response["status"] == "success"
    assert response["data"] == data
    assert "timestamp" in response
    assert isinstance(response["timestamp"], float)


def test_sample_user_fixture(sample_user):
    """Test the sample user fixture"""
    assert sample_user["id"] == "user-123"
    assert sample_user["email"] == "test@example.com"
    assert "recruiter" in sample_user["role"]
    assert "read" in sample_user["permissions"]


def test_mock_candidate_profile_fixture(mock_candidate_profile):
    """Test the mock candidate profile fixture"""
    assert mock_candidate_profile["name"] == "John Doe"
    assert "Python" in mock_candidate_profile["skills"]
    assert mock_candidate_profile["experience_years"] == 5


def test_mock_job_requirement_fixture(mock_job_requirement):
    """Test the mock job requirement fixture"""
    assert mock_job_requirement["title"] == "Senior Software Engineer"
    assert "Python" in mock_job_requirement["required_skills"]
    assert mock_job_requirement["experience_level"] == "Senior"
