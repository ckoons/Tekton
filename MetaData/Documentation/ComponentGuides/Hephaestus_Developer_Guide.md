# Hephaestus Developer Guide

## Introduction

This guide provides detailed instructions for developers who want to create new components or extend existing components in the Hephaestus UI system. Hephaestus is the unified UI component for the Tekton AI orchestration system, designed with a focus on maintainability, isolation, and consistent user experience.

## Prerequisites

Before you begin developing for Hephaestus, ensure you have:

1. Basic knowledge of HTML, CSS, and JavaScript
2. Understanding of Shadow DOM concepts
3. Familiarity with the Tekton system architecture
4. Local development environment setup with the Tekton codebase

## Component Architecture Overview

Hephaestus uses a Shadow DOM-based component architecture to ensure proper isolation between different UI components. Each component consists of three primary files:

1. **HTML Template** - Defines the component's structure and markup
2. **CSS Styles** - Defines component-specific styling using the Hephaestus CSS naming convention
3. **JavaScript** - Implements the component's behavior and functionality

All components are loaded and managed by the `ComponentLoader` class, which handles Shadow DOM creation, theme propagation, and component lifecycle.

## Creating a New Component

Follow these steps to create a new component for Hephaestus:

### 1. Plan Your Component

Before writing any code, plan your component's:

- Purpose and functionality
- Required UI elements
- Data it will access or modify
- Integration points with other Tekton components
- State management needs

### 2. Create the Component Structure

Create the following directory structure for your component:

```
/Hephaestus/ui/components/your-component/
  your-component.html
/Hephaestus/ui/styles/your-component/
  your-component-component.css
/Hephaestus/ui/scripts/your-component/
  your-component-component.js
```

### 3. Implement the HTML Template

Create your component's HTML template in `your-component.html` following these guidelines:

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

**Guidelines:**
- Use component-specific class names following the BEM-inspired naming convention
- Include proper semantic HTML elements
- Use `id` attributes for elements you'll need to reference in JavaScript
- Don't use inline styles; all styling should be in the CSS file
- Don't include `<script>` tags; JavaScript will be loaded separately

### 4. Create Component Styles

Implement your component styles in `your-component-component.css` following these guidelines:

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

/* Content */
.your-component-content {
  flex: 1;
  padding: var(--your-component-spacing);
  overflow-y: auto;
}

/* Section */
.your-component-section {
  margin-bottom: var(--your-component-spacing);
  background-color: var(--bg-card);
  border-radius: var(--your-component-border-radius);
  padding: var(--your-component-spacing);
}

.your-component-section__title {
  margin-top: 0;
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-md);
  font-weight: 500;
}

/* Form */
.your-component-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.your-component-form__field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.your-component-form__label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-secondary);
}

.your-component-form__input {
  padding: var(--spacing-sm);
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  color: var(--text-primary);
  font-size: var(--font-size-md);
}

