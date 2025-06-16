# Hephaestus Integration Guide

## Overview

This guide provides detailed instructions for integrating Hephaestus, the UI component system for Tekton, with other components and applications. Hephaestus uses a component-based architecture with Shadow DOM for isolation, providing a flexible and robust UI framework.

## Integration Methods

Hephaestus provides multiple integration points:

1. **Web Components**: Custom elements that can be used in any web application
2. **Component Registry**: Central registry for component discovery and loading
3. **State Management**: Shared and isolated state management systems
4. **Event System**: Inter-component communication mechanism
5. **CSS Framework**: Consistent styling system with isolation

## Web Component Integration

### Basic Component Usage

Hephaestus components can be used in any HTML page:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Hephaestus Integration</title>
  <!-- Load Hephaestus core -->
  <script src="https://tekton-server/ui/scripts/component-loader.js"></script>
</head>
<body>
  <!-- Use Hephaestus components -->
  <tekton-terminal></tekton-terminal>
  <tekton-profile></tekton-profile>
  
  <script>
    // Initialize components after they're loaded
    document.addEventListener('hephaestus:ready', () => {
      console.log('Hephaestus components are ready');
    });
  </script>
</body>
</html>
```

### Component Registration

Register a custom component with Hephaestus:

```javascript
// myapp-component.js
class MyAppComponent extends HTMLElement {
  constructor() {
    super();
    // Create shadow DOM
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          padding: 16px;
          border: 1px solid #ccc;
        }
        h2 {
          color: #333;
        }
      </style>
      <div class="myapp-component">
        <h2>My App Component</h2>
        <slot></slot>
      </div>
    `;
  }
  
  connectedCallback() {
    console.log('MyAppComponent connected');
  }
  
  disconnectedCallback() {
    console.log('MyAppComponent disconnected');
  }
}

// Register with Hephaestus
window.Hephaestus.registerComponent('myapp-component', MyAppComponent);
```

Register with the component registry server:

```javascript
// Register component metadata with server
fetch('/ui/server/component_registry', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'myapp-component',
    version: '1.0.0',
    description: 'Custom component for MyApp',
    dependencies: [],
    assets: {
      js: ['myapp-component.js'],
      css: ['myapp-component.css']
    }
  })
});
```

## State Management Integration

### Using the State Manager

Integrate with Hephaestus state management:

```javascript
// Import state manager
import { StateManager } from '/ui/scripts/state-manager.js';

// Initialize state
const initialState = {
  user: {
    name: 'Guest',
    preferences: {
      theme: 'light'
    }
  },
  app: {
    currentView: 'home'
  }
};

// Create state manager instance
const stateManager = new StateManager(initialState);

// Subscribe to state changes
const unsubscribe = stateManager.subscribe(['user.preferences'], (newState, oldState) => {
  console.log('User preferences changed:', newState.user.preferences);
});

// Update state
stateManager.setState('user.preferences.theme', 'dark');

// Later, unsubscribe when no longer needed
unsubscribe();
```

### Component-specific State

Use isolated component state:

```javascript
import { ComponentState } from '/ui/scripts/component-utils-state.js';

class MyComponent extends HTMLElement {
  constructor() {
    super();
    
    // Initialize component state
    this.state = new ComponentState(this, {
      count: 0,
      items: [],
      isLoading: false
    });
    
    // Subscribe to state changes
    this.state.subscribe(['count'], this.onCountChange.bind(this));
  }
  
  onCountChange(newState, oldState) {
    console.log(`Count changed from ${oldState.count} to ${newState.count}`);
    this.updateUI();
  }
  
  incrementCount() {
    this.state.setState('count', this.state.getState('count') + 1);
  }
  
  updateUI() {
    // Update UI based on state
  }
}
```

### Shared State Between Components

Share state between components:

```javascript
import { SharedState } from '/ui/scripts/component-utils-state.js';

// Create a shared state instance
const sharedAppState = new SharedState('app-state', {
  documents: [],
  selectedDocument: null,
  isEditing: false
});

// In component A
class DocumentListComponent extends HTMLElement {
  constructor() {
    super();
    
    // Connect to shared state
    this.state = sharedAppState;
    
    // Subscribe to changes
    this.state.subscribe(['documents'], this.onDocumentsChange.bind(this));
  }
  
  onDocumentsChange(newState) {
    // Update document list UI
    this.renderDocuments(newState.documents);
  }
  
  addDocument(doc) {
    const docs = [...this.state.getState('documents'), doc];
    this.state.setState('documents', docs);
  }
}

// In component B
class DocumentEditorComponent extends HTMLElement {
  constructor() {
    super();
    
    // Connect to same shared state
    this.state = sharedAppState;
    
    // Subscribe to selected document changes
    this.state.subscribe(['selectedDocument'], this.onDocumentSelected.bind(this));
  }
  
  onDocumentSelected(newState) {
    if (newState.selectedDocument) {
      this.loadDocument(newState.selectedDocument);
    }
  }
  
  saveDocument(changes) {
    const docs = this.state.getState('documents');
    const docIndex = docs.findIndex(d => d.id === this.state.getState('selectedDocument').id);
    
    if (docIndex >= 0) {
      const updatedDocs = [...docs];
      updatedDocs[docIndex] = {...updatedDocs[docIndex], ...changes};
      this.state.setState('documents', updatedDocs);
    }
  }
}
```

## Event System Integration

### Component Event Communication

Use the event system for inter-component communication:

```javascript
import { EventBus } from '/ui/scripts/component-utils.js';

// In component A
class NotificationSender extends HTMLElement {
  constructor() {
    super();
    this.eventBus = new EventBus();
  }
  
  sendNotification(message) {
    // Dispatch event to all subscribers
    this.eventBus.dispatch('notification', {
      message,
      timestamp: new Date().toISOString()
    });
  }
}

// In component B
class NotificationReceiver extends HTMLElement {
  constructor() {
    super();
    this.eventBus = new EventBus();
    
    // Subscribe to notification events
    this.unsubscribe = this.eventBus.subscribe('notification', this.handleNotification.bind(this));
  }
  
  handleNotification(data) {
    console.log(`Received notification: ${data.message} at ${data.timestamp}`);
    // Show notification in UI
  }
  
  disconnectedCallback() {
    // Clean up subscription
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  }
}
```

### Direct Component Communication

Communicate directly between components:

```javascript
// Get reference to another component
const terminal = document.querySelector('tekton-terminal');

// Call public methods
if (terminal) {
  terminal.executeCommand('help');
}

// Listen for custom events
terminal.addEventListener('command-executed', (event) => {
  console.log('Command executed:', event.detail);
});
```

## CSS Integration

### Using the Styling System

Integrate with Hephaestus CSS framework:

```html
<!-- Import Hephaestus styles -->
<link rel="stylesheet" href="/ui/styles/main.css">

<!-- Component-specific styles using BEM naming convention -->
<style>
  .myapp-component {
    /* Base component styling */
  }
  
  .myapp-component__header {
    /* Element styling */
  }
  
  .myapp-component--highlighted {
    /* Modifier styling */
  }
</style>
```

### Shadow DOM Styling

Style components within Shadow DOM:

```javascript
class StyledComponent extends HTMLElement {
  constructor() {
    super();
    
    // Create shadow DOM
    this.attachShadow({ mode: 'open' });
    
    // Apply styles within shadow DOM
    this.shadowRoot.innerHTML = `
      <style>
        /* Component-specific styles */
        :host {
          display: block;
          margin: 16px;
        }
        
