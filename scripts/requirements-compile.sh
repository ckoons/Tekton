#!/bin/bash
# Requirements compilation script for Tekton using UV

set -e

# ANSI colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERBOSE="-v"  # Use -v for less detail, -vvv for more detail

# Check for UV and install if needed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV not found. Installing...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add UV to PATH if not already added by installer
    if ! command -v uv &> /dev/null; then
        echo -e "${YELLOW}Adding UV to PATH...${NC}"
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
fi

echo -e "${BLUE}Compiling requirements for all Tekton components...${NC}"

# Components to process
COMPONENTS=(tekton-core Athena Engram Ergon Rhetor Telos Harmonia Sophia Synthesis Hermes Prometheus)

# Process each component
for component in "${COMPONENTS[@]}"; do
    COMPONENT_DIR="$SCRIPT_DIR/$component"
    
    if [ ! -d "$COMPONENT_DIR" ]; then
        echo -e "${YELLOW}Component directory not found: $component, skipping${NC}"
        continue
    fi
    
    echo -e "${BLUE}Processing $component requirements...${NC}"
    
    # Check if component has requirements.in
    if [ -f "$COMPONENT_DIR/requirements.in" ]; then
        echo -e "${GREEN}Compiling $component/requirements.in to requirements.txt${NC}"
        
        uv pip compile $VERBOSE \
            --output-file="$COMPONENT_DIR/requirements.txt" \
            "$COMPONENT_DIR/requirements.in"
            
    # Check if component has setup.py but no requirements.in
    elif [ -f "$COMPONENT_DIR/setup.py" ]; then
        echo -e "${YELLOW}$component has setup.py but no requirements.in, extracting requirements...${NC}"
        
        # Create temporary requirements.in from setup.py
        TMP_REQUIREMENTS="$COMPONENT_DIR/requirements.in.tmp"
        python -c "
import re
import sys

with open('$COMPONENT_DIR/setup.py', 'r') as f:
    setup_py = f.read()

# Extract install_requires section
install_requires = re.search(r'install_requires=\[([^\]]+)\]', setup_py)
if install_requires:
    reqs = install_requires.group(1)
    # Clean up the requirements
    reqs = re.sub(r'[\'\"]([\w\-=<>\.]+)[\'\"]', r'\1', reqs)
    requirements = [r.strip() for r in reqs.split(',') if r.strip()]
    
    # Write to temporary file
    with open('$TMP_REQUIREMENTS', 'w') as out:
        for req in requirements:
            out.write(req + '\n')
    print('Generated requirements.in from setup.py')
else:
    print('No install_requires found in setup.py')
    sys.exit(1)
"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Compiling extracted requirements for $component${NC}"
            uv pip compile $VERBOSE \
                --output-file="$COMPONENT_DIR/requirements.txt" \
                "$TMP_REQUIREMENTS"
            
            rm "$TMP_REQUIREMENTS"
        else
            echo -e "${RED}Failed to extract requirements from $component/setup.py${NC}"
        fi
    else
        echo -e "${YELLOW}No requirements.in or setup.py found for $component, skipping${NC}"
    fi
done

# Special handling for Codex which has its own compilation script
if [ -d "$SCRIPT_DIR/Codex" ] && [ -f "$SCRIPT_DIR/Codex/scripts/pip-compile.sh" ]; then
    echo -e "${BLUE}Processing Codex requirements using its own script...${NC}"
    (cd "$SCRIPT_DIR/Codex" && bash scripts/pip-compile.sh)
fi

echo -e "${GREEN}All requirements compiled successfully!${NC}"