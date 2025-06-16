#!/bin/bash

# Setup script for Apollo

set -e  # Exit on error

# Ensure the script is run from the Apollo directory
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -U pip
pip install -r requirements.txt

# Install package in development mode
echo "Installing Apollo in development mode..."
pip install -e .

# Make run script executable
chmod +x run_apollo.sh

echo "Apollo setup complete!"
echo "Run './run_apollo.sh' to start the Apollo server."