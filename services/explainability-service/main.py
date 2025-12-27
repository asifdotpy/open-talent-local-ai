from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel


# Pydantic models for API requests and responses
class InterviewExplanationRequest(BaseModel):
    interview_id: str
    candidate_id: str
    decision: str  # "pass", "fail", "review"
    scores: dict[str, float]
    feedback: str | None = None


class ScoringExplanationRequest(BaseModel):
    candidate_id: str
    job_id: str
    scores: dict[str, float]
    criteria: list[str]


class BiasCheckRequest(BaseModel):
    data: dict[str, Any]
    model_type: str
    threshold: float | None = 0.1


class ExplanationResponse(BaseModel):
    explanation_id: str
    timestamp: str
    summary: str
    details: dict[str, Any]
    confidence: float
    recommendations: list[str]


class BiasReportResponse(BaseModel):
    report_id: str
    timestamp: str
    bias_detected: bool
    bias_score: float
    affected_groups: list[str]
    recommendations: list[str]
    details: dict[str, Any]


# FastAPI app with OpenAPI documentation
app = FastAPI(
    title="OpenTalent Explainability Service API",
    description="""
    AI explainability and transparency service for the OpenTalent platform.

    This service provides insights into AI decision-making processes, model interpretability,
    bias detection, and compliance support for transparent AI operations.

    ## Features
    - **Decision Explanations**: Explain AI interview decisions and candidate scoring
    - **Model Interpretability**: Understand AI model behavior and predictions
    - **Bias Detection**: Identify and report potential bias in AI decisions
    - **Transparency Reports**: Generate detailed explanation reports
    - **Compliance Support**: Support for AI transparency regulations
    """,
    version="1.0.0",
    contact={
        "name": "OpenTalent Platform Team",
        "email": "team@OpenTalent.com",
    },
    license_info={
        "name": "Internal Use",
    },
)


@app.get("/")
async def root():
    """Root endpoint for the Explainability Service."""
    return {"message": "OpenTalent Explainability Service is running!"}


@app.get("/health")
async def health_check():
    """Health check endpoint for the Explainability Service."""
    return {"status": "healthy", "service": "explainability-service", "version": "1.0.0"}


