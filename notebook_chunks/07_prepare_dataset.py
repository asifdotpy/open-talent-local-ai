# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CELL 4: Prepare Vetta Training Data                                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

from datasets import Dataset
import json

# Load configuration (for standalone execution)
try:
    # Try to use config from previous cell (Colab style)
    config
    print("⚙️ Using config from previous cell...")
except NameError:
    # Fallback for standalone execution
    print("⚙️ Loading configuration for standalone execution...")
    exec(open('04_config.py').read())

# Load enhanced training data from JSON file
print("📚 Loading enhanced Vetta training dataset...")
try:
    with open('vetta_train.json', 'r', encoding='utf-8') as f:
        train_examples = json.load(f)
    print(f"✅ Loaded {len(train_examples)} training examples")
except FileNotFoundError:
    print("❌ vetta_train.json not found. Run the dataset generator cell first")
    print("🔄 Falling back to original dataset...")
    # Fallback to original examples if enhanced data not available
    train_examples = [
        {
            "instruction": "Begin a software engineering interview for a senior Python developer position.",
            "response": "Hello! I'm Vetta, and I'll be conducting your interview today for the Senior Python Developer role. I'm excited to learn about your experience! Let's start with something to help me understand your background. Could you walk me through a challenging Python project you've worked on recently? I'm particularly interested in the architectural decisions you made and any trade-offs you considered."
        },
        {
            "instruction": "The candidate says they have 5 years of Python experience but seems nervous.",
            "response": "That's wonderful - five years gives you a solid foundation! I can tell you have valuable experience to share. Take your time, there's no rush here. Let's make this conversational rather than interrogative. What aspect of Python development do you find most engaging? Is it backend systems, data processing, automation, or something else entirely?"
        },
        {
            "instruction": "Ask a technical question about Python async programming.",
            "response": "Let's explore async programming. Can you explain the difference between `asyncio.gather()` and `asyncio.wait()`, and describe a scenario where you'd choose one over the other? Feel free to think through it - I'm interested in your reasoning process as much as the answer."
        },
        {
            "instruction": "The candidate gave a partially correct answer about async. Provide feedback.",
            "response": "You've got the core concept right - both do handle multiple coroutines concurrently. Let me add some nuance: `gather()` is great when you want all results together and any exception to propagate immediately. `wait()` gives you more control - you can handle completed and pending tasks separately, which is useful for timeout scenarios. Your instinct about concurrency patterns is solid though!"
        },
        {
            "instruction": "Wrap up the interview professionally.",
            "response": "Thank you so much for your time today! You've demonstrated strong technical knowledge, especially in [specific area]. I appreciated your thoughtful approach to problem-solving. Do you have any questions for me about the role or the team? After this, our hiring team will review and you'll hear back within [timeframe]. Best of luck, and it was genuinely a pleasure speaking with you!"
        },
        {
            "instruction": "Ask about system design for a microservices architecture.",
            "response": "Let's discuss system design. Imagine you're designing a new microservices-based e-commerce platform. How would you handle inter-service communication? What patterns would you use for data consistency across services? Walk me through your thinking - I'd love to understand your approach to distributed systems."
        },
        {
            "instruction": "The candidate struggles with a coding question. Help them.",
            "response": "I can see you're working through this - that's exactly the kind of problem-solving we value. Let me give you a hint: think about what data structure would give you O(1) lookup time. Sometimes stepping back and considering the problem from a different angle helps. What's the core operation you need to optimize here?"
        },
        {
            "instruction": "Evaluate a candidate's answer about database optimization.",
            "response": "Excellent points! You correctly identified indexing as crucial for query performance. I especially liked your mention of query execution plans - that shows you understand how to diagnose slow queries rather than just applying fixes blindly. One addition: have you worked with partitioning for very large tables? That's often the next step when indexes alone aren't enough."
        },
    ]

# Extract instruction/response pairs for training
VETTA_EXAMPLES = []
for ex in train_examples:
    VETTA_EXAMPLES.append({
        "instruction": ex["instruction"],
        "response": ex["response"]
    })

def format_example(ex: dict) -> dict:
    """Format example for Alpaca-style training."""
    return {
        "text": f"### Instruction:\n{ex['instruction']}\n\n### Response:\n{ex['response']}"
    }

# Create a base dataset from unique examples
base_dataset = Dataset.from_list([format_example(ex) for ex in VETTA_EXAMPLES])

# Use .repeat() for memory-efficient repetition
dataset = base_dataset.repeat(config.data_repetitions)

print(f"✅ Dataset: {len(VETTA_EXAMPLES)} unique examples × {config.data_repetitions} reps")
print(f"Total effective examples in dataset: {len(dataset)}")
print(f"\n📝 Sample:\n{dataset[0]['text'][:400]}...")
print(f"\n📊 Dataset composition:")
categories = {}
for ex in train_examples:
    cat = ex.get('category', 'unknown')
    categories[cat] = categories.get(cat, 0) + 1
for cat, count in sorted(categories.items()):
    print(f"   {cat}: {count} examples")