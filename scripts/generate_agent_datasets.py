#!/usr/bin/env python3
"""
Multi-Agent Dataset Generator

Generates domain-specific datasets for all 8 agents in the OpenTalent platform.
"""

import json
import random
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass
class DatasetExample:
    """Standard dataset example format."""

    instruction: str
    response: str
    category: str
    difficulty: str  # beginner, intermediate, advanced
    domain: str
    expected_length: str  # short, medium, long
    has_context: bool = False
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ScoutCoordinatorDatasetGenerator:
    """Generate dataset for Scout Coordinator agent."""

    @staticmethod
    def generate_examples() -> list[DatasetExample]:
        """Generate Scout coordinator training examples."""
        examples = []

        # Sourcing Initiation Examples (50)
        for i in range(50):
            role = random.choice(
                [
                    "Software Engineer",
                    "Product Manager",
                    "Data Scientist",
                    "UX Designer",
                    "DevOps Engineer",
                ]
            )
            level = random.choice(["junior", "mid-level", "senior", "staff"])

            examples.append(
                DatasetExample(
                    instruction=f"Initiate sourcing pipeline for {level} {role} with 5+ years experience",
                    response=f"Pipeline initialized for {role} role. Setting criteria: experience_level={level}, min_years=5, focus_skills=[technical, leadership]. Starting multi-agent scanning across LinkedIn, GitHub, Stack Overflow. Estimated completion: 24 hours.",
                    category="sourcing_initiation",
                    difficulty="beginner",
                    domain="talent_acquisition",
                    expected_length="medium",
                    metadata={"role": role, "level": level},
                )
            )

        # Candidate Profiling Examples (50)
        for i in range(50):
            profile_type = random.choice(["full", "quick", "deep"])

            examples.append(
                DatasetExample(
                    instruction=f"Create {profile_type} candidate profile from: name=John Doe, LinkedIn=john-doe-123, GitHub=johndoe",
                    response=f"Profile created: {profile_type} analysis mode. Extracted: work_history=[3 startups, 2 FAANG], skills=[Python, Go, Kubernetes], projects=15, contributions=450. Relevance score: 0.87/1.0. Ready for engagement.",
                    category="candidate_profiling",
                    difficulty="intermediate",
                    domain="talent_acquisition",
                    expected_length="long",
                    metadata={"profile_type": profile_type},
                )
            )

        # Workflow Orchestration Examples (50)
        for i in range(50):
            workflow_stage = random.choice(
                ["scanning", "scoring", "engagement", "interviewing", "closing"]
            )

            examples.append(
                DatasetExample(
                    instruction=f"Execute {workflow_stage} stage for 100 candidates in pipeline #42",
                    response=f"Starting {workflow_stage} stage for 100 candidates. Coordinating: scanning_agent, quality_agent, engagement_agent. Expected duration: 4 hours. Progress tracking enabled. Notifications will be sent every 30 minutes.",
                    category="workflow_orchestration",
                    difficulty="intermediate",
                    domain="talent_acquisition",
                    expected_length="medium",
                    metadata={"stage": workflow_stage, "count": 100},
                )
            )

        # Agent Coordination Examples (50)
        for i in range(50):
            agents_involved = random.sample(
                ["boolean_agent", "scanning_agent", "quality_agent", "engagement_agent"], 2
            )

            examples.append(
                DatasetExample(
                    instruction=f"Coordinate {' and '.join(agents_involved)} for parallel task execution",
                    response=f"Coordination initiated. Assigning tasks to {agents_involved[0]} and {agents_involved[1]}. Setting shared context and sync points. Monitoring for conflicts and deadlocks. Expected completion: 2 hours.",
                    category="agent_coordination",
                    difficulty="advanced",
                    domain="agent_orchestration",
                    expected_length="medium",
                    metadata={"agents": agents_involved},
                )
            )

        # Execution Monitoring Examples (50)
        for i in range(50):
            metric = random.choice(
                ["success_rate", "processing_time", "quality_score", "error_rate"]
            )

            examples.append(
                DatasetExample(
                    instruction=f"Monitor {metric} for current sourcing pipeline",
                    response=f"{metric} report: current=0.92/1.0, target=0.90/1.0, trend=increasing. Status: HEALTHY. Last updated: 2 minutes ago. Recommendations: maintain current configuration.",
                    category="execution_monitoring",
                    difficulty="intermediate",
                    domain="platform_management",
                    expected_length="medium",
                    metadata={"metric": metric},
                )
            )

        return examples


