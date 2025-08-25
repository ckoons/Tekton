# Footer Components Sprint - Claude Code Implementation Guide

## Context

You are assisting with the completion of the Clean Slate Sprint for the Tekton project by implementing the three remaining footer components: Budget, Profile, and Settings. The main Clean Slate Sprint has already successfully implemented the core components (Athena, Ergon, Hermes, Engram, Rhetor, Prometheus, and Tekton Core) following strict architectural principles for component isolation and consistency.

These footer components are critical for providing users with important functionality:
1. **Budget Component**: For monitoring and managing resource usage and costs
2. **Profile Component**: For managing user information and preferences
3. **Settings Component**: For configuring application-wide settings

Your task is to implement these components following the same Clean Slate architecture patterns that have proven successful with the other components. The Athena component serves as the "golden example" that all components should follow.

## Your Role

As the CI assistant for this sprint, your role is to implement the plans following a methodical, restrained approach that prioritizes reliability over feature richness. You should:

1. Follow the implementation plan exactly, progressing through phases in order
2. Focus on creating simple, reliable solutions with clear patterns
3. Test each step before proceeding to the next
4. Maintain strict component isolation to prevent interference
5. Document your work clearly for future reference
6. Work only with explicit approval from Casey, the human-in-the-loop project manager

## Key Principles to Follow

### 1. Restraint and Simplicity

- Keep implementations as simple as possible
- Resist the urge to add features or optimizations before basics work
- Focus on doing one thing well before moving to the next
- When in doubt, choose the simpler approach
- Make no changes to the codebase without explicit approval

### 2. Strict Component Isolation

- Components should never affect other components
- CSS must use BEM notation with component prefixes
- JS must query elements only within the component container
- Use relative positioning instead of absolute positioning
- Respect the boundaries between components and the main UI

### 3. Template-Based Development

- Use the Athena component as the starting point for all components
- Make minimal modifications to the template pattern
- Follow the same structure and naming conventions consistently
- Document any deviations from the template pattern

### 4. Progressive Enhancement

- First ensure components load correctly
- Then add basic interactivity
- Add more complex features only after basics work
- Test each stage before proceeding

## Directory Structure

All components should follow the established directory structure:

```
/Hephaestus/ui/
├── components/
│   ├── budget/
│   │   └── budget-component.html
│   ├── profile/
│   │   └── profile-component.html
│   └── settings/
│       └── settings-component.html
├── scripts/
│   ├── budget/
│   │   ├── budget-component.js
│   │   └── budget-service.js
│   ├── profile/
│   │   ├── profile-component.js
│   │   └── profile-service.js
│   └── settings/
│       ├── settings-component.js
│       └── settings-service.js
└── styles/
    ├── budget.css
    ├── profile.css
    └── settings.css
```

## Implementation Approach

### Phase 1: Foundation and Preparation

1. **Analyze existing components**
   - Review current Budget component structure and required changes
   - Review current Profile component structure and required changes
   - Review current Settings component structure and required changes
   - Document gaps between current state and Clean Slate requirements

2. **Establish golden reference**
   - Use Athena component as the primary reference
   - Identify key patterns to replicate
   - Define component-specific adaptations needed

3. **Prepare development environment**
   - Verify you're on the correct branch (sprint/Clean_Slate_051125)
   - Set up local testing workflow

### Phase 2: Component Implementation (Budget, Profile, Settings)

For each component, follow this implementation sequence:

1. **HTML Structure**
   - Implement component HTML with proper BEM naming
   - Create tab structure with component-specific tabs
   - Create placeholder panel content for each tab
   - Implement footer controls when needed

2. **CSS Implementation**
   - Implement component CSS with BEM naming
   - Create component-specific variables for colors and styling
   - Implement responsive layouts for all panels
   - Ensure proper visual hierarchy

3. **JavaScript Implementation**
   - Implement component JS with container-scoped queries
   - Create lifecycle methods (init, activate, cleanup)
   - Implement tab switching functionality
   - Add basic state management

4. **Feature Implementation**
   - Implement panel-specific features
   - Add form validation and submission logic
   - Implement data persistence
   - Add user feedback mechanisms

5. **Debug Instrumentation**
   - Add debug instrumentation to component
   - Implement component-specific debug panel
   - Add event logging for key operations
   - Create debug toggle functionality

### Phase 3: Testing and Validation

- Test each component individually
- Test component interactions
- Validate proper isolation
- Check for visual consistency

### Phase 4: Documentation and Finalization

- Update component documentation
- Create implementation guides
- Update Clean Slate Sprint summary
- Prepare final commit

## Budget Component Specifications

The Budget component provides users with functionality to monitor and manage resource usage and financial aspects of Tekton operation. It should include:

1. **Dashboard Tab**
   - Overall usage metrics visualization
   - Spending summary
   - Quick actions for budget management
   - Alert indicators for approaching limits

2. **Usage Details Tab**
   - Detailed usage statistics
   - Filtering by time period, service, and project
   - Usage trends visualization
   - Export functionality for reports

