"""
Pydantic models for the Interview process, based on the Agent-to-Interview Handoff Contract.
"""

from pydantic import BaseModel, Field
from typing import List

class SearchCriteria(BaseModel):
    jobTitle: str = Field(..., description="The target job title.")
    requiredSkills: List[str] = Field(..., description="A list of mandatory skills for the role.")
    niceToHaveSkills: List[str] = Field(..., description="A list of desired but not essential skills.")
    companyCulture: List[str] = Field(..., description="Keywords describing the company culture.")
    experienceLevel: str = Field(..., description="The target seniority for the role (e.g., 'Senior').")

class WorkExperience(BaseModel):
    title: str
    company: str
    duration: str
    responsibilities: List[str]

class Education(BaseModel):
    institution: str
    degree: str
    year: str

class Skills(BaseModel):
    matched: List[str]
    unmatched: List[str]

class InitialQuestion(BaseModel):
    question: str = Field(..., description="Targeted question based on profile.")
    reasoning: str = Field(..., description="Why this question is being asked.")

class CandidateProfile(BaseModel):
    fullName: str = Field(..., description="The candidate's full name.")
    sourceUrl: str = Field(..., description="The primary URL where the candidate's profile was found.")
    summary: str = Field(..., description="AI-generated summary of the candidate's profile.")
    workExperience: List[WorkExperience]
    education: List[Education]
    skills: Skills
    alignmentScore: float = Field(..., description="Score indicating alignment with the search criteria.")
    initialQuestions: List[InitialQuestion]

class HandoffPayload(BaseModel):
    searchCriteria: SearchCriteria
    candidateProfile: CandidateProfile
