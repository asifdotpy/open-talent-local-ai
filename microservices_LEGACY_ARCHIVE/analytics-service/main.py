from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from textblob import TextBlob


# Pydantic models for analytics requests and responses
class SentimentAnalysisRequest(BaseModel):
    text: str


class SentimentAnalysis(BaseModel):
    polarity: float = -1.0
    subjectivity: float = 0.5
    confidence: float = 0.8
    emotion: str = "neutral"
    intensity: float = 0.0
    keywords: list[str] = []


class ResponseQualityRequest(BaseModel):
    response_text: str
    question_context: str


class ResponseQuality(BaseModel):
    overall_score: float = 5.0
    completeness: float = 0.5
    relevance: float = 0.5
    clarity: float = 0.5
    technical_accuracy: float = 0.5
    strengths: list[str] = []
    improvements: list[str] = []


class BiasDetectionRequest(BaseModel):
    text: str
    participants: list[dict[str, Any]] | None = None


class BiasDetection(BaseModel):
    bias_score: float = 0.0
    flags: list[str] = []
    severity: str = "low"
    categories: list[str] = []
    recommendations: list[str] = []


class ExpertiseAssessmentRequest(BaseModel):
    response_text: str
    question_context: str


class ExpertiseAssessment(BaseModel):
    level: str = "intermediate"
    confidence: float = 0.7
    technical_skills: list[str] = []
    knowledge_gaps: list[str] = []
    experience_years: int | None = 3


class InterviewPerformanceRequest(BaseModel):
    room_id: str
    response_analyses: list[dict[str, Any]] = []


class InterviewPerformance(BaseModel):
    overall_score: float = 5.0
    sentiment_trend: str = "neutral"
    expertise_level: str = "unknown"
    bias_incidents: int = 0
    quality_trend: str = "unknown"
    recommendations: list[str] = []


class IntelligenceReportRequest(BaseModel):
    room_id: str
    analyses: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    room_created_at: str


class IntelligenceReport(BaseModel):
    summary: dict[str, Any] = {}
    sentiment_analysis: dict[str, Any] = {}
    bias_report: dict[str, Any] = {}
    expertise_evaluation: dict[str, Any] = {}
    quality_metrics: dict[str, Any] = {}
    recommendations: list[str] = []
    interview_effectiveness: float = 5.0


