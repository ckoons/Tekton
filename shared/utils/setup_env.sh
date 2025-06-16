#!/bin/bash
# Shared environment setup for Tekton components
# Usage: source "$TEKTON_ROOT/shared/utils/setup_env.sh"

# Set up Python path (avoid duplicates)
setup_pythonpath() {
    local script_dir="$1"
    local tekton_root="$2"
    
    case ":$PYTHONPATH:" in
        *":$tekton_root:"*) ;;
        *) export PYTHONPATH="$tekton_root:$PYTHONPATH" ;;
    esac
    case ":$PYTHONPATH:" in
        *":$script_dir:"*) ;;
        *) export PYTHONPATH="$script_dir:$PYTHONPATH" ;;
    esac
}

# Load Tekton environment configuration
load_tekton_env() {
    local tekton_root="$1"
    if [ -f "$tekton_root/.env.tekton" ]; then
        set -a  # Enable auto-export
        source "$tekton_root/.env.tekton"
        set +a  # Disable auto-export
    fi
}

# Complete setup - call this from run scripts
setup_tekton_env() {
    local script_dir="$1"
    local tekton_root="$2"
    
    setup_pythonpath "$script_dir" "$tekton_root"
    load_tekton_env "$tekton_root"
}