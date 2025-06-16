# Fix GUI Sprint - Claude Code Prompt (SESSION 5: HERMES COMPONENT IMPLEMENTATION)

## Overview
This document serves as the prompt for the fifth Claude Code session working on the Fix GUI Sprint. In previous sessions, we successfully implemented the Athena and Ergon components and refactored the UI manager into manageable chunks. Now we're ready to implement the Hermes component, which is the next in our roadmap.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This Development Sprint focuses on implementing reliable UI components following our standardized patterns.

**IMPORTANT: The previous pragmatic refactoring in Session 4 was successful, and we now have working Athena and Ergon components with a maintainable UI architecture. Continue following the same direct HTML injection pattern for the Hermes component.**

## Current Status - Success

We have successfully implemented:

1. **Athena Component**: Fully functional with knowledge graph and chat interfaces
2. **Ergon Component**: Complete with agent management, executions, and workflow tabs
3. **UI Manager Refactoring**: Modularized structure with manageable file sizes
4. **Component Architecture**: Established reliable patterns for component implementation
5. **Technical Debt Resolution**: Fixed WebSocket connections, chat positioning, server stability

## Hermes Component Implementation

Hermes is a crucial component for service orchestration and component registration in Tekton. It serves as the communication hub between all Tekton components.

### Component Structure

1. **Header**: Compact title bar with service status indicators
2. **Tab Navigation**:
   - Services (default) - Lists available services with status and controls
   - Registrations - Shows registered components with details
   - Communication - Displays message flow between components 
   - Logs - Shows service logs with filtering options
   - Team Chat - Standard team communication interface

### Implementation Requirements

1. **Class-Based Architecture**:
```javascript
class HermesComponent {
  constructor() {
    this.state = {
      initialized: false,
      activeTab: 'services', // Default tab
      services: [], // List of available services
      registrations: [], // List of registered components
      messages: [] // Communication messages
    };
  }
  
  init() {
    console.log('Initializing Hermes component');
    this.loadComponentHTML();
    this.setupEventListeners();
    this.state.initialized = true;
    return this;
  }
  
  async loadComponentHTML() {
    // Implementation...
  }
  
  setupEventListeners() {
    // Implementation...
  }
  
  // Component-specific methods...
}

// Create global instance
window.hermesComponent = new HermesComponent();
```

2. **UI Features**:
   - Real-time service status indicators (active/inactive)
   - Component registration management interface
   - Visual communication flow diagram
   - Log filtering and search capability
   - Standard team chat interface consistent with other components

3. **Technical Integration**:
   - WebSocket connection for real-time updates
   - REST API for service management 
   - Consistent styling using the standardized CSS framework
   - DOM-based event handling for component interaction

## Design Guidelines

Follow these guidelines established in our previous successful implementations:

1. **Direct HTML Injection**: Use template strings for component HTML rather than external files
2. **Class-Based Architecture**: Use ES6 classes for component encapsulation
3. **DOM-Based UI**: No Shadow DOM; direct DOM manipulation for simplicity
4. **State Management**: Maintain component state within the class
5. **BEM Styling**: Use Block Element Modifier convention for CSS organization
6. **Standardized Panel Structure**: Follow our established Header, Tabs, Content, Footer pattern

## Implementation Steps

1. **Component Analysis**:
   - Document Hermes tab structure and functionality
   - Identify special requirements like service visualization
   - Map out event handlers and state management needs
   - Create implementation plan

2. **Core Implementation**:
   - Create the HermesComponent class with state management
   - Implement loadHermesComponent() function
   - Create standardized tab interface
   - Implement service listing with status indicators
   - Add component registration management
   - Implement communication visualization
   - Add log filtering and display
   - Integrate team chat interface

3. **Testing**:
   - Test navigation between tabs
   - Verify service status updates
   - Check registration management
   - Test log filtering
   - Ensure chat interface works properly
   - Verify WebSocket connectivity

## Key Files

### Implementation Files
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/hermesComponent.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager-hermes.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/hermes.css`

### HTML Template Structure
```html
<div id="hermes-container" class="hermes" style="height: 100%; width: 100%;">
  <!-- HEADER SECTION -->
  <header class="hermes__header">
    <h2>Hermes</h2>
    <div class="hermes__metrics">
      <!-- Service status indicators -->
    </div>
  </header>
  
  <!-- MENU/TAB NAVIGATION -->
  <div class="hermes__tabs">
    <div class="tab active" data-tab="services">Services</div>
    <div class="tab" data-tab="registrations">Registrations</div>
    <div class="tab" data-tab="communication">Communication</div>
    <div class="tab" data-tab="logs">Logs</div>
    <div class="tab" data-tab="team-chat">Team Chat</div>
  </div>
  
  <!-- WORK AREA -->
  <div class="tab-content">
    <!-- Services Panel -->
    <div id="services-panel" class="panel active">
      <div class="hermes__services">
        <!-- Service cards with status -->
      </div>
    </div>
    
    <!-- Registrations Panel -->
    <div id="registrations-panel" class="panel">
      <div class="hermes__registrations">
        <!-- Component registration details -->
      </div>
    </div>
    
    <!-- Communication Panel -->
    <div id="communication-panel" class="panel">
      <div class="hermes__communication">
        <!-- Communication flow visualization -->
      </div>
    </div>
    
    <!-- Logs Panel -->
    <div id="logs-panel" class="panel">
      <div class="hermes__logs">
        <!-- Log display with filtering -->
      </div>
    </div>
    
    <!-- Team Chat Panel -->
    <div id="team-chat-panel" class="panel chat-panel">
      <!-- Reuse standard chat panel structure -->
    </div>
  </div>
