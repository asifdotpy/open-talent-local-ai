from fastapi import FastAPI

from .models import JobDetails

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint to verify the service is running.

    Returns:
        JSON response with a heartbeat message.
    """
    return {"message": "Project Service is running!"}


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service status.

    Returns:
        JSON response indicating the service is healthy.
    """
    return {"status": "healthy"}


@app.get("/jobs/{project_id}", response_model=JobDetails)
async def get_job_details(project_id: str):
    """Retrieve detailed information for a specific job/project.

    Note: This is currently a placeholder returning mock data.

    Args:
        project_id: The unique identifier for the project.

    Returns:
        JobDetails object with title, description, and requirements.
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


if __name__ == "__main__":
    import os

    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8015))
    uvicorn.run(app, host=host, port=port)
