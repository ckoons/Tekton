#!/usr/bin/env bash
#
# Example usage of tekton-branch-merge utility
#
# This script demonstrates how to use the tekton-branch-merge utility
# for different merge scenarios.

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GITHUB_DIR="$(dirname "${SCRIPT_DIR}")"

# Make the utility executable
chmod +x "${GITHUB_DIR}/tekton-branch-merge"

echo "Tekton Branch Merge Utility Examples"
echo "==================================="
echo

# Example 1: Dry run to see what would happen
echo "Example 1: Dry run merge from feature branch to main"
echo "$ tekton-branch-merge --dry-run sprint/example-feature-250430"
echo
echo "This command shows what would happen if you merged the feature branch"
echo "into main across all Tekton components, without making any changes."
echo

# Example 2: Interactive merge
echo "Example 2: Interactive merge from feature branch to main"
echo "$ tekton-branch-merge sprint/example-feature-250430"
echo
echo "This command interactively merges the feature branch into main"
echo "across all Tekton components, with confirmation prompts."
echo

# Example 3: YOLO mode (non-interactive with push)
echo "Example 3: Non-interactive merge with push (YOLO mode)"
echo "$ tekton-branch-merge --yes --push sprint/example-feature-250430"
echo
echo "This command merges the feature branch into main across all Tekton"
echo "components, skipping all confirmation prompts and pushing changes."
echo

# Example 4: Pull request mode
echo "Example 4: Create pull requests instead of direct merge"
echo "$ tekton-branch-merge --pr sprint/example-feature-250430"
echo
echo "This command creates pull requests from the feature branch to main"
echo "for all Tekton components, instead of performing direct merges."
echo

# Example 5: Custom merge commit message
echo "Example 5: Custom merge commit message"
echo "$ tekton-branch-merge --message \"Merge feature X with improvements\" sprint/example-feature-250430"
echo
echo "This command merges the feature branch with a custom commit message."
echo

# Example 6: Merge to a different target branch
echo "Example 6: Merge to a different target branch"
echo "$ tekton-branch-merge sprint/example-feature-250430 develop"
echo
echo "This command merges the feature branch into the develop branch"
echo "instead of main."
echo

# Example 7: Merge components only
echo "Example 7: Merge only component repositories"
echo "$ tekton-branch-merge --components sprint/example-feature-250430"
echo
echo "This command merges the feature branch only in component repositories,"
echo "skipping the main Tekton repository."
echo

echo "To run any of these examples, copy and paste the command into your terminal."
echo "Replace 'sprint/example-feature-250430' with your actual branch name."