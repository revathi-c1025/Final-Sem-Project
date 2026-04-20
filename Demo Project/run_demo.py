#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo Script for Mid-Term Presentation
This script demonstrates the AI-Powered Agentic Test Automation System
using the standalone framework (recommended for demo).
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"{'='*70}")
    print(f"Command: {cmd}")
    print(f"{'-'*70}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    if result.returncode != 0:
        print(f"[X] Failed with exit code {result.returncode}")
        return False
    print(f"[OK] Success")
    return True

def main():
    """Run the demo."""
    print("\n" + "="*70)
    print("AI-Powered Agentic Test Automation System - Demo")
    print("="*70)
    print("\nThis demo showcases the standalone test framework")
    print("which generates and executes test cases without Atlas dependencies.")
    print("\nRecommended for mid-term demo presentation.")
    print("\n" + "="*70)

    # Step 1: Regenerate all test cases
    success = run_command(
        "py regenerate_tests.py",
        "Step 1: Generate all test cases using SimpleTestGenerator"
    )
    if not success:
        print("\n[X] Demo failed at test generation step")
        return 1

    # Step 2: Run all tests
    success = run_command(
        "py -m pytest generated_tests/ -v",
        "Step 2: Execute all test cases with pytest"
    )
    if not success:
        print("\n[X] Demo failed at test execution step")
        return 1

    # Step 3: Show summary
    print("\n" + "="*70)
    print("Demo Summary")
    print("="*70)
    print("[OK] All 10 test cases generated successfully")
    print("[OK] All 10 test cases passed")
    print("[OK] Using standalone framework (no Atlas dependencies)")
    print("[OK] System is ready for demonstration")
    print("\nGenerated test files are in: generated_tests/")
    print("Each test uses the standalone framework with mock API client")
    print("\n" + "="*70)
    print("Demo completed successfully!")
    print("="*70 + "\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
