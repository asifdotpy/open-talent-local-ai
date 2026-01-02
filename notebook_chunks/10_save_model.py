# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL 7: Save Model                                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

import os

from unsloth import FastLanguageModel

# Load configuration (for standalone execution)
try:
    # Try to use config from previous cell (Colab style)
    config
    print("⚙️ Using config from previous cell...")
except NameError:
    # Fallback for standalone execution
    print("⚙️ Loading configuration for standalone execution...")
    exec(open("04_config.py").read())

# Check if model and tokenizer are defined. If not, try to load from checkpoint or base model.
if "model" not in globals() or "tokenizer" not in globals():
    print("🔄 Model or tokenizer not found in memory. Attempting to load...")

    # First, try to load from the latest checkpoint if available
    checkpoint_dir = config.output_dir
    if os.path.exists(checkpoint_dir):
        # Find the latest checkpoint
        checkpoints = [d for d in os.listdir(checkpoint_dir) if d.startswith("checkpoint-")]
        if checkpoints:
            latest_checkpoint = max(checkpoints, key=lambda x: int(x.split("-")[1]))
            checkpoint_path = os.path.join(checkpoint_dir, latest_checkpoint)
            print(f"📂 Found checkpoint: {checkpoint_path}")
            try:
                model, tokenizer = FastLanguageModel.from_pretrained(
                    model_name=checkpoint_path,
                    max_seq_length=config.max_seq_length,
                    dtype=None,
                    load_in_4bit=config.load_in_4bit,
                )
                print("✅ Loaded model from latest checkpoint.")
            except Exception as e:
                print(f"❌ Failed to load from checkpoint: {e}")
                print("🔄 Falling back to loading base model...")
                # Load the base model
                model, tokenizer = FastLanguageModel.from_pretrained(
                    model_name=config.model_name,
                    max_seq_length=config.max_seq_length,
                    dtype=None,
                    load_in_4bit=config.load_in_4bit,
                )
                print("✅ Loaded base model.")
        else:
            print("📂 No checkpoints found, loading base model...")
            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name=config.model_name,
                max_seq_length=config.max_seq_length,
                dtype=None,
                load_in_4bit=config.load_in_4bit,
            )
            print("✅ Loaded base model.")
    else:
        print("📂 No checkpoint directory found, loading base model...")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=config.model_name,
            max_seq_length=config.max_seq_length,
            dtype=None,
            load_in_4bit=config.load_in_4bit,
        )
        print("✅ Loaded base model.")

    # Add LoRA adapters (assuming we need to add them if loading base model)
    model = FastLanguageModel.get_peft_model(
        model,
        r=config.lora_r,
        target_modules=list(config.target_modules),
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )
    print("✅ LoRA adapters added.")

# Directories - Use Drive for persistence
lora_dir = f"{config.models_dir}/lora"
merged_dir = f"{config.models_dir}/merged"
gguf_dir = f"{config.models_dir}/gguf"

# Ensure directories exist
os.makedirs(config.models_dir, exist_ok=True)
os.makedirs(lora_dir, exist_ok=True)
os.makedirs(merged_dir, exist_ok=True)
os.makedirs(gguf_dir, exist_ok=True)

# 1. Save LoRA adapters (~50MB)
print("💾 Saving LoRA adapters...")
model.save_pretrained(lora_dir)
tokenizer.save_pretrained(lora_dir)
print(f"   ✅ {lora_dir}")

# 2. Save merged model (~4GB) - SKIPPED in Colab to prevent session resets
print("\n💾 Skipping merged model save in Colab (memory intensive)...")
print("   ℹ️  Merge locally using: python merge_lora.py")
print("   ✅ Skipped to prevent Colab crashes")

# 3. Save GGUF for Ollama (~1.5GB)
print("\n💾 Skipping GGUF save in Colab (memory intensive)...")
print("   ℹ️  GGUF conversion requires ~16GB+ RAM and compilation")
print("   ℹ️  Convert locally using: python convert_to_gguf.py")
print("   ✅ Skipped to prevent Colab crashes")

# Show sizes
print("\n📊 Model sizes:")
for name, path in [("LoRA", lora_dir), ("Merged", merged_dir), ("GGUF", gguf_dir)]:
    if os.path.exists(path):
        size = sum(
            os.path.getsize(os.path.join(path, f))
            for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
        )
        if size > 0:
            print(f"   {name}: {size / 1024**2:.1f} MB")
        else:
            print(f"   {name}: Skipped (directory empty)")
    else:
        print(f"   {name}: Directory not created")