class BooleanMasteryDatasetGenerator:
    """Generate dataset for Boolean Mastery agent."""

    @staticmethod
    def generate_examples() -> list[DatasetExample]:
        """Generate Boolean query optimization examples."""
        examples = []

        # LinkedIn Query Examples (40)
        roles = ["Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer"]
        skills = ["Python", "Go", "Rust", "Node.js", "SQL", "Kubernetes", "AWS"]

        for i in range(40):
            role = random.choice(roles)
            skill = random.choice(skills)

            examples.append(
                DatasetExample(
                    instruction=f"Generate LinkedIn boolean query for {role} with {skill} skills in USA",
                    response=f'("Software Engineer" OR "Sr. Engineer" OR "Principal Engineer") AND ({skill}) AND (location: "United States") AND (experience: 5+ years)',
                    category="linkedin_queries",
                    difficulty="intermediate",
                    domain="search_optimization",
                    expected_length="short",
                    metadata={"role": role, "skill": skill, "platform": "linkedin"},
                )
            )

        # GitHub Search Examples (40)
        for i in range(40):
            language = random.choice(["python", "golang", "rust", "javascript"])
            repo_type = random.choice(["data-science", "backend", "devops", "infrastructure"])

            examples.append(
                DatasetExample(
                    instruction=f"Generate GitHub search query for {repo_type} projects in {language}",
                    response=f"language:{language} stars:>100 topic:{repo_type} pushed:>2024-01-01 sort:stars-desc",
                    category="github_searches",
                    difficulty="intermediate",
                    domain="search_optimization",
                    expected_length="short",
                    metadata={"language": language, "repo_type": repo_type, "platform": "github"},
                )
            )

        # Stack Overflow Query Examples (40)
        for i in range(40):
            tag = random.choice(["python", "javascript", "go", "kubernetes", "aws"])
            reputation = random.choice(["2000+", "5000+", "10000+"])

            examples.append(
                DatasetExample(
                    instruction=f"Generate Stack Overflow search for experts in {tag} with {reputation} reputation",
                    response=f"[{tag}] is:answer score:>10 user_rep:>{reputation}",
                    category="stack_overflow_queries",
                    difficulty="beginner",
                    domain="search_optimization",
                    expected_length="short",
                    metadata={"tag": tag, "reputation": reputation, "platform": "stackoverflow"},
                )
            )

        # Query Optimization Examples (40)
        for i in range(40):
            issue = random.choice(["too_broad", "too_narrow", "no_results", "too_many_results"])

            examples.append(
                DatasetExample(
                    instruction=f"Optimize query that has issue: {issue}",
                    response=f"Analysis: {issue} detected. Optimization: removing generic terms, adding specific skills, refining date range. New query: [optimized boolean expression]. Expected improvement: 40% relevance increase.",
                    category="query_optimization",
                    difficulty="advanced",
                    domain="search_optimization",
                    expected_length="medium",
                    metadata={"issue": issue},
                )
            )

        # Platform Adaptation Examples (40)
        for i in range(40):
            from_platform = random.choice(["linkedin", "github", "stackoverflow"])
            to_platform = random.choice(["linkedin", "github", "stackoverflow"])

            if from_platform != to_platform:
                examples.append(
                    DatasetExample(
                        instruction=f"Adapt query from {from_platform} syntax to {to_platform} syntax",
                        response="Query adapted successfully. Original: [source query]. Adapted: [target platform syntax]. Equivalent match probability: 0.95/1.0.",
                        category="platform_adaptation",
                        difficulty="advanced",
                        domain="search_optimization",
                        expected_length="medium",
                        metadata={"from_platform": from_platform, "to_platform": to_platform},
                    )
                )

        return examples