        /* Apply theme variables from parent */
        .container {
          background-color: var(--background-color, #fff);
          color: var(--text-color, #333);
        }
        
        /* Slot styling */
        ::slotted(h2) {
          color: #0066cc;
        }
      </style>
      
      <div class="container">
        <slot></slot>
      </div>
    `;
  }
}
```

### CSS Variable Integration

Use CSS variables for theming:

```css
/* Define variables at root level */
:root {
  --primary-color: #0066cc;
  --secondary-color: #009933;
  --background-color: #ffffff;
  --text-color: #333333;
  --accent-color: #ff6600;
  
  /* Spacing */
  --spacing-small: 8px;
  --spacing-medium: 16px;
  --spacing-large: 24px;
  
  /* Typography */
  --font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  --font-size-small: 12px;
  --font-size-medium: 14px;
  --font-size-large: 18px;
}

/* Dark theme */
.theme-dark {
  --background-color: #222222;
  --text-color: #f0f0f0;
}
```

In your component:

```javascript
class ThemedComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        .themed-content {
          background-color: var(--background-color);
          color: var(--text-color);
          padding: var(--spacing-medium);
          font-family: var(--font-family);
          font-size: var(--font-size-medium);
        }
        
        .themed-button {
          background-color: var(--primary-color);
          color: white;
          border: none;
          padding: var(--spacing-small) var(--spacing-medium);
          border-radius: 4px;
        }
      </style>
      
      <div class="themed-content">
        <h2>Themed Component</h2>
        <button class="themed-button">Click Me</button>
      </div>
    `;
  }
}
```

## Server-Side Integration

### Component Registry API

Register components programmatically:

```python
import requests
import json

def register_component(component_data):
    response = requests.post(
        "http://localhost:8080/ui/server/component_registry",
        headers={"Content-Type": "application/json"},
        data=json.dumps(component_data)
    )
    
