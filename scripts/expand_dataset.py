#!/usr/bin/env python3
"""
Dataset Expansion Script for Vetta Interview Dataset

This script expands the enhanced Vetta dataset by generating new examples
using template-based generation and variation techniques.

Target: Expand from 160 → 500+ high-quality examples

Usage:
    python scripts/expand_dataset.py [--target 500] [--output notebooks/data/vetta_expanded_v2.json]
"""

import argparse
import json
import os
import random
from collections import Counter
from datetime import datetime
from typing import Any

# ============================================================================
# INTERVIEW TEMPLATES BY CATEGORY
# ============================================================================

OPENING_TEMPLATES = [
    {
        "instruction": "Start an interview for {role} with a candidate who has {experience} experience.",
        "response": "Hello! I'm Vetta, and I'll be conducting your interview today for the {role} position. Thank you for taking the time to speak with me. Before we dive into the technical aspects, I'd love to hear about your journey and what drew you to this opportunity.",
        "category": "opening",
        "difficulty": "beginner",
        "domain": "general",
    },
    {
        "instruction": "Begin a {interview_type} interview for {role}.",
        "response": "Welcome! I'm Vetta, your interviewer today. We'll be focusing on {interview_type} aspects of the {role} role. Let's start with a brief introduction - could you tell me about yourself and your relevant experience?",
        "category": "opening",
        "difficulty": "beginner",
        "domain": "general",
    },
    {
        "instruction": "Open an interview for a {level} {role} candidate.",
        "response": "Good to meet you! I'm Vetta, and I'll guide you through today's interview for our {level} {role} position. I've reviewed your background and I'm excited to learn more. What aspects of this role interest you most?",
        "category": "opening",
        "difficulty": "beginner",
        "domain": "general",
    },
    {
        "instruction": "Start a remote video interview for {role}.",
        "response": "Hello and welcome to your virtual interview! I'm Vetta, and I'll be your interviewer today for the {role} position. Can you hear and see me clearly? Great! Let's begin by having you share a bit about your background.",
        "category": "opening",
        "difficulty": "beginner",
        "domain": "general",
    },
    {
        "instruction": "Begin an interview for {role} with someone transitioning from {previous_field}.",
        "response": "Welcome! I'm Vetta. I noticed you're transitioning from {previous_field} to {role} - that's an exciting career move. I'd love to hear what inspired this transition and how your previous experience might bring unique value to this role.",
        "category": "opening",
        "difficulty": "intermediate",
        "domain": "general",
    },
]

BEHAVIORAL_TEMPLATES = [
    {
        "instruction": "Ask a behavioral question about {skill}.",
        "response": "I'd like to explore your experience with {skill}. Can you walk me through a specific situation where you had to demonstrate this? What was the context, your approach, and the outcome?",
        "category": "behavioral",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Ask about a time the candidate faced {challenge}.",
        "response": "Tell me about a time you faced {challenge}. How did you approach the situation? What steps did you take, and what did you learn from the experience?",
        "category": "behavioral",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Ask a STAR-format question about {scenario}.",
        "response": "I'd like to hear about {scenario}. Using the STAR format, could you describe the Situation you were in, the Task you needed to accomplish, the Actions you took, and the Results you achieved?",
        "category": "behavioral",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Ask about conflict resolution in a {context} environment.",
        "response": "In {context} environments, conflicts can arise. Tell me about a disagreement you had with a colleague or stakeholder. How did you handle it, and what was the resolution?",
        "category": "behavioral",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Ask about leadership experience in {situation}.",
        "response": "Leadership takes many forms. Describe a time in {situation} where you had to lead, whether formally or informally. How did you motivate others and drive results?",
        "category": "behavioral",
        "difficulty": "advanced",
        "domain": "general",
    },
]

