#!/usr/bin/env bash
#
# branch-management.sh - Example of branch management operations
#
# This script demonstrates various branch management operations using
# the GitHub utilities, including creation, status checking, verification,
# synchronization, and cleanup.

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
echo -e "${BLUE}      Branch Management Examples         ${RESET}"
echo -e "${BLUE}=========================================${RESET}"
echo ""

# Example 1: Branch Creation
echo -e "${GREEN}Example 1: Branch Creation${RESET}"
echo "Create a branch in the main repository only:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-create --main-only sprint/feature-main-only${RESET}"
echo ""
echo "Create a branch in component repositories only:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-create --components sprint/feature-components-only${RESET}"
echo ""
echo "Create a branch from a specific base branch:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-create -b develop sprint/feature-from-develop${RESET}"
echo ""
echo "Create a branch and push to remote:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-create -p sprint/feature-with-push${RESET}"
echo ""

# Example 2: Branch Status
echo -e "${GREEN}Example 2: Branch Status${RESET}"
echo "Check status of current branch:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-status${RESET}"
echo ""
echo "Check status of a specific branch:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-status sprint/feature-name${RESET}"
echo ""
echo "Get JSON-formatted status output:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-status -j sprint/feature-name${RESET}"
echo ""
echo "Check status against a different remote:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-status -r upstream sprint/feature-name${RESET}"
echo ""

# Example 3: Branch Verification
echo -e "${GREEN}Example 3: Branch Verification${RESET}"
echo "Verify current branch against expected branch:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-verify sprint/expected-branch${RESET}"
echo ""
echo "Verify with strict matching:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-verify -s sprint/expected-branch${RESET}"
echo ""
echo "Verify with Claude-friendly output:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-verify -c sprint/expected-branch${RESET}"
echo ""

# Example 4: Branch Synchronization
echo -e "${GREEN}Example 4: Branch Synchronization${RESET}"
echo "Synchronize current branch with main branch:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-sync main sprint/feature-branch${RESET}"
echo ""
echo "Synchronize using rebase strategy:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-sync -s rebase main sprint/feature-branch${RESET}"
echo ""
echo "Synchronize and push changes:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-sync -p main sprint/feature-branch${RESET}"
echo ""
echo "Preview synchronization without making changes:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-sync -d main sprint/feature-branch${RESET}"
echo ""

# Example 5: Branch Cleanup
echo -e "${GREEN}Example 5: Branch Cleanup${RESET}"
echo "Preview branch cleanup (dry run):"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-cleanup -d \"sprint/*\"${RESET}"
echo ""
echo "Cleanup local branches only:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-cleanup -l \"sprint/*\"${RESET}"
echo ""
echo "Cleanup branches older than 30 days:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-cleanup -o 30 \"sprint/*\"${RESET}"
echo ""
echo "Force cleanup of unmerged branches:"
echo -e "${YELLOW}${PARENT_DIR}/tekton-branch-cleanup -f \"sprint/*\"${RESET}"
echo ""

echo -e "${BLUE}=========================================${RESET}"
echo -e "${BLUE}   End of Branch Management Examples     ${RESET}"
echo -e "${BLUE}=========================================${RESET}"
