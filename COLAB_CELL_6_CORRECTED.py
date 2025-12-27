# ════════════════════════════════════════════════════════════════════════════
# CORRECTED CODE BLOCK: Dataset Push and Load for Colab
# ════════════════════════════════════════════════════════════════════════════
#
# Use this code block in Colab notebook cell 6
#
# Workflow:
# 1. LOCAL: Run push_dataset_to_hub.py to push dataset to HF Hub (ONE TIME)
# 2. COLAB: Run this cell to load dataset from HF Hub
#
# ════════════════════════════════════════════════════════════════════════════

import json
from pathlib import Path

from datasets import Dataset, DatasetDict, load_dataset

print("🚀 Dataset Management: Push to HF or Load from Hub")
print(f"🎯 Target repo: {config['huggingface']['dataset_repo']}")

# ─────────────────────────────────────────────────────────────────
# Try local files first (for pushing to HF Hub)
# ─────────────────────────────────────────────────────────────────

local_train = Path("/home/asif1/open-talent-platform/notebooks/data/llm_training_train.json")
local_val = Path("/home/asif1/open-talent-platform/notebooks/data/llm_training_validation.json")

if local_train.exists() and local_val.exists():
    print("\n✅ Found local dataset files")

    with open(local_train) as f:
        train_data = json.load(f)
    with open(local_val) as f:
        val_data = json.load(f)

    dataset_dict = DatasetDict(
        {"train": Dataset.from_list(train_data), "validation": Dataset.from_list(val_data)}
    )

    print(f"📊 Loaded: {len(train_data)} train, {len(val_data)} validation")

    # Push to HF Hub
    print("\n📤 Pushing to HF Hub...")
    try:
        dataset_dict.push_to_hub(
            config["huggingface"]["dataset_repo"],
            private=True,
            commit_message="OpenTalent comprehensive dataset - 8 domains, 2075 examples",
        )
        print(f"✅ Pushed to HF Hub: {config['huggingface']['dataset_repo']}")
    except Exception as e:
        print(f"⚠️  Push error (may already exist): {e}")

else:
    print("\n📥 Local files not found, loading from HF Hub...")

    try:
        dataset_dict = load_dataset(config["huggingface"]["dataset_repo"], trust_remote_code=True)
        train_data = dataset_dict["train"].to_list() if "train" in dataset_dict else []
        val_data = dataset_dict["validation"].to_list() if "validation" in dataset_dict else []
        print(f"✅ Loaded from HF Hub: {len(train_data)} train, {len(val_data)} validation")

    except Exception as e:
        print(f"❌ Failed: {e}")
        print("📋 Solution: Push dataset from local first, then re-run this cell")
        raise

# ─────────────────────────────────────────────────────────────────
# Format for training
# ─────────────────────────────────────────────────────────────────


def format_example(ex):
    return {"text": f"### Instruction:\n{ex['instruction']}\n\n### Response:\n{ex['response']}"}


train_dataset = dataset_dict["train"].map(format_example)
val_dataset = dataset_dict["validation"].map(format_example)

print("\n✅ Ready for training!")
print(f"📊 Train: {len(train_dataset)} | Validation: {len(val_dataset)}")
print(f"📝 Sample:\n{train_dataset[0]['text'][:250]}...")

# ════════════════════════════════════════════════════════════════════════════
# WORKFLOW NOTES
# ════════════════════════════════════════════════════════════════════════════
#
# Step 1: PUSH DATASET (Run ONCE locally)
# ─────────────────────────────────────────────────────────────────
#   python scripts/push_dataset_to_hub.py
#
#   This will:
#   - Load local JSON files from notebooks/data/
#   - Create HF datasets
#   - Push to private repo: asifdotpy/OpenTalent-comprehensive-dataset
#   - Requires HF_TOKEN with write access
#
# Step 2: USE IN COLAB
# ─────────────────────────────────────────────────────────────────
#   1. Open: granite_fine_tuning_v4_comprehensive.ipynb
#   2. Replace cell 6 with this code block
#   3. Run cell 6 - will load from HF Hub
#   4. Run remaining cells to train
#
# ════════════════════════════════════════════════════════════════════════════
