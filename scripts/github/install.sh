#!/usr/bin/env bash
#
# install.sh - Install Tekton GitHub utilities
#
# This script installs the Tekton GitHub utilities by creating symbolic links
# to the utility scripts in a directory on the user's PATH.

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"

# shellcheck source=lib/error-utils.sh
source "${LIB_DIR}/error-utils.sh"

# Default installation directory
DEFAULT_INSTALL_DIR="${HOME}/.local/bin"

# Function to display usage information
usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install Tekton GitHub utilities by creating symbolic links in a directory on your PATH.

Options:
  -h, --help              Display this help message and exit
  -v, --verbose           Enable verbose output
  -d, --directory DIR     Installation directory (default: ${DEFAULT_INSTALL_DIR})
  -f, --force             Force installation even if utilities already exist
  -l, --list              List utilities that will be installed
  
Examples:
  $(basename "$0")
    Install utilities in the default directory (${DEFAULT_INSTALL_DIR})

  $(basename "$0") -d ~/bin
    Install utilities in ~/bin

  $(basename "$0") -f
    Force reinstallation of utilities

EOF
  exit 1
}

# Function to list utilities that will be installed
list_utilities() {
  echo "The following utilities will be installed:"
  echo ""
  
  # List main utilities
  echo "Main utilities:"
  for util in "${SCRIPT_DIR}"/tekton-*; do
    if [[ -x "${util}" ]]; then
      echo "  - $(basename "${util}")"
    fi
  done
  
  echo ""
  echo "Claude helper scripts:"
  for util in "${SCRIPT_DIR}"/claude/*.sh; do
    if [[ -x "${util}" ]]; then
      echo "  - claude/$(basename "${util}")"
    fi
  done
  
  echo ""
  echo "Example scripts:"
  for util in "${SCRIPT_DIR}"/examples/*.sh; do
    if [[ -x "${util}" ]]; then
      echo "  - examples/$(basename "${util}")"
    fi
  done
  
  echo ""
  exit 0
}

# Parse arguments
verbose=false
install_dir="${DEFAULT_INSTALL_DIR}"
force_install=false
show_list=false

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
    -d|--directory)
      install_dir="$2"
      shift 2
      ;;
    -f|--force)
      force_install=true
      shift
      ;;
    -l|--list)
      show_list=true
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

# Show utility list if requested
if [[ "${show_list}" == "true" ]]; then
  list_utilities
fi

# Check if installation directory exists
if [[ ! -d "${install_dir}" ]]; then
  info "Installation directory ${install_dir} does not exist"
  read -p "Create it? [y/N] " create_dir
  if [[ "${create_dir}" =~ ^[Yy]$ ]]; then
    mkdir -p "${install_dir}" || error_exit "Failed to create directory ${install_dir}"
    success "Created directory ${install_dir}"
  else
    error_exit "Installation directory ${install_dir} does not exist"
  fi
fi

# Check if installation directory is on PATH
if ! echo "${PATH}" | tr ':' '\n' | grep -q "^${install_dir}$"; then
  warn "Installation directory ${install_dir} is not in your PATH"
  warn "You may need to add it to your PATH by adding the following to your shell profile:"
  warn "  export PATH=\"${install_dir}:\${PATH}\""
fi

# Install utilities
install_count=0
skip_count=0

# Install main utilities
for util in "${SCRIPT_DIR}"/tekton-*; do
  if [[ -x "${util}" ]]; then
    util_name=$(basename "${util}")
    target="${install_dir}/${util_name}"
    
    # Check if utility already exists
    if [[ -e "${target}" && "${force_install}" != "true" ]]; then
      warn "Utility ${util_name} already exists at ${target}, skipping (use --force to override)"
      ((skip_count++))
      continue
    fi
    
    # Create symbolic link
    ln -sf "${util}" "${target}" || error_exit "Failed to create symbolic link for ${util_name}"
    success "Installed ${util_name} -> ${target}"
    ((install_count++))
  fi
done

# Create directory for Claude helpers if needed
claude_dir="${install_dir}/claude"
if [[ ! -d "${claude_dir}" ]]; then
  mkdir -p "${claude_dir}" || error_exit "Failed to create directory ${claude_dir}"
  success "Created directory ${claude_dir}"
fi

# Install Claude helper scripts
for util in "${SCRIPT_DIR}"/claude/*.sh; do
  if [[ -x "${util}" ]]; then
    util_name=$(basename "${util}")
    target="${claude_dir}/${util_name}"
    
    # Check if utility already exists
    if [[ -e "${target}" && "${force_install}" != "true" ]]; then
      warn "Utility claude/${util_name} already exists at ${target}, skipping (use --force to override)"
      ((skip_count++))
      continue
    fi
    
    # Create symbolic link
    ln -sf "${util}" "${target}" || error_exit "Failed to create symbolic link for claude/${util_name}"
    success "Installed claude/${util_name} -> ${target}"
    ((install_count++))
  fi
done

# Create directory for examples if needed
examples_dir="${install_dir}/tekton-examples"
if [[ ! -d "${examples_dir}" ]]; then
  mkdir -p "${examples_dir}" || error_exit "Failed to create directory ${examples_dir}"
  success "Created directory ${examples_dir}"
fi

# Install example scripts
for util in "${SCRIPT_DIR}"/examples/*.sh; do
  if [[ -x "${util}" ]]; then
    util_name=$(basename "${util}")
    target="${examples_dir}/${util_name}"
    
    # Check if utility already exists
    if [[ -e "${target}" && "${force_install}" != "true" ]]; then
      warn "Example ${util_name} already exists at ${target}, skipping (use --force to override)"
      ((skip_count++))
      continue
    fi
    
    # Create symbolic link
    ln -sf "${util}" "${target}" || error_exit "Failed to create symbolic link for examples/${util_name}"
    success "Installed example ${util_name} -> ${target}"
    ((install_count++))
  fi
done

# Print summary
echo ""
echo "Installation Summary:"
echo "--------------------"
echo "Installed: ${install_count}"
echo "Skipped: ${skip_count}"
echo "Installation directory: ${install_dir}"
echo ""

# Print usage instructions
if [[ ${install_count} -gt 0 ]]; then
  echo "Usage Instructions:"
  echo "-----------------"
  echo "The utilities are now available in your PATH. You can run them directly:"
  echo ""
  echo "  tekton-branch-create --help"
  echo "  tekton-branch-status --help"
  echo "  tekton-branch-verify --help"
  echo "  tekton-branch-sync --help"
  echo "  tekton-branch-cleanup --help"
  echo "  tekton-commit --help"
  echo ""
  echo "Claude helper scripts are available in ${claude_dir}:"
  echo ""
  echo "  ${claude_dir}/prepare-session.sh --help"
  echo ""
  echo "Example scripts are available in ${examples_dir}:"
  echo ""
  echo "  ${examples_dir}/sprint-workflow.sh"
  echo ""
  
  # Check if installation directory is on PATH
  if ! echo "${PATH}" | tr ':' '\n' | grep -q "^${install_dir}$"; then
    echo "IMPORTANT: Add ${install_dir} to your PATH by adding this to your shell profile:"
    echo ""
    echo "  export PATH=\"${install_dir}:\${PATH}\""
    echo ""
  fi
fi

exit 0