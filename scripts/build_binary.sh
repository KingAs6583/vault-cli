#!/bin/bash
set -e

echo "Building Vault CLI binary..."
pyinstaller --onefile \
  --name vault \
  --clean \
  src/vault/cli.py

echo "Binary created in dist/"
