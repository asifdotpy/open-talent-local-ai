"""
Model registry for managing different AI model architectures.

Supports Granite, Llama, Mistral, and other transformer models with
proper initialization, loading, and management.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

import torch
from peft import PeftConfig, PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)

from ..config import ModelConfig, settings

logger = logging.getLogger(__name__)


class BaseModelHandler(ABC):
    """Abstract base class for model handlers."""

    def __init__(self, model_name: str, config: ModelConfig):
        self.model_name = model_name
        self.config = config
        self.model = None
        self.tokenizer = None
        self.pipeline = None

    @abstractmethod
    def load_model(self) -> bool:
        """Load the model and tokenizer."""
        pass

    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response for the given prompt."""
        pass

    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        """Get model information and capabilities."""
        pass

    def unload_model(self):
        """Unload model from memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
        torch.cuda.empty_cache()


class GraniteModelHandler(BaseModelHandler):
    """Handler for Granite models."""

    def load_model(self) -> bool:
        """Load Granite model with appropriate quantization."""
        try:
            model_path = settings.model_cache_dir / self.model_name

            # Quantization config for Granite
            if self.config.quantization == "4bit":
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
            else:
                bnb_config = None

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16,
            )

            # Check if it's a fine-tuned model
            if self.config.base_model:
                peft_config = PeftConfig.from_pretrained(model_path)
                self.model = PeftModel.from_pretrained(self.model, model_path, config=peft_config)

            # Create pipeline
            self.pipeline = pipeline(
                "text-generation", model=self.model, tokenizer=self.tokenizer, device_map="auto"
            )

            logger.info(f"Successfully loaded Granite model: {self.model_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to load Granite model {self.model_name}: {e}")
            return False

    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Granite model."""
        if not self.pipeline:
            raise RuntimeError("Model not loaded")

        # Default parameters for Granite
        generation_kwargs = {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "do_sample": True,
            "pad_token_id": self.tokenizer.eos_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            **kwargs,
        }

        try:
            outputs = self.pipeline(prompt, **generation_kwargs)
            response = outputs[0]["generated_text"][len(prompt) :].strip()
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""

    def get_model_info(self) -> dict[str, Any]:
        """Get Granite model information."""
        return {
            "architecture": "Granite",
            "size": self.config.size,
            "quantization": self.config.quantization,
            "max_context": self.config.max_context,
            "fine_tuned": self.config.base_model is not None,
            "capabilities": ["text_generation", "question_answering", "interview_intelligence"],
        }


class LlamaModelHandler(BaseModelHandler):
    """Handler for Llama models."""

    def load_model(self) -> bool:
        """Load Llama model with QLoRA support."""
        try:
            model_path = settings.model_cache_dir / self.model_name

            # QLoRA config for larger Llama models
            if self.config.size in ["7b", "13b", "30b", "70b"]:
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
            else:
                bnb_config = None

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=bnb_config,
                device_map="auto",
                torch_dtype=torch.float16,
            )

            # Check for fine-tuned adapters
            if self.config.base_model:
                peft_config = PeftConfig.from_pretrained(model_path)
                self.model = PeftModel.from_pretrained(self.model, model_path, config=peft_config)

            # Create pipeline
            self.pipeline = pipeline(
                "text-generation", model=self.model, tokenizer=self.tokenizer, device_map="auto"
            )

            logger.info(f"Successfully loaded Llama model: {self.model_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to load Llama model {self.model_name}: {e}")
            return False

    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Llama model."""
        if not self.pipeline:
            raise RuntimeError("Model not loaded")

        # Format prompt for chat models
        if "chat" in self.model_name.lower():
            formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        else:
            formatted_prompt = prompt

        generation_kwargs = {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "do_sample": True,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            **kwargs,
        }

        try:
            outputs = self.pipeline(formatted_prompt, **generation_kwargs)
            response = outputs[0]["generated_text"][len(formatted_prompt) :].strip()
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""

    def get_model_info(self) -> dict[str, Any]:
        """Get Llama model information."""
        return {
            "architecture": "Llama",
            "size": self.config.size,
            "quantization": self.config.quantization,
            "max_context": self.config.max_context,
            "fine_tuned": self.config.base_model is not None,
            "capabilities": [
                "text_generation",
                "question_answering",
                "interview_intelligence",
                "chat",
            ],
        }


class MistralModelHandler(BaseModelHandler):
    """Handler for Mistral models."""

    def load_model(self) -> bool:
        """Load Mistral model with appropriate configuration."""
        try:
            model_path = settings.model_cache_dir / self.model_name

            # Quantization config
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
            )

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=bnb_config,
                device_map="auto",
                torch_dtype=torch.float16,
            )

            # Check for fine-tuned adapters
            if self.config.base_model:
                peft_config = PeftConfig.from_pretrained(model_path)
                self.model = PeftModel.from_pretrained(self.model, model_path, config=peft_config)

            # Create pipeline
            self.pipeline = pipeline(
                "text-generation", model=self.model, tokenizer=self.tokenizer, device_map="auto"
            )

            logger.info(f"Successfully loaded Mistral model: {self.model_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to load Mistral model {self.model_name}: {e}")
            return False

    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Mistral model."""
        if not self.pipeline:
            raise RuntimeError("Model not loaded")

        # Format prompt for instruction models
        if "instruct" in self.model_name.lower():
            formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        else:
            formatted_prompt = prompt

        generation_kwargs = {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "do_sample": True,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            **kwargs,
        }

        try:
            outputs = self.pipeline(formatted_prompt, **generation_kwargs)
            response = outputs[0]["generated_text"][len(formatted_prompt) :].strip()
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""

    def get_model_info(self) -> dict[str, Any]:
        """Get Mistral model information."""
        return {
            "architecture": "Mistral",
            "size": self.config.size,
            "quantization": self.config.quantization,
            "max_context": self.config.max_context,
            "fine_tuned": self.config.base_model is not None,
            "capabilities": [
                "text_generation",
                "question_answering",
                "interview_intelligence",
                "instruction_following",
            ],
        }


