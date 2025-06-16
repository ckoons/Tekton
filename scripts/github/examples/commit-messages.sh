#!/usr/bin/env bash
#
# commit-messages.sh - Example of commit message creation
#
# This script demonstrates various ways to create standardized commit messages
# using the tekton-commit utility.

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "${SCRIPT_DIR}")"
LIB_DIR="${PARENT_DIR}/lib"

# shellcheck source=../lib/error-utils.sh
source "${LIB_DIR}/error-utils.sh"

# Print header
echo -e "${BLUE}=========================================${RESET}"
echo -e "${BLUE}      Commit Message Examples           ${RESET}"
echo -e "${BLUE}=========================================${RESET}"
echo ""

# Example 1: List available commit types
echo -e "${GREEN}Example 1: List Available Commit Types${RESET}"
echo "Show all available commit types and their templates:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-commit --list${RESET}"
echo ""

# Example 2: Feature commit
echo -e "${GREEN}Example 2: Feature Commit${RESET}"
echo "Create a feature commit with a title:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-commit --title \"Add branch management utilities\" feature${RESET}"
echo ""

# Example 3: Fix commit
echo -e "${GREEN}Example 3: Fix Commit${RESET}"
echo "Create a fix commit with issue reference:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-commit --title \"Fix component detection bug\" --issue 123 fix${RESET}"
echo ""

# Example 4: Documentation commit
echo -e "${GREEN}Example 4: Documentation Commit${RESET}"
echo "Create a documentation commit:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-commit --title \"Update GitHub workflow documentation\" docs${RESET}"
echo ""

# Example 5: Custom message
echo -e "${GREEN}Example 5: Custom Message${RESET}"
echo "Create a commit with a custom message:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-commit --title \"Refactor component detection\" --message \"- Improve performance by 30%\n- Reduce code complexity\n- Add better error handling\" refactor${RESET}"
echo ""

# Example 6: Preview commit message
echo -e "${GREEN}Example 6: Preview Commit Message${RESET}"
echo "Preview a commit message without creating a commit:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-commit --preview --title \"Update dependencies\" chore${RESET}"
echo ""

# Example 7: Include component information
echo -e "${GREEN}Example 7: Include Component Information${RESET}"
echo "Create a commit that includes affected component information:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-commit --title \"Update Ergon integration\" --components feature${RESET}"
echo ""

# Example 8: Edit commit message before committing
echo -e "${GREEN}Example 8: Edit Commit Message${RESET}"
echo "Create a commit and edit the message before finalizing:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-commit --title \"Add new tests\" --edit test${RESET}"
echo ""

echo -e "${BLUE}=========================================${RESET}"
echo -e "${BLUE}   End of Commit Message Examples       ${RESET}"
echo -e "${BLUE}=========================================${RESET}"
