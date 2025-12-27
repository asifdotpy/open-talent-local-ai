#!/usr/bin/env python3
"""
OpenTalent Language Model Training Dataset Generator

Generates 2,100+ instruction-response pairs to train the language model
to handle complete OpenTalent recruitment pipeline operations.

Covers 8 agent domains + 35 subcategories across all platform functions.
"""

import json
import random
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class TrainingExample:
    """Single training example for LLM"""

    instruction: str
    input: str
    response: str
    domain: str
    agent: str
    category: str
    difficulty: str
    context: dict
    metadata: dict


class LLMTrainingDataGenerator:
    """Generate comprehensive LLM training dataset for OpenTalent platform"""

    def __init__(self, output_dir: str = "notebooks/data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.examples: list[TrainingExample] = []

    # ─────────────────────────────────────────────────────────────────────
    # DOMAIN 1: SCOUT COORDINATOR (250 examples)
    # ─────────────────────────────────────────────────────────────────────

    def generate_scout_coordinator_examples(self) -> list[TrainingExample]:
        """Scout Coordinator: Sourcing strategy and pipeline orchestration"""
        examples = []

        # Category 1: Pipeline Initiation (50 examples)
        job_reqs = [
            ("Senior Backend Engineer", "Python, AWS, Kubernetes", "5+ years"),
            ("Data Scientist", "ML, SQL, Statistics", "3+ years"),
            ("Frontend Developer", "React, TypeScript, CSS", "3+ years"),
            ("DevOps Engineer", "Linux, CI/CD, Docker", "4+ years"),
            ("Product Manager", "Technical background preferred", "5+ years"),
        ]

        for job_title, skills, exp in job_reqs:
            for urgency, timeline in [
                ("high", "2 weeks"),
                ("medium", "4 weeks"),
                ("low", "8 weeks"),
            ]:
                for headcount in [1, 3, 5]:
                    examples.append(
                        TrainingExample(
                            instruction=f"Given a job requirement for {headcount} {job_title}(s) needed in {timeline}, create a sourcing strategy",
                            input=f"Job: {job_title}\nRequired: {skills}\nExperience: {exp}\nUrgency: {urgency}\nHeadcount: {headcount}\nTimeline: {timeline}",
                            response=self._generate_sourcing_strategy(
                                job_title, headcount, timeline, urgency
                            ),
                            domain="sourcing",
                            agent="scout-coordinator",
                            category="pipeline-initiation",
                            difficulty=self._assess_difficulty(
                                ["medium", "high"][urgency == "high"]
                            ),
                            context={
                                "scenario": "Recruiter initiating new sourcing pipeline",
                                "constraints": [
                                    "Multi-channel approach",
                                    "Timeline constraints",
                                    f"Need {headcount} candidates",
                                ],
                                "expected_behavior": "Strategic sourcing plan with channel selection and timing",
                            },
                            metadata=self._create_metadata("synthetic"),
                        )
                    )

        # Category 2: Channel Selection (50 examples)
        channels = [
            "LinkedIn",
            "GitHub",
            "StackOverflow",
            "Recruitment Agency",
            "Employee Referral",
            "Job Boards",
        ]
        for _ in range(50):
            role = random.choice([j[0] for j in job_reqs])
            selected_channels = random.sample(channels, k=random.randint(2, 4))
            examples.append(
                TrainingExample(
                    instruction=f"For a {role} role, rank these channels by effectiveness and explain why",
                    input=f"Role: {role}\nAvailable channels: {', '.join(channels)}\nTarget: 10 qualified candidates in 3 weeks",
                    response=self._rank_channels(selected_channels, role),
                    domain="sourcing",
                    agent="scout-coordinator",
                    category="channel-selection",
                    difficulty=random.choice(["beginner", "intermediate"]),
                    context={
                        "scenario": "Selecting sourcing channels for specific role",
                        "constraints": [
                            "Time constraint: 3 weeks",
                            "Quality threshold: qualified candidates",
                        ],
                        "expected_behavior": "Data-driven channel ranking with reasoning",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Category 3: Workflow Orchestration (50 examples)
        for _ in range(50):
            examples.append(
                TrainingExample(
                    instruction="What's the ideal sequence of agent activations for a typical hiring pipeline?",
                    input="Workflow phases: Sourcing → Search → Engagement → Assessment → Offer\nTeam size: 3 recruiters\nTarget: Fill 5 roles",
                    response=self._generate_workflow_sequence(),
                    domain="sourcing",
                    agent="scout-coordinator",
                    category="workflow-orchestration",
                    difficulty="intermediate",
                    context={
                        "scenario": "Planning agent coordination in recruitment pipeline",
                        "constraints": ["Parallel where possible", "Maintain quality gates"],
                        "expected_behavior": "Logical workflow with dependency management",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Category 4: Vendor Coordination (50 examples)
        for _ in range(50):
            examples.append(
                TrainingExample(
                    instruction="How would you coordinate with an external recruitment agency for pipeline success?",
                    input="Agency: Specialized in tech recruiting\nCapacity: 20 candidate leads/week\nCost: $2k/placement\nTarget roles: Backend engineers",
                    response=self._vendor_coordination_strategy(),
                    domain="sourcing",
                    agent="scout-coordinator",
                    category="vendor-coordination",
                    difficulty=random.choice(["intermediate", "advanced"]),
                    context={
                        "scenario": "Managing external recruitment partnerships",
                        "constraints": ["Cost control", "Quality consistency", "Timeline"],
                        "expected_behavior": "Structured partnership framework with KPIs",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Category 5: Success Metrics (50 examples)
        for _ in range(50):
            examples.append(
                TrainingExample(
                    instruction="Define pipeline health metrics for a sourcing operation",
                    input="Team: 2 sourcers, 1 coordinator\nMonthly capacity: 50 sourcing activities\nGoal: Fill 5 engineering roles",
                    response=self._pipeline_metrics(),
                    domain="sourcing",
                    agent="scout-coordinator",
                    category="success-metrics",
                    difficulty="intermediate",
                    context={
                        "scenario": "Setting up pipeline KPI tracking",
                        "constraints": ["Actionable metrics", "Easy to measure"],
                        "expected_behavior": "Specific, measurable metrics with targets",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        return examples

    # ─────────────────────────────────────────────────────────────────────
    # DOMAIN 2: BOOLEAN MASTERY (250 examples)
    # ─────────────────────────────────────────────────────────────────────

    def generate_boolean_mastery_examples(self) -> list[TrainingExample]:
        """Boolean Mastery: Search query optimization across platforms"""
        examples = []

        # LinkedIn Queries (70 examples)
        for _ in range(70):
            examples.append(
                TrainingExample(
                    instruction="Create an optimized LinkedIn search query for this role",
                    input=random.choice(
                        [
                            "Role: Senior Backend Engineer\nSkills: Python, AWS, System Design\nExperience: 5+ years",
                            "Role: Data Engineer\nSkills: SQL, Spark, Cloud platforms\nExperience: 4+ years",
                            "Role: ML Engineer\nSkills: PyTorch, TensorFlow, Python\nExperience: 3+ years",
                        ]
                    ),
                    response=self._generate_linkedin_query(),
                    domain="search",
                    agent="boolean-mastery",
                    category="linkedin-queries",
                    difficulty=random.choice(["beginner", "intermediate"]),
                    context={
                        "scenario": "Generating targeted LinkedIn recruiter search",
                        "constraints": [
                            "Use boolean operators",
                            "Include AND/OR/NOT",
                            "Realistic search",
                        ],
                        "expected_behavior": "Valid LinkedIn query returning high-intent candidates",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # GitHub Searches (70 examples)
        for _ in range(70):
            examples.append(
                TrainingExample(
                    instruction="Create a GitHub search to find developers with specific expertise",
                    input=random.choice(
                        [
                            "Need: Kubernetes contributors with Go experience\nMinimum stars: 100+",
                            "Need: FastAPI developers with recent activity\nMinimum repos: 5",
                            "Need: React maintainers with TypeScript expertise\nMinimum followers: 50",
                        ]
                    ),
                    response=self._generate_github_query(),
                    domain="search",
                    agent="boolean-mastery",
                    category="github-patterns",
                    difficulty=random.choice(["intermediate", "advanced"]),
                    context={
                        "scenario": "Finding talent via GitHub repositories",
                        "constraints": [
                            "GitHub search syntax",
                            "Activity signals",
                            "Contribution quality",
                        ],
                        "expected_behavior": "Valid GitHub search identifying active contributors",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Stack Overflow Searches (70 examples)
        for _ in range(70):
            examples.append(
                TrainingExample(
                    instruction="Describe how to find domain experts on Stack Overflow",
                    input=random.choice(
                        [
                            "Domain: Kubernetes and container orchestration",
                            "Domain: Machine learning and AI",
                            "Domain: Distributed systems and databases",
                        ]
                    ),
                    response=self._stackoverflow_strategy(),
                    domain="search",
                    agent="boolean-mastery",
                    category="stackoverflow-expertise",
                    difficulty="intermediate",
                    context={
                        "scenario": "Using Stack Overflow reputation to identify experts",
                        "constraints": [
                            "Reputation signals",
                            "Answer quality",
                            "Expertise verification",
                        ],
                        "expected_behavior": "Strategy to identify high-signal experts",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Query Optimization (20 examples)
        for _ in range(20):
            examples.append(
                TrainingExample(
                    instruction="Refine this search query to improve result quality",
                    input=random.choice(
                        [
                            "Query: python developer\nResults: 50,000 candidates (too many)\nTarget: Senior backend engineers",
                            "Query: data engineer\nResults: Including data analysts (wrong role)\nNeed: SQL + Spark expertise",
                            "Query: javascript developer\nResults: All experience levels mixed\nTarget: 5+ years only",
                        ]
                    ),
                    response=self._refine_query(),
                    domain="search",
                    agent="boolean-mastery",
                    category="query-refinement",
                    difficulty="advanced",
                    context={
                        "scenario": "Iterating on search queries for precision",
                        "constraints": ["Reduce noise", "Increase relevance", "Maintain reach"],
                        "expected_behavior": "Refined query with better signal-to-noise ratio",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        return examples

    # ─────────────────────────────────────────────────────────────────────
    # DOMAIN 3: ENGAGEMENT AGENT (300 examples)
    # ─────────────────────────────────────────────────────────────────────

    def generate_engagement_examples(self) -> list[TrainingExample]:
        """Personalized Engagement: Multi-channel recruitment messaging"""
        examples = []

        # Email personalization (80 examples)
        for _ in range(80):
            examples.append(
                TrainingExample(
                    instruction="Write a personalized outreach email to a prospect",
                    input=self._generate_candidate_profile(),
                    response=self._generate_email(),
                    domain="engagement",
                    agent="personalized-engagement",
                    category="email-personalization",
                    difficulty=random.choice(["beginner", "intermediate"]),
                    context={
                        "scenario": "Cold outreach email to passive candidate",
                        "constraints": ["Personalized", "Value proposition", "Clear CTA"],
                        "expected_behavior": "Compelling email that increases open rate",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # LinkedIn messaging (80 examples)
        for _ in range(80):
            examples.append(
                TrainingExample(
                    instruction="Compose a LinkedIn message to a passive candidate",
                    input=self._generate_candidate_profile(),
                    response=self._generate_linkedin_message(),
                    domain="engagement",
                    agent="personalized-engagement",
                    category="linkedin-messaging",
                    difficulty=random.choice(["beginner", "intermediate"]),
                    context={
                        "scenario": "LinkedIn outreach to passive candidate",
                        "constraints": [
                            "Character limit awareness",
                            "Professional tone",
                            "Personalized",
                        ],
                        "expected_behavior": "High-engagement message with conversation starter",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # WhatsApp sequences (60 examples)
        for _ in range(60):
            examples.append(
                TrainingExample(
                    instruction="Create a 3-message WhatsApp outreach sequence",
                    input=f"Candidate: {random.choice(['Software Engineer', 'Product Manager', 'Data Scientist'])}\nRole: {random.choice(['Senior Engineer', 'Tech Lead', 'Architect'])}\nCompany: High-growth startup",
                    response=self._generate_whatsapp_sequence(),
                    domain="engagement",
                    agent="personalized-engagement",
                    category="whatsapp-sequences",
                    difficulty="intermediate",
                    context={
                        "scenario": "Multi-message WhatsApp engagement sequence",
                        "constraints": [
                            "Casual but professional",
                            "Progressive value",
                            "CTA in final message",
                        ],
                        "expected_behavior": "3-step sequence with escalating engagement",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Multi-touch campaigns (40 examples)
        for _ in range(40):
            examples.append(
                TrainingExample(
                    instruction="Design a 5-touch multi-channel engagement campaign",
                    input="Target: Senior backend engineer\nTimeline: 3 weeks\nChannels: Email, LinkedIn, Referral, Direct, Industry event",
                    response=self._multi_touch_campaign(),
                    domain="engagement",
                    agent="personalized-engagement",
                    category="multi-touch-campaigns",
                    difficulty="advanced",
                    context={
                        "scenario": "Coordinated multi-channel outreach sequence",
                        "constraints": ["Avoid spam", "Escalate gradually", "Track engagement"],
                        "expected_behavior": "Structured campaign with touch points and timing",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Objection handling (40 examples)
        for _ in range(40):
            examples.append(
                TrainingExample(
                    instruction="Respond to this candidate objection professionally",
                    input=random.choice(
                        [
                            "Candidate: 'I'm not looking to change jobs right now'",
                            "Candidate: 'Your company doesn't have the brand recognition I'm looking for'",
                            "Candidate: 'I don't have the specific experience you're looking for'",
                            "Candidate: 'The salary is below my current package'",
                        ]
                    ),
                    response=self._handle_objection(),
                    domain="engagement",
                    agent="personalized-engagement",
                    category="objection-handling",
                    difficulty="advanced",
                    context={
                        "scenario": "Addressing candidate concerns in recruitment",
                        "constraints": ["Respectful", "Data-driven", "Open-ended"],
                        "expected_behavior": "Response that addresses concern and keeps door open",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        return examples

    # ─────────────────────────────────────────────────────────────────────
    # DOMAIN 4: TALENT DISCOVERY (200 examples)
    # ─────────────────────────────────────────────────────────────────────

    def generate_discovery_examples(self) -> list[TrainingExample]:
        """Talent Discovery: Profile evaluation and deduplication"""
        examples = []

        # Profile analysis (60 examples)
        for _ in range(60):
            examples.append(
                TrainingExample(
                    instruction="What profile signals indicate a strong candidate for this role?",
                    input=random.choice(
                        [
                            "Role: Senior Backend Engineer (Python, AWS, System Design)",
                            "Role: Machine Learning Engineer (PyTorch, Research papers)",
                            "Role: DevOps Engineer (Kubernetes, Infrastructure-as-code)",
                        ]
                    ),
                    response=self._profile_signals(),
                    domain="discovery",
                    agent="proactive-scanning",
                    category="profile-analysis",
                    difficulty="intermediate",
                    context={
                        "scenario": "Evaluating LinkedIn/GitHub profiles for role fit",
                        "constraints": [
                            "Observable signals",
                            "Role-specific",
                            "Quality indicators",
                        ],
                        "expected_behavior": "Checklist of signals indicating strong candidate",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Repository assessment (50 examples)
        for _ in range(50):
            examples.append(
                TrainingExample(
                    instruction="How would you evaluate a developer's GitHub repositories?",
                    input="Candidate: Software engineer with 15 repos\nTarget role: Backend engineer (Go, Kubernetes)",
                    response=self._repo_assessment_criteria(),
                    domain="discovery",
                    agent="proactive-scanning",
                    category="repository-assessment",
                    difficulty="intermediate",
                    context={
                        "scenario": "Evaluating GitHub portfolio for talent quality",
                        "constraints": [
                            "Code quality signals",
                            "Contribution frequency",
                            "Skill relevance",
                        ],
                        "expected_behavior": "Evaluation framework for GitHub contributions",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Expertise matching (40 examples)
        for _ in range(40):
            examples.append(
                TrainingExample(
                    instruction="Identify Stack Overflow expertise from profile data",
                    input="Candidate: Stack Overflow with 15,000 reputation, top tags: Python, Django, PostgreSQL",
                    response=self._expertise_matching(),
                    domain="discovery",
                    agent="proactive-scanning",
                    category="expertise-matching",
                    difficulty="beginner",
                    context={
                        "scenario": "Matching Stack Overflow expertise to role requirements",
                        "constraints": ["Tag-based", "Reputation levels", "Recency"],
                        "expected_behavior": "Signal extraction from Stack Overflow profile",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Deduplication logic (30 examples)
        for _ in range(30):
            examples.append(
                TrainingExample(
                    instruction="Determine if these are the same person across platforms",
                    input=random.choice(
                        [
                            "LinkedIn: John Smith, Python developer at Google, San Francisco\nGitHub: jsmith42, maintainer of kubernetes-plugin\nStackOverflow: johnsmith_dev, 10k reputation",
                            "LinkedIn: Sarah Johnson, ML Engineer at Meta, New York\nGitHub: sarahj_ml, 200+ stars on ML repos\nStackOverflow: sarahj_ai, PyTorch expert",
                        ]
                    ),
                    response=self._dedup_logic(),
                    domain="discovery",
                    agent="proactive-scanning",
                    category="deduplication",
                    difficulty="intermediate",
                    context={
                        "scenario": "Cross-platform candidate deduplication",
                        "constraints": [
                            "Match confidence threshold",
                            "Consider variations",
                            "False positive cost",
                        ],
                        "expected_behavior": "Deduplication score with reasoning",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Data extraction (20 examples)
        for _ in range(20):
            examples.append(
                TrainingExample(
                    instruction="Extract structured data from this candidate profile",
                    input="LinkedIn summary: 5 years software engineer at Google, Python expert, led team of 5, passionate about ML",
                    response=self._data_extraction(),
                    domain="discovery",
                    agent="proactive-scanning",
                    category="data-extraction",
                    difficulty="beginner",
                    context={
                        "scenario": "Parsing profile information into structured format",
                        "constraints": [
                            "Parse accurately",
                            "Handle missing data",
                            "Standardized format",
                        ],
                        "expected_behavior": "Structured candidate data from free-text profile",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        return examples

    # ─────────────────────────────────────────────────────────────────────
    # DOMAIN 5: QUALITY ASSESSMENT (300 examples)
    # ─────────────────────────────────────────────────────────────────────

    def generate_quality_assessment_examples(self) -> list[TrainingExample]:
        """Quality Assessment: Candidate evaluation and hiring decisions"""
        examples = []

        # Skill matching (80 examples)
        for _ in range(80):
            examples.append(
                TrainingExample(
                    instruction="Score this candidate's skill match to the role",
                    input=self._generate_skill_match_scenario(),
                    response=self._generate_skill_match_score(),
                    domain="quality",
                    agent="quality-focused",
                    category="skill-matching",
                    difficulty=random.choice(["beginner", "intermediate"]),
                    context={
                        "scenario": "Evaluating candidate technical skills vs. job requirements",
                        "constraints": [
                            "Specific scoring",
                            "Gap identification",
                            "Trainability assessment",
                        ],
                        "expected_behavior": "Skill match percentage with gap analysis",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Experience validation (70 examples)
        for _ in range(70):
            examples.append(
                TrainingExample(
                    instruction="Assess this candidate's experience level for the role",
                    input=self._generate_experience_scenario(),
                    response=self._generate_experience_assessment(),
                    domain="quality",
                    agent="quality-focused",
                    category="experience-validation",
                    difficulty="intermediate",
                    context={
                        "scenario": "Evaluating depth and breadth of experience",
                        "constraints": [
                            "Years != competence",
                            "Relevant experience",
                            "Growth potential",
                        ],
                        "expected_behavior": "Experience assessment with competency levels",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Red flag detection (60 examples)
        for _ in range(60):
            examples.append(
                TrainingExample(
                    instruction="Identify potential red flags in this candidate profile",
                    input=self._generate_candidate_scenario(),
                    response=self._generate_red_flags(),
                    domain="quality",
                    agent="quality-focused",
                    category="red-flag-detection",
                    difficulty="intermediate",
                    context={
                        "scenario": "Screening for warning signs in candidate history",
                        "constraints": ["Objective signals", "Job-hopping patterns", "Skill gaps"],
                        "expected_behavior": "List of flags with confidence levels",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Cultural fit evaluation (50 examples)
        for _ in range(50):
            examples.append(
                TrainingExample(
                    instruction="Assess cultural fit for this candidate",
                    input=self._generate_cultural_scenario(),
                    response=self._generate_culture_fit(),
                    domain="quality",
                    agent="quality-focused",
                    category="cultural-fit",
                    difficulty="intermediate",
                    context={
                        "scenario": "Evaluating alignment with company values and team",
                        "constraints": [
                            "Predictive signals",
                            "Team compatibility",
                            "Growth mindset",
                        ],
                        "expected_behavior": "Culture fit assessment with recommendations",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Hiring decisions (40 examples)
        for _ in range(40):
            examples.append(
                TrainingExample(
                    instruction="Make a hiring recommendation based on interview performance",
                    input=self._generate_interview_performance(),
                    response=self._generate_hiring_recommendation(),
                    domain="quality",
                    agent="quality-focused",
                    category="hiring-decisions",
                    difficulty="advanced",
                    context={
                        "scenario": "Synthesizing multiple evaluation signals into decision",
                        "constraints": ["Data-driven", "Multi-signal", "Bias awareness"],
                        "expected_behavior": "Clear recommendation (Hire/Conditional/Pass) with reasoning",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        return examples

    # ─────────────────────────────────────────────────────────────────────
    # DOMAIN 6: MARKET INTELLIGENCE (200 examples)
    # ─────────────────────────────────────────────────────────────────────

    def generate_market_examples(self) -> list[TrainingExample]:
        """Market Intelligence: Salary analysis, skill trends, competitive data"""
        examples = []

        # Salary benchmarking (60 examples)
        for _ in range(60):
            examples.append(
                TrainingExample(
                    instruction="Determine competitive salary range for this role",
                    input=self._generate_salary_scenario(),
                    response=self._generate_salary_range(),
                    domain="market",
                    agent="market-intelligence",
                    category="salary-benchmarking",
                    difficulty="intermediate",
                    context={
                        "scenario": "Researching market compensation data",
                        "constraints": ["Location-aware", "Experience-adjusted", "Current market"],
                        "expected_behavior": "Salary range with market context",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Trend analysis (50 examples)
        for _ in range(50):
            examples.append(
                TrainingExample(
                    instruction="What are the trending skills in this domain?",
                    input=random.choice(
                        [
                            "Domain: Data Engineering (2024-2025)",
                            "Domain: Machine Learning Engineering (2024-2025)",
                            "Domain: Backend Development (2024-2025)",
                        ]
                    ),
                    response=self._generate_skill_trends(),
                    domain="market",
                    agent="market-intelligence",
                    category="trend-analysis",
                    difficulty="intermediate",
                    context={
                        "scenario": "Identifying emerging and declining skills",
                        "constraints": ["Current data", "Market momentum", "Hiring demand"],
                        "expected_behavior": "Trending skills with growth indicators",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Competitive positioning (50 examples)
        for _ in range(50):
            examples.append(
                TrainingExample(
                    instruction="How does our offer compare to market competitors?",
                    input=self._generate_competitive_scenario(),
                    response=self._generate_competitive_analysis(),
                    domain="market",
                    agent="market-intelligence",
                    category="competitive-positioning",
                    difficulty="advanced",
                    context={
                        "scenario": "Positioning company offer vs. competitors",
                        "constraints": [
                            "Realistic comparison",
                            "Compensation",
                            "Benefits",
                            "Growth",
                        ],
                        "expected_behavior": "Competitive positioning strategy with recommendations",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Offer recommendations (40 examples)
        for _ in range(40):
            examples.append(
                TrainingExample(
                    instruction="Recommend an offer package for this candidate",
                    input=self._generate_offer_scenario(),
                    response=self._generate_offer_recommendation(),
                    domain="market",
                    agent="market-intelligence",
                    category="offer-recommendations",
                    difficulty="advanced",
                    context={
                        "scenario": "Designing competitive offer package",
                        "constraints": ["Market-competitive", "Within budget", "Attractive"],
                        "expected_behavior": "Detailed offer recommendation with rationale",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        return examples

    # ─────────────────────────────────────────────────────────────────────
    # DOMAIN 7: TOOL INTEGRATION (200 examples)
    # ─────────────────────────────────────────────────────────────────────

    def generate_tool_examples(self) -> list[TrainingExample]:
        """Tool Integration: ATS/CRM workflows, system synchronization"""
        examples = []

        # ATS workflows (70 examples)
        for _ in range(70):
            examples.append(
                TrainingExample(
                    instruction="Describe the workflow to sync a candidate into ATS",
                    input="Candidate: Backend engineer from GitHub\nATS: Workday\nTarget: Rank in pipeline for Backend role",
                    response=self._generate_ats_workflow(),
                    domain="integration",
                    agent="tool-leverage",
                    category="ats-workflows",
                    difficulty="intermediate",
                    context={
                        "scenario": "Integrating discovered talent into ATS system",
                        "constraints": ["Data mapping", "Deduplication", "Status tracking"],
                        "expected_behavior": "Step-by-step integration process",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # CRM integration (50 examples)
        for _ in range(50):
            examples.append(
                TrainingExample(
                    instruction="How would you sync candidate engagement data to CRM?",
                    input="CRM: Salesforce\nData to sync: Outreach attempts, responses, interaction history\nSync frequency: Real-time",
                    response=self._generate_crm_integration(),
                    domain="integration",
                    agent="tool-leverage",
                    category="crm-integration",
                    difficulty="intermediate",
                    context={
                        "scenario": "Maintaining candidate engagement records in CRM",
                        "constraints": [
                            "Real-time sync",
                            "Data consistency",
                            "History preservation",
                        ],
                        "expected_behavior": "CRM integration workflow with field mapping",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Contact enrichment (40 examples)
        for _ in range(40):
            examples.append(
                TrainingExample(
                    instruction="What enrichment data should we add to candidate profiles?",
                    input="Candidate: Found on GitHub, minimal contact info\nEnrichment providers available: Clearbit, Apollo, Hunter",
                    response=self._generate_enrichment_strategy(),
                    domain="integration",
                    agent="tool-leverage",
                    category="contact-enrichment",
                    difficulty="beginner",
                    context={
                        "scenario": "Enriching candidate data from multiple sources",
                        "constraints": ["Data privacy", "Cost efficiency", "Accuracy"],
                        "expected_behavior": "Enrichment strategy with data sources",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Pipeline automation (40 examples)
        for _ in range(40):
            examples.append(
                TrainingExample(
                    instruction="Design workflow automation triggers for this scenario",
                    input="Trigger: Candidate completes interview\nAction needed: Update ATS, send email, log in CRM\nCondition: Score > 70%",
                    response=self._generate_automation_triggers(),
                    domain="integration",
                    agent="tool-leverage",
                    category="pipeline-automation",
                    difficulty="advanced",
                    context={
                        "scenario": "Automating repetitive pipeline tasks with triggers",
                        "constraints": ["Reliable triggers", "Error handling", "Audit trail"],
                        "expected_behavior": "Automation workflow with conditions and actions",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        return examples

    # ─────────────────────────────────────────────────────────────────────
    # DOMAIN 8: INTERVIEW & CONVERSATION (400 examples)
    # ─────────────────────────────────────────────────────────────────────

    def generate_interview_examples(self) -> list[TrainingExample]:
        """Interview & Conversation: Enhanced from existing Vetta dataset"""
        examples = []

        # Contextual question generation (100 examples)
        for _ in range(100):
            examples.append(
                TrainingExample(
                    instruction="Generate interview questions for this candidate/role",
                    input=self._generate_interview_scenario(),
                    response=self._generate_interview_questions(),
                    domain="interview",
                    agent="vetta-ai",
                    category="contextual-questions",
                    difficulty=random.choice(["intermediate", "advanced"]),
                    context={
                        "scenario": "Tailored interview questions based on background",
                        "constraints": [
                            "Role-specific",
                            "Background-aware",
                            "Behavioral + Technical",
                        ],
                        "expected_behavior": "Contextual questions that probe depth and fit",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Follow-up questions (80 examples)
        for _ in range(80):
            examples.append(
                TrainingExample(
                    instruction="Generate follow-up questions based on candidate answer",
                    input=self._generate_followup_scenario(),
                    response=self._generate_followup_questions(),
                    domain="interview",
                    agent="vetta-ai",
                    category="follow-up-questions",
                    difficulty="advanced",
                    context={
                        "scenario": "Adaptive interview with follow-ups based on responses",
                        "constraints": ["Probe depth", "Clarify gaps", "Assess reasoning"],
                        "expected_behavior": "Natural follow-up that deepens understanding",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Response analysis (80 examples)
        for _ in range(80):
            examples.append(
                TrainingExample(
                    instruction="Analyze this interview response and score it",
                    input=self._generate_response_analysis(),
                    response=self._generate_response_score(),
                    domain="interview",
                    agent="vetta-ai",
                    category="response-analysis",
                    difficulty="intermediate",
                    context={
                        "scenario": "Evaluating interview responses for quality",
                        "constraints": ["Fair scoring", "Evidence-based", "Comparative"],
                        "expected_behavior": "Response score with feedback",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Feedback generation (60 examples)
        for _ in range(60):
            examples.append(
                TrainingExample(
                    instruction="Generate interview feedback for this candidate",
                    input=self._generate_feedback_scenario(),
                    response=self._generate_feedback(),
                    domain="interview",
                    agent="vetta-ai",
                    category="feedback-generation",
                    difficulty="intermediate",
                    context={
                        "scenario": "Creating constructive interview feedback",
                        "constraints": ["Specific observations", "Actionable", "Professional"],
                        "expected_behavior": "Balanced feedback with strengths and growth areas",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        # Conversation orchestration (80 examples)
        for _ in range(80):
            examples.append(
                TrainingExample(
                    instruction="Orchestrate next steps in the interview process",
                    input=self._generate_orchestration_scenario(),
                    response=self._generate_orchestration_decision(),
                    domain="interview",
                    agent="conversation-service",
                    category="conversation-orchestration",
                    difficulty="advanced",
                    context={
                        "scenario": "Coordinating multi-phase interview process",
                        "constraints": [
                            "Candidate progression",
                            "Time efficiency",
                            "Decision quality",
                        ],
                        "expected_behavior": "Clear next step with reasoning",
                    },
                    metadata=self._create_metadata("synthetic"),
                )
            )

        return examples

    # ─────────────────────────────────────────────────────────────────────
    # HELPER METHODS FOR RESPONSE GENERATION
    # ─────────────────────────────────────────────────────────────────────

    def _generate_sourcing_strategy(
        self, job_title: str, headcount: int, timeline: str, urgency: str
    ) -> str:
        """Generate sourcing strategy response"""
        strategies = [
            f"1. Activate Boolean Mastery for database searches (Day 1-2). 2. Parallel outreach via LinkedIn recruiter (Day 2-5). 3. Engage external agency for extended reach (Day 3). 4. Internal referral program activation ($X per hire). Timeline: {timeline}, Headcount: {headcount}. Expected pipeline: 3:1 ratio.",
            f"Strategy for {headcount} {job_title}(s) in {timeline}: Phase 1 (Week 1): Database search + passive outreach. Phase 2 (Week 2): Agency coordination + industry events. Phase 3 (Week 3): Final interviews + offer. Urgency: {urgency}",
        ]
        return random.choice(strategies)

    def _rank_channels(self, channels: list, role: str) -> str:
        """Rank sourcing channels"""
        return f"For {role}: 1. LinkedIn (highest quality, targeted), 2. GitHub (strong for technical), 3. Recruitment agencies (speed), 4. Referrals (conversion). Expected yield: 15-20 qualified leads"

    def _generate_workflow_sequence(self) -> str:
        """Generate workflow orchestration"""
        return "Ideal sequence: Scout initiates → Boolean generates queries (parallel) → Scanning discovers candidates (parallel) → Engagement contacts → Assessment interviews → Quality scores → Tool sync to ATS. Parallel execution reduces time from 4 weeks to 2 weeks."

    def _vendor_coordination_strategy(self) -> str:
        """Vendor coordination approach"""
        return "1. Set KPI agreement: quality standard (80%+ fit), time-to-fill, cost/placement. 2. Weekly sync calls for pipeline status. 3. Exclusive vs. non-exclusive roles by skill. 4. Feedback loop on candidate quality. 5. Trial period with pilot role. Expected: 60% of placements from agency in 90 days."

    def _pipeline_metrics(self) -> str:
        """Pipeline health metrics"""
        return "Key metrics: 1. Pipeline coverage (candidates in pipeline / open roles): Target 5:1. 2. Conversion rate (offers / pipeline): Target 20%. 3. Time-to-fill (days to hire): Target 15-21 days. 4. Cost per hire: Track vs. budget. 5. Quality (retention at 6mo): Target 95%+"

    def _generate_linkedin_query(self) -> str:
        """Generate LinkedIn boolean query"""
        return '("Senior Backend Engineer" OR "Backend Software Engineer") AND (Python OR Go) AND (AWS OR GCP) AND ("system design" OR "distributed systems") AND (5 OR 6 OR 7 OR 8) AND NOT (junior OR intern OR bootcamp)'

    def _generate_github_query(self) -> str:
        """Generate GitHub search"""
        return (
            "language:go stars:>100 topic:kubernetes topic:cloud-native created:>2022 followers:>50"
        )

    def _stackoverflow_strategy(self) -> str:
        """Stack Overflow expert strategy"""
        return "Look for: 10k+ reputation in domain tags, recent activity (last 3 months), high answer score, badges (gold/silver), consistent contributions. Cross-verify on LinkedIn/GitHub for employment context. Reach out with specific praise for answer quality."

    def _refine_query(self) -> str:
        """Refine search query"""
        return '("senior backend engineer" OR "lead backend engineer") AND (python OR golang) AND NOT (junior OR graduate OR 0-2 years) AND (5+ OR 6+ OR 7+) AND (AWS OR distributed) NOT (data engineer OR frontend)'

    def _generate_email(self) -> str:
        """Generate personalized email"""
        return "Hi [Name],\n\nI noticed your impressive work on [project] and your expertise in [skill]. We're building [mission] at [company], and your background aligns perfectly.\n\nWould you be open to a 15-minute conversation about the role? [Link to calendar]\n\nLooking forward to connecting.\n\nBest,\n[Your name]"

    def _generate_linkedin_message(self) -> str:
        """Generate LinkedIn message"""
        return "Hi [Name], Your [specific achievement] on [project] caught my attention—exactly what we need at [Company]. Open to a quick chat about an opportunity?"

    def _generate_whatsapp_sequence(self) -> str:
        """Generate WhatsApp sequence"""
        return 'Message 1: "Hi [Name], saw your GitHub work—impressive! We\'re hiring for [role] at [company]. Interested?"\nMessage 2 (Day 3): "[Name], adding you to our newsletter re: tech roles. Check out: [link]"\nMessage 3 (Day 7): "Last attempt :) Open role closes Friday. Your background fits: [brief reason]. Calendar: [link]"'

    def _multi_touch_campaign(self) -> str:
        """Generate multi-touch campaign"""
        return "Touch 1 (Day 1): Email with value prop. Touch 2 (Day 3): LinkedIn message. Touch 3 (Day 5): Referral outreach. Touch 4 (Day 10): Direct call/message. Touch 5 (Day 14): Final email with urgency. Expected response rate: 5-8% across 5 touches."

    def _handle_objection(self) -> str:
        """Handle candidate objection"""
        return "Response: \"[Name], I understand—you're established at [company]. Here's what makes this different for you: [specific value]. Our growth rate means [opportunity]. Could we do 15 minutes to explore?\""

    def _profile_signals(self) -> str:
        """Profile quality signals"""
        return "Strong signals: 1. 5+ years backend experience, 2. Python/AWS in headline, 3. System design in projects, 4. Recent role at tier-1 company, 5. Open source contributions, 6. Active on GitHub/StackOverflow, 7. Certifications (AWS, Kubernetes), 8. Speaking/writing on technical topics"

    def _repo_assessment_criteria(self) -> str:
        """Repository assessment"""
        return "Evaluate: 1. Code quality (readability, testing, documentation), 2. Stars/forks (community interest), 3. Recency (active last 3 months), 4. Language match (Go, Kubernetes), 5. Contribution frequency, 6. Issue/PR response time, 7. Project scale (complexity), 8. Maintenance of dependencies"

    def _expertise_matching(self) -> str:
        """Stack Overflow expertise"""
        return "Expertise signal: Top tags (Python, Django, PostgreSQL) match 80% with role (90% match). 15k reputation = strong expertise level. Recent activity (answering in last 30 days) = current knowledge. Strong signal: Hire."

    def _dedup_logic(self) -> str:
        """Deduplication reasoning"""
        return "Confidence: 92% (same person). Evidence: Name match (high), geography match (Bay Area), employer overlap (Google), skills intersection (Python, AWS), activity timeframe consistent. Action: Merge profiles, use primary LinkedIn ID."

    def _data_extraction(self) -> str:
        """Extract structured data"""
        return "Extracted: Title=Software Engineer, Years=5, Company=Google, Skills=[Python, ML, Leadership], Team_Size=5, Location=Bay Area, Interest_Areas=[ML], Certifications=None"

    def _generate_skill_match_score(self) -> str:
        """Skill match scoring"""
        return "Skill Match: 85%. Required: Python (match: 95%), AWS (match: 80%), System Design (match: 75%). Gap: Kubernetes experience (0% → need 90%). Trainability: 9/10 (can learn Kubernetes in 2-4 weeks). Recommendation: STRONG FIT"

    def _generate_experience_assessment(self) -> str:
        """Experience assessment"""
        return "Experience Level: 80% (4 years vs 5+ required). Depth: Advanced in Python/backend. Breadth: Good across AWS services. Concern: Limited system design at scale (working at startups). Growth potential: 8/10. Recommendation: Hire with architect mentoring."

    def _generate_red_flags(self) -> str:
        """Red flags identification"""
        return "Flags: 1. Job-hopping (3 roles in 2 years) - Confidence: 70% concern. 2. Employment gap (6 months) - Confidence: low without context. 3. Skill degradation (moved away from engineering) - Confidence: medium. Overall risk: Medium. Action: Probe in interview about transitions."

    def _generate_culture_fit(self) -> str:
        """Culture fit assessment"""
        return "Culture Fit: 75% (good technical values, open source mindset, mentors juniors). Strength: Values learning/growth. Concern: Previous feedback on communication style (need clarity). Recommendation: Pair interview with culture lead. Overall: Acceptable with awareness."

    def _generate_hiring_recommendation(self) -> str:
        """Hiring recommendation"""
        return "Recommendation: HIRE. Rationale: Technical 8/10 (strong fundamentals, system design gaps can close), Communication 7/10 (good, but not exceptional), Culture 8/10 (values alignment), Growth potential 8/10. Risk mitigation: Assign architect mentor for first 3 months. Expected impact: High productivity in 4 weeks."

    def _generate_salary_range(self) -> str:
        """Salary benchmarking"""
        return "Role: Senior Backend Engineer, Location: San Francisco, Experience: 5 years. Market range: $150K-$180K base. Total comp (with equity): $200K-$280K. Market context: High demand, $180K base + equity will attract. Recommendation: $165K base + $60K equity ($150K over 4 years)."

    def _generate_skill_trends(self) -> str:
        """Skill trending analysis"""
        return "Trending Up: dbt, Snowflake, Spark, Arrow, Polars, data mesh. Emerging: Rust for data (performance). Stable: Python, SQL, Kubernetes. Declining: Hadoop, MapReduce. Highest premium: Data + ML Ops (15% salary boost). Hiring difficulty: High (shortage of experts)."

    def _generate_competitive_analysis(self) -> str:
        """Competitive positioning"""
        return "vs. Competitors: Google: $200K base + $400K equity (total: $700K). Facebook: $180K + $350K (total: $530K). Our offer: $165K base + $60K equity (total: $225K). Gap: Behind on total comp. Strength: Better growth trajectory, mission-driven, better work/life. Positioning: Growth focus, not pure comp."

    def _generate_offer_recommendation(self) -> str:
        """Offer package"""
        return "Offer package: Base $170K (market-competitive), Equity 75K shares over 4 years ($400K+ value), Bonus 15% ($25.5K), Healthcare (full coverage), 401k match 4%, Remote flexibility. Total: $230K+ first year. Competitiveness: Strong vs. startups, competitive with FAANG given other factors."

    def _generate_ats_workflow(self) -> str:
        """ATS integration workflow"""
        return 'Workflow: 1. Extract candidate data (name, email, skills, experience) 2. Map to Workday schema 3. Dedup check (existing profiles) 4. Create candidate record 5. Assign to Backend role requisition 6. Set source = "GitHub discovery" 7. Log all interactions (emails, etc) 8. Track through pipeline. Automation: Email trigger when moved to screening.'

    def _generate_crm_integration(self) -> str:
        """CRM workflow"""
        return "Workflow: 1. Outreach attempt logged in Salesforce (email sent) 2. Response received = activity update 3. Interview scheduled = opportunity created 4. Interview completed = notes + score synced 5. Offer sent = stage advancement 6. Accepted = customer record created. Automation: Real-time sync via API, history preserved for analytics."

    def _generate_enrichment_strategy(self) -> str:
        """Enrichment strategy"""
        return "Priority enrichment: 1. Email (Hunter/Clearbit) - highest value. 2. Phone normalization (PhoneValidator). 3. Company info (LinkedIn scrape). 4. Employment history validation (Background check). Cost: $2-5 per candidate. ROI: Reduces outreach bounce rate from 15% to 5%, saves time."

    def _generate_automation_triggers(self) -> str:
        """Automation triggers"""
        return 'Triggers: IF interview_score > 70% THEN [send thank you email, update ATS status to "Passed", create Salesforce task for offer discussion, notify hiring manager, log in CRM with score]. IF interview_score < 50% THEN [send rejection email, mark as "Not fit"]. Timing: Immediate (< 1 min latency).'

    def _generate_response_score(self) -> str:
        """Response scoring"""
        return "Score: 7/10. Strengths: Good architecture overview, identified key components. Gaps: Missed discussing failure recovery, latency optimization not addressed. Communication: Clear explanation, drew diagrams. Overall: Solid mid-level thinking, lacks depth for senior role. Recommendation: Probe further or pass."

    def _generate_feedback(self) -> str:
        """Interview feedback"""
        return "Feedback: [Candidate] demonstrated solid technical foundation in backend systems. Strengths: Clear communication, systematic approach to problem-solving. Areas for growth: Deeper consideration of failure scenarios, performance optimization under constraints. Overall: Good fit for mid-level, growth potential to senior in 1-2 years."

    def _generate_orchestration_decision(self) -> str:
        """Orchestration next steps"""
        return "Next step: Move to final round (2 technical interviewers + culture fit). Schedule within 3 days (show momentum). Provide offer decision within 24 hours of final round. Feedback: Candidate strong on fundamentals, discuss growth opportunities in offer conversation."

    # Additional helper methods

    def _generate_candidate_profile(self) -> str:
        """Generate random candidate profile"""
        roles = ["Backend Engineer", "Data Scientist", "Frontend Developer"]
        companies = ["Google", "Facebook", "Startups", "Consulting firms"]
        years = random.randint(3, 8)
        return f"Candidate: {random.choice(roles)} with {years} years at {random.choice(companies)}\nSkills: Python, AWS, Leadership"

    def _generate_skill_match_scenario(self) -> str:
        """Skill match scenario"""
        return "Candidate: 5 years Python experience, AWS, limited Kubernetes\nRole: Senior Backend Engineer (Python, AWS, Kubernetes required)\nExperience match: 5 years = exact fit"

    def _generate_experience_scenario(self) -> str:
        """Experience scenario"""
        return "Candidate: 4 years as mid-level backend engineer\nRole: Senior Engineer (5+ years required)\nBackground: Strong Python, limited system design, good communication"

    def _generate_candidate_scenario(self) -> str:
        """Candidate scenario for red flags"""
        return "Candidate profile: 3 roles in 2 years, 6-month employment gap, moved from engineering to management then back, weak recent references"

    def _generate_cultural_scenario(self) -> str:
        """Cultural scenario"""
        return "Candidate: Open source contributor, mentors junior developers, growth mindset\nCompany: Startup with high collaboration, learning-focused\nPrevious feedback: Communication style can be direct sometimes"

    def _generate_interview_performance(self) -> str:
        """Interview performance"""
        return "Technical interview: 7/10 (good fundamentals, missed edge cases)\nSystem design: 6/10 (solid but incomplete)\nCommunication: 8/10 (clear, asks questions)\nCultural: 7/10 (alignment on values, slight concern on collaboration)"

    def _generate_salary_scenario(self) -> str:
        """Salary scenario"""
        return "Role: Senior Backend Engineer\nLocation: San Francisco\nExperience: 5 years\nCurrent market: High demand, tight market"

    def _generate_competitive_scenario(self) -> str:
        """Competitive scenario"""
        return "Our offer: $160K base + $50K equity\nCompetitors: Google $200K, Facebook $180K, startup $120K\nCandidate value: Mission-driven, growth opportunity"

    def _generate_offer_scenario(self) -> str:
        """Offer scenario"""
        return "Candidate: 5yr senior engineer, currently $150K total\nBudget: $250K total comp ceiling\nGoal: Attract top talent, competitive offer"

    def _generate_feedback_scenario(self) -> str:
        """Feedback scenario"""
        return "Interview performance: Technical 7/10, Communication 8/10, Culture fit 6/10\nOverall impression: Capable but not exceptional, growth potential"

    def _generate_orchestration_scenario(self) -> str:
        """Orchestration scenario"""
        return "Candidate just completed first technical interview (score: 75%)\nPipeline: 3 more rounds planned\nTimeline: Need to hire in 2 weeks"

    def _generate_response_analysis(self) -> str:
        """Response analysis input"""
        return 'Q: Design a URL shortener service. A: "I\'d use a key-value store like Redis to map short codes to long URLs. For generation, use UUID + hash to collision-free codes. Store in database with TTL for expiration. Scale with caching layer."'

    def _generate_interview_scenario(self) -> str:
        """Generate interview scenario"""
        role = random.choice(["Backend Engineer", "Data Scientist", "Frontend Developer"])
        background = random.choice(
            ["5 years at Google", "3 years at startup", "4 years at Facebook"]
        )
        return f"Candidate: {role} with {background}\nRole: Senior {role}\nFocus areas: Technical depth and problem-solving"

    def _generate_interview_questions(self) -> str:
        """Generate interview questions"""
        return "Q1: Walk us through a complex system you designed. Q2: How would you handle scale? Q3: Tell us about a conflict with teammate. Q4: What questions for us?"

    def _generate_followup_scenario(self) -> str:
        """Generate follow-up scenario"""
        return 'Initial answer: "I used a load balancer to scale"\nContext: Interviewer wants more depth\nObjective: Probe understanding of failure modes'

    def _generate_followup_questions(self) -> str:
        """Generate follow-up questions"""
        return "Follow-up: What happens if the load balancer fails? How would you handle consistency? Walk through your specific monitoring approach."

    def _assess_difficulty(self, level: str = "intermediate") -> str:
        """Assess difficulty level"""
        return level if level in ["beginner", "intermediate", "advanced"] else "intermediate"

    def _create_metadata(self, source: str = "synthetic") -> dict:
        """Create metadata for example"""
        return {
            "created_date": datetime.now().isoformat(),
            "source": source,
            "quality_score": round(random.uniform(0.75, 1.0), 2),
            "reviewed": False,
        }

    # ─────────────────────────────────────────────────────────────────────
    # MAIN GENERATION & OUTPUT
    # ─────────────────────────────────────────────────────────────────────

    def generate_all(self) -> list[TrainingExample]:
        """Generate all training examples"""
        print("Generating LLM training dataset...")

        print("  Scout Coordinator (250 examples)...", end=" ")
        self.examples.extend(self.generate_scout_coordinator_examples())
        print("✓")

        print("  Boolean Mastery (250 examples)...", end=" ")
        self.examples.extend(self.generate_boolean_mastery_examples())
        print("✓")

        print("  Engagement Agent (300 examples)...", end=" ")
        self.examples.extend(self.generate_engagement_examples())
        print("✓")

        print("  Talent Discovery (200 examples)...", end=" ")
        self.examples.extend(self.generate_discovery_examples())
        print("✓")

        print("  Quality Assessment (300 examples)...", end=" ")
        self.examples.extend(self.generate_quality_assessment_examples())
        print("✓")

        print("  Market Intelligence (200 examples)...", end=" ")
        self.examples.extend(self.generate_market_examples())
        print("✓")

        print("  Tool Integration (200 examples)...", end=" ")
        self.examples.extend(self.generate_tool_examples())
        print("✓")

        print("  Interview & Conversation (400 examples)...", end=" ")
        self.examples.extend(self.generate_interview_examples())
        print("✓")

        return self.examples

    def save_to_file(self, filename: str = "llm_training_dataset.json") -> str:
        """Save examples to JSON file"""
        output_file = self.output_dir / filename
        data = [asdict(ex) for ex in self.examples]

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        return str(output_file)

    def generate_report(self) -> dict:
        """Generate dataset report"""
        report = {
            "total_examples": len(self.examples),
            "domains": {},
            "difficulty_distribution": {"beginner": 0, "intermediate": 0, "advanced": 0},
            "quality_metrics": {
                "average_quality_score": 0,
                "examples_above_08": 0,
                "reviewed_count": 0,
            },
        }

        # Domain breakdown
        for ex in self.examples:
            domain = ex.domain
            if domain not in report["domains"]:
                report["domains"][domain] = 0
            report["domains"][domain] += 1

            report["difficulty_distribution"][ex.difficulty] += 1

            if ex.metadata.get("quality_score", 0) >= 0.8:
                report["quality_metrics"]["examples_above_08"] += 1
            if ex.metadata.get("reviewed"):
                report["quality_metrics"]["reviewed_count"] += 1

        # Calculate averages
        avg_quality = sum(ex.metadata.get("quality_score", 0) for ex in self.examples) / len(
            self.examples
        )
        report["quality_metrics"]["average_quality_score"] = round(avg_quality, 2)

        return report

    def print_summary(self):
        """Print generation summary"""
        report = self.generate_report()

        print("\n" + "=" * 80)
        print("LLM TRAINING DATASET GENERATION COMPLETE")
        print("=" * 80)
        print(f"\n✅ Total Examples: {report['total_examples']}")
        print(f"✅ Average Quality Score: {report['quality_metrics']['average_quality_score']}")
        print(f"✅ Examples ≥0.8 quality: {report['quality_metrics']['examples_above_08']}")

        print("\n📊 Domain Breakdown:")
        for domain, count in sorted(report["domains"].items()):
            print(f"  • {domain:20} {count:4} examples")

        print("\n📈 Difficulty Distribution:")
        for difficulty, count in report["difficulty_distribution"].items():
            pct = (count / report["total_examples"]) * 100
            print(f"  • {difficulty:15} {count:4} examples ({pct:5.1f}%)")

        print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point"""
    generator = LLMTrainingDataGenerator()

    # Generate all examples
    generator.generate_all()

    # Save to file
    output_file = generator.save_to_file()
    print(f"\n✅ Saved to: {output_file}")

    # Print summary
    generator.print_summary()

    # Print first 3 examples for verification
    print("📝 Sample Examples:\n")
    for i, ex in enumerate(generator.examples[:3], 1):
        print(f"--- Example {i} ---")
        print(f"Domain: {ex.domain} | Agent: {ex.agent}")
        print(f"Instruction: {ex.instruction[:80]}...")
        print()


if __name__ == "__main__":
    main()
