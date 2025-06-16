#!/usr/bin/env bash
#
# sprint-workflow.sh - Example workflow for a complete Development Sprint lifecycle
#
# This script demonstrates the complete lifecycle of a Development Sprint using
# the GitHub utilities. It includes branch creation, status checking, committing,
# and synchronization.

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
echo -e "${BLUE}   Tekton Development Sprint Workflow   ${RESET}"
echo -e "${BLUE}=========================================${RESET}"
echo ""

# Step 1: Create a new sprint branch
echo -e "${GREEN}Step 1: Creating new sprint branch${RESET}"
echo "This would create a new branch across all components:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-create -p sprint/example-feature-$(date +%y%m%d)${RESET}"
echo ""

# Step 2: Verify branch creation
echo -e "${GREEN}Step 2: Verifying branch status${RESET}"
echo "This would check the status of the new branch across all components:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-status sprint/example-feature-$(date +%y%m%d)${RESET}"
echo ""

# Step 3: Prepare Claude session
echo -e "${GREEN}Step 3: Preparing Claude session${RESET}"
echo "This would prepare the Claude session with project context:"
echo -e "${YELLOW}${PARENT_DIR}/claude/prepare-session.sh -c -p sprint/example-feature-$(date +%y%m%d)${RESET}"
echo ""

# Step 4: Make changes and commit
echo -e "${GREEN}Step 4: Making changes and committing${RESET}"
echo "After making changes, use the commit utility to create standardized commits:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-commit --title \"Implement new feature\" feature${RESET}"
echo ""

# Step 5: Synchronize with main branch
echo -e "${GREEN}Step 5: Synchronizing with main${RESET}"
echo "This would synchronize the sprint branch with the main branch:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-sync main sprint/example-feature-$(date +%y%m%d)${RESET}"
echo ""

# Step 6: Final status check
echo -e "${GREEN}Step 6: Final status check${RESET}"
echo "Before completing the sprint, check the final status:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-status sprint/example-feature-$(date +%y%m%d)${RESET}"
echo ""

# Step 7: Cleanup
echo -e "${GREEN}Step 7: Branch cleanup${RESET}"
echo "After merging, clean up the sprint branch:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-cleanup \"sprint/example-feature-*\"${RESET}"
echo ""

echo -e "${BLUE}=========================================${RESET}"
echo -e "${BLUE}   End of Development Sprint Workflow    ${RESET}"
echo -e "${BLUE}=========================================${RESET}"
