"""Pydantic models for the Interview process, based on the Agent-to-Interview Handoff Contract."""


from pydantic import BaseModel, Field


class SearchCriteria(BaseModel):
    jobTitle: str = Field(..., description="The target job title.")
    requiredSkills: list[str] = Field(..., description="A list of mandatory skills for the role.")
    niceToHaveSkills: list[str] = Field(..., description="A list of desired but not essential skills.")
    companyCulture: list[str] = Field(..., description="Keywords describing the company culture.")
    experienceLevel: str = Field(..., description="The target seniority for the role (e.g., 'Senior').")

class WorkExperience(BaseModel):
    title: str
    company: str
    duration: str
    responsibilities: list[str]

class Education(BaseModel):
    institution: str
    degree: str
    year: str

class Skills(BaseModel):
    matched: list[str]
    unmatched: list[str]

class InitialQuestion(BaseModel):
    question: str = Field(..., description="Targeted question based on profile.")
    reasoning: str = Field(..., description="Why this question is being asked.")

class CandidateProfile(BaseModel):
    fullName: str = Field(..., description="The candidate's full name.")
    sourceUrl: str = Field(..., description="The primary URL where the candidate's profile was found.")
    summary: str = Field(..., description="AI-generated summary of the candidate's profile.")
    workExperience: list[WorkExperience]
    education: list[Education]
    skills: Skills
    alignmentScore: float = Field(..., description="Score indicating alignment with the search criteria.")
    initialQuestions: list[InitialQuestion]

class HandoffPayload(BaseModel):
    searchCriteria: SearchCriteria
    candidateProfile: CandidateProfile