class EngagementDatasetGenerator:
    """Generate dataset for Personalized Engagement agent."""

    @staticmethod
    def generate_examples() -> list[DatasetExample]:
        """Generate personalized engagement training examples."""
        examples = []

        # Email Personalization (50)
        companies = ["Google", "Meta", "Apple", "Amazon", "Microsoft", "Netflix"]
        roles = ["Senior Engineer", "Tech Lead", "Staff Engineer"]

        for i in range(50):
            company = random.choice(companies)
            role = random.choice(roles)

            examples.append(
                DatasetExample(
                    instruction=f"Generate personalized email for {role} at {company} with Python expertise",
                    response=f"Subject: Exciting Python Backend Opportunity\nDear [Name],\n\nI came across your impressive work on Python optimization at {company}. Our platform is building next-gen infrastructure where your expertise would be invaluable...",
                    category="email_personalization",
                    difficulty="intermediate",
                    domain="candidate_engagement",
                    expected_length="long",
                    metadata={"company": company, "role": role, "channel": "email"},
                )
            )

        # LinkedIn Outreach (50)
        for i in range(50):
            achievement = random.choice(
                ["open_source_contributions", "speaking_engagements", "patents", "publications"]
            )

            examples.append(
                DatasetExample(
                    instruction=f"Craft LinkedIn connection request mentioning {achievement}",
                    response=f"Hi [Name], I'm impressed by your {achievement} in the DevOps space. Would love to connect and discuss how we're solving similar problems at OpenTalent. Looking forward!",
                    category="linkedin_outreach",
                    difficulty="beginner",
                    domain="candidate_engagement",
                    expected_length="short",
                    metadata={"achievement": achievement, "channel": "linkedin"},
                )
            )

        # WhatsApp Messages (50)
        for i in range(50):
            urgency = random.choice(["normal", "high", "time_sensitive"])

            examples.append(
                DatasetExample(
                    instruction=f"Compose {urgency} WhatsApp message for candidate follow-up",
                    response="Hi! 👋 Quick check-in - are you still open to exploring that principal engineer role we discussed? We'd love to move forward this week. Let me know! 🚀",
                    category="whatsapp_messages",
                    difficulty="beginner",
                    domain="candidate_engagement",
                    expected_length="short",
                    metadata={"urgency": urgency, "channel": "whatsapp"},
                )
            )

        # Follow-up Sequences (50)
        for i in range(50):
            stage = random.choice(
                ["initial_outreach", "after_one_week", "after_two_weeks", "final_followup"]
            )

            examples.append(
                DatasetExample(
                    instruction=f"Generate follow-up message at stage: {stage}",
                    response=f"[Personalized message for {stage} with: prior context, new value proposition, clear call-to-action, respect for candidate's time]",
                    category="follow_up_sequences",
                    difficulty="intermediate",
                    domain="candidate_engagement",
                    expected_length="medium",
                    metadata={
                        "stage": stage,
                        "sequence_number": ["1", "2", "3", "4"][
                            [
                                "initial_outreach",
                                "after_one_week",
                                "after_two_weeks",
                                "final_followup",
                            ].index(stage)
                        ],
                    },
                )
            )

        return examples


class MarketIntelligenceDatasetGenerator:
    """Generate dataset for Market Intelligence agent."""

    @staticmethod
    def generate_examples() -> list[DatasetExample]:
        """Generate market intelligence analysis examples."""
        examples = []

        # Salary Analysis (35)
        roles = ["Software Engineer", "Senior Engineer", "Staff Engineer", "Engineering Manager"]
        locations = ["San Francisco", "New York", "Seattle", "Remote"]

        for i in range(35):
            role = random.choice(roles)
            location = random.choice(locations)

            examples.append(
                DatasetExample(
                    instruction=f"Analyze salary benchmarks for {role} in {location}",
                    response=f"Market analysis for {role} ({location}): Median salary: $185,000, Range: $150K-$250K, 75th percentile: $220K, YoY growth: +3.2%. Data sources: Glassdoor, Payscale, Levels.fyi. Sample size: 500+ reports.",
                    category="salary_analysis",
                    difficulty="intermediate",
                    domain="market_intelligence",
                    expected_length="medium",
                    metadata={"role": role, "location": location},
                )
            )

        # Skill Trends (35)
        skills = ["Python", "Go", "Rust", "Kubernetes", "AWS", "Machine Learning", "TypeScript"]

        for i in range(35):
            skill = random.choice(skills)

            examples.append(
                DatasetExample(
                    instruction=f"Analyze demand trends for {skill} in tech market",
                    response=f"Skill trend analysis for {skill}: Demand growing {random.randint(5, 25)}% YoY, Median salary premium: +{random.randint(10, 30)}%, Job openings: {random.randint(1000, 10000)}+, Learning curve: {random.choice(['steep', 'moderate', 'gentle'])}. Recommendation: High priority skill.",
                    category="skill_trends",
                    difficulty="intermediate",
                    domain="market_intelligence",
                    expected_length="medium",
                    metadata={"skill": skill},
                )
            )

        # Competitor Analysis (40)
        competitors = ["Juicebox", "HireVue", "Pymetrics", "Unbiased", "Vervoe"]

        for i in range(40):
            competitor = random.choice(competitors)

            examples.append(
                DatasetExample(
                    instruction=f"Analyze competitive positioning vs {competitor}",
                    response=f"Competitive analysis: {competitor} strengths: [sourcing at scale], weaknesses: [limited AI avatar capabilities], OpenTalent advantage: [avatar interviews + multi-agent sourcing], market position: [complementary to their sourcing-first approach]",
                    category="competitor_analysis",
                    difficulty="advanced",
                    domain="market_intelligence",
                    expected_length="long",
                    metadata={"competitor": competitor},
                )
            )

        # Market Insights (40)
        for i in range(40):
            insight_type = random.choice(
                ["hiring_volume", "skill_shortage", "compensation_trends", "remote_adoption"]
            )

            examples.append(
                DatasetExample(
                    instruction=f"Generate market insight report on: {insight_type}",
                    response=f"Market insight - {insight_type}: [Quantified data], [Industry analysis], [Regional variations], [Forecast for next quarter], [Implications for OpenTalent platform]",
                    category="market_insights",
                    difficulty="advanced",
                    domain="market_intelligence",
                    expected_length="long",
                    metadata={"insight_type": insight_type},
                )
            )

        return examples


