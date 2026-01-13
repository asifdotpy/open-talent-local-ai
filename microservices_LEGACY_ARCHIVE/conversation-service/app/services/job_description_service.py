"""
Job Description service for dynamic loading from project/candidate data.
Integrates with project-service and candidate-service.
"""

import logging
import os
from typing import Dict, Any, Optional
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs from environment
PROJECT_SERVICE_URL = os.getenv("PROJECT_SERVICE_URL", "http://localhost:8005")
CANDIDATE_SERVICE_URL = os.getenv("CANDIDATE_SERVICE_URL", "http://localhost:8006")
USE_MOCK_JOB_DESC = os.getenv("USE_MOCK_JOB_DESC", "true").lower() == "true"


class JobDescriptionService:
    """Service for fetching job descriptions from project service."""

    def __init__(self):
        self.project_service_url = PROJECT_SERVICE_URL
        self.candidate_service_url = CANDIDATE_SERVICE_URL
        self.use_mock = USE_MOCK_JOB_DESC
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_job_description(
        self, project_id: Optional[str] = None, job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch job description from project service.

        Args:
            project_id: Project ID to fetch job for
            job_id: Direct job ID

        Returns:
            Job description dictionary with title, description, skills, responsibilities
        """
        if self.use_mock:
            return self._get_mock_job_description(project_id or job_id)

        try:
            # Try to fetch from project service
            endpoint = f"{self.project_service_url}/api/v1/projects/{project_id or job_id}"
            response = await self.client.get(endpoint)

            if response.status_code == 200:
                job_data = response.json()
                return self._format_job_description(job_data)
            else:
                logger.warning(f"Project service returned {response.status_code}, using mock")
                return self._get_mock_job_description(project_id or job_id)

        except Exception as e:
            logger.error(f"Error fetching job description: {e}")
            return self._get_mock_job_description(project_id or job_id)

    async def get_candidate_profile(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch candidate profile from candidate service.

        Args:
            candidate_id: Candidate ID to fetch

        Returns:
            Candidate profile dictionary
        """
        if self.use_mock:
            return self._get_mock_candidate_profile(candidate_id)

        try:
            endpoint = f"{self.candidate_service_url}/api/v1/candidates/{candidate_id}"
            response = await self.client.get(endpoint)

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Candidate service returned {response.status_code}, using mock")
                return self._get_mock_candidate_profile(candidate_id)

        except Exception as e:
            logger.error(f"Error fetching candidate profile: {e}")
            return self._get_mock_candidate_profile(candidate_id)

    def _format_job_description(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format job data from project service into standard structure."""
        return {
            "job_id": job_data.get("id"),
            "title": job_data.get("title", "Software Engineer"),
            "description": job_data.get("description", ""),
            "required_skills": job_data.get("required_skills", []),
            "key_responsibilities": job_data.get("key_responsibilities", []),
            "experience_level": job_data.get("experience_level", "mid"),
            "department": job_data.get("department", "Engineering"),
            "location": job_data.get("location", "Remote"),
            "employment_type": job_data.get("employment_type", "Full-time"),
        }

    def _get_mock_job_description(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate mock job description for development/testing."""

        mock_jobs = {
            "python-backend": {
                "job_id": "python-backend",
                "title": "Senior Python Backend Engineer",
                "description": "We're seeking an experienced Python backend engineer to join our team. You'll work on building scalable microservices using Django and FastAPI.",
                "required_skills": [
                    "Python",
                    "Django",
                    "FastAPI",
                    "PostgreSQL",
                    "Redis",
                    "Docker",
                    "AWS",
                ],
                "key_responsibilities": [
                    "Design and implement RESTful APIs",
                    "Optimize database queries and improve performance",
                    "Write comprehensive unit and integration tests",
                    "Collaborate with frontend team on API contracts",
                    "Mentor junior developers",
                ],
                "experience_level": "senior",
                "department": "Engineering",
                "location": "Remote",
                "employment_type": "Full-time",
            },
            "frontend-react": {
                "job_id": "frontend-react",
                "title": "Frontend Engineer (React)",
                "description": "Join our frontend team to build responsive, performant user interfaces using React and modern JavaScript.",
                "required_skills": ["React", "JavaScript", "TypeScript", "CSS", "Webpack", "Git"],
                "key_responsibilities": [
                    "Build reusable React components",
                    "Implement responsive designs",
                    "Optimize application performance",
                    "Write unit tests with Jest and React Testing Library",
                    "Collaborate with designers and backend engineers",
                ],
                "experience_level": "mid",
                "department": "Engineering",
                "location": "Hybrid",
                "employment_type": "Full-time",
            },
            "devops": {
                "job_id": "devops",
                "title": "DevOps Engineer",
                "description": "We need a DevOps engineer to manage our cloud infrastructure and CI/CD pipelines.",
                "required_skills": [
                    "Kubernetes",
                    "Docker",
                    "AWS",
                    "Terraform",
                    "Jenkins",
                    "Python",
                    "Bash",
                ],
                "key_responsibilities": [
                    "Manage Kubernetes clusters",
                    "Build and maintain CI/CD pipelines",
                    "Monitor system performance and reliability",
                    "Automate infrastructure provisioning",
                    "Implement security best practices",
                ],
                "experience_level": "senior",
                "department": "Infrastructure",
                "location": "Remote",
                "employment_type": "Full-time",
            },
        }

        # Return specific job or default to Python backend
        if job_id and job_id in mock_jobs:
            return mock_jobs[job_id]

        return mock_jobs["python-backend"]

    def _get_mock_candidate_profile(self, candidate_id: str) -> Dict[str, Any]:
        """Generate mock candidate profile for development/testing."""
        return {
            "candidate_id": candidate_id,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "years_of_experience": 5,
            "skills": ["Python", "Django", "React", "PostgreSQL", "Docker"],
            "previous_roles": [
                "Senior Software Engineer at Tech Corp",
                "Software Engineer at StartupXYZ",
            ],
            "education": "BS Computer Science",
            "location": "San Francisco, CA",
            "availability": "2 weeks notice",
        }

    def build_job_description_text(self, job_data: Dict[str, Any]) -> str:
        """
        Build a comprehensive job description text for LLM context.

        Args:
            job_data: Job description dictionary

        Returns:
            Formatted text description
        """
        text = f"""Position: {job_data.get('title', 'Software Engineer')}
Department: {job_data.get('department', 'Engineering')}
Location: {job_data.get('location', 'Remote')}
Employment Type: {job_data.get('employment_type', 'Full-time')}
Experience Level: {job_data.get('experience_level', 'mid')}

Description:
{job_data.get('description', 'No description available')}

Required Skills:
{', '.join(job_data.get('required_skills', []))}

Key Responsibilities:
"""

        for i, responsibility in enumerate(job_data.get("key_responsibilities", []), 1):
            text += f"{i}. {responsibility}\n"

        return text.strip()

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Global job description service instance
job_description_service = JobDescriptionService()
