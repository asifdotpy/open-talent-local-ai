#!/usr/bin/env python3
"""
Create comprehensive Granite 3.0 2B fine-tuning notebook for Google Colab.
Addresses missing YAML config and dataset upload requirements.
"""

import json

# Create notebook structure
notebook = {
    "cells": [
        # Title
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# 🚀 Granite 3.0 2B - Comprehensive OpenTalent Fine-Tuning (v4)\n\n",
                "**Dataset:** 2,075 examples (1,660 train / 415 val) | **Domains:** 8 | **Quality:** 0.875 avg\n\n",
                "**Goal:** Fine-tune Granite 3.0 2B on complete OpenTalent platform capabilities\n\n",
                "**Storage:** No Google Drive checkpoints - saves storage quota!",
            ],
        },
        # Install
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "%%capture\n",
                '!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"\n',
                '!pip install --no-deps "trl<0.9.0" peft accelerate bitsandbytes "xformers<0.0.27"\n',
                "!pip install huggingface_hub datasets pyyaml",
            ],
        },
        # HF Auth
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from huggingface_hub import login\n",
                "from google.colab import userdata\n\n",
                "try:\n",
                "    login(token=userdata.get('HF_TOKEN'))\n",
                "except:\n",
                "    login(token=input('HF Token: '))\n",
                "print('✅ Authenticated')",
            ],
        },
        # Load Config
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "import yaml\n\n",
                "# Use local temp storage - no Drive checkpoints to save storage\n",
                "config = {\n",
                "    'model': {'name': 'ibm-granite/granite-3.0-2b-instruct', 'max_seq_length': 2048, 'load_in_4bit': True},\n",
                "    'lora': {'r': 16, 'alpha': 16, 'dropout': 0.0, 'target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']},\n",
                "    'training': {'batch_size': 4, 'gradient_accumulation_steps': 2, 'num_epochs': 5, 'learning_rate': 2e-4, 'warmup_steps': 10, 'logging_steps': 50},\n",
                "    'dataset': {'repetitions': 1},\n",
                "    'directories': {'output_dir': '/content/training_output', 'lora_dir': '/content/lora_model'},\n",
                "    'huggingface': {'username': 'asifdotpy', 'version': 'v4', 'lora_repo': 'asifdotpy/vetta-granite-2b-lora-v4', 'dataset_repo': 'asifdotpy/OpenTalent-comprehensive-dataset'}\n",
                "}\n\n",
                "# Create directories\n",
                "os.makedirs(config['directories']['output_dir'], exist_ok=True)\n",
                "os.makedirs(config['directories']['lora_dir'], exist_ok=True)\n\n",
                "print(f\"✅ Config loaded: {config['huggingface']['lora_repo']}\")\n",
                "print(f\"📁 Output: {config['directories']['output_dir']} (local temp - no Drive checkpoints)\")",
            ],
        },
        # Upload Dataset
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 📊 Dataset Upload\n\n",
                "**Option 1:** Download from GitHub repo (automatic below)\n\n",
                "**Option 2:** Upload manually to `/content/` if files are local:\n",
                "- `llm_training_train.json` (1,660 examples)\n",
                "- `llm_training_validation.json` (415 examples)",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import json\n",
                "from datasets import Dataset, DatasetDict\n\n",
                "# Try to download from GitHub first\n",
                "train_file = '/content/llm_training_train.json'\n",
                "val_file = '/content/llm_training_validation.json'\n\n",
                "if not os.path.exists(train_file) or not os.path.exists(val_file):\n",
                "    print('📥 Downloading dataset from GitHub...')\n",
                "    !wget -q https://raw.githubusercontent.com/asifdotpy/open-talent-platform/main/notebooks/data/llm_training_train.json -O {train_file}\n",
                "    !wget -q https://raw.githubusercontent.com/asifdotpy/open-talent-platform/main/notebooks/data/llm_training_validation.json -O {val_file}\n",
                "    print('✅ Downloaded from GitHub')\n\n",
                "with open(train_file) as f: train_data = json.load(f)\n",
                "with open(val_file) as f: val_data = json.load(f)\n\n",
                "dataset_dict = DatasetDict({\n",
                "    'train': Dataset.from_list(train_data),\n",
                "    'validation': Dataset.from_list(val_data)\n",
                "})\n\n",
                "# Push to HF Hub\n",
                "try:\n",
                "    dataset_dict.push_to_hub(config['huggingface']['dataset_repo'], private=False)\n",
                "    print(f'✅ Dataset uploaded to HF Hub: {len(train_data)} train, {len(val_data)} val')\n",
                "except Exception as e:\n",
                "    print(f'⚠️ HF upload skipped (may already exist): {e}')\n",
                "    print(f'✅ Dataset loaded: {len(train_data)} train, {len(val_data)} val')",
            ],
        },
        # Format Dataset
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "def format_example(ex):\n",
                "    return {'text': f\"### Instruction:\\n{ex['instruction']}\\n\\n### Response:\\n{ex['response']}\"}\n\n",
                "train_dataset = dataset_dict['train'].map(format_example)\n",
                "val_dataset = dataset_dict['validation'].map(format_example)\n",
                "print(f'✅ Formatted: {len(train_dataset)} train, {len(val_dataset)} val')",
            ],
        },
        # Load Model
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from unsloth import FastLanguageModel\n",
                "import torch\n\n",
                "model, tokenizer = FastLanguageModel.from_pretrained(\n",
                "    model_name=config['model']['name'],\n",
                "    max_seq_length=config['model']['max_seq_length'],\n",
                "    dtype=None,\n",
                "    load_in_4bit=config['model']['load_in_4bit'],\n",
                ")\n",
                "print(f'✅ Model loaded | GPU: {torch.cuda.memory_allocated() / 1024**3:.2f} GB')",
            ],
        },
        # LoRA
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "model = FastLanguageModel.get_peft_model(\n",
                "    model, r=config['lora']['r'], target_modules=config['lora']['target_modules'],\n",
                "    lora_alpha=config['lora']['alpha'], lora_dropout=config['lora']['dropout'],\n",
                "    bias='none', use_gradient_checkpointing='unsloth', random_state=3407,\n",
                ")\n",
                "model.print_trainable_parameters()",
            ],
        },
        # Train
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from transformers import TrainingArguments\n",
                "from trl import SFTTrainer\n\n",
                "training_args = TrainingArguments(\n",
                "    per_device_train_batch_size=config['training']['batch_size'],\n",
                "    gradient_accumulation_steps=config['training']['gradient_accumulation_steps'],\n",
                "    num_train_epochs=config['training']['num_epochs'],\n",
                "    learning_rate=config['training']['learning_rate'],\n",
                "    warmup_steps=config['training']['warmup_steps'],\n",
                "    fp16=not torch.cuda.is_bf16_supported(),\n",
                "    bf16=torch.cuda.is_bf16_supported(),\n",
                "    optim='adamw_8bit',\n",
                "    weight_decay=0.01,\n",
                "    logging_steps=config['training']['logging_steps'],\n",
                "    save_strategy='no',  # No checkpointing - saves storage\n",
                "    output_dir=config['directories']['output_dir'],\n",
                "    seed=3407,\n",
                ")\n\n",
                "trainer = SFTTrainer(\n",
                "    model=model, tokenizer=tokenizer, train_dataset=train_dataset,\n",
                "    dataset_text_field='text', max_seq_length=config['model']['max_seq_length'],\n",
                "    args=training_args, packing=True,\n",
                ")\n\n",
                "print('🚀 Starting training...')\n",
                "print(f'⚡ No checkpoints - final model only (saves storage)')\n",
                "stats = trainer.train()\n",
                "print(f'\\n✅ Complete! Loss: {stats.training_loss:.4f}, Time: {stats.metrics[\"train_runtime\"] / 60:.1f}min')",
            ],
        },
        # Test
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "FastLanguageModel.for_inference(model)\n",
                "test_prompt = 'Generate a boolean search query for a senior Python developer.'\n",
                "inputs = tokenizer(f'### Instruction:\\n{test_prompt}\\n\\n### Response:\\n', return_tensors='pt').to('cuda')\n",
                "outputs = model.generate(**inputs, max_new_tokens=150, temperature=0.7)\n",
                "print(tokenizer.decode(outputs[0], skip_special_tokens=True).split('### Response:')[-1])",
            ],
        },
        # Save
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "lora_dir = config['directories']['lora_dir']\n",
                "model.save_pretrained(lora_dir)\n",
                "tokenizer.save_pretrained(lora_dir)\n",
                "print(f'✅ LoRA saved locally: {lora_dir}')\n",
                "print(f'📦 Size: {sum(os.path.getsize(os.path.join(lora_dir, f)) for f in os.listdir(lora_dir)) / 1024**2:.1f} MB')",
            ],
        },
        # Upload
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from huggingface_hub import HfApi\n",
                "api = HfApi()\n",
                "lora_repo = config['huggingface']['lora_repo']\n\n",
                "api.create_repo(lora_repo, exist_ok=True, private=False)\n",
                "api.upload_folder(folder_path=lora_dir, repo_id=lora_repo, repo_type='model',\n",
                "                 commit_message='Upload comprehensive OpenTalent platform LoRA v4')\n",
                "print(f'✅ Uploaded: https://huggingface.co/{lora_repo}')",
            ],
        },
        # Done
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## ✅ Training Complete!\n\n",
                "**Model:** https://huggingface.co/asifdotpy/vetta-granite-2b-lora-v4\n\n",
                "**Dataset:** https://huggingface.co/datasets/asifdotpy/OpenTalent-comprehensive-dataset",
            ],
        },
    ],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.12"},
        "colab": {"provenance": [], "gpuType": "T4", "machine_shape": "hm"},
        "accelerator": "GPU",
    },
    "nbformat": 4,
    "nbformat_minor": 0,
}

# Save notebook
output_path = (
    "/home/asif1/open-talent-platform/notebooks/granite_fine_tuning_v4_comprehensive.ipynb"
)
with open(output_path, "w") as f:
    json.dump(notebook, f, indent=2)

print(f"✅ Notebook created: {output_path}")
print(f"📊 Total cells: {len(notebook['cells'])}")
