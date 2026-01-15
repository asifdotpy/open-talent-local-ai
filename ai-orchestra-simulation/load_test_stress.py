#!/usr/bin/env python3
"""
Stress Test for Avatar Renderer
Tests 50 concurrent users for 10 minutes
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
CONCURRENT_USERS = 50
TEST_DURATION = 600  # 10 minutes
REQUESTS_PER_USER = 20  # Total requests per user during test

# Sample phoneme data for testing
SAMPLE_PHONEMES = [
    {"phoneme": "AA", "start": 0.0, "end": 0.1},
    {"phoneme": "EH", "start": 0.1, "end": 0.2},
    {"phoneme": "IH", "start": 0.2, "end": 0.3},
    {"phoneme": "OH", "start": 0.3, "end": 0.4},
    {"phoneme": "UH", "start": 0.4, "end": 0.5},
]


class StressTester:
    def __init__(self):
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
        self.request_count = 0

    async def make_request(self, client, user_id, request_id):
        """Make a single render request"""
        payload = {"phonemes": SAMPLE_PHONEMES, "duration": 0.5}

        start_time = time.time()
        try:
            response = await client.post(
                f"{SERVER_URL}/render/lipsync",
                json=payload,
                timeout=60.0,  # Longer timeout for stress test
            )

            end_time = time.time()
            response_time = end_time - start_time

            self.request_count += 1

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
                    "error_message": response.text[:200],  # Truncate long error messages
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
                "error_message": str(e)[:200],  # Truncate long error messages
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

                # Variable delay between requests (0.5-2 seconds)
                delay = 0.5 + (user_id % 5) * 0.1 + (request_id % 3) * 0.2
                await asyncio.sleep(delay)

    def get_system_stats(self):
        """Get current system resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_mb": psutil.virtual_memory().used / 1024 / 1024,
            "disk_usage_percent": psutil.disk_usage("/").percent,
            "network_connections": len(psutil.net_connections()),
            "timestamp": datetime.now().isoformat(),
        }

    async def run_test(self):
        """Run the stress test"""
        print("🔥 Starting Stress Test")
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
                await asyncio.sleep(10)  # Monitor every 10 seconds for stress test
            except asyncio.CancelledError:
                break

        # Save system stats
        with open("load_test_stress_system_stats.json", "w") as f:
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
                    "test_type": "Stress Test",
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
                    "99th_percentile_response_time": f"{statistics.quantiles(response_times, n=20)[19]:.3f}s",
                    "average_processing_time": f"{statistics.mean(processing_times):.1f}ms",
                },
                "performance_analysis": self.analyze_performance(),
                "errors": self.errors[:20],  # First 20 errors
                "recommendations": self.generate_recommendations(),
            }
        else:
            report = {
                "test_info": {
                    "test_type": "Stress Test",
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
                "recommendations": ["Server appears to be down or unreachable under stress"],
            }

        # Save detailed results
        with open("load_test_stress_results.json", "w") as f:
            json.dump(self.results, f, indent=2)

        with open("load_test_stress_errors.json", "w") as f:
            json.dump(self.errors, f, indent=2)

        with open("load_test_stress_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Print summary to console
        print("\n📊 STRESS TEST RESULTS")
        print("=" * 50)
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {successful_requests}")
        print(f"Errors: {error_requests}")
        print(f"Success Rate: {report['summary'].get('success_rate', 'N/A')}")
        print(f"Requests/sec: {report['summary'].get('requests_per_second', 'N/A')}")
        if "average_response_time" in report["summary"]:
            print(f"Avg Response Time: {report['summary']['average_response_time']}")
            print(f"95th Percentile: {report['summary']['95th_percentile_response_time']}")
            print(f"99th Percentile: {report['summary']['99th_percentile_response_time']}")
        print(f"Test Duration: {total_time:.2f}s")

        if "performance_analysis" in report:
            print("\n📈 PERFORMANCE ANALYSIS:")
            for key, value in report["performance_analysis"].items():
                print(f"   {key}: {value}")

        if report["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")

        print("\n📁 Results saved to load_test_stress_*.json files")

    def analyze_performance(self):
        """Analyze performance characteristics"""
        if not self.results:
            return {}

        response_times = [r["response_time"] for r in self.results]

        # Calculate throughput stability
        time_windows = {}
        for result in self.results:
            window = int(result["timestamp"].split("T")[1].split(":")[1]) // 2  # 2-minute windows
            if window not in time_windows:
                time_windows[window] = []
            time_windows[window].append(result["response_time"])

        throughput_stability = "Unknown"
        if len(time_windows) > 1:
            window_rates = [
                len(times) / 120 for times in time_windows.values()
            ]  # requests per 2 minutes
            if window_rates:
                stability = (
                    statistics.stdev(window_rates) / statistics.mean(window_rates)
                    if statistics.mean(window_rates) > 0
                    else 0
                )
                if stability < 0.1:
                    throughput_stability = "Very Stable"
                elif stability < 0.25:
                    throughput_stability = "Stable"
                elif stability < 0.5:
                    throughput_stability = "Moderate"
                else:
                    throughput_stability = "Unstable"

        # Error pattern analysis
        error_rate_trend = "Unknown"
        if len(self.errors) > 10:
            # Check if errors are clustered at the end (resource exhaustion)
            error_timestamps = [e["timestamp"] for e in self.errors]
            if error_timestamps:
                first_error = min(error_timestamps)
                last_error = max(error_timestamps)
                error_span = (
                    datetime.fromisoformat(last_error) - datetime.fromisoformat(first_error)
                ).total_seconds()
                if error_span < total_time * 0.3:  # Errors concentrated in last 30%
                    error_rate_trend = "Increasing (possible resource exhaustion)"
                else:
                    error_rate_trend = "Distributed"

        return {
            "throughput_stability": throughput_stability,
            "error_rate_trend": error_rate_trend,
            "peak_concurrent_requests": f"{self.request_count} total",
            "memory_efficiency": "Monitor system stats for details",
        }

    def generate_recommendations(self):
        """Generate recommendations based on stress test results"""
        recommendations = []

        if len(self.errors) > len(self.results) * 0.2:  # More than 20% errors
            recommendations.append(
                "CRITICAL: High error rate under stress - server may need more resources"
            )
        elif len(self.errors) > len(self.results) * 0.1:  # More than 10% errors
            recommendations.append("WARNING: Moderate error rate - monitor closely in production")

        if self.results:
            avg_response_time = statistics.mean([r["response_time"] for r in self.results])
            if avg_response_time > 10.0:
                recommendations.append(
                    "CRITICAL: Average response time > 10s under stress - performance bottleneck"
                )
            elif avg_response_time > 5.0:
                recommendations.append("WARNING: Response time > 5s - may impact user experience")

            p99_response_time = statistics.quantiles(
                [r["response_time"] for r in self.results], n=20
            )[19]
            if p99_response_time > 30.0:
                recommendations.append(
                    "CRITICAL: 99th percentile > 30s - severe performance issues"
                )

            success_rate = len(self.results) / (len(self.results) + len(self.errors))
            if success_rate < 0.8:
                recommendations.append(
                    "CRITICAL: Success rate < 80% under stress - not production ready"
                )
            elif success_rate < 0.95:
                recommendations.append("WARNING: Success rate < 95% - monitor resource usage")

        if len(recommendations) == 0:
            recommendations.append(
                "✅ Stress test passed - server handles 50 concurrent users adequately"
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
                print("✅ Server is healthy and ready for stress testing")
            else:
                print(f"⚠️  Server health check failed: {response.status_code}")
                return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the avatar renderer is running on port 3001")
        return

    print("⚠️  WARNING: This test will generate high load. Ensure adequate system resources.")
    print("   Recommended: 16+ CPU cores, 32GB+ RAM, fast storage")
    input("Press Enter to continue or Ctrl+C to abort...")

    # Run the test
    tester = StressTester()
    await tester.run_test()


if __name__ == "__main__":
    asyncio.run(main())
