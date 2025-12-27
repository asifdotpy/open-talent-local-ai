"""
Constants for Granite Interview Service.
"""

# Hardware requirements
MEMORY_REQUIREMENT_MAP = {"350m": "4GB", "7b": "14GB", "13b": "24GB", "30b": "48GB", "65b": "96GB"}

DISK_REQUIREMENT_MAP = {"350m": "700MB", "7b": "14GB", "13b": "26GB", "30b": "60GB", "65b": "130GB"}

# Training defaults
DEFAULT_TRAINING_CONFIG = {
    "num_train_epochs": 3,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 2,
    "learning_rate": 2e-4,
    "weight_decay": 0.01,
    "warmup_steps": 100,
    "logging_steps": 10,
    "save_steps": 500,
    "evaluation_strategy": "steps",
    "eval_steps": 500,
    "load_best_model_at_end": True,
    "metric_for_best_model": "loss",
    "greater_is_better": False,
    "fp16": True,
}

# Model mapping (HuggingFace)
HG_REPO_MAP = {
    "granite4:350m-h": "ibm-granite/granite-3.1-2b-instruct",
    "granite-interview-ft": "ibm-granite/granite-3.1-2b-instruct",
    "llama-2-7b-chat": "meta-llama/Llama-2-7b-chat-hf",
    "llama-2-13b-chat": "meta-llama/Llama-2-13b-chat-hf",
    "llama-2-70b-chat": "meta-llama/Llama-2-70b-chat-hf",
    "mistral-7b-instruct": "mistralai/Mistral-7B-Instruct-v0.1",
    "mistral-7b-instruct-v0.2": "mistralai/Mistral-7B-Instruct-v0.2",
}

# Training constants
MIN_DATASET_SAMPLES = 100
GB_TO_BYTES = 1024**3
DISK_SPACE_MULTIPLIER = 2