@app.get("/doc")
async def doc_redirect():
    """Alternative redirect to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/api-docs")
async def api_docs_info():
    """Get API documentation information and available endpoints."""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append(
                {
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": getattr(route, "name", ""),
                    "summary": getattr(route, "summary", None),
                }
            )

    return {
        "service": "OpenTalent Explainability Service API",
        "version": "1.0.0",
        "total_endpoints": len(routes),
        "documentation_urls": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "routes": routes,
    }


# Explainability endpoints
@app.post("/explain/interview", response_model=ExplanationResponse)
async def explain_interview_decision(request: InterviewExplanationRequest):
    """Explain AI interview decisions.

    This endpoint provides detailed explanations for AI-powered interview decisions,
    including reasoning, confidence scores, and recommendations for improvement.

    - **interview_id**: Unique identifier for the interview session
    - **candidate_id**: Unique identifier for the candidate
    - **decision**: AI decision ("pass", "fail", "review")
    - **scores**: Dictionary of scoring metrics from the interview
    - **feedback**: Optional additional feedback or context
    """
    # Mock implementation - in production, this would analyze actual AI model decisions
    explanation_id = f"exp_int_{request.interview_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Generate mock explanation based on decision
    if request.decision == "pass":
        summary = "Candidate passed the interview with strong performance across all criteria."
        confidence = 0.92
        recommendations = [
            "Consider for immediate hiring",
            "Schedule technical assessment to validate skills",
        ]
    elif request.decision == "fail":
        summary = "Candidate did not meet the minimum requirements for this position."
        confidence = 0.88
        recommendations = [
            "Provide constructive feedback to candidate",
            "Consider for similar roles with lower requirements",
        ]
    else:  # review
        summary = "Candidate requires additional review before final decision."
        confidence = 0.75
        recommendations = ["Schedule follow-up interview", "Review specific weak areas identified"]

    details = {
        "decision_factors": list(request.scores.keys()),
        "score_breakdown": request.scores,
        "key_strengths": [k for k, v in request.scores.items() if v >= 0.8],
        "areas_for_improvement": [k for k, v in request.scores.items() if v < 0.6],
        "ai_model_used": "talent_ai_interview_v2.1",
        "processing_time_ms": 245,
    }

    return ExplanationResponse(
        explanation_id=explanation_id,
        timestamp=datetime.now().isoformat(),
        summary=summary,
        details=details,
        confidence=confidence,
        recommendations=recommendations,
    )


@app.post("/explain/scoring", response_model=ExplanationResponse)
async def explain_candidate_scoring(request: ScoringExplanationRequest):
    """Explain candidate scoring and ranking decisions.

    Provides detailed breakdown of how candidates are scored and ranked
    for job positions, including factor weights and reasoning.

    - **candidate_id**: Unique identifier for the candidate
    - **job_id**: Unique identifier for the job position
    - **scores**: Dictionary of scoring metrics
    - **criteria**: List of evaluation criteria used
    """
    explanation_id = f"exp_score_{request.candidate_id}_{request.job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Calculate overall score
    overall_score = sum(request.scores.values()) / len(request.scores) if request.scores else 0

    if overall_score >= 0.8:
        summary = (
            "Candidate shows excellent fit for the position with high scores across all criteria."
        )
        confidence = 0.95
    elif overall_score >= 0.6:
        summary = "Candidate shows good potential with solid performance in key areas."
        confidence = 0.82
    else:
        summary = (
            "Candidate may not be the best fit; consider additional training or different roles."
        )
        confidence = 0.78

    details = {
        "job_requirements": request.criteria,
        "score_breakdown": request.scores,
        "overall_score": overall_score,
        "top_performing_criteria": sorted(request.scores.items(), key=lambda x: x[1], reverse=True)[
            :3
        ],
        "scoring_model": "talent_ai_scoring_v1.3",
        "benchmark_comparison": "Above average compared to similar candidates",
    }

    recommendations = [
        "Review candidate's experience in top-performing areas",
        "Consider skill development in lower-scoring areas",
        "Compare with other candidates using similar scoring",
    ]

    return ExplanationResponse(
        explanation_id=explanation_id,
        timestamp=datetime.now().isoformat(),
        summary=summary,
        details=details,
        confidence=confidence,
        recommendations=recommendations,
    )


@app.get("/explain/model/{model_id}", response_model=ExplanationResponse)
async def get_model_explanation(model_id: str):
    """Get explanation of AI model behavior and characteristics.

    Provides insights into how specific AI models work, their training data,
    performance metrics, and decision-making patterns.

    - **model_id**: Unique identifier for the AI model
    """
    # Mock model explanations
    models = {
        "interview_ai_v2.1": {
            "name": "Interview AI v2.1",
            "type": "NLP Classification Model",
            "purpose": "Evaluate candidate responses in technical interviews",
            "accuracy": 0.89,
            "features": ["sentiment_analysis", "technical_accuracy", "communication_skills"],
            "training_data": "5000+ interview transcripts",
            "bias_checks": "Regular monitoring for demographic bias",
        },
        "scoring_ai_v1.3": {
            "name": "Scoring AI v1.3",
            "type": "Regression Model",
            "purpose": "Score candidates based on job requirements",
            "accuracy": 0.91,
            "features": ["skill_matching", "experience_weighting", "cultural_fit"],
            "training_data": "10000+ candidate profiles",
            "bias_checks": "Automated fairness metrics",
        },
    }

    if model_id not in models:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")

    model_info = models[model_id]
    explanation_id = f"exp_model_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    details = {
        "model_info": model_info,
        "performance_metrics": {
            "accuracy": model_info["accuracy"],
            "precision": model_info["accuracy"] - 0.02,
            "recall": model_info["accuracy"] + 0.01,
            "f1_score": model_info["accuracy"],
        },
        "decision_factors": model_info["features"],
        "limitations": [
            "May not account for all soft skills",
            "Performance can vary by industry",
            "Requires sufficient training data",
        ],
        "last_updated": "2025-11-01",
        "version": model_id.split("_")[-1],
    }

    return ExplanationResponse(
        explanation_id=explanation_id,
        timestamp=datetime.now().isoformat(),
        summary=f"Explanation of {model_info['name']} - {model_info['purpose']}",
        details=details,
        confidence=0.95,
        recommendations=[
            "Use model outputs as one factor in decision-making",
            "Regular validation against human expert judgments",
            "Monitor for performance drift over time",
        ],
    )


@app.post("/bias/check", response_model=BiasReportResponse)
async def check_bias(request: BiasCheckRequest):
    """Check for potential bias in AI decisions or data.

    Analyzes data and model outputs for potential bias across protected
    characteristics and provides recommendations for mitigation.

    - **data**: Data to analyze for bias
    - **model_type**: Type of model or analysis being performed
    - **threshold**: Bias detection threshold (default: 0.1)
    """
    report_id = f"bias_{request.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Mock bias analysis - in production, this would use statistical tests
    # and fairness metrics
    bias_detected = False
    bias_score = 0.02  # Low bias detected
    affected_groups = []

    if bias_score > request.threshold:
        bias_detected = True
        affected_groups = ["gender", "age_group"]

    details = {
        "analysis_method": "Statistical parity and equal opportunity testing",
        "metrics_checked": ["demographic_parity", "equalized_odds", "predictive_parity"],
        "protected_attributes": ["gender", "race", "age", "disability_status"],
        "sample_size": len(request.data) if isinstance(request.data, list) else "unknown",
        "confidence_interval": "95%",
        "p_value": 0.23,
        "statistical_tests": {
            "demographic_parity": {"difference": bias_score, "threshold": request.threshold},
            "equal_opportunity": {"difference": 0.015, "threshold": request.threshold},
        },
    }

    recommendations = [
        "Continue monitoring for bias in production",
        "Consider additional training data for underrepresented groups",
        "Implement human oversight for high-stakes decisions",
    ]

    if bias_detected:
        recommendations.extend(
            [
                "Review model training data for representation",
                "Implement bias mitigation techniques",
                "Conduct additional fairness audits",
            ]
        )

    return BiasReportResponse(
        report_id=report_id,
        timestamp=datetime.now().isoformat(),
        bias_detected=bias_detected,
        bias_score=bias_score,
        affected_groups=affected_groups,
        recommendations=recommendations,
        details=details,
    )


@app.get("/bias/report", response_model=BiasReportResponse)
async def get_bias_report(report_id: str | None = None):
    """Get the latest bias analysis report or a specific report by ID.

    Returns comprehensive bias analysis results with detailed metrics
    and recommendations for bias mitigation.

    - **report_id**: Optional specific report ID to retrieve
    """
    # Mock latest report - in production, this would retrieve from database
    if report_id:
        # Return specific report
        pass
    else:
        # Return latest report
        report_id = f"bias_latest_{datetime.now().strftime('%Y%m%d')}"

    return BiasReportResponse(
        report_id=report_id,
        timestamp=datetime.now().isoformat(),
        bias_detected=False,
        bias_score=0.02,
        affected_groups=[],
        recommendations=[
            "Maintain regular bias monitoring",
            "Ensure diverse training data",
            "Implement fairness constraints in model training",
        ],
        details={
            "monitoring_period": "Last 30 days",
            "total_decisions_analyzed": 1250,
            "bias_checks_performed": 5,
            "overall_fairness_score": 0.98,
            "recommendations_implemented": 3,
        },
    )