3. **Budget Settings Tab**
   - Budget limit configuration
   - Service allocation controls
   - Budget period settings
   - Approval workflow settings

4. **Alerts Tab**
   - Alert threshold configuration
   - Notification method settings
   - Automated action settings
   - Alert history

5. **Team Chat Tab**
   - Team communication about budget matters
   - Consistent with chat implementation in other components
   - Budget-specific message templates
   - Notification controls

Follow the color scheme: primary color `#34A853` (green) with appropriate variations for the Budget component.

## Profile Component Specifications

The Profile component allows users to manage their personal information and preferences. It should include:

1. **Personal Info Tab**
   - Name, email, and bio management
   - Profile picture upload and management
   - Display name settings
   - Account type information

2. **Contact Tab**
   - Contact information management
   - Communication preferences
   - Time zone settings
   - Notification settings

3. **Social Accounts Tab**
   - Social media account linking
   - GitHub integration
   - OAuth connections
   - Profile sharing settings

4. **Security Tab**
   - Password management
   - Two-factor authentication
   - Security questions
   - Session management

5. **Preferences Tab**
   - User-specific preferences
   - Default settings for new projects
   - Language preferences
   - Accessibility settings

Follow the color scheme: primary color `#9C27B0` (purple) with appropriate variations for the Profile component.

## Settings Component Specifications

The Settings component provides application-wide configuration options. It should include:

1. **Theme Tab**
   - Light/dark mode toggle
   - Accent color selection
   - Custom theme creation
   - Font settings

2. **Interface Tab**
   - Layout options
   - Panel size settings
   - Navigation preferences
   - Keyboard shortcut configuration

3. **Terminal Tab**
   - Font family and size
   - Cursor style
   - Color scheme
   - Command history settings

4. **Chat Tab**
   - Message display settings
   - History retention settings
   - Auto-completion preferences
   - Notification settings

5. **Hermes Tab**
   - Hermes service configuration
   - Integration settings
   - API key management
   - Service fallback options

6. **System Tab**
   - System information
   - Cache management
   - Data reset options
   - Advanced debugging settings

Follow the color scheme: primary color `#1E88E5` (blue) with appropriate variations for the Settings component.

## Key Files to Reference

### Golden Reference
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/athena/athena-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/athena/athena-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/athena.css`

### Target Components
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/budget/budget-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/profile/profile-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/settings/settings-component.html`

### Debug Instrumentation
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/debug-shim.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/server/debug_utils.py`

## Implementation Tips

### HTML Structure
- Use semantic HTML elements
- Follow BEM naming: `.component__element--modifier`
- Create consistent tab structure
- Use proper ARIA attributes for accessibility
- Match the HTML structure of Athena

### CSS Implementation
- Scope all styles to component using BEM
- Create component-specific variables
- Use relative units (rem, em, %)
- Follow responsive design principles
- Match visual styling with other components

### JavaScript Pattern
- Follow the component lifecycle:
  - `constructor()`: Initialize properties
  - `connectedCallback()`: Render and setup
  - `disconnectedCallback()`: Cleanup
- Use container-scoped queries:
  - `this.shadowRoot.querySelector()`
- Implement the tab switching pattern:
  - Track active tab
  - Toggle tab visibility
  - Update active tab indicator
- Use proper event delegation
- Implement state management with localStorage

### Debug Instrumentation
- Use `console.group()` for logical grouping
- Add instrumentation points at lifecycle methods
- Log important state changes
- Provide toggle mechanism for debug mode

## Getting Started

1. Verify you're on the correct branch:
   ```bash
   git branch
   # Should show sprint/Clean_Slate_051125
   ```

2. Examine the Athena component as reference:
   ```bash
   cat /Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/athena/athena-component.html
   ```

3. Review existing footer components to understand current state:
   ```bash
   cat /Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/budget/budget-component.html
   cat /Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/profile/profile-component.html
   cat /Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/settings/settings-component.html
   ```

4. Test the component in the Hephaestus UI by running:
   ```bash
   cd /Users/cskoons/projects/github/Tekton/Hephaestus/ui && python server/server.py
   ```

## Important Notes

1. **Always get explicit approval**: Do not make any changes to files without Casey's explicit approval
2. **Make small, incremental changes**: This makes debugging easier
3. **Test thoroughly**: Test each change before moving on
4. **Document your work**: Document any challenges, decisions, or patterns
5. **Follow the established patterns**: Consistency is crucial
6. **Maintain restraint**: Focus on reliability over features
7. **Visual consistency**: Ensure components visually match other components
8. **Progressive implementation**: Implement basic functionality first, then add features

## Documentation

Refer to these documents for detailed guidance:

- [Footer Components Sprint Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/FooterComponentsSprintPlan.md)
- [Footer Components Architectural Decisions](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/FooterComponentsArchitecturalDecisions.md)
- [Footer Components Implementation Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/FooterComponentsImplementationPlan.md)
- [Original Clean Slate Sprint Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/SprintPlan.md)
- [Clean Slate Architectural Decisions](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/ArchitecturalDecisions.md)
- [Debug Instrumentation Guide](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/DeveloperGuides/Debugging/ComponentInstrumentation.md)