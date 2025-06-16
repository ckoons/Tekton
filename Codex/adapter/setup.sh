#!/bin/bash
# Setup script for Codex adapter

echo "Setting up Codex adapter for Tekton..."

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CODEX_DIR="$( dirname "$SCRIPT_DIR" )"
TEKTON_ROOT="$( dirname "$CODEX_DIR" )"

# Set up Python path
export PYTHONPATH="$TEKTON_ROOT:$PYTHONPATH"

# Install adapter dependencies
echo "Installing Python dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p "$TEKTON_ROOT/Hephaestus/hephaestus/ui/static/component"

# Copy component template to Hephaestus
TEMPLATE_SOURCE="$CODEX_DIR/ui/component_template.html"
TEMPLATE_DEST="$TEKTON_ROOT/Hephaestus/hephaestus/ui/static/component/codex.html"

if [ -f "$TEMPLATE_SOURCE" ]; then
    echo "Copying component template to Hephaestus..."
    cp "$TEMPLATE_SOURCE" "$TEMPLATE_DEST"
else
    echo "Warning: Component template not found at $TEMPLATE_SOURCE"
fi

# Register with Hermes
echo "Registering Codex with Hermes..."
python "$SCRIPT_DIR/register_with_hermes.py"

echo "Setup complete!"
echo "You can now launch the Codex component using the launch-tekton.sh script."