# Tekton Shared Utilities Implementation

## Overview

This implementation provides a set of standardized shared utility libraries for the Tekton ecosystem. These utilities replace duplicated code across components, ensuring consistent behavior, improved maintainability, and unified error handling.

## Core Components

### 1. Shell Utility Libraries

The shell utility libraries provide common functions for Tekton scripts:

- **tekton-utils.sh**: Core utility functions for logging, directory detection, and command execution
- **tekton-ports.sh**: Port management for Tekton's Single Port Architecture
- **tekton-process.sh**: Process management for starting, stopping, and monitoring components
- **tekton-config.sh**: Configuration management from files and environment variables

### 2. Python Configuration Bridge

A Python CLI tool (`tekton-config-cli.py`) bridges bash scripts and Python configurations:

- Loads configuration from environment variables and files
- Provides CLI commands to get/set configuration values
- Handles port mapping for components
- Generates environment variables for Docker/shell consumption

### 3. Refactored Core Scripts

Core Tekton management scripts have been updated to use the shared utilities:

- **tekton-launch-new**: Launches Tekton components with improved component detection
- **tekton-status-new**: Shows status of all Tekton components and services
- **tekton-kill-new**: Stops all Tekton components with graceful shutdown

## Usage

### Shell Utilities

```bash
#!/usr/bin/env bash

# Load libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/../lib"

source "${LIB_DIR}/tekton-utils.sh"
source "${LIB_DIR}/tekton-ports.sh"
source "${LIB_DIR}/tekton-process.sh"
source "${LIB_DIR}/tekton-config.sh"

# Use library functions
tekton_find_root
tekton_is_port_used 8080
tekton_release_port 8080 "Hephaestus UI"
tekton_kill_processes "hermes" "Hermes Service"
tekton_get_component_port "hermes"
```

### Python Configuration

```bash
# Get a configuration value
value=$(tekton-config-cli.py get my-key default-value)

# Set a configuration value
tekton-config-cli.py set my-key "my value"

# Get a component port
port=$(tekton-config-cli.py get-port hephaestus)

# Generate environment variables
eval $(tekton-config-cli.py generate-env)
```

## Testing

To test the shared utilities, run:

```bash
./scripts/lib/test-utils.sh
```

This will test all shared utility functions and report their status.

## Migration Guide

1. Replace bash scripts that use the old format with the new shared libraries:

```bash
# Old format
BLUE="\033[94m"
GREEN="\033[92m"
RESET="\033[0m"

# New format
source "${SCRIPT_DIR}/lib/tekton-utils.sh"
# Use tekton_info, tekton_success, etc.
```

2. Replace process management code with shared utilities:

```bash
# Old format
pgrep -f "pattern" >/dev/null
kill $(pgrep -f "pattern")

# New format
tekton_is_running "pattern"
tekton_kill_processes "pattern" "Description"
```

3. Replace port management code with shared utilities:

```bash
# Old format
lsof -ti :8080 >/dev/null 2>&1
kill $(lsof -ti :8080)

# New format
tekton_is_port_used 8080
tekton_release_port 8080 "Description"
```

## Next Steps

- Migrate all components to use these shared utilities
- Create a unified `tekton-register` utility to replace individual registration scripts
- Enhance `tekton-llm-client` with shared prompt templates and response handlers