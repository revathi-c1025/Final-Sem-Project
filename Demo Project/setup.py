#!/usr/bin/env python3
"""
Setup Wizard for AI-Powered Agentic Test Automation System
This script helps initialize the project on a new system.
"""

import os
import sys
import subprocess
import json


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")


def print_step(step_num, text):
    """Print a step indicator."""
    print(f"[{step_num}] {text}")


def check_python_version():
    """Check if Python version is compatible."""
    print_step(1, "Checking Python version...")
    version = sys.version_info
    print(f"   Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   [ERROR] Python 3.8 or higher is required")
        return False
    print("   [OK] Python version is compatible")
    return True


def check_pip():
    """Check if pip is available."""
    print_step(2, "Checking pip availability...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                      capture_output=True, check=True)
        print("   [OK] pip is available")
        return True
    except subprocess.CalledProcessError:
        print("   [ERROR] pip is not available")
        return False


def install_dependencies():
    """Install required dependencies."""
    print_step(3, "Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r",
                        "requirements.txt"], check=True)
        print("   [OK] Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   [ERROR] Failed to install dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    print_step(4, "Creating project directories...")
    directories = [
        "generated_tests",
        "logs",
        "reports",
        "output"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   [OK] Created directory: {directory}")

    return True


def check_config_file():
    """Check if config file exists."""
    print_step(5, "Checking configuration file...")
    if os.path.isfile("config.py"):
        print("   [OK] config.py exists")
        return True
    else:
        print("   [ERROR] config.py not found")
        return False


def check_test_data():
    """Check if demo test data exists."""
    print_step(6, "Checking demo test data...")
    if os.path.isfile("demo_testcases.json"):
        print("   [OK] demo_testcases.json exists")
        try:
            with open("demo_testcases.json", "r") as f:
                data = json.load(f)
                print(f"   [OK] Found {len(data)} test cases in demo data")
        except json.JSONDecodeError:
            print("   [WARNING] demo_testcases.json has invalid JSON")
        return True
    else:
        print("   [ERROR] demo_testcases.json not found")
        return False


def check_reference_repo():
    """Check if reference repository exists."""
    print_step(7, "Checking reference test repository...")
    repo_path = "demo_reference_tests"
    if os.path.isdir(repo_path):
        print(f"   [OK] Reference repository exists: {repo_path}")
        return True
    else:
        print(f"   [WARNING] Reference repository not found: {repo_path}")
        print("   The system will work without it, but test generation may be limited")
        return True  # Not a critical error


def run_basic_test():
    """Run a basic import test."""
    print_step(8, "Running basic import test...")
    try:
        # Test basic imports
        import flask
        import pytest
        print("   [OK] Basic imports successful")
        return True
    except ImportError as e:
        print(f"   [ERROR] Import test failed: {e}")
        return False


def print_summary(results):
    """Print setup summary."""
    print_header("Setup Summary")

    all_passed = all(results.values())

    for step, passed in results.items():
        status = "[OK]" if passed else "[FAILED]"
        print(f"{status}: {step}")

    print()

    if all_passed:
        print("[SUCCESS] Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the application:")
        print("   - Windows: run.bat")
        print("   - Linux/Mac: ./run.sh")
        print("   - Or: python app.py")
        print("\n2. Open your browser to: http://localhost:5001")
        print("\n3. Check the README.md for detailed usage instructions")
    else:
        print("[WARNING] Setup completed with some errors.")
        print("Please fix the errors above before running the application.")
        print("\nFor help, check the README.md file.")


def main():
    """Main setup wizard function."""
    print_header("AI-Powered Test Automation System - Setup Wizard")

    print("This wizard will help you set up the project on your system.")
    print("Please ensure you have Python 3.8+ and internet connection for dependencies.\n")

    results = {}

    # Run all checks
    results["Python version check"] = check_python_version()
    if not results["Python version check"]:
        print_summary(results)
        sys.exit(1)

    results["pip availability"] = check_pip()
    if not results["pip availability"]:
        print_summary(results)
        sys.exit(1)

    results["Dependency installation"] = install_dependencies()
    if not results["Dependency installation"]:
        print_summary(results)
        sys.exit(1)

    results["Directory creation"] = create_directories()
    results["Configuration file"] = check_config_file()
    results["Demo test data"] = check_test_data()
    results["Reference repository"] = check_reference_repo()
    results["Basic import test"] = run_basic_test()

    # Print summary
    print_summary(results)

    # Exit with appropriate code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
