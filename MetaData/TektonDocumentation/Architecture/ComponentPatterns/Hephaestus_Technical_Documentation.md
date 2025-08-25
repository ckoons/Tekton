# Hephaestus Technical Documentation

## Overview

Hephaestus is the unified user interface component for the Tekton CI orchestration system. It provides a component-based, isolated UI for interacting with all Tekton subsystems through a combination of terminal and graphical interfaces. Hephaestus is designed with a focus on simplicity, maintainability, and proper component isolation.

This document provides technical details about the Hephaestus architecture, implementation, and integration points for developers working on or extending the system.

## Architecture

### Core Design Principles

1. **Vanilla Web Technologies**: Hephaestus is implemented using standard HTML, CSS, and JavaScript without complex frameworks or build systems.
2. **Shadow DOM Isolation**: Each component is loaded in its own Shadow DOM for proper style encapsulation and isolation.
3. **Component-Based Design**: The UI is organized into discrete components, each representing a Tekton subsystem.
4. **Theme Propagation**: Theme variables are propagated across shadow boundaries for consistent UI appearance.
5. **WebSocket Communication**: Real-time communication with backend services is implemented through WebSockets.
6. **Graceful Degradation**: Components handle unavailable services and error states gracefully.

### System Components

The Hephaestus UI consists of the following major technical components:

1. **ComponentLoader**: Manages the loading, lifecycle, and isolation of UI components.
2. **UI Manager**: Controls the main application UI, navigation, and component switching.
3. **Terminal System**: Provides terminal interface for command-line interaction.
4. **WebSocket Client**: Handles real-time communication with backend services.
5. **Component Utilities**: Shared utilities and patterns for component implementation.
6. **State Management**: Client-side state persistence and synchronization.

## Component Isolation Strategy

Hephaestus implements a Shadow DOM-based component isolation strategy to address style bleeding, DOM duplication, and event handler collisions between components.

### Shadow DOM Implementation

Each component is loaded into its own Shadow DOM, attached to a dedicated host element:

```javascript
function _createShadowDOM(componentId, containerElement) {
  // Clear container
  containerElement.innerHTML = '';
  
  // Create host element
  const host = document.createElement('div');
  host.id = `${componentId}-host`;
  host.dataset.componentId = componentId;
  containerElement.appendChild(host);
  
  // Create shadow root
  const shadowRoot = host.attachShadow({ mode: 'open' });
  
  // Add component attribute to the shadow root
  shadowRoot.host.dataset.component = componentId;
  
  return shadowRoot;
}
```

### Theme Propagation

CSS variables are used to propagate theming across shadow boundaries:

