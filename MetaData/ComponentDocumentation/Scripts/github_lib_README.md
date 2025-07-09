# GitHub Utilities Library

## Overview

This directory contains shared library functions used by Tekton's GitHub utilities. These libraries provide common functionality for repository operations, error handling, and component management.

## Available Libraries

- `github-utils.sh`: Core utility functions for GitHub operations
- `error-utils.sh`: Error handling and reporting utilities
- `component-utils.sh`: Utilities for managing Tekton components

## Usage

These libraries are designed to be sourced by other scripts. Example usage:

```bash
#!/usr/bin/env bash

# Load libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"

source "${LIB_DIR}/github-utils.sh"
source "${LIB_DIR}/error-utils.sh"
source "${LIB_DIR}/component-utils.sh"

# Use library functions
if ! check_git_repo; then
  error_exit "Not in a git repository"
fi

# Get Tekton components
components=$(list_tekton_components)
```

## Function Documentation

See comments in each library file for detailed documentation of available functions.