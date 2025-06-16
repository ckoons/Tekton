#!/bin/bash
# Install Auto-Approved Tekton MCP for Claude
# 
# This script installs the enhanced Hermes bridge with automatic tool approval
# and AI onboarding capabilities.
# Check if the first argument is -r or --remove or -h or --help for usage"

if [ "$#" -gt 0 ]; then
  if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "install_tekton_mcps.sh [-h | --help | -r | --remove]"
    exit 0;
  fi
fi

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "=========================================="
echo "  Tekton Auto-Approved MCP Installation"
echo "=========================================="
echo ""

# Check if claude command exists
if ! command -v claude &> /dev/null; then
    echo -e "${RED}Error: 'claude' command not found${NC}"
    echo "Please ensure Claude Desktop is installed and the CLI is available in your PATH"
    exit 1
fi

# Remove any existing Tekton MCP installations
echo -e "${YELLOW}Removing existing Tekton MCP installations...${NC}"
claude mcp remove -s user tekton 2>/dev/null || true
claude mcp remove -s user tekton-auto 2>/dev/null || true

# Check if the first argument is -r or --remove or -h or --help for usage"
if [ "$#" -gt 0 ]; then
  if [ "$1" == "-r" ] || [ "$1" == "--remove" ]; then
    echo "Remove only option selected"
    exit 0;
  fi
fi

# Get the absolute path to the auto-approved bridge script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEKTON_ROOT="$(dirname "$SCRIPT_DIR")"
BRIDGE_SCRIPT="$TEKTON_ROOT/Hermes/hermes/api/mcp_auto_approve.py"

# Check if bridge script exists
if [ ! -f "$BRIDGE_SCRIPT" ]; then
    echo -e "${RED}Error: Auto-approved MCP bridge script not found at $BRIDGE_SCRIPT${NC}"
    exit 1
fi

# Make the bridge script executable
chmod +x "$BRIDGE_SCRIPT"

# Install the auto-approved bridge
echo -e "${YELLOW}Installing Tekton with automatic approval...${NC}"

# For CLI use
claude mcp add tekton -s user python "$BRIDGE_SCRIPT"

# Update Claude Desktop config for auto-approval
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
if [ -f "$CLAUDE_CONFIG" ]; then
    echo -e "${YELLOW}Updating Claude Desktop configuration...${NC}"
    
    # Backup existing config
    cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup"
    
    # Update config with jq if available, otherwise use Python
    if command -v jq &> /dev/null; then
        jq '.mcpServers.tekton = {
            "command": "python",
            "args": ["'$BRIDGE_SCRIPT'"],
            "alwaysAllow": true,
            "metadata": {
                "autoApprove": true,
                "type": "cognitive-system"
            }
        }' "$CLAUDE_CONFIG" > "$CLAUDE_CONFIG.tmp" && mv "$CLAUDE_CONFIG.tmp" "$CLAUDE_CONFIG"
    else
        python3 -c "
import json
config_path = '$CLAUDE_CONFIG'
with open(config_path, 'r') as f:
    config = json.load(f)
    
if 'mcpServers' not in config:
    config['mcpServers'] = {}
    
config['mcpServers']['tekton'] = {
    'command': 'python',
    'args': ['$BRIDGE_SCRIPT'],
    'alwaysAllow': True,
    'metadata': {
        'autoApprove': True,
        'type': 'cognitive-system'
    }
}

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
"
    fi
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Installation complete!${NC}"
    echo ""
    echo -e "${BLUE}Features enabled:${NC}"
    echo "  • All Tekton tools are pre-approved (no Y/N prompts)"
    echo "  • AI onboarding system activated"
    echo "  • Enhanced tool categorization"
    echo "  • Memory-based identity support"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Ensure all Tekton components are running"
    echo "  2. Restart Claude Desktop if it's open"
    echo "  3. Start Claude: claude"
    echo "  4. Try: 'Show me the Tekton onboarding guide'"
    echo ""
    echo -e "${BLUE}Onboarding prompts available:${NC}"
    echo "  • /prompt tekton_onboarding - Introduction to Tekton"
    echo "  • /prompt component_roles - Learn about each AI's personality"
    echo "  • /prompt memory_guide - How to live in your memory"
    echo "  • /prompt collaboration_guide - Working as a collective"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Installation failed${NC}"
    exit 1
fi
