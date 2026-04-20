"""
Shared fixtures and configuration for ShopEasy demo test suite.
"""
import os
import sys

# Ensure the shopease_framework package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shopease_framework"))
