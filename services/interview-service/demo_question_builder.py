#!/usr/bin/env python3
"""Demo script for Natural Language Question Builder
Shows how to use the service to generate interview questions.

Inspired by PeopleGPT's natural language search paradigm
"""

import asyncio
import os

from services.question_builder import (
    NaturalLanguagePrompt,
    NaturalLanguageQuestionBuilder,
    QuestionDifficulty,
)


async def demo_natural_language_generation():
    """Demo: Generate questions from natural language."""
    print("=" * 80)
    print("DEMO 1: Natural Language Question Generation")
    print("=" * 80)

    builder = NaturalLanguageQuestionBuilder(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), model="smollm:135m"
    )

    prompt = NaturalLanguagePrompt(
        prompt="Create questions to assess system design skills for senior backend engineer with focus on scalability",
        job_title="Senior Backend Engineer",
        required_skills=["System Design", "Scalability", "Microservices"],
        company_culture=["Remote-first", "Fast-paced", "Innovation"],
        num_questions=3,
        difficulty=QuestionDifficulty.SENIOR,
        interview_duration=30,
    )

    print("\n📝 Natural Language Prompt:")
    print(f"   '{prompt.prompt}'")
    print("\n⚙️  Configuration:")
    print(f"   Job Title: {prompt.job_title}")
    print(f"   Required Skills: {', '.join(prompt.required_skills)}")
    print(f"   Difficulty: {prompt.difficulty.value}")
    print(f"   Questions: {prompt.num_questions}")
    print(f"   Duration: {prompt.interview_duration} minutes")

    print("\n🤖 Generating questions...")
    questions = await builder.generate_questions(prompt)

    print(f"\n✅ Generated {len(questions)} questions:\n")

    for i, question in enumerate(questions, 1):
        print(f"{'=' * 80}")
        print(f"Question {i}:")
        print(f"{'=' * 80}")
        print(f"❓ {question.question_text}")
        print(f"\n📌 Priority: {question.priority.value.upper()}")
        print(f"⏱️  Expected Duration: {question.expected_duration} minutes")
        print(f"🏷️  Type: {question.question_type.value}")
        print(f"🎯 Difficulty: {question.difficulty.value}")

        if question.evaluation_criteria:
            print("\n✓ Evaluation Criteria:")
            for criterion in question.evaluation_criteria:
                print(f"  • {criterion}")

        if question.skill_assessed:
            print(f"\n🔧 Skills Assessed: {', '.join(question.skill_assessed)}")

        if question.follow_up_questions:
            print("\n💬 Follow-up Questions:")
            for fq in question.follow_up_questions:
                print(f"  → {fq}")

        print()


async def demo_template_usage():
    """Demo: Use a pre-built template."""
    print("\n" + "=" * 80)
    print("DEMO 2: Using Pre-built Templates")
    print("=" * 80)

    builder = NaturalLanguageQuestionBuilder(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), model="smollm:135m"
    )

    # List available templates
    print("\n📚 Available Templates:")
    templates = builder.list_templates()
    for template in templates:
        print(f"\n  • {template.template_name} (ID: {template.template_id})")
        print(f"    {template.description}")
        print(f"    Questions: {len(template.questions)}")
        print(f"    Job Roles: {', '.join(template.job_roles)}")

    # Use backend template
    print("\n\n🎯 Using 'backend-senior' template:")
    template = builder.get_template("backend-senior")

    print(f"\n📋 Template: {template.template_name}")
    print(f"📄 Description: {template.description}")
    print(f"\n✅ Template Questions ({len(template.questions)}):\n")

    for i, question in enumerate(template.questions, 1):
        print(f"{i}. {question.question_text}")
        print(f"   Priority: {question.priority.value} | Duration: {question.expected_duration}min")
        print()


