# Fix GUI Sprint - Claude Code Prompt

## Overview

This document serves as the initial prompt for a Claude Code session working on the Fix GUI Sprint Development Sprint for the Tekton project. It provides comprehensive instructions for implementing the planned changes, references to relevant documentation, and guidelines for deliverables.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This Development Sprint focuses on simplifying and standardizing the Hephaestus UI architecture to create a more reliable component integration system.

## Sprint Context

**Sprint Goal**: Simplify the Hephaestus UI architecture and standardize component rendering to fix UI integration issues, particularly for the Athena component, and add a chat interface to all components.

**Current Phase**: Phase 1: UI Architecture Simplification

**Branch Name**: `sprint/fix-gui-050425`

## Required Reading

Before beginning implementation, please thoroughly review the following documents:

1. **General Development Sprint Process**: `/MetaData/DevelopmentSprints/README.md`
2. **Sprint Plan**: `/MetaData/DevelopmentSprints/Fix_GUI_Sprint/SprintPlan.md`
3. **Architectural Decisions**: `/MetaData/DevelopmentSprints/Fix_GUI_Sprint/ArchitecturalDecisions.md`
4. **Implementation Plan**: `/MetaData/DevelopmentSprints/Fix_GUI_Sprint/ImplementationPlan.md`
5. **Current Hephaestus UI Architecture**: `/MetaData/ComponentDocumentation/Hephaestus/TECHNICAL_DOCUMENTATION.md`
6. **Current UI Issues**: `/MetaData/DevelopmentSprints/Launch_Testing_Sprint/UNRESOLVED_ISSUES.md#6-ui-component-integration-issues`

## Branch Verification (CRITICAL)

Before making any changes, verify you are working on the correct branch:

```bash
git branch --show-current
```

Ensure the output matches: `sprint/fix-gui-050425`

If you are not on the correct branch, please do not proceed until this is resolved.

## Implementation Instructions

The implementation should follow the detailed plan in the Implementation Plan document. For this specific phase (Phase 1: UI Architecture Simplification), focus on the following tasks:

### Task 1: Refactor Panel System in UI Manager

**Description**: Update the UI manager to use a single panel for all components, eliminating the terminal/HTML distinction.

**Steps**:
1. Analyze the current panel system in `ui-manager.js`
2. Identify all occurrences of panel-based decisions (e.g., `usesTerminal` flag)
3. Refactor the panel activation logic to use a single main content area
4. Update component loading to always use the main panel
5. Ensure backward compatibility for existing components

**Files to Modify**:
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js`: Update panel management logic
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/main.css`: Update panel styling if needed

**Acceptance Criteria**:
- All components render in the main content area
- No distinction between terminal and HTML modes
- Backward compatibility with existing components

### Task 2: Simplify Component Registry Structure

**Description**: Update the component registry structure to eliminate confusing flags like `usesTerminal`.

**Steps**:
1. Analyze the current component registry structure in `component_registry.json`
2. Identify flags that are no longer needed with the simplified panel system
3. Update the schema to remove these flags
4. Ensure all component entries are updated to the new schema
5. Update any code that references the removed flags

