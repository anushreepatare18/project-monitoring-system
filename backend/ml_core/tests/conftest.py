"""conftest.py — makes project root importable for all tests."""
import sys
import os

# Ensure the repo root (SIH26103/) is on PYTHONPATH
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
