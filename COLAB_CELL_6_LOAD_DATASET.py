# ════════════════════════════════════════════════════════════════════════════
# COLAB CELL 6: Load Dataset from HuggingFace Hub
# ════════════════════════════════════════════════════════════════════════════
# Copy this entire block into Colab notebook cell 6
# Dataset is already pushed to HF Hub: asifdotpy/talentai-comprehensive-dataset
# ════════════════════════════════════════════════════════════════════════════

from datasets import load_dataset
import os

print("🚀 Loading TalentAI Dataset from HuggingFace Hub")
print("=" * 60)

# Configuration
HF_DATASET_REPO = "asifdotpy/talentai-comprehensive-dataset"
HF_TOKEN = os.getenv("HF_TOKEN", None)

# Load dataset from HF Hub
print(f"\n📥 Loading from HuggingFace Hub...")
print(f"   Repository: {HF_DATASET_REPO}")

try:
    dataset_dict = load_dataset(
        HF_DATASET_REPO,
        token=HF_TOKEN,
        trust_remote_code=True
    )
    
    train_data = dataset_dict['train']
    val_data = dataset_dict['validation']
    
    print(f"\n✅ Dataset loaded successfully!")
    print(f"   Train split: {len(train_data)} examples")
    print(f"   Validation split: {len(val_data)} examples")
    print(f"   Total: {len(train_data) + len(val_data)} examples")
    
except Exception as e:
    print(f"\n❌ Failed to load dataset: {e}")
    print(f"\n📋 Troubleshooting:")
    print(f"   1. Verify HF_TOKEN is set in Colab Secrets")
    print(f"   2. Token must have read access to private dataset")
    print(f"   3. Dataset must be pushed to HF Hub first")
    print(f"\n   Dataset link: https://huggingface.co/datasets/{HF_DATASET_REPO}")
    raise

# ─────────────────────────────────────────────────────────────────
# Format for Alpaca training
# ─────────────────────────────────────────────────────────────────

def format_alpaca(example):
    """Format example for Alpaca instruction-response training"""
    text = f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['response']}"
    return {'text': text}

# Apply formatting
print(f"\n📝 Formatting for training...")
train_dataset = train_data.map(format_alpaca)
val_dataset = val_data.map(format_alpaca)

print(f"✅ Formatted and ready for training!")
print(f"\n📊 Sample training example:")
print(train_dataset[0]['text'][:300] + "...\n")

# ════════════════════════════════════════════════════════════════════════════
# NEXT STEPS
# ════════════════════════════════════════════════════════════════════════════
# 1. Verify data loaded (check sample above)
# 2. Run next cells to load model and apply LoRA
# 3. Cell 9 will train using these datasets
# 4. Training ~60-90 min on T4 GPU
# 5. Final model uploaded to: asifdotpy/vetta-granite-2b-lora-v4
# ════════════════════════════════════════════════════════════════════════════
