#!/usr/bin/env python3
"""
Split Vetta Multi-Persona Dataset into Separate Agent Repositories

This script:
1. Loads the current mixed dataset (461 examples)
2. Splits into three focused datasets:
   - vetta-interview-dataset: Interview-only data (428 examples)
   - scout-sourcing-dataset: Sourcing-only data (33 examples)
   - talent-ai-complete-dataset: All data combined (461 examples)
3. Pushes each to separate Hugging Face repositories
"""

import os
import datasets
from huggingface_hub import HfApi, login
from typing import Dict, Any
import tempfile

def get_dataset_splits() -> Dict[str, Dict[str, Any]]:
    """Define the three dataset splits with their configurations."""

    return {
        "vetta-interview": {
            "repo_id": "asifdotpy/vetta-interview-dataset",
            "categories": [
                'behavioral', 'behavioral_interview', 'closing', 'edge_case',
                'feedback', 'hr_interview', 'multi_turn', 'opening',
                'technical_interview', 'technical_question'
            ],
            "title": "Vetta Interview Dataset",
            "description": "Interview-focused dataset for fine-tuning Vetta (interviewer agent)",
            "agent": "Vetta (Interviewer Agent)"
        },
        "scout-sourcing": {
            "repo_id": "asifdotpy/scout-sourcing-dataset",
            "categories": [
                'agent_coordination', 'candidate_profiling', 'candidate_sourcing',
                'data_driven_insights', 'execution_monitoring', 'persona_adaptation',
                'platform_navigation', 'sourcing_initiation', 'workflow_orchestration'
            ],
            "title": "Scout Sourcing Dataset",
            "description": "Sourcing and coordination dataset for fine-tuning Scout/Sourcer agent",
            "agent": "Scout/Sourcer Agent"
        },
        "talent-ai-complete": {
            "repo_id": "asifdotpy/talent-ai-complete-dataset",
            "categories": None,  # All categories
            "title": "TalentAI Complete Dataset",
            "description": "Complete multi-agent dataset combining interview and sourcing interactions",
            "agent": "All Agents (Combined)"
        }
    }

def create_dataset_readme(config: Dict[str, Any], example_count: int) -> str:
    """Create a README for the dataset."""

    return f"""# {config['title']}

{config['description']}

## Dataset Details

- **Total Examples**: {example_count}
- **Agent**: {config['agent']}
- **Categories**: {len(config['categories']) if config['categories'] else 'All'}
- **Source**: Split from vetta-multi-persona-dataset

## Usage

This dataset is used to fine-tune language models for {config['agent'].lower()} in the TalentAI platform.

## Categories

{chr(10).join(f"- `{cat}`" for cat in config['categories']) if config['categories'] else "- All categories from interview and sourcing domains"}

## Columns

- `instruction`: The prompt or question
- `response`: The expected response
- `category`: Type of interaction
- `difficulty`: Complexity level (easy/medium/hard)
- `domain`: Professional domain
- `expected_length`: Response length expectation
- `has_context`: Whether additional context is provided
- `_metadata`: Additional metadata including source information
"""

def main():
    """Main function to split and push datasets."""

    # Check for HF token
    hf_token = os.environ.get('HF_TOKEN')
    if not hf_token:
        print("❌ Error: HF_TOKEN environment variable not set")
        return

    # Login to Hugging Face
    try:
        login(token=hf_token)
        print("✅ Successfully logged in to Hugging Face")
    except Exception as e:
        print(f"❌ Failed to login to Hugging Face: {e}")
        return

    # Load the complete dataset
    try:
        print("📥 Loading complete dataset...")
        dataset = datasets.load_dataset("asifdotpy/vetta-multi-persona-dataset", split='train')
        print(f"✅ Loaded dataset with {len(dataset)} examples")
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        return

    # Convert to pandas for filtering
    df = dataset.to_pandas()
    splits = get_dataset_splits()

    # Process each split
    for split_name, config in splits.items():
        print(f"\n🔄 Processing {split_name} dataset...")

        try:
            if config['categories'] is None:
                # Complete dataset - all examples
                split_df = df
            else:
                # Filtered dataset
                split_df = df[df['category'].isin(config['categories'])]

            split_dataset = datasets.Dataset.from_pandas(split_df, preserve_index=False)

            print(f"  📊 {split_name}: {len(split_dataset)} examples")

            # Create README
            readme_content = create_dataset_readme(config, len(split_dataset))

            # Push dataset
            print(f"  🚀 Pushing to {config['repo_id']}...")
            split_dataset.push_to_hub(
                repo_id=config['repo_id'],
                commit_message=f"Create {split_name} dataset with {len(split_dataset)} examples",
                private=False
            )

            # Upload README
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(readme_content)
                temp_file_path = f.name

            try:
                api = HfApi()
                api.upload_file(
                    path_or_fileobj=temp_file_path,
                    path_in_repo="README.md",
                    repo_id=config['repo_id'],
                    repo_type="dataset",
                    commit_message="Add dataset README and documentation"
                )
            finally:
                os.unlink(temp_file_path)

            print(f"  ✅ Successfully created {config['repo_id']}")

        except Exception as e:
            print(f"  ❌ Failed to create {split_name}: {e}")
            continue

    print("\n🎉 Dataset split complete!")
    print("\n📍 New Repositories:")
    for split_name, config in splits.items():
        print(f"  • {config['repo_id']}")
        print(f"    {config['description']}")

if __name__ == "__main__":
    main()