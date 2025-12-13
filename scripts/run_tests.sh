#!/usr/bin/env bash
set -e

# Run tests for the project. Assumes environment has dev dependencies installed.
# Return non-zero exit code if tests fail.
pytest -q
