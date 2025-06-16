#!/bin/bash
# setup_symlinks.sh - Create symlinks for Tekton scripts in ~/utils

# Create the ~/utils directory if it doesn't exist
mkdir -p ~/utils

# Get the absolute path to the scripts directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create symlink for tekton_client.py
echo "Creating symlink for tekton_client.py in ~/utils..."
ln -sf "${SCRIPT_DIR}/tekton_client.py" ~/utils/tekton_client

# Create symlink for tekton.py (main Tekton suite launcher)
echo "Creating symlink for tekton.py in ~/utils..."
ln -sf "${SCRIPT_DIR}/tekton.py" ~/utils/tekton

# Make sure the symlinks are executable
chmod +x ~/utils/tekton_client
chmod +x ~/utils/tekton

echo "Symlinks created successfully."
echo "You can now run the following commands (if ~/utils is in your PATH):"
echo "  - tekton_client - Launch individual AI clients with Tekton integration"
echo "  - tekton - Unified Tekton suite launcher to start/stop all components"