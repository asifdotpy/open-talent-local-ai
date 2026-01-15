# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL 6: Test Vetta                                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

from unsloth import FastLanguageModel

# Enable fast inference
FastLanguageModel.for_inference(model)

TEST_PROMPTS = [
    "Begin a technical interview for a machine learning engineer position.",
    "The candidate seems unsure about their answer on neural networks. Encourage them.",
    "Ask a follow-up question about the candidate's experience with PyTorch.",
]

print("🧪 Testing Vetta's responses:\n")

for i, prompt in enumerate(TEST_PROMPTS, 1):
    inputs = tokenizer(f"### Instruction:\n{prompt}\n\n### Response:\n", return_tensors="pt").to(
        "cuda"
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.7,
        do_sample=True,
        top_p=0.9,
        repetition_penalty=1.1,
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response.split("### Response:")[-1].strip()

    print(f"📝 Test {i}: {prompt}")
    print(f"🤖 Vetta: {response[:350]}...\n")
    print("-" * 60)
