# Apollo UI Development Sprint - Claude Code Prompt

## Overview

You are tasked with implementing the Apollo UI component for the Tekton system. Apollo is the executive coordinator and predictive planning system responsible for managing LLM operations, token flow, and behavioral reliability. The backend components are being implemented in a separate sprint, and this sprint focuses exclusively on creating the UI component.

Your goal is to create a UI component that strictly follows the patterns established in the Clean Slate Sprint, using the Athena component as the "golden example." The Apollo UI will provide visualization and control capabilities for monitoring LLM health, managing token budgets, configuring protocols, and visualizing predictions.

## Key Requirements

1. **Strict Component Isolation**: Follow the exact isolation pattern from the Clean Slate Sprint
2. **Athena as Reference**: Use the Athena component as your primary reference
3. **Standard UI Elements**: Implement HEADER, MENU BAR with chat options, and FOOTER exactly as in Athena
4. **Tab-Based Structure**: Implement navigation tabs for different Apollo functions
5. **Visualizations**: Create intuitive visualizations for LLM health and metrics
6. **Service Layer**: Implement a service class for API communication
7. **Standards Compliance**: Adhere to all Tekton UI standards

## Component Features

The Apollo UI component should include the following features:

1. **HEADER**: Matches Athena's header height and style
2. **MENU BAR**: Includes Attention Chat and Team Chat options, matching Athena's implementation
3. **Dashboard**: Overview of all LLM sessions with health indicators
4. **Sessions**: Detailed view of individual LLM sessions with metrics
5. **Token Budgets**: Tools for managing token allocations
6. **Protocols**: Interface for protocol management
7. **Forecasting**: Predictive visualizations for LLM behavior
8. **Actions**: Tools for executing commands and interventions
9. **Settings**: Configuration options for the component
10. **FOOTER**: Matches Athena's footer implementation

## Directory Structure

Create the following directory structure:

```
Apollo/
├── ui/
│   ├── apollo-component.html       # Main component file
│   ├── scripts/
│   │   ├── apollo-component.js     # Component implementation
│   │   ├── apollo-service.js       # API service layer
│   │   └── [other component scripts]
│   └── styles/
│       └── apollo.css              # Component styles
```

## Implementation Instructions

### Step 1: Create Basic Component Structure

1. Create `apollo-component.html` based on the Athena template
2. Implement the component container, HEADER, MENU BAR with chat options, and FOOTER
3. Set up basic styling using BEM conventions
4. Ensure proper script loading and initialization
5. Match HEADER and MENU BAR heights exactly with Athena's implementation

### Step 2: Implement MENU BAR with Chat Options

1. Create MENU BAR with Attention Chat and Team Chat options
2. Match Athena's MENU BAR height exactly
3. Style according to Athena's implementation
4. Implement consistent event handling

### Step 3: Implement Tab Navigation

1. Create component-specific tab switching function
2. Implement UI Manager protection
3. Add HTML panel protection
4. Ensure all DOM queries are scoped to the component container

### Step 4: Implement FOOTER

1. Create FOOTER section following Athena's implementation exactly
2. Include status indicators and action buttons
3. Match styling and positioning
4. Implement functionality consistent with Athena

### Step 5: Create Service Layer

1. Implement `apollo-service.js` following the `AthenaClient` pattern
2. Include methods for all Apollo API endpoints
3. Add error handling and fallbacks
4. Implement environment-aware base URL resolution

### Step 6: Implement Dashboard

1. Create grid layout for session overview
2. Implement health status indicators
3. Add token usage visualizations
4. Create alert indicators for potential issues

### Step 7: Implement Other Tabs

1. Create detailed session view
2. Implement token budget interface
3. Add protocol management panel
4. Create forecasting visualizations
5. Implement action panel for command execution

### Step 8: Add Real-Time Updates

1. Implement polling mechanism for data updates
2. Ensure efficient DOM updates
3. Add configurable refresh rates
4. Implement WebSocket handler for streaming data

### Step 9: Polish and Finalize

1. Refine visual elements for consistency
2. Add comprehensive error handling
3. Implement responsive design considerations
4. Complete documentation

## Critical Implementation Notes

### Component Isolation

Ensure strict component isolation by:

1. Using component-specific prefixes for all JavaScript functions
2. Scoping all DOM queries to the component container
3. Using inline event handlers with component-specific functions
4. Protecting the HTML panel from being hidden
5. Implementing UI Manager protection mechanisms
6. Following BEM naming convention for all CSS classes

### Menu Bar and Header Heights

1. HEADER must exactly match Athena's height
2. MENU BAR must exactly match Athena's height
3. If any secondary menu bars are added, they must match the same height
4. Use the same dimensions and proportions as Athena for consistency

### API Integration

For API integration, use mock data initially, then:

1. Create methods for each Apollo API endpoint
2. Implement error handling and fallbacks
3. Add data transformation utilities
4. Support both HTTP and WebSocket communication

### Implementation Approach

