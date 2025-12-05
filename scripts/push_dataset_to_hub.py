#!/usr/bin/env python3
"""
Push TalentAI dataset to HuggingFace Hub
Run this ONCE locally to push the dataset, then use Colab notebook to train
"""

import json
from pathlib import Path
from datasets import Dataset, DatasetDict
from huggingface_hub import login

# Configuration - Use absolute paths
DATA_DIR = Path("/home/asif1/talent-ai-platform/notebooks/data")
TRAIN_FILE = DATA_DIR / "llm_training_train.json"
VAL_FILE = DATA_DIR / "llm_training_validation.json"
HF_DATASET_REPO = "asifdotpy/talentai-comprehensive-dataset"

def main():
    print("🚀 TalentAI Dataset Push to HuggingFace Hub")
    print("=" * 60)
    
    # Check files exist
    if not TRAIN_FILE.exists() or not VAL_FILE.exists():
        print(f"❌ Dataset files not found:")
        print(f"   Expected: {TRAIN_FILE}")
        print(f"   Expected: {VAL_FILE}")
        return False
    
    print(f"\n✅ Found dataset files:")
    print(f"   {TRAIN_FILE} ({TRAIN_FILE.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"   {VAL_FILE} ({VAL_FILE.stat().st_size / 1024 / 1024:.1f} MB)")
    
    # Load data
    print(f"\n📂 Loading JSON files...")
    with open(TRAIN_FILE) as f:
        train_data = json.load(f)
    with open(VAL_FILE) as f:
        val_data = json.load(f)
    
    print(f"   Train: {len(train_data)} examples")
    print(f"   Validation: {len(val_data)} examples")
    
    # Create dataset
    print(f"\n🔧 Creating HuggingFace datasets...")
    dataset_dict = DatasetDict({
        'train': Dataset.from_list(train_data),
        'validation': Dataset.from_list(val_data)
    })
    
    # Authenticate
    print(f"\n🔐 Authenticating with HuggingFace...")
    try:
        login()
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print(f"📋 Make sure HF_TOKEN is set or you ran `huggingface-cli login`")
        return False
    
    # Push to hub
    print(f"\n📤 Pushing to HuggingFace Hub...")
    print(f"   Repository: {HF_DATASET_REPO}")
    
    try:
        dataset_dict.push_to_hub(
            HF_DATASET_REPO,
            private=True,
            commit_message="TalentAI comprehensive dataset - 8 domains, 2,075 examples, 0.875 avg quality"
        )
        print(f"\n✅ SUCCESS!")
        print(f"   Dataset pushed to: https://huggingface.co/datasets/{HF_DATASET_REPO}")
        print(f"   Train split: {len(train_data)} examples")
        print(f"   Validation split: {len(val_data)} examples")
        print(f"\n📋 Next steps:")
        print(f"   1. Copy Colab notebook: granite_fine_tuning_v4_comprehensive.ipynb")
        print(f"   2. Open in: https://colab.research.google.com")
        print(f"   3. Select T4 GPU runtime")
        print(f"   4. Run cells in order")
        print(f"   5. Model will be saved to HF: asifdotpy/vetta-granite-2b-lora-v4")
        return True
        
    except Exception as e:
        print(f"\n❌ Push failed: {e}")
        print(f"📋 Troubleshooting:")
        print(f"   - Check HF token has 'datasets' write permission")
        print(f"   - Verify .env HF_TOKEN is valid")
        print(f"   - Try: huggingface-cli login --token <YOUR_TOKEN>")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