def demo_pinning_logic():
    """Demo: Pin/unpin questions (must-ask vs nice-to-ask)."""
    print("\n" + "=" * 80)
    print("DEMO 3: Question Pinning (Must-Ask vs Nice-to-Ask)")
    print("=" * 80)

    builder = NaturalLanguageQuestionBuilder()

    # Get backend template
    template = builder.get_template("backend-senior")
    questions = template.questions[:3]  # First 3 questions

    print("\n📌 Pinning Logic (inspired by PeopleGPT):")
    print("   • Pinned questions = MUST ask (highest priority)")
    print("   • Unpinned questions = NICE to ask (ask if time permits)")

    print("\n\n🔄 Initial State:")
    for i, q in enumerate(questions, 1):
        print(f"{i}. [{q.priority.value.upper()}] {q.question_text[:80]}...")

    # Pin first question
    print("\n\n📍 Pinning question 1...")
    questions[0] = builder.pin_question(questions[0])

    # Unpin second question
    print("📌 Unpinning question 2...")
    questions[1] = builder.unpin_question(questions[1])

    print("\n\n✅ Updated State:")
    for i, q in enumerate(questions, 1):
        status = "🔴 MUST ASK" if q.priority.value == "must_ask" else "🟢 NICE TO ASK"
        print(f"{i}. [{status}] {q.question_text[:80]}...")


async def demo_different_roles():
    """Demo: Generate questions for different roles."""
    print("\n" + "=" * 80)
    print("DEMO 4: Questions for Different Roles")
    print("=" * 80)

    builder = NaturalLanguageQuestionBuilder(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), model="smollm:135m"
    )

    roles = [
        {
            "prompt": "Generate behavioral questions for a product manager focused on stakeholder management",
            "job_title": "Product Manager",
            "num_questions": 2,
        },
        {
            "prompt": "Create technical questions for a data scientist with ML experience",
            "job_title": "Data Scientist",
            "num_questions": 2,
        },
    ]

    for role in roles:
        print(f"\n\n📋 Role: {role['job_title']}")
        print(f"💬 Prompt: '{role['prompt']}'")

        prompt = NaturalLanguagePrompt(
            prompt=role["prompt"],
            job_title=role["job_title"],
            num_questions=role["num_questions"],
            difficulty=QuestionDifficulty.MID_LEVEL,
        )

        questions = await builder.generate_questions(prompt)

        print("\n✅ Generated Questions:")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q.question_text}")
            print(f"   Type: {q.question_type.value} | Skills: {', '.join(q.skill_assessed)}")


async def main():
    """Run all demos."""
    print("\n")
    print("🚀 OpenTalent Natural Language Question Builder Demo")
    print("=" * 80)
    print("\nInspired by PeopleGPT's natural language search paradigm:")
    print("  ✓ Describe what you want in plain English")
    print("  ✓ AI generates structured, insightful questions")
    print("  ✓ No complex forms or Boolean operators needed")
    print("  ✓ Pin important questions (must-ask vs nice-to-ask)")
    print()

    # Check if Ollama is available
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    if not os.path.exists("/usr/local/bin/ollama"):  # Basic check if ollama is installed
        print("⚠️  WARNING: Ollama not detected on system")
        print("   Question generation will fall back to templates")
        print("   Install Ollama and run: ollama pull granite4")
        print(f"   Set OLLAMA_BASE_URL={ollama_url} to use local Granite4 model")
    else:
        print("✅ Ollama detected - Granite4 model will be used")
        print(f"   Ollama URL: {ollama_url}")

    print("\n" + "=" * 80)

    try:
        # Run demos
        await demo_natural_language_generation()
        await demo_template_usage()
        demo_pinning_logic()
        await demo_different_roles()

        print("\n" + "=" * 80)
        print("✅ Demo Complete!")
        print("=" * 80)
        print("\nNext Steps:")
        print("  1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("  2. Pull Granite4 model: ollama pull granite4")
        print("  3. Set OLLAMA_BASE_URL=http://localhost:11434 (default)")
        print("  4. Run tests: pytest tests/test_question_builder.py -v")
        print("  5. Start FastAPI server: uvicorn main:app --reload")
        print("  6. Test API: curl http://localhost:8000/api/v1/questions/templates")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
