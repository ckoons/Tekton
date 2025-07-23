#!/bin/bash
# Script to manually populate Athena with Tekton component relationships

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEKTON_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔄 Populating Athena with Tekton component relationships..."

# Run the population script
python3 "$TEKTON_ROOT/populate_athena_relationships.py"

if [ $? -eq 0 ]; then
    echo "✅ Successfully populated Athena"
else
    echo "❌ Failed to populate Athena"
    exit 1
fi