# FastAPI app
app = FastAPI(
    title="OpenTalent Analytics Service API",
    description="AI-powered analytics and intelligence service for interview analysis",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Root endpoint for the Analytics Service."""
    return {"message": "OpenTalent Analytics Service - AI Interview Intelligence"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "analytics"}


# --- Sentiment Analysis ---
@app.post("/api/v1/analyze/sentiment", response_model=SentimentAnalysis)
async def analyze_sentiment(request: SentimentAnalysisRequest):
    """Analyze sentiment of text using TextBlob."""
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
    """Analyze the quality of a candidate response."""
    try:
        # Basic quality metrics
        length_score = min(len(request.response_text) / 200, 1.0) * 2.5

        # Relevance check (simple keyword matching)
        question_keywords = set(request.question_context.lower().split())
        response_keywords = set(request.response_text.lower().split())
        relevance_score = len(question_keywords.intersection(response_keywords)) / max(len(question_keywords), 1) * 2.5

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
async def assess_expertise(request: ExpertiseAssessmentRequest):
    """Assess candidate's expertise level from response."""
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
        level = "intermediate" if max_score == 0 else max(expertise_scores, key=expertise_scores.get)

        # Estimate years of experience
        years_estimate = {"beginner": 1, "intermediate": 3, "advanced": 5, "expert": 8}.get(level, 3)

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
        avg_sentiment = sum(a.get("sentiment", {}).get("polarity", 0) for a in analyses) / len(analyses)
        avg_quality = sum(a.get("quality", {}).get("overall_score", 5) for a in analyses) / len(analyses)
        total_bias = sum(len(a.get("bias_detection", {}).get("flags", [])) for a in analyses)

        # Determine trends
        sentiment_trend = "positive" if avg_sentiment > 0.2 else "negative" if avg_sentiment < -0.2 else "neutral"
        quality_trend = "improving" if avg_quality > 7 else "declining" if avg_quality < 5 else "stable"

        # Expertise level (use latest assessment)
        expertise_level = (
            analyses[-1].get("expertise_assessment", {}).get("level", "unknown") if analyses else "unknown"
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
        avg_quality = sum(a.get("quality", {}).get("overall_score", 5) for a in analyses) / len(analyses)
        avg_sentiment = sum(a.get("sentiment", {}).get("polarity", 0) for a in analyses) / len(analyses)

        # Sentiment analysis summary
        sentiment_distribution = {
            "positive": len([a for a in analyses if a.get("sentiment", {}).get("polarity", 0) > 0.2]),
            "neutral": len([a for a in analyses if -0.2 <= a.get("sentiment", {}).get("polarity", 0) <= 0.2]),
            "negative": len([a for a in analyses if a.get("sentiment", {}).get("polarity", 0) < -0.2]),
        }

        # Bias report
        total_bias_incidents = sum(len(a.get("bias_detection", {}).get("flags", [])) for a in analyses)
        bias_categories = {}
        for a in analyses:
            for category in a.get("bias_detection", {}).get("categories", []):
                bias_categories[category] = bias_categories.get(category, 0) + 1

        # Expertise evaluation
        expertise_levels = [a.get("expertise_assessment", {}).get("level", "unknown") for a in analyses]
        most_common_expertise = (
            max(set(expertise_levels), key=expertise_levels.count) if expertise_levels else "unknown"
        )

        # Quality metrics
        quality_trends = {
            "completeness": sum(a.get("quality", {}).get("completeness", 0.5) for a in analyses) / len(analyses),
            "relevance": sum(a.get("quality", {}).get("relevance", 0.5) for a in analyses) / len(analyses),
            "clarity": sum(a.get("quality", {}).get("clarity", 0.5) for a in analyses) / len(analyses),
            "technical_accuracy": sum(a.get("quality", {}).get("technical_accuracy", 0.5) for a in analyses)
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
                "duration_minutes": (datetime.now() - datetime.fromisoformat(request.room_created_at)).total_seconds()
                / 60,
            },
            sentiment_analysis={
                "overall_sentiment": "positive"
                if avg_sentiment > 0.2
                else "negative"
                if avg_sentiment < -0.2
                else "neutral",
                "distribution": sentiment_distribution,
                "emotional_intensity": sum(a.get("sentiment", {}).get("intensity", 0) for a in analyses)
                / len(analyses),
            },
            bias_report={
                "total_incidents": total_bias_incidents,
                "categories": bias_categories,
                "severity_distribution": {
                    "low": len([a for a in analyses if a.get("bias_detection", {}).get("severity", "low") == "low"]),
                    "medium": len(
                        [a for a in analyses if a.get("bias_detection", {}).get("severity", "low") == "medium"]
                    ),
                    "high": len([a for a in analyses if a.get("bias_detection", {}).get("severity", "low") == "high"]),
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
                    a.get("expertise_assessment", {}).get("experience_years", 0) or 0 for a in analyses
                )
                / len(analyses),
            },
            quality_metrics={
                "average_score": round(avg_quality, 2),
                "trends": quality_trends,
                "strengths_distribution": {
                    "high_quality": len([a for a in analyses if a.get("quality", {}).get("overall_score", 5) >= 8]),
                    "medium_quality": len(
                        [a for a in analyses if 6 <= a.get("quality", {}).get("overall_score", 5) < 8]
                    ),
                    "low_quality": len([a for a in analyses if a.get("quality", {}).get("overall_score", 5) < 6]),
                },
            },
            recommendations=recommendations,
            interview_effectiveness=round(effectiveness, 2),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port)
