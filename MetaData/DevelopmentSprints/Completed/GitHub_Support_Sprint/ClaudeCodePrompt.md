# GitHub Support Sprint - Claude Code Prompt

## Overview

This document serves as the initial prompt for a Claude Code session working on the GitHub Support Development Sprint for the Tekton project. It provides comprehensive instructions for implementing the planned GitHub utilities, references to relevant documentation, and guidelines for deliverables.

Tekton is an intelligent orchestration system that coordinates multiple CI models and resources to efficiently solve complex software engineering problems. This Development Sprint focuses on creating utilities and documentation to enhance Tekton's integration with GitHub, particularly for managing branches across multiple components during Development Sprints.

## Sprint Context

**Sprint Goal**: Create a comprehensive set of utilities and documentation for managing GitHub branches across multiple Tekton components during Development Sprints.

**Current Phase**: Phase 1: Core Utilities Development

**Branch Name**: `sprint/github-support-250430`

## Required Reading

Before beginning implementation, please thoroughly review the following documents:

1. **General Development Sprint Process**: `/MetaData/DevelopmentSprints/README.md`
2. **Sprint Plan**: `/MetaData/DevelopmentSprints/GitHub_Support_Sprint/SprintPlan.md`
3. **Architectural Decisions**: `/MetaData/DevelopmentSprints/GitHub_Support_Sprint/ArchitecturalDecisions.md`
4. **Implementation Plan**: `/MetaData/DevelopmentSprints/GitHub_Support_Sprint/ImplementationPlan.md`
5. **Branch Management Guide**: `/MetaData/DevelopmentSprints/Templates/BranchManagement.md`

## Branch Verification (CRITICAL)

Before making any changes, verify you are working on the correct branch:

```bash
git branch --show-current
```

Ensure the output matches: `sprint/github-support-250430`

If you are not on the correct branch, please do not proceed until this is resolved.

## Implementation Instructions

The implementation should follow the detailed plan in the Implementation Plan document. For Phase 1, focus on the following tasks:

### Task 1: Create GitHub Utilities Directory Structure

**Description**: Set up the basic directory structure for GitHub utilities

**Steps**:
1. Create the main `scripts/github/` directory
2. Create subdirectories for `lib/`, `templates/`, `claude/`, and `examples/`
3. Create placeholder README.md files in each directory

**Files to Create**:
- `scripts/github/README.md`: Main documentation for GitHub utilities
- `scripts/github/lib/README.md`: Documentation for shared libraries
- `scripts/github/templates/README.md`: Documentation for templates
- `scripts/github/claude/README.md`: Documentation for Claude helper scripts
- `scripts/github/examples/README.md`: Documentation for examples

**Acceptance Criteria**:
- Directory structure is created following Tekton conventions
- README files include basic descriptions of the purpose of each directory
- Main README.md includes an overview of the GitHub utilities

### Task 2: Implement Core Utility Library

**Description**: Create a library of shared functions for GitHub operations

**Steps**:
1. Create the main utility library file `scripts/github/lib/github-utils.sh`
2. Implement core functions for environment detection, component discovery, and basic operations
3. Include comprehensive documentation for each function
4. Implement error handling utilities in `scripts/github/lib/error-utils.sh`
5. Create component management utilities in `scripts/github/lib/component-utils.sh`

**Files to Create**:
- `scripts/github/lib/github-utils.sh`: Core utility functions
- `scripts/github/lib/error-utils.sh`: Error handling utilities
- `scripts/github/lib/component-utils.sh`: Component management utilities

**Acceptance Criteria**:
- Libraries implement all core functionality needed by the utilities
- Each function is well-documented with description, parameters, and return values
- Error handling is comprehensive and consistent
- Libraries follow bash best practices
- Code is well-commented and maintainable

### Task 3: Implement Branch Creation Utility

**Description**: Create a script for creating branches across multiple components

**Steps**:
1. Create the main script file `scripts/github/tekton-branch-create`
2. Implement argument parsing and validation
3. Implement branch creation logic for the main repository
4. Implement branch creation for component repositories
5. Add proper error handling and reporting
6. Include usage documentation

**Files to Create**:
- `scripts/github/tekton-branch-create`: Branch creation script

**Acceptance Criteria**:
- Script creates branches with consistent naming across all components
- Comprehensive argument validation and error handling
- Clear usage documentation
- Follows the design patterns specified in the Implementation Plan

### Task 4: Implement Branch Status Utility

**Description**: Create a script for checking branch status across components

**Steps**:
1. Create the main script file `scripts/github/tekton-branch-status`
2. Implement argument parsing and validation
3. Implement logic to check branch status across all components
4. Format output in a clear, readable format
5. Add proper error handling and reporting
6. Include usage documentation

**Files to Create**:
- `scripts/github/tekton-branch-status`: Branch status script

**Acceptance Criteria**:
- Script accurately reports branch status for all components
- Output is clear and easy to understand
- Comprehensive argument validation and error handling
- Clear usage documentation
- Follows the design patterns specified in the Implementation Plan

### Task 5: Implement Branch Verification Utility

