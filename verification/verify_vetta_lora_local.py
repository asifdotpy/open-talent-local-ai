#!/usr/bin/env python3
"""
Vetta LoRA Model Verification Script

This script verifies that the Vetta AI interviewer LoRA model is working correctly
by testing it with sample interview questions.

Usage:
    python verify_vetta_lora.py

Requirements:
    pip install torch transformers unsloth huggingface_hub
"""

import os
import time

import torch
from huggingface_hub import login
from unsloth import FastLanguageModel


def main():
    print("🔍 Vetta LoRA Model Verification")
    print("=" * 50)

    # Configuration
    LORA_REPO = "asifdotpy/vetta-granite-2b-lora-v3"
    BASE_MODEL = "ibm-granite/granite-3.0-2b-instruct"

    # Authenticate
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("❌ Please set HF_TOKEN environment variable")
        return

    login(token=hf_token)
    print("✅ Authenticated with Hugging Face")

    # Load model
    print(f"📥 Loading model from: {LORA_REPO}")
    start_time = time.time()

    try:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=BASE_MODEL,
            max_seq_length=2048,
            load_in_4bit=True,
            device_map="auto",
        )

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

        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.1f} seconds")
        # Enable inference
        FastLanguageModel.for_inference(model)
        print("✅ Model ready for inference")

        # Test questions
        test_questions = [
            "Hello, I'm here for a software engineering interview. Can you introduce yourself?",
            "What programming languages should I be proficient in for a backend developer role?",
        ]

        print("\n🧪 Testing Interview Responses:")
        print("-" * 30)

        for i, question in enumerate(test_questions, 1):
            print(f"\nQ{i}: {question}")

            prompt = f"""You are Vetta, a professional AI interviewer conducting technical interviews.

Question: {question}

Response:"""

            inputs = tokenizer(prompt, return_tensors="pt").to(
                "cuda" if torch.cuda.is_available() else "cpu"
            )

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )

            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            if "Response:" in response:
                response = response.split("Response:")[-1].strip()

            print(f"Vetta: {response[:200]}{'...' if len(response) > 200 else ''}")

        print("\n✅ Verification Complete!")
        print("🎉 Vetta LoRA model is working correctly!")

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
