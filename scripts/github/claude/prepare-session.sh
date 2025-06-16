#!/usr/bin/env bash
#
# prepare-session.sh - Prepare environment for Claude Code sessions
#
# This script prepares the environment for a Claude Code session by verifying
# the branch, loading project context, and generating structured output.

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "${SCRIPT_DIR}")"
LIB_DIR="${PARENT_DIR}/lib"

# shellcheck source=../lib/github-utils.sh
source "${LIB_DIR}/github-utils.sh"
# shellcheck source=../lib/error-utils.sh
source "${LIB_DIR}/error-utils.sh"
# shellcheck source=../lib/component-utils.sh
source "${LIB_DIR}/component-utils.sh"

# Function to display usage information
usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS] EXPECTED_BRANCH

Prepare environment for Claude Code sessions by verifying the branch,
loading project context, and generating structured output.

Options:
  -h, --help           Display this help message and exit
  -v, --verbose        Enable verbose output
  -c, --component      Include component-specific context
  -p, --project        Include project-wide context
  -s, --strict         Fail if branch doesn't exactly match expected
  
Arguments:
  EXPECTED_BRANCH      Expected branch name to verify against

Examples:
  $(basename "$0") sprint/github-support-250430
    Prepare session for the 'sprint/github-support-250430' branch

  $(basename "$0") -c -p sprint/feature-name-250430
    Prepare session with component and project context

EOF
  exit 1
}

# Parse arguments
verbose=false
include_component=false
include_project=false
strict_matching=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      ;;
    -v|--verbose)
      verbose=true
      enable_debug
      shift
      ;;
    -c|--component)
      include_component=true
      shift
      ;;
    -p|--project)
      include_project=true
      shift
      ;;
    -s|--strict)
      strict_matching=true
      shift
      ;;
    -*)
      error_exit "Unknown option: $1"
      ;;
    *)
      break
      ;;
  esac
done

# Get expected branch name
if [[ $# -lt 1 ]]; then
  error_exit "Expected branch name must be provided"
fi
expected_branch="$1"

# Begin Claude session context output
echo "<claude_session_context>"

# Verify branch
echo "## Branch Verification"
if [[ "${strict_matching}" == "true" ]]; then
  "${PARENT_DIR}/tekton-branch-verify" --claude --strict "${expected_branch}" || true
else
  "${PARENT_DIR}/tekton-branch-verify" --claude "${expected_branch}" || true
fi

# Get current component if in a component directory
if [[ "${include_component}" == "true" ]]; then
  echo "\n## Component Context"
  current_component="$(get_current_component)" || true
  if [[ -n "${current_component}" ]]; then
    echo "Current component: ${current_component}"
    
    # Get component directory
    component_dir="$(get_component_directory "${current_component}")" || true
    if [[ -n "${component_dir}" ]]; then
      # Check for component README
      if [[ -f "${component_dir}/README.md" ]]; then
        echo "\n### Component README"
        echo '```markdown'
        head -n 20 "${component_dir}/README.md"
        echo '```'
      fi
      
      # Check for implementation guide
      impl_guide="${component_dir}/IMPLEMENTATION_GUIDE.md"
      if [[ ! -f "${impl_guide}" ]]; then
        impl_guide="${component_dir}/docs/implementation_guide.md"
      fi
      if [[ -f "${impl_guide}" ]]; then
        echo "\n### Implementation Guide"
        echo '```markdown'
        head -n 20 "${impl_guide}"
        echo '```'
      fi
    fi
  else
    echo "Not in a component directory"
  fi
fi

# Include project context
if [[ "${include_project}" == "true" ]]; then
  echo "\n## Project Context"
  
  # Get Tekton root directory
  tekton_root="$(detect_tekton_root)"
  if [[ -n "${tekton_root}" ]]; then
    # Check for sprint documentation
    sprint_dir="${tekton_root}/MetaData/DevelopmentSprints"
    branch_parts=(${expected_branch//\// })
    if [[ "${branch_parts[0]}" == "sprint" ]]; then
      sprint_name="${branch_parts[1]}"
      sprint_name_upper=$(echo "${sprint_name}" | tr '[:lower:]' '[:upper:]')
      
      # Look for sprint documentation
      possible_dirs=(
        "${sprint_dir}/${sprint_name}"
        "${sprint_dir}/${sprint_name_upper}"
        "${sprint_dir}/${sprint_name^}_Sprint"
        "${sprint_dir}/${sprint_name_upper}_SPRINT"
      )
      
      for dir in "${possible_dirs[@]}"; do
        if [[ -d "${dir}" ]]; then
          echo "\n### Sprint Documentation"
          echo "Found sprint documentation in ${dir}"
          
          # Check for implementation plan
          if [[ -f "${dir}/ImplementationPlan.md" ]]; then
            echo "\n#### Implementation Plan"
            echo '```markdown'
            head -n 20 "${dir}/ImplementationPlan.md"
            echo '```'
          fi
          
          # Check for sprint plan
          if [[ -f "${dir}/SprintPlan.md" ]]; then
            echo "\n#### Sprint Plan"
            echo '```markdown'
            head -n 20 "${dir}/SprintPlan.md"
            echo '```'
          fi
          
          break
        fi
      done
    fi
  fi
fi

# Include project structure summary
echo "\n## Project Structure"
echo "Main Tekton components: $(list_tekton_components | tr '\n' ' ')"

# Include GitHub utilities information
echo "\n## GitHub Utilities"
echo "Available utilities:"
echo "- tekton-branch-create: Create branches across components"
echo "- tekton-branch-status: Check branch status across components"
echo "- tekton-branch-verify: Verify branch correctness"
echo "- tekton-branch-sync: Synchronize branches across components"
echo "- tekton-commit: Generate and apply standardized commit messages"

# End Claude session context
echo "</claude_session_context>"

exit 0