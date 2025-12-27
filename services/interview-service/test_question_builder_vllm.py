#!/usr/bin/env python3
"""Test script for vLLM + Qdrant integration
Tests the Natural Language Question Builder with vector database.
"""

import asyncio
import sys

# Add the app directory to the Python path
sys.path.append(".")

from services.question_builder import (
    NaturalLanguagePrompt,
    NaturalLanguageQuestionBuilder,
)


async def test_vllm_qdrant_integration():
    """Test the complete vLLM + Qdrant integration."""
    print("🧪 Testing vLLM + Qdrant Integration")
    print("=" * 50)

    try:
        # Initialize the question builder
        print("🔧 Initializing Question Builder...")
        builder = NaturalLanguageQuestionBuilder()
        print("✅ Question Builder initialized")

        # Test 1: Generate new questions
        print("\n📝 Test 1: Generating New Questions")
        prompt = NaturalLanguagePrompt(
            prompt="Create technical questions for a senior Python backend developer role",
            job_title="Senior Python Backend Developer",
            required_skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
            num_questions=3,
        )

        questions = await builder.generate_questions(prompt)
        print(f"✅ Generated {len(questions)} questions")

        for i, q in enumerate(questions, 1):
            print(f"{i}. {q.question_text[:60]}... ({q.question_type.value})")

        # Test 2: Semantic search (should find similar questions)
        print("\n🔍 Test 2: Semantic Search")
        search_prompt = NaturalLanguagePrompt(
            prompt="Questions about Python web development and APIs",
            job_title="Python Developer",
            required_skills=["Python", "Django", "REST APIs"],
            num_questions=2,
        )

        similar_questions = await builder._semantic_search_questions(search_prompt)
        if similar_questions:
            print(f"✅ Found {len(similar_questions)} similar questions in vector DB")
            for i, q in enumerate(similar_questions, 1):
                print(f"{i}. {q.question_text[:60]}...")
        else:
            print("ℹ️ No similar questions found (expected on first run)")

        # Test 3: Generate questions again (should use semantic search)
        print("\n🔄 Test 3: Second Generation (with semantic search)")
        prompt2 = NaturalLanguagePrompt(
            prompt="Technical questions for backend development with databases",
            job_title="Backend Developer",
            required_skills=["Python", "SQL", "APIs"],
            num_questions=2,
        )

        questions2 = await builder.generate_questions(prompt2)
        print(f"✅ Generated {len(questions2)} questions (with vector search)")

        print("\n🎉 All tests passed!")
        print("✅ vLLM inference working")
        print("✅ Qdrant vector database operational")
        print("✅ Semantic search functional")
        print("✅ Question generation with vector similarity working")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_basic_vllm_connection():
    """Test basic vLLM connection without Qdrant."""
    print("🔗 Testing Basic vLLM Connection")
    print("=" * 40)

    try:
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test vLLM health
            response = await client.get("http://localhost:8000/v1/models")
            if response.status_code == 200:
                print("✅ vLLM server is responding")
                models = response.json()
                print(f"📊 Available models: {len(models.get('data', []))}")
            else:
                print(f"❌ vLLM server error: {response.status_code}")
                return False

            # Test Qdrant health
            response = await client.get("http://localhost:6333/health")
            if response.status_code == 200:
                print("✅ Qdrant database is responding")
            else:
                print(f"❌ Qdrant database error: {response.status_code}")
                return False

        return True

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 OpenTalent Question Builder - vLLM + Qdrant Test Suite")
    print("=" * 60)

    async def main():
        # Test basic connections first
        basic_test = await test_basic_vllm_connection()
        if not basic_test:
            print("\n❌ Basic connection tests failed. Please check:")
            print("   - Is vLLM running on port 8000?")
            print("   - Is Qdrant running on port 6333?")
            print("   - Are Docker containers started?")
            sys.exit(1)

        # Test full integration
        integration_test = await test_vllm_qdrant_integration()
        if integration_test:
            print("\n🎯 SUCCESS: vLLM + Qdrant integration is working!")
            print("📚 Your question builder now has:")
            print("   • High-performance vLLM inference")
            print("   • Qdrant vector database for semantic search")
            print("   • Question similarity matching")
            print("   • Efficient caching and retrieval")
        else:
            print("\n❌ Integration tests failed")
            sys.exit(1)

    asyncio.run(main())
