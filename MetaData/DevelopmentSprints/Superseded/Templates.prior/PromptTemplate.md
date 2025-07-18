# [Sprint Name] - Claude Code Prompt

## Overview

This document serves as the initial prompt for a Claude Code session working on the [Sprint Name] Development Sprint for the Tekton project. It provides comprehensive instructions for implementing the planned changes, references to relevant documentation, and guidelines for deliverables.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This Development Sprint focuses on [brief description of the focus area].

## Sprint Context

**Sprint Goal**: [Clear statement of the sprint goal]

**Current Phase**: [Phase X: Phase Name]

**Branch Name**: `sprint/[sprint-name]-[date]`

## Required Reading

Before beginning implementation, please thoroughly review the following documents:

1. **General Development Sprint Process**: `/MetaData/DevelopmentSprints/README.md`
2. **Sprint Plan**: `/MetaData/DevelopmentSprints/[SprintName]/SprintPlan.md`
3. **Architectural Decisions**: `/MetaData/DevelopmentSprints/[SprintName]/ArchitecturalDecisions.md`
4. **Implementation Plan**: `/MetaData/DevelopmentSprints/[SprintName]/ImplementationPlan.md`
5. **[Any other relevant documentation]**: [path/to/document]

## Branch Verification (CRITICAL)

Before making any changes, verify you are working on the correct branch:

```bash
git branch --show-current
```

Ensure the output matches: `sprint/[sprint-name]-[date]`

If you are not on the correct branch, please do not proceed until this is resolved.

## Implementation Instructions

The implementation should follow the detailed plan in the Implementation Plan document. For this specific phase, focus on the following tasks:

### Task 1: [Task Name]

**Description**: [Detailed description of the task]

**Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Files to Modify**:
- [path/to/file1]: [What to change]
- [path/to/file2]: [What to change]
- [path/to/file3]: [What to change]

**Acceptance Criteria**:
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

### Task 2: [Task Name]

**Description**: [Detailed description of the task]

**Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Files to Modify**:
- [path/to/file1]: [What to change]
- [path/to/file2]: [What to change]
- [path/to/file3]: [What to change]

**Acceptance Criteria**:
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

### Task 3: [Task Name]

[...Repeat for each task...]

## Testing Requirements

After implementing the changes, perform the following tests:

1. **Unit Testing**:
   - Run existing unit tests: `[command to run tests]`
   - Implement new unit tests for the changed functionality
   - Ensure all tests pass

2. **Integration Testing**:
   - Test integration with [Component 1]
   - Test integration with [Component 2]
   - Verify [specific behavior]

3. **Manual Testing** (if applicable):
   - Start the affected components: `[command]`
   - Verify [specific behavior]
   - Check for [specific issues]

## Documentation Updates

Update the following documentation as part of this implementation:

1. **MUST Update**:
   - [path/to/doc1]: [What to update]
   - [path/to/doc2]: [What to update]
   - [path/to/doc3]: [What to update]

2. **CAN Update** (if relevant):
   - [path/to/doc1]: [What to update]
   - [path/to/doc2]: [What to update]
   - [path/to/doc3]: [What to update]

## Deliverables

Upon completion of this phase, produce the following deliverables:

1. **Code Changes**:
   - All implemented tasks as specified in the Implementation Plan
   - New or updated tests
   - Clean, well-documented code following Tekton's code style guidelines

2. **Status Report**:
   - Create `/MetaData/DevelopmentSprints/[SprintName]/StatusReports/Phase[X]Status.md`
   - Include summary of completed work
   - List any challenges encountered
   - Document any deviations from the Implementation Plan
   - Provide recommendations for subsequent phases (if applicable)

3. **Documentation Updates**:
   - All specified documentation changes
   - Any additional documentation created or updated

4. **Next Phase Instructions** (if applicable):
   - Create `/MetaData/DevelopmentSprints/[SprintName]/Instructions/Phase[X+1]Instructions.md`
   - Provide detailed instructions for the next phase
   - Include context about current state
   - Highlight any areas requiring special attention

## Questions and Clarifications

If you have any questions or need clarification before beginning implementation:

1. Ask specific questions about the implementation plan
2. Identify any ambiguities in the requirements
3. Request additional context if needed

## Code Style and Practices

Follow these guidelines during implementation:

1. **Python Code Style**:
   - Use f-strings for string formatting
   - Add type hints to function signatures
   - Follow PEP 8 guidelines
   - Use 4 spaces for indentation
   - Add docstrings for all functions and classes

2. **Comments**:
   - Include brief comments for complex sections
   - Add TODOs for future improvements
   - Document any workarounds or tricky implementations

3. **Error Handling**:
   - Use try/except blocks for operations that could fail
   - Log errors with appropriate level (info, warning, error)
   - Return meaningful error messages

4. **Commit Messages**:
   - Follow the format specified in CLAUDE.md
   - Include the sprint name in commit messages
   - Make atomic commits with clear purposes

## References

- [Link to relevant documentation]
- [Link to relevant code or components]
- [Link to related issues or discussions]
- [Link to any external resources or references]

## Final Note

Remember that your work will be reviewed by Casey before being merged. Focus on quality, maintainability, and adherence to the implementation plan. If you encounter any significant obstacles, document them clearly and propose alternative approaches if appropriate.