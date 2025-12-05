# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL 5: Train Vetta                                                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# --- Re-load model and tokenizer if not in scope ---
# This part is crucial to ensure 'model' and 'tokenizer' are defined.
# Assumes 'config' and 'dataset' are already defined from previous cells.

# Note: config is assumed to be available from a previous cell. If not, it needs to be defined here.
# For safety, replicating the config definition temporarily if not guaranteed:
import datetime
from dataclasses import dataclass
@dataclass
class Config:
    model_name: str = "ibm-granite/granite-3.0-2b-instruct"
    max_seq_length: int = 2048
    load_in_4bit: bool = True
    lora_r: int = 16; lora_alpha: int = 16; lora_dropout: float = 0
    target_modules: tuple = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")
    batch_size: int = 4 # Updated
    gradient_accumulation: int = 2 # Updated
    epochs: int = 5 # Updated
    learning_rate: float = 2e-4; warmup_steps: int = 10
    output_dir: str = "/content/drive/MyDrive/talent-ai-vetta/checkpoints"  # Drive path
    models_dir: str = "/content/drive/MyDrive/talent-ai-vetta/models"      # Drive path
    data_repetitions: int = 10 # Updated
config = Config()

# Check if model and tokenizer are defined. If not, load them.
if 'model' not in globals() or 'tokenizer' not in globals():
    print(f"🔄 Model or tokenizer not found in memory. Attempting to load for training...")
    # Load the base model
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=config.model_name,
        max_seq_length=config.max_seq_length,
        dtype=None,
        load_in_4bit=config.load_in_4bit,
    )
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
    print("✅ Model and tokenizer loaded successfully for training.")


training_args = TrainingArguments(
    # Batch settings
    per_device_train_batch_size=config.batch_size,
    gradient_accumulation_steps=config.gradient_accumulation,

    # Duration
    num_train_epochs=config.epochs,

    # Learning rate
    learning_rate=config.learning_rate,
    warmup_steps=config.warmup_steps,

    # Precision - auto-detect best for GPU
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),

    # Optimizer
    optim="adamw_8bit",
    weight_decay=0.01,

    # Logging & Checkpoints - Save more frequently to Drive for safety
    logging_steps=50,
    logging_dir=f"{config.output_dir}/logs",  # Save logs to Drive
    save_steps=100,   # Save every 100 steps to Drive (safer than 500)
    save_total_limit=5,  # Keep more checkpoints
    output_dir=config.output_dir,

    # Reproducibility
    seed=3407,
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=config.max_seq_length,
    args=training_args,
    packing=True, # Updated from False to True
)

print("🚀 Starting Vetta training...")
print(f"   Epochs: {config.epochs}")
print(f"   Effective batch: {config.batch_size * config.gradient_accumulation}")
print(f"   Precision: {'BF16' if training_args.bf16 else 'FP16'}")
print(f"\n⏱️  Expected time: ~45-60 minutes on T4 GPU\n")

stats = trainer.train()

print(f"\n✅ Training complete!")
print(f"📊 Final loss: {stats.training_loss:.4f}")
print(f"⏱️  Time: {stats.metrics['train_runtime'] / 60:.1f} minutes")

# Save training stats to Drive for persistence
stats_file = f"{config.output_dir}/training_stats.txt"
with open(stats_file, "w") as f:
    f.write(f"Training completed on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Final loss: {stats.training_loss:.4f}\n")
    f.write(f"Training runtime: {stats.metrics['train_runtime'] / 60:.1f} minutes\n")
    f.write(f"Training samples per second: {stats.metrics['train_samples_per_second']:.2f}\n")
    f.write(f"Training steps per second: {stats.metrics['train_steps_per_second']:.2f}\n")
    f.write(f"Epochs trained: {stats.metrics['epoch']:.2f}\n")
print(f"📄 Training stats saved to: {stats_file}")