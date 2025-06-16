# Clean Slate Sprint - Claude Code Implementation Guide for Tekton Core

## Context

You are assisting with the Clean Slate Sprint for the Tekton project. This sprint focuses on rebuilding the UI component architecture to address persistent issues in previous implementations. The goal is to establish a reliable, standardized approach to UI components with proper isolation and clear patterns.

The project has made excellent progress. So far, we have:
1. Implemented the Athena component with BEM naming and proper isolation
2. Implemented the Ergon component following the same patterns
3. Implemented the Hermes component following the same patterns
4. Implemented the Engram component (memory system) with proper isolation and BEM naming
5. Implemented the Rhetor component following the same patterns
6. Implemented the Prometheus component (planning system) following the same patterns
7. Created a comprehensive debug instrumentation system for both frontend and backend
8. Added debug instrumentation to all implemented components

**IMPORTANT UPDATE (May 14, 2025):** Prometheus implementation is now complete. The next major task is to implement the Tekton Core component (project management system) using the same patterns established for other components, with Athena as the gold standard reference model.

**SPECIAL NOTE:** Use Athena as the canonical reference implementation for all component patterns, not Rhetor or other components.

## Your Role

As the AI assistant for this sprint, your role is to implement the Tekton Core component following a methodical, restrained approach that prioritizes reliability over feature richness. You should:

1. Follow the implementation plan exactly, using Athena as the reference
2. Focus on creating simple, reliable solutions with clear patterns
3. Test each step before proceeding to the next
4. Maintain strict component isolation to prevent interference
5. Document your work clearly for future reference

## Key Principles to Follow

### 1. Restraint and Simplicity
- Keep implementations as simple as possible
- Resist the urge to add features or optimizations before basics work
- Focus on doing one thing well before moving to the next
- When in doubt, choose the simpler approach

### 2. Strict Component Isolation
- Components should never affect other components
- CSS must use BEM notation with component prefixes
- JS must query elements only within the component container
- Use relative positioning instead of absolute positioning
- Respect the boundaries between components and the main UI

### 3. Template-Based Development
- Use the Athena component as the gold standard reference template
- Make minimal modifications to the template pattern
- Follow the same structure and naming conventions consistently
- Document any deviations from the template pattern

### 4. Progressive Enhancement
- First ensure components load correctly
- Then add basic interactivity
- Add more complex features only after basics work
- Test each stage before proceeding

## Implementation Approach

### Phase 1: Foundation (Completed)
- Established the foundation with the component loader
- Created golden component templates based on Athena
- Defined component contracts for lifecycle, events, and state
- Implemented debug instrumentation

### Phase 2: Component Implementation (Current Focus)
1. **Implement Tekton Core component** ⚠️
   - Start with HTML structure following the Athena template
   - Add CSS with BEM naming
   - Implement JS with lifecycle methods
   - Add GitHub project management functionality
   - Ensure visual consistency with other components, especially Athena

### Phase 3: Validation and Documentation (Ongoing)
1. **Documentation updates** (continuous)
   - Document the Tekton Core implementation
   - Update guides and references
   - Create troubleshooting information

2. **Testing and validation** (with Tekton Core component)
   - Test loading and functionality
   - Verify isolation from other components
   - Test error handling and recovery

## Specific Guidelines

### Working with HTML
- Follow semantic HTML principles
- Use clear, descriptive class names following BEM
- Ensure proper nesting and hierarchy
- Keep markup clean and minimal
- Follow the established structure:
  - Component container
  - Header with title
  - Menu bar with tabs
  - Content area with panels
  - Footer with input (for chat components)

### Working with CSS
- Always use BEM notation: `.tekton__element--modifier`
- Scope all styles to the component root
- Avoid global styles or resets
- Use relative units when possible
- Prefer flexbox/grid for layout
- Match heights and spacing with Athena component:
  - Header height: 50px
  - Menu bar height: 46px
  - Footer height: 70px

### Working with JavaScript
- Scope queries to component container: `document.querySelector('.tekton').querySelector()`
- Use clear method and variable names
- Follow the defined lifecycle pattern
- Implement proper error handling
- Clean up event listeners and resources
- Protect against UI Manager interference

## Key Files to Modify

