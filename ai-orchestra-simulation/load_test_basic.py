#!/usr/bin/env python3
"""
Basic Load Test for Avatar Renderer
Tests 10 concurrent users for 5 minutes
"""

import asyncio
import json
import statistics
import time
from datetime import datetime

import httpx
import psutil

# Configuration
SERVER_URL = "http://localhost:3001"
CONCURRENT_USERS = 10
TEST_DURATION = 300  # 5 minutes
REQUESTS_PER_USER = 50  # Total requests per user during test

# Sample phoneme data for testing
SAMPLE_PHONEMES = [
    {"phoneme": "AA", "start": 0.0, "end": 0.1},
    {"phoneme": "EH", "start": 0.1, "end": 0.2},
    {"phoneme": "IH", "start": 0.2, "end": 0.3},
    {"phoneme": "OH", "start": 0.3, "end": 0.4},
    {"phoneme": "UH", "start": 0.4, "end": 0.5},
]


class LoadTester:
    def __init__(self):
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None

    async def make_request(self, client, user_id, request_id):
        """Make a single render request"""
        payload = {"phonemes": SAMPLE_PHONEMES, "duration": 0.5}

        start_time = time.time()
        try:
            response = await client.post(f"{SERVER_URL}/render/lipsync", json=payload, timeout=30.0)

            end_time = time.time()
            response_time = end_time - start_time

            if response.status_code == 200:
                content_length = len(response.content)
                processing_time = response.headers.get("X-Processing-Time", "0ms")
                processing_time = int(processing_time.replace("ms", ""))

                result = {
                    "user_id": user_id,
                    "request_id": request_id,
                    "status": "success",
                    "response_time": response_time,
                    "processing_time": processing_time,
                    "content_length": content_length,
                    "timestamp": datetime.now().isoformat(),
                }
                self.results.append(result)
                return result
            else:
                error = {
                    "user_id": user_id,
                    "request_id": request_id,
                    "status": "error",
                    "error_code": response.status_code,
                    "error_message": response.text,
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat(),
                }
                self.errors.append(error)
                return error

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            error = {
                "user_id": user_id,
                "request_id": request_id,
                "status": "exception",
                "error_message": str(e),
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
            }
            self.errors.append(error)
            return error

    async def user_worker(self, user_id):
        """Simulate a single user making requests"""
        async with httpx.AsyncClient() as client:
            for request_id in range(REQUESTS_PER_USER):
                await self.make_request(client, user_id, request_id)

                # Small delay between requests (0.1-0.5 seconds)
                await asyncio.sleep(0.1 + (user_id * 0.01))

    def get_system_stats(self):
        """Get current system resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_mb": psutil.virtual_memory().used / 1024 / 1024,
            "timestamp": datetime.now().isoformat(),
        }

    async def run_test(self):
        """Run the load test"""
        print("🚀 Starting Basic Load Test")
        print(f"   Server: {SERVER_URL}")
        print(f"   Concurrent Users: {CONCURRENT_USERS}")
        print(f"   Test Duration: {TEST_DURATION} seconds")
        print(f"   Requests per User: {REQUESTS_PER_USER}")
        print("-" * 60)

        self.start_time = time.time()

        # Start monitoring task
        monitor_task = asyncio.create_task(self.monitor_system())

        # Create user tasks
        user_tasks = []
        for user_id in range(CONCURRENT_USERS):
            task = asyncio.create_task(self.user_worker(user_id))
            user_tasks.append(task)

        # Wait for all user tasks to complete or timeout
        try:
            await asyncio.wait_for(asyncio.gather(*user_tasks), timeout=TEST_DURATION)
        except TimeoutError:
            print("⏰ Test duration reached, stopping...")

        # Stop monitoring
        monitor_task.cancel()

        self.end_time = time.time()
        await self.generate_report()

    async def monitor_system(self):
        """Monitor system resources during test"""
        system_stats = []
        while True:
            try:
                stats = self.get_system_stats()
                system_stats.append(stats)
                await asyncio.sleep(5)  # Monitor every 5 seconds
            except asyncio.CancelledError:
                break

        # Save system stats
        with open("load_test_basic_system_stats.json", "w") as f:
            json.dump(system_stats, f, indent=2)

    async def generate_report(self):
        """Generate comprehensive test report"""
        total_time = self.end_time - self.start_time
        total_requests = len(self.results) + len(self.errors)
        successful_requests = len(self.results)
        error_requests = len(self.errors)

        if self.results:
            response_times = [r["response_time"] for r in self.results]
            processing_times = [r["processing_time"] for r in self.results]

            report = {
                "test_info": {
                    "test_type": "Basic Load Test",
                    "server_url": SERVER_URL,
                    "concurrent_users": CONCURRENT_USERS,
                    "test_duration_seconds": total_time,
                    "requests_per_user": REQUESTS_PER_USER,
                    "timestamp": datetime.now().isoformat(),
                },
                "summary": {
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "error_requests": error_requests,
                    "success_rate": f"{(successful_requests / total_requests) * 100:.2f}%"
                    if total_requests > 0
                    else "0%",
                    "requests_per_second": f"{total_requests / total_time:.2f}",
                    "average_response_time": f"{statistics.mean(response_times):.3f}s",
                    "median_response_time": f"{statistics.median(response_times):.3f}s",
                    "min_response_time": f"{min(response_times):.3f}s",
                    "max_response_time": f"{max(response_times):.3f}s",
                    "95th_percentile_response_time": f"{statistics.quantiles(response_times, n=20)[18]:.3f}s",
                    "average_processing_time": f"{statistics.mean(processing_times):.1f}ms",
                },
                "errors": self.errors[:10],  # First 10 errors
                "recommendations": self.generate_recommendations(),
            }
        else:
            report = {
                "test_info": {
                    "test_type": "Basic Load Test",
                    "server_url": SERVER_URL,
                    "concurrent_users": CONCURRENT_USERS,
                    "test_duration_seconds": total_time,
                    "timestamp": datetime.now().isoformat(),
                },
                "summary": {
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "error_requests": error_requests,
                    "success_rate": "0%",
                    "error": "No successful requests",
                },
                "errors": self.errors,
                "recommendations": ["Server appears to be down or unreachable"],
            }

        # Save detailed results
        with open("load_test_basic_results.json", "w") as f:
            json.dump(self.results, f, indent=2)

        with open("load_test_basic_errors.json", "w") as f:
            json.dump(self.errors, f, indent=2)

        with open("load_test_basic_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Print summary to console
        print("\n📊 BASIC LOAD TEST RESULTS")
        print("=" * 50)
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {successful_requests}")
        print(f"Errors: {error_requests}")
        print(f"Success Rate: {report['summary'].get('success_rate', 'N/A')}")
        print(f"Requests/sec: {report['summary'].get('requests_per_second', 'N/A')}")
        if "average_response_time" in report["summary"]:
            print(f"Avg Response Time: {report['summary']['average_response_time']}")
            print(f"95th Percentile: {report['summary']['95th_percentile_response_time']}")
        print(f"Test Duration: {total_time:.2f}s")

        if report["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")

        print("\n📁 Results saved to load_test_basic_*.json files")

    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []

        if len(self.errors) > len(self.results) * 0.1:  # More than 10% errors
            recommendations.append(
                "High error rate detected - check server logs and resource usage"
            )

        if self.results:
            avg_response_time = statistics.mean([r["response_time"] for r in self.results])
            if avg_response_time > 5.0:
                recommendations.append(
                    "Average response time > 5s - consider optimizing rendering performance"
                )
            elif avg_response_time > 2.0:
                recommendations.append("Response time acceptable but could be improved")

            if statistics.quantiles([r["response_time"] for r in self.results], n=20)[18] > 10.0:
                recommendations.append(
                    "95th percentile response time > 10s - potential scaling issues"
                )

        if len(recommendations) == 0:
            recommendations.append(
                "✅ Basic load test passed - server handles 10 concurrent users well"
            )

        return recommendations


async def main():
    """Main entry point"""
    print("🎭 Avatar Renderer Load Test Suite")
    print("===================================")

    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVER_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ Server is healthy and ready for testing")
            else:
                print(f"⚠️  Server health check failed: {response.status_code}")
                return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the avatar renderer is running on port 3001")
        return

    # Run the test
    tester = LoadTester()
    await tester.run_test()


if __name__ == "__main__":
    asyncio.run(main())
