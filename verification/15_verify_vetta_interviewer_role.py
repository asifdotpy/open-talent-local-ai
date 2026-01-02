# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL: Enhanced Vetta LoRA Model Response Quality Verification       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# Install required packages (run this first if not installed)
# !pip install torch transformers unsloth huggingface_hub

import time

import torch
from huggingface_hub import login
from unsloth import FastLanguageModel

# 1. CONFIGURATION
LORA_REPO = "asifdotpy/vetta-granite-2b-lora-v3"
BASE_MODEL = "ibm-granite/granite-3.0-2b-instruct"

print("🔍 Enhanced Vetta LoRA Model Response Quality Verification")
print("=" * 70)
print(f"📋 Model: {LORA_REPO}")
print(f"📋 Base:  {BASE_MODEL}")
print()

# 2. AUTHENTICATE
try:
    # Use HF_TOKEN from environment
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
        print("✅ Authenticated with Hugging Face")
    else:
        print(
            "⚠️  HF_TOKEN not set. Please set HF_TOKEN environment variable or run huggingface-cli login"
        )
        login()  # Will prompt for token
except Exception as e:
    print(f"❌ HF Authentication failed: {e}")
    print("💡 Make sure HF_TOKEN is set in environment variables")
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

    # Enable inference mode
    FastLanguageModel.for_inference(model)
    print("✅ Ready for inference")

except Exception as e:
    print(f"❌ Model loading failed: {e}")
    raise

# 4. ENHANCED TEST SCENARIOS FOR INTERVIEWER ROLE
test_scenarios = [
    {
        "role": "Interviewer Introduction",
        "context": "Candidate has just joined the video call",
        "candidate_input": "Hi, I'm John. I'm here for the software engineering interview.",
        "expected": "Professional greeting, introduction as interviewer, explain process, ask icebreaker question",
    },
    {
        "role": "Technical Follow-up",
        "context": "Candidate just explained they worked with React",
        "candidate_input": "I've been working with React for about 2 years now, building user interfaces and managing state.",
        "expected": "Ask specific technical questions about React experience, probe for depth, ask about challenges",
    },
    {
        "role": "Behavioral Probing",
        "context": "Candidate mentioned they solved a performance issue",
        "candidate_input": "I once had to optimize a slow database query that was causing page load times of 5+ seconds.",
        "expected": "Ask follow-up questions about the problem-solving process, technical details, outcomes",
    },
    {
        "role": "Experience Assessment",
        "context": "Candidate is explaining their background",
        "candidate_input": "I have experience with Python, JavaScript, and some cloud technologies like AWS.",
        "expected": "Ask about specific projects, depth of experience, ask to elaborate on technologies mentioned",
    },
    {
        "role": "Problem-Solving Evaluation",
        "context": "Candidate is walking through a coding problem",
        "candidate_input": "For this algorithm, I think we should use a hash table to store the frequencies.",
        "expected": "Ask why they chose that approach, probe about trade-offs, ask about edge cases",
    },
    {
        "role": "Culture Fit Assessment",
        "context": "Candidate is asked about team collaboration",
        "candidate_input": "I prefer working independently because I can focus better that way.",
        "expected": "Gently probe about teamwork preferences, ask about past collaborative experiences, explore flexibility",
    },
    {
        "role": "Closing Questions",
        "context": "Interview is wrapping up",
        "candidate_input": "I think that covers most of my experience. Do you have any other questions?",
        "expected": "Ask candidate if they have questions about the role/company, provide next steps, thank them",
    },
]


def analyze_interviewer_response(response, expected_behavior):
    """Analyze if response shows interviewer behavior"""
    analysis = {
        "word_count": len(response.split()),
        "asks_questions": "?" in response,
        "follow_up_questions": response.count("?") >= 2,
        "probing_depth": any(
            word in response.lower()
            for word in [
                "why",
                "how",
                "what",
                "tell me more",
                "can you elaborate",
                "walk me through",
            ]
        ),
        "shows_engagement": any(
            word in response.lower()
            for word in ["interesting", "great", "excellent", "impressive", "fascinating"]
        ),
        "professional_tone": not any(
            word in response.lower()
            for word in ["i think", "i believe", "in my experience", "i remember"]
        ),
        "interviewer_indicators": any(
            word in response.lower()
            for word in [
                "let's talk about",
                "can you tell me",
                "i'd like to know",
                "help me understand",
            ]
        ),
    }

    # Calculate quality score
    score = 0
    score += 2 if analysis["asks_questions"] else 0
    score += 2 if analysis["follow_up_questions"] else 0
    score += 2 if analysis["probing_depth"] else 0
    score += 1 if analysis["shows_engagement"] else 0
    score += 1 if analysis["professional_tone"] else 0
    score += 1 if analysis["interviewer_indicators"] else 0

    analysis["quality_score"] = score
    analysis["max_score"] = 9

    return analysis