class ToolLeverageDatasetGenerator:
    """Generate dataset for Tool Leverage agent."""

    @staticmethod
    def generate_examples() -> list[DatasetExample]:
        """Generate tool integration and leverage examples."""
        examples = []

        # ATS Sync (35)
        ats_systems = ["Greenhouse", "Lever", "iCIMS", "Workday", "BambooHR"]

        for i in range(35):
            ats = random.choice(ats_systems)

            examples.append(
                DatasetExample(
                    instruction=f"Sync candidate profile to {ats} ATS system",
                    response=f"Sync initiated with {ats}. Mapping fields: name→name, email→email, skills→custom_field_skills. Candidate record created: ID=ATS_12345. Status update enabled for bidirectional sync. Next sync: 1 hour.",
                    category="ats_sync",
                    difficulty="intermediate",
                    domain="tool_integration",
                    expected_length="medium",
                    metadata={"ats_system": ats},
                )
            )

        # CRM Integration (35)
        crms = ["Salesforce", "HubSpot", "Pipedrive", "Monday.com", "Zoho"]

        for i in range(35):
            crm = random.choice(crms)

            examples.append(
                DatasetExample(
                    instruction=f"Push candidate data to {crm} CRM",
                    response=f"{crm} integration: Candidate created in sales pipeline. Contact info synchronized. Interview stage updated. Follow-up reminder scheduled. CRM sync status: SUCCESS.",
                    category="crm_integration",
                    difficulty="intermediate",
                    domain="tool_integration",
                    expected_length="medium",
                    metadata={"crm_system": crm},
                )
            )

        # Data Enrichment (40)
        enrichment_sources = ["ContactOut", "SalesQL", "RocketReach", "ZoomInfo", "Apollo"]

        for i in range(40):
            source = random.choice(enrichment_sources)

            examples.append(
                DatasetExample(
                    instruction=f"Enrich candidate data using {source}",
                    response=f"Data enrichment via {source}: Added phone_number, company_info, recent_title_change, social_profiles. Enrichment score: 0.92/1.0. New fields populated: 12. Data confidence: 95%.",
                    category="data_enrichment",
                    difficulty="intermediate",
                    domain="tool_integration",
                    expected_length="medium",
                    metadata={"source": source},
                )
            )

        # Contact Sync (40)
        for i in range(40):
            sync_type = random.choice(["one_way", "bidirectional", "scheduled", "real_time"])

            examples.append(
                DatasetExample(
                    instruction=f"Configure {sync_type} contact synchronization",
                    response=f"Sync configured: mode={sync_type}, frequency=hourly, conflict_resolution=source_wins, status=active. Ready to sync 250 contacts. Last successful sync: 30 minutes ago.",
                    category="contact_sync",
                    difficulty="advanced",
                    domain="tool_integration",
                    expected_length="medium",
                    metadata={"sync_type": sync_type},
                )
            )

        return examples