    if response.status_code == 200:
        print(f"Component {component_data['name']} registered successfully")
        return response.json()
    else:
        print(f"Failed to register component: {response.text}")
        return None

# Register a component
component = {
    "name": "data-visualization",
    "version": "1.0.0",
    "description": "Data visualization component",
    "author": "Data Team",
    "dependencies": ["chart-library"],
    "assets": {
        "js": ["data-viz.js"],
        "css": ["data-viz.css"]
    },
    "settings": {
        "defaultChartType": "bar"
    }
}

register_component(component)
```

Query available components:

```python
import requests

def get_components():
    response = requests.get("http://localhost:8080/ui/server/component_registry")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get components: {response.text}")
        return []

components = get_components()
for component in components:
    print(f"{component['name']} v{component['version']}")
```

## Integration with Other Tekton Components

### Terma Terminal Integration

Integrate the Terma terminal component:

```javascript
// Import Terma Terminal
import { TermaTerminal } from '/ui/terma/terma-terminal.js';

class MyApplication extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    
    // Set up terminal container
    this.shadowRoot.innerHTML = `
      <div class="terminal-container"></div>
    `;
    
    // Create and configure terminal
    this.terminal = new TermaTerminal();
    this.shadowRoot.querySelector('.terminal-container').appendChild(this.terminal);
    
    // Configure terminal
    this.terminal.setPrompt('myapp> ');
    this.terminal.registerCommand('hello', (args) => {
      return `Hello, ${args[0] || 'world'}!`;
    });
    
    // Listen for command events
    this.terminal.addEventListener('command', (event) => {
      console.log(`Command executed: ${event.detail.command}`);
    });
  }
}

customElements.define('my-application', MyApplication);
```

### Ergon Integration

Integrate with Ergon for state management:

```javascript
import { ErgonStateManager } from '/ui/scripts/ergon-state-manager.js';

class MyErgonComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    
    // Set up component UI
    this.shadowRoot.innerHTML = `
      <div class="ergon-client">
        <h2>Ergon Client</h2>
        <div class="task-list"></div>
        <button class="add-task">Add Task</button>
      </div>
    `;
    
    // Initialize Ergon state manager
    this.ergonState = new ErgonStateManager('my-component');
    
    // Subscribe to task updates
    this.ergonState.subscribe('tasks', this.renderTasks.bind(this));
    
    // Set up event listeners
    this.shadowRoot.querySelector('.add-task').addEventListener('click', () => {
      this.addTask('New Task ' + Date.now());
    });
    
    // Initialize tasks
    this.ergonState.initState('tasks', []);
  }
  
  addTask(name) {
    const tasks = [...this.ergonState.getState('tasks')];
    tasks.push({
      id: Date.now(),
      name,
      completed: false
    });
    
    this.ergonState.setState('tasks', tasks);
  }
  
  renderTasks(tasks) {
    const container = this.shadowRoot.querySelector('.task-list');
    container.innerHTML = '';
    
    tasks.forEach(task => {
      const taskEl = document.createElement('div');
      taskEl.className = 'task';
      taskEl.innerHTML = `
        <input type="checkbox" ${task.completed ? 'checked' : ''}>
        <span>${task.name}</span>
      `;
      
      // Add event listener for checkbox
      const checkbox = taskEl.querySelector('input');
      checkbox.addEventListener('change', () => {
        this.toggleTaskComplete(task.id);
      });
      
      container.appendChild(taskEl);
    });
  }
  
  toggleTaskComplete(taskId) {
    const tasks = this.ergonState.getState('tasks');
    const updatedTasks = tasks.map(task => {
      if (task.id === taskId) {
        return {...task, completed: !task.completed};
      }
      return task;
    });
    
    this.ergonState.setState('tasks', updatedTasks);
  }
}

