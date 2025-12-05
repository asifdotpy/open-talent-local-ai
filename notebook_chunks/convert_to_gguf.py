# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  Local GGUF Conversion Script                                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

"""
WHEN TO RUN: After uploading LoRA and merged models to Hugging Face.
Run this on a LOCAL MACHINE with 16GB+ RAM (not in Colab).

WHY: GGUF conversion requires compiling llama.cpp and quantizing,
which exceeds Colab's 12-15GB RAM limit and causes crashes.

WORKFLOW:
1. Train and save models in Colab (LoRA + merged only)
2. Upload to Hugging Face from Colab
3. Download merged model locally
4. Run this script: python convert_to_gguf.py
5. Upload GGUF folder to: asifdotpy/vetta-granite-2b-gguf-v3

REQUIRES: 16GB+ RAM, Python with unsloth installed
"""

import os
from unsloth import FastLanguageModel

def convert_to_gguf():
    # CONFIGURE THIS PATH: Download from Hugging Face first
    merged_model_path = "/path/to/downloaded/merged/model"  # ← CHANGE THIS
    gguf_output_dir = "./gguf"

    print("🔄 Local GGUF Conversion (16GB+ RAM required)")
    print("⚠️  This will take 20-30 minutes and requires significant RAM")
    print(f"📂 Input: {merged_model_path}")
    print(f"📂 Output: {gguf_output_dir}")
    print()

    if merged_model_path == "/path/to/downloaded/merged/model":
        print("❌ ERROR: You must update merged_model_path first!")
        print("   1. Go to: https://huggingface.co/asifdotpy/vetta-granite-2b-v3")
        print("   2. Download the entire repository (Download ZIP)")
        print("   3. Extract and set merged_model_path to the extracted folder")
        print("   4. Run this script again")
        return

    try:
        print("🔄 Loading merged model for GGUF conversion...")
        # Load the merged model
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=merged_model_path,
            max_seq_length=2048,
            dtype=None,  # Auto-detect
            load_in_4bit=False,  # Load in full precision for conversion
        )

        print("✅ Model loaded successfully")

        # Create output directory
        os.makedirs(gguf_output_dir, exist_ok=True)

        print("🔄 Converting to GGUF format (Q4_K_M quantization)...")
        # Convert to GGUF
        model.save_pretrained_gguf(
            gguf_output_dir,
            tokenizer,
            quantization_method="q4_k_m",
        )

        print(f"✅ GGUF conversion complete! Files saved to: {gguf_output_dir}")

        # Show file sizes
        if os.path.exists(gguf_output_dir):
            total_size = 0
            for file in os.listdir(gguf_output_dir):
                file_path = os.path.join(gguf_output_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    total_size += size
                    print(f"   {file}: {size / 1024**3:.2f} GB")

            print(f"   Total: {total_size / 1024**3:.2f} GB")

        print("\n📤 Upload instructions:")
        print("1. Go to: https://huggingface.co/asifdotpy/vetta-granite-2b-gguf-v3")
        print("2. Upload the entire 'gguf' folder")
        print("3. The model card will be auto-generated")
        print("\n🎉 All three model formats now available!")

    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        print("\n💡 Troubleshooting:")
        print("- Ensure you have 16GB+ RAM available")
        print("- Check that the merged model path is correct")
        print("- Try running on a machine with more RAM")
        print("- Make sure unsloth is installed: pip install unsloth")

if __name__ == "__main__":
    convert_to_gguf()</content>
<parameter name="filePath">/home/asif1/talent-ai-platform/notebook_chunks/convert_to_gguf.py