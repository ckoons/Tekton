#!/usr/bin/env bash
#
# generate-commit.sh - Generate commit message for Claude Code sessions
#
# This script generates a structured commit message template for
# Claude Code sessions based on specified commit type.

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "${SCRIPT_DIR}")"

# Show help if no args provided
if [[ $# -lt 1 ]]; then
  echo "Usage: $(basename "$0") COMMIT_TYPE"
  echo "\nGenerate a structured commit message template for Claude Code sessions."
  echo "\nAvailable commit types: feature, fix, docs, refactor, test, chore"
  echo "\nExample: $(basename "$0") feature"
  exit 1
fi

commit_type="$1"

# Run tekton-commit in preview mode
exec "${PARENT_DIR}/tekton-commit" --preview "${commit_type}"