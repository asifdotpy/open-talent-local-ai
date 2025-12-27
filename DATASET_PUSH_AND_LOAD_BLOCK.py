# ====================================================================
# CORRECTED CODE BLOCK: Push Dataset to HuggingFace Hub
# ====================================================================
# 
# This cell pushes local dataset files to HF Hub as the single
# source of truth. GitHub is private, so URLs don't work.
# 
# Use this for INITIAL setup to push dataset to HF Hub.
# After first push, use the load_dataset() cell instead.
#
# ====================================================================

import json
from datasets import Dataset, DatasetDict
from pathlib import Path
import os

print("🚀 Pushing dataset to HuggingFace Hub...")
print(f"🎯 Target: {config['huggingface']['dataset_repo']}")

# ─────────────────────────────────────────────────────────────────
# OPTION 1: Push from local files (if running locally)
# ─────────────────────────────────────────────────────────────────

local_train = Path('/home/asif1/talent-ai-platform/notebooks/data/llm_training_train.json')
local_val = Path('/home/asif1/talent-ai-platform/notebooks/data/llm_training_validation.json')

if local_train.exists() and local_val.exists():
    print(f"\n📂 Found local files:")
    print(f"   Train: {local_train}")
    print(f"   Validation: {local_val}")
    
    with open(local_train) as f:
        train_data = json.load(f)
    with open(local_val) as f:
        val_data = json.load(f)
    
    dataset_dict = DatasetDict({
        'train': Dataset.from_list(train_data),
        'validation': Dataset.from_list(val_data)
    })
    
    print(f"\n📊 Dataset loaded:")
    print(f"   Train: {len(train_data)} examples")
    print(f"   Validation: {len(val_data)} examples")
    
    # Push to HF Hub
    print(f"\n📤 Pushing to HF Hub...")
    try:
        dataset_dict.push_to_hub(
            config['huggingface']['dataset_repo'],
            private=True,  # Keep dataset private
            commit_message="Upload comprehensive OpenTalent platform dataset"
        )
        print(f"✅ Successfully pushed to: {config['huggingface']['dataset_repo']}")
        print(f"   - Train split: {len(train_data)} examples")
        print(f"   - Validation split: {len(val_data)} examples")
        print(f"🔗 View at: https://huggingface.co/datasets/asifdotpy/{config['huggingface']['dataset_repo'].split('/')[-1]}")
        
    except Exception as e:
        print(f"❌ Push failed: {e}")
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Check HF_TOKEN is valid: from huggingface_hub import login; login()")
        print(f"   2. Ensure token has 'datasets' write permission")
        print(f"   3. Check if dataset repo already exists (can overwrite with existing)")

# ─────────────────────────────────────────────────────────────────
# OPTION 2: Load from HF Hub (if dataset already pushed)
# ─────────────────────────────────────────────────────────────────

else:
    print(f"\n📥 Local files not found, attempting to load from HF Hub...")
    print(f"🔗 Loading from: {config['huggingface']['dataset_repo']}")
    
    try:
        from datasets import load_dataset
        
        dataset_dict = load_dataset(
            config['huggingface']['dataset_repo'],
            trust_remote_code=True
        )
        
        train_data = dataset_dict['train'].to_list() if 'train' in dataset_dict else []
        val_data = dataset_dict['validation'].to_list() if 'validation' in dataset_dict else []
        
        print(f"✅ Loaded from HF Hub:")
        print(f"   Train: {len(train_data)} examples")
        print(f"   Validation: {len(val_data)} examples")
        
    except Exception as e:
        print(f"❌ Load failed: {e}")
        print(f"\n⚠️  Dataset not found on HF Hub")
        print(f"📋 Next steps:")
        print(f"   1. Push dataset from local machine: python scripts/push_dataset_to_hub.py")
        print(f"   2. Or manually run: dataset_dict.push_to_hub('{config['huggingface']['dataset_repo']}')")
        print(f"   3. Then re-run this cell")
        raise

# ─────────────────────────────────────────────────────────────────
# Format for training (both options)
# ─────────────────────────────────────────────────────────────────

def format_example(ex):
    return {'text': f"### Instruction:\n{ex['instruction']}\n\n### Response:\n{ex['response']}"}

train_dataset = dataset_dict['train'].map(format_example) if 'train' in dataset_dict else None
val_dataset = dataset_dict['validation'].map(format_example) if 'validation' in dataset_dict else None

print(f"\n✅ Dataset formatted and ready for training")
print(f"📊 Train samples: {len(train_dataset) if train_dataset else 0}")
print(f"📊 Validation samples: {len(val_dataset) if val_dataset else 0}")
if train_dataset and len(train_dataset) > 0:
    print(f"\n📝 Sample training text:\n{train_dataset[0]['text'][:300]}...")
