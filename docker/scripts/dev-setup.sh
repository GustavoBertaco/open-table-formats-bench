#!/bin/bash

# Development environment setup script

# Exit on error
set -e

# Install system dependencies
apt-get update && apt-get install -y \
    git \
    curl \
    build-essential

# Clean up apt cache
rm -rf /var/lib/apt/lists/*

# Install Python development tools
pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy

# Install project dependencies
pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Create necessary directories
mkdir -p /app/data
mkdir -p /app/logs

# Set up Git hooks
cp /app/docker/scripts/pre-commit.sh /app/.git/hooks/pre-commit
chmod +x /app/.git/hooks/pre-commit

echo "Development environment setup complete!"