### Tekton Core Component (to implement)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/tekton/tekton-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/tekton/tekton-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/tekton/github-service.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/tekton/project-manager.js`

### Reference Components (already implemented)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/athena/athena-component.html` (PRIMARY REFERENCE)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/prometheus/prometheus-component.html`

### Debug Instrumentation
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/debug-shim.js`

## Getting Started

1. Verify you're on the correct branch:
   ```bash
   git branch
   # Should show sprint/Clean_Slate_051125
   ```

2. Examine the Athena component as your primary reference:
   ```bash
   cat /Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/athena/athena-component.html
   ```

3. Begin implementing the Tekton Core component following the established patterns from Athena

4. Test the component in the Hephaestus UI by running:
   ```bash
   cd /Users/cskoons/projects/github/Tekton/Hephaestus/ui && python server/server.py
   ```

## Implementation Requirements

**CRITICAL**: You MUST follow the TektonCoreImplementationGuide.md document exactly, without any deviations. If you believe any changes are needed, you MUST discuss these with Casey (human-in-the-loop) first before implementation. No architectural changes, altered patterns, or extra features are allowed without explicit approval.

## Important Notes

1. **Use Athena as the gold standard**: The Athena component is the canonical reference for all UI patterns
2. **Do not rely on Rhetor documentation**: Due to issues with previous implementation
3. **Make small, incremental changes**: This makes debugging easier
4. **Test thoroughly**: Test each change before moving on
5. **Document your work**: Document any challenges, decisions, or patterns
6. **Follow the established patterns**: Consistency is crucial
7. **Maintain restraint**: Focus on reliability over features
8. **Visual consistency**: Ensure the Tekton Core component visually matches other components

## Documentation

Refer to these documents for detailed guidance:

- [Sprint Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/SprintPlan.md)
- [Architectural Decisions](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/ArchitecturalDecisions.md)
- [Implementation Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/ImplementationPlan.md)
- [Tekton Core Implementation Guide](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/TektonCoreImplementationGuide.md)
- [Debug Instrumentation Guide](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/DeveloperGuides/Debugging/ComponentInstrumentation.md)

## Tekton Core Component Overview

The Tekton Core component is the central project management system of the Tekton platform, focused on GitHub integration and project management. It should include the following key features:

1. **Projects Panel** - For managing projects linked to GitHub repositories
2. **Repositories Panel** - For managing GitHub repositories
3. **Branches Panel** - For managing branches across repositories
4. **Actions Panel** - For performing common GitHub operations
5. **Project Chat Panel** - For project management assistance
6. **Team Chat Panel** - For team communication (consistent with other components)

The component should follow the same visual and structural patterns as the other components, with tabs at the top, content panels in the middle, and a consistent footer for input. The Tekton Core component should match the visual style of other components, especially Athena.

Build the component following the same BEM patterns, component isolation, and debug instrumentation as implemented in the Athena component.

## UI Manager Protection

**CRITICAL**: The UI Manager in the Hephaestus system can sometimes interfere with components. You MUST implement protection against this by:

1. Immediately setting `window.uiManager._ignoreComponent = 'tekton'` at the beginning of your JS file
2. Implementing the tab switching function outside of any classes
3. Scoping all DOM queries to the component container
4. Using inline event handlers with `return false` to prevent propagation

## HTML Panel Protection

**CRITICAL**: The HTML panel in Hephaestus can sometimes be hidden by other components. You MUST implement protection by:

1. Setting `htmlPanelElements.forEach(panel => { if (panel) panel.style.display = 'block'; });` in your tab switching function
2. Ensuring all panel visibility changes are scoped to the component container
3. Using `style.display = 'block'` rather than just adding/removing classes

## MCP Integration

The Tekton Core component should use MCP functions for GitHub operations when possible. These include:

- `mcp__github__search_repositories`
- `mcp__github__create_repository`
- `mcp__github__get_file_contents`
- `mcp__github__push_files`
- `mcp__github__create_issue`
- `mcp__github__create_pull_request`
- `mcp__github__fork_repository`
- `mcp__github__create_branch`
- `mcp__github__list_commits`
- `mcp__github__list_issues`
- And other GitHub-related MCP functions

The GitHub service should wrap these MCP functions with proper error handling and logging.