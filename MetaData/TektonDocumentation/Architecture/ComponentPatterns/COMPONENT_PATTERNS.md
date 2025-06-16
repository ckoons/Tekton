# Component Patterns Guide

**Last Updated:** May 21, 2025

This guide documents the standardized patterns for creating components within the Hephaestus UI framework. Following these patterns ensures consistency, maintainability, and proper isolation between components.

## Table of Contents

1. [Shadow DOM Architecture](#shadow-dom-architecture)
2. [Component Structure](#component-structure)
3. [Service Implementation Patterns](#service-implementation-patterns)
4. [Network Communication Patterns](#network-communication-patterns)
5. [UI Component Patterns](#ui-component-patterns)
6. [Event Handling Best Practices](#event-handling-best-practices)
7. [Cleanup and Lifecycle Management](#cleanup-and-lifecycle-management)
8. [Example Implementation](#example-implementation)

## Shadow DOM Architecture

All Hephaestus UI components use Shadow DOM for proper isolation, which provides several benefits:

- **Style Isolation**: CSS rules only apply within the component's shadow boundary
- **DOM Isolation**: Document queries are scoped to the component
- **Clean Component APIs**: Standardized interfaces between components
- **Theme Propagation**: Theme variables traverse shadow boundaries for consistency
- **Event Bubbling Control**: Events can be contained or allowed to cross boundaries

The Shadow DOM architecture consists of the following layers:

1. **Host Element**: The container that holds the shadow root
2. **Shadow Root**: The boundary for isolation
3. **Component Container**: The root element within the shadow DOM
4. **Component Structure**: The actual HTML structure of the component

## Component Structure

Every component should follow this file structure:

```
ui/
├── components/
│   └── [component-name]/
│       └── [component-name]-component.html
├── styles/
│   └── [component-name]/
│       └── [component-name]-component.css
└── scripts/
    └── [component-name]/
        ├── [component-name]-service.js (optional)
        └── [component-name]-component.js
```

### HTML Structure

Component HTML files should:

1. Use the BEM naming convention with component-specific prefixes
2. Maintain semantic hierarchy with appropriate heading levels
3. Group related elements into sections
4. Use consistent class naming for similar elements

Example:
```html
<div class="settings-container">
  <div class="settings-header">
    <h2 class="settings-header__title">Settings</h2>
    <div class="settings-header__controls">
      <button class="settings-button settings-button--primary">Save</button>
    </div>
  </div>
  
  <div class="settings-section">
    <h3 class="settings-section__title">Section Title</h3>
    <!-- Section content -->
  </div>
</div>
```

### CSS Structure

Component CSS files should:

1. Follow the BEM naming convention
2. Use component-specific class prefixes
3. Utilize CSS variables for theming
4. Include fallback values for variables
5. Organize styles by component section

Example:
```css
/* Settings Component Styles */

.settings-container {
  padding: var(--spacing-md, 16px);
  background-color: var(--bg-primary, #1e1e1e);
}

.settings-header {
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-md, 16px);
}

.settings-header__title {
  color: var(--text-primary, #f0f0f0);
  margin: 0;
}

.settings-button {
  padding: var(--spacing-sm, 8px) var(--spacing-md, 16px);
  border-radius: var(--border-radius-sm, 4px);
}

.settings-button--primary {
  background-color: var(--color-primary, #007bff);
  color: white;
}
```

## Service Implementation Patterns

Components with complex data management should implement a service class that:

1. Extends the base `BaseService` class
2. Registers itself globally for other components to use
3. Provides a clean API for accessing component data
4. Implements proper connection and disconnection methods
5. Includes fallback mechanisms when the real API is unavailable

Example:
```javascript
class SettingsService extends window.tektonUI.componentUtils.BaseService {
    constructor() {
        super('settingsService', '/api/settings');
        this.settings = {
            // Default settings
        };
    }
    
    async connect() {
        if (this.connected) return true;
        
        try {
            // Connect to the API
            const response = await fetch(`${this.apiUrl}/ping`);
            if (!response.ok) {
                throw new Error(`Failed to connect: ${response.status}`);
            }
            
            this.connected = true;
            this.dispatchEvent('connected', {});
            return true;
        } catch (error) {
            console.error('Connection failed:', error);
            this.connected = false;
            this.dispatchEvent('connectionFailed', { error });
            throw error;
        }
    }
    
    // Additional methods for service functionality
}
```

Services should provide:

- Connection management
- Data fetching methods
- Event dispatching for state changes
- Error handling
- Fallback mechanisms

## Network Communication Patterns

### Single Port Architecture

All Tekton components **must** use a single port for all operations. This includes REST API endpoints, WebSocket connections, and event-based communication. This architecture simplifies deployment and improves consistency across components.

### Service Configuration

When initializing a component service, use a single base URL for all communication types:

```javascript
class ComponentService extends window.tektonUI.componentUtils.BaseService {
    constructor() {
        const componentPort = 8XXX; // Replace with actual component port
        const componentHost = window.tektonUI.config.get('componentHost', 'localhost');
        const baseUrl = `http://${componentHost}:${componentPort}`;
        
        super('componentService', baseUrl);
        
        // Configure different endpoint paths on the same port
        this.apiUrl = `${baseUrl}/api/v1`;
        this.wsUrl = `${baseUrl.replace('http', 'ws')}/ws`;
        this.eventUrl = `${baseUrl}/events`;
    }
    
    // Service methods...
}
```

### Multiple Communication Channels

To support different communication protocols through a single port:

#### REST API Communication

```javascript
async fetchData(endpoint) {
    try {
        const response = await fetch(`${this.apiUrl}/${endpoint}`);
        if (!response.ok) throw new Error(`HTTP error ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        this.dispatchEvent('error', { message: error.message, type: 'api' });
        throw error;
    }
}
```

#### WebSocket Communication

```javascript
connectWebSocket() {
    if (this.wsConnection) return;
    
    this.wsConnection = new WebSocket(this.wsUrl);
    
    this.wsConnection.onopen = () => {
        console.log('WebSocket connected');
        this.dispatchEvent('websocketConnected', {});
    };
    
    this.wsConnection.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleWsMessage(data);
    };
    
    this.wsConnection.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.dispatchEvent('error', { message: 'WebSocket error', type: 'websocket' });
    };
    
    this.wsConnection.onclose = () => {
        console.log('WebSocket closed');
        this.wsConnection = null;
        this.dispatchEvent('websocketDisconnected', {});
    };
}
```

#### Event-Based Communication

```javascript
async sendEvent(eventType, eventData) {
    try {
        const response = await fetch(this.eventUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: eventType,
                data: eventData,
                source: this.serviceName,
                timestamp: new Date().toISOString()
            })
        });
        
        if (!response.ok) throw new Error(`HTTP error ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Event sending failed:', error);
        this.dispatchEvent('error', { message: error.message, type: 'event' });
        throw error;
    }
}
```

### Connection Management

Ensure that all communication channels are properly established and torn down:

```javascript
async connect() {
    if (this.connected) return true;
    
    try {
        // Check REST API availability
        const response = await fetch(`${this.apiUrl}/health`);
        if (!response.ok) throw new Error(`HTTP error ${response.status}`);
        
        // Connect WebSocket if needed
        if (this.requiresWebSocket) {
            this.connectWebSocket();
        }
        
        this.connected = true;
        this.dispatchEvent('connected', {});
        return true;
    } catch (error) {
        console.error('Connection failed:', error);
        this.connected = false;
        this.dispatchEvent('connectionFailed', { error });
        throw error;
    }
}

disconnect() {
    if (!this.connected) return;
    
    // Close WebSocket connection if open
    if (this.wsConnection) {
        this.wsConnection.close();
        this.wsConnection = null;
    }
    
    this.connected = false;
    this.dispatchEvent('disconnected', {});
}
```

## UI Component Patterns

### Notifications

Use the shared notification system for temporary messages:

```javascript
// Show a notification within the component
component.utils.notifications.show(
    component,         // Component context
    'Success',         // Title
    'Settings saved',  // Message
    'success',         // Type: 'success', 'error', 'warning', 'info'
    3000               // Duration in ms (0 for no auto-hide)
);
```

### Loading Indicators

Use the shared loading indicator for asynchronous operations:

```javascript
// Show loading indicator
const loader = component.utils.loading.show(component, 'Loading settings...');

// Perform async operation
await fetchData();

// Hide loading indicator
component.utils.loading.hide(component);
```

### Dialogs

Create standardized confirmation dialogs:

```javascript
function showConfirmationDialog(title, message, onConfirm, onCancel) {
    // Create dialog element
    const dialog = document.createElement('div');
    dialog.className = 'component-dialog';
    
    // Add content and buttons
    
    // Attach to shadow root
    component.root.appendChild(dialog);
    
    // Add event handlers for buttons
}
```

### Component Initialization Pattern

All components should follow this initialization pattern:

```javascript
(function(component) {
    'use strict';
    
    // Component-specific utilities
    const dom = component.utils.dom;
    const notifications = component.utils.notifications;
    const loading = component.utils.loading;
    const lifecycle = component.utils.lifecycle;
    
    // Service reference
    let componentService = null;
    
    /**
     * Initialize the component
     */
    function initComponent() {
        // Initialize or get required services
        initServices();
        
        // Set up event listeners
        setupEventListeners();
        
        // Update UI to reflect current state
        updateUI();
        
        // Register cleanup function
        component.registerCleanup(cleanupComponent);
    }
    
    // Additional component functions
    
    // Initialize the component
    initComponent();
    
})(component);
```

## Event Handling Best Practices

### Event Delegation

Use event delegation to handle events efficiently:

```javascript
// Using component's built-in event delegation
component.on('click', '.settings-button', function(event) {
    // 'this' refers to the matched element
    console.log('Button clicked:', this.textContent);
});
```

### Lifecycle-Managed Event Handlers

For direct event listeners, use lifecycle management:

```javascript
// Register event with automatic cleanup
component.utils.lifecycle.registerEventHandler(
    component,                 // Component context
    element,                   // Element to attach listener to
    'click',                   // Event type
    function(event) {          // Event handler
        console.log('Clicked');
    }
);
```

### Custom Events

Use custom events for component communication:

```javascript
// Dispatch a custom event
component.dispatch('settingsChanged', {
    theme: 'dark',
    showGreekNames: true
});

// Listen for custom events from other components
document.addEventListener('settingsChanged', (event) => {
    if (event.detail.componentId !== component.id) {
        // Handle event from another component
        console.log('Settings changed in another component:', event.detail);
    }
});
```

## Cleanup and Lifecycle Management

### Component Cleanup

Always register cleanup functions to prevent memory leaks:

```javascript
// Register the main cleanup function
component.registerCleanup(function() {
    // Clean up resources
    disconnectFromServices();
    releaseReferences();
});
```

### Multiple Cleanup Tasks

For more complex components, register multiple cleanup tasks:

```javascript
// Register multiple cleanup tasks
component.utils.lifecycle.registerCleanupTasks(component, [
    () => disconnectFromService(),
    () => cancelPendingRequests(),
    () => releaseResourceReferences()
]);
```

### Service Disconnection

Always disconnect from services during cleanup:

```javascript
function disconnectFromServices() {
    if (componentService && componentService.connected) {
        componentService.disconnect();
    }
}
```

## Example Implementation

Below is a minimal example of a complete component implementation:

### HTML (component-component.html):
```html
<div class="component-container">
  <div class="component-header">
    <h2 class="component-header__title">Component Title</h2>
    <div class="component-header__controls">
      <button class="component-button component-button--primary" id="save-button">Save</button>
    </div>
  </div>
  
  <div class="component-content">
    <!-- Component content here -->
  </div>
</div>
```

### CSS (component-component.css):
```css
/* Component Styles */

.component-container {
  padding: var(--spacing-md);
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.component-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.component-button {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  cursor: pointer;
}

.component-button--primary {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}
```

### JavaScript (component-component.js):
```javascript
/**
 * Example Component
 */

(function(component) {
    'use strict';
    
    // Component-specific utilities
    const dom = component.utils.dom;
    const notifications = component.utils.notifications;
    const loading = component.utils.loading;
    const lifecycle = component.utils.lifecycle;
    
    // State and service references
    let data = null;
    let componentService = null;
    
    /**
     * Initialize the component
     */
    function initComponent() {
        console.log('Initializing component...');
        
        // Initialize or get required services
        initServices();
        
        // Set up event listeners
        setupEventListeners();
        
        // Load initial data
        loadData();
        
        // Register cleanup function
        component.registerCleanup(cleanupComponent);
        
        console.log('Component initialized');
    }
    
    /**
     * Initialize required services
     */
    function initServices() {
        // Get or create the service
        if (window.tektonUI?.services?.exampleService) {
            componentService = window.tektonUI.services.exampleService;
        } else {
            // Create a new service instance
            componentService = new ExampleService();
        }
    }
    
    /**
     * Set up event listeners
     */
    function setupEventListeners() {
        // Save button
        component.on('click', '#save-button', function() {
            saveData();
        });
        
        // Other event listeners...
    }
    
    /**
     * Load initial data
     */
    async function loadData() {
        loading.show(component, 'Loading data...');
        
        try {
            await componentService.connect();
            data = await componentService.getData();
            updateUI();
            loading.hide(component);
        } catch (error) {
            loading.hide(component);
            notifications.show(component, 'Error', 'Failed to load data', 'error');
        }
    }
    
    /**
     * Save data changes
     */
    async function saveData() {
        loading.show(component, 'Saving data...');
        
        try {
            await componentService.saveData(data);
            loading.hide(component);
            notifications.show(component, 'Success', 'Data saved successfully', 'success');
        } catch (error) {
            loading.hide(component);
            notifications.show(component, 'Error', 'Failed to save data', 'error');
        }
    }
    
    /**
     * Update UI with current data
     */
    function updateUI() {
        if (!data) return;
        
        // Update UI elements with data values
    }
    
    /**
     * Clean up component resources
     */
    function cleanupComponent() {
        console.log('Cleaning up component');
        
        // Disconnect from services
        if (componentService && componentService.connected) {
            componentService.disconnect();
        }
        
        // Release references
        data = null;
        componentService = null;
    }
    
    // Initialize the component
    initComponent();
    
})(component);
```

By following these patterns, components will have consistent structure, proper isolation, and efficient resource management, making the Hephaestus UI more maintainable and robust.