class QualityScoringDatasetGenerator:
    """Generate dataset for Quality-Focused agent."""

    @staticmethod
    def generate_examples() -> list[DatasetExample]:
        """Generate quality scoring and evaluation examples."""
        examples = []

        # Skill Matching (50)
        skills = ["Python", "AWS", "Kubernetes", "Machine Learning", "System Design"]
        years = [3, 5, 7, 10, 15]

        for i in range(50):
            skill = random.choice(skills)
            year = random.choice(years)

            examples.append(
                DatasetExample(
                    instruction=f"Score candidate match for {skill} requirement ({year}+ years)",
                    response=f"Skill match score: 0.87/1.0. Candidate has {year} years {skill} experience. Assessment: STRONG MATCH. Evidence: [portfolio projects, job history, certifications]. Confidence: 0.92/1.0.",
                    category="skill_matching",
                    difficulty="intermediate",
                    domain="candidate_quality",
                    expected_length="medium",
                    metadata={"skill": skill, "years": year},
                )
            )

        # Experience Evaluation (50)
        for i in range(50):
            level = random.choice(["junior", "mid", "senior", "staff"])

            examples.append(
                DatasetExample(
                    instruction=f"Evaluate experience level: candidate is {level}-level applying for {random.choice(['senior', 'staff'])} role",
                    response=f"Experience evaluation: Candidate level={level}, Role requirement=senior. Gap analysis: needs 2-3 more years at current pace. Recommendation: Consider for mid-senior hybrid role or invest in mentorship. Fit score: 0.65/1.0.",
                    category="experience_evaluation",
                    difficulty="intermediate",
                    domain="candidate_quality",
                    expected_length="medium",
                    metadata={"level": level},
                )
            )

        # Bias Detection (50)
        for i in range(50):
            bias_type = random.choice(["age", "gender", "location", "university", "accent"])

            examples.append(
                DatasetExample(
                    instruction=f"Check for {bias_type} bias in evaluation",
                    response=f"Bias detection scan: Checking for {bias_type} bias. Analysis: No {bias_type}-based discrimination detected. Evaluation based on: technical skills, experience, culture fit. Risk level: LOW. Recommendation: PROCEED with evaluation.",
                    category="bias_detection",
                    difficulty="advanced",
                    domain="candidate_quality",
                    expected_length="medium",
                    metadata={"bias_type": bias_type},
                )
            )

        # Ranking Logic (50)
        for i in range(50):
            metric = random.choice(
                ["skill_match", "experience", "cultural_fit", "growth_potential", "availability"]
            )

            examples.append(
                DatasetExample(
                    instruction=f"Rank 10 candidates using weighted scoring: skill_match=40%, experience=30%, cultural_fit=20%, growth={metric}=10%",
                    response="Ranking calculation completed. Top candidate: [name], score=0.89/1.0 [breakdown]. 2nd: 0.82, 3rd: 0.78. Recommendations: Interview top-3. Pipeline depth: Strong.",
                    category="ranking_logic",
                    difficulty="advanced",
                    domain="candidate_quality",
                    expected_length="long",
                    metadata={"metric": metric},
                )
            )

        return examples


