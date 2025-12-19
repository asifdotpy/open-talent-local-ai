"""
Analytics Service - Pydantic V2 Schemas
Generated: December 17, 2025
Coverage: ~14 request/response models for sentiment, quality, bias, expertise, performance, metrics, and reports.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


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
    keywords: List[str] = []


class ResponseQualityRequest(BaseModel):
    response_text: str = Field(..., min_length=1)
    question_context: str = Field(..., min_length=1)


class ResponseQuality(BaseModel):
    overall_score: float
    completeness: float
    relevance: float
    clarity: float
    technical_accuracy: float
    strengths: List[str] = []
    improvements: List[str] = []


class BiasDetectionRequest(BaseModel):
    text: str = Field(..., min_length=1)
    participants: Optional[List[Dict[str, Any]]] = None


class BiasDetection(BaseModel):
    bias_score: float
    flags: List[str]
    severity: SeverityLevel = SeverityLevel.low
    categories: List[str]
    recommendations: List[str]


class ExpertiseAssessmentRequest(BaseModel):
    response_text: str
    question_context: str


class ExpertiseAssessment(BaseModel):
    level: str = "intermediate"
    confidence: float = Field(..., ge=0.0, le=1.0)
    technical_skills: List[str] = []
    knowledge_gaps: List[str] = []
    experience_years: Optional[int] = None


class InterviewPerformanceRequest(BaseModel):
    room_id: str
    response_analyses: List[Dict[str, Any]] = []


class InterviewPerformance(BaseModel):
    overall_score: float
    sentiment_trend: str
    expertise_level: str
    bias_incidents: int
    quality_trend: str
    recommendations: List[str] = []


class IntelligenceReportRequest(BaseModel):
    room_id: str
    analyses: List[Dict[str, Any]] = []
    responses: List[Dict[str, Any]] = []
    room_created_at: str


class IntelligenceReport(BaseModel):
    summary: Dict[str, Any]
    sentiment_analysis: Dict[str, Any]
    bias_report: Dict[str, Any]
    expertise_evaluation: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    recommendations: List[str] = []
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
    points: List[MetricPoint]


class ReportCreateRequest(BaseModel):
    type: str = Field(..., pattern=r"^(interview_summary|candidate_summary|daily|weekly|monthly)$")
    date_range: str = Field(..., pattern=r"^(day|week|month|quarter|year)$")
    filters: Optional[Dict[str, Any]] = None


class ReportResponse(BaseModel):
    report_id: str
    status: str
    created_at: datetime
    url: Optional[str] = None


class ReportExportResponse(BaseModel):
    report_id: str
    format: str
    url: Optional[str] = None
    expires_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
