"""
Configuration settings for Granite Interview Service.

Handles model configurations, training prerequisites, and service settings
for multiple model architectures (Granite, Llama, Mistral, etc.).
"""

import os
from pathlib import Path
from typing import Any

import yaml


class ModelConfig:
    """Configuration for a specific model."""

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.architecture = config.get("architecture", "unknown")
        self.size = config.get("size", "unknown")
        self.quantization = config.get("quantization", "4bit")
        self.max_context = config.get("max_context", 2048)
        self.base_model = config.get("base_model")

        # Fine-tuning configuration
        ft_config = config.get("fine_tuning", {})
        self.fine_tuning_supported = ft_config.get("supported", True)
        self.fine_tuning_technique = ft_config.get("technique", "lora")
        self.lora_rank = ft_config.get("rank", 16)
        self.dataset = ft_config.get("dataset")

        # Hardware requirements
        self.min_memory = self._get_memory_requirement()
        self.disk_space = self._get_disk_requirement()

    def _get_memory_requirement(self) -> str:
        """Get minimum memory requirement based on model size."""
        size_map = {"350m": "4GB", "7b": "14GB", "13b": "24GB", "30b": "48GB", "65b": "96GB"}
        return size_map.get(self.size.lower(), "8GB")

    def _get_disk_requirement(self) -> str:
        """Get disk space requirement based on model size."""
        size_map = {"350m": "700MB", "7b": "14GB", "13b": "26GB", "30b": "60GB", "65b": "130GB"}
        return size_map.get(self.size.lower(), "1GB")

    def get_training_config(self) -> dict[str, Any]:
        """Get training configuration for this model."""
        if not self.fine_tuning_supported:
            return {}

        base_config = {
            "technique": self.fine_tuning_technique,
            "rank": self.lora_rank,
            "target_modules": self._get_target_modules(),
            "lora_dropout": 0.05,
            "bias": "none",
            "task_type": "CAUSAL_LM",
        }

        # Architecture-specific configurations
        if self.architecture.lower() == "granite":
            base_config.update(
                {
                    "lora_alpha": self.lora_rank * 2,
                    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
                }
            )
        elif self.architecture.lower() in ["llama", "mistral"]:
            base_config.update(
                {
                    "lora_alpha": self.lora_rank * 2,
                    "target_modules": [
                        "q_proj",
                        "k_proj",
                        "v_proj",
                        "o_proj",
                        "gate_proj",
                        "up_proj",
                        "down_proj",
                    ],
                }
            )
            # QLoRA for larger models
            if self.size in ["7b", "13b", "30b", "65b"]:
                base_config.update(
                    {
                        "load_in_4bit": True,
                        "bnb_4bit_compute_dtype": "torch.float16",
                        "bnb_4bit_use_double_quant": True,
                        "bnb_4bit_quant_type": "nf4",
                    }
                )

        return base_config

    def _get_target_modules(self) -> list[str]:
        """Get target modules for LoRA based on architecture."""
        if self.architecture.lower() == "granite":
            return ["q_proj", "k_proj", "v_proj", "o_proj"]
        elif self.architecture.lower() in ["llama", "mistral"]:
            return ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        else:
            # Default for unknown architectures
            return ["q_proj", "k_proj", "v_proj", "o_proj"]

    def get_data_requirements(self) -> dict[str, Any]:
        """Get data requirements for training this model."""
        base_requirements = {
            "format": "instruction-response pairs",
            "min_samples": 1000,
            "max_length": self.max_context,
            "validation_split": 0.1,
            "test_split": 0.1,
        }

        # Size-based requirements
        if self.size == "350m":
            base_requirements.update({"min_samples": 1000, "recommended_samples": 5000})
        elif self.size in ["7b", "13b"]:
            base_requirements.update({"min_samples": 5000, "recommended_samples": 10000})
        elif self.size in ["30b", "65b"]:
            base_requirements.update({"min_samples": 10000, "recommended_samples": 25000})

        return base_requirements