.your-component-form__input:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* Button */
.your-component-button {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.your-component-button--primary {
  background-color: var(--color-primary);
  color: white;
  border: none;
}

.your-component-button--primary:hover {
  background-color: var(--color-primary-hover);
}
```

**Guidelines:**
- Use the BEM-inspired naming convention for all selectors
- Use CSS variables for theming and configuration
- Organize styles logically (layout, typography, colors, etc.)
- Ensure styles are properly encapsulated within the component
- Use responsive design principles
- Implement hover, focus, and active states for interactive elements

### 5. Implement Component Functionality

Create the JavaScript functionality in `your-component-component.js`:

```javascript
/**
 * Your Component
 * 
 * Description of what this component does and its purpose in the Tekton system.
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
    
    // Example form input handler
    component.on('change', '.your-component-form__input', handleInputChange);
    
    // Register cleanup handler
    component.registerCleanup(cleanup);
  }
  
  /**
   * Handle form submission
   * @param {Event} event - The click event
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
      componentState.isLoading = false;
      updateUI();
      
      // Show error notification
      component.utils.notifications.show(
        component,
        'Error',
        `Failed to complete operation: ${error.message}`,
        'error',
        5000
      );
    }
  }
  
  /**
   * Handle input change events
   * @param {Event} event - The change event
   */
  function handleInputChange(event) {
    // Update state based on input
    const inputValue = event.target.value;
    componentState.selectedOption = inputValue;
    
    // Update UI if needed
    updateUI();
  }
  
  /**
   * Update the UI based on current state
   */
  function updateUI() {
    // Example of showing/hiding loading state
    if (componentState.isLoading) {
      submitButton.disabled = true;
      submitButton.textContent = 'Processing...';
    } else {
      submitButton.disabled = false;
      submitButton.textContent = 'Submit';
    }
    
    // Example of updating UI with data
    if (componentState.data) {
      const dataContainer = component.$('.your-component-section__content');
      if (dataContainer) {
        dataContainer.innerHTML = `
          <div class="your-component-data">
            <p>Data received: ${JSON.stringify(componentState.data)}</p>
          </div>
        `;
      }
    }
  }
  
  /**
   * Load initial data for the component
   */
  async function loadInitialData() {
    try {
      componentState.isLoading = true;
      updateUI();
      
      // Example of loading initial data
      const initialData = await callExampleAPI();
      
      componentState.data = initialData;
      componentState.isLoading = false;
      updateUI();
    } catch (error) {
      console.error('Error loading initial data:', error);
      componentState.isLoading = false;
      updateUI();
      
      // Show error notification
      component.utils.notifications.show(
        component,
        'Error',
        `Failed to load initial data: ${error.message}`,
        'error',
        5000
      );
    }
  }
  
  /**
   * Example API call function
   * @returns {Promise<Object>} - Promise resolving to API response
   */
  async function callExampleAPI() {
    // Example of using a service from tektonUI
    if (window.tektonUI?.services?.yourService) {
      return window.tektonUI.services.yourService.getData();
    }
    
    // Fallback to fetch
    const response = await fetch('/api/your-service/data');
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    return await response.json();
  }
  
  /**
   * Clean up component resources
   */
  function cleanup() {
    console.log(`Cleaning up ${component.id} component`);
    // Cancel any pending requests
    // Remove any added global event listeners
    // Clear any timers or intervals
  }
  
})(component);
```

**Guidelines:**
- Use a self-executing function with the component context
- Implement clear initialization, event handling, and cleanup logic
- Use component's scoped query selectors (`component.$` and `component.$$`)
- Use component's event delegation (`component.on`)
- Register a cleanup function for proper resource disposal
- Implement proper error handling for all async operations
- Use utility functions from `component.utils` for common UI patterns
- Follow a consistent pattern for state management and UI updates

### 6. Register Your Component

Add your component to the component registry in `/Hephaestus/ui/server/component_registry.json`:

```json
{
  "components": [
    {
      "id": "your-component",
      "name": "Your Component",
      "description": "Description of your component",
      "version": "1.0.0",
      "author": "Your Name",
      "category": "Tools",
      "icon": "your-component-icon.png",
      "entryPoint": "/components/your-component/your-component.html",
      "dependencies": [
        "hermes",
        "engram"
      ]
    }
  ]
}
```

### 7. Add Navigation Entry

Add your component to the navigation in `/Hephaestus/ui/index.html`:

```html
<li class="nav-item" data-component="your-component">
  <span class="nav-label">Your Component - Description</span>
  <span class="status-indicator"></span>
</li>
```

## Using Component Utilities

Hephaestus provides several utilities to simplify component development:

### Notifications

```javascript
// Show success notification
component.utils.notifications.show(
  component,
  'Success',
  'Operation completed successfully',
  'success',  // Options: 'success', 'error', 'warning', 'info'
  3000        // Auto-hide after 3000ms (0 to disable)
);
```

### Loading Indicators

```javascript
// Show loading overlay
component.utils.loading.show(component, 'Loading data...');

// Hide loading overlay
component.utils.loading.hide(component);
```

### Dialogs

```javascript
// Show confirmation dialog
component.utils.dialogs.confirm(
  component,
  'Are you sure you want to delete this item?',
  () => {
    // User confirmed
    deleteItem();
  },
  () => {
    // User cancelled
    console.log('Operation cancelled');
  }
);

// Show alert dialog
component.utils.dialogs.alert(
  component,
  'Operation completed successfully',
  () => {
    // Dialog closed
    console.log('User acknowledged');
  }
);

// Show custom dialog
component.utils.dialogs.show(component, {
  title: 'Custom Dialog',
  content: '<p>This is a custom dialog with HTML content.</p>',
  primaryButton: 'Proceed',
  secondaryButton: 'Cancel',
  onPrimary: () => { console.log('Primary action'); },
  onSecondary: () => { console.log('Secondary action'); },
  onClose: () => { console.log('Dialog closed'); }
});
```

### Tabs

```javascript
// Initialize tabs
const tabs = component.utils.tabs.init(component, {
  containerId: 'your-tabs-container',
  onChange: (index, tabId) => {
    console.log(`Tab changed to ${tabId} at index ${index}`);
  }
});

// Activate a tab programmatically
tabs.activateTabById('details');
```

### Form Validation

```javascript
// Define validations
const validations = {
  name: component.utils.validation.required('Name is required'),
  email: component.utils.validation.combine(
    component.utils.validation.required('Email is required'),
    component.utils.validation.email('Please enter a valid email address')
  ),
  password: component.utils.validation.combine(
    component.utils.validation.required('Password is required'),
    component.utils.validation.minLength(8, 'Password must be at least 8 characters')
  )
};

