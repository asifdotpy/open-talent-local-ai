#!/usr/bin/env python3
"""
Convert Vetta Granite merged model to GGUF format for Ollama deployment
"""

import os
import sys

import torch
from huggingface_hub import HfApi, login
from transformers import AutoModelForCausalLM, AutoTokenizer


def convert_to_gguf():
    """Convert the merged model to GGUF format"""

    # Configuration
    HF_USERNAME = "asifdotpy"
    MERGED_REPO = f"{HF_USERNAME}/vetta-granite-2b-v3"
    GGUF_REPO = f"{HF_USERNAME}/vetta-granite-2b-gguf-v3"

    print("🔄 Starting GGUF conversion process...")

    # Login to Hugging Face
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("❌ HF_TOKEN environment variable not set")
        sys.exit(1)

    login(token=hf_token)
    api = HfApi(token=hf_token)
    print("✅ Logged in to Hugging Face")

    # Load merged model
    print(f"📥 Loading merged model from: {MERGED_REPO}")
    try:
        model = AutoModelForCausalLM.from_pretrained(
            MERGED_REPO, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True
        )
        tokenizer = AutoTokenizer.from_pretrained(MERGED_REPO)
        print("✅ Merged model loaded")
    except Exception as e:
        print(f"❌ Failed to load merged model: {e}")
        sys.exit(1)

    # For GGUF conversion, we'll use llama.cpp or similar
    # Since we don't have unsloth locally, let's use transformers to save in a compatible format
    # and then use llama.cpp for GGUF conversion

    print("🔄 Converting to GGUF format...")

    # Save model in a format that llama.cpp can convert
    temp_dir = "/tmp/vetta-granite-gguf"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Save tokenizer and config
        tokenizer.save_pretrained(temp_dir)
        model.config.save_pretrained(temp_dir)

        # Save model weights (this will be large)
        model.save_pretrained(temp_dir, safe_serialization=True)
        print("✅ Model saved to temporary directory")
    except Exception as e:
        print(f"❌ Failed to save model: {e}")
        sys.exit(1)

    # Use llama.cpp to convert to GGUF
    print("🔄 Converting to GGUF using llama.cpp...")

    # First, convert to GGML format, then to GGUF
    import subprocess

    try:
        # Convert pytorch model to ggml
        convert_cmd = [
            "python",
            "-m",
            "llama_cpp.convert",
            "--model",
            temp_dir,
            "--outtype",
            "f16",
            "--outfile",
            f"{temp_dir}/vetta-granite-f16.gguf",
        ]

        result = subprocess.run(convert_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ GGUF conversion failed: {result.stderr}")
            sys.exit(1)

        print("✅ GGUF conversion completed")

        # Quantize to Q4_K_M
        quantize_cmd = [
            "llama-quantize",
            f"{temp_dir}/vetta-granite-f16.gguf",
            f"{temp_dir}/vetta-granite-q4_k_m.gguf",
            "q4_k_m",
        ]

        result = subprocess.run(quantize_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Quantization failed: {result.stderr}")
            sys.exit(1)

        print("✅ Model quantized to Q4_K_M")

    except Exception as e:
        print(f"❌ GGUF conversion process failed: {e}")
        print("Note: This requires llama.cpp to be installed. Install with:")
        print("git clone https://github.com/ggerganov/llama.cpp")
        print("cd llama.cpp && make")
        sys.exit(1)

    # Upload to Hugging Face
    print(f"📤 Uploading GGUF to: {GGUF_REPO}")
    try:
        api.create_repo(GGUF_REPO, exist_ok=True, private=False)

        api.upload_file(
            path_or_fileobj=f"{temp_dir}/vetta-granite-q4_k_m.gguf",
            path_in_repo="vetta-granite-2b-gguf-v3.gguf",
            repo_id=GGUF_REPO,
            repo_type="model",
            commit_message="Upload GGUF quantized model for Vetta Granite v3 (Q4_K_M)",
        )
        print("✅ GGUF model uploaded to Hugging Face")

    except Exception as e:
        print(f"❌ GGUF upload failed: {e}")
        sys.exit(1)

    # Create model card
    model_card = """---
language: en
tags:
- granite
- gguf
- quantized
- interview
- ai-interviewer
- vetta
- ollama
license: apache-2.0
---

# Vetta Granite GGUF Model v3

This repository contains the quantized GGUF version of the Vetta AI interviewer model for efficient inference with Ollama or vLLM.

## Usage with Ollama

1. Download the GGUF file: `vetta-granite-2b-gguf-v3.gguf`
2. Create Modelfile:
```
FROM ./vetta-granite-2b-gguf-v3.gguf
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
SYSTEM "You are Vetta, a professional AI interviewer conducting technical interviews."
```

3. Create model: `ollama create vetta-granite -f Modelfile`
4. Run: `ollama run vetta-granite`

## Training Details
- Base Model: ibm-granite/granite-3.0-2b-instruct
- Training Method: LoRA fine-tuning
- Quantization: Q4_K_M
- Dataset: Custom interview conversation dataset
- Training Steps: 2250
- Final Loss: 0.1124

## Intended Use
This model is designed to conduct professional AI-powered interviews, providing empathetic and technically accurate responses.
"""

    try:
        api.upload_file(
            path_or_fileobj=model_card.encode(),
            path_in_repo="README.md",
            repo_id=GGUF_REPO,
            repo_type="model",
            commit_message="Add model card and usage instructions",
        )
        print("✅ Model card uploaded")
    except Exception as e:
        print(f"❌ Model card upload failed: {e}")

    print("\n" + "=" * 60)
    print("🎉 GGUF CONVERSION COMPLETE!")
    print("=" * 60)
    print(f"GGUF Model: https://huggingface.co/{GGUF_REPO}")
    print("\nReady for Ollama integration!")


if __name__ == "__main__":
    convert_to_gguf()
