#!/usr/bin/env python3
"""
Expand Vetta Multi-Persona Dataset with Persona Examples and Push to Hugging Face

This script:
1. Loads the base Vetta multi-persona dataset (453 examples)
2. Adds 4 additional persona examples from agents directory
3. Creates combined dataset (457 examples)
4. Pushes the expanded dataset to Hugging Face Hub
"""

import os
from typing import Any

import datasets
from huggingface_hub import HfApi, login


def get_persona_examples() -> list[dict[str, Any]]:
    """Get the 4 additional persona examples from agents directory analysis."""

    return [
        {
            "instruction": "As an HR interviewer, evaluate this candidate's experience with team collaboration and conflict resolution.",
            "response": "Based on the candidate's description of leading cross-functional teams and mediating conflicts, they demonstrate strong collaboration skills. Their experience shows they can navigate interpersonal dynamics while maintaining team productivity. I'd rate their collaboration skills as excellent.",
            "category": "hr_interview",
            "difficulty": "medium",
            "domain": "human_resources",
            "expected_length": "short",
            "has_context": False,
            "_metadata": {"source": "agents/hr_persona", "persona": "hr_interviewer"},
        },
        {
            "instruction": "As a technical interviewer, assess this developer's understanding of system design principles.",
            "response": "The candidate shows solid understanding of scalability and distributed systems. Their explanation of microservices architecture demonstrates practical knowledge. However, they could elaborate more on trade-offs between different design patterns. Overall, competent technical foundation.",
            "category": "technical_interview",
            "difficulty": "hard",
            "domain": "software_engineering",
            "expected_length": "medium",
            "has_context": False,
            "_metadata": {"source": "agents/technical_persona", "persona": "technical_interviewer"},
        },
        {
            "instruction": "As a behavioral interviewer, explore how this candidate handles high-pressure situations.",
            "response": "The candidate describes using structured problem-solving approaches under pressure. Their example of managing a critical system outage shows good crisis management skills. They prioritize communication and quick decision-making, which are valuable traits for high-stakes environments.",
            "category": "behavioral_interview",
            "difficulty": "medium",
            "domain": "behavioral_assessment",
            "expected_length": "medium",
            "has_context": False,
            "_metadata": {
                "source": "agents/behavioral_persona",
                "persona": "behavioral_interviewer",
            },
        },
        {
            "instruction": "As a sourcer, evaluate this candidate profile for a senior developer position.",
            "response": "Strong candidate match: 8+ years experience, led multiple projects, contributed to open source. Technical skills align well with requirements. Location and salary expectations are reasonable. Would recommend for technical interview. Risk assessment: medium - verify recent project involvement.",
            "category": "candidate_sourcing",
            "difficulty": "medium",
            "domain": "talent_acquisition",
            "expected_length": "short",
            "has_context": False,
            "_metadata": {"source": "agents/sourcer_persona", "persona": "talent_sourcer"},
        },
    ]


def main():
    """Main function to expand dataset and push to Hugging Face."""

    # Check for HF token
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("❌ Error: HF_TOKEN environment variable not set")
        print("Please set your Hugging Face API token:")
        print("export HF_TOKEN=your_token_here")
        return

    # Login to Hugging Face
    try:
        login(token=hf_token)
        print("✅ Successfully logged in to Hugging Face")
    except Exception as e:
        print(f"❌ Failed to login to Hugging Face: {e}")
        return

    # Load base dataset
    try:
        print("📥 Loading base Vetta multi-persona dataset...")
        dataset = datasets.load_dataset("asifdotpy/vetta-multi-persona-dataset")
        print(f"✅ Loaded base dataset with {len(dataset['train'])} examples")
    except Exception as e:
        print(f"❌ Failed to load base dataset: {e}")
        return

    # Get persona examples
    persona_examples = get_persona_examples()
    print(f"📝 Adding {len(persona_examples)} persona examples...")

    # Create dataset from persona examples
    persona_dataset = datasets.Dataset.from_list(persona_examples)

    # Combine datasets
    combined_dataset = datasets.concatenate_datasets([dataset["train"], persona_dataset])
    print(f"✅ Combined dataset now has {len(combined_dataset)} examples")

    # Verify the expansion
    print("\n📊 Dataset Statistics:")
    print(f"Original: {len(dataset['train'])} examples")
    print(f"Added: {len(persona_examples)} examples")
    print(f"Total: {len(combined_dataset)} examples")

    # Show category distribution
    categories = combined_dataset.to_pandas()["category"].value_counts()
    print("\n📈 Category Distribution:")
    for cat, count in categories.items():
        print(f"  {cat}: {count}")

    # Push to Hugging Face
    try:
        print("\n🚀 Pushing expanded dataset to Hugging Face...")

        # Create dataset card
        dataset_card = """# Vetta Multi-Persona Interview Dataset (Expanded)

This dataset contains examples of interviewer-candidate interactions across multiple personas and domains.

## Dataset Details

- **Total Examples**: 457 (expanded from 453)
- **Categories**: 15 different interview types
- **Personas**: HR, Technical, Behavioral, Sourcer
- **Domains**: Software Engineering, Human Resources, Behavioral Assessment, Talent Acquisition

## Recent Updates (December 3, 2025)

**Version 1.1**: Added 4 persona-specific examples to enhance model understanding of different interviewer roles:
- HR Interviewer: Focus on candidate evaluation and HR processes
- Technical Interviewer: Deep technical assessment and system design
- Behavioral Interviewer: Soft skills and situational judgment
- Talent Sourcer: Candidate profiling and recruitment evaluation

## Usage

This dataset is used to fine-tune language models for multi-persona interview simulations in the OpenTalent platform.

## Columns

- `instruction`: The interview question or prompt
- `response`: The expected response from the interviewer
- `category`: Type of interview interaction
- `difficulty`: Complexity level (easy/medium/hard)
- `domain`: Professional domain
- `expected_length`: Response length expectation
- `has_context`: Whether additional context is provided
- `_metadata`: Additional metadata including source and persona information
"""

        # Push the dataset
        combined_dataset.push_to_hub(
            repo_id="asifdotpy/vetta-multi-persona-dataset",
            commit_message="Expand dataset to 457 examples with persona-specific training data",
            private=False,
        )

        # Write dataset card to temporary file and upload
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(dataset_card)
            temp_file_path = f.name

        try:
            api = HfApi()
            api.upload_file(
                path_or_fileobj=temp_file_path,
                path_in_repo="README.md",
                repo_id="asifdotpy/vetta-multi-persona-dataset",
                repo_type="dataset",
                commit_message="Update dataset card for expanded version",
            )
        finally:
            os.unlink(temp_file_path)

        print("✅ Successfully pushed expanded dataset to Hugging Face!")
        print("📍 Repository: https://huggingface.co/datasets/asifdotpy/vetta-multi-persona-dataset")

    except Exception as e:
        print(f"❌ Failed to push dataset: {e}")
        return


if __name__ == "__main__":
    main()
