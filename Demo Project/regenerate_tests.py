#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Regenerate all test files using SimpleTestGenerator (standalone framework)
Use this script if the web UI accidentally overwrites test files with the old framework.
"""

import sys
import os

# Add current directory to path to ensure we use the correct modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Debug: Print which Python is being used
print(f"DEBUG: Python executable: {sys.executable}")
print(f"DEBUG: Current working directory: {os.getcwd()}")
print(f"DEBUG: Script directory: {os.path.dirname(os.path.abspath(__file__))}")

from simple_test_generator import SimpleTestGenerator
from agents.qtest_agent import QTestAgent

def main():
    print("Regenerating all test files using SimpleTestGenerator...")
    
    qtest = QTestAgent()
    gen = SimpleTestGenerator()
    
    for i in range(1, 51):
        tc_id = f'TC-{i:03d}'
        try:
            tc = qtest.fetch_test_case(tc_id)
            result = gen.generate_test(tc)
            print(f'[OK] Generated {tc_id}: {result["file_path"]}')
        except Exception as e:
            print(f'[FAIL] Failed to generate {tc_id}: {e}')
    
    print("\nAll test files regenerated successfully!")
    print("Run tests with: py -m pytest generated_tests/ -v")

if __name__ == "__main__":
    main()
