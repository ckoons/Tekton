#!/bin/bash
# Simple script to start the Tekton UI with Ergon display

# Navigate to Tekton root
cd "$(dirname "$0")/../"

# Ensure the components directory exists
mkdir -p ./Hephaestus/src/components/ergon

# Link the UI connector
ln -sf ../../../Ergon/ui_connector.js ./Hephaestus/src/components/ergon/ui_connector.js

# Start Hephaestus UI
echo "Starting Tekton UI..."
./hephaestus_launch