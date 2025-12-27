# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL 2: Configuration                                                    ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

from dataclasses import dataclass


@dataclass
class Config:
    """Training configuration."""

    # Model
    model_name: str = "ibm-granite/granite-3.0-2b-instruct"
    max_seq_length: int = 2048
    load_in_4bit: bool = True

    # LoRA
    lora_r: int = 16
    lora_alpha: int = 16
    lora_dropout: float = 0
    target_modules: tuple = (
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    )

    # Training - REDUCED for better dataset
    batch_size: int = 4  # Updated from 2 to 4
    gradient_accumulation: int = 2  # Updated from 4 to 2
    epochs: int = 5  # Changed from 1 to 5
    learning_rate: float = 2e-4
    warmup_steps: int = 10

    # Output - Use Google Drive for persistence
    output_dir: str = "/content/drive/MyDrive/open-talent-vetta/checkpoints"
    models_dir: str = "/content/drive/MyDrive/open-talent-vetta/models"

    # Data
    data_repetitions: int = 10  # Updated to 10


config = Config()
print(f"🎯 Model: {config.model_name}")
print(f"📦 Output: {config.output_dir}")
print(
    f"⚡ Batch: {config.batch_size} × {config.gradient_accumulation} = {config.batch_size * config.gradient_accumulation} effective"
)
print(f"📚 Epochs: {config.epochs} (optimized for {config.data_repetitions}× dataset)")
