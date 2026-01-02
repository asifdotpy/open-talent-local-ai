#!/usr/bin/env python3
"""
Granite Fine-Tuning Setup Validator
Validates that all components are ready for Colab fine-tuning
"""

import json
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    if filepath.exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (MISSING)")
        return False


def validate_training_data():
    """Validate the training data file."""
    data_file = Path("microservices/granite-interview-service/data/interview_v1.json")

    if not check_file_exists(data_file, "Training data file"):
        return False

    try:
        with open(data_file) as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("❌ Training data must be a JSON array")
            return False

        if len(data) < 5:
            print(f"⚠️  Training data has only {len(data)} examples (recommended: 10+)")
        else:
            print(f"✅ Training data has {len(data)} examples")

        # Check data structure
        required_fields = ["instruction", "input", "output"]
        for i, item in enumerate(data[:3]):  # Check first 3 examples
            missing_fields = [field for field in required_fields if field not in item]
            if missing_fields:
                print(f"❌ Example {i+1} missing fields: {missing_fields}")
                return False

        print("✅ Training data structure is valid")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in training data: {e}")
        return False


def validate_colab_notebook():
    """Validate the Colab notebook exists."""
    notebook_file = Path("notebooks/granite_fine_tuning_colab.ipynb")
    return check_file_exists(notebook_file, "Colab notebook")


def validate_directories():
    """Validate required directories exist."""
    dirs = [
        "microservices/granite-interview-service",
        "microservices/granite-interview-service/data",
        "notebooks",
    ]

    all_exist = True
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Directory missing: {dir_path}")
            all_exist = False

    return all_exist


def main():
    """Main validation function."""
    print("🔍 Granite Fine-Tuning Setup Validator")
    print("=" * 40)
    print()

    # Change to project root if running from scripts directory
    if Path.cwd().name == "scripts":
        project_root = Path.cwd().parent
        print(f"📁 Changing to project root: {project_root}")
        import os

        os.chdir(project_root)
        print()

    checks = [
        ("Directories", validate_directories),
        ("Training Data", validate_training_data),
        ("Colab Notebook", validate_colab_notebook),
    ]

    results = []
    for check_name, check_func in checks:
        print(f"🔍 Checking {check_name}...")
        result = check_func()
        results.append(result)
        print()

    # Summary
    print("📊 Validation Summary")
    print("-" * 20)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print()
        print("🎉 Setup is ready for Colab fine-tuning!")
        print()
        print("🚀 Next steps:")
        print("   1. Open Google Colab: https://colab.research.google.com/")
        print("   2. Upload notebooks/granite_fine_tuning_colab.ipynb")
        print("   3. Run cells in order (enable GPU runtime)")
        print("   4. Fine-tuning will take 2-4 hours")
        print()
        print("💡 Pro tips:")
        print("   • Use Colab Pro for longer sessions if needed")
        print("   • Monitor GPU memory during training")
        print("   • Download checkpoints regularly")
        return 0
    else:
        print(f"❌ Some checks failed ({passed}/{total})")
        print()
        print("🔧 Please fix the issues above before proceeding.")
        print("   Run: ./scripts/setup-colab-fine-tuning.sh")
        return 1


if __name__ == "__main__":
    sys.exit(main())
