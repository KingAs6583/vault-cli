#!/usr/bin/env python3
"""Cross-platform cleanup helper to remove build artifacts and caches.

This script mirrors scripts/clean.sh but is cross-platform for use in pre-commit hooks.
"""
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def remove_if_exists(path: Path):
    try:
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
    except Exception:
        # Ignore any permission or missing file errors
        pass

def main():
    print("🧹 Cleaning project (python)")
    patterns = [
        ROOT / "build",
        ROOT / "dist",
        ROOT / "__pycache__",
        ROOT / ".pytest_cache",
    ]
    for p in patterns:
        remove_if_exists(p)

    # remove top-level __pycache__ directories recursively
    for d in ROOT.rglob("__pycache__"):
        if d.is_dir():
            remove_if_exists(d)

    # Clean artifacts with wildcard patterns (e.g., *.spec)
    for spec in ROOT.glob("*.spec"):
        remove_if_exists(spec)

    print("✅ Clean complete.")

if __name__ == "__main__":
    main()
