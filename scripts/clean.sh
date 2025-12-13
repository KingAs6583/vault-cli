#!/usr/bin/env bash
set -e

echo "Cleaning project..."

rm -rf \
  build \
  dist \
  __pycache__ \
  .pytest_cache \
  *.spec

find . -type d -name "__pycache__" -exec rm -rf {} +

echo "Clean complete."

# Ensure scripts are executable in a cross-platform manner - no-op on Windows
chmod +x scripts/*.sh 2>/dev/null || true
