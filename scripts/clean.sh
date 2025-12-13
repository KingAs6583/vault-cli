#!/usr/bin/env bash
set -e

echo "🧹 Cleaning project..."

rm -rf \
  build \
  dist \
  __pycache__ \
  .pytest_cache \
  *.spec

find . -type d -name "__pycache__" -exec rm -rf {} +

echo "✅ Clean complete."
