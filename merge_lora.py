#!/usr/bin/env python3
"""
Merge LoRA adapters with base model for Vetta Granite fine-tuned model.

This script:
1. Loads the base Granite 3.0 2B Instruct model
2. Applies LoRA adapters from Hugging Face
3. Merges the weights into a full model
4. Saves the merged model locally
5. Optionally uploads to Hugging Face

Usage:
    python merge_lora.py [--upload]

Requirements:
    pip install torch transformers unsloth huggingface_hub
"""

import argparse
import os

from huggingface_hub import HfApi, login
from unsloth import FastLanguageModel


def main():
    parser = argparse.ArgumentParser(description="Merge LoRA adapters with base model")
    parser.add_argument("--upload", action="store_true", help="Upload merged model to Hugging Face")
    parser.add_argument("--hf-token", type=str, help="Hugging Face token (or set HF_TOKEN env var)")
    parser.add_argument(
        "--output-dir", type=str, default="./merged_model", help="Output directory for merged model"
    )
    args = parser.parse_args()

    print("🔄 Starting LoRA merge process...")

    # Configuration
    BASE_MODEL = "ibm-granite/granite-3.0-2b-instruct"
    LORA_REPO = "asifdotpy/vetta-granite-2b-lora-v3"
    MERGED_REPO = "asifdotpy/vetta-granite-2b-v3"
    VERSION = "v3"

    # Get HF token
    hf_token = args.hf_token or os.getenv("HF_TOKEN")
    if not hf_token and args.upload:
        raise ValueError("HF_TOKEN environment variable or --hf-token required for upload")

    if args.upload:
        login(token=hf_token)
        api = HfApi(token=hf_token)

    print(f"📥 Loading base model: {BASE_MODEL}")
    print(f"📥 Loading LoRA adapters: {LORA_REPO}")

    # Load model in full precision for merging
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL,
        max_seq_length=2048,
        load_in_4bit=False,  # Full precision for merging
        device_map="auto",  # Use GPU if available
    )

    # Apply LoRA adapters
    model = FastLanguageModel.get_peft_model(
        model,
        lora_path=LORA_REPO,
        r=16,
        lora_alpha=16,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )

    print("🔀 Merging LoRA weights...")
    # Merge and unload LoRA weights
    model = model.merge_and_unload()

    print(f"💾 Saving merged model to: {args.output_dir}")
    os.makedirs(args.output_dir, exist_ok=True)

    # Save model and tokenizer
    model.save_pretrained(args.output_dir, safe_serialization=True)  # Use safe serialization
    tokenizer.save_pretrained(args.output_dir)

    print("✅ Merged model saved successfully!")
    print(
        f"📏 Model size: {sum(os.path.getsize(os.path.join(args.output_dir, f)) for f in os.listdir(args.output_dir) if os.path.isfile(os.path.join(args.output_dir, f))) / (1024**3):.2f} GB"
    )

    # Upload to Hugging Face if requested
    if args.upload:
        print(f"📤 Uploading merged model to: {MERGED_REPO}")
        try:
            api.create_repo(MERGED_REPO, exist_ok=True, private=False)

            api.upload_folder(
                folder_path=args.output_dir,
                repo_id=MERGED_REPO,
                repo_type="model",
                commit_message=f"Upload merged Vetta Granite fine-tuned model {VERSION} (16-bit)",
            )

            print("✅ Merged model uploaded successfully!")
            print(f"👉 https://huggingface.co/{MERGED_REPO}")

            # Create model card
            model_card = f"""---
language: en
tags:
- granite
- fine-tuned
- interview
- ai-interviewer
- vetta
- merged
license: apache-2.0
---

# Vetta Granite Merged Model {VERSION}

This repository contains the full merged Vetta AI interviewer model, fine-tuned on Granite 3.0 2B Instruct with LoRA weights integrated.

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(
    "asifdotpy/vetta-granite-2b-{VERSION}",
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("asifdotpy/vetta-granite-2b-{VERSION}")

# Generate
inputs = tokenizer("Begin a technical interview...", return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=256, temperature=0.7)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## Training Details
- Base Model: ibm-granite/granite-3.0-2b-instruct
- Training Method: LoRA fine-tuning with merged weights
- Dataset: Custom interview conversation dataset
- Training Steps: 2250
- Final Loss: 0.1124
- Precision: 16-bit

## Intended Use
This model is designed to conduct professional AI-powered interviews, providing empathetic and technically accurate responses.
"""

            api.upload_file(
                path_or_fileobj=model_card.encode(),
                path_in_repo="README.md",
                repo_id=MERGED_REPO,
                repo_type="model",
                commit_message="Add model card and usage instructions",
            )
            print("✅ Model card uploaded")

        except Exception as e:
            print(f"❌ Error uploading merged model: {e}")
            return

    print("\n🎉 Merge process complete!")
    print(f"Merged model saved locally at: {args.output_dir}")
    if args.upload:
        print(f"Merged model uploaded to: https://huggingface.co/{MERGED_REPO}")
    else:
        print("To upload manually, run: python merge_lora.py --upload")


if __name__ == "__main__":
    main()
