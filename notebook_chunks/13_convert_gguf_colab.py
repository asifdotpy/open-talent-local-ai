# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL: Convert Merged Model to GGUF (Colab Version)                    ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# Install required packages (run this first if not installed)
# !pip install torch transformers unsloth huggingface_hub

import os
from unsloth import FastLanguageModel
from huggingface_hub import HfApi
from google.colab import userdata

# 1. CONFIGURATION
HF_USERNAME = "asifdotpy"
BASE_MODEL = "ibm-granite/granite-3.0-2b-instruct"
MERGED_REPO = f"{HF_USERNAME}/vetta-granite-2b-v3"
GGUF_REPO = f"{HF_USERNAME}/vetta-granite-2b-gguf-v3"
VERSION = "v3"

# Drive paths
models_dir = "/content/drive/MyDrive/talent-ai-vetta/models"
merged_dir = f"{models_dir}/merged"
gguf_dir = f"{models_dir}/gguf"

print("🔄 Starting GGUF conversion process in Colab...")
print(f"📂 Merged directory: {merged_dir}")
print(f"📂 GGUF directory: {gguf_dir}")

# 2. SAFETY CHECKS
if not os.path.exists(merged_dir):
    raise FileNotFoundError(f"❌ Merged model directory not found: {merged_dir}. Run merge cell first.")

# Check if merged model has files
import os
merged_files = [f for f in os.listdir(merged_dir) if os.path.isfile(os.path.join(merged_dir, f))]
if not merged_files:
    raise FileNotFoundError(f"❌ No files found in merged directory: {merged_dir}")

print(f"✅ Found merged model with {len(merged_files)} files")

# 3. LOGIN TO HUGGING FACE
try:
    hf_token = userdata.get('HF_TOKEN')
    from huggingface_hub import login
    login(token=hf_token)
    api = HfApi(token=hf_token)
    print("✅ Logged in to Hugging Face")
except Exception as e:
    print(f"❌ HF login failed: {e}")
    raise

# 4. LOAD MERGED MODEL
print(f"📥 Loading merged model from: {merged_dir}")
try:
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=merged_dir,  # Load from local Drive
        max_seq_length=2048,
        load_in_4bit=False,  # Full precision for conversion
        device_map="auto",
    )
    print("✅ Merged model loaded")
except Exception as e:
    print(f"❌ Failed to load merged model: {e}")
    raise

# 5. CONVERT TO GGUF
print(f"🔄 Converting to GGUF format (Q4_K_M quantization)...")
print(f"💾 Saving GGUF to: {gguf_dir}")

os.makedirs(gguf_dir, exist_ok=True)

try:
    # Use Unsloth's GGUF conversion
    model.save_pretrained_gguf(
        gguf_dir,
        tokenizer,
        quantization_method="q4_k_m",  # Good balance of size/speed
    )
    print("✅ GGUF conversion completed")
except Exception as e:
    print(f"❌ GGUF conversion failed: {e}")
    raise

# 6. VERIFY GGUF FILES
gguf_files = [f for f in os.listdir(gguf_dir) if f.endswith('.gguf')]
if not gguf_files:
    raise FileNotFoundError(f"❌ No GGUF files found in {gguf_dir}")

print(f"✅ GGUF files created: {gguf_files}")

# 7. UPLOAD GGUF TO HUGGING FACE
print(f"📤 Uploading GGUF to: {GGUF_REPO}")
try:
    api.create_repo(GGUF_REPO, exist_ok=True, private=False)

    api.upload_folder(
        folder_path=gguf_dir,
        repo_id=GGUF_REPO,
        repo_type="model",
        commit_message=f"Upload GGUF quantized model for Vetta Granite {VERSION} (Q4_K_M)"
    )
    print("✅ GGUF model uploaded to Hugging Face")
    print(f"👉 https://huggingface.co/{GGUF_REPO}")

except Exception as e:
    print(f"❌ GGUF upload failed: {e}")
    raise

# 8. CREATE GGUF MODEL CARD
print("📝 Creating GGUF model card...")
gguf_card = f"""---
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

# Vetta Granite GGUF Model {VERSION}

This repository contains the quantized GGUF version of the Vetta AI interviewer model for efficient inference with Ollama or vLLM.

## Usage with Ollama

1. Download the GGUF file
2. Create Modelfile:
```
FROM ./vetta-granite-2b-gguf-{VERSION}.gguf
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
        path_or_fileobj=gguf_card.encode(),
        path_in_repo="README.md",
        repo_id=GGUF_REPO,
        repo_type="model",
        commit_message="Add model card and usage instructions"
    )
    print("✅ GGUF model card uploaded")
except Exception as e:
    print(f"❌ GGUF model card upload failed: {e}")

print("\n" + "="*60)
print("🎉 GGUF CONVERSION COMPLETE!")
print("="*60)
print(f"LoRA Adapters: https://huggingface.co/{HF_USERNAME}/vetta-granite-2b-lora-{VERSION}")
print(f"Merged Model:  https://huggingface.co/{MERGED_REPO}")
print(f"GGUF Model:    https://huggingface.co/{GGUF_REPO}")
print("\nAll model formats are now available!")
print("You can integrate Vetta into your interview service using any format:")
print("- LoRA: Fast loading, requires base model")
print("- Merged: Standalone, good performance")
print("- GGUF: Quantized, best for production/Ollama")