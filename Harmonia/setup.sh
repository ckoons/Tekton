#!/bin/bash
#
# Setup script for Harmonia - Workflow Orchestration Engine for Tekton
#

# Exit on error
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "Setting up Harmonia - Workflow Orchestration Engine for Tekton"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies including tekton-core
echo "Installing dependencies..."
pip install -e ../tekton-core
pip install -e .

# Install dev dependencies
if [ -f "requirements-dev.txt" ]; then
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Create data directories
echo "Creating data directories..."
mkdir -p ~/.harmonia/state
mkdir -p ~/.harmonia/workflows
mkdir -p logs

echo "Setup complete!"
echo "To activate the virtual environment, run: source venv/bin/activate"