// Validate a form
if (component.utils.validation.validateForm(component, '#your-form', validations)) {
  // Form is valid, proceed with submission
  submitForm();
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

// Add it to the DOM
component.$('.your-component-content').appendChild(button);

// Create a form field
const emailField = component.utils.dom.createFormField({
  id: 'email',
  label: 'Email Address',
  type: 'email',
  placeholder: 'Enter your email',
  required: true,
  validation: component.utils.validation.email()
});

component.$('.your-component-form').appendChild(emailField);
```

## Integrating with Tekton Services

### LLM Adapter Integration

```javascript
// Get the LLM Adapter client
const llmClient = window.tektonUI.services.llmAdapter;

// Check if connected
if (!llmClient || !llmClient.connected) {
  // Show error or fallback UI
  component.utils.notifications.show(
    component,
    'Service Unavailable',
    'LLM service is currently unavailable. Some features may not work.',
    'warning',
    5000
  );
  return;
}

// Send text to LLM
async function generateWithLLM(prompt) {
  try {
    // Show loading state
    component.utils.loading.show(component, 'Generating response...');
    
    // Send prompt to LLM
    const response = await llmClient.sendPrompt({
      prompt: prompt,
      model: 'claude-3-sonnet-20240229',
      stream: true,
      onChunk: (chunk) => {
        // Handle streaming response
        const outputElement = component.$('#response-output');
        if (outputElement) {
          outputElement.textContent += chunk;
        }
      }
    });
    
    // Hide loading state
    component.utils.loading.hide(component);
    
    return response;
  } catch (error) {
    console.error('LLM error:', error);
    component.utils.loading.hide(component);
    
    component.utils.notifications.show(
      component,
      'Error',
      `Failed to generate response: ${error.message}`,
      'error',
      5000
    );
    
    return null;
  }
}
```

### Hermes Message Bus Integration

```javascript
// Get the Hermes connector
const hermes = window.tektonUI.services.hermes;

// Subscribe to events
const subscriptionId = hermes.subscribe('component.status', (data) => {
  console.log('Component status updated:', data);
  // Update UI based on status
  updateComponentStatus(data);
});

// Publish an event
hermes.publish('ui.action', {
  action: 'user_interaction',
  componentId: component.id,
  details: {
    type: 'button_click',
    buttonId: 'your-button-id',
    timestamp: new Date().toISOString()
  }
});

// Clean up subscription when component is unloaded
component.registerCleanup(() => {
  hermes.unsubscribe(subscriptionId);
});
```

### Engram Memory Integration

```javascript
// Get the Engram client
const engram = window.tektonUI.services.engram;

// Store component state
async function saveComponentState() {
  try {
    await engram.storeMemory({
      type: 'component_state',
      component: component.id,
      data: {
        // Component state to persist
        selectedTab: tabs.getActiveTabId(),
        settings: {
          // User settings
          showDetails: true,
          sortOrder: 'asc'
        }
      }
    });
  } catch (error) {
    console.error('Failed to save component state:', error);
  }
}

// Retrieve component state
async function loadComponentState() {
  try {
    const state = await engram.retrieveMemory({
      type: 'component_state',
      component: component.id
    });
    
    if (state) {
      // Restore component state
      if (state.selectedTab && tabs) {
        tabs.activateTabById(state.selectedTab);
      }
      
      if (state.settings) {
        // Apply user settings
        updateSettings(state.settings);
      }
    }
  } catch (error) {
    console.error('Failed to load component state:', error);
  }
}
```

## Testing Your Component

Follow these testing steps to ensure your component works correctly:

1. **Isolation Testing**
   - Verify your component's styles don't leak outside the Shadow DOM
   - Ensure your component doesn't affect other components when loaded

2. **Theme Testing**
   - Switch between light and dark themes and verify the component updates correctly
   - Check that all UI elements follow the theme colors

3. **Functionality Testing**
   - Test all interactive elements (buttons, forms, etc.)
   - Verify error handling for API calls and user interactions
   - Test edge cases (empty data, slow network, etc.)

4. **Integration Testing**
   - Test integration with required Tekton services
   - Verify the component gracefully handles unavailable services

5. **Performance Testing**
   - Check that the component loads quickly
   - Ensure it doesn't block the UI during long operations
   - Test with large datasets if applicable

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

### Debug Mode

Enable debug mode for more verbose logging:

```javascript
// Set debug mode
window.tektonUI.debug = true;

// Use debug logging
if (window.tektonUI.debug) {
  console.log('Component state:', componentState);
}
```

## Conclusion

This guide provides the foundation for creating components in the Hephaestus UI system. By following these patterns and guidelines, you'll create components that are consistent, maintainable, and properly isolated from other parts of the system.

For more detailed information, refer to the [Technical Documentation](./technical_documentation.md) and the existing component implementations in the Hephaestus codebase.