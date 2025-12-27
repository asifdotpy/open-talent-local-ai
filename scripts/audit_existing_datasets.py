#!/usr/bin/env python3
"""
Dataset Inventory & Analysis Tool

Analyzes all existing datasets and generates comprehensive inventory report.
"""

import datetime
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


class DatasetAnalyzer:
    def __init__(self, data_dir: str = "/home/asif1/open-talent-platform/notebooks/data"):
        self.data_dir = Path(data_dir)
        self.datasets = {}
        self.analysis = {}

    def load_all_datasets(self) -> dict[str, list[dict[str, Any]]]:
        """Load all available datasets."""
        print("🔍 Scanning for dataset files...")

        json_files = list(self.data_dir.glob("*.json"))
        print(f"Found {len(json_files)} JSON files")

        for file_path in json_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)

                # Handle both direct arrays and dicts with 'examples' key
                if isinstance(data, dict) and "examples" in data:
                    examples = data["examples"]
                elif isinstance(data, list):
                    examples = data
                else:
                    continue

                self.datasets[file_path.stem] = examples
                print(f"  ✓ {file_path.name}: {len(examples)} examples")
            except Exception as e:
                print(f"  ✗ {file_path.name}: {e}")

        return self.datasets

    def analyze_dataset(self, name: str, examples: list[dict]) -> dict[str, Any]:
        """Analyze a single dataset."""
        if not examples:
            return {"status": "empty"}

        analysis = {
            "total_examples": len(examples),
            "file_size_mb": 0,
            "categories": Counter(),
            "difficulties": Counter(),
            "domains": Counter(),
            "required_fields": {},
            "schema_consistency": {},
            "quality_scores": [],
            "avg_response_length": 0,
        }

        # Analyze schema
        all_fields = set()
        total_response_length = 0

        for i, example in enumerate(examples):
            # Track fields
            all_fields.update(example.keys())

            # Category distribution
            if "category" in example:
                analysis["categories"][example["category"]] += 1

            # Difficulty distribution
            if "difficulty" in example:
                analysis["difficulties"][example["difficulty"]] += 1

            # Domain distribution
            if "domain" in example:
                analysis["domains"][example["domain"]] += 1

            # Response length
            if "response" in example and isinstance(example["response"], str):
                total_response_length += len(example["response"].split())

            # Quality score
            if "quality_score" in example:
                analysis["quality_scores"].append(example["quality_score"])

        # Calculate averages
        if total_response_length > 0:
            analysis["avg_response_length"] = total_response_length / len(examples)

        if analysis["quality_scores"]:
            analysis["avg_quality_score"] = sum(analysis["quality_scores"]) / len(
                analysis["quality_scores"]
            )

        analysis["fields"] = list(all_fields)
        analysis["field_count"] = len(all_fields)

        return analysis

    def generate_report(self) -> str:
        """Generate comprehensive inventory report."""
        report = []
        report.append("# OpenTalent Platform - Dataset Inventory Report\n")
        report.append(
            f"**Generated**: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M UTC')}\n"
        )
        report.append("---\n\n")

        # Summary
        total_examples = sum(len(examples) for examples in self.datasets.values())
        report.append("## 📊 Summary\n\n")
        report.append(f"- **Total Datasets**: {len(self.datasets)}\n")
        report.append(f"- **Total Examples**: {total_examples:,}\n")
        report.append(
            f"- **Average Examples/Dataset**: {total_examples // max(len(self.datasets), 1)}\n\n"
        )

        # Detailed inventory
        report.append("## 📋 Dataset Inventory\n\n")
        report.append("| File | Examples | Quality | Categories | Avg Length | Status |\n")
        report.append("|------|----------|---------|------------|------------|--------|\n")

        for name, examples in sorted(self.datasets.items(), key=lambda x: len(x[1]), reverse=True):
            analysis = self.analyze_dataset(name, examples)

            if analysis.get("status") == "empty":
                report.append(f"| {name} | 0 | N/A | - | - | ⚠️ EMPTY |\n")
                continue

            quality = analysis.get("avg_quality_score", 0)
            quality_str = f"{quality:.2f}" if quality > 0 else "N/A"

            categories = len(analysis["categories"])
            avg_length = analysis.get("avg_response_length", 0)

            # Status indicator
            if len(examples) > 500:
                status = "✅ READY"
            elif len(examples) > 200:
                status = "🟢 GOOD"
            elif len(examples) > 50:
                status = "🟡 SMALL"
            else:
                status = "🔴 TINY"

            report.append(
                f"| {name} | {len(examples)} | {quality_str} | {categories} | {avg_length:.0f} | {status} |\n"
            )

        report.append("\n")

        # Category analysis
        report.append("## 🏷️ Category Distribution\n\n")
        all_categories = defaultdict(int)
        for examples in self.datasets.values():
            for example in examples:
                if "category" in example:
                    all_categories[example["category"]] += 1

        for category, count in sorted(all_categories.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{category}**: {count} examples\n")

        report.append("\n")

        # Domain analysis
        report.append("## 🌍 Domain Distribution\n\n")
        all_domains = defaultdict(int)
        for examples in self.datasets.values():
            for example in examples:
                if "domain" in example:
                    all_domains[example["domain"]] += 1

        for domain, count in sorted(all_domains.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{domain}**: {count} examples\n")

        report.append("\n")

        # Recommendations
        report.append("## 💡 Recommendations\n\n")

        if total_examples < 2000:
            report.append(
                "- ⚠️ **Expand Data Coverage**: Current dataset is below optimal size. Target: 2000-3000 total examples across all agents.\n"
            )

        if len(all_categories) < 15:
            report.append(
                f"- ⚠️ **Add Categories**: Only {len(all_categories)} categories covered. Target: 15+ diverse categories.\n"
            )

        if len(all_domains) < 8:
            report.append(
                f"- ⚠️ **Add Domains**: Only {len(all_domains)} domains covered. Target: 8+ professional domains.\n"
            )

        report.append("- 📋 **Next Steps**:\n")
        report.append("  1. Review `DATASET_STRATEGY_ROADMAP.md` for comprehensive plan\n")
        report.append(
            "  2. Generate datasets for Scout, Boolean Mastery, Engagement, Market Intel, Tool Leverage, Quality, and Scanning agents\n"
        )
        report.append("  3. Validate all datasets using quality pipeline\n")
        report.append("  4. Upload to Hugging Face with proper documentation\n")
        report.append("  5. Integrate into agent training pipelines\n")

        return "".join(report)

    def run(self):
        """Run complete analysis."""
        print("\n" + "=" * 60)
        print("OpenTalent Dataset Inventory & Analysis Tool")
        print("=" * 60 + "\n")

        self.load_all_datasets()

        if not self.datasets:
            print("❌ No datasets found!")
            return

        report = self.generate_report()

        # Save report
        report_file = self.data_dir / "dataset_inventory_report.md"
        with open(report_file, "w") as f:
            f.write(report)

        print("\n✅ Analysis complete!")
        print(f"📁 Report saved: {report_file}\n")
        print(report)


if __name__ == "__main__":
    analyzer = DatasetAnalyzer()
    analyzer.run()
