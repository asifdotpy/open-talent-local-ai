"""
Model loader service for downloading and managing AI models.

Handles model downloads from Hugging Face, local caching, and
prerequisite validation for different model architectures.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional

from huggingface_hub import HfApi, snapshot_download

from ..config import settings
from ..models import model_registry

logger = logging.getLogger(__name__)


class ModelLoader:
    """Service for loading and managing AI models."""

    def __init__(self):
        self.hf_api = HfApi()
        self.download_tasks: dict[str, asyncio.Task] = {}

    async def download_model(self, model_name: str, force: bool = False) -> bool:
        """Download model from Hugging Face if not cached."""
        config = settings.get_model_config(model_name)
        if not config:
            logger.error(f"No configuration found for model: {model_name}")
            return False

        model_path = settings.model_cache_dir / model_name

        # Check if already downloaded
        if model_path.exists() and not force:
            logger.info(f"Model {model_name} already cached at {model_path}")
            return True

        # Check hardware compatibility before downloading
        compatibility = settings.validate_model_compatibility(model_name)
        if not compatibility["compatible"]:
            logger.error(
                f"Model {model_name} not compatible with current hardware: {compatibility['reason']}"
            )
            return False

        try:
            logger.info(f"Downloading model {model_name}...")

            # Create download task
            task = asyncio.create_task(self._download_model_async(model_name, model_path))
            self.download_tasks[model_name] = task

            # Wait for completion
            success = await task
            del self.download_tasks[model_name]

            if success:
                logger.info(f"Successfully downloaded model {model_name}")
                return True
            else:
                logger.error(f"Failed to download model {model_name}")
                return False

        except Exception as e:
            logger.error(f"Error downloading model {model_name}: {e}")
            return False

    async def _download_model_async(self, model_name: str, model_path: Path) -> bool:
        """Async model download implementation."""
        try:
            # Map model names to Hugging Face repo IDs
            repo_id = self._get_huggingface_repo_id(model_name)

            if not repo_id:
                logger.error(f"No Hugging Face repo mapping found for model: {model_name}")
                return False

            # Download with progress
            snapshot_download(
                repo_id=repo_id,
                local_dir=str(model_path),
                local_dir_use_symlinks=False,
                ignore_patterns=["*.md", "*.txt", "*.json"],  # Skip documentation
            )

            return True

        except Exception as e:
            logger.error(f"Download failed for {model_name}: {e}")
            return False

    def _get_huggingface_repo_id(self, model_name: str) -> Optional[str]:
        """Map model names to Hugging Face repository IDs."""
        # Granite models
        if model_name == "granite4:350m-h":
            return "ibm-granite/granite-3.1-2b-instruct"  # Using available Granite model
        elif model_name == "granite-interview-ft":
            return "ibm-granite/granite-3.1-2b-instruct"  # Base model for fine-tuning

        # Llama models
        elif model_name == "llama-2-7b-chat":
            return "meta-llama/Llama-2-7b-chat-hf"
        elif model_name == "llama-2-13b-chat":
            return "meta-llama/Llama-2-13b-chat-hf"
        elif model_name == "llama-2-70b-chat":
            return "meta-llama/Llama-2-70b-chat-hf"

        # Mistral models
        elif model_name == "mistral-7b-instruct":
            return "mistralai/Mistral-7B-Instruct-v0.1"
        elif model_name == "mistral-7b-instruct-v0.2":
            return "mistralai/Mistral-7B-Instruct-v0.2"

        # Custom fine-tuned models (would need actual repo IDs)
        elif model_name == "granite-interview-advanced":
            return "ibm-granite/granite-3.1-2b-instruct"
        elif model_name == "llama-interview-ft":
            return "meta-llama/Llama-2-7b-chat-hf"

        return None

    async def load_model(self, model_name: str) -> bool:
        """Load a model into memory."""
        # Ensure model is downloaded first
        if not await self.download_model(model_name):
            return False

        # Load using registry
        return model_registry.load_model(model_name)

    def unload_model(self, model_name: str):
        """Unload a model from memory."""
        model_registry.unload_model(model_name)

    def get_download_progress(self, model_name: str) -> Optional[dict[str, Any]]:
        """Get download progress for a model."""
        if model_name in self.download_tasks:
            task = self.download_tasks[model_name]
            return {
                "status": "downloading" if not task.done() else "completed",
                "done": task.done(),
                "exception": str(task.exception()) if task.done() and task.exception() else None,
            }
        return None

    def get_loaded_models(self) -> list[str]:
        """Get list of currently loaded models."""
        return model_registry.get_loaded_models()

    def get_cached_models(self) -> list[str]:
        """Get list of cached models on disk."""
        cached = []
        if settings.model_cache_dir.exists():
            for item in settings.model_cache_dir.iterdir():
                if item.is_dir():
                    cached.append(item.name)
        return cached

    def get_model_info(self, model_name: str) -> Optional[dict[str, Any]]:
        """Get comprehensive model information."""
        config = settings.get_model_config(model_name)
        if not config:
            return None

        info = {
            "name": model_name,
            "architecture": config.architecture,
            "size": config.size,
            "quantization": config.quantization,
            "max_context": config.max_context,
            "fine_tuning_supported": config.fine_tuning_supported,
            "min_memory": config.min_memory,
            "disk_space": config.disk_space,
            "base_model": config.base_model,
            "cached": model_name in self.get_cached_models(),
            "loaded": model_name in self.get_loaded_models(),
            "huggingface_repo": self._get_huggingface_repo_id(model_name),
            "training_config": config.get_training_config()
            if config.fine_tuning_supported
            else None,
            "data_requirements": config.get_data_requirements()
            if config.fine_tuning_supported
            else None,
        }

        # Add hardware compatibility
        compatibility = settings.validate_model_compatibility(model_name)
        info["hardware_compatible"] = compatibility["compatible"]
        if not compatibility["compatible"]:
            info["compatibility_reason"] = compatibility["reason"]

        # Add download progress if downloading
        progress = self.get_download_progress(model_name)
        if progress:
            info["download_progress"] = progress

        return info

    async def preload_models(self, model_names: list[str]):
        """Preload multiple models asynchronously."""
        tasks = []
        for model_name in model_names:
            task = asyncio.create_task(self.load_model(model_name))
            tasks.append(task)

        # Wait for all downloads to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Load models sequentially to avoid memory issues
        for model_name in model_names:
            try:
                model_registry.load_model(model_name)
                logger.info(f"Preloaded model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to preload model {model_name}: {e}")

    def cleanup_cache(self, keep_models: Optional[list[str]] = None):
        """Clean up model cache, keeping specified models."""
        if not settings.model_cache_dir.exists():
            return

        keep_models = keep_models or []
        removed_count = 0

        for item in settings.model_cache_dir.iterdir():
            if item.is_dir() and item.name not in keep_models:
                try:
                    import shutil

                    shutil.rmtree(item)
                    removed_count += 1
                    logger.info(f"Removed cached model: {item.name}")
                except Exception as e:
                    logger.error(f"Failed to remove {item.name}: {e}")

        logger.info(f"Cache cleanup completed. Removed {removed_count} models.")


# Global loader instance
model_loader = ModelLoader()
