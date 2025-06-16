#!/bin/bash
#
# Setup script for Synthesis - Execution Engine for Tekton
#

# Exit on error
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
TEKTON_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$SCRIPT_DIR"

echo "Setting up Synthesis - Execution Engine for Tekton"

# Check for Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required but not found. Please install Python 3."
    exit 1
fi

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

# Install tekton-core if it exists
if [ -d "$TEKTON_ROOT/tekton-core" ]; then
    echo "Installing tekton-core..."
    pip install -e "$TEKTON_ROOT/tekton-core"
fi

# Install dependencies
echo "Installing dependencies..."
pip install -e .

# Install additional dependencies for API and async operations
echo "Installing additional API dependencies..."
pip install fastapi uvicorn aiohttp pydantic

# Install dev dependencies
echo "Installing development dependencies..."
pip install pytest pytest-asyncio pytest-cov black isort mypy

# Create log directory
echo "Creating log directory..."
mkdir -p logs

# Create data directories
echo "Creating data directories..."
mkdir -p "$TEKTON_ROOT/.tekton/synthesis/data"

# Create configuration file if it doesn't exist
CONFIG_DIR="$TEKTON_ROOT/.tekton/synthesis"
CONFIG_FILE="$CONFIG_DIR/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default configuration file..."
    mkdir -p "$CONFIG_DIR"
    cat > "$CONFIG_FILE" << EOL
{
    "port": 8009,
    "log_level": "INFO",
    "max_concurrent_executions": 10,
    "data_dir": "$TEKTON_ROOT/.tekton/synthesis/data",
    "enable_remote_execution": false,
    "enable_telemetry": true
}
EOL
    echo "Created default configuration at $CONFIG_FILE"
fi

# Make run_synthesis.sh executable
if [ -f "$TEKTON_ROOT/run_synthesis.sh" ]; then
    chmod +x "$TEKTON_ROOT/run_synthesis.sh"
    echo "Made run_synthesis.sh executable"
fi

echo "Setup complete!"
echo "To activate the virtual environment, run: source venv/bin/activate"
echo "To run Synthesis, use: $TEKTON_ROOT/run_synthesis.sh"
