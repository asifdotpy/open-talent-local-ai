#!/usr/bin/env python3
"""
Cross-service integration tests for TalentAI microservices.
Tests communication between Avatar and Interview services.
"""

import asyncio
import httpx
import time

# Service URLs
AVATAR_SERVICE_URL = "http://localhost:8001"
INTERVIEW_SERVICE_URL = "http://localhost:8004"
FRONTEND_SERVICE_URL = "http://localhost:8080"
TIMEOUT = 15.0


class IntegrationTestSuite:
    """Integration test suite for all TalentAI services."""

    async def test_all_services_running(self):
        """Test that all services are running and responsive."""
        print("🔍 Testing service availability...")
        
        services = [
            ("Avatar Service", f"{AVATAR_SERVICE_URL}/health"),
            ("Interview Service", f"{INTERVIEW_SERVICE_URL}/"),
        ]
        
        # Optional services (don't fail if not running)
        optional_services = [
            ("Frontend Service", f"{FRONTEND_SERVICE_URL}/")
        ]
        
        async with httpx.AsyncClient() as client:
            # Test required services
            for service_name, url in services:
                try:
                    response = await client.get(url, timeout=TIMEOUT)
                    assert response.status_code == 200
                    print(f"✅ {service_name} is running")
                except Exception as e:
                    print(f"❌ {service_name} failed: {e}")
                    return False
            
            # Test optional services (log but don't fail)
            for service_name, url in optional_services:
                try:
                    response = await client.get(url, timeout=TIMEOUT)
                    if response.status_code == 200:
                        print(f"✅ {service_name} is running")
                    else:
                        print(f"⚠️ {service_name} returned status {response.status_code}")
                except Exception as e:
                    print(f"⚠️ {service_name} not available: {e}")
        
        return True

    async def test_end_to_end_interview_flow(self):
        """Test complete end-to-end interview creation flow."""
        print("🔄 Testing end-to-end interview flow...")
        
        async with httpx.AsyncClient() as client:
            # Step 1: Create interview room via Interview
            room_payload = {
                "candidateId": "integration-test-candidate",
                "interviewerId": "integration-test-interviewer",
                "scheduledTime": "2025-08-20T16:00:00Z",
                "duration": 30
            }
            
            room_response = await client.post(
                f"{INTERVIEW_SERVICE_URL}/create-interview-room",
                json=room_payload,
                timeout=TIMEOUT
            )
            
            assert room_response.status_code == 200
            room_data = room_response.json()
            assert room_data["success"] == True
            
            room_name = room_data["room_name"]
            custom_url = room_data["custom_meet_url"]
            
            print(f"✅ Room created: {room_name}")
            
            # Step 2: Test custom Jitsi interface
            jitsi_response = await client.get(custom_url, timeout=TIMEOUT)
            assert jitsi_response.status_code == 200
            assert "TalentAI Interview" in jitsi_response.text
            
            print("✅ Custom Jitsi interface accessible")
            
            # Step 3: Test Avatar service voice generation (mock implementation)
            voice_payload = {
                "text": f"Welcome to your interview, integration test candidate! I'm Interview, and I'll be conducting your interview today.",
                "voice_id": "mock_voice"
            }
            
            voice_response = await client.post(
                f"{AVATAR_SERVICE_URL}/api/v1/generate-voice",
                json=voice_payload,
                timeout=TIMEOUT
            )
            
            assert voice_response.status_code == 200
            voice_data = voice_response.json()
            assert "success" in voice_data
            assert voice_data["success"] == False  # Mock implementation
            assert "error" in voice_data
            
            print("✅ Voice generation request processed (mock)")
            
            return True

    async def test_performance_under_load(self):
        """Test system performance with concurrent requests."""
        print("⚡ Testing performance under load...")
        
        async def create_concurrent_room(candidate_id: str):
            async with httpx.AsyncClient() as client:
                start_time = time.time()
                response = await client.post(
                    f"{INTERVIEW_SERVICE_URL}/create-interview-room",
                    json={"candidateId": f"load-test-{candidate_id}", "interviewerId": "load-interviewer"},
                    timeout=TIMEOUT
                )
                end_time = time.time()
                return response.status_code == 200, end_time - start_time
        
        # Create 10 concurrent room creation requests
        tasks = [create_concurrent_room(f"candidate-{i}") for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for success, _ in results if success)
        response_times = [time_taken for _, time_taken in results]
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        print(f"✅ Concurrent load test: {success_count}/10 successful")
        print(f"✅ Average response time: {avg_response_time:.3f}s")
        print(f"✅ Max response time: {max_response_time:.3f}s")
        
        # Performance assertions
        assert success_count >= 9  # At least 90% success rate
        assert avg_response_time < 1.0  # Average response < 1s
        assert max_response_time < 2.0  # Max response < 2s
        
        return True

    async def test_error_handling_resilience(self):
        """Test error handling and service resilience."""
        print("🛡️ Testing error handling and resilience...")
        
        async with httpx.AsyncClient() as client:
            # Test 1: Invalid endpoints
            invalid_endpoints = [
                f"{AVATAR_SERVICE_URL}/invalid-endpoint",
                f"{INTERVIEW_SERVICE_URL}/nonexistent-path"
            ]
            
            for endpoint in invalid_endpoints:
                response = await client.get(endpoint, timeout=TIMEOUT)
                assert response.status_code == 404
                print(f"✅ 404 handling: {endpoint}")
            
            # Test 2: Malformed requests
            malformed_response = await client.post(
                f"{INTERVIEW_SERVICE_URL}/create-interview-room",
                content="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=TIMEOUT
            )
            assert malformed_response.status_code == 422
            print("✅ Malformed JSON handling")
            
            # Test 3: Missing required fields
            empty_voice_request = await client.post(
                f"{AVATAR_SERVICE_URL}/api/v1/generate-voice",
                json={},  # Missing required 'text' field
                timeout=TIMEOUT
            )
            assert empty_voice_request.status_code == 422
            print("✅ Validation error handling")
            
        return True

    async def test_service_dependencies(self):
        """Test service dependencies and communication patterns."""
        print("🔗 Testing service dependencies...")
        
        async with httpx.AsyncClient() as client:
            # Test Avatar service can be called from Interview context
            # This simulates how Interview would call Avatar for voice generation
            
            # Step 1: Create interview session
            interview_payload = {
                "search_criteria": {
                    "job_title": "Integration Test Engineer",
                    "required_skills": ["Testing", "Python"],
                    "nice_to_have_skills": ["Automation"],
                    "company_culture": ["Quality", "Innovation"],
                    "experience_level": "Mid-level"
                },
                "candidate_profile": {
                    "full_name": "Integration Test User",
                    "source_url": "https://test.example.com",
                    "summary": "Test candidate for integration testing",
                    "work_experience": [],
                    "education": [],
                    "skills": {"matched": ["Testing", "Python"], "unmatched": []},
                    "alignment_score": 0.9,
                    "initial_questions": []
                }
            }
            
            interview_response = await client.post(
                f"{INTERVIEW_SERVICE_URL}/api/v1/interview/start",
                json=interview_payload,
                timeout=TIMEOUT
            )
            
            assert interview_response.status_code == 200
            interview_data = interview_response.json()
            
            # Check if Avatar service integration is mentioned
            assert "avatar_ready" in interview_data or "voice_generation" in interview_data
            print("✅ Service dependency test passed")
            
        return True

    async def test_api_consistency(self):
        """Test API response consistency and structure."""
        print("📋 Testing API consistency...")
        
        async with httpx.AsyncClient() as client:
            # Test Avatar service API consistency
            avatar_health = await client.get(f"{AVATAR_SERVICE_URL}/health", timeout=TIMEOUT)
            avatar_data = avatar_health.json()
            
            required_avatar_fields = ["status", "voice_integration"]
            for field in required_avatar_fields:
                assert field in avatar_data, f"Missing field in Avatar health: {field}"
            
            # Test Interview service API consistency  
            interview_health = await client.get(f"{INTERVIEW_SERVICE_URL}/", timeout=TIMEOUT)
            interview_data = interview_health.json()
            
            assert "status" in interview_data
            
            # Test room creation response structure
            room_response = await client.post(
                f"{INTERVIEW_SERVICE_URL}/create-interview-room",
                json={"candidateId": "api-test", "interviewerId": "api-interviewer"},
                timeout=TIMEOUT
            )
            
            room_data = room_response.json()
            required_room_fields = ["success", "room_id", "room_name", "custom_meet_url", "message"]
            for field in required_room_fields:
                assert field in room_data, f"Missing field in room creation: {field}"
            
            print("✅ API consistency test passed")
            
        return True


async def run_integration_tests():
    """Run all integration tests."""
    print("🧪 Starting TalentAI Integration Test Suite")
    print("=" * 60)
    
    test_suite = IntegrationTestSuite()
    
    try:
        # Basic service availability
        if not await test_suite.test_all_services_running():
            print("❌ Service availability test failed")
            return False
        
        # Core functionality tests
        if not await test_suite.test_end_to_end_interview_flow():
            print("❌ End-to-end interview flow test failed")
            return False
        
        # Performance tests
        if not await test_suite.test_performance_under_load():
            print("❌ Performance under load test failed")
            return False
        
        # Resilience tests
        if not await test_suite.test_error_handling_resilience():
            print("❌ Error handling resilience test failed")
            return False
        
        # Dependency tests
        if not await test_suite.test_service_dependencies():
            print("❌ Service dependencies test failed")
            return False
        
        # API consistency tests
        if not await test_suite.test_api_consistency():
            print("❌ API consistency test failed")
            return False
        
        print("=" * 60)
        print("✅ All integration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(run_integration_tests())
        print(f"\n🎉 Integration Test Suite: {'PASSED' if result else 'FAILED'}")
        exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Integration test suite failed with error: {e}")
        exit(1)