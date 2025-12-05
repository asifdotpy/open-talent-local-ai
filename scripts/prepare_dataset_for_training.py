#!/usr/bin/env python3
"""
Prepare LLM Training Dataset for LoRA Fine-Tuning
================================================

This script prepares the comprehensive LLM training dataset for Granite 3.0-2B fine-tuning:
- Splits dataset into train/validation (80/20)
- Formats for Alpaca-style training
- Generates statistics and metadata
- Creates ready-to-use JSON files

Output:
    - llm_training_train.json (1,660 examples)
    - llm_training_validation.json (415 examples)
    - dataset_statistics.json (metadata and stats)

Usage:
    python scripts/prepare_dataset_for_training.py
"""

import json
import random
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DatasetStats:
    """Statistics for dataset splits."""
    total_examples: int
    train_examples: int
    val_examples: int
    domains: Dict[str, int]
    categories: Dict[str, int]
    difficulties: Dict[str, int]
    quality_avg: float
    quality_min: float
    quality_max: float


def load_dataset(file_path: str) -> List[Dict[str, Any]]:
    """Load the comprehensive LLM training dataset."""
    print(f"📥 Loading dataset from: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Loaded {len(data)} examples")
    return data


def stratified_split(
    examples: List[Dict[str, Any]],
    train_ratio: float = 0.8,
    stratify_by: str = "domain",
    seed: int = 42
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Create stratified train/validation split.
    
    Ensures balanced representation of each domain in both splits.
    """
    random.seed(seed)
    
    # Group by stratification field
    groups = {}
    for ex in examples:
        key = ex.get(stratify_by, 'unknown')
        if key not in groups:
            groups[key] = []
        groups[key].append(ex)
    
    train_examples = []
    val_examples = []
    
    # Split each group proportionally
    for group_examples in groups.values():
        random.shuffle(group_examples)
        split_idx = int(len(group_examples) * train_ratio)
        train_examples.extend(group_examples[:split_idx])
        val_examples.extend(group_examples[split_idx:])
    
    # Shuffle final datasets
    random.shuffle(train_examples)
    random.shuffle(val_examples)
    
    return train_examples, val_examples


def format_for_alpaca(ex: Dict[str, Any]) -> Dict[str, str]:
    """
    Format example for Alpaca-style training.
    
    Alpaca format: instruction + input + response
    """
    # Combine instruction and input for context
    instruction_text = ex['instruction']
    input_text = ex.get('input', '')
    
    if input_text:
        full_instruction = f"{instruction_text}\n\nContext:\n{input_text}"
    else:
        full_instruction = instruction_text
    
    return {
        "instruction": full_instruction,
        "response": ex['response'],
        # Preserve metadata for analysis
        "domain": ex['domain'],
        "category": ex['category'],
        "difficulty": ex['difficulty']
    }


def calculate_stats(train: List[Dict], val: List[Dict]) -> DatasetStats:
    """Calculate comprehensive dataset statistics."""
    all_examples = train + val
    
    # Quality scores
    quality_scores = [ex['metadata']['quality_score'] for ex in all_examples if 'metadata' in ex]
    
    # Distributions
    domains = Counter(ex['domain'] for ex in all_examples)
    categories = Counter(ex['category'] for ex in all_examples)
    difficulties = Counter(ex['difficulty'] for ex in all_examples)
    
    return DatasetStats(
        total_examples=len(all_examples),
        train_examples=len(train),
        val_examples=len(val),
        domains=dict(domains),
        categories=dict(categories),
        difficulties=dict(difficulties),
        quality_avg=sum(quality_scores) / len(quality_scores),
        quality_min=min(quality_scores),
        quality_max=max(quality_scores)
    )


def save_formatted_dataset(examples: List[Dict], output_path: str):
    """Save formatted dataset to JSON."""
    # Format for Alpaca-style training
    formatted = [format_for_alpaca(ex) for ex in examples]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(formatted)} formatted examples to {output_path}")


def save_statistics(stats: DatasetStats, output_path: str):
    """Save dataset statistics to JSON."""
    stats_dict = {
        "generated_date": datetime.now().isoformat(),
        "total_examples": stats.total_examples,
        "train_examples": stats.train_examples,
        "validation_examples": stats.val_examples,
        "split_ratio": f"{stats.train_examples / stats.total_examples:.1%} / {stats.val_examples / stats.total_examples:.1%}",
        "quality_metrics": {
            "average": round(stats.quality_avg, 3),
            "min": round(stats.quality_min, 3),
            "max": round(stats.quality_max, 3)
        },
        "domain_distribution": stats.domains,
        "category_distribution": stats.categories,
        "difficulty_distribution": stats.difficulties
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stats_dict, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved statistics to {output_path}")


def main():
    """Main data preparation pipeline."""
    print("=" * 80)
    print("LLM TRAINING DATASET PREPARATION")
    print("=" * 80)
    print()
    
    # Paths
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "notebooks" / "data"
    input_file = data_dir / "llm_training_dataset.json"
    
    output_train = data_dir / "llm_training_train.json"
    output_val = data_dir / "llm_training_validation.json"
    output_stats = data_dir / "dataset_statistics.json"
    
    # Step 1: Load dataset
    examples = load_dataset(str(input_file))
    
    # Step 2: Create stratified split
    print("\n✂️ Creating train/validation split (80/20)...")
    train_examples, val_examples = stratified_split(examples, train_ratio=0.8, stratify_by="domain")
    
    print(f"   Train: {len(train_examples)} examples ({len(train_examples)/len(examples)*100:.1f}%)")
    print(f"   Validation: {len(val_examples)} examples ({len(val_examples)/len(examples)*100:.1f}%)")
    
    # Step 3: Calculate statistics
    print("\n📊 Calculating dataset statistics...")
    stats = calculate_stats(train_examples, val_examples)
    
    print(f"   Quality avg: {stats.quality_avg:.3f}")
    print(f"   Domains: {len(stats.domains)}")
    print(f"   Categories: {len(stats.categories)}")
    
    # Step 4: Save formatted datasets
    print("\n💾 Saving formatted datasets...")
    save_formatted_dataset(train_examples, str(output_train))
    save_formatted_dataset(val_examples, str(output_val))
    save_statistics(stats, str(output_stats))
    
    # Step 5: Display domain balance
    print("\n🎯 DOMAIN BALANCE CHECK")
    print("-" * 80)
    for domain, count in sorted(stats.domains.items()):
        train_count = len([ex for ex in train_examples if ex['domain'] == domain])
        val_count = len([ex for ex in val_examples if ex['domain'] == domain])
        print(f"{domain:15s} Total: {count:4d} | Train: {train_count:4d} ({train_count/len(train_examples)*100:5.1f}%) | Val: {val_count:3d} ({val_count/len(val_examples)*100:5.1f}%)")
    
    # Step 6: Display difficulty balance
    print("\n📊 DIFFICULTY BALANCE CHECK")
    print("-" * 80)
    for diff, count in sorted(stats.difficulties.items()):
        train_count = len([ex for ex in train_examples if ex['difficulty'] == diff])
        val_count = len([ex for ex in val_examples if ex['difficulty'] == diff])
        print(f"{diff:15s} Total: {count:4d} | Train: {train_count:4d} ({train_count/len(train_examples)*100:5.1f}%) | Val: {val_count:3d} ({val_count/len(val_examples)*100:5.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ DATASET PREPARATION COMPLETE")
    print("=" * 80)
    print(f"\n📁 Output Files:")
    print(f"   • {output_train}")
    print(f"   • {output_val}")
    print(f"   • {output_stats}")
    print(f"\n🚀 Ready for LoRA fine-tuning with Granite 3.0-2B!")
    print(f"   • Train examples: {len(train_examples)}")
    print(f"   • Validation examples: {len(val_examples)}")
    print(f"   • Quality avg: {stats.quality_avg:.3f}")
    print()


if __name__ == "__main__":
    main()
