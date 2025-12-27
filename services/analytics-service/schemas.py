"""Analytics Service - Pydantic V2 Schemas
Generated: December 17, 2025
Coverage: ~14 request/response models for sentiment, quality, bias, expertise, performance, metrics, and reports.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class SentimentAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1)


class SentimentAnalysis(BaseModel):
    polarity: float
    subjectivity: float
    confidence: float
    emotion: str
    intensity: float
    keywords: list[str] = []


class ResponseQualityRequest(BaseModel):
    response_text: str = Field(..., min_length=1)
    question_context: str = Field(..., min_length=1)


class ResponseQuality(BaseModel):
    overall_score: float
    completeness: float
    relevance: float
    clarity: float
    technical_accuracy: float
    strengths: list[str] = []
    improvements: list[str] = []


class BiasDetectionRequest(BaseModel):
    text: str = Field(..., min_length=1)
    participants: list[dict[str, Any]] | None = None


class BiasDetection(BaseModel):
    bias_score: float
    flags: list[str]
    severity: SeverityLevel = SeverityLevel.low
    categories: list[str]
    recommendations: list[str]


class ExpertiseAssessmentRequest(BaseModel):
    response_text: str
    question_context: str


class ExpertiseAssessment(BaseModel):
    level: str = "intermediate"
    confidence: float = Field(..., ge=0.0, le=1.0)
    technical_skills: list[str] = []
    knowledge_gaps: list[str] = []
    experience_years: int | None = None


class InterviewPerformanceRequest(BaseModel):
    room_id: str
    response_analyses: list[dict[str, Any]] = []


class InterviewPerformance(BaseModel):
    overall_score: float
    sentiment_trend: str
    expertise_level: str
    bias_incidents: int
    quality_trend: str
    recommendations: list[str] = []


class IntelligenceReportRequest(BaseModel):
    room_id: str
    analyses: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    room_created_at: str


class IntelligenceReport(BaseModel):
    summary: dict[str, Any]
    sentiment_analysis: dict[str, Any]
    bias_report: dict[str, Any]
    expertise_evaluation: dict[str, Any]
    quality_metrics: dict[str, Any]
    recommendations: list[str] = []
    interview_effectiveness: float


class MetricPoint(BaseModel):
    timestamp: datetime
    value: float


class MetricsResponse(BaseModel):
    interviews_analyzed: int
    avg_sentiment: float
    avg_quality_score: float
    bias_incidents: int
    trend: str


class MetricsTimeSeriesResponse(BaseModel):
    metric: str
    points: list[MetricPoint]


class ReportCreateRequest(BaseModel):
    type: str = Field(..., pattern=r"^(interview_summary|candidate_summary|daily|weekly|monthly)$")
    date_range: str = Field(..., pattern=r"^(day|week|month|quarter|year)$")
    filters: dict[str, Any] | None = None


class ReportResponse(BaseModel):
    report_id: str
    status: str
    created_at: datetime
    url: str | None = None


class ReportExportResponse(BaseModel):
    report_id: str
    format: str
    url: str | None = None
    expires_at: datetime | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
