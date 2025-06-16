#!/bin/bash

# Setup script for Metis component
# This script initializes the Metis environment

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR" || exit 1

echo "Setting up Metis environment..."

# Create virtual environment using uv
uv venv

# Activate the virtual environment
source .venv/bin/activate || source venv/bin/activate

# Install dependencies
echo "Installing dependencies with uv..."
uv pip install -e .

echo "Metis setup complete!"
echo "You can now run Metis using './run_metis.sh'"