TECHNICAL_TEMPLATES = [
    {
        "instruction": "Ask a {difficulty} technical question about {technology}.",
        "response": "Let's discuss {technology}. {question} Walk me through your thought process as you approach this.",
        "category": "technical_question",
        "difficulty": "{difficulty}",
        "domain": "{domain}",
    },
    {
        "instruction": "Ask about system design for {system}.",
        "response": "Let's work through a design problem. How would you design {system}? Consider scalability, reliability, and performance. What components would you include and why?",
        "category": "technical_question",
        "difficulty": "advanced",
        "domain": "system_design",
    },
    {
        "instruction": "Ask about debugging approach for {issue_type} issues.",
        "response": "Debugging is crucial for any developer. Walk me through how you would approach diagnosing and fixing {issue_type} issues. What tools and techniques would you use?",
        "category": "technical_question",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Ask about code review practices for {codebase_type}.",
        "response": "Code reviews are essential for quality. How do you approach reviewing code in {codebase_type}? What do you look for, and how do you provide constructive feedback?",
        "category": "technical_question",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Ask about testing strategy for {application_type}.",
        "response": "Testing is critical. For {application_type}, what testing strategies would you employ? How do you balance unit tests, integration tests, and end-to-end tests?",
        "category": "technical_question",
        "difficulty": "intermediate",
        "domain": "general",
    },
]

FEEDBACK_TEMPLATES = [
    {
        "instruction": "Provide positive feedback on the candidate's {strength}.",
        "response": "Excellent work on {strength}! Your approach demonstrates strong understanding and practical experience. I particularly appreciated how you {specific_observation}.",
        "category": "feedback",
        "difficulty": "beginner",
        "domain": "general",
    },
    {
        "instruction": "Give constructive feedback on {area} while being encouraging.",
        "response": "That's a good foundation in {area}. To strengthen your answer further, you might consider {suggestion}. Many candidates at this stage are still developing this skill, so don't be discouraged.",
        "category": "feedback",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Acknowledge a partial answer about {topic} and guide deeper.",
        "response": "You've touched on important aspects of {topic}. Let's explore this further - what about {follow_up_aspect}? This will help me understand the depth of your knowledge.",
        "category": "feedback",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Provide feedback after a {interview_type} question.",
        "response": "Thank you for that detailed response. Your experience with {interview_type} clearly shows. I'd like to build on that - {transition_to_next}.",
        "category": "feedback",
        "difficulty": "beginner",
        "domain": "general",
    },
]

CLOSING_TEMPLATES = [
    {
        "instruction": "Close the interview and explain next steps for {role}.",
        "response": "Thank you for your time today! I've enjoyed learning about your experience and how you'd approach the {role} position. Our team will review all candidates and you'll hear back within {timeframe}. Do you have any questions for me before we wrap up?",
        "category": "closing",
        "difficulty": "beginner",
        "domain": "general",
    },
    {
        "instruction": "End a positive interview for {role}.",
        "response": "This has been a great conversation! Your background in {skill_area} is impressive, and I think you'd be a strong fit for our team. We'll be in touch soon with next steps. Is there anything else you'd like to know about the role or our company?",
        "category": "closing",
        "difficulty": "beginner",
        "domain": "general",
    },
    {
        "instruction": "Conclude an interview where the candidate needs more experience.",
        "response": "Thank you for taking the time to interview with us. I appreciate your honesty about your experience level. While this particular role may require more {area} experience, I'd encourage you to keep developing those skills. We'll follow up with our decision soon.",
        "category": "closing",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Close the interview and ask for candidate questions.",
        "response": "We're coming to the end of our time together. Before we finish, I want to make sure you have a complete picture of the opportunity. What questions do you have about the role, team, or company?",
        "category": "closing",
        "difficulty": "beginner",
        "domain": "general",
    },
]

EDGE_CASE_TEMPLATES = [
    {
        "instruction": "Handle a candidate who {awkward_situation}.",
        "response": "I understand - {empathetic_response}. Let's {suggested_action}. The important thing is that we have a productive conversation and I get a fair assessment of your abilities.",
        "category": "edge_case",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Respond when a candidate asks about {sensitive_topic}.",
        "response": "That's a fair question about {sensitive_topic}. I want to be transparent with you - {honest_answer}. Do you have any other concerns I can address?",
        "category": "edge_case",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Handle technical difficulties during a {interview_format} interview.",
        "response": "It seems we're having some technical issues with {issue}. No worries - these things happen. Let's {solution}. If the issues persist, we can always reschedule.",
        "category": "edge_case",
        "difficulty": "beginner",
        "domain": "general",
    },
    {
        "instruction": "Respond when a candidate goes off-topic about {tangent}.",
        "response": "That's interesting context about {tangent}. I'd like to bring us back to the main topic though - {redirect}. This will help me better evaluate your fit for the role.",
        "category": "edge_case",
        "difficulty": "intermediate",
        "domain": "general",
    },
]

