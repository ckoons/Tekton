# Hephaestus UI Reimplementation - Implementation Guide

This document provides detailed instructions for implementing the Hephaestus UI reimplementation across multiple Claude Code sessions. Follow these guidelines to ensure consistency and successful implementation of the Shadow DOM-based component isolation strategy.

## Session Workflow Overview

Each Claude Code session should follow this workflow:

1. **Orientation** - Review status and understand previous work
2. **Implementation** - Focus on specific tasks for the current session
3. **Testing** - Verify current implementation works as expected
4. **Handoff** - Document progress and prepare instructions for the next session

## Starting Each Session

Begin each session with these commands to understand the current state:

```bash
# Check what files have been created/modified
git status

# View the implementation notes from previous sessions
cat Hephaestus/IMPLEMENTATION_STATUS.md

# Check the core UI files to understand current implementation
ls -la Hephaestus/ui/
```

After orientation, explain your understanding of the current status and confirm the tasks for the session.

## Implementation Phases

### Phase 1: Core Infrastructure (First Session)

1. **Create Shadow DOM Component Loader**
   - Create `ComponentLoader` class in `ui/scripts/component-loader.js`
   - Implement Shadow DOM creation and management
   - Add theme variable propagation across shadow boundaries
   - Implement component lifecycle management

2. **Update Core UI Files**
   - Modify `ui-manager.js` to use the new component loader
   - Update main.js to initialize the component loader
   - Create base component structure that all components will follow

3. **Implementation Tasks:**
   - Create component-loader.js with basic Shadow DOM functionality
   - Modify ui-manager.js to use the new loader for component switching
   - Create base component structure for HTML, CSS, and JS files
   - Test loading a simple test component with Shadow DOM isolation

### Phase 2: Rhetor Component Migration (Second Session)

1. **Refactor Rhetor Component**
   - Update rhetor-component.html to use component-specific classes
   - Refactor rhetor-component.css following the naming convention
   - Update rhetor-component.js to work within Shadow DOM context
   - Test migration with the new component loader

2. **Implementation Tasks:**
   - Rename CSS classes in rhetor-component.html to follow BEM convention
   - Update rhetor-component.css with proper namespacing
   - Modify rhetor-component.js to use scoped DOM queries and event delegation
   - Test the migrated component for proper isolation and functionality

### Phase 3: Budget Component Migration (Third Session)

1. **Refactor Budget Component**
   - Update budget-dashboard.html to use component-specific classes
   - Refactor budget-component.css following the naming convention
   - Update budget-dashboard.js to work within Shadow DOM context
   - Decouple from Rhetor component dependencies
   - Test migration with the new component loader

2. **Implementation Tasks:**
   - Rename CSS classes in budget-dashboard.html to follow BEM convention
   - Update budget-component.css with proper namespacing
   - Modify budget-dashboard.js to use scoped DOM queries
   - Create a shared service for Rhetor client functionality
   - Test the migrated component for proper isolation and functionality

### Phase 4: Component Utilities & Shared Services (Fourth Session)

1. **Create Component Utilities**
   - Implement shared tab navigation functionality
   - Create form element standardization utilities
   - Develop card and layout components
   - Implement event delegation helpers

2. **Create Shared Services**
   - Develop RhetorService for LLM-related operations
   - Create BudgetService for cost tracking functionality
   - Implement ThemeService for consistent theming
   - Develop StorageService for component state preservation

3. **Implementation Tasks:**
   - Create ui/scripts/component-utils.js with reusable UI patterns
   - Develop ui/scripts/services/ directory with shared services
   - Refactor existing components to use the shared services
   - Test components with shared services for proper interaction

### Phase 5: Remaining Component Migration (Fifth Session)

1. **Migrate Terma Component**
   - Update terma-component.html to use component-specific classes
   - Refactor terma-terminal.css following the naming convention
   - Update terma-terminal.js to work within Shadow DOM context
   - Test migration with the new component loader

2. **Migrate Settings and Profile Components**
   - Update settings.html and profile.html to use component-specific classes
   - Refactor settings.css and profile.css following the naming convention
   - Update settings-ui.js and profile-ui.js to work within Shadow DOM
   - Test migration with the new component loader

3. **Implementation Tasks:**
   - Apply the same migration pattern to each component
   - Focus on proper isolation and consistent naming
   - Ensure components use shared services for common functionality
   - Test each migrated component for proper isolation and functionality

### Phase 6: Testing & Refinement (Sixth Session)

1. **Comprehensive Testing**
   - Test all component combinations and interactions
   - Verify theme switching works across all components
   - Test component state preservation during navigation
   - Verify error handling and fallback mechanisms

2. **Performance Optimization**
   - Implement lazy loading for component resources
   - Add component caching for faster switching
   - Optimize CSS and JavaScript for better performance
   - Profile and address any performance bottlenecks

3. **Implementation Tasks:**
   - Create test scenarios for component interactions
   - Implement performance optimizations
   - Address any issues found during testing
   - Document performance metrics and improvements

## Handoff Documentation

Before reaching context exhaustion in each session, create or update the following documentation:

### 1. Implementation Status Document

Update `Hephaestus/IMPLEMENTATION_STATUS.md` with:

```markdown
# Implementation Status - [Date]

## Completed Tasks
- [List of completed tasks with file paths and brief descriptions]

## Current State
- [Description of the current implementation state]
- [Any known issues or limitations]

## Next Steps
- [Detailed list of next tasks to implement]
- [Any decisions that need to be made]

## Testing Notes
- [Results of any testing performed]
- [Areas that need additional testing]
```