class Settings:
    """Main configuration settings for the service."""

    def __init__(self):
        # Service settings
        self.host = os.environ.get("HOST", "0.0.0.0")  # nosec B104
        self.port = int(os.environ.get("PORT", 8005))
        self.workers = int(os.environ.get("WORKERS", 2))
        self.debug = os.environ.get("DEBUG", "false").lower() == "true"

        # Model settings
        self.default_model = os.environ.get("DEFAULT_MODEL", "granite4:350m-h")
        self.model_cache_dir = Path(os.environ.get("MODEL_CACHE_DIR", "/app/models"))
        self.max_model_memory = float(os.environ.get("MAX_MODEL_MEMORY", 0.8))

        # Training settings
        self.training_data_dir = Path(os.environ.get("TRAINING_DATA_DIR", "/app/data"))
        self.output_dir = Path(os.environ.get("OUTPUT_DIR", "/app/models/fine-tuned"))
        self.wandb_project = os.environ.get("WANDB_PROJECT", "open-talent-granite")

        # Load model configurations
        self.models = self._load_model_configs()

        # Create directories
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        self.training_data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_model_configs(self) -> dict[str, ModelConfig]:
        """Load model configurations from YAML file."""
        config_file = Path(__file__).parent / "models.yaml"

        if not config_file.exists():
            # Default configurations
            default_configs = self._get_default_configs()
            self._save_default_configs(config_file, default_configs)
        else:
            with open(config_file) as f:
                configs = yaml.safe_load(f)

        # Convert to ModelConfig objects
        model_configs = {}
        for name, config in configs.get("models", {}).items():
            model_configs[name] = ModelConfig(name, config)

        return model_configs

    def _get_default_configs(self) -> dict[str, Any]:
        """Get default model configurations."""
        return {
            "models": {
                "granite4:350m-h": {
                    "architecture": "granite",
                    "size": "350m",
                    "quantization": "4bit",
                    "max_context": 2048,
                    "fine_tuning": {"supported": True, "technique": "lora", "rank": 16},
                },
                "llama-2-7b-chat": {
                    "architecture": "llama",
                    "size": "7b",
                    "quantization": "4bit",
                    "max_context": 4096,
                    "fine_tuning": {"supported": True, "technique": "qlora", "rank": 64},
                },
                "mistral-7b-instruct": {
                    "architecture": "mistral",
                    "size": "7b",
                    "quantization": "4bit",
                    "max_context": 4096,
                    "fine_tuning": {"supported": True, "technique": "qlora", "rank": 64},
                },
                "granite-interview-ft": {
                    "architecture": "granite",
                    "size": "350m",
                    "quantization": "4bit",
                    "max_context": 2048,
                    "base_model": "granite4:350m-h",
                    "fine_tuning": {
                        "supported": False,
                        "technique": "lora",
                        "rank": 16,
                        "dataset": "interview_v1",
                    },
                },
            }
        }

    def _save_default_configs(self, config_file: Path, configs: dict[str, Any]):
        """Save default configurations to file."""
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w") as f:
            yaml.dump(configs, f, default_flow_style=False)

    def get_model_config(self, model_name: str) -> ModelConfig | None:
        """Get configuration for a specific model."""
        return self.models.get(model_name)

    def get_supported_architectures(self) -> list[str]:
        """Get list of supported model architectures."""
        return list({config.architecture for config in self.models.values()})

    def validate_model_compatibility(self, model_name: str) -> dict[str, Any]:
        """Validate if a model can run on current hardware."""
        config = self.get_model_config(model_name)
        if not config:
            return {"compatible": False, "reason": "Model not configured"}

        # Check memory requirements
        try:
            import torch

            if torch.cuda.is_available():
                device_props = torch.cuda.get_device_properties(0)
                available_memory = device_props.total_memory / 1024**3  # GB

                min_memory_gb = float(config.min_memory.replace("GB", ""))
                if available_memory < min_memory_gb:
                    return {
                        "compatible": False,
                        "reason": f"Insufficient GPU memory: {available_memory:.1f}GB available, {min_memory_gb}GB required",
                    }
            else:
                # CPU-only system
                if config.size not in ["350m"]:
                    return {"compatible": False, "reason": "Large models require GPU acceleration"}
        except ImportError:
            return {"compatible": False, "reason": "PyTorch not available"}

        return {"compatible": True}


# Global settings instance
settings = Settings()
