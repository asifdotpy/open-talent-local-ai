"""
Training service for fine-tuning AI models.

Handles LoRA/QLoRA fine-tuning with prerequisite validation,
data preparation, and training orchestration for different model architectures.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
import wandb

from ..config import settings
from ..models import model_registry

logger = logging.getLogger(__name__)

class TrainingService:
    """Service for fine-tuning AI models."""

    def __init__(self):
        self.active_trainings: Dict[str, Dict[str, Any]] = {}

    def validate_training_prerequisites(
        self,
        model_name: str,
        dataset_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate all prerequisites for training a model."""

        config = settings.get_model_config(model_name)
        if not config:
            return {
                'valid': False,
                'reason': f'No configuration found for model: {model_name}'
            }

        if not config.fine_tuning_supported:
            return {
                'valid': False,
                'reason': f'Model {model_name} does not support fine-tuning'
            }

        # Check hardware requirements
        compatibility = settings.validate_model_compatibility(model_name)
        if not compatibility['compatible']:
            return {
                'valid': False,
                'reason': f'Hardware not compatible: {compatibility["reason"]}'
            }

        # Check dataset requirements
        dataset_path = dataset_path or config.dataset
        if not dataset_path:
            return {
                'valid': False,
                'reason': 'No dataset specified for training'
            }

        dataset_file = Path(settings.training_data_dir) / f"{dataset_path}.json"
        if not dataset_file.exists():
            return {
                'valid': False,
                'reason': f'Dataset file not found: {dataset_file}'
            }

        # Validate dataset format and size
        try:
            with open(dataset_file, 'r') as f:
                data = json.load(f)

            if not isinstance(data, list) or len(data) < 100:
                return {
                    'valid': False,
                    'reason': f'Dataset must contain at least 100 samples, found {len(data) if isinstance(data, list) else 0}'
                }

            # Check data format
            sample = data[0]
            required_fields = ['instruction', 'input', 'output']
            if not all(field in sample for field in required_fields):
                return {
                    'valid': False,
                    'reason': f'Dataset must contain fields: {required_fields}'
                }

        except (json.JSONDecodeError, FileNotFoundError) as e:
            return {
                'valid': False,
                'reason': f'Dataset validation failed: {e}'
            }

        # Check available disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(settings.output_dir.parent)
            free_gb = free / (1024**3)

            # Estimate space needed (model size * 2 for checkpoints)
            model_size_gb = self._estimate_model_size_gb(config.size)
            required_space = model_size_gb * 2

            if free_gb < required_space:
                return {
                    'valid': False,
                    'reason': f'Insufficient disk space: {free_gb:.1f}GB available, {required_space:.1f}GB required'
                }

        except Exception as e:
            logger.warning(f"Could not check disk space: {e}")

        return {
            'valid': True,
            'model_config': config,
            'dataset_path': str(dataset_file),
            'estimated_duration': self._estimate_training_time(config.size, len(data))
        }

    def _estimate_model_size_gb(self, model_size: str) -> float:
        """Estimate model size in GB."""
        size_map = {
            '350m': 0.7,
            '7b': 14,
            '13b': 26,
            '30b': 60,
            '65b': 130,
            '70b': 140
        }
        return size_map.get(model_size.lower(), 1.0)

    def _estimate_training_time(self, model_size: str, dataset_size: int) -> str:
        """Estimate training time based on model size and dataset."""
        # Rough estimates based on A100 GPU
        base_time_per_sample = {
            '350m': 0.1,  # seconds per sample
            '7b': 0.5,
            '13b': 1.0,
            '30b': 2.0,
            '65b': 4.0,
            '70b': 4.5
        }

        time_per_sample = base_time_per_sample.get(model_size.lower(), 0.1)
        total_seconds = time_per_sample * dataset_size

        # Convert to hours
        hours = total_seconds / 3600
        if hours < 1:
            return f"{total_seconds/60:.0f} minutes"
        elif hours < 24:
            return f"{hours:.1f} hours"
        else:
            return f"{hours/24:.1f} days"

    async def start_training(
        self,
        model_name: str,
        dataset_path: Optional[str] = None,
        training_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start fine-tuning a model."""

        # Validate prerequisites
        validation = self.validate_training_prerequisites(model_name, dataset_path)
        if not validation['valid']:
            return {
                'success': False,
                'error': validation['reason']
            }

        config = validation['model_config']
        dataset_file = validation['dataset_path']

        # Generate training ID
        training_id = f"{model_name}_{config.dataset}_{len(self.active_trainings)}"

        # Set up training configuration
        train_config = self._get_default_training_config(config, training_config or {})

        # Start training in background
        try:
            import asyncio
            training_task = asyncio.create_task(
                self._run_training(training_id, model_name, dataset_file, train_config)
            )

            self.active_trainings[training_id] = {
                'task': training_task,
                'model_name': model_name,
                'status': 'starting',
                'config': train_config,
                'start_time': None
            }

            return {
                'success': True,
                'training_id': training_id,
                'estimated_duration': validation['estimated_duration'],
                'status': 'starting'
            }

        except Exception as e:
            logger.error(f"Failed to start training: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_default_training_config(
        self,
        config: Any,
        user_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get default training configuration."""

        defaults = {
            'output_dir': str(settings.output_dir / f"{config.name}_ft"),
            'num_train_epochs': 3,
            'per_device_train_batch_size': 4,
            'gradient_accumulation_steps': 2,
            'learning_rate': 2e-4,
            'weight_decay': 0.01,
            'warmup_steps': 100,
            'logging_steps': 10,
            'save_steps': 500,
            'evaluation_strategy': 'steps',
            'eval_steps': 500,
            'load_best_model_at_end': True,
            'metric_for_best_model': 'loss',
            'greater_is_better': False,
            'fp16': True,
            'report_to': 'wandb' if settings.wandb_project else 'none'
        }

        # Apply model-specific training config
        model_training_config = config.get_training_config()
        defaults.update(model_training_config)

        # Apply user overrides
        defaults.update(user_config)

        return defaults

    async def _run_training(
        self,
        training_id: str,
        model_name: str,
        dataset_file: str,
        train_config: Dict[str, Any]
    ):
        """Run the actual training process."""

        try:
            self.active_trainings[training_id]['status'] = 'loading_data'
            logger.info(f"Starting training {training_id}")

            # Load dataset
            with open(dataset_file, 'r') as f:
                data = json.load(f)

            # Prepare dataset
            dataset = Dataset.from_list(data)
            dataset = self._prepare_dataset(dataset, model_name)

            # Load model and tokenizer
            self.active_trainings[training_id]['status'] = 'loading_model'

            config = settings.get_model_config(model_name)
            model_path = settings.model_cache_dir / model_name

            tokenizer = AutoTokenizer.from_pretrained(model_path)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map='auto',
                torch_dtype=torch.float16
            )

            # Apply LoRA/QLoRA
            self.active_trainings[training_id]['status'] = 'configuring_lora'

            lora_config = LoraConfig(**config.get_training_config())
            model = prepare_model_for_kbit_training(model)
            model = get_peft_model(model, lora_config)

            # Set up training arguments
            training_args = TrainingArguments(**train_config)

            # Initialize wandb if configured
            if settings.wandb_project:
                wandb.init(
                    project=settings.wandb_project,
                    name=training_id,
                    config=train_config
                )

            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=dataset,
                data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
            )

            # Start training
            self.active_trainings[training_id]['status'] = 'training'
            self.active_trainings[training_id]['start_time'] = torch.cuda.Event(enable_timing=True)
            self.active_trainings[training_id]['start_time'].record()

            trainer.train()

            # Save model
            self.active_trainings[training_id]['status'] = 'saving'
            trainer.save_model()
            tokenizer.save_pretrained(train_config['output_dir'])

            # Mark as completed
            self.active_trainings[training_id]['status'] = 'completed'
            logger.info(f"Training {training_id} completed successfully")

        except Exception as e:
            logger.error(f"Training {training_id} failed: {e}")
            self.active_trainings[training_id]['status'] = 'failed'
            self.active_trainings[training_id]['error'] = str(e)

    def _prepare_dataset(self, dataset: Dataset, model_name: str) -> Dataset:
        """Prepare dataset for training."""

        def format_instruction(example):
            """Format instruction-response pairs."""
            if 'input' in example and example['input'].strip():
                instruction = f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n{example['output']}"
            else:
                instruction = f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['output']}"

            return {'text': instruction}

        return dataset.map(format_instruction)

    def get_training_status(self, training_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a training job."""
        if training_id not in self.active_trainings:
            return None

        training = self.active_trainings[training_id]
        status = {
            'training_id': training_id,
            'model_name': training['model_name'],
            'status': training['status'],
            'config': training['config']
        }

        # Add timing information if available
        if training.get('start_time') and torch.cuda.is_available():
            current_time = torch.cuda.Event(enable_timing=True)
            current_time.record()
            elapsed_ms = training['start_time'].elapsed_time(current_time)
            status['elapsed_time_seconds'] = elapsed_ms / 1000

        # Add error information if failed
        if training['status'] == 'failed':
            status['error'] = training.get('error')

        return status

    def list_active_trainings(self) -> List[Dict[str, Any]]:
        """List all active training jobs."""
        return [
            self.get_training_status(training_id)
            for training_id in self.active_trainings.keys()
        ]

    def cancel_training(self, training_id: str) -> bool:
        """Cancel a training job."""
        if training_id not in self.active_trainings:
            return False

        training = self.active_trainings[training_id]
        if training['status'] in ['completed', 'failed']:
            return False

        # Cancel the task
        training['task'].cancel()
        training['status'] = 'cancelled'

        logger.info(f"Training {training_id} cancelled")
        return True

    def cleanup_completed_trainings(self):
        """Clean up completed training records."""
        to_remove = []
        for training_id, training in self.active_trainings.items():
            if training['status'] in ['completed', 'failed', 'cancelled']:
                to_remove.append(training_id)

        for training_id in to_remove:
            del self.active_trainings[training_id]

        logger.info(f"Cleaned up {len(to_remove)} completed trainings")

# Global training service instance
training_service = TrainingService()