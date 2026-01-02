"""CRUD operations for interview-related data.
"""

import uuid

from sqlalchemy.orm import Session

from app.db.models import interview as interview_models
from app.schemas import interview as interview_schemas


def _create_search_criteria(
    db: Session, search_criteria_payload: interview_schemas.SearchCriteria
) -> interview_models.SearchCriteria:
    """Creates a new SearchCriteria record in the database."""
    search_criteria = interview_models.SearchCriteria(
        job_title=search_criteria_payload.jobTitle,
        required_skills=",".join(search_criteria_payload.requiredSkills),
        nice_to_have_skills=",".join(search_criteria_payload.niceToHaveSkills),
        company_culture=",".join(search_criteria_payload.companyCulture),
        experience_level=search_criteria_payload.experienceLevel,
    )
    db.add(search_criteria)
    db.commit()
    db.refresh(search_criteria)
    return search_criteria


def _create_candidate_profile(
    db: Session, candidate_profile_payload: interview_schemas.CandidateProfile
) -> interview_models.CandidateProfile:
    """Creates a new CandidateProfile record in the database."""
    candidate_profile = interview_models.CandidateProfile(
        full_name=candidate_profile_payload.fullName,
        source_url=candidate_profile_payload.sourceUrl,
        summary=candidate_profile_payload.summary,
        alignment_score=candidate_profile_payload.alignmentScore,
    )
    db.add(candidate_profile)
    db.commit()
    db.refresh(candidate_profile)
    return candidate_profile


def _create_work_experiences(
    db: Session, candidate_id: int, work_experiences_payload: list[interview_schemas.WorkExperience]
):
    """Creates and associates WorkExperience records with a candidate profile."""
    for exp in work_experiences_payload:
        data = exp.model_dump()
        data["responsibilities"] = ",".join(exp.responsibilities)
        work_exp = interview_models.WorkExperience(**data, candidate_id=candidate_id)
        db.add(work_exp)
    db.commit()


def _create_education_records(
    db: Session, candidate_id: int, education_payload: list[interview_schemas.Education]
):
    """Creates and associates Education records with a candidate profile."""
    for edu in education_payload:
        education = interview_models.Education(**edu.model_dump(), candidate_id=candidate_id)
        db.add(education)
    db.commit()


def _associate_skills(
    db: Session,
    candidate_profile: interview_models.CandidateProfile,
    skills_payload: interview_schemas.Skills,
):
    """Creates and associates Skill records with a candidate profile."""
    for skill_name in skills_payload.matched:
        skill = (
            db.query(interview_models.Skill)
            .filter(interview_models.Skill.name == skill_name)
            .first()
        )
        if not skill:
            skill = interview_models.Skill(name=skill_name, type="matched")
            db.add(skill)
        candidate_profile.skills.append(skill)

    for skill_name in skills_payload.unmatched:
        skill = (
            db.query(interview_models.Skill)
            .filter(interview_models.Skill.name == skill_name)
            .first()
        )
        if not skill:
            skill = interview_models.Skill(name=skill_name, type="unmatched")
            db.add(skill)
        candidate_profile.skills.append(skill)
    db.commit()


def _create_initial_questions(
    db: Session,
    candidate_id: int,
    initial_questions_payload: list[interview_schemas.InitialQuestion],
):
    """Creates and associates InitialQuestion records with a candidate profile."""
    for q in initial_questions_payload:
        question = interview_models.InitialQuestion(**q.model_dump(), candidate_id=candidate_id)
        db.add(question)
    db.commit()


def _create_interview_record(
    db: Session, search_criteria_id: int, candidate_profile_id: int
) -> interview_models.Interview:
    """Creates the main Interview record."""
    interview = interview_models.Interview(
        session_id=str(uuid.uuid4()),
        search_criteria_id=search_criteria_id,
        candidate_profile_id=candidate_profile_id,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def create_interview(
    db: Session, payload: interview_schemas.HandoffPayload
) -> interview_models.Interview:
    """Creates a new interview record in the database by orchestrating calls to helper methods."""
    search_criteria = _create_search_criteria(db, payload.searchCriteria)
    candidate_profile = _create_candidate_profile(db, payload.candidateProfile)

    _create_work_experiences(db, candidate_profile.id, payload.candidateProfile.workExperience)
    _create_education_records(db, candidate_profile.id, payload.candidateProfile.education)
    _associate_skills(db, candidate_profile, payload.candidateProfile.skills)
    _create_initial_questions(db, candidate_profile.id, payload.candidateProfile.initialQuestions)

    # Refresh candidate_profile to ensure relationships are loaded after associated records are committed
    db.refresh(candidate_profile)

    interview = _create_interview_record(db, search_criteria.id, candidate_profile.id)

    return interview
