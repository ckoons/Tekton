#!/usr/bin/env bash
#
# branch-validator.sh - Validate branch for Claude Code sessions
#
# This script checks if the current branch matches the expected branch
# and outputs structured results for Claude Code sessions to interpret.

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "${SCRIPT_DIR}")"

# Run branch verify with Claude formatting
exec "${PARENT_DIR}/tekton-branch-verify" --claude "$@"