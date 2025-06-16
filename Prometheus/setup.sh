#!/bin/bash
# Setup script for Prometheus/Epimethius
set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install the package in development mode
echo "Installing Prometheus/Epimethius in development mode..."
pip install -e .

# Install development dependencies
echo "Installing development dependencies..."
pip install -e ".[dev]"

# Set up environment variables
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# Prometheus/Epimethius configuration
PROMETHEUS_PORT=8006
HERMES_URL=http://localhost:8000/api
TELOS_URL=http://localhost:8008/api
RHETOR_URL=http://localhost:8005/api
ENGRAM_URL=http://localhost:8001/api
EOL
    echo ".env file created"
fi

# Create log directory if it doesn't exist
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "Created logs directory"
fi

# Register with Hermes if available
if command -v curl &> /dev/null; then
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health 2>/dev/null | grep -q "200"; then
        echo "Registering with Hermes..."
        python register_with_hermes.py
    else
        echo "Hermes is not running. Will need to register later."
    fi
else
    echo "curl not found. Please register with Hermes manually."
fi

echo "Setup complete!"
echo "To start the server: python -m prometheus.api.app"