MULTI_TURN_TEMPLATES = [
    {
        "instruction": "Follow up on the candidate's mention of {topic} to explore deeper.",
        "response": "You mentioned {topic} earlier - that's interesting. Can you elaborate on {specific_aspect}? I'd like to understand how this experience shaped your approach.",
        "category": "multi_turn",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Connect the candidate's {previous_answer} to ask about {related_topic}.",
        "response": "Building on what you shared about {previous_answer}, how does that relate to {related_topic}? I'm curious about the connection you see between these areas.",
        "category": "multi_turn",
        "difficulty": "intermediate",
        "domain": "general",
    },
    {
        "instruction": "Probe deeper into {claim} the candidate made.",
        "response": "You mentioned {claim}. That's impressive - can you walk me through a specific example? What were the challenges you faced and how did you overcome them?",
        "category": "multi_turn",
        "difficulty": "intermediate",
        "domain": "general",
    },
]

# ============================================================================
# VARIABLE POOLS FOR TEMPLATE FILLING
# ============================================================================

ROLES = [
    "Software Engineer",
    "Senior Software Engineer",
    "Staff Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Data Engineer",
    "DevOps Engineer",
    "Site Reliability Engineer",
    "Platform Engineer",
    "Product Manager",
    "Technical Product Manager",
    "Engineering Manager",
    "QA Engineer",
    "Security Engineer",
    "Mobile Developer",
    "Cloud Architect",
    "Solutions Architect",
    "Technical Lead",
]

EXPERIENCE_LEVELS = [
    "1-2 years",
    "3-5 years",
    "5+ years",
    "7+ years",
    "10+ years",
    "entry-level",
    "mid-level",
    "senior",
    "principal",
    "staff",
]

LEVELS = ["Junior", "Mid-level", "Senior", "Staff", "Principal", "Lead"]

INTERVIEW_TYPES = [
    "technical",
    "behavioral",
    "system design",
    "coding",
    "culture fit",
    "leadership",
    "problem-solving",
]

SKILLS = [
    "problem-solving",
    "teamwork",
    "communication",
    "leadership",
    "time management",
    "adaptability",
    "conflict resolution",
    "decision-making",
    "project management",
    "mentoring",
    "technical writing",
    "stakeholder management",
    "prioritization",
]

CHALLENGES = [
    "a tight deadline with competing priorities",
    "a disagreement with a team member",
    "a project that wasn't going as planned",
    "learning a new technology quickly",
    "communicating technical concepts to non-technical stakeholders",
    "handling negative feedback on your work",
    "working with limited resources",
    "a critical production incident",
    "scope creep in a project",
    "onboarding to a complex legacy codebase",
]

TECHNOLOGIES = [
    "Python",
    "JavaScript",
    "TypeScript",
    "React",
    "Node.js",
    "Docker",
    "Kubernetes",
    "AWS",
    "PostgreSQL",
    "Redis",
    "GraphQL",
    "REST APIs",
    "microservices",
    "CI/CD pipelines",
    "machine learning models",
    "data pipelines",
    "distributed systems",
]

SYSTEMS = [
    "a real-time notification system",
    "a scalable e-commerce platform",
    "a social media feed",
    "a ride-sharing application",
    "a video streaming service",
    "a payment processing system",
    "a search engine",
    "a chat application",
    "an analytics dashboard",
    "a recommendation engine",
]

