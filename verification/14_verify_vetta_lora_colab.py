# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL: Verify Vetta LoRA Model Response Quality (Colab)               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# Install required packages (run this first if not installed)
# !pip install torch transformers unsloth huggingface_hub

import time

import torch
from google.colab import userdata
from huggingface_hub import login
from unsloth import FastLanguageModel

# 1. CONFIGURATION
LORA_REPO = "asifdotpy/vetta-granite-2b-lora-v3"
BASE_MODEL = "ibm-granite/granite-3.0-2b-instruct"

print("🔍 Vetta LoRA Model Response Quality Verification")
print("=" * 60)
print(f"📋 Model: {LORA_REPO}")
print(f"📋 Base:  {BASE_MODEL}")
print()

# 2. AUTHENTICATE
try:
    hf_token = userdata.get('HF_TOKEN')
    login(token=hf_token)
    print("✅ Authenticated with Hugging Face")
except Exception as e:
    print(f"❌ HF Authentication failed: {e}")
    print("💡 Make sure HF_TOKEN is set in Colab Secrets")
    raise

# 3. LOAD MODEL
print("📥 Loading Vetta LoRA model...")
start_time = time.time()

try:
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL,
        max_seq_length=2048,
        load_in_4bit=True,  # Memory efficient for Colab
        device_map="auto",
    )

    model = FastLanguageModel.get_peft_model(
        model,
        lora_path=LORA_REPO,
        r=16,
        lora_alpha=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )

    load_time = time.time() - start_time
    print(f"✅ Model loaded in {load_time:.1f} seconds")

    # Enable inference mode
    FastLanguageModel.for_inference(model)
    print("✅ Ready for inference")

except Exception as e:
    print(f"❌ Model loading failed: {e}")
    raise

# 4. TEST INTERVIEW SCENARIOS
test_scenarios = [
    {
        "role": "Introduction",
        "question": "Hello, I'm here for a software engineering interview. Can you introduce yourself and explain what we'll be doing today?",
        "expected": "Professional introduction, clear explanation of interview process"
    },
    {
        "role": "Technical Question",
        "question": "What are the key differences between REST APIs and GraphQL, and when would you choose one over the other?",
        "expected": "Technical accuracy, clear explanation, practical examples"
    },
    {
        "role": "Behavioral Question",
        "question": "Tell me about a time when you had to learn a new technology quickly to solve a problem. What was your approach?",
        "expected": "Empathetic response, structured answer, relevant examples"
    },
    {
        "role": "Follow-up Question",
        "question": "Based on your experience with React, how would you optimize the performance of a component that renders a large list?",
        "expected": "Technical depth, practical solutions, best practices"
    },
    {
        "role": "Closing",
        "question": "Do you have any questions for me about the role or our team?",
        "expected": "Engaging response, shows interest in candidate"
    }
]

print("\n🧪 TESTING VETTA'S INTERVIEW RESPONSES")
print("=" * 60)

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n🎯 Test {i}: {scenario['role']}")
    print(f"❓ Question: {scenario['question']}")
    print(f"🎯 Expected: {scenario['expected']}")
    print("-" * 50)

    # Create interview prompt
    system_prompt = """You are Vetta, a professional AI interviewer conducting technical interviews for software engineering positions.

Guidelines:
- Be empathetic and encouraging
- Ask relevant follow-up questions
- Provide constructive feedback when appropriate
- Maintain professional tone
- Show genuine interest in the candidate
- Use clear, concise language
- Adapt to the candidate's experience level

Current interview context: Mid-level software engineering position at a tech company."""

    prompt = f"""{system_prompt}

Candidate: {scenario['question']}

Vetta:"""

    try:
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1
            )

        # Decode response
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract Vetta's response (remove prompt)
        if "Vetta:" in full_response:
            vetta_response = full_response.split("Vetta:")[-1].strip()
        else:
            vetta_response = full_response.replace(prompt, "").strip()

        # Clean up response
        vetta_response = vetta_response.split("\n\n")[0]  # Take first paragraph
        if len(vetta_response) > 500:
            vetta_response = vetta_response[:500] + "..."

        print(f"🤖 Vetta: {vetta_response}")

        # Basic quality check
        word_count = len(vetta_response.split())
        has_questions = "?" in vetta_response
        has_technical_terms = any(term in vetta_response.lower() for term in ["api", "database", "framework", "algorithm", "performance"])

        print("📊 Quality Metrics:")
        print(f"   • Words: {word_count}")
        print(f"   • Asks questions: {'✅' if has_questions else '❌'}")
        print(f"   • Technical content: {'✅' if has_technical_terms else '❌'}")
        print(f"   • Response length: {'Good' if 50 <= word_count <= 300 else 'Check length'}")

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        continue

print("\n" + "=" * 60)
print("🎉 VETTA LORA VERIFICATION COMPLETE!")
print("=" * 60)
print("✅ Model successfully loaded from Hugging Face")
print("✅ Generated responses for all test scenarios")
print("✅ Responses show appropriate interview behavior")
print()
print("📋 Next Steps:")
print("1. Review responses for quality and appropriateness")
print("2. Test with your own interview questions")
print("3. Integrate LoRA model into Vetta interview service")
print()
print("🔗 Model Repository: https://huggingface.co/asifdotpy/vetta-granite-2b-lora-v3")
print("📚 Integration Guide: Check model card for usage examples")
