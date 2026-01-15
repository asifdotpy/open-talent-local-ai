"""
Test Suite Runner for Avatar Integration

Runs comprehensive tests for Phase 1 and Phase 2 implementations:
- Phase 1: Voice Service Phoneme Extraction
- Phase 2: Avatar Service Real Rendering
- End-to-end integration tests

Usage:
    python run_avatar_tests.py              # Run all tests
    python run_avatar_tests.py --unit       # Run only unit tests
    python run_avatar_tests.py --integration # Run only integration tests
    python run_avatar_tests.py --quick      # Run quick tests only
    python run_avatar_tests.py --verbose    # Run with verbose output

Requirements:
    - Voice service running on port 8002
    - Avatar service running on port 8001
    - Avatar renderer running on port 3001

Created: November 11, 2025
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text):
    """Print formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def check_services():
    """Check if required services are running."""
    import httpx

    services = {
        "Voice Service": "http://localhost:8002/health",
        "Avatar Service": "http://localhost:8001/health",
        "Avatar Renderer": "http://localhost:3001/health",
    }

    all_running = True

    print_header("Checking Services")

    for name, url in services.items():
        try:
            response = httpx.get(url, timeout=5.0)
            if response.status_code == 200:
                print_success(f"{name} is running")
            else:
                print_error(f"{name} returned status {response.status_code}")
                all_running = False
        except Exception as e:
            print_error(f"{name} is not reachable: {e}")
            all_running = False

    if not all_running:
        print_warning("\nSome services are not running. Some tests may fail.")
        print_info("Start services with:")
        print_info(
            "  Voice service: cd microservices/voice-service && source .venv/bin/activate && python main.py"
        )
        print_info(
            "  Avatar service: cd microservices/avatar-service && source venv/bin/activate && python main.py"
        )
        print_info("  Avatar renderer: cd ai-orchestra-simulation && node avatar-renderer-v2.js")
        response = input("\nContinue anyway? [y/N]: ")
        if response.lower() != "y":
            sys.exit(1)

    return all_running


def run_tests(test_type, verbose=False, markers=None):
    """Run pytest with specified configuration."""
    project_root = Path(__file__).parent.parent

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    # Add test paths based on type
    if test_type == "unit":
        cmd.append(str(project_root / "tests" / "unit"))
    elif test_type == "integration":
        cmd.append(str(project_root / "tests" / "integration"))
    elif test_type == "all":
        cmd.append(str(project_root / "tests"))
    else:
        cmd.append(test_type)  # Custom path

    # Add options
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    cmd.extend(["--tb=short", "--color=yes", f"--rootdir={project_root}"])

    # Add markers if specified
    if markers:
        cmd.extend(["-m", markers])

    # Add coverage if running all tests
    if test_type == "all":
        cmd.extend(
            [
                "--cov=microservices/voice-service",
                "--cov=microservices/avatar-service",
                "--cov-report=term-missing",
                "--cov-report=html",
            ]
        )

    print_info(f"Running: {' '.join(cmd)}\n")

    # Run tests
    start_time = time.time()
    result = subprocess.run(cmd, cwd=project_root)
    elapsed = time.time() - start_time

    print(f"\n{Colors.BOLD}Test execution time: {elapsed:.2f}s{Colors.ENDC}")

    return result.returncode


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description="Run Avatar Integration Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_avatar_tests.py                    # Run all tests
  python run_avatar_tests.py --unit             # Unit tests only
  python run_avatar_tests.py --integration      # Integration tests only
  python run_avatar_tests.py --quick            # Quick tests only
  python run_avatar_tests.py --verbose          # Verbose output
  python run_avatar_tests.py --no-service-check # Skip service check
        """,
    )

    parser.add_argument("--unit", action="store_true", help="Run only unit tests")

    parser.add_argument("--integration", action="store_true", help="Run only integration tests")

    parser.add_argument(
        "--quick", action="store_true", help="Run only quick tests (exclude slow tests)"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    parser.add_argument(
        "--no-service-check", action="store_true", help="Skip service availability check"
    )

    parser.add_argument("--path", type=str, help="Run tests from specific path")

    args = parser.parse_args()

    # Print banner
    print_header("Avatar Integration Test Suite")
    print(f"{Colors.BOLD}Phase 1:{Colors.ENDC} Voice Service Phoneme Extraction")
    print(f"{Colors.BOLD}Phase 2:{Colors.ENDC} Avatar Service Real Rendering")
    print()

    # Check services unless skipped
    if not args.no_service_check:
        try:
            check_services()
        except ModuleNotFoundError:
            print_warning("httpx not installed, skipping service check")
            print_info("Install with: pip install httpx")

    # Determine test type
    if args.path:
        test_type = args.path
    elif args.unit:
        test_type = "unit"
    elif args.integration:
        test_type = "integration"
    else:
        test_type = "all"

    # Determine markers
    markers = None
    if args.quick:
        markers = "not slow"

    # Run tests
    print_header(f"Running {test_type.upper()} Tests")

    exit_code = run_tests(test_type, verbose=args.verbose, markers=markers)

    # Print summary
    print_header("Test Summary")

    if exit_code == 0:
        print_success("All tests passed!")
        print_info("\nPhase 1: Voice Service Phoneme Extraction ✓")
        print_info("Phase 2: Avatar Service Real Rendering ✓")
        print_info("End-to-end Integration ✓")
    else:
        print_error("Some tests failed")
        print_info("\nCheck the output above for details")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