customElements.define('my-ergon-component', MyErgonComponent);
```

### Hermes Integration

Use Hermes for component communication:

```javascript
import { HermesConnector } from '/ui/scripts/hermes-connector.js';

class HermesComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    
    // Basic UI
    this.shadowRoot.innerHTML = `
      <div class="hermes-component">
        <h2>Hermes Component</h2>
        <div class="message-log"></div>
        <input type="text" class="message-input">
        <button class="send-button">Send</button>
      </div>
    `;
    
    // Initialize Hermes connector
    this.hermes = new HermesConnector({
      componentId: 'hermes-component',
      url: 'ws://localhost:8002/ws'
    });
    
    // Set up event listeners
    this.shadowRoot.querySelector('.send-button').addEventListener('click', () => {
      this.sendMessage();
    });
    
    // Subscribe to messages
    this.hermes.subscribe('notifications', this.handleNotification.bind(this));
  }
  
  connectedCallback() {
    // Connect to Hermes when component is added to DOM
    this.hermes.connect();
  }
  
  disconnectedCallback() {
    // Disconnect from Hermes when component is removed
    this.hermes.disconnect();
  }
  
  sendMessage() {
    const input = this.shadowRoot.querySelector('.message-input');
    const message = input.value.trim();
    
    if (message) {
      this.hermes.publish('messages', {
        text: message,
        sender: 'hermes-component',
        timestamp: new Date().toISOString()
      });
      
      input.value = '';
    }
  }
  
  handleNotification(notification) {
    const log = this.shadowRoot.querySelector('.message-log');
    const entry = document.createElement('div');
    
    entry.className = 'log-entry';
    entry.innerHTML = `
      <span class="timestamp">${new Date(notification.timestamp).toLocaleTimeString()}</span>
      <span class="message">${notification.text}</span>
    `;
    
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
  }
}

customElements.define('hermes-component', HermesComponent);
```

## Single Port Architecture Integration

Hephaestus follows the Tekton Single Port Architecture pattern for consistent component communication.

### URL Path Structure

```
http://localhost:8080/         # Main UI
  ├── api/                     # HTTP API endpoints
  ├── ws/                      # WebSocket endpoint
  ├── components/              # Component definitions
  │   ├── register            # Component registration endpoint
  │   └── :component          # Component metadata endpoints
  ├── assets/                  # Static assets
  │   ├── js/                 # JavaScript files
  │   ├── css/                # CSS files
  │   └── images/             # Image files
  └── events/                  # Server-sent events endpoint
```

### Environment Configuration

Configure component URLs:

```javascript
// Load environment configuration
import { env } from '/ui/scripts/env.js';

// Use URLs with consistent path structure
const componentsUrl = `${env.HEPHAESTUS_URL}/components`;
const apiUrl = `${env.HEPHAESTUS_URL}/api`;
const wsUrl = `${env.HEPHAESTUS_URL}/ws`;

// Example usage
async function loadComponent(componentName) {
  const response = await fetch(`${componentsUrl}/${componentName}`);
  return response.json();
}