class ModelRegistry:
    """Registry for managing different model handlers."""

    def __init__(self):
        self.handlers: dict[str, type[BaseModelHandler]] = {
            "granite": GraniteModelHandler,
            "llama": LlamaModelHandler,
            "mistral": MistralModelHandler,
        }
        self.loaded_models: dict[str, BaseModelHandler] = {}

    def get_handler_class(self, architecture: str) -> Optional[type[BaseModelHandler]]:
        """Get handler class for architecture."""
        return self.handlers.get(architecture.lower())

    def load_model(self, model_name: str) -> bool:
        """Load a model by name."""
        config = settings.get_model_config(model_name)
        if not config:
            logger.error(f"No configuration found for model: {model_name}")
            return False

        # Check hardware compatibility
        compatibility = settings.validate_model_compatibility(model_name)
        if not compatibility["compatible"]:
            logger.error(f"Model {model_name} not compatible: {compatibility['reason']}")
            return False

        # Get handler class
        handler_class = self.get_handler_class(config.architecture)
        if not handler_class:
            logger.error(f"No handler available for architecture: {config.architecture}")
            return False

        # Create and load handler
        handler = handler_class(model_name, config)
        if handler.load_model():
            self.loaded_models[model_name] = handler
            logger.info(f"Successfully loaded model: {model_name}")
            return True
        else:
            logger.error(f"Failed to load model: {model_name}")
            return False

    def unload_model(self, model_name: str):
        """Unload a model by name."""
        if model_name in self.loaded_models:
            self.loaded_models[model_name].unload_model()
            del self.loaded_models[model_name]
            logger.info(f"Unloaded model: {model_name}")

    def get_loaded_models(self) -> list[str]:
        """Get list of currently loaded models."""
        return list(self.loaded_models.keys())

    def get_model_handler(self, model_name: str) -> Optional[BaseModelHandler]:
        """Get handler for a loaded model."""
        return self.loaded_models.get(model_name)

    def generate_response(self, model_name: str, prompt: str, **kwargs) -> str:
        """Generate response using specified model."""
        handler = self.get_model_handler(model_name)
        if not handler:
            raise ValueError(f"Model {model_name} not loaded")

        return handler.generate_response(prompt, **kwargs)

    def get_model_info(self, model_name: str) -> Optional[dict[str, Any]]:
        """Get information about a model."""
        handler = self.get_model_handler(model_name)
        if handler:
            return handler.get_model_info()

        # Return config info if not loaded
        config = settings.get_model_config(model_name)
        if config:
            return {
                "architecture": config.architecture,
                "size": config.size,
                "quantization": config.quantization,
                "max_context": config.max_context,
                "fine_tuned": config.base_model is not None,
                "loaded": False,
            }

        return None


# Global registry instance
model_registry = ModelRegistry()
