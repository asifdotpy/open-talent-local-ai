# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL 3: Load Model with Unsloth                                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

import torch
from unsloth import FastLanguageModel

print(f"🏔️ Loading {config.model_name}...")

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=config.model_name,
    max_seq_length=config.max_seq_length,
    dtype=None,  # Auto-detect: Float16 for T4, BFloat16 for Ampere+
    load_in_4bit=config.load_in_4bit,
)

print(f"✅ Model loaded | GPU: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")

# Add LoRA adapters
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

print("✅ LoRA adapters added")
model.print_trainable_parameters()
