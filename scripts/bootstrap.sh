#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo " Enterprise RAG Platform — Bootstrap Setup"
echo "=================================================="

# Check Python version
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "✔ Found Python: $PY_VER"
else
    echo "❌ Python 3 is not installed or not in PATH."
    exit 1
fi

# Ensure .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✔ .env created"
else
    echo "✔ .env already exists"
fi

# Set up virtual environment
if command -v uv &>/dev/null; then
    echo "Setting up virtual environment with uv..."
    uv venv --python 3.11
    source .venv/bin/activate || source .venv/Scripts/activate
    uv pip install -e ".[dev]"
else
    echo "uv not found; falling back to python venv and pip..."
    python3 -m venv .venv
    source .venv/bin/activate || source .venv/Scripts/activate
    pip install --upgrade pip
    pip install -e ".[dev]"
fi

# Install pre-commit hooks if available
if command -v pre-commit &>/dev/null; then
    pre-commit install
    echo "✔ Pre-commit hooks installed"
fi

echo "=================================================="
echo " Bootstrap complete! Run 'docker compose up -d' or 'make up' to start services."
echo "=================================================="
