#!/usr/bin/env python
"""Thin CLI wrapper: `python scripts/generate_synthetic_dataset.py --out demo.json`."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.data.inject_conflicts import _main  # noqa: E402

if __name__ == "__main__":
    _main()