TECHNICAL_QUESTIONS = {
    "Python": [
        "How would you implement a decorator that caches function results?",
        "Explain the difference between `__new__` and `__init__`.",
        "How would you handle memory management in a long-running Python process?",
        "What are the tradeoffs between threads, multiprocessing, and asyncio?",
    ],
    "JavaScript": [
        "Explain the event loop and how it handles asynchronous operations.",
        "What are closures and how would you use them in practice?",
        "How does prototypal inheritance work?",
        "Explain the differences between var, let, and const.",
    ],
    "system_design": [
        "How would you handle millions of concurrent connections?",
        "What strategies would you use for database sharding?",
        "How would you design for fault tolerance and high availability?",
        "What caching strategies would you employ and why?",
    ],
    "general": [
        "How do you approach optimizing slow database queries?",
        "What factors do you consider when choosing between SQL and NoSQL?",
        "How would you design an API for external developers?",
        "What's your approach to handling technical debt?",
    ],
}

STRENGTHS = [
    "explaining complex technical concepts clearly",
    "providing concrete examples from your experience",
    "demonstrating strong problem-solving skills",
    "showing depth of knowledge in this area",
    "articulating your thought process well",
    "connecting different concepts together",
]

AREAS_FOR_IMPROVEMENT = [
    "system design fundamentals",
    "explaining technical tradeoffs",
    "providing specific metrics and outcomes",
    "considering edge cases in your solutions",
    "time and space complexity analysis",
]

AWKWARD_SITUATIONS = [
    "is very nervous and speaking quickly",
    "gives very short answers",
    "seems distracted or unfocused",
    "is being interviewed in a noisy environment",
    "appears to be reading from notes",
    "asks to take a break",
    "mentions they're interviewing with competitors",
]

SENSITIVE_TOPICS = [
    "salary expectations",
    "work-life balance",
    "remote work policy",
    "team dynamics",
    "company stability",
    "growth opportunities",
    "the previous person in this role",
    "recent layoffs",
]

TIMEFRAMES = [
    "1-2 business days",
    "3-5 business days",
    "one week",
    "7-10 business days",
    "the next two weeks",
]

PREVIOUS_FIELDS = [
    "finance",
    "healthcare",
    "education",
    "consulting",
    "academia",
    "startups",
    "enterprise",
    "government",
]


# ============================================================================
# GENERATION FUNCTIONS
# ============================================================================


def fill_template(template: dict[str, Any], variables: dict[str, str]) -> dict[str, Any]:
    """Fill a template with variable values."""
    filled = {}
    for key, value in template.items():
        if isinstance(value, str):
            try:
                filled[key] = value.format(**variables)
            except KeyError:
                filled[key] = value
        else:
            filled[key] = value
    return filled


def generate_opening_examples(count: int) -> list[dict[str, Any]]:
    """Generate opening interview examples."""
    examples = []
    for _ in range(count):
        template = random.choice(OPENING_TEMPLATES)
        variables = {
            "role": random.choice(ROLES),
            "experience": random.choice(EXPERIENCE_LEVELS),
            "interview_type": random.choice(INTERVIEW_TYPES),
            "level": random.choice(LEVELS),
            "previous_field": random.choice(PREVIOUS_FIELDS),
        }
        example = fill_template(template, variables)
        example["expected_length"] = "medium"
        example["has_context"] = False
        examples.append(example)
    return examples


def generate_behavioral_examples(count: int) -> list[dict[str, Any]]:
    """Generate behavioral interview examples."""
    examples = []
    contexts = ["team", "cross-functional", "remote", "high-pressure", "startup", "enterprise"]
    situations = [
        "a team project",
        "a critical deadline",
        "organizational change",
        "a product launch",
    ]

    for _ in range(count):
        template = random.choice(BEHAVIORAL_TEMPLATES)
        variables = {
            "skill": random.choice(SKILLS),
            "challenge": random.choice(CHALLENGES),
            "scenario": random.choice(
                [
                    "when you had to influence without authority",
                    "when you received critical feedback",
                    "when you had to make a difficult decision quickly",
                    "when you helped a struggling team member",
                    "when you had to push back on a stakeholder",
                ]
            ),
            "context": random.choice(contexts),
            "situation": random.choice(situations),
        }
        example = fill_template(template, variables)
        example["expected_length"] = "long"
        example["has_context"] = False
        examples.append(example)
    return examples


