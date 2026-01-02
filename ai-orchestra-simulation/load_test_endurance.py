#!/usr/bin/env python3
"""
Endurance Test for Avatar Renderer
Tests 25 concurrent users for 30 minutes
"""

import asyncio
import json
import os
import statistics
import time
from datetime import datetime

import httpx
import psutil

# Configuration
SERVER_URL = "http://localhost:3001"
CONCURRENT_USERS = 25
TEST_DURATION = 1800  # 30 minutes
REQUESTS_PER_USER = 100  # Total requests per user during test

# Sample phoneme data for testing
SAMPLE_PHONEMES = [
    {"phoneme": "AA", "start": 0.0, "end": 0.1},
    {"phoneme": "EH", "start": 0.1, "end": 0.2},
    {"phoneme": "IH", "start": 0.2, "end": 0.3},
    {"phoneme": "OH", "start": 0.3, "end": 0.4},
    {"phoneme": "UH", "start": 0.4, "end": 0.5},
]


class EnduranceTester:
    def __init__(self):
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
        self.request_count = 0
        self.performance_windows = []

    async def make_request(self, client, user_id, request_id):
        """Make a single render request"""
        payload = {"phonemes": SAMPLE_PHONEMES, "duration": 0.5}

        start_time = time.time()
        try:
            response = await client.post(f"{SERVER_URL}/render/lipsync", json=payload, timeout=60.0)

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
                    "error_message": response.text[:200],
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
                "error_message": str(e)[:200],
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

                # Realistic delay between requests (1-5 seconds)
                delay = 1.0 + (user_id % 3) * 0.5 + (request_id % 5) * 0.2
                await asyncio.sleep(delay)

    def get_system_stats(self):
        """Get current system resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_mb": psutil.virtual_memory().used / 1024 / 1024,
            "disk_usage_percent": psutil.disk_usage("/").percent,
            "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
            "network_connections": len(psutil.net_connections()),
            "open_files": len(psutil.Process().open_files()) if psutil.Process() else 0,
            "timestamp": datetime.now().isoformat(),
        }

    async def run_test(self):
        """Run the endurance test"""
        print("🏃 Starting Endurance Test")
        print(f"   Server: {SERVER_URL}")
        print(f"   Concurrent Users: {CONCURRENT_USERS}")
        print(f"   Test Duration: {TEST_DURATION} seconds ({TEST_DURATION//60} minutes)")
        print(f"   Requests per User: {REQUESTS_PER_USER}")
        print("-" * 60)

        self.start_time = time.time()

        # Start monitoring tasks
        monitor_task = asyncio.create_task(self.monitor_system())
        performance_task = asyncio.create_task(self.monitor_performance())

        # Create user tasks
        user_tasks = []
        for user_id in range(CONCURRENT_USERS):
            task = asyncio.create_task(self.user_worker(user_id))
            user_tasks.append(task)

        # Wait for all user tasks to complete or timeout
        try:
            await asyncio.wait_for(asyncio.gather(*user_tasks), timeout=TEST_DURATION)
        except asyncio.TimeoutError:
            print("⏰ Test duration reached, stopping...")

        # Stop monitoring
        monitor_task.cancel()
        performance_task.cancel()

        self.end_time = time.time()
        await self.generate_report()

    async def monitor_system(self):
        """Monitor system resources during test"""
        system_stats = []
        while True:
            try:
                stats = self.get_system_stats()
                system_stats.append(stats)
                await asyncio.sleep(30)  # Monitor every 30 seconds for endurance test
            except asyncio.CancelledError:
                break

        # Save system stats
        with open("load_test_endurance_system_stats.json", "w") as f:
            json.dump(system_stats, f, indent=2)

    async def monitor_performance(self):
        """Monitor performance metrics over time"""
        while True:
            try:
                window_start = time.time()
                await asyncio.sleep(300)  # 5-minute windows
                window_end = time.time()

                # Calculate metrics for this window
                window_results = [
                    r
                    for r in self.results
                    if window_start
                    <= datetime.fromisoformat(r["timestamp"]).timestamp()
                    <= window_end
                ]
                window_errors = [
                    e
                    for e in self.errors
                    if window_start
                    <= datetime.fromisoformat(e["timestamp"]).timestamp()
                    <= window_end
                ]

                if window_results:
                    avg_response_time = statistics.mean(
                        [r["response_time"] for r in window_results]
                    )
                    success_rate = len(window_results) / (len(window_results) + len(window_errors))
                    throughput = len(window_results) / 300  # requests per second

                    window_data = {
                        "window_start": datetime.fromtimestamp(window_start).isoformat(),
                        "window_end": datetime.fromtimestamp(window_end).isoformat(),
                        "requests": len(window_results),
                        "errors": len(window_errors),
                        "avg_response_time": avg_response_time,
                        "success_rate": success_rate,
                        "throughput_rps": throughput,
                    }
                    self.performance_windows.append(window_data)

            except asyncio.CancelledError:
                break

        # Save performance windows
        with open("load_test_endurance_performance.json", "w") as f:
            json.dump(self.performance_windows, f, indent=2)

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
                    "test_type": "Endurance Test",
                    "server_url": SERVER_URL,
                    "concurrent_users": CONCURRENT_USERS,
                    "test_duration_seconds": total_time,
                    "test_duration_minutes": total_time / 60,
                    "requests_per_user": REQUESTS_PER_USER,
                    "timestamp": datetime.now().isoformat(),
                },
                "summary": {
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "error_requests": error_requests,
                    "success_rate": f"{(successful_requests/total_requests)*100:.2f}%"
                    if total_requests > 0
                    else "0%",
                    "requests_per_second": f"{total_requests/total_time:.2f}",
                    "average_response_time": f"{statistics.mean(response_times):.3f}s",
                    "median_response_time": f"{statistics.median(response_times):.3f}s",
                    "min_response_time": f"{min(response_times):.3f}s",
                    "max_response_time": f"{max(response_times):.3f}s",
                    "95th_percentile_response_time": f"{statistics.quantiles(response_times, n=20)[18]:.3f}s",
                    "99th_percentile_response_time": f"{statistics.quantiles(response_times, n=20)[19]:.3f}s",
                    "average_processing_time": f"{statistics.mean(processing_times):.1f}ms",
                },
                "endurance_analysis": self.analyze_endurance(),
                "performance_trends": self.performance_windows,
                "errors": self.errors[:30],  # First 30 errors
                "recommendations": self.generate_recommendations(),
            }
        else:
            report = {
                "test_info": {
                    "test_type": "Endurance Test",
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
                "recommendations": [
                    "Server appears to be down or unreachable during endurance test"
                ],
            }

        # Save detailed results
        with open("load_test_endurance_results.json", "w") as f:
            json.dump(self.results, f, indent=2)

        with open("load_test_endurance_errors.json", "w") as f:
            json.dump(self.errors, f, indent=2)

        with open("load_test_endurance_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Print summary to console
        print("\n📊 ENDURANCE TEST RESULTS")
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
        print(f"Test Duration: {total_time:.2f}s ({total_time/60:.1f} minutes)")

        if "endurance_analysis" in report:
            print("\n🏃 ENDURANCE ANALYSIS:")
            for key, value in report["endurance_analysis"].items():
                print(f"   {key}: {value}")

        if report["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")

        print("\n📁 Results saved to load_test_endurance_*.json files")

    def analyze_endurance(self):
        """Analyze endurance characteristics"""
        if not self.performance_windows:
            return {}

        # Analyze performance degradation over time
        response_times = [
            w["avg_response_time"] for w in self.performance_windows if "avg_response_time" in w
        ]
        success_rates = [w["success_rate"] for w in self.performance_windows if "success_rate" in w]
        throughputs = [
            w["throughput_rps"] for w in self.performance_windows if "throughput_rps" in w
        ]

        degradation_analysis = "Unknown"
        if len(response_times) > 1:
            first_avg = response_times[0]
            last_avg = response_times[-1]
            degradation_percent = ((last_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0

            if degradation_percent < 10:
                degradation_analysis = f"Stable (+{degradation_percent:.1f}%)"
            elif degradation_percent < 25:
                degradation_analysis = f"Moderate degradation (+{degradation_percent:.1f}%)"
            elif degradation_percent < 50:
                degradation_analysis = f"Significant degradation (+{degradation_percent:.1f}%)"
            else:
                degradation_analysis = f"Severe degradation (+{degradation_percent:.1f}%)"

        # Analyze success rate stability
        success_stability = "Unknown"
        if len(success_rates) > 1:
            success_std = statistics.stdev(success_rates) if len(success_rates) > 1 else 0
            if success_std < 0.02:
                success_stability = "Very Stable"
            elif success_std < 0.05:
                success_stability = "Stable"
            elif success_std < 0.1:
                success_stability = "Moderate"
            else:
                success_stability = "Unstable"

        # Memory leak detection (if system stats available)
        memory_trend = "Unknown"
        try:
            with open("load_test_endurance_system_stats.json") as f:
                system_stats = json.load(f)
                if len(system_stats) > 5:
                    memory_values = [
                        s["memory_used_mb"] for s in system_stats if "memory_used_mb" in s
                    ]
                    if len(memory_values) > 1:
                        first_memory = memory_values[0]
                        last_memory = memory_values[-1]
                        memory_growth = (
                            ((last_memory - first_memory) / first_memory) * 100
                            if first_memory > 0
                            else 0
                        )

                        if memory_growth < 5:
                            memory_trend = f"Stable (+{memory_growth:.1f}%)"
                        elif memory_growth < 15:
                            memory_trend = f"Moderate growth (+{memory_growth:.1f}%)"
                        else:
                            memory_trend = f"Potential leak (+{memory_growth:.1f}%)"
        except:
            pass

        return {
            "performance_degradation": degradation_analysis,
            "success_rate_stability": success_stability,
            "memory_trend": memory_trend,
            "total_windows_analyzed": len(self.performance_windows),
            "average_throughput": f"{statistics.mean(throughputs):.2f} rps"
            if throughputs
            else "N/A",
        }

    def generate_recommendations(self):
        """Generate recommendations based on endurance test results"""
        recommendations = []

        if len(self.errors) > len(self.results) * 0.15:  # More than 15% errors
            recommendations.append(
                "CRITICAL: High error rate during endurance - investigate resource leaks"
            )

        if self.results:
            avg_response_time = statistics.mean([r["response_time"] for r in self.results])
            if avg_response_time > 8.0:
                recommendations.append(
                    "WARNING: Average response time > 8s during endurance - monitor resource usage"
                )

            success_rate = len(self.results) / (len(self.results) + len(self.errors))
            if success_rate < 0.9:
                recommendations.append(
                    "CRITICAL: Success rate < 90% during endurance - not suitable for production"
                )

            # Check for performance degradation
            if self.performance_windows:
                response_times = [w.get("avg_response_time", 0) for w in self.performance_windows]
                if len(response_times) > 1 and response_times[-1] > response_times[0] * 1.5:
                    recommendations.append(
                        "WARNING: Significant performance degradation over time - possible memory/resource leaks"
                    )

        if len(recommendations) == 0:
            recommendations.append(
                "✅ Endurance test passed - server maintains performance over 30 minutes"
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
                print("✅ Server is healthy and ready for endurance testing")
            else:
                print(f"⚠️  Server health check failed: {response.status_code}")
                return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the avatar renderer is running on port 3001")
        return

    print("⚠️  WARNING: This test runs for 30 minutes. Ensure system is stable.")
    print("   Recommended: Monitor system resources during test")
    input("Press Enter to continue or Ctrl+C to abort...")

    # Run the test
    tester = EnduranceTester()
    await tester.run_test()


if __name__ == "__main__":
    asyncio.run(main())