1. Start with core functionality
2. Use mock data for initial development
3. Focus on component structure and isolation first
4. Add visualizations incrementally
5. Test thoroughly with other components

## Reference Components

### Athena Component

The primary reference is the Athena component. Study these files:

- `/Athena/ui/athena-component.html`
- `/Athena/ui/scripts/athena-component.js`
- `/Athena/ui/scripts/athena-service.js`

### Apollo Backend

The Apollo backend architecture is defined in:

- `/MetaData/DevelopmentSprints/Clean_Slate_Sprint/apollo_specification.md`
- `/MetaData/DevelopmentSprints/Apollo_Instantiation_Sprint/ImplementationPlan.md`

### UI Standards

Follow the standards defined in:

- `/MetaData/UI/ComponentImplementationStandard.md`
- `/MetaData/DevelopmentSprints/Clean_Slate_Sprint/ComponentImplementationGuide.md`

## Important Guidelines

1. **Strict Adherence**: Follow the Athena/Clean Slate pattern exactly
2. **No External Dependencies**: Do not add third-party libraries
3. **Progressive Enhancement**: Implement core functionality first
4. **Thorough Testing**: Test with other components frequently
5. **Consistent Styling**: Maintain visual harmony with Tekton UI

## Working Guidelines

### Validation Process

Before proceeding to each next step:

1. Verify component loads correctly in isolation
2. Test with other components to ensure no interference
3. Check that tab switching functions correctly
4. Ensure HTML panel protection works
5. Validate that all DOM queries are properly scoped
6. Verify that styling is correctly isolated
7. Confirm HEADER, MENU BAR, and FOOTER match Athena's implementation

### Collaboration with Casey

1. Seek feedback at each phase of implementation
2. Ask for clarification when encountering ambiguity
3. Propose solutions for complex visualizations
4. Provide clear status updates on progress

## Success Criteria

Your implementation will be considered successful if:

1. The Apollo UI component loads reliably in the Hephaestus UI
2. HEADER, MENU BAR, and FOOTER match Athena's implementation exactly
3. All tabs and features function properly
4. The component adheres strictly to the Clean Slate standards
5. The component works harmoniously alongside other components
6. The UI accurately represents Apollo's functionality
7. All visual elements follow the Tekton design language
8. Documentation is complete and accurate

## Start with Component Structure

Begin by creating the basic component structure in `apollo-component.html`, following the Athena pattern exactly. Focus on establishing the proper isolation patterns, HEADER, MENU BAR with chat options, and FOOTER before moving on to specific visualizations.

Here's a template to get started:

```html
<!-- Apollo Executive Component - LLM Monitoring and Control Center -->
<div id="apollo-component">
  <!-- Component Header -->
  <div class="apollo__header">
    <div class="apollo__title">
      <img src="/images/icon.jpg" alt="Apollo" class="apollo__logo">
      <h1>Apollo Executive Coordinator</h1>
    </div>
    <div class="apollo__controls">
      <!-- Header controls -->
    </div>
  </div>
  
  <!-- Menu Bar with Chat Options -->
  <div class="apollo__menu-bar">
    <div class="apollo__chat-options">
      <div class="apollo__chat-option apollo__chat-option--attention">Attention Chat</div>
      <div class="apollo__chat-option apollo__chat-option--team">Team Chat</div>
    </div>
    <div class="apollo__menu-actions">
      <!-- Additional menu actions -->
    </div>
  </div>
  
  <!-- Tab Navigation -->
  <div class="apollo__tabs">
    <div class="apollo__tab apollo__tab--active" data-tab="dashboard" 
         onclick="apollo_switchTab('dashboard'); return false;">Dashboard</div>
    <!-- Other tabs -->
  </div>
  
  <!-- Content Panels -->
  <div class="apollo__content">
    <div id="dashboard-panel" class="apollo__panel apollo__panel--active">
      <!-- Dashboard content -->
    </div>
    <!-- Other panels -->
  </div>
  
  <!-- Footer -->
  <div class="apollo__footer">
    <div class="apollo__footer-status">
      <!-- Status indicators -->
    </div>
    <div class="apollo__footer-actions">
      <!-- Footer actions -->
    </div>
  </div>
  
  <!-- Component will be loaded by the Hephaestus component loader -->
  <script src="scripts/apollo-component.js" type="module"></script>
</div>
```

Casey will review your work and provide guidance at each stage of implementation.

## References

- [Apollo Specification](/MetaData/DevelopmentSprints/Clean_Slate_Sprint/apollo_specification.md)
- [Apollo Instantiation Sprint Implementation Plan](/MetaData/DevelopmentSprints/Apollo_Instantiation_Sprint/ImplementationPlan.md)
- [Component Implementation Standard](/MetaData/UI/ComponentImplementationStandard.md)
- [Clean Slate Sprint Documentation](/MetaData/DevelopmentSprints/Clean_Slate_Sprint/)
- [Athena Component](/Athena/ui/athena-component.html)