def generate_technical_examples(count: int) -> list[dict[str, Any]]:
    """Generate technical interview examples."""
    examples = []
    difficulties = ["beginner", "intermediate", "advanced"]
    issue_types = ["performance", "memory leak", "race condition", "networking", "database"]
    codebase_types = ["a large monolith", "microservices", "legacy code", "open source projects"]
    application_types = [
        "web applications",
        "APIs",
        "data pipelines",
        "mobile apps",
        "distributed systems",
    ]

    for _ in range(count):
        template = random.choice(TECHNICAL_TEMPLATES)
        tech = random.choice(list(TECHNICAL_QUESTIONS.keys()))
        question = random.choice(TECHNICAL_QUESTIONS[tech])
        difficulty = random.choice(difficulties)

        variables = {
            "difficulty": difficulty,
            "technology": random.choice(TECHNOLOGIES),
            "question": question,
            "domain": "system_design" if tech == "system_design" else "general",
            "system": random.choice(SYSTEMS),
            "issue_type": random.choice(issue_types),
            "codebase_type": random.choice(codebase_types),
            "application_type": random.choice(application_types),
        }
        example = fill_template(template, variables)
        if example.get("difficulty") == "{difficulty}":
            example["difficulty"] = difficulty
        if example.get("domain") == "{domain}":
            example["domain"] = variables["domain"]
        example["expected_length"] = "long"
        example["has_context"] = False
        examples.append(example)
    return examples


def generate_feedback_examples(count: int) -> list[dict[str, Any]]:
    """Generate feedback examples."""
    examples = []
    topics = TECHNOLOGIES + SKILLS
    follow_up_aspects = [
        "the scalability considerations",
        "how you'd handle edge cases",
        "the tradeoffs you considered",
        "how you'd improve it with more time",
    ]
    suggestions = [
        "considering the edge cases more explicitly",
        "quantifying the impact with specific metrics",
        "exploring alternative approaches",
        "thinking about the long-term maintainability",
    ]
    specific_observations = [
        "structured your explanation clearly",
        "provided concrete examples",
        "considered multiple perspectives",
        "demonstrated practical experience",
    ]

    for _ in range(count):
        template = random.choice(FEEDBACK_TEMPLATES)
        variables = {
            "strength": random.choice(STRENGTHS),
            "area": random.choice(AREAS_FOR_IMPROVEMENT),
            "topic": random.choice(topics),
            "follow_up_aspect": random.choice(follow_up_aspects),
            "suggestion": random.choice(suggestions),
            "specific_observation": random.choice(specific_observations),
            "interview_type": random.choice(INTERVIEW_TYPES),
            "transition_to_next": "can you tell me more about a related experience?",
        }
        example = fill_template(template, variables)
        example["expected_length"] = "medium"
        example["has_context"] = True
        examples.append(example)
    return examples


def generate_closing_examples(count: int) -> list[dict[str, Any]]:
    """Generate closing interview examples."""
    examples = []
    skill_areas = TECHNOLOGIES + ["leadership", "problem-solving", "communication"]
    areas_needed = ["technical depth", "system design", "leadership", "specific domain expertise"]

    for _ in range(count):
        template = random.choice(CLOSING_TEMPLATES)
        variables = {
            "role": random.choice(ROLES),
            "timeframe": random.choice(TIMEFRAMES),
            "skill_area": random.choice(skill_areas),
            "area": random.choice(areas_needed),
        }
        example = fill_template(template, variables)
        example["expected_length"] = "medium"
        example["has_context"] = False
        examples.append(example)
    return examples


