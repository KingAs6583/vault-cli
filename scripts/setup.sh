#!/usr/bin/env bash
set -e

echo "🔐 Setting up Vault CLI development environment..."

# Create venv if missing
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "📦 Virtual environment created"
fi

# Activate venv
source venv/bin/activate

# Upgrade tooling
pip install --upgrade pip

# Install project in editable mode
pip install -e .

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  source venv/bin/activate"
echo "  vault setup"
