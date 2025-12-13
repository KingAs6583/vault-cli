# scripts/build_binary.ps1
# Build standalone Vault CLI binary for Windows

$ErrorActionPreference = "Stop"

Write-Host "🔐 Building Vault CLI binary..." -ForegroundColor Cyan

# Ensure venv exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found. Run setup.sh first." -ForegroundColor Red
    exit 1
}

# Activate venv
.\venv\Scripts\Activate.ps1

# Install build dependencies
pip install --upgrade pip pyinstaller

# Clean old builds
if (Test-Path "build") { Remove-Item build -Recurse -Force }
if (Test-Path "dist") { Remove-Item dist -Recurse -Force }

# Build binary
pyinstaller `
  --onefile `
  --name vault `
  --clean `
  src/vault/cli.py

Write-Host "✅ Build complete!" -ForegroundColor Green
Write-Host "📦 Binary available at: dist\vault.exe" -ForegroundColor Yellow