// WebSocket connection
const socket = new WebSocket(wsUrl);
```

## Testing Your Integration

### Component Testing

Test your component integration:

```javascript
// component-test.js
describe('MyAppComponent', () => {
  let component;
  
  beforeEach(() => {
    // Create component instance
    component = document.createElement('myapp-component');
    document.body.appendChild(component);
  });
  
  afterEach(() => {
    // Clean up
    if (component && component.parentNode) {
      component.parentNode.removeChild(component);
    }
  });
  
  it('should render correctly', () => {
    // Get shadow root content
    const shadowRoot = component.shadowRoot;
    const header = shadowRoot.querySelector('h2');
    
    expect(header.textContent).toBe('My App Component');
  });
  
  it('should respond to state changes', () => {
    // Trigger state change
    component.setState('count', 5);
    
    // Verify rendering updated
    const countElement = component.shadowRoot.querySelector('.count');
    expect(countElement.textContent).toBe('5');
  });
});
```

### Integration Testing

Test integration with Hephaestus:

```javascript
// integration-test.js
describe('Hephaestus Integration', () => {
  beforeAll(async () => {
    // Load Hephaestus core
    await loadScript('/ui/scripts/component-loader.js');
    
    // Wait for Hephaestus to initialize
    await new Promise(resolve => {
      if (window.Hephaestus && window.Hephaestus.isReady) {
        resolve();
      } else {
        window.addEventListener('hephaestus:ready', resolve, { once: true });
      }
    });
  });
  
  it('should register custom components', async () => {
    // Register test component
    class TestComponent extends HTMLElement {
      constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.innerHTML = '<div>Test Component</div>';
      }
    }
    
    // Register with Hephaestus
    window.Hephaestus.registerComponent('test-component', TestComponent);
    
    // Create instance
    const element = document.createElement('test-component');
    document.body.appendChild(element);
    
    // Verify registration worked
    expect(element.shadowRoot).toBeTruthy();
    expect(element.shadowRoot.querySelector('div').textContent).toBe('Test Component');
    
    // Cleanup
    document.body.removeChild(element);
  });
  
  it('should share state between components', async () => {
    // Create two components using shared state
    const componentA = document.createElement('state-producer');
    const componentB = document.createElement('state-consumer');
    
    document.body.appendChild(componentA);
    document.body.appendChild(componentB);
    
    // Update state in component A
    componentA.updateValue('test value');
    
    // Verify component B received the update
    await new Promise(resolve => setTimeout(resolve, 0)); // Wait for async update
    expect(componentB.getValue()).toBe('test value');
    
    // Cleanup
    document.body.removeChild(componentA);
    document.body.removeChild(componentB);
  });
});
```

## Troubleshooting

### Common Integration Issues

1. **Component Registration Failures**
   - Check that component names follow the custom element naming rules (must include a dash)
   - Verify all required metadata is provided during registration
   - Ensure there are no duplicate component registrations

2. **Shadow DOM Styling Issues**
   - Remember that external styles don't penetrate the shadow DOM
   - Use CSS custom properties (variables) for theming
   - Check for proper encapsulation of styles

3. **State Management Problems**
   - Verify subscriptions are properly set up
   - Use immutable patterns when updating state (create new objects/arrays)
   - Check for circular dependencies in state updates

4. **Event Communication Issues**
   - Ensure event names are consistent
   - Verify event handlers are properly bound
   - Check that event payload structures match expectations

### Debugging Tips

1. **Component Inspection**
   ```javascript
   // Inspect shadow DOM
   const component = document.querySelector('my-component');
   console.log(component.shadowRoot);
   
   // Access component internals
   console.dir(component);
   ```

2. **State Debugging**
   ```javascript
   // Import state debugging tools
   import { StateDebug } from '/ui/scripts/state-debug.js';
   
   // Enable state logging
   StateDebug.enableLogging();
   
   // Log specific state changes
   StateDebug.watchPath('user.preferences');
   ```

3. **Event Logging**
   ```javascript
   // Log all events on the event bus
   EventBus.enableDebug();
   
   // Monitor specific event
   EventBus.debugEvent('notification');
   ```

## Best Practices

1. **Component Design**
   - Keep components focused on a single responsibility
   - Use composition over inheritance
   - Design components to be reusable and configurable
   - Document component APIs and events

2. **State Management**
   - Use the appropriate state scope (global, shared, or component)
   - Minimize state changes to improve performance
   - Implement validation for state updates
   - Keep state structures simple and flat when possible

3. **Shadow DOM Usage**
   - Properly encapsulate component internals
   - Use slots for flexible content projection
   - Apply CSS variables for themeable components
   - Minimize DOM operations for better performance

4. **Event Handling**
   - Use custom events for component communication
   - Keep event payloads small and focused
   - Implement proper event cleanup in disconnectedCallback
   - Use event delegation for dynamic content

5. **Performance Optimization**
   - Lazy-load components when possible
   - Optimize render cycles
   - Use efficient DOM operations
   - Implement debouncing for frequent state updates

## Conclusion

This guide covers the basics of integrating with Hephaestus. For more detailed information on specific APIs and components, refer to the [API Reference](./API_REFERENCE.md) and [Technical Documentation](./TECHNICAL_DOCUMENTATION.md).

If you encounter issues or need assistance with integration, please refer to the [Tekton Documentation](../../README.md) for community support options.