def generate_edge_case_examples(count: int) -> list[dict[str, Any]]:
    """Generate edge case examples."""
    examples = []
    empathetic_responses = [
        "interviews can be stressful",
        "that's completely understandable",
        "no need to worry",
        "we can work around that",
    ]
    suggested_actions = [
        "take a moment to collect your thoughts",
        "move on and come back to this later",
        "try a different approach",
        "focus on what you do know",
    ]
    honest_answers = [
        "I can share what I know, though some details would come from HR",
        "our policy on that is flexible based on team needs",
        "I'd encourage you to discuss specifics with your recruiter",
    ]
    interview_formats = ["video", "phone", "virtual whiteboard"]
    technical_issues = ["audio", "video", "screen sharing", "connection"]
    solutions = [
        "try reconnecting",
        "switch to audio only",
        "use the chat instead",
        "take a brief pause",
    ]
    redirects = [
        "could you tell me more about your specific experience with this?",
        "let's discuss how you'd apply this in our context",
        "I'd like to understand your approach to the core problem",
    ]

    for _ in range(count):
        template = random.choice(EDGE_CASE_TEMPLATES)
        variables = {
            "awkward_situation": random.choice(AWKWARD_SITUATIONS),
            "empathetic_response": random.choice(empathetic_responses),
            "suggested_action": random.choice(suggested_actions),
            "sensitive_topic": random.choice(SENSITIVE_TOPICS),
            "honest_answer": random.choice(honest_answers),
            "interview_format": random.choice(interview_formats),
            "issue": random.choice(technical_issues),
            "solution": random.choice(solutions),
            "tangent": random.choice(["a previous project", "industry news", "personal interests"]),
            "redirect": random.choice(redirects),
        }
        example = fill_template(template, variables)
        example["expected_length"] = "medium"
        example["has_context"] = True
        examples.append(example)
    return examples


def generate_multi_turn_examples(count: int) -> list[dict[str, Any]]:
    """Generate multi-turn conversation examples."""
    examples = []
    topics = (
        TECHNOLOGIES
        + SKILLS
        + ["your previous role", "a challenging project", "team collaboration"]
    )
    specific_aspects = [
        "the technical decisions you made",
        "how you measured success",
        "what you'd do differently",
        "the team dynamics involved",
    ]
    related_topics = [
        "similar challenges in our context",
        "your approach to continuous learning",
        "how you'd apply this here",
        "scaling this approach",
    ]
    claims = [
        "leading that initiative",
        "improving performance by a significant margin",
        "building that system from scratch",
        "mentoring the team",
    ]

    for _ in range(count):
        template = random.choice(MULTI_TURN_TEMPLATES)
        variables = {
            "topic": random.choice(topics),
            "specific_aspect": random.choice(specific_aspects),
            "previous_answer": random.choice(topics),
            "related_topic": random.choice(related_topics),
            "claim": random.choice(claims),
        }
        example = fill_template(template, variables)
        example["expected_length"] = "medium"
        example["has_context"] = True
        examples.append(example)
    return examples


def add_metadata(examples: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    """Add metadata to generated examples."""
    for example in examples:
        example["_metadata"] = {
            "source": source,
            "generated_at": datetime.now().isoformat(),
            "quality_score": 1.0,
            "version": "2.0.0",
        }
    return examples


def deduplicate_by_instruction(examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove examples with duplicate instructions."""
    seen = set()
    unique = []
    for ex in examples:
        key = ex["instruction"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(ex)
    return unique


def load_existing_dataset(file_path: str) -> list[dict[str, Any]]:
    """Load existing dataset to avoid duplicates."""
    if not os.path.exists(file_path):
        return []

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    # Handle both formats (with or without wrapper)
    if isinstance(data, dict) and "examples" in data:
        return data["examples"]
    return data


def calculate_category_targets(existing: list[dict[str, Any]], total_target: int) -> dict[str, int]:
    """Calculate how many examples needed per category to reach target."""
    # Current distribution
    current_counts = Counter(ex.get("category", "unknown") for ex in existing)

    # Ideal distribution (percentages based on plan)
    ideal_distribution = {
        "opening": 0.10,
        "behavioral": 0.20,
        "technical_question": 0.25,
        "feedback": 0.15,
        "closing": 0.08,
        "edge_case": 0.10,
        "multi_turn": 0.12,
    }

    # Calculate targets
    targets = {}
    for category, percentage in ideal_distribution.items():
        ideal_count = int(total_target * percentage)
        current_count = current_counts.get(category, 0)
        needed = max(0, ideal_count - current_count)
        targets[category] = needed

    return targets


def generate_dataset(
    existing_path: str, output_path: str, target_total: int = 500
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Generate expanded dataset."""
    print(f"🚀 Starting dataset expansion to {target_total} examples")
    print("=" * 60)

    # Load existing data
    existing = load_existing_dataset(existing_path)
    print(f"📥 Loaded {len(existing)} existing examples")

    # Calculate what we need
    targets = calculate_category_targets(existing, target_total)
    print("\n📊 Generation targets by category:")
    for cat, count in targets.items():
        print(f"   {cat}: +{count} examples")

    # Generate new examples
    new_examples = []

    generators = {
        "opening": generate_opening_examples,
        "behavioral": generate_behavioral_examples,
        "technical_question": generate_technical_examples,
        "feedback": generate_feedback_examples,
        "closing": generate_closing_examples,
        "edge_case": generate_edge_case_examples,
        "multi_turn": generate_multi_turn_examples,
    }

    print("\n🔧 Generating new examples...")
    for category, count in targets.items():
        if count > 0 and category in generators:
            generated = generators[category](count)
            generated = add_metadata(generated, f"synthetic_expansion_v2_{category}")
            new_examples.extend(generated)
            print(f"   ✅ Generated {len(generated)} {category} examples")

    # Combine and deduplicate
    all_examples = existing + new_examples
    unique_examples = deduplicate_by_instruction(all_examples)

    print("\n📈 Results:")
    print(f"   Existing: {len(existing)}")
    print(f"   Generated: {len(new_examples)}")
    print(f"   After dedup: {len(unique_examples)}")

    # Final distribution
    final_counts = Counter(ex.get("category", "unknown") for ex in unique_examples)

    stats = {
        "total_examples": len(unique_examples),
        "original_count": len(existing),
        "generated_count": len(new_examples),
        "duplicates_removed": len(all_examples) - len(unique_examples),
        "category_distribution": dict(final_counts),
        "generated_at": datetime.now().isoformat(),
    }

    return unique_examples, stats


def save_dataset(examples: list[dict[str, Any]], stats: dict[str, Any], output_path: str):
    """Save the expanded dataset."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    output_data = {
        "_dataset_metadata": {
            "name": "vetta-interview-dataset-expanded",
            "version": "2.0.0",
            "created_at": datetime.now().isoformat(),
            "total_examples": len(examples),
            "generation_stats": stats,
        },
        "examples": examples,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved {len(examples)} examples to {output_path}")


def print_summary(stats: dict[str, Any]):
    """Print a summary of the generation."""
    print("\n" + "=" * 60)
    print("📊 DATASET EXPANSION SUMMARY")
    print("=" * 60)
    print(f"Total Examples: {stats['total_examples']}")
    print(f"Original: {stats['original_count']}")
    print(f"Generated: {stats['generated_count']}")
    print(f"Duplicates Removed: {stats['duplicates_removed']}")
    print("\nCategory Distribution:")
    for cat, count in sorted(stats["category_distribution"].items()):
        pct = (count / stats["total_examples"]) * 100
        bar = "█" * int(pct / 2)
        print(f"  {cat:20} {count:4} ({pct:5.1f}%) {bar}")


def main():
    parser = argparse.ArgumentParser(description="Expand Vetta interview dataset")
    parser.add_argument(
        "--target", type=int, default=500, help="Target total number of examples (default: 500)"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="notebooks/data/vetta_comprehensive_enhanced.json",
        help="Input dataset file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="notebooks/data/vetta_expanded_v2.json",
        help="Output dataset file",
    )

    args = parser.parse_args()

    # Generate expanded dataset
    examples, stats = generate_dataset(
        existing_path=args.input, output_path=args.output, target_total=args.target
    )

    # Save results
    save_dataset(examples, stats, args.output)

    # Print summary
    print_summary(stats)

    print("\n✅ Dataset expansion complete!")
    print(f"📁 Output: {args.output}")
    print("\n🔄 Next steps:")
    print("   1. Review generated examples for quality")
    print("   2. Run quality_enhance_dataset.py on the new file")
    print("   3. Upload to Hugging Face with upload_enhanced_dataset.py")


if __name__ == "__main__":
    main()
