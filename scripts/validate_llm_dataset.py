#!/usr/bin/env python3
"""
LLM Training Dataset Validator

Validates the generated training dataset for:
- JSON integrity
- Field completeness
- Quality score distribution
- Domain balance
- Duplicate detection
"""

import json
from collections import Counter
from pathlib import Path


def validate_dataset(filepath: str = "notebooks/data/llm_training_dataset.json") -> dict:
    """Validate training dataset"""

    results = {
        "file_valid": False,
        "total_examples": 0,
        "json_errors": [],
        "field_completeness": {},
        "domain_distribution": {},
        "difficulty_distribution": {},
        "quality_metrics": {
            "average": 0,
            "min": 1.0,
            "max": 0,
            "std_dev": 0,
            "examples_below_07": [],
            "examples_below_06": [],
        },
        "duplicate_detection": {
            "duplicate_instructions": 0,
            "near_duplicates": 0,
            "sample_duplicates": [],
        },
        "warnings": [],
        "errors": [],
        "overall_status": "UNKNOWN",
    }

    # Load file
    try:
        with open(filepath) as f:
            data = json.load(f)
        results["file_valid"] = True
        results["total_examples"] = len(data)
    except Exception as e:
        results["errors"].append(f"Failed to load JSON: {str(e)}")
        results["overall_status"] = "FAILED"
        return results

    # Field completeness check
    required_fields = [
        "instruction",
        "input",
        "response",
        "domain",
        "agent",
        "category",
        "difficulty",
        "context",
        "metadata",
    ]
    field_count = dict.fromkeys(required_fields, 0)

    # Quality checks
    quality_scores = []
    instructions = []

    for i, example in enumerate(data):
        # Check fields
        for field in required_fields:
            if field in example and example[field]:
                field_count[field] += 1

        # Check quality score
        quality = example.get("metadata", {}).get("quality_score", 0)
        quality_scores.append(quality)

        if quality < 0.7:
            results["quality_metrics"]["examples_below_07"].append((i, quality))
        if quality < 0.6:
            results["quality_metrics"]["examples_below_06"].append((i, quality))

        # Track instructions for dedup
        instructions.append(example.get("instruction", ""))

    # Field completeness percentage
    for field, count in field_count.items():
        pct = (count / len(data)) * 100 if len(data) > 0 else 0
        results["field_completeness"][field] = f"{pct:.1f}%"
        if pct < 100:
            results["warnings"].append(f"Field '{field}' missing in {len(data) - count} examples")

    # Quality metrics
    if quality_scores:
        results["quality_metrics"]["average"] = sum(quality_scores) / len(quality_scores)
        results["quality_metrics"]["min"] = min(quality_scores)
        results["quality_metrics"]["max"] = max(quality_scores)

        avg = results["quality_metrics"]["average"]
        variance = sum((x - avg) ** 2 for x in quality_scores) / len(quality_scores)
        results["quality_metrics"]["std_dev"] = variance**0.5

    # Domain distribution
    domains = Counter()
    difficulties = Counter()
    for example in data:
        domains[example.get("domain", "unknown")] += 1
        difficulties[example.get("difficulty", "unknown")] += 1

    results["domain_distribution"] = dict(domains)
    results["difficulty_distribution"] = dict(difficulties)

    # Duplicate detection
    instruction_counts = Counter(instructions)
    duplicates = {k: v for k, v in instruction_counts.items() if v > 1}
    results["duplicate_detection"]["duplicate_instructions"] = len(duplicates)
    if duplicates:
        results["duplicate_detection"]["sample_duplicates"] = list(duplicates.items())[:5]
        results["warnings"].append(f"Found {len(duplicates)} duplicate instructions")

    # Overall status
    if results["errors"]:
        results["overall_status"] = "FAILED"
    elif results["quality_metrics"]["examples_below_06"]:
        results["overall_status"] = "DEGRADED"
    elif results["warnings"]:
        results["overall_status"] = "WARNING"
    else:
        results["overall_status"] = "VALID"

    return results


def print_validation_report(results: dict):
    """Print validation report"""
    print("\n" + "=" * 80)
    print("LLM TRAINING DATASET VALIDATION REPORT")
    print("=" * 80)

    print(f"\n📊 STATUS: {results['overall_status']}")

    if results["file_valid"]:
        print(f"✅ File loaded: {results['total_examples']} examples")
    else:
        print("❌ File load errors:")
        for error in results["json_errors"]:
            print(f"   • {error}")

    print("\n📋 Field Completeness:")
    for field, pct in results["field_completeness"].items():
        status = "✅" if pct == "100.0%" else "⚠️"
        print(f"   {status} {field:15} {pct}")

    print("\n📈 Quality Metrics:")
    print(f"   Average Score:        {results['quality_metrics']['average']:.3f}")
    print(f"   Min Score:            {results['quality_metrics']['min']:.3f}")
    print(f"   Max Score:            {results['quality_metrics']['max']:.3f}")
    print(f"   Std Dev:              {results['quality_metrics']['std_dev']:.3f}")
    print(f"   Examples <0.7:        {len(results['quality_metrics']['examples_below_07'])}")
    print(f"   Examples <0.6:        {len(results['quality_metrics']['examples_below_06'])}")

    print("\n🎯 Domain Distribution:")
    for domain, count in sorted(results["domain_distribution"].items()):
        pct = (count / results["total_examples"]) * 100
        print(f"   {domain:15} {count:4} ({pct:5.1f}%)")

    print("\n📊 Difficulty Distribution:")
    for difficulty, count in sorted(results["difficulty_distribution"].items()):
        pct = (count / results["total_examples"]) * 100
        print(f"   {difficulty:15} {count:4} ({pct:5.1f}%)")

    print("\n🔍 Duplicate Detection:")
    print(f"   Duplicate instructions: {results['duplicate_detection']['duplicate_instructions']}")
    if results["duplicate_detection"]["sample_duplicates"]:
        print("   Sample duplicates:")
        for text, count in results["duplicate_detection"]["sample_duplicates"]:
            print(f'      • "{text[:50]}..." (×{count})')

    if results["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in results["warnings"]:
            print(f"   • {warning}")

    if results["errors"]:
        print("\n❌ Errors:")
        for error in results["errors"]:
            print(f"   • {error}")

    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80 + "\n")


def main():
    """Main entry point"""
    filepath = Path("notebooks/data/llm_training_dataset.json")

    if not filepath.exists():
        print(f"❌ Dataset not found at {filepath}")
        return

    print(f"🔍 Validating dataset: {filepath}")
    results = validate_dataset(str(filepath))
    print_validation_report(results)

    # Return exit code based on status
    exit_codes = {
        "FAILED": 1,
        "DEGRADED": 0,  # Warning but still usable
        "WARNING": 0,  # Non-critical warnings
        "VALID": 0,  # All good
    }

    import sys

    sys.exit(exit_codes.get(results["overall_status"], 1))


if __name__ == "__main__":
    main()
