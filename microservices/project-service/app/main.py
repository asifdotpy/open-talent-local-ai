from fastapi import FastAPI

from .models import JobDetails

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Project Service is running!"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/jobs/{project_id}", response_model=JobDetails)
async def get_job_details(project_id: str):
    """Returns the details for a specific job (project).
    NOTE: This currently returns mocked data.
    """
    return {
        "title": "Senior Software Engineer",
        "description": "Develop and maintain web applications.",
        "key_responsibilities": [
            "Design and implement new features",
            "Write clean, maintainable code",
            "Collaborate with the team",
        ],
        "required_skills": ["Python", "FastAPI", "SQL", "Docker"],
    }