**Files to Modify**:
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/server/component_registry.json`: Update component definitions
- Any code that references the removed flags

**Acceptance Criteria**:
- Registry structure is simplified and intuitive
- All components are properly registered
- No confusing or redundant flags

### Task 3: Create Standardized Component Container

**Description**: Implement a standardized container element for all components in the main content area.

**Steps**:
1. Design a standard HTML structure for component containers
2. Create CSS styles for the container that ensure proper sizing and layout
3. Update the component loading mechanism to use this container
4. Test with various component types to ensure compatibility

**Files to Modify**:
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js`: Update component loading
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/main.css`: Add container styles

**Acceptance Criteria**:
- All components use the same container structure
- Container properly sizes to fill the main content area
- No visual artifacts or layout issues

### Task 4: Implement Simplified Component Loading

**Description**: Create a simplified component loading mechanism that doesn't rely on Shadow DOM.

**Steps**:
1. Analyze the current Shadow DOM-based component loading
2. Design a simpler HTML-based loading mechanism
3. Implement CSS namespacing to prevent style conflicts
4. Update the component loading functions to use the new approach
5. Ensure proper error handling and fallbacks

**Files to Modify**:
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js`: Update loading mechanism
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/component-loader.js`: Simplify if needed

**Acceptance Criteria**:
- Components load correctly without Shadow DOM
- No CSS conflicts between components
- Proper component initialization

## Testing Requirements

After implementing the changes, perform the following tests:

1. **Component Rendering Tests**:
   - Test each component to ensure it renders correctly in the main content area
   - Verify that all component functionality works as expected
   - Check for any visual artifacts or layout issues

2. **Component Switching Tests**:
   - Test switching between different components
   - Verify that component state is maintained when switching back
   - Check for any memory leaks or performance issues

3. **Backward Compatibility Tests**:
   - Test all existing components to ensure they still work
   - Verify that no functionality is lost
   - Check for any visual regressions

4. **Error Handling Tests**:
   - Test with missing or invalid component definitions
   - Verify that appropriate error messages are displayed
   - Check that the UI remains usable after errors

## Documentation Updates

Update the following documentation as part of this implementation:

1. **MUST Update**:
   - `/MetaData/ComponentDocumentation/Hephaestus/TECHNICAL_DOCUMENTATION.md`: Update UI architecture details
   - `/MetaData/ComponentDocumentation/Hephaestus/IMPLEMENTATION_GUIDE.md`: Update component development guidelines
   - `/Users/cskoons/projects/github/Tekton/Hephaestus/README.md`: Update overview of UI architecture

2. **CAN Update** (if relevant):
   - Individual component README files
   - General Tekton UI guidelines

## Deliverables

Upon completion of this phase, produce the following deliverables:

1. **Code Changes**:
   - Updated `ui-manager.js` with simplified panel management
   - Simplified component registry structure
   - Standardized component container implementation
   - Simplified component loading mechanism

2. **Status Report**:
   - Create `/MetaData/DevelopmentSprints/Fix_GUI_Sprint/StatusReports/Phase1Status.md`
   - Include summary of completed work
   - List any challenges encountered
   - Document any deviations from the Implementation Plan
   - Provide recommendations for Phase 2

3. **Documentation Updates**:
   - Updated technical documentation
   - Updated implementation guidelines
   - Any additional documentation created or updated

4. **Next Phase Instructions**:
   - Create `/MetaData/DevelopmentSprints/Fix_GUI_Sprint/Instructions/Phase2Instructions.md`
   - Provide detailed instructions for Phase 2
   - Include context about current state
   - Highlight any areas requiring special attention

## Questions and Clarifications

If you have any questions or need clarification before beginning implementation:

1. Ask specific questions about the UI architecture
2. Identify any ambiguities in the requirements
3. Request additional context if needed
4. Seek clarification on the existing component behavior

## Code Style and Practices

Follow these guidelines during implementation:

1. **JavaScript Code Style**:
   - Use ES6+ features where appropriate
   - Add comments for complex sections
   - Follow consistent naming conventions
   - Break complex functions into smaller, more manageable pieces

2. **CSS Practices**:
   - Use namespaced CSS classes to prevent conflicts
   - Keep styles modular and component-specific
   - Minimize use of global styles
   - Use CSS variables for consistent theming

3. **HTML Structure**:
   - Keep HTML structure clean and semantic
   - Use appropriate ARIA attributes for accessibility
   - Ensure consistent element nesting
   - Validate HTML structure

4. **Error Handling**:
   - Add comprehensive error handling
   - Provide user-friendly error messages
   - Log errors to console with descriptive messages
   - Implement fallbacks for error cases

5. **Commit Messages**:
   - Follow the format specified in CLAUDE.md
   - Include the sprint name in commit messages
   - Make atomic commits with clear purposes
   - Reference specific tasks from the Implementation Plan

## References

- [Hephaestus UI Documentation](/Users/cskoons/projects/github/Tekton/MetaData/ComponentDocumentation/Hephaestus)
- [UI Component Integration Issues](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Launch_Testing_Sprint/UNRESOLVED_ISSUES.md#6-ui-component-integration-issues)
- [HTML and CSS Best Practices](https://github.com/hail2u/html-best-practices)
- [JavaScript Style Guide](https://github.com/airbnb/javascript)

## Final Note

Remember that your work will be reviewed by Casey before being merged. Focus on quality, maintainability, and adherence to the implementation plan. The goal is to create a simpler, more intuitive UI architecture that will make it easier to integrate components in the future. Pay particular attention to the Athena component, as fixing its rendering is a key objective of this sprint.