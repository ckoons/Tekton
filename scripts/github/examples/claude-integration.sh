#!/usr/bin/env bash
#
# claude-integration.sh - Example of Claude Code integration
#
# This script demonstrates how to use the Claude Code helper scripts
# for GitHub operations within Claude Code sessions.

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "${SCRIPT_DIR}")"
LIB_DIR="${PARENT_DIR}/lib"
CLAUDE_DIR="${PARENT_DIR}/claude"

# shellcheck source=../lib/error-utils.sh
source "${LIB_DIR}/error-utils.sh"

# Print header
echo -e "${BLUE}=========================================${RESET}"
echo -e "${BLUE}      Claude Integration Examples       ${RESET}"
echo -e "${BLUE}=========================================${RESET}"
echo ""

# Example 1: Branch Validation
echo -e "${GREEN}Example 1: Branch Validation${RESET}"
echo "Validate current branch for Claude Code session:"
echo -e "${YELLOW}${CLAUDE_DIR}/branch-validator.sh sprint/expected-branch${RESET}"
echo ""
echo "The output will be formatted for Claude to easily parse and will include:"
echo "- Expected branch name"
echo "- Current branch name"
echo "- Match result (exact, similar, different)"
echo "- Verification result (success, warning, failure)"
echo ""

# Example 2: Session Preparation
echo -e "${GREEN}Example 2: Session Preparation${RESET}"
echo "Prepare a Claude Code session with basic branch verification:"
echo -e "${YELLOW}${CLAUDE_DIR}/prepare-session.sh sprint/expected-branch${RESET}"
echo ""
echo "Prepare a session with component-specific context:"
echo -e "${YELLOW}${CLAUDE_DIR}/prepare-session.sh -c sprint/expected-branch${RESET}"
echo ""
echo "Prepare a session with both component and project context:"
echo -e "${YELLOW}${CLAUDE_DIR}/prepare-session.sh -c -p sprint/expected-branch${RESET}"
echo ""
echo "Prepare a session with strict branch verification:"
echo -e "${YELLOW}${CLAUDE_DIR}/prepare-session.sh -s sprint/expected-branch${RESET}"
echo ""
echo "The output will include:"
echo "- Branch verification information"
echo "- Component-specific documentation (if requested)"
echo "- Project context including sprint documentation (if requested)"
echo "- Available GitHub utilities"
echo ""

# Example 3: Commit Message Generation
echo -e "${GREEN}Example 3: Commit Message Generation${RESET}"
echo "Generate a feature commit message template for Claude:"
echo -e "${YELLOW}${CLAUDE_DIR}/generate-commit.sh feature${RESET}"
echo ""
echo "Generate a fix commit message template for Claude:"
echo -e "${YELLOW}${CLAUDE_DIR}/generate-commit.sh fix${RESET}"
echo ""
echo "Generate a documentation commit message template for Claude:"
echo -e "${YELLOW}${CLAUDE_DIR}/generate-commit.sh docs${RESET}"
echo ""
echo "The output will be a structured commit message template that Claude can fill in with appropriate details."
echo ""

# Example 4: Complete Claude Workflow
echo -e "${GREEN}Example 4: Complete Claude Workflow${RESET}"
echo "This demonstrates a typical Claude Code session workflow:"
echo ""
echo "1. Start Claude Code session with branch verification:"
echo -e "${YELLOW}${CLAUDE_DIR}/prepare-session.sh -c -p sprint/feature-name-250430${RESET}"
echo ""
echo "2. Claude implements changes as directed in the sprint plan"
echo ""
echo "3. Get a commit message template for the changes:"
echo -e "${YELLOW}${CLAUDE_DIR}/generate-commit.sh feature${RESET}"
echo ""
echo "4. Create a commit with the filled template:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-commit --title \"Implement feature X\" feature${RESET}"
echo ""
echo "5. Verify branch status before completing the session:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-status${RESET}"
echo ""

echo -e "${BLUE}=========================================${RESET}"
echo -e "${BLUE}   End of Claude Integration Examples   ${RESET}"
echo -e "${BLUE}=========================================${RESET}"
