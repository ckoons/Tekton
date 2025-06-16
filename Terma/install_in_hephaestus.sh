#\!/bin/bash
# 
# Terma Installation Script for Hephaestus
#
# This script installs the Terma terminal component into the Hephaestus UI system,
# creating the necessary symlinks and registering the component with Hephaestus.
#

# Exit on error
set -e

# Get the path to the script directory
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# Detect Hephaestus directory
HEPHAESTUS_DIR="${SCRIPT_DIR}/../Hephaestus"
if [ \! -d "$HEPHAESTUS_DIR" ]; then
    echo "Error: Hephaestus directory not found at $HEPHAESTUS_DIR"
    echo "Please specify the Hephaestus directory path:"
    read -r HEPHAESTUS_DIR
    
    if [ \! -d "$HEPHAESTUS_DIR" ]; then
        echo "Error: Invalid Hephaestus directory: $HEPHAESTUS_DIR"
        exit 1
    fi
fi

echo "==== Installing Terma Terminal Component in Hephaestus ===="
echo "Hephaestus directory: $HEPHAESTUS_DIR"
echo "Terma directory: $SCRIPT_DIR"
echo ""

# Create directories if they don't exist
mkdir -p "${HEPHAESTUS_DIR}/ui/components/terma"
mkdir -p "${HEPHAESTUS_DIR}/ui/scripts/terma"
mkdir -p "${HEPHAESTUS_DIR}/ui/styles/terma"

# Copy or symlink the Terma component files
echo "Creating symlinks for Terma component files..."

# Create symlink for the component HTML
ln -sf "${SCRIPT_DIR}/ui/hephaestus/terma-component.html" "${HEPHAESTUS_DIR}/ui/components/terma/terma-component.html"

# Create symlinks for the component JavaScript files
mkdir -p "${HEPHAESTUS_DIR}/ui/scripts/terma"
ln -sf "${SCRIPT_DIR}/ui/hephaestus/js/terma-component.js" "${HEPHAESTUS_DIR}/ui/scripts/terma/terma-component.js"
ln -sf "${SCRIPT_DIR}/ui/js/terma-terminal.js" "${HEPHAESTUS_DIR}/ui/scripts/terma/terma-terminal.js"

# Create symlinks for the component CSS files
mkdir -p "${HEPHAESTUS_DIR}/ui/styles/terma"
ln -sf "${SCRIPT_DIR}/ui/hephaestus/css/terma-hephaestus.css" "${HEPHAESTUS_DIR}/ui/styles/terma/terma-hephaestus.css"
ln -sf "${SCRIPT_DIR}/ui/css/terma-terminal.css" "${HEPHAESTUS_DIR}/ui/styles/terma/terma-terminal.css"

# Create a ui/css and ui/js directory in case it's needed directly
mkdir -p "${HEPHAESTUS_DIR}/ui/css"
mkdir -p "${HEPHAESTUS_DIR}/ui/js"

# Create symlinks in ui/css and ui/js for direct access
ln -sf "${SCRIPT_DIR}/ui/css/terma-terminal.css" "${HEPHAESTUS_DIR}/ui/css/terma-terminal.css"
ln -sf "${SCRIPT_DIR}/ui/js/terma-terminal.js" "${HEPHAESTUS_DIR}/ui/js/terma-terminal.js"

# Note about fixed ports - we're using explicit ports in the code now
echo "Note: Using fixed ports: 8765 for API server and 8767 for WebSocket server"
echo "These ports match the TERMA_API_PORT and TERMA_WS_PORT values in tekton-launch"

# Add the component to the Hephaestus component registry
REGISTRY_FILE="${HEPHAESTUS_DIR}/ui/server/component_registry.json"

# Check if Terma is already in the component registry
if grep -q "\"id\": \"terma\"" "$REGISTRY_FILE"; then
    echo "Terma is already in the component registry"
else
    echo "Adding Terma to the component registry..."
    
    # Create a backup of the registry file
    cp "$REGISTRY_FILE" "${REGISTRY_FILE}.bak"
    
    # Add Terma to the components array
    TMP_FILE=$(mktemp)
    jq '.components = [{
      "id": "terma",
      "name": "Terma",
      "description": "Advanced terminal environment",
      "icon": "🖥️",
      "defaultMode": "html",
      "capabilities": ["terminal", "command_execution", "shell_access"]
    }] + .components' "$REGISTRY_FILE" > "$TMP_FILE" && mv "$TMP_FILE" "$REGISTRY_FILE"
    
    echo "Terma added to the component registry"
fi

# Check if terminal settings are already in the settings template
SETTINGS_FILE="${HEPHAESTUS_DIR}/ui/components/settings.html"
if grep -q "Terminal Settings" "$SETTINGS_FILE"; then
    echo "Terminal settings already exist in the settings UI"
else
    echo "Note: The Terminal Settings section needs to be manually added to the Hephaestus settings UI."
    echo "Please refer to the documentation in /Users/cskoons/projects/github/Tekton/Terma/docs/PHASE_3.5_COMPLETED.md"
fi

# Add required API routes to the Hephaestus server
SERVER_FILE="${HEPHAESTUS_DIR}/ui/server/server.py"
if [ -f "$SERVER_FILE" ]; then
    # Check if the server already has Terma API route
    if grep -q "/terma/" "$SERVER_FILE"; then
        echo "Terma API routes already added to Hephaestus server"
    else
        echo "Adding Terma API routes to Hephaestus server..."
        
        # Look for the line where routes are defined
        ROUTES_LINE=$(grep -n "app.add_api_route" "$SERVER_FILE" | head -n 1 | cut -d ':' -f 1)
        
        if [ -n "$ROUTES_LINE" ]; then
            # Create a temporary file with the new routes
            sed "${ROUTES_LINE}i\\
# Terma terminal routes\\
@app.get('/terma/ui/{path:path}')\\
async def serve_terma_ui(path: str):\\
    \"\"\"Serve Terma UI files\"\"\"\\
    terma_ui_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'Terma', 'ui')\\
    file_path = os.path.join(terma_ui_dir, path)\\
    if os.path.exists(file_path) and os.path.isfile(file_path):\\
        return FileResponse(file_path)\\
    raise HTTPException(status_code=404, detail=f\"Terma UI file {path} not found\")\\
" "$SERVER_FILE" > "${SERVER_FILE}.tmp"
            
            # Replace the server file
            mv "${SERVER_FILE}.tmp" "$SERVER_FILE"
        else
            echo "Warning: Could not find the right location to add Terma API routes"
            echo "Please manually add the following routes to ${SERVER_FILE}:"
            echo '@app.get("/terma/ui/{path:path}")'
            echo 'async def serve_terma_ui(path: str):'
            echo '    """Serve Terma UI files"""'
            echo '    terma_ui_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "Terma", "ui")'
            echo '    file_path = os.path.join(terma_ui_dir, path)'
            echo '    if os.path.exists(file_path) and os.path.isfile(file_path):'
            echo '        return FileResponse(file_path)'
            echo '    raise HTTPException(status_code=404, detail=f"Terma UI file {path} not found")'
        fi
    fi
else
    echo "Warning: Hephaestus server file not found at $SERVER_FILE"
    echo "Please manually add the Terma API routes to your Hephaestus server"
fi

echo ""
echo "==== Terma Installation Complete ===="
echo "Terma terminal component has been successfully installed in Hephaestus."
echo "Restart the Hephaestus UI server to apply the changes."
echo ""
