#!/usr/bin/env python3
"""
CI/CD Pipeline Verification Script

Verifies that the CI/CD pipeline components are properly configured and functional.
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_section(title: str):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def run_command(cmd: List[str], cwd: str = None) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def check_git_status() -> bool:
    """Check git repository status"""
    print_section("Git Repository Status")

    # Check if we're in a git repo
    code, stdout, stderr = run_command(["git", "rev-parse", "--git-dir"])
    if code != 0:
        print_error("Not a git repository")
        return False
    print_success("Git repository detected")

    # Get current branch
    code, stdout, stderr = run_command(["git", "branch", "--show-current"])
    if code == 0:
        branch = stdout.strip()
        print_success(f"Current branch: {branch}")

    # Check remote
    code, stdout, stderr = run_command(["git", "remote", "-v"])
    if code == 0:
        print_success("Git remote configured")
        for line in stdout.strip().split('\n')[:2]:  # Show first 2 lines
            print(f"  {line}")

    return True


def check_workflow_files() -> bool:
    """Check GitHub Actions workflow files"""
    print_section("GitHub Actions Workflow Files")

    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print_error("No .github/workflows directory found")
        return False

    print_success(f"Workflows directory exists: {workflows_dir}")

    workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    if not workflow_files:
        print_error("No workflow files found")
        return False

    print_success(f"Found {len(workflow_files)} workflow file(s):")
    for wf in workflow_files:
        print(f"  • {wf.name}")

        # Parse and validate workflow
        with open(wf) as f:
            content = f.read()
            if "runs-on: self-hosted" in content:
                print_success(f"    Uses self-hosted runner ✓")
            if "pytest" in content:
                print_success(f"    Includes pytest tests ✓")
            if "flake8" in content:
                print_success(f"    Includes flake8 linting ✓")

    return True


def check_test_suite() -> bool:
    """Check test suite configuration"""
    print_section("Test Suite Configuration")

    # Check for pytest.ini or pyproject.toml
    pytest_ini = Path("pytest.ini")
    if pytest_ini.exists():
        print_success("pytest.ini found")
        with open(pytest_ini) as f:
            content = f.read()
            if "testpaths" in content:
                print_success("  Test paths configured")
            if "markers" in content:
                print_success("  Test markers configured")
    else:
        print_warning("No pytest.ini found")

    # Check tests directory
    tests_dir = Path("tests")
    if tests_dir.exists():
        print_success(f"Tests directory exists: {tests_dir}")

        # Count test files
        test_files = list(tests_dir.rglob("test_*.py"))
        print_success(f"Found {len(test_files)} test files")

        # Check for conftest.py
        if (tests_dir / "conftest.py").exists():
            print_success("  conftest.py found (fixtures configured)")

        # Check test organization
        subdirs = [d for d in tests_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
        if subdirs:
            print_success(f"  Test organization: {', '.join(d.name for d in subdirs)}")
    else:
        print_error("No tests directory found")
        return False

    return True


def check_dependencies() -> bool:
    """Check Python dependencies"""
    print_section("Python Dependencies")

    # Check requirements files
    req_files = ["requirements.txt", "requirements-dev.txt"]
    for req_file in req_files:
        if Path(req_file).exists():
            print_success(f"{req_file} found")
        else:
            print_warning(f"{req_file} not found")

    # Check if pytest is available
    code, stdout, stderr = run_command([sys.executable, "-m", "pytest", "--version"])
    if code == 0:
        version = stdout.strip()
        print_success(f"pytest available: {version}")
    else:
        print_warning("pytest not installed in current environment")

    # Check if flake8 is available
    code, stdout, stderr = run_command([sys.executable, "-m", "flake8", "--version"])
    if code == 0:
        version = stdout.strip().split('\n')[0]
        print_success(f"flake8 available: {version}")
    else:
        print_warning("flake8 not installed in current environment")

    return True


def check_self_hosted_runner() -> bool:
    """Check for self-hosted runner configuration"""
    print_section("Self-Hosted Runner Status")

    # Check if we can access runner info
    # Note: This requires appropriate permissions
    code, stdout, stderr = run_command(["gh", "run", "list", "--limit", "1"])
    if code == 0:
        print_success("GitHub CLI access configured")
        print("Recent workflow run:")
        print(f"  {stdout.strip()}")
    else:
        print_warning("Cannot access GitHub Actions runs (gh CLI may need authentication)")

    return True


def run_sample_tests() -> bool:
    """Run a sample of tests to verify they work"""
    print_section("Sample Test Execution")

    # Run a quick test
    print("Running sample tests...")
    code, stdout, stderr = run_command(
        [sys.executable, "-m", "pytest", "tests/unit/test_config.py", "-v", "--tb=short"]
    )

    if code == 0:
        print_success("Sample tests passed")
        # Show summary
        for line in stdout.split('\n'):
            if 'passed' in line or 'PASSED' in line or 'failed' in line or 'FAILED' in line:
                print(f"  {line}")
    else:
        print_warning("Sample tests had issues")
        print(f"Exit code: {code}")
        if stderr:
            print(f"Error: {stderr[:500]}")

    return code == 0


def generate_report() -> Dict:
    """Generate a comprehensive status report"""
    print_section("CI/CD Pipeline Verification Report")

    checks = {
        "Git Repository": check_git_status(),
        "Workflow Files": check_workflow_files(),
        "Test Suite": check_test_suite(),
        "Dependencies": check_dependencies(),
        "Self-Hosted Runner": check_self_hosted_runner(),
    }

    # Optional: run sample tests
    try:
        checks["Sample Tests"] = run_sample_tests()
    except Exception as e:
        print_error(f"Could not run sample tests: {e}")
        checks["Sample Tests"] = False

    return checks


def main():
    """Main verification routine"""
    print(f"\n{Colors.BOLD}Omnix CI/CD Pipeline Verification Tool{Colors.RESET}")
    print(f"Working directory: {os.getcwd()}\n")

    # Run all checks
    results = generate_report()

    # Summary
    print_section("Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check, status in results.items():
        if status:
            print_success(f"{check}: OK")
        else:
            print_error(f"{check}: FAILED")

    print(f"\n{Colors.BOLD}Results: {passed}/{total} checks passed{Colors.RESET}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ CI/CD pipeline is fully operational!{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some checks failed. Review the report above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
