import asyncio
import os
import sys

sys.path.append(".")

# Test Gemini directly
os.environ["OLLAMA_MODEL"] = "nonexistent-model"

import google.generativeai as genai
from services.question_builder import NaturalLanguagePrompt


async def test_gemini_direct():
    print("🧪 Testing Gemini API Directly")
    print("=" * 50)

    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = NaturalLanguagePrompt(
        prompt="Generate questions for junior React developer role",
        job_title="Junior React Developer",
        required_skills=["React", "JavaScript", "CSS"],
        num_questions=2,
    )

    # Build prompt for Gemini (same as in code)
    gemini_prompt = f"""You are an expert interview question generator. Generate exactly {prompt.num_questions} interview questions in JSON format.

Requirements:
- Output ONLY a JSON array, no other text
- Each question must have: question_text, question_type, difficulty, priority, expected_duration, evaluation_criteria, follow_up_questions, skill_assessed
- question_type must be one of: technical, behavioral, situational, cultural_fit, problem_solving, leadership, system_design
- difficulty must be one of: junior, mid_level, senior, principal, executive
- priority must be one of: must_ask, nice_to_ask
- Include at least 2 "must_ask" priority questions
- expected_duration in minutes (5-15)
- evaluation_criteria as array of strings
- follow_up_questions as array of strings
- skill_assessed as array of strings

Context:
Job Title: {prompt.job_title or "Software Engineer"}
Skills: {", ".join(prompt.required_skills) if prompt.required_skills else "General technical skills"}
Difficulty: {prompt.difficulty.value}
Duration: {prompt.interview_duration} minutes

Request: {prompt.prompt}

Output JSON array:"""

    print("📤 Sending prompt to Gemini...")
    print(gemini_prompt[:200] + "...")
    print()

    try:
        response = model.generate_content(gemini_prompt)
        print("📥 Gemini Response:")
        print("=" * 30)
        print(response.text)
        print("=" * 30)

        # Try to parse it
        import json

        content = response.text.strip()

        # Try to extract JSON from markdown code blocks
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            if json_end > json_start:
                content = content[json_start:json_end].strip()
        elif "```" in content:
            json_start = content.find("```") + 3
            json_end = content.find("```", json_start)
            if json_end > json_start:
                content = content[json_start:json_end].strip()

        print("🔍 Extracted JSON content:")
        print(content)
        print()

        questions_data = json.loads(content)
        print(f"✅ Successfully parsed {len(questions_data)} questions")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_gemini_direct())