### 2. Component Migration Tracker

Update `Hephaestus/COMPONENT_MIGRATION_TRACKER.md` with:

```markdown
# Component Migration Tracker

| Component | HTML Updated | CSS Refactored | JS Updated | Tests Passed | Notes |
|-----------|--------------|----------------|------------|--------------|-------|
| Rhetor    | [Yes/No]     | [Yes/No]       | [Yes/No]   | [Yes/No]     | [Any issues] |
| Budget    | [Yes/No]     | [Yes/No]       | [Yes/No]   | [Yes/No]     | [Any issues] |
| Terma     | [Yes/No]     | [Yes/No]       | [Yes/No]   | [Yes/No]     | [Any issues] |
| Settings  | [Yes/No]     | [Yes/No]       | [Yes/No]   | [Yes/No]     | [Any issues] |
| Profile   | [Yes/No]     | [Yes/No]       | [Yes/No]   | [Yes/No]     | [Any issues] |
```

### 3. Code Changes Summary

Create files in `Hephaestus/session_logs/` for each session with:

```markdown
# Session [Number] - [Date] - Code Changes Summary

## New Files Created
- [file path]: [brief description]

## Modified Files
- [file path]: [description of changes]

## Implementation Decisions
- [Any significant design decisions made during implementation]

## Known Issues
- [Any issues that couldn't be resolved in this session]
```

## Maintaining Consistency

### Code Style Guidelines

1. **JavaScript**
   - Use ES6+ features (arrow functions, destructuring, etc.)
   - Follow camelCase for variables and functions
   - Use PascalCase for classes
   - Add JSDoc comments for functions and classes
   - Use consistent indentation (2 spaces)

2. **CSS**
   - Follow the BEM naming convention with component prefixes
   - Use CSS variables for theming and configuration
   - Organize styles logically (layout, typography, colors, etc.)
   - Minimize specificity and nesting

3. **HTML**
   - Use semantic HTML elements where appropriate
   - Ensure proper accessibility attributes
   - Follow consistent indentation
   - Use double quotes for attributes

### File Organization

1. **JavaScript**
   - Core functionality in `ui/scripts/core/`
   - Component-specific scripts in `ui/scripts/[component]/`
   - Shared services in `ui/scripts/services/`
   - Utilities in `ui/scripts/utils/`

2. **CSS**
   - Global styles in `ui/styles/main.css`
   - Theme files in `ui/styles/themes/`
   - Component-specific styles in `ui/styles/[component]/`

3. **HTML**
   - Component templates in `ui/components/[component]/`
   - Shared templates in `ui/components/shared/`

## Testing Approach

### Manual Testing Steps

For each component migration:

1. **Isolation Testing**
   - Verify CSS doesn't leak between components
   - Check that DOM structure is properly isolated
   - Test that events only affect the component that owns them

2. **Functionality Testing**
   - Verify all interactive elements work as expected
   - Test component-specific features
   - Ensure component can be initialized multiple times

3. **Theme Testing**
   - Switch between light and dark themes
   - Verify theme changes propagate correctly to Shadow DOM
   - Check that all themed elements update properly

### Test Validation

After each implementation phase, validate with:

```bash
# Start the UI server
cd Hephaestus/ui/server
python server.py

# Visit http://localhost:8080 in a browser
# Test the implemented components and interactions
```

Document test results in the implementation status document.

## Session-by-Session Plan

### Session 1: Core Infrastructure
- Create component-loader.js
- Update ui-manager.js
- Create test component for validation
- Update IMPLEMENTATION_STATUS.md with progress

### Session 2: Rhetor Component Migration
- Apply CSS naming convention to Rhetor
- Migrate Rhetor component to Shadow DOM
- Test Rhetor isolation and functionality
- Update component migration tracker

### Session 3: Budget Component Migration
- Apply CSS naming convention to Budget
- Migrate Budget component to Shadow DOM
- Decouple from Rhetor dependencies
- Test Budget isolation and functionality

### Session 4: Component Utilities & Services
- Create shared services
- Implement component utilities
- Refactor components to use shared services
- Test component interactions

### Session 5: Remaining Components
- Migrate Terma component
- Migrate Settings and Profile components
- Test all component combinations
- Update migration tracker

### Session 6: Testing & Refinement
- Comprehensive testing
- Performance optimization
- Documentation finalization
- Final validation

## First Session Kickstart

The first Claude Code session should start with:

1. Creating the component-loader.js file
2. Implementing basic Shadow DOM functionality
3. Updating ui-manager.js to use the new loader
4. Creating a test component to validate the approach

Begin with this command:

```bash
cd /Users/cskoons/projects/github/Tekton
cat Hephaestus/PHASE_0_SUMMARY.md
cat Hephaestus/COMPONENT_ISOLATION_STRATEGY.md
cat Hephaestus/CSS_NAMING_CONVENTION.md
```

Then proceed with implementation following the Session 1 tasks.

## Conclusion

This implementation guide provides a structured approach to the Hephaestus UI reimplementation across multiple Claude Code sessions. By following these guidelines, you can ensure consistent progress, maintain code quality, and successfully implement the Shadow DOM-based component isolation strategy.

Remember to:
1. Start each session with orientation
2. Focus on the specific tasks for that session
3. Test your implementation thoroughly
4. Document progress and prepare handoff information
5. Maintain consistency in code style and organization

Good luck with the implementation!