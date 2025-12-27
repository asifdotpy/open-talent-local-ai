#!/usr/bin/env python3
"""
Update Vetta Dataset Card with Correct _metadata Schema
"""
from pathlib import Path

from huggingface_hub import HfApi


def main():
    # Load .env file
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        return

    hf_token = None
    with open(env_path) as f:
        for line in f:
            if line.startswith("HF_TOKEN="):
                hf_token = line.split("=", 1)[1].strip().strip('"')
                break

    if not hf_token:
        print("❌ HF_TOKEN not found in .env file!")
        return

    api = HfApi(token=hf_token)

    # Updated dataset card with correct _metadata schema
    dataset_card = """---
dataset_info:
  features:
  - name: instruction
    dtype: string
  - name: response
    dtype: string
  - name: category
    dtype: string
  - name: difficulty
    dtype: string
  - name: domain
    dtype: string
  - name: expected_length
    dtype: string
  - name: has_context
    dtype: bool
  - name: _metadata
    struct:
    - name: last_updated
      dtype: string
    - name: version
      dtype: string
  configs:
  - config_name: default
    data_files:
    - split: train
      path: data/vetta_comprehensive.json
---

# Vetta Multi-Persona Dataset

## Overview

The Vetta Multi-Persona Dataset is a comprehensive instruction-tuning dataset designed to train AI models for multi-role orchestration within the OpenTalent platform. This dataset transforms a single-purpose interview AI into a versatile platform orchestrator capable of handling the entire hiring workflow.

## Dataset Details

### Statistics
- **Total Examples**: 453 instruction-response pairs
- **Categories**: 15 distinct workflow categories
- **Difficulty Levels**: 3 (beginner, intermediate, advanced)
- **Domains**: 7 specialized knowledge areas
- **Personas**: 7 distinct behavioral modes
- **Response Lengths**: 3 categories (short, medium, long)
- **Context Awareness**: 22% of examples include conversational context

### Category Distribution
| Category | Examples | Focus |
|----------|----------|-------|
| feedback | 100 | Interview feedback and assessment |
| multi_turn | 99 | Multi-turn conversation handling |
| behavioral | 48 | Behavioral interview techniques |
| edge_case | 48 | Handling difficult interview scenarios |
| closing | 50 | Interview conclusion and next steps |
| opening | 50 | Interview initiation and rapport building |
| technical_question | 27 | Technical skill assessment |
| sourcing | 15 | Candidate sourcing orchestration |
| engagement | 12 | Multi-channel outreach |
| market_analysis | 8 | Salary benchmarking and intelligence |
| quality_assessment | 10 | Candidate scoring and bias detection |
| pipeline_coordination | 6 | Workflow management |
| scanning | 8 | Platform scanning and discovery |
| boolean_query | 5 | Advanced search query generation |
| tool_integration | 7 | ATS/CRM integration |

## Multi-Persona System

This dataset enables training of AI models with 7 distinct personas:

### 1. Interviewer
Conducts professional technical interviews and assesses candidate skills.

### 2. Scout Coordinator
Orchestrates intelligent talent sourcing workflow and manages agent pipelines.

### 3. Proactive Scanner
Multi-platform talent discovery (LinkedIn, GitHub, Stack Overflow).

### 4. Boolean Mastery
Advanced search query generation with platform-specific syntax.

### 5. Personalized Engagement
Custom outreach and multi-channel communication.

### 6. Market Intelligence
Salary trends and competitive intelligence analysis.

### 7. Quality-Focused
Candidate scoring and bias detection.

## Data Format

Each example follows this JSON structure:
```json
{
  "instruction": "Human-readable task description",
  "response": "Expected AI response with proper formatting",
  "category": "workflow_category",
  "difficulty": "beginner|intermediate|advanced",
  "domain": "backend_python|frontend|ml_ai|system_design|general|talent_sourcing|market_intelligence",
  "expected_length": "short|medium|long",
  "has_context": true|false,
  "_metadata": {
    "last_updated": "2025-11-28",
    "version": "1.1"
  }
}
```

## Usage

### Loading the Dataset
```python
from datasets import load_dataset

# Load the complete dataset
dataset = load_dataset("asifdotpy/vetta-multi-persona-dataset", name="default")
```

### Training Example
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import load_dataset

# Load dataset
dataset = load_dataset("asifdotpy/vetta-multi-persona-dataset")

# Initialize model and tokenizer
model = AutoModelForCausalLM.from_pretrained("ibm-granite/granite-3.0-2b-instruct")
tokenizer = AutoTokenizer.from_pretrained("ibm-granite/granite-3.0-2b-instruct")

# Training setup
training_args = TrainingArguments(
    output_dir="./vetta-fine-tuned",
    num_train_epochs=1,
    per_device_train_batch_size=4,
    save_steps=100,
    logging_steps=10,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
)

trainer.train()
```

## Intended Use

### Primary Use Cases
- **Fine-tuning LLMs** for multi-role AI assistants in HR/recruiting
- **Research** in persona-based AI systems and role adaptation
- **Platform Integration** for OpenTalent and similar HR platforms
- **Benchmarking** multi-persona AI capabilities

### Out-of-Scope Use
- General instruction tuning without HR/recruiting context
- Single-purpose interview AI training
- Non-HR domain applications

## Dataset Creation

### Methodology
1. **Gap Analysis**: Identified limitations in original interview-focused dataset
2. **Systematic Expansion**: Added examples across full hiring workflow
3. **Persona Alignment**: Created examples aligned with distinct behavioral modes
4. **Quality Assurance**: Maintained consistent formatting and metadata structure

### Source Data
- **Original Dataset**: 422 interview-focused examples
- **Expansion**: +31 examples across new categories
- **Quality Control**: 100% format compliance, persona alignment accuracy

## Ethical Considerations

### Bias and Fairness
- Dataset designed to reduce hiring bias through structured assessment
- Includes examples promoting fair and inclusive hiring practices
- Emphasizes skill-based evaluation over demographic factors

### Privacy
- All examples are synthetic and do not contain real candidate data
- No personally identifiable information included
- Focuses on general hiring best practices and techniques

## Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{vetta_multi_persona_2025,
  title={Vetta Multi-Persona Dataset},
  author={Asif Rahman},
  year={2025},
  publisher={Hugging Face},
  url={https://huggingface.co/datasets/asifdotpy/vetta-multi-persona-dataset}
}
```

## License

This dataset is released under the Apache 2.0 License.

## Contact

For questions or contributions, please contact the maintainer at the Hugging Face repository.
"""

    print("Updating dataset card with correct _metadata schema...")
    api.upload_file(
        path_or_fileobj=dataset_card.encode(),
        path_in_repo="README.md",
        repo_id="asifdotpy/vetta-multi-persona-dataset",
        repo_type="dataset",
        commit_message="Fix _metadata schema to match actual data structure (last_updated, version)",
    )
    print("✅ Dataset card updated with correct schema!")


if __name__ == "__main__":
    main()
