"""Database models for the interview process."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.base import Base

candidate_skill_association = Table(
    "candidate_skill_association",
    Base.metadata,
    Column("candidate_profile_id", Integer, ForeignKey("candidate_profile.id")),
    Column("skill_id", Integer, ForeignKey("skill.id")),
)


class Interview(Base):
    __tablename__ = "interview"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    search_criteria_id = Column(Integer, ForeignKey("search_criteria.id"))
    candidate_profile_id = Column(Integer, ForeignKey("candidate_profile.id"))

    search_criteria = relationship("SearchCriteria", back_populates="interview")
    candidate_profile = relationship("CandidateProfile", back_populates="interview")


class SearchCriteria(Base):
    __tablename__ = "search_criteria"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String)
    required_skills = Column(String)  # Storing as comma-separated string
    nice_to_have_skills = Column(String)  # Storing as comma-separated string
    company_culture = Column(String)  # Storing as comma-separated string
    experience_level = Column(String)

    interview = relationship("Interview", back_populates="search_criteria")


class CandidateProfile(Base):
    __tablename__ = "candidate_profile"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    source_url = Column(String)
    summary = Column(String)
    alignment_score = Column(Float)

    work_experience = relationship("WorkExperience", back_populates="candidate")
    education = relationship("Education", back_populates="candidate")
    skills = relationship("Skill", secondary=candidate_skill_association, back_populates="candidates")
    initial_questions = relationship("InitialQuestion", back_populates="candidate")
    interview = relationship("Interview", back_populates="candidate_profile")


class WorkExperience(Base):
    __tablename__ = "work_experience"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    duration = Column(String)
    responsibilities = Column(String)  # Storing as comma-separated string
    candidate_id = Column(Integer, ForeignKey("candidate_profile.id"))

    candidate = relationship("CandidateProfile", back_populates="work_experience")


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    institution = Column(String)
    degree = Column(String)
    year = Column(String)
    candidate_id = Column(Integer, ForeignKey("candidate_profile.id"))

    candidate = relationship("CandidateProfile", back_populates="education")


class Skill(Base):
    __tablename__ = "skill"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String)  # "matched" or "unmatched"

    candidates = relationship("CandidateProfile", secondary=candidate_skill_association, back_populates="skills")


class InitialQuestion(Base):
    __tablename__ = "initial_question"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    reasoning = Column(String)
    candidate_id = Column(Integer, ForeignKey("candidate_profile.id"))

    candidate = relationship("CandidateProfile", back_populates="initial_questions")
