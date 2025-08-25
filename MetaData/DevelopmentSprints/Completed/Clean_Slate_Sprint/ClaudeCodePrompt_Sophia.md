# Claude Code Prompt: Sophia Implementation

## Prompt Overview

This prompt guides Claude in implementing the Sophia component for the Tekton Clean Slate Architecture. The implementation should strictly follow the Clean Slate Architecture and use Athena as the gold standard reference implementation.

## System Information

- Current directory: `/Users/cskoons/projects/github/Tekton`
- Working on Clean Slate Sprint
- Branch: `sprint/Clean_Slate_051125`

## Task Overview

Implement the Sophia component (AI Intelligence Measurement & Continuous Improvement) following the Clean Slate architecture pattern. The component should include:

1. Component HTML structure with proper BEM naming
2. CSS styling with BEM naming convention
3. JavaScript with component isolation and Clean Slate patterns
4. 6 tabs: Metrics, Intelligence, Experiments, Recommendations, Research Chat, and Team Chat

## Implementation Steps

1. First, study the Clean Slate architecture by examining:
   - Athena implementation (primary reference)
   - The SophiaImplementationGuide.md

2. Implement the component following the structure:
   - Component HTML file
   - Component core JavaScript
   - Service JavaScript files 
   - Additional UI functionality

3. Ensure all implementation precisely follows:
   - BEM naming convention with `sophia__` prefix
   - HTML panel protection
   - UI Manager protection
   - Self-contained tab switching
   - Component isolation
   - Debug logging with [SOPHIA] prefix

## Required Files

Create/edit the following files:

1. `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/sophia/sophia-component.html`
2. `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/sophia/sophia-component.js`
3. `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/sophia/sophia-service.js`
4. `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/sophia/sophia-intelligence-service.js`
5. `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/sophia/sophia-analytics-service.js`

## Critical Requirements

1. **Mandatory Reference Implementation**: Use Athena as the gold standard. Every pattern, structure, and convention MUST match Athena's implementation with appropriate Sophia-specific content.

2. **Design Pattern**: Follow the exact same design pattern as Athena with:
   - Same HTML structure with BEM naming
   - Same CSS organization with Sophia-specific theme colors
   - Same JavaScript patterns for component isolation

3. **Explicit Non-Negotiables**:
   - UI Manager Protection: `window.uiManager._ignoreComponent = 'sophia'`
   - HTML Panel Protection: Force `display: block` on HTML panel
   - Tab Switching: Self-contained not using shared utilities
   - DOM Queries: Scope all queries to `.sophia` container
   - Error Handling: Comprehensive try/catch and logging
   - Debug Prefix: Use '[SOPHIA]' prefix for all console logs

4. **No Deviation**: This implementation MUST follow the guide exactly as written. Any deviations from the Clean Slate architecture or Athena reference implementation are strictly prohibited without explicit approval.

## Design Notes

1. **Tabs**: 
   - Metrics: Performance and resource metrics dashboard
   - Intelligence: Intelligence dimensions visualization and comparison
   - Experiments: Experiment management and tracking
   - Recommendations: Improvement recommendations tracking
   - Research Chat: CI research assistant
   - Team Chat: Shared team communication

2. **Visual Theme**:
   - Main accent color: Purple (#9C27B0 for Sophia)
   - Consistent with Athena's general design (spacing, layout, typography)

3. **Functionality Scope**:
   - Focus on component isolation and correct architecture
   - Implement sample metrics/analytics displays
   - Functional tab switching
   - Basic chat functionality
   - All lists should have sample data for UI testing

## Important Considerations

1. **Component Isolation**: The component MUST NOT interfere with other components. Use component-scoped DOM queries.

2. **Performance**: Follow Athena patterns for loading content on demand rather than all at once.

3. **JavaScript Organization**: Follow Athena's patterns for organizing JavaScript into main component file and service modules.

4. **Error Handling**: Implement comprehensive error handling with proper user feedback.

5. **State Management**: Implement proper state management with localStorage persistence.

## Testing Instructions

After implementation, test to ensure:

1. Component loads without errors
2. Tab switching works properly
3. No interference with other components
4. Sample data displays correctly
5. HTML panel remains visible
6. Chat functionality works in Research Chat and Team Chat tabs

## Important Note

This implementation is part of the Clean Slate Sprint to standardize all Tekton components. The consistent architecture is crucial for maintainability and future development. Athena has been established as the gold standard reference implementation, and all components MUST follow the same patterns without deviation.