class ScanningDatasetGenerator:
    """Generate dataset for Proactive Scanning agent."""

    @staticmethod
    def generate_examples() -> list[DatasetExample]:
        """Generate scanning and discovery examples."""
        examples = []

        # Profile Discovery (40)
        for i in range(40):
            platform = random.choice(["LinkedIn", "GitHub", "Stack Overflow"])

            examples.append(
                DatasetExample(
                    instruction=f"Scan {platform} for profiles matching: Python, AWS, 5+ years, USA",
                    response=f"Scan initiated on {platform}. Query executed. Discovered: 150 matching profiles. Retrieved profile data: 150/150 (100%). Processing time: 45 seconds. Next: deduplication and ranking.",
                    category="profile_discovery",
                    difficulty="beginner",
                    domain="talent_scanning",
                    expected_length="medium",
                    metadata={"platform": platform},
                )
            )

        # Data Extraction (40)
        for i in range(40):
            data_type = random.choice(
                ["work_history", "skills", "projects", "social_profiles", "certifications"]
            )

            examples.append(
                DatasetExample(
                    instruction=f"Extract {data_type} from candidate profile",
                    response=f"Data extraction: {data_type} parsed. Results: [structured data]. Extraction confidence: 0.95/1.0. Missing fields: 2%. Quality: HIGH. Ready for enrichment.",
                    category="data_extraction",
                    difficulty="intermediate",
                    domain="talent_scanning",
                    expected_length="medium",
                    metadata={"data_type": data_type},
                )
            )

        # Platform-Specific Scanning (35)
        for i in range(35):
            platform = random.choice(["LinkedIn", "GitHub", "Stack Overflow", "AngelList", "Blind"])

            examples.append(
                DatasetExample(
                    instruction=f"Execute platform-specific scan on {platform} with optimized queries",
                    response=f"{platform} scan completed. Profiles found: {random.randint(50, 500)}. API rate limit: {random.randint(50, 200)}/1000 remaining. Quality: HIGH. Continuing scan...",
                    category="platform_specific",
                    difficulty="advanced",
                    domain="talent_scanning",
                    expected_length="medium",
                    metadata={"platform": platform},
                )
            )

        # Deduplication (35)
        for i in range(35):
            examples.append(
                DatasetExample(
                    instruction="Deduplicate 500 profiles from multiple platform scans",
                    response=f"Deduplication analysis: Comparing across {random.randint(2, 4)} platforms. Duplicates found: {random.randint(20, 60)}. Unique profiles: {500 - random.randint(20, 60)}. Method: email + name fuzzy matching. Confidence: 0.98/1.0.",
                    category="deduplication",
                    difficulty="advanced",
                    domain="talent_scanning",
                    expected_length="medium",
                    metadata={"total_profiles": 500},
                )
            )

        return examples


def save_dataset(examples: list[DatasetExample], filename: str, agent_name: str):
    """Save dataset to JSON file."""
    data = {
        "agent": agent_name,
        "generated_at": datetime.now().isoformat(),
        "total_examples": len(examples),
        "examples": [asdict(ex) for ex in examples],
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved {agent_name}: {len(examples)} examples → {filename}")


def main():
    """Generate all agent datasets."""
    print("\n" + "=" * 70)
    print("OpenTalent Multi-Agent Dataset Generator")
    print("=" * 70 + "\n")

    base_dir = "/home/asif1/open-talent-platform/notebooks/data"

    # Generate Scout dataset
    scout_examples = ScoutCoordinatorDatasetGenerator.generate_examples()
    save_dataset(scout_examples, f"{base_dir}/scout_coordinator_dataset.json", "Scout Coordinator")

    # Generate Boolean Mastery dataset
    boolean_examples = BooleanMasteryDatasetGenerator.generate_examples()
    save_dataset(boolean_examples, f"{base_dir}/boolean_mastery_dataset.json", "Boolean Mastery")

    # Generate Engagement dataset
    engagement_examples = EngagementDatasetGenerator.generate_examples()
    save_dataset(
        engagement_examples, f"{base_dir}/engagement_dataset.json", "Personalized Engagement"
    )

    # Generate Market Intelligence dataset
    market_examples = MarketIntelligenceDatasetGenerator.generate_examples()
    save_dataset(
        market_examples, f"{base_dir}/market_intelligence_dataset.json", "Market Intelligence"
    )

    # Generate Tool Leverage dataset
    tool_examples = ToolLeverageDatasetGenerator.generate_examples()
    save_dataset(tool_examples, f"{base_dir}/tool_leverage_dataset.json", "Tool Leverage")

    # Generate Quality Scoring dataset
    quality_examples = QualityScoringDatasetGenerator.generate_examples()
    save_dataset(quality_examples, f"{base_dir}/quality_scoring_dataset.json", "Quality-Focused")

    # Generate Scanning dataset
    scanning_examples = ScanningDatasetGenerator.generate_examples()
    save_dataset(scanning_examples, f"{base_dir}/scanning_dataset.json", "Proactive Scanning")

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    total_examples = (
        len(scout_examples)
        + len(boolean_examples)
        + len(engagement_examples)
        + len(market_examples)
        + len(tool_examples)
        + len(quality_examples)
        + len(scanning_examples)
    )

    print("\n✅ Generated datasets for 7 agents")
    print(f"📊 Total examples created: {total_examples}")
    print(f"📁 Location: {base_dir}/")
    print("\nNext steps:")
    print("  1. Run dataset validation: python scripts/validate_multi_dataset.py")
    print("  2. Generate inventory report: python scripts/audit_existing_datasets.py")
    print("  3. Upload to Hugging Face: python scripts/upload_all_datasets.py")
    print("\n")


if __name__ == "__main__":
    main()
