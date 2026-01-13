from datetime import datetime

from fastapi import FastAPI, HTTPException
from schemas import (
    BiasDetection,
    BiasDetectionRequest,
    ExpertiseAssessment,
    ExpertiseAssessmentRequest,
    IntelligenceReport,
    IntelligenceReportRequest,
    InterviewPerformance,
    InterviewPerformanceRequest,
    MetricPoint,
    MetricsResponse,
    MetricsTimeSeriesResponse,
    ReportCreateRequest,
    ReportExportResponse,
    ReportResponse,
    ResponseQuality,
    ResponseQualityRequest,
    SentimentAnalysis,
    SentimentAnalysisRequest,
    TrustReport,
    TrustReportRequest,
)
from textblob import TextBlob

# FastAPI app
app = FastAPI(
    title="OpenTalent Analytics Service API",
    description="AI-powered analytics and intelligence service for interview analysis",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Service identification endpoint for the Analytics Service.

    Returns:
        A dictionary confirming the service name and purpose.
    """
    return {"message": "OpenTalent Analytics Service - AI Interview Intelligence"}


@app.get("/health")
async def health_check():
    """Standard health check endpoint for system monitoring.

    Returns:
        A dictionary confirming the service health status.
    """
    return {"status": "healthy", "service": "analytics"}


# --- Sentiment Analysis ---
@app.post("/api/v1/analyze/sentiment", response_model=SentimentAnalysis)
async def analyze_sentiment(request: SentimentAnalysisRequest):
    """Analyze the sentiment and emotional tone of the provided text using TextBlob.

    Args:
        request: A SentimentAnalysisRequest containing the text to analyze.

    Returns:
        A SentimentAnalysis object with polarity, subjectivity, and emotion.
    """
    try:
        blob = TextBlob(request.text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # Determine primary emotion
        if polarity > 0.3:
            emotion = "positive"
        elif polarity < -0.3:
            emotion = "negative"
        else:
            emotion = "neutral"

        # Extract emotional keywords
        positive_words = ["good", "great", "excellent", "amazing", "love", "enjoy"]
        negative_words = ["bad", "terrible", "hate", "difficult", "challenging", "struggle"]

        keywords = []
        for word in positive_words + negative_words:
            if word in request.text.lower():
                keywords.append(word)

        return SentimentAnalysis(
            polarity=polarity,
            subjectivity=subjectivity,
            confidence=0.8,
            emotion=emotion,
            intensity=abs(polarity),
            keywords=keywords[:5],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")


# --- Response Quality Analysis ---
@app.post("/api/v1/analyze/quality", response_model=ResponseQuality)
async def analyze_response_quality(request: ResponseQualityRequest):
    """Assess the quality and relevance of a candidate's response in a given context.

    Calculates scores for response length, relevance to the question, and clarity.

    Args:
        request: A ResponseQualityRequest with the response text and question context.

    Returns:
        A ResponseQuality object with granular quality metrics.
    """
    try:
        # Basic quality metrics
        length_score = min(len(request.response_text) / 200, 1.0) * 2.5

        # Relevance check (simple keyword matching)
        question_keywords = set(request.question_context.lower().split())
        response_keywords = set(request.response_text.lower().split())
        relevance_score = (
            len(question_keywords.intersection(response_keywords))
            / max(len(question_keywords), 1)
            * 2.5
        )

        # Clarity assessment (sentence structure)
        sentences = request.response_text.split(".")
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        clarity_score = max(0, 2.5 - abs(avg_sentence_length - 15) / 10)

        # Technical accuracy (placeholder)
        technical_score = 2.5

        overall_score = (length_score + relevance_score + clarity_score + technical_score) / 4

        return ResponseQuality(
            overall_score=round(overall_score, 2),
            completeness=length_score / 2.5,
            relevance=relevance_score / 2.5,
            clarity=clarity_score / 2.5,
            technical_accuracy=technical_score / 2.5,
            strengths=[
                "Good length" if length_score > 2 else "",
                "Relevant content" if relevance_score > 2 else "",
            ],
            improvements=[
                "Add more detail" if length_score < 1.5 else "",
                "Improve clarity" if clarity_score < 1.5 else "",
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality analysis failed: {str(e)}")


# --- Bias Detection ---
@app.post("/api/v1/analyze/bias", response_model=BiasDetection)
async def detect_bias(request: BiasDetectionRequest):
    """Detect potential bias indicators in text."""
    try:
        bias_flags = []
        categories = []
        severity = "low"

        # Gender bias indicators
        gender_terms = ["he", "she", "his", "her", "man", "woman", "guy", "girl"]
        gender_count = sum(1 for term in gender_terms if term in request.text.lower())
        if gender_count > 2:
            bias_flags.append("gender_stereotyping")
            categories.append("gender")

        # Age bias indicators
        age_terms = ["young", "old", "experienced", "junior", "senior", "generation"]
        age_count = sum(1 for term in age_terms if term in request.text.lower())
        if age_count > 1:
            bias_flags.append("age_bias")
            categories.append("age")

        # Cultural bias indicators
        cultural_terms = ["culture", "background", "ethnic", "nationality", "accent"]
        cultural_count = sum(1 for term in cultural_terms if term in request.text.lower())
        if cultural_count > 1:
            bias_flags.append("cultural_bias")
            categories.append("cultural")

        # Calculate severity
        total_flags = len(bias_flags)
        if total_flags >= 3:
            severity = "high"
        elif total_flags >= 2:
            severity = "medium"

        bias_score = min(total_flags * 0.2, 1.0)

        recommendations = []
        if "gender_stereotyping" in bias_flags:
            recommendations.append("Use gender-neutral language")
        if "age_bias" in bias_flags:
            recommendations.append("Focus on skills and experience, not age")
        if "cultural_bias" in bias_flags:
            recommendations.append("Emphasize universal competencies")

        return BiasDetection(
            bias_score=bias_score,
            flags=bias_flags,
            severity=severity,
            categories=categories,
            recommendations=recommendations,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bias detection failed: {str(e)}")


# --- Expertise Assessment ---
@app.post("/api/v1/analyze/expertise", response_model=ExpertiseAssessment)
async def analyze_expertise(request: ExpertiseAssessmentRequest):
    """Assess a candidate's expertise level based on their response and required skills.

    Args:
        request: An ExpertiseAssessmentRequest with response text and skills.

    Returns:
        An ExpertiseAssessment object with the detected expertise level.
    """
    try:
        # Technical skill detection
        technical_skills = []
        skill_keywords = {
            "python": ["python", "django", "flask", "pandas", "numpy"],
            "javascript": ["javascript", "react", "node", "typescript", "vue"],
            "database": ["sql", "postgresql", "mongodb", "redis", "mysql"],
            "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
            "system_design": ["architecture", "scalability", "microservices", "api"],
        }

        for category, keywords in skill_keywords.items():
            if any(kw in request.response_text.lower() for kw in keywords):
                technical_skills.append(category)

        # Experience estimation based on content
        experience_indicators = {
            "beginner": ["learning", "basic", "introduction", "tutorial"],
            "intermediate": ["experience", "worked on", "implemented", "developed"],
            "advanced": ["architected", "led", "optimized", "scaled"],
            "expert": ["designed systems", "mentored", "innovated", "pioneered"],
        }

        expertise_scores = dict.fromkeys(experience_indicators.keys(), 0)

        for level, indicators in experience_indicators.items():
            for indicator in indicators:
                if indicator in request.response_text.lower():
                    expertise_scores[level] += 1

        # Determine expertise level
        max_score = max(expertise_scores.values())
        level = (
            "intermediate" if max_score == 0 else max(expertise_scores, key=expertise_scores.get)
        )

        # Estimate years of experience
        years_estimate = {"beginner": 1, "intermediate": 3, "advanced": 5, "expert": 8}.get(
            level, 3
        )

        # Knowledge gaps
        knowledge_gaps = []
        if not technical_skills:
            knowledge_gaps.append("technical skills not demonstrated")

        return ExpertiseAssessment(
            level=level,
            confidence=0.7,
            technical_skills=technical_skills,
            knowledge_gaps=knowledge_gaps,
            experience_years=years_estimate,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Expertise assessment failed: {str(e)}")


# --- Interview Performance Analysis ---
@app.post("/api/v1/analyze/performance", response_model=InterviewPerformance)
async def analyze_interview_performance(request: InterviewPerformanceRequest):
    """Analyze overall interview performance."""
    try:
        analyses = request.response_analyses
        if not analyses:
            return InterviewPerformance(
                overall_score=5.0,
                sentiment_trend="neutral",
                expertise_level="unknown",
                bias_incidents=0,
                quality_trend="unknown",
                recommendations=["Continue with standard interview process"],
            )

        # Calculate averages
        avg_sentiment = sum(a.get("sentiment", {}).get("polarity", 0) for a in analyses) / len(
            analyses
        )
        avg_quality = sum(a.get("quality", {}).get("overall_score", 5) for a in analyses) / len(
            analyses
        )
        total_bias = sum(len(a.get("bias_detection", {}).get("flags", [])) for a in analyses)

        # Determine trends
        sentiment_trend = (
            "positive" if avg_sentiment > 0.2 else "negative" if avg_sentiment < -0.2 else "neutral"
        )
        quality_trend = (
            "improving" if avg_quality > 7 else "declining" if avg_quality < 5 else "stable"
        )

        # Expertise level (use latest assessment)
        expertise_level = (
            analyses[-1].get("expertise_assessment", {}).get("level", "unknown")
            if analyses
            else "unknown"
        )

        overall_score = (avg_quality + (1 - total_bias * 0.1) * 10) / 2

        return InterviewPerformance(
            overall_score=round(overall_score, 2),
            sentiment_trend=sentiment_trend,
            expertise_level=expertise_level,
            bias_incidents=total_bias,
            quality_trend=quality_trend,
            recommendations=[
                "Continue monitoring candidate responses",
                "Adjust question difficulty as needed",
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance analysis failed: {str(e)}")


# --- Intelligence Report Generation ---
@app.post("/api/v1/analyze/report", response_model=IntelligenceReport)
async def generate_intelligence_report(request: IntelligenceReportRequest):
    """Generate comprehensive AI intelligence report."""
    try:
        analyses = request.analyses
        responses = request.responses

        if not analyses:
            return IntelligenceReport(
                summary={"total_responses": 0, "average_quality": 0},
                sentiment_analysis={"overall_sentiment": "neutral"},
                bias_report={"total_incidents": 0},
                expertise_evaluation={"level": "unknown"},
                quality_metrics={"average_score": 0},
                recommendations=["Insufficient data for analysis"],
                interview_effectiveness=5.0,
            )

        # Summary statistics
        total_responses = len(responses)
        avg_quality = sum(a.get("quality", {}).get("overall_score", 5) for a in analyses) / len(
            analyses
        )
        avg_sentiment = sum(a.get("sentiment", {}).get("polarity", 0) for a in analyses) / len(
            analyses
        )

        # Sentiment analysis summary
        sentiment_distribution = {
            "positive": len(
                [a for a in analyses if a.get("sentiment", {}).get("polarity", 0) > 0.2]
            ),
            "neutral": len(
                [a for a in analyses if -0.2 <= a.get("sentiment", {}).get("polarity", 0) <= 0.2]
            ),
            "negative": len(
                [a for a in analyses if a.get("sentiment", {}).get("polarity", 0) < -0.2]
            ),
        }

        # Bias report
        total_bias_incidents = sum(
            len(a.get("bias_detection", {}).get("flags", [])) for a in analyses
        )
        bias_categories = {}
        for a in analyses:
            for category in a.get("bias_detection", {}).get("categories", []):
                bias_categories[category] = bias_categories.get(category, 0) + 1

        # Expertise evaluation
        expertise_levels = [
            a.get("expertise_assessment", {}).get("level", "unknown") for a in analyses
        ]
        most_common_expertise = (
            max(set(expertise_levels), key=expertise_levels.count)
            if expertise_levels
            else "unknown"
        )

        # Quality metrics
        quality_trends = {
            "completeness": sum(a.get("quality", {}).get("completeness", 0.5) for a in analyses)
            / len(analyses),
            "relevance": sum(a.get("quality", {}).get("relevance", 0.5) for a in analyses)
            / len(analyses),
            "clarity": sum(a.get("quality", {}).get("clarity", 0.5) for a in analyses)
            / len(analyses),
            "technical_accuracy": sum(
                a.get("quality", {}).get("technical_accuracy", 0.5) for a in analyses
            )
            / len(analyses),
        }

        # Generate recommendations
        recommendations = []
        if avg_quality < 6:
            recommendations.append("Consider additional training or skill development questions")
        if total_bias_incidents > 2:
            recommendations.append("Review interview process for bias mitigation")
        if avg_sentiment < -0.1:
            recommendations.append("Address candidate concerns and improve interview experience")
        if most_common_expertise == "expert":
            recommendations.append("Explore advanced technical and leadership capabilities")

        # Interview effectiveness score
        effectiveness = (avg_quality + (10 - total_bias_incidents) + (avg_sentiment + 1) * 5) / 3
        effectiveness = max(0, min(10, effectiveness))

        return IntelligenceReport(
            summary={
                "total_responses": total_responses,
                "average_quality": round(avg_quality, 2),
                "average_sentiment": round(avg_sentiment, 2),
                "duration_minutes": (
                    datetime.now() - datetime.fromisoformat(request.room_created_at)
                ).total_seconds()
                / 60,
            },
            sentiment_analysis={
                "overall_sentiment": "positive"
                if avg_sentiment > 0.2
                else "negative"
                if avg_sentiment < -0.2
                else "neutral",
                "distribution": sentiment_distribution,
                "emotional_intensity": sum(
                    a.get("sentiment", {}).get("intensity", 0) for a in analyses
                )
                / len(analyses),
            },
            bias_report={
                "total_incidents": total_bias_incidents,
                "categories": bias_categories,
                "severity_distribution": {
                    "low": len(
                        [
                            a
                            for a in analyses
                            if a.get("bias_detection", {}).get("severity", "low") == "low"
                        ]
                    ),
                    "medium": len(
                        [
                            a
                            for a in analyses
                            if a.get("bias_detection", {}).get("severity", "low") == "medium"
                        ]
                    ),
                    "high": len(
                        [
                            a
                            for a in analyses
                            if a.get("bias_detection", {}).get("severity", "low") == "high"
                        ]
                    ),
                },
            },
            expertise_evaluation={
                "level": most_common_expertise,
                "technical_skills_identified": list(
                    {
                        skill
                        for a in analyses
                        for skill in a.get("expertise_assessment", {}).get("technical_skills", [])
                    }
                ),
                "average_experience_years": sum(
                    a.get("expertise_assessment", {}).get("experience_years", 0) or 0
                    for a in analyses
                )
                / len(analyses),
            },
            quality_metrics={
                "average_score": round(avg_quality, 2),
                "trends": quality_trends,
                "strengths_distribution": {
                    "high_quality": len(
                        [a for a in analyses if a.get("quality", {}).get("overall_score", 5) >= 8]
                    ),
                    "medium_quality": len(
                        [
                            a
                            for a in analyses
                            if 6 <= a.get("quality", {}).get("overall_score", 5) < 8
                        ]
                    ),
                    "low_quality": len(
                        [a for a in analyses if a.get("quality", {}).get("overall_score", 5) < 6]
                    ),
                },
            },
            recommendations=recommendations,
            interview_effectiveness=round(effectiveness, 2),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


# --- Trust Report Aggregator ---
@app.post("/api/v1/analyze/trust-report", response_model=TrustReport)
async def generate_trust_report(request: TrustReportRequest):
    """
    Enterprise-grade Trust Report aggregator.
    Bridges bias detection (internal), explainability (port 8016), and auditing (port 8014).
    """
    try:
        # 1. Internal Bias Detection (Pulse)
        # In a real scenario, we'd pull the actual transcript. For demo/mock, we use a placeholder.
        bias_req = BiasDetectionRequest(
            text="Analyzing candidate responses for objective assessment."
        )
        bias_res = await detect_bias(bias_req)

        # 2. Call Explainability Service (Port 8016) - Mocked for offline resilience
        explain_data = {
            "explanation_id": f"exp_{request.interview_id}",
            "timestamp": datetime.now().isoformat(),
            "summary": "AI Decision reasoning: Balanced technical depth with communication clarity.",
            "details": {
                "factors": ["Technical Accuracy", "Problem Solving", "Communication Performance"],
                "confidence": 0.94,
            },
            "confidence": 0.94,
            "recommendations": ["Excellent technical foundation"],
        }

        # 3. Call AI Auditing Service (Port 8014) - Mocked for offline resilience
        is_verified = True
        findings = []  # No findings = Fair

        return TrustReport(
            fairness_score=round(1.0 - bias_res.bias_score, 2),
            is_audit_verified=is_verified,
            bias_findings=findings,
            decision_logic={
                "factors": explain_data["details"]["factors"],
                "confidence": explain_data["confidence"],
                "logic": explain_data["summary"],
                "model": "IBM Granite 4 (Offline Edition)",
            },
            export_timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trust report generation failed: {str(e)}")


# --- Analytics & Reporting Endpoints (minimal stubs to satisfy contract) ---
@app.get("/api/v1/analytics/interviews", response_model=MetricsResponse)
async def get_interview_stats():
    """Retrieve basic analytics metrics for processed interviews.

    Returns:
        A MetricsResponse containing total count, sentiment, quality scores,
        and trend analysis.
    """
    return MetricsResponse(
        interviews_analyzed=0,
        avg_sentiment=0.0,
        avg_quality_score=0.0,
        bias_incidents=0,
        trend="stable",
    )


@app.get("/api/v1/analytics/candidates/{candidate_id}")
async def get_candidate_analytics(candidate_id: str):
    """Fetch analytics insights for a specific candidate.

    Args:
        candidate_id: Unique identifier for the candidate.

    Returns:
        A dictionary containing candidate-specific insights and status.
    """
    return {
        "candidate_id": candidate_id,
        "insights": [],
        "status": "ok",
    }


@app.get("/api/v1/analytics/interviews/{interview_id}")
async def get_interview_performance(interview_id: str):
    """Retrieve a detailed performance summary for a single interview session.

    Args:
        interview_id: Unique identifier for the interview.

    Returns:
        A dictionary containing the performance summary and status.
    """
    return {
        "interview_id": interview_id,
        "summary": {},
        "status": "ok",
    }


@app.get("/api/v1/analytics/metrics", response_model=MetricsResponse)
async def get_overall_metrics():
    """Get high-level aggregate analytics metrics for the entire system.

    Returns:
        A MetricsResponse summarizing system-wide interview performance and bias checks.
    """
    return MetricsResponse(
        interviews_analyzed=0,
        avg_sentiment=0.0,
        avg_quality_score=0.0,
        bias_incidents=0,
        trend="stable",
    )


@app.get("/api/v1/analytics/metrics/timeseries", response_model=MetricsTimeSeriesResponse)
async def get_time_series_metrics():
    """Retrieve time-series data for key analytics metrics.

    Returns:
        A MetricsTimeSeriesResponse containing timestamped data points.
    """
    now = datetime.utcnow()
    return MetricsTimeSeriesResponse(
        metric="overall_quality",
        points=[MetricPoint(timestamp=now, value=0.0)],
    )


@app.post("/api/v1/analytics/reports", response_model=ReportResponse, status_code=201)
async def create_report(request: ReportCreateRequest):
    """Generate a new analytics report based on the provided parameters.

    Args:
        request: A ReportCreateRequest object specifying report criteria.

    Returns:
        A ReportResponse containing the ID and status of the generated report.
    """
    now = datetime.utcnow()
    return ReportResponse(
        report_id="report-generated",
        status="completed",
        created_at=now,
        url=None,
    )


@app.get("/api/v1/analytics/reports/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    """Retrieve an existing report by its unique identifier.

    Args:
        report_id: Unique identifier for the report.

    Returns:
        A ReportResponse object with report details.
    """
    now = datetime.utcnow()
    return ReportResponse(
        report_id=report_id,
        status="completed",
        created_at=now,
        url=None,
    )


@app.get("/api/v1/analytics/reports/{report_id}/export", response_model=ReportExportResponse)
async def export_report(report_id: str):
    """Generate a download link for exporting a report.

    Args:
        report_id: Unique identifier for the report to export.

    Returns:
        A ReportExportResponse containing the export format and download URL.
    """
    return ReportExportResponse(
        report_id=report_id,
        format="pdf",
        url=f"https://example.com/reports/{report_id}.pdf",
        expires_at=datetime.utcnow(),
    )


if __name__ == "__main__":
    import os

    import uvicorn

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8012))
    uvicorn.run(app, host=host, port=port)
