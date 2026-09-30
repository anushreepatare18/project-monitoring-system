"""conftest.py — adds repo root to PYTHONPATH for all pragya_xai tests."""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
