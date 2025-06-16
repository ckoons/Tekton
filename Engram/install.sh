#!/bin/bash
# Engram Installation Script
# This script installs Engram and its dependencies

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BIN_DIR="$HOME/bin"

# Create bin directory if it doesn't exist
if [ ! -d "$BIN_DIR" ]; then
    echo "Creating $BIN_DIR directory..."
    mkdir -p "$BIN_DIR"
    
    # Check if $BIN_DIR is in PATH, if not, add it
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo "Adding $BIN_DIR to PATH in your shell profile..."
        
        # Determine shell profile
        if [ -f "$HOME/.zshrc" ]; then
            PROFILE="$HOME/.zshrc"
        elif [ -f "$HOME/.bashrc" ]; then
            PROFILE="$HOME/.bashrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            PROFILE="$HOME/.bash_profile"
        else
            PROFILE="$HOME/.profile"
        fi
        
        # Add to profile
        echo 'export PATH="$HOME/bin:$PATH"' >> "$PROFILE"
        echo "Added $BIN_DIR to PATH in $PROFILE"
        echo "You'll need to restart your terminal or run 'source $PROFILE' for this to take effect"
    fi
fi

# Create symbolic link for engram launcher
echo "Creating symbolic link for 'engram' command..."
ln -sf "$SCRIPT_DIR/utils/engram_launcher.sh" "$BIN_DIR/engram"
chmod +x "$BIN_DIR/engram"

# Check for UV and install if needed
if ! command -v uv &> /dev/null; then
    echo "UV not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add UV to PATH if not already added by installer
    if ! command -v uv &> /dev/null; then
        echo "Adding UV to PATH..."
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
fi

# Install Python dependencies
echo "Installing Python dependencies with UV..."

# Create and use virtual environment
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment with UV..."
    uv venv "$SCRIPT_DIR/venv" --python=python3.10
fi

# Install in the virtual environment
echo "Installing dependencies in virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"
uv pip install -r "$SCRIPT_DIR/requirements.txt"
uv pip install requests urllib3 pydantic==2.10.6 fastapi python-dotenv
deactivate

# Make sure scripts are executable
chmod +x "$SCRIPT_DIR/utils/engram_launcher.sh"
chmod +x "$SCRIPT_DIR/core/engram_with_claude"
chmod +x "$SCRIPT_DIR/utils/engram_check.py"
chmod +x "$SCRIPT_DIR/core/engram_consolidated"

echo ""
echo "Engram installed successfully!"
echo ""
echo "Usage:"
echo "  engram                     # Start Claude with Engram memory service"
echo ""
echo "In Claude Code sessions:"
echo "  from engram.cli.quickmem import m, t, r, w, l, c, k, f, i, x, s, a, p, v"
echo ""