</div>
```

## CSS Implementation (BEM Pattern)

```css
/* Block */
.hermes { }

/* Elements */
.hermes__header { }
.hermes__tabs { }
.hermes__services { }
.hermes__registrations { }
.hermes__communication { }
.hermes__logs { }

/* Service Cards */
.hermes__service-card { }
.hermes__service-title { }
.hermes__service-status { }
.hermes__service-controls { }

/* Registration Items */
.hermes__registration-item { }
.hermes__registration-details { }

/* Communication Visualization */
.hermes__communication-diagram { }
.hermes__communication-arrow { }
.hermes__communication-node { }

/* Log Interface */
.hermes__log-filters { }
.hermes__log-display { }
.hermes__log-entry { }
.hermes__log-search { }

/* Modifiers */
.hermes__service-status--active { }
.hermes__service-status--inactive { }
.hermes__log-entry--error { }
.hermes__log-entry--warning { }
.hermes__log-entry--info { }
```

## Special Features to Implement

1. **Service Status Dashboard**:
   - Card-based layout showing service status
   - Status indicators with color coding (green for active, red for inactive)
   - Service control buttons (restart, configure)
   - Service details display (version, uptime, endpoints)

2. **Component Registration Management**:
   - List of registered components with details
   - Registration form for adding new components
   - Visual indicator of registration status
   - Connection testing interface

3. **Communication Flow Visualization**:
   - Network diagram showing message flow between components
   - Real-time updates for active communications
   - Filtering by component or message type
   - Details panel for message inspection

4. **Log Interface**:
   - Real-time log display with auto-scroll
   - Filtering by level (error, warning, info)
   - Text search capability
   - Clear button and export functionality
   - Timestamp display and sorting

## Integration Points

1. **WebSocket for Real-Time Updates**:
   - Connect to Hermes service for status updates
   - Listen for service state changes
   - Receive log entries in real-time
   - Track communication flow

2. **Service API Integration**:
   - Fetch service list and status
   - Manage component registrations
   - Control service operations (restart, configure)
   - Query logs with filtering

3. **Team Chat Integration**:
   - Reuse the shared team chat component
   - Ensure proper styling within Hermes context
   - Maintain chat history state

## Testing Points

1. **Functionality Testing**:
   - All tabs should display correctly
   - Services should show proper status
   - Registrations should be manageable
   - Communication flow should visualize properly
   - Logs should display with filtering
   - Team chat should work correctly

2. **Integration Testing**:
   - WebSocket connection should work
   - Service API calls should function
   - Real-time updates should display

3. **UI Testing**:
   - Styling should be consistent with other components
   - Responsive layout should work at different sizes
   - Interactive elements should provide feedback
   - Error states should display properly

## Implementation Notes

- Follow the same implementation pattern used for Athena and Ergon
- Maintain consistency in styling and interaction patterns
- Ensure proper error handling for all network operations
- Add appropriate loading states for asynchronous operations
- Use the standard tab navigation system from shared utilities
- Implement proper WebSocket reconnection handling

## Deliverables

1. **HermesComponent Class Implementation**:
   - Complete class with proper initialization
   - State management for all component aspects
   - Event handlers for user interactions

2. **UI Integration**:
   - Properly styled component following BEM conventions
   - Tab navigation consistent with other components
   - Service status dashboard with interactive elements
   - Component registration interface
   - Communication visualization
   - Log display with filtering
   - Team chat integration

3. **Documentation**:
   - Clear comments explaining component functionality
   - Documentation of integration points
   - Usage examples for service API

4. **Testing**:
   - Verification of all functionality
   - Confirmation of proper styling
   - Validation of WebSocket integration

## Success Criteria

The Hermes component implementation will be considered successful if:

1. All tabs function correctly with proper content display
2. Service status updates are shown in real time
3. Component registrations can be viewed and managed
4. Communication flow is properly visualized
5. Logs are displayed with filtering capabilities
6. Team chat works consistently with other components
7. The component follows our established design patterns
8. The implementation is maintainable and follows BEM conventions

With the successful implementation of the Hermes component, we will continue with the next component in our roadmap: Engram.