print("\n🧪 TESTING VETTA AS INTERVIEWER (Enhanced Scenarios)")
print("=" * 70)

total_score = 0
max_possible_score = 0

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n🎯 Test {i}: {scenario['role']}")
    print(f"📝 Context: {scenario['context']}")
    print(f"👤 Candidate: {scenario['candidate_input']}")
    print(f"🎯 Expected: {scenario['expected']}")
    print("-" * 60)

    # Create interviewer prompt with clear role definition
    system_prompt = """You are Vetta, a professional AI interviewer conducting technical interviews.

CRITICAL: You are the INTERVIEWER, not the interviewee. Your role is to:
- Ask questions to learn about the candidate
- Probe deeper into their experiences
- Show interest and engagement
- Guide the conversation professionally
- Assess their skills and fit

NEVER respond as if you are the candidate being interviewed. Always respond as the interviewer asking questions."""

    prompt = f"""{system_prompt}

Interview Context: {scenario['context']}

Candidate's Response: {scenario['candidate_input']}

As the interviewer, how would you respond? Ask follow-up questions and show engagement:

Vetta:"""

    try:
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=250,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1,
            )

        # Decode response
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract Vetta's response
        if "Vetta:" in full_response:
            vetta_response = full_response.split("Vetta:")[-1].strip()
        else:
            vetta_response = full_response.replace(prompt, "").strip()

        # Clean up response
        vetta_response = vetta_response.split("\n\n")[0]  # Take first paragraph
        if len(vetta_response) > 600:
            vetta_response = vetta_response[:600] + "..."

        print(f"🤖 Vetta: {vetta_response}")

        # Analyze response quality
        analysis = analyze_interviewer_response(vetta_response, scenario["expected"])

        print("📊 Interviewer Quality Analysis:")
        print(f"   • Words: {analysis['word_count']}")
        print(f"   • Asks questions: {'✅' if analysis['asks_questions'] else '❌'}")
        print(f"   • Multiple questions: {'✅' if analysis['follow_up_questions'] else '❌'}")
        print(f"   • Probing depth: {'✅' if analysis['probing_depth'] else '❌'}")
        print(f"   • Shows engagement: {'✅' if analysis['shows_engagement'] else '❌'}")
        print(f"   • Professional tone: {'✅' if analysis['professional_tone'] else '❌'}")
        print(f"   • Interviewer indicators: {'✅' if analysis['interviewer_indicators'] else '❌'}")
        print(f"   • Quality Score: {analysis['quality_score']}/{analysis['max_score']}")

        total_score += analysis["quality_score"]
        max_possible_score += analysis["max_score"]

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        max_possible_score += 9
        continue

# Overall assessment
overall_percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0

print("\n" + "=" * 70)
print("🎉 ENHANCED VETTA LORA VERIFICATION COMPLETE!")
print("=" * 70)
print("✅ Model successfully loaded from Hugging Face")
print("✅ Generated responses for enhanced interviewer scenarios")
print(f"📊 Overall Quality Score: {total_score}/{max_possible_score} ({overall_percentage:.1f}%)")

# Assessment levels
if overall_percentage >= 80:
    assessment = "🟢 EXCELLENT - Ready for production"
elif overall_percentage >= 60:
    assessment = "🟡 GOOD - Needs minor improvements"
elif overall_percentage >= 40:
    assessment = "🟠 FAIR - Significant improvements needed"
else:
    assessment = "🔴 POOR - Major retraining required"

print(f"🎯 Assessment: {assessment}")

print("\n📋 Key Findings:")
if total_score < max_possible_score * 0.6:
    print("⚠️  Model appears to respond as interviewee rather than interviewer")
    print("💡 Consider retraining with interviewer-focused conversations")
else:
    print("✅ Model shows interviewer behavior patterns")
    print("✅ Ready for integration testing")

print("\n📋 Next Steps:")
print("1. Review individual responses for role confusion")
print("2. Consider additional training data focused on interviewer role")
print("3. Test integration with actual interview flow")
print("4. Validate with human interviewers")

print("\n🔗 Model Repository: https://huggingface.co/asifdotpy/vetta-granite-2b-lora-v3")
print("📚 Integration Guide: Check model card for usage examples")