**Description**: Create a script for verifying branch correctness for Claude sessions

**Steps**:
1. Create the main script file `scripts/github/tekton-branch-verify`
2. Implement argument parsing and validation
3. Implement logic to verify branch correctness across all components
4. Provide clear feedback for Claude sessions to interpret
5. Add proper error handling and reporting
6. Include usage documentation

**Files to Create**:
- `scripts/github/tekton-branch-verify`: Branch verification script

**Acceptance Criteria**:
- Script verifies branch status and provides clear feedback
- Output is designed to be easily interpreted by Claude sessions
- Comprehensive argument validation and error handling
- Clear usage documentation
- Follows the design patterns specified in the Implementation Plan

## Testing Requirements

After implementing the changes, perform the following tests:

1. **Unit Testing**:
   - Test each function in the utility libraries
   - Verify correct behavior with various inputs
   - Test error handling with invalid inputs

2. **Integration Testing**:
   - Test branch creation utility with a test repository
   - Test branch status utility with various configurations
   - Test branch verification utility with correct and incorrect branches
   - Verify utilities work together correctly

3. **Manual Testing**:
   - Run scripts with various arguments to verify behavior
   - Test on both Linux and macOS if possible
   - Verify output formatting is clear and consistent

## Documentation Updates

Update the following documentation as part of this implementation:

1. **MUST Update**:
   - Create comprehensive documentation in `scripts/github/README.md`
   - Document all utility libraries in their respective README files
   - Include detailed usage examples for each script

2. **CAN Update** (if relevant):
   - `/MetaData/DevelopmentSprints/Templates/BranchManagement.md`: Add references to the new utilities

## Deliverables

Upon completion of this phase, produce the following deliverables:

1. **Code Changes**:
   - Implemented directory structure
   - Core utility libraries
   - Branch management scripts
   - All README files and documentation

2. **Status Report**:
   - Create `/MetaData/DevelopmentSprints/GitHub_Support_Sprint/StatusReports/Phase1Status.md`
   - Include summary of completed work
   - List any challenges encountered
   - Document any deviations from the Implementation Plan
   - Provide recommendations for Phase 2

3. **Testing Results**:
   - Document testing performed
   - Report any issues or limitations found

## Code Style and Practices

Follow these guidelines during implementation:

1. **Bash Script Style**:
   - Use the shebang `#!/usr/bin/env bash` for improved portability
   - Include a brief description at the top of each script
   - Use meaningful variable and function names
   - Add comments for complex sections
   - Follow consistent indentation (2 spaces recommended for bash)
   - Quote all variables: `"${variable}"` not `$variable`
   - Use `set -e` to exit on errors
   - Use `set -u` to error on undefined variables
   - Use `set -o pipefail` to catch pipe failures

2. **Documentation Style**:
   - Use Markdown formatting for all documentation
   - Include examples for all functions and scripts
   - Document all parameters and return values
   - Use consistent formatting for command examples
   - Include troubleshooting information where appropriate

3. **Error Handling**:
   - Implement comprehensive error handling
   - Provide clear error messages
   - Use appropriate exit codes
   - Clean up temporary files and resources on exit

4. **Security Considerations**:
   - Avoid storing credentials in scripts
   - Validate and sanitize all user inputs
   - Be careful with command substitution
   - Don't use `eval` without careful consideration

## Example Script Template

Use this template for all scripts:

```bash
#!/usr/bin/env bash
#
# tekton-script-name - Brief description of what this script does
#
# This script provides detailed functionality for [purpose].
# It [detailed description of what it does and why].

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"

# shellcheck source=lib/github-utils.sh
source "${LIB_DIR}/github-utils.sh"
# shellcheck source=lib/error-utils.sh
source "${LIB_DIR}/error-utils.sh"

# Function to display usage information
usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS] ARGUMENTS

Brief description of what this script does.

Options:
  -h, --help     Display this help message and exit
  -v, --verbose  Enable verbose output
  
Arguments:
  ARGUMENT1      Description of argument 1
  ARGUMENT2      Description of argument 2

Examples:
  $(basename "$0") example-arg1 example-arg2
    Description of what this example does

EOF
  exit 1
}

# Parse arguments
verbose=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      ;;
    -v|--verbose)
      verbose=true
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

# Validate arguments
if [[ $# -lt 1 ]]; then
  error_exit "Missing required arguments"
fi

# Main script logic
main() {
  # Main implementation here
  echo "Implementing functionality..."
}

# Run the main function
main "$@"
```

## References

- [Bash Scripting Best Practices](https://mywiki.wooledge.org/BashGuide)
- [Git Documentation](https://git-scm.com/docs)
- [Tekton Development Sprint Process](/MetaData/DevelopmentSprints/README.md)

## Final Note

Remember that your work will be reviewed by Casey before being merged. Focus on quality, maintainability, and adherence to the implementation plan. If you encounter any significant obstacles, document them clearly and propose alternative approaches if appropriate.

Upon completion of your work, please provide a comprehensive status report as specified in the Deliverables section. This report will be crucial for planning Phase 2 of the sprint.