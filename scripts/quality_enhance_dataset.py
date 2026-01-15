#!/usr/bin/env python3
"""
Quality Enhancement Script for Vetta Comprehensive Dataset

This script cleans and enhances the vetta_comprehensive.json dataset by:
1. Removing duplicate instruction-response pairs
2. Improving metadata with proper source tracking
3. Balancing category distributions
4. Adding quality validation
5. Preparing for Hugging Face upload

Usage:
    python scripts/quality_enhance_dataset.py
"""

import json
import os
from collections import Counter
from datetime import datetime
from typing import Any


def load_dataset(file_path: str) -> list[dict[str, Any]]:
    """Load the dataset from JSON file."""
    print(f"📥 Loading dataset from {file_path}")
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    # Handle both formats (with or without wrapper)
    if isinstance(data, dict) and "examples" in data:
        examples = data["examples"]
    else:
        examples = data

    print(f"✅ Loaded {len(examples)} examples")
    return examples


def remove_duplicates(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicate instruction-response pairs, keeping the first occurrence."""
    print("🔄 Removing duplicates...")

    seen_pairs = set()
    unique_data = []

    for item in data:
        # Create a unique key from instruction + response
        pair_key = (item["instruction"], item["response"])

        if pair_key not in seen_pairs:
            seen_pairs.add(pair_key)
            unique_data.append(item)

    removed_count = len(data) - len(unique_data)
    print(f"✅ Removed {removed_count} duplicates, kept {len(unique_data)} unique examples")
    return unique_data


def enhance_metadata(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Enhance metadata with proper source tracking and quality indicators."""
    print("🔧 Enhancing metadata...")

    for item in data:
        # Ensure _metadata exists and is a dict
        if not isinstance(item.get("_metadata"), dict):
            item["_metadata"] = {}

        metadata = item["_metadata"]

        # Add source information
        if "source" not in metadata:
            metadata["source"] = "vetta_comprehensive_v1"

        # Add quality score based on content
        quality_score = calculate_quality_score(item)
        metadata["quality_score"] = quality_score

        # Add processing timestamp
        metadata["processed_at"] = datetime.now().isoformat()

        # Add version info
        metadata["version"] = "1.1.0"

    print("✅ Enhanced metadata for all examples")
    return data


def calculate_quality_score(item: dict[str, Any]) -> float:
    """Calculate a quality score for the example (0.0 to 1.0)."""
    score = 0.0

    # Base score for having required fields
    if "instruction" in item and "response" in item:
        score += 0.3

    # Content quality
    instruction = item.get("instruction", "")
    response = item.get("response", "")

    # Length checks (reasonable lengths)
    if 20 <= len(instruction) <= 200:
        score += 0.2
    if 50 <= len(response) <= 500:
        score += 0.2

    # Metadata completeness
    metadata_fields = ["category", "difficulty", "domain"]
    metadata_score = sum(1 for field in metadata_fields if field in item) / len(metadata_fields)
    score += metadata_score * 0.3

    return round(min(score, 1.0), 2)


def balance_categories(data: list[dict[str, Any]], min_examples: int = 10) -> list[dict[str, Any]]:
    """Balance category distributions by ensuring minimum examples per category."""
    print("⚖️ Balancing category distributions...")

    # Count current distribution
    categories = Counter(item.get("category", "unknown") for item in data)
    print(f"Current categories: {dict(categories)}")

    # Identify underrepresented categories
    underrepresented = {cat: count for cat, count in categories.items() if count < min_examples}

    if not underrepresented:
        print("✅ All categories have sufficient examples")
        return data

    print(f"📉 Underrepresented categories: {underrepresented}")

    # For now, we'll note this but not artificially inflate categories
    # In a real scenario, you'd generate synthetic examples or collect more data
    print("⚠️ Note: Some categories have few examples. Consider collecting more diverse data.")

    return data


def validate_dataset(data: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate the dataset quality and return validation results."""
    print("🔍 Validating dataset quality...")

    validation = {
        "total_examples": len(data),
        "missing_fields": {},
        "empty_fields": {},
        "quality_distribution": Counter(),
        "category_distribution": Counter(),
        "domain_distribution": Counter(),
        "warnings": [],
        "errors": [],
    }

    for item in data:
        # Check required fields
        required_fields = ["instruction", "response", "category", "difficulty", "domain"]
        for field in required_fields:
            if field not in item:
                validation["missing_fields"][field] = validation["missing_fields"].get(field, 0) + 1
            elif not item[field] or str(item[field]).strip() == "":
                validation["empty_fields"][field] = validation["empty_fields"].get(field, 0) + 1

        # Collect distributions
        validation["quality_distribution"][item.get("_metadata", {}).get("quality_score", 0)] += 1
        validation["category_distribution"][item.get("category", "unknown")] += 1
        validation["domain_distribution"][item.get("domain", "unknown")] += 1

    # Generate warnings and errors
    if validation["missing_fields"]:
        validation["errors"].append(f"Missing required fields: {validation['missing_fields']}")

    if validation["empty_fields"]:
        validation["warnings"].append(f"Empty fields found: {validation['empty_fields']}")

    low_quality = sum(
        count for score, count in validation["quality_distribution"].items() if score < 0.7
    )
    if low_quality > len(data) * 0.1:  # More than 10% low quality
        validation["warnings"].append(f"{low_quality} examples have quality score < 0.7")

    print("✅ Validation complete")
    return validation


def save_dataset(data: list[dict[str, Any]], output_path: str, validation: dict[str, Any]):
    """Save the enhanced dataset with validation summary."""
    print(f"💾 Saving enhanced dataset to {output_path}")

    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Add validation summary as a comment/metadata
    enhanced_data = {
        "_dataset_metadata": {
            "created_at": datetime.now().isoformat(),
            "total_examples": len(data),
            "validation_summary": validation,
            "enhancement_version": "1.1.0",
        },
        "examples": data,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enhanced_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(data)} examples to {output_path}")


def generate_quality_report(validation: dict[str, Any], output_path: str):
    """Generate a quality report."""
    report_path = output_path.replace(".json", "_quality_report.md")

    report = f"""# Dataset Quality Report
Generated: {datetime.now().isoformat()}

## Summary
- **Total Examples**: {validation["total_examples"]}
- **Quality Score Distribution**: {dict(validation["quality_distribution"])}
- **Category Distribution**: {dict(validation["category_distribution"])}
- **Domain Distribution**: {dict(validation["domain_distribution"])}

## Issues Found
"""

    if validation["errors"]:
        report += "\n### Errors\n"
        for error in validation["errors"]:
            report += f"- {error}\n"

    if validation["warnings"]:
        report += "\n### Warnings\n"
        for warning in validation["warnings"]:
            report += f"- {warning}\n"

    if not validation["errors"] and not validation["warnings"]:
        report += "\n✅ No issues found!\n"

    report += "\n## Recommendations\n"
    report += "- Review examples with quality score < 0.7\n"
    report += "- Consider collecting more data for underrepresented categories\n"
    report += "- Validate instruction-response pairs for coherence\n"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"📊 Quality report saved to {report_path}")


def main():
    """Main function to enhance dataset quality."""
    import argparse

    parser = argparse.ArgumentParser(description="Enhance dataset quality")
    parser.add_argument(
        "--input",
        type=str,
        default="notebooks/data/vetta_comprehensive.json",
        help="Input dataset file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output dataset file (default: input_enhanced.json)",
    )
    args = parser.parse_args()

    print("🚀 Starting Vetta Dataset Quality Enhancement")
    print("=" * 50)

    # File paths
    input_file = args.input
    if args.output:
        output_file = args.output
    else:
        output_file = input_file.replace(".json", "_enhanced.json")

    # Load dataset
    data = load_dataset(input_file)

    # Remove duplicates
    data = remove_duplicates(data)

    # Enhance metadata
    data = enhance_metadata(data)

    # Balance categories (informational only for now)
    data = balance_categories(data)

    # Validate
    validation = validate_dataset(data)

    # Save enhanced dataset
    save_dataset(data, output_file, validation)

    # Generate quality report
    generate_quality_report(validation, output_file)

    print("\n" + "=" * 50)
    print("✅ Dataset quality enhancement complete!")
    print(f"📁 Enhanced dataset: {output_file}")
    print(f"📊 Quality report: {output_file.replace('.json', '_quality_report.md')}")

    # Summary
    print("\n📈 Summary:")
    print(f"  • Started with: {validation['total_examples']} examples")
    print(f"  • Quality distribution: {dict(validation['quality_distribution'])}")
    print(f"  • Categories: {len(validation['category_distribution'])}")
    print(f"  • Domains: {len(validation['domain_distribution'])}")


if __name__ == "__main__":
    main()