```javascript
function _addThemeStylesToShadowRoot(shadowRoot) {
  const themeStyle = document.createElement('style');
  themeStyle.textContent = `
    :host {
      /* Import theme variables from parent */
      --bg-primary: var(--bg-primary, #1e1e1e);
      --text-primary: var(--text-primary, #f0f0f0);
      /* ... additional variables ... */
    }
  `;
  shadowRoot.prepend(themeStyle);
}
```

### Component Context

Components are provided with a scoped context object that includes utilities for DOM querying, event delegation, and lifecycle management:

```javascript
const component = {
  id: componentId,
  root: shadowRoot,
  
  // Scoped query selector
  $: function(selector) {
    return this.root.querySelector(selector);
  },
  
  // Event delegation helper
  on: function(eventType, selector, handler) {
    this.root.addEventListener(eventType, (event) => {
      const elements = this.root.querySelectorAll(selector);
      const element = event.target.closest(selector);
      if (element && [...elements].includes(element)) {
        handler.call(element, event, this);
      }
    });
  },
  
  // Register cleanup function
  registerCleanup: function(cleanupFn) {
    window.__componentCleanupHandlers = window.__componentCleanupHandlers || {};
    window.__componentCleanupHandlers[componentId] = cleanupFn;
  }
}
```

## Component Structure

### File Organization

Components follow a standardized file structure:

```
/ui/components/{component-name}/{component-name}-component.html   # Component HTML template
/ui/styles/{component-name}/{component-name}-component.css        # Component-specific styles
/ui/scripts/{component-name}/{component-name}-component.js        # Component functionality
```

### CSS Naming Convention

Hephaestus uses a modified BEM (Block-Element-Modifier) methodology with component prefixes:

```
{componentId}-{block}__{element}--{modifier}
```

Examples:
```css
.rhetor-container { }                     /* Block */
.rhetor-container__header { }             /* Element */
.rhetor-container__header--sticky { }     /* Modifier */
```

## Component Lifecycle

### Loading Process

1. **Initialization**: A component is requested for loading by the UI manager.
2. **Shadow DOM Creation**: A new shadow root is created and attached to a host element.
3. **Theme Integration**: Theme variables are added to the shadow root.
4. **Content Loading**: Component HTML content is fetched and loaded into the shadow root.
5. **Style Loading**: Component-specific styles are fetched and added to the shadow root.
6. **Script Initialization**: Component script is loaded and executed within the component context.
7. **Cleanup Registration**: Component registers any cleanup handlers needed.

### Cleanup Process

1. **Triggering**: Cleanup occurs when switching to another component or unloading.
2. **Executing Handlers**: Any registered cleanup functions are executed.
3. **Observer Disconnection**: Theme observers are disconnected.
4. **DOM Removal**: The shadow root host is removed from the DOM.

## Component Utilities

Hephaestus provides a comprehensive set of utilities for component implementation:

### Notification System

```javascript
// Show a notification within a component
component.utils.notifications.show(
  component,
  "Success",
  "Operation completed successfully",
  "success",
  3000
);
```

### Loading Indicators

```javascript
// Show a loading indicator
const loader = component.utils.loading.show(component, "Loading data...");

// Hide the loading indicator when done
component.utils.loading.hide(component);
```

### Dialog System

```javascript
// Show a confirmation dialog
component.utils.dialogs.confirm(
  component,
  "Are you sure you want to delete this item?",
  onConfirm,
  onCancel
);
```

### Tabs System

```javascript
// Initialize tabs
const tabs = component.utils.tabs.init(component, {
  containerId: 'tabs-container',
  onChange: (index, tabId) => console.log(`Tab changed to ${tabId}`)
});

// Activate a tab programmatically
tabs.activateTabById('settings');
```

### Form Validation

```javascript
// Define validations
const validations = {
  email: component.utils.validation.email(),
  password: component.utils.validation.combine(
    component.utils.validation.required(),
    component.utils.validation.minLength(8)
  )
};

// Validate a form
if (component.utils.validation.validateForm(component, '#login-form', validations)) {
  // Form is valid, proceed with submission
}
```

### DOM Helpers

```javascript
// Create an element with attributes and content
const button = component.utils.dom.createElement('button', {
  className: 'your-component-button your-component-button--primary',
  id: 'your-button-id',
  onClick: () => { console.log('Button clicked'); }
}, 'Click Me');

// Create a form field
const emailField = component.utils.dom.createFormField({
  id: 'email',
  label: 'Email Address',
  type: 'email',
  placeholder: 'Enter your email',
  required: true,
  validation: component.utils.validation.email()
});
```

## Integration Points

### LLM Adapter Integration

Hephaestus integrates with the LLM Adapter for CI capabilities:

```javascript
// Get the LLM Adapter client instance
const llmClient = window.tektonUI.services.llmAdapter;

// Send a prompt to the LLM
const response = await llmClient.sendPrompt({
  prompt: "Explain the Tekton architecture",
  model: "claude-3-sonnet-20240229",
  stream: true,
  onChunk: (chunk) => {
    // Handle streaming response
    console.log(chunk);
  }
});
```

### Hermes Message Bus

Components can publish and subscribe to events through the Hermes message bus:

```javascript
// Get the Hermes connector
const hermes = window.tektonUI.services.hermes;

// Subscribe to events
hermes.subscribe('component.status', (data) => {
  console.log('Component status updated:', data);
});

// Publish an event
hermes.publish('ui.action', {
  action: 'component_selected',
  componentId: 'rhetor'
});
```

### Engram Memory System

Components can store and retrieve persistent data through Engram:

```javascript
// Get the Engram client
const engram = window.tektonUI.services.engram;

// Store component state
await engram.storeMemory({
  type: 'component_state',
  component: 'rhetor',
  data: {
    selectedTab: 'templates',
    lastUsedModel: 'claude-3-sonnet'
  }
});

// Retrieve component state
const state = await engram.retrieveMemory({
  type: 'component_state',
  component: 'rhetor'
});
```

## WebSocket Communication

Hephaestus uses WebSockets for real-time communication with backend services:

```javascript
// Message format for WebSocket communication
const message = {
  type: "COMMAND",
  source: "UI",
  target: "RHETOR",
  timestamp: new Date().toISOString(),
  payload: {
    command: "process_prompt",
    prompt: "Explain the Tekton architecture"
  }
};

// Send message
websocketManager.sendMessage(message);

// Register event handler for responses
websocketManager.addEventListener("message", (event) => {
  const response = JSON.parse(event.data);
  if (response.type === "RESPONSE" && response.source === "RHETOR") {
    console.log("Received response:", response.payload);
  }
});
```

## State Management

Hephaestus implements client-side state management for component persistence:

```javascript
// Get the state manager
const stateManager = window.tektonUI.stateManager;

// Set state value
stateManager.setState('rhetor.selectedModel', 'claude-3-sonnet');

// Get state value
const model = stateManager.getState('rhetor.selectedModel');

// Subscribe to state changes
stateManager.subscribe('rhetor.selectedModel', (newValue) => {
  console.log('Selected model changed:', newValue);
});
```

## Error Handling

Hephaestus implements a robust error handling strategy:

1. **Component Loading Errors**: If a component fails to load, an error UI is shown with retry capability.
2. **API Request Errors**: Service requests use try/catch with appropriate fallbacks.
3. **WebSocket Disconnections**: Automatic reconnection with exponential backoff.
4. **Missing Services**: Graceful degradation when backend services are unavailable.

## Themes

Hephaestus supports multiple themes through CSS variables:

```css
/* Theme variable definition */
:root[data-theme="dark-blue"] {
  --bg-primary: #1a1a2e;
  --bg-secondary: #16213e;
  --color-primary: #0f3460;
  --color-secondary: #533483;
  --text-primary: #e1e1e1;
  --text-secondary: #a7a7a7;
}

/* Theme switching */
document.documentElement.dataset.theme = "dark-blue";
```

## Adding New Components

To add a new component to Hephaestus:

1. **Create HTML Template**: Create a new HTML file at `/ui/components/{component-name}/{component-name}-component.html`.
2. **Add CSS Styling**: Create component-specific styles at `/ui/styles/{component-name}/{component-name}-component.css`.
3. **Implement Functionality**: Create JavaScript functionality at `/ui/scripts/{component-name}/{component-name}-component.js`.
4. **Register Component**: Add the component entry to the component registry in `/ui/server/component_registry.json`.
5. **Add Navigation Entry**: Add the component to the navigation list in `index.html`.

## Component Implementation Example

Here's a simplified example of a component implementation:

### HTML Template

```html
<div class="your-component-container">
  <div class="your-component-header">
    <h2 class="your-component-header__title">Your Component Title</h2>
  </div>
  
  <div class="your-component-content">
    <!-- Component-specific content goes here -->
    <div class="your-component-section">
      <h3 class="your-component-section__title">Section Title</h3>
      <div class="your-component-section__content">
        <!-- Section content -->
      </div>
    </div>
    
    <!-- Example of a form element -->
    <div class="your-component-form">
      <div class="your-component-form__field">
        <label class="your-component-form__label">Field Label</label>
        <input type="text" class="your-component-form__input" id="your-field-id">
      </div>
      <button class="your-component-button your-component-button--primary" id="your-submit-button">
        Submit
      </button>
    </div>
  </div>
</div>
```

### CSS Styling

```css
/* Component Variables */
:host {
  --your-component-spacing: var(--spacing-md, 16px);
  --your-component-border-radius: var(--border-radius-md, 8px);
}

/* Container */
.your-component-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

/* Header */
.your-component-header {
  padding: var(--your-component-spacing);
  border-bottom: 1px solid var(--border-color);
}

.your-component-header__title {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: 600;
}

/* Additional styles... */
```

### JavaScript Functionality

```javascript
/**
 * Your Component
 */
(function(component) {
  // Component initialization
  console.log(`Initializing ${component.id} component`);
  
  // Cache DOM elements
  const container = component.$('.your-component-container');
  const submitButton = component.$('#your-submit-button');
  
  // Initialize state
  let componentState = {
    isLoading: false,
    data: null,
    selectedOption: 'default'
  };
  
  // Set up event listeners
  initializeEventListeners();
  
  // Initial data loading
  loadInitialData();
  
  /**
   * Initialize component event listeners
   */
  function initializeEventListeners() {
    // Example button click handler
    component.on('click', '#your-submit-button', handleSubmit);
    
    // Register cleanup handler
    component.registerCleanup(cleanup);
  }
  
  /**
   * Handle form submission
   */
  async function handleSubmit(event) {
    try {
      // Show loading state
      componentState.isLoading = true;
      updateUI();
      
      // Example API call
      const result = await callExampleAPI();
      
      // Update state with result
      componentState.data = result;
      componentState.isLoading = false;
      
      // Update UI with new data
      updateUI();
      
      // Show success notification
      component.utils.notifications.show(
        component,
        'Success',
        'Operation completed successfully',
        'success',
        3000
      );
    } catch (error) {
      // Handle errors
      console.error('Error in submit handler:', error);
      // Error handling...
    }
  }
  
  /**
   * Clean up component resources
   */
  function cleanup() {
    console.log(`Cleaning up ${component.id} component`);
    // Cleanup logic...
  }
  
})(component);
```

## Testing

Hephaestus employs testing procedures for new components:

1. **Isolation Testing**: Verify CSS doesn't leak between components.
2. **Theme Testing**: Ensure theme changes propagate correctly to Shadow DOM.
3. **Component Switching**: Test rapid switching between components.
4. **Error Handling**: Verify component failure doesn't affect others.
5. **WebSocket Testing**: Test real-time communication with backend services.

## Security Considerations

1. **Content Security**: No dynamic script evaluation outside the controlled component loader.
2. **Data Validation**: All user inputs are validated before processing.
3. **Error Exposure**: Error details are shown only in debug mode.
4. **CORS Handling**: API requests follow proper CORS policies.

## Performance Optimization

1. **Lazy Loading**: Components are loaded only when needed.
2. **Resource Caching**: Component resources use cache-busting parameters for updates.
3. **Event Delegation**: Event handling uses delegation to minimize handlers.
4. **DOM Operations**: Batch DOM operations to minimize reflows.

## Accessibility

Hephaestus implements accessibility features:

1. **Keyboard Navigation**: All interactive elements are keyboard accessible.
2. **ARIA Attributes**: Proper ARIA roles and attributes for UI elements.
3. **Focus Management**: Improved focus handling for UI interactions.
4. **Color Contrast**: Color schemes follow WCAG contrast guidelines.

## Best Practices

1. **Performance**
   - Minimize DOM operations by batching updates
   - Use event delegation for event handlers
   - Debounce/throttle handlers for frequent events (scroll, resize, etc.)

2. **Error Handling**
   - Always use try/catch blocks for async operations
   - Provide user-friendly error messages
   - Include fallbacks for unavailable services

3. **Accessibility**
   - Use semantic HTML elements
   - Include proper ARIA attributes
   - Ensure keyboard navigability
   - Maintain sufficient color contrast

4. **Code Organization**
   - Use clear function and variable names
   - Comment complex code sections
   - Break large functions into smaller, focused functions
   - Keep related functionality together

5. **State Management**
   - Centralize component state in a single object
   - Implement a clear update pattern for UI changes
   - Consider using a simple state management pattern for complex components

## Troubleshooting

### Common Issues and Solutions

1. **Component Not Loading**
   - Check browser console for errors
   - Verify file paths in component registry
   - Check for syntax errors in HTML, CSS, or JavaScript

2. **Style Issues**
   - Ensure CSS selectors match your HTML structure
   - Verify theme variables are properly used
   - Check for CSS syntax errors

3. **JavaScript Errors**
   - Use browser dev tools to debug
   - Check for undefined variables or functions
   - Verify proper use of async/await

4. **Service Integration Issues**
   - Check if the service is running
   - Verify connection parameters
   - Implement proper error handling for service failures

## Conclusion

Hephaestus represents a modern, maintainable UI architecture for the Tekton system, using Shadow DOM isolation to ensure component independence while providing a consistent user experience. The component-based design allows for easy extension and maintenance, while the standardized utilities promote code reuse and consistency across the system.