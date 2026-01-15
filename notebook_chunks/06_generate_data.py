# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  ENHANCED VETTA DATASET GENERATOR - Copy this entire cell to Colab      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

"""
Enhanced Vetta Training Data Generator
=====================================

This module provides an improved dataset for fine-tuning Vetta, the AI interviewer.
Based on evaluation feedback, this version uses Hugging Face datasets for efficiency.

- Loads pre-existing datasets from user's Hugging Face account (asifdotpy)
- Falls back to databricks-dolly-15k if no user datasets found
- Filters and adapts data for interview scenarios
- Includes metadata and validation
- Train/validation split capability

Usage:
    python enhanced_vetta_data.py  # Generates and validates dataset
"""

import json
import os
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

from datasets import load_dataset


@dataclass
class ExampleMetadata:
    """Metadata for training examples."""

    category: (
        str  # opening, technical_question, feedback, behavioral, closing, edge_case, multi_turn
    )
    difficulty: str  # beginner, intermediate, advanced
    domain: str  # backend_python, frontend, ml_ai, system_design, behavioral, general
    expected_length: str  # short, medium, long
    has_context: bool = False  # Whether this is part of a multi-turn conversation


def validate_dataset(examples: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Validate dataset quality and provide statistics.

    Returns comprehensive validation report.
    """
    validation_report = {
        "total_examples": len(examples),
        "warnings": [],
        "errors": [],
        "statistics": {},
    }

    # Category distribution
    categories = Counter(ex.get("category", "unknown") for ex in examples)
    validation_report["statistics"]["categories"] = dict(categories)

    # Check category balance
    total = len(examples)
    max_category_pct = max(categories.values()) / total
    if max_category_pct > 0.4:
        validation_report["warnings"].append(
            f"Imbalanced categories - largest category represents {max_category_pct:.1%} of dataset"
        )

    # Response length analysis
    response_lengths = []
    for ex in examples:
        response = ex.get("response", "")
        word_count = len(response.split())
        response_lengths.append(word_count)

    if response_lengths:
        min_len, max_len = min(response_lengths), max(response_lengths)
        avg_len = sum(response_lengths) / len(response_lengths)
        validation_report["statistics"]["response_lengths"] = {
            "min": min_len,
            "max": max_len,
            "avg": round(avg_len, 1),
        }

        # Check for length variety
        if max_len - min_len < 50:
            validation_report["warnings"].append(
                "Limited response length variety - add more short and long responses"
            )

    # Dataset size check
    if total < 200:
        validation_report["warnings"].append(
            "Dataset too small for fine-tuning - aim for 500+ examples"
        )
    elif total < 500:
        validation_report["warnings"].append(
            "Dataset size adequate for basic training but consider expansion for better generalization"
        )

    # Difficulty distribution
    difficulties = Counter(ex.get("difficulty", "unknown") for ex in examples)
    validation_report["statistics"]["difficulties"] = dict(difficulties)

    # Domain distribution
    domains = Counter(ex.get("domain", "unknown") for ex in examples)
    validation_report["statistics"]["domains"] = dict(domains)

    # Multi-turn examples
    multi_turn_count = sum(1 for ex in examples if ex.get("has_context", False))
    validation_report["statistics"]["multi_turn_examples"] = multi_turn_count

    if multi_turn_count < total * 0.1:
        validation_report["warnings"].append(
            "Few multi-turn conversation examples - add more context-aware responses"
        )

    return validation_report


def create_enhanced_vetta_examples() -> list[dict[str, Any]]:
    """
    Create an enhanced dataset using Hugging Face datasets.
    Loads pre-existing data from user's Hugging Face account and adapts it for Vetta interview training.
    Includes expanded persona examples for HR, interviewer, and sourcer roles.
    """

    # Set Hugging Face token for authentication
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        os.environ["HF_TOKEN"] = hf_token
    else:
        print("⚠️  HF_TOKEN not set. Please set it or run huggingface-cli login")

    # Load the specific dataset from user's Hugging Face account
    dataset_name = "asifdotpy/vetta-multi-persona-dataset"
    print(f"📥 Loading dataset from your Hugging Face account: {dataset_name}")

    dataset = load_dataset(dataset_name, split="train")

    examples = []
    interview_categories = {
        "opening": "opening",
        "technical_question": "technical_question",
        "closing": "closing",
        "sourcing_initiation": "general",
        "behavioral": "behavioral",
        "agent_coordination": "general",
        "feedback": "feedback",
        "multi_turn": "multi_turn",
        "persona_adaptation": "general",
        "workflow_orchestration": "general",
        "platform_navigation": "general",
        "candidate_profiling": "general",
        "execution_monitoring": "general",
        "data_driven_insights": "general",
        "edge_case": "edge_case",
    }

    # Process and categorize examples
    for item in dataset:
        instruction = item.get("instruction", "")
        response = item.get("response", "")
        category = item.get("category", "")

        # Map to interview categories
        vetta_category = interview_categories.get(category, "general")

        # Determine difficulty and domain based on content
        difficulty = "intermediate"
        domain = "general"
        if "python" in instruction.lower() or "code" in instruction.lower():
            domain = "backend_python"
            difficulty = "advanced" if "advanced" in instruction.lower() else "intermediate"
        elif "javascript" in instruction.lower() or "react" in instruction.lower():
            domain = "frontend"
        elif "machine learning" in instruction.lower() or "ml" in instruction.lower():
            domain = "ml_ai"
        elif "system design" in instruction.lower():
            domain = "system_design"

        # Determine expected length
        word_count = len(response.split())
        expected_length = "short" if word_count < 50 else "medium" if word_count < 150 else "long"

        # Check for multi-turn context
        has_context = "follow up" in instruction.lower() or "previous" in instruction.lower()

        examples.append(
            {
                "instruction": instruction,
                "response": response,
                "category": vetta_category,
                "difficulty": difficulty,
                "domain": domain,
                "expected_length": expected_length,
                "has_context": has_context,
            }
        )

        # Limit to ~400 examples to leave room for expanded persona examples
        if len(examples) >= 400:
            break

    # Add expanded persona-specific examples
    print("🎭 Adding expanded persona-specific training examples...")
    persona_examples = create_persona_examples()
    examples.extend(persona_examples)

    print(f"📊 Total examples after persona expansion: {len(examples)}")

    return examples


def create_persona_examples() -> list[dict[str, Any]]:
    """
    Create expanded persona-specific training examples for HR, interviewer, and sourcer roles.
    Based on the actual persona definitions found in the agents directory.
    """
    persona_examples = []

    # Technical Interviewer Examples (from Modelfile.technical)
    technical_examples = [
        {
            "instruction": "As a technical interviewer, ask a question about Python experience.",
            "response": "Can you walk me through your experience with Python? I'd like to understand what types of projects you've worked on and how you've applied Python in solving technical challenges.",
            "category": "technical_question",
            "difficulty": "intermediate",
            "domain": "backend_python",
            "expected_length": "medium",
            "has_context": False,
        },
        {
            "instruction": "Evaluate this technical problem-solving approach: 'I would use a dictionary for O(1) lookups'",
            "response": "That's a solid approach for optimizing lookup time. The O(1) complexity is excellent for this use case. Can you elaborate on when you might choose this over other data structures and any trade-offs to consider?",
            "category": "feedback",
            "difficulty": "advanced",
            "domain": "system_design",
            "expected_length": "medium",
            "has_context": True,
        },
        {
            "instruction": "Ask about system design considerations for a high-traffic web application.",
            "response": "How would you approach designing a system that needs to handle millions of requests per day? What key considerations would you prioritize for scalability, reliability, and maintainability?",
            "category": "technical_question",
            "difficulty": "advanced",
            "domain": "system_design",
            "expected_length": "medium",
            "has_context": False,
        },
    ]

    # Behavioral Interviewer Examples (from Modelfile.behavioral)
    behavioral_examples = [
        {
            "instruction": "As a behavioral interviewer, ask about handling team conflicts.",
            "response": "Tell me about a time when you faced a conflict with a colleague or team member. How did you approach resolving it, and what was the outcome?",
            "category": "behavioral",
            "difficulty": "intermediate",
            "domain": "behavioral",
            "expected_length": "medium",
            "has_context": False,
        },
        {
            "instruction": "Evaluate communication skills in this response about project collaboration.",
            "response": "Your response shows good awareness of communication challenges in team settings. The STAR method you used helps structure your experience clearly. How do you typically ensure all team members are aligned on project goals?",
            "category": "feedback",
            "difficulty": "intermediate",
            "domain": "behavioral",
            "expected_length": "medium",
            "has_context": True,
        },
        {
            "instruction": "Ask about adaptability when facing changing project requirements.",
            "response": "Describe a situation where project requirements changed significantly midway through development. How did you adapt your approach, and what did you learn from that experience?",
            "category": "behavioral",
            "difficulty": "intermediate",
            "domain": "behavioral",
            "expected_length": "medium",
            "has_context": False,
        },
    ]

    # HR Interviewer Examples (from Modelfile.hr)
    hr_examples = [
        {
            "instruction": "As an HR interviewer, ask about long-term career goals.",
            "response": "Where do you see yourself in 3-5 years? How does this role align with your career aspirations and professional development goals?",
            "category": "closing",
            "difficulty": "intermediate",
            "domain": "general",
            "expected_length": "medium",
            "has_context": False,
        },
        {
            "instruction": "Discuss company culture fit and values alignment.",
            "response": "Our company values innovation, collaboration, and continuous learning. Can you tell me about a time when you've contributed to a positive team culture or demonstrated these values in your work?",
            "category": "behavioral",
            "difficulty": "intermediate",
            "domain": "general",
            "expected_length": "medium",
            "has_context": False,
        },
        {
            "instruction": "Ask about motivation for joining the company.",
            "response": "What attracted you to our company specifically? Have you researched our mission, values, or recent projects, and how do they align with what you're looking for in your next role?",
            "category": "opening",
            "difficulty": "intermediate",
            "domain": "general",
            "expected_length": "medium",
            "has_context": False,
        },
    ]

    # Sourcer/Coordinator Examples (from scout-coordinator-agent)
    sourcer_examples = [
        {
            "instruction": "As a talent sourcer, initiate scanning for Python developers in San Francisco.",
            "response": "I'll start scanning LinkedIn, GitHub, and Stack Overflow for Python developers in the San Francisco area. I'll focus on candidates with 3+ years experience and active contributions to open source projects.",
            "category": "sourcing_initiation",
            "difficulty": "intermediate",
            "domain": "general",
            "expected_length": "medium",
            "has_context": False,
        },
        {
            "instruction": "Coordinate between scanning agents and quality assessment for found candidates.",
            "response": "Great! The scanning agents have found 25 qualified candidates. I'll now activate the Quality-Focused Agent to score these candidates based on skills match, experience, and profile completeness.",
            "category": "agent_coordination",
            "difficulty": "intermediate",
            "domain": "general",
            "expected_length": "medium",
            "has_context": True,
        },
        {
            "instruction": "Monitor sourcing pipeline progress and provide status update.",
            "response": "Pipeline status: 45 candidates sourced, 12 contacted, 8 responded, 3 interviews scheduled. The scanning phase is 85% complete. Quality assessment is underway for the remaining candidates.",
            "category": "execution_monitoring",
            "difficulty": "intermediate",
            "domain": "general",
            "expected_length": "medium",
            "has_context": False,
        },
    ]

    # Add all persona examples
    persona_examples.extend(technical_examples)
    persona_examples.extend(behavioral_examples)
    persona_examples.extend(hr_examples)
    persona_examples.extend(sourcer_examples)

    print(f"✅ Added {len(persona_examples)} persona-specific examples:")
    print(f"   - Technical: {len(technical_examples)}")
    print(f"   - Behavioral: {len(behavioral_examples)}")
    print(f"   - HR: {len(hr_examples)}")
    print(f"   - Sourcer: {len(sourcer_examples)}")

    return persona_examples


def create_train_validation_split(
    examples: list[dict[str, Any]], train_ratio: float = 0.8, stratify_by: str = "category"
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Create stratified train/validation split.

    Args:
        examples: List of training examples
        train_ratio: Ratio of examples for training (0.0-1.0)
        stratify_by: Field to stratify by (e.g., 'category', 'difficulty')

    Returns:
        Tuple of (train_examples, val_examples)
    """
    # Group by stratification field
    groups = defaultdict(list)
    for ex in examples:
        key = ex.get(stratify_by, "unknown")
        groups[key].append(ex)

    train_examples = []
    val_examples = []

    for group_examples in groups.values():
        random.shuffle(group_examples)
        split_idx = int(len(group_examples) * train_ratio)
        train_examples.extend(group_examples[:split_idx])
        val_examples.extend(group_examples[split_idx:])

    # Shuffle final datasets
    random.shuffle(train_examples)
    random.shuffle(val_examples)

    return train_examples, val_examples


def save_dataset(examples: list[dict[str, Any]], filename: str):
    """Save dataset to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(examples)} examples to {filename}")


def main():
    """Generate and validate the enhanced dataset."""
    print("🚀 Generating Enhanced Vetta Training Dataset...")
    print("=" * 60)

    # Generate examples
    examples = create_enhanced_vetta_examples()
    print(f"📊 Generated {len(examples)} examples")

    # Validate dataset
    print("\n🔍 Validating dataset...")
    validation = validate_dataset(examples)

    print(f"Total examples: {validation['total_examples']}")
    print(f"Categories: {validation['statistics']['categories']}")
    print(f"Response lengths: {validation['statistics']['response_lengths']}")
    print(f"Multi-turn examples: {validation['statistics']['multi_turn_examples']}")

    if validation["warnings"]:
        print("\n⚠️ Warnings:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")

    if validation["errors"]:
        print("\n❌ Errors:")
        for error in validation["errors"]:
            print(f"  - {error}")

    # Create train/validation split
    print("\n✂️ Creating train/validation split...")
    train_examples, val_examples = create_train_validation_split(examples)
    print(f"Train: {len(train_examples)} examples")
    print(f"Validation: {len(val_examples)} examples")

    # Save datasets
    print("\n💾 Saving datasets...")
    save_dataset(train_examples, "vetta_train.json")
    save_dataset(val_examples, "vetta_validation.json")
    save_dataset(examples, "vetta_full.json")

    print("\n✅ Dataset generation complete!")
    print("📁 Files created:")
    print("  - vetta_full.json (complete dataset)")
    print("  - vetta_train.json (training split)")
    print("  - vetta_validation.json (validation split)")


if __name__ == "__main__":
    main()
