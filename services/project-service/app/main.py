import json

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import database, models

# Initialize database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()


# Seeding logic: ensure some real data exists on startup
def seed_data():
    db = database.SessionLocal()
    try:
        # Check if we already have jobs
        if db.query(models.Project).count() == 0:
            initial_jobs = [
                {
                    "id": "project-001",
                    "title": "Senior AI Architect",
                    "description": "Lead the design and implementation of large-scale agentic AI systems.",
                    "key_responsibilities": [
                        "Architect multi-agent orchestration layers",
                        "Evaluate and select foundation models",
                        "Lead a team of 5 AI engineers",
                    ],
                    "required_skills": ["Python", "PyTorch", "Kubernetes", "LLMs"],
                },
                {
                    "id": "project-002",
                    "title": "Frontend Lead (React/Vite)",
                    "description": "Build high-performance, developer-focused recruiter dashboards.",
                    "key_responsibilities": [
                        "Maintain the OpenTalent core UI kit",
                        "Optimize dashboard rendering performance",
                        "Drive accessibility compliance (WCAG)",
                    ],
                    "required_skills": ["React", "TypeScript", "Vite", "TailwindCSS"],
                },
            ]
            for job_data in initial_jobs:
                job = models.Project(
                    id=job_data["id"],
                    title=job_data["title"],
                    description=job_data["description"],
                    key_responsibilities_json=json.dumps(job_data["key_responsibilities"]),
                    required_skills_json=json.dumps(job_data["required_skills"]),
                )
                db.add(job)
            db.commit()
    finally:
        db.close()


# Run seed on startup
seed_data()


@app.get("/")
async def root():
    return {"message": "Project Service (Production Mode) is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}


@app.get("/jobs", response_model=list[models.JobDetails])
async def list_jobs(db: Session = Depends(database.get_db)):
    projects = db.query(models.Project).all()
    # Manual conversion for Pydantic (using the properties defined in models.py)
    return [
        models.JobDetails(
            id=p.id,
            title=p.title,
            description=p.description,
            key_responsibilities=p.key_responsibilities,
            required_skills=p.required_skills,
        )
        for p in projects
    ]


@app.get("/jobs/{project_id}", response_model=models.JobDetails)
async def get_job_details(project_id: str, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return models.JobDetails(
        id=project.id,
        title=project.title,
        description=project.description,
        key_responsibilities=project.key_responsibilities,
        required_skills=project.required_skills,
    )


@app.post("/jobs", response_model=models.JobDetails)
async def create_job(job_in: models.JobDetails, db: Session = Depends(database.get_db)):
    # Check if ID exists
    if db.query(models.Project).filter(models.Project.id == job_in.id).first():
        raise HTTPException(status_code=400, detail="Project ID already exists")

    db_job = models.Project(
        id=job_in.id,
        title=job_in.title,
        description=job_in.description,
        key_responsibilities_json=json.dumps(job_in.key_responsibilities),
        required_skills_json=json.dumps(job_in.required_skills),
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return models.JobDetails(
        id=db_job.id,
        title=db_job.title,
        description=db_job.description,
        key_responsibilities=db_job.key_responsibilities,
        required_skills=db_job.required_skills,
    )


if __name__ == "__main__":
    import os

    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8015))
    uvicorn.run(app, host=host, port=port)
