# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL 6: Load Dataset from HuggingFace Hub                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

from datasets import load_dataset, DatasetDict, Dataset
import os
import json

print("📥 Loading dataset from HuggingFace Hub...")
print(f"🔗 Dataset: {config['huggingface']['dataset_repo']}")

try:
    # Load from HF Hub (private repo)
    dataset_dict = load_dataset(
        config['huggingface']['dataset_repo'],
        trust_remote_code=True,
        download_mode='force_redownload'
    )
    print(f"✅ Loaded from HF Hub:")
    print(f"   Train: {len(dataset_dict['train'])} examples")
    print(f"   Validation: {len(dataset_dict['validation'])} examples")
    
except Exception as e:
    print(f"⚠️  HF Hub load failed: {e}")
    print(f"🔄 Attempting fallback: Create minimal dataset...")
    
    # Fallback: Create minimal dataset for testing
    fallback_data = [
        {
            "instruction": "Begin a software engineering interview for a senior Python developer position.",
            "response": "Hello! I'm Vetta, and I'll be conducting your interview today for the Senior Python Developer role. I'm excited to learn about your experience! Let's start with something to help me understand your background."
        },
        {
            "instruction": "Ask a technical question about Python async programming.",
            "response": "Can you explain the difference between `asyncio.gather()` and `asyncio.wait()`? I'm interested in your reasoning process as much as the answer."
        },
        {
            "instruction": "The candidate gave a good answer. Provide positive feedback.",
            "response": "You've got the core concept exactly right! Your instinct about concurrency patterns is solid. Let me add some nuance for completeness."
        },
        {
            "instruction": "Ask about system design for microservices architecture.",
            "response": "Let's discuss system design. How would you handle inter-service communication in a microservices-based platform?"
        },
        {
            "instruction": "Wrap up the interview professionally.",
            "response": "Thank you so much for your time today! You've demonstrated strong technical knowledge. Our hiring team will review and you'll hear back within the timeframe."
        },
    ]
    
    # Split 80/20 for train/validation
    split_idx = int(len(fallback_data) * 0.8)
    train_data = fallback_data[:split_idx]
    val_data = fallback_data[split_idx:]
    
    dataset_dict = DatasetDict({
        'train': Dataset.from_list(train_data),
        'validation': Dataset.from_list(val_data)
    })
    
    print(f"✅ Created fallback dataset:")
    print(f"   Train: {len(dataset_dict['train'])} examples")
    print(f"   Validation: {len(dataset_dict['validation'])} examples")
    print(f"\n⚠️  NOTE: Using minimal fallback. For full training, ensure:")
    print(f"   1. HF token is valid (has access to private dataset)")
    print(f"   2. Dataset is pushed to: asifdotpy/talentai-comprehensive-dataset")
    print(f"   3. Token user has read access to private repos")

# Format for training
def format_example(ex):
    return {'text': f"### Instruction:\n{ex['instruction']}\n\n### Response:\n{ex['response']}"}

train_dataset = dataset_dict['train'].map(format_example)
val_dataset = dataset_dict['validation'].map(format_example)

print(f"\n✅ Dataset formatted and ready for training")
print(f"📊 Train samples: {len(train_dataset)}")
print(f"📊 Validation samples: {len(val_dataset)}")
print(f"\n📝 Sample training text:\n{train_dataset[0]['text'][:300]}...")
