# tests/shared/performance/benchmarks.py
"""
Performance benchmarks and thresholds for the OpenTalent Platform.
All submodules should meet or exceed these performance standards.
"""

from typing import Any

# API Performance Benchmarks
API_BENCHMARKS = {
    "response_time": {
        "health_check": 100,  # ms
        "simple_query": 200,  # ms
        "complex_query": 500,  # ms
        "file_upload": 2000,  # ms
        "report_generation": 5000,  # ms
    },
    "throughput": {
        "requests_per_second": 1000,
        "concurrent_users": 100,
        "data_transfer_rate": 10 * 1024 * 1024,  # 10 MB/s
    },
    "error_rate": {
        "max_acceptable": 0.001,  # 0.1%
        "target": 0.0001,  # 0.01%
    },
    "availability": {
        "target_uptime": 0.999,  # 99.9%
        "critical_uptime": 0.9999,  # 99.99%
    },
}

# UI Performance Benchmarks
UI_BENCHMARKS = {
    "first_paint": 1500,  # ms
    "largest_contentful_paint": 2500,  # ms
    "first_input_delay": 100,  # ms
    "cumulative_layout_shift": 0.1,  # score
    "time_to_interactive": 3000,  # ms
    "bundle_size": 2 * 1024 * 1024,  # 2 MB
}

# Agent Performance Benchmarks
AGENT_BENCHMARKS = {
    "scoring_latency": 500,  # ms
    "analysis_time": 2000,  # ms
    "concurrent_requests": 100,
    "memory_usage": 512 * 1024 * 1024,  # 512 MB
    "cpu_usage": 80,  # percentage
}

# Database Performance Benchmarks
DATABASE_BENCHMARKS = {
    "query_time": {
        "simple_select": 50,  # ms
        "complex_join": 200,  # ms
        "bulk_insert": 1000,  # ms
    },
    "connection_pool": {
        "min_connections": 5,
        "max_connections": 50,
        "idle_timeout": 300,  # seconds
    },
    "cache_hit_rate": 0.95,  # 95%
}

# Voice/Audio Performance Benchmarks
VOICE_BENCHMARKS = {
    "synthesis_latency": 1000,  # ms
    "transcription_accuracy": 0.95,  # 95%
    "audio_quality": {
        "sample_rate": 44100,  # Hz
        "bit_depth": 16,
        "channels": 2,
    },
    "real_time_processing": 100,  # ms latency
}

# Avatar/Video Performance Benchmarks
AVATAR_BENCHMARKS = {
    "render_time": 200,  # ms per frame
    "frame_rate": 30,  # fps
    "video_quality": {
        "resolution": "1080p",
        "bitrate": 5000,  # kbps
        "codec": "H.264",
    },
    "lip_sync_accuracy": 0.9,  # 90%
}

# Load Testing Scenarios
LOAD_TEST_SCENARIOS = {
    "light_load": {
        "concurrent_users": 10,
        "duration": 60,  # seconds
        "ramp_up": 10,  # seconds
    },
    "normal_load": {
        "concurrent_users": 50,
        "duration": 300,  # seconds
        "ramp_up": 30,  # seconds
    },
    "peak_load": {
        "concurrent_users": 200,
        "duration": 600,  # seconds
        "ramp_up": 60,  # seconds
    },
    "stress_test": {
        "concurrent_users": 500,
        "duration": 300,  # seconds
        "ramp_up": 30,  # seconds
    },
}

# Performance Test Configuration
PERFORMANCE_TEST_CONFIG = {
    "warmup_time": 30,  # seconds
    "measurement_time": 60,  # seconds
    "cooldown_time": 30,  # seconds
    "percentiles": [50, 90, 95, 99, 99.9],
    "tolerance": 0.05,  # 5% tolerance for benchmarks
}


def get_benchmarks_for_service(service_name: str) -> dict[str, Any]:
    """Get performance benchmarks for a specific service"""
    benchmark_map = {
        "api": API_BENCHMARKS,
        "ui": UI_BENCHMARKS,
        "agents": AGENT_BENCHMARKS,
        "database": DATABASE_BENCHMARKS,
        "voice": VOICE_BENCHMARKS,
        "avatar": AVATAR_BENCHMARKS,
    }
    return benchmark_map.get(service_name, {})


def validate_performance_metric(metric_name: str, actual_value: float, service_name: str) -> bool:
    """Validate a performance metric against benchmarks"""
    benchmarks = get_benchmarks_for_service(service_name)

    # Navigate nested benchmark structure
    keys = metric_name.split(".")
    expected_value = benchmarks
    for key in keys:
        if isinstance(expected_value, dict) and key in expected_value:
            expected_value = expected_value[key]
        else:
            return False  # Metric not found in benchmarks

    if not isinstance(expected_value, (int, float)):
        return False  # Benchmark is not a numeric value

    # Apply tolerance
    tolerance = PERFORMANCE_TEST_CONFIG["tolerance"]
    min_acceptable = expected_value * (1 - tolerance)
    max_acceptable = expected_value * (1 + tolerance)

    return min_acceptable <= actual_value <= max_acceptable


def generate_performance_report(results: dict[str, Any], service_name: str) -> dict[str, Any]:
    """Generate a performance test report"""
    report = {
        "service": service_name,
        "timestamp": "2024-01-01T00:00:00Z",  # Should be current timestamp
        "benchmarks": get_benchmarks_for_service(service_name),
        "results": {},
        "passed": True,
        "failed_metrics": [],
    }

    for metric_name, actual_value in results.items():
        passed = validate_performance_metric(metric_name, actual_value, service_name)
        report["results"][metric_name] = {"actual": actual_value, "passed": passed}

        if not passed:
            report["passed"] = False
            report["failed_metrics"].append(metric_name)

    return report
