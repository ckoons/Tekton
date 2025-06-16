# Hephaestus Technical Documentation

This document provides detailed technical information about the Hephaestus component's architecture, internal systems, and implementation details.

## Architecture Overview

Hephaestus implements a modular, component-based architecture designed for flexibility, extensibility, and robustness. The component follows the Single Port Architecture pattern and is structured into several key layers:

1. **Core UI Framework**: Provides the foundation for the user interface
2. **Component System**: Manages the loading, initialization, and lifecycle of UI components
3. **Communication Layer**: Handles interaction with backend services
4. **State Management**: Manages UI state and persistence
5. **Shadow DOM Integration**: Provides component isolation

## Core UI Framework

The core UI framework provides the foundation for the Hephaestus user interface.

### Architecture Principles

The framework is built on several key principles:

- **Vanilla First**: Uses native browser capabilities without heavy frameworks
- **Progressive Enhancement**: Works with basic browsers but enhances with modern features
- **Component Isolation**: Each component operates independently
- **Event-Driven**: Communication through standardized events
- **Responsive Design**: Adapts to different screen sizes and devices

### Key Components

The framework consists of these key components:

- **UI Manager**: Central controller for the user interface
- **Component Registry**: Manages available components
- **Event Bus**: Facilitates communication between components
- **State Manager**: Manages and persists UI state
- **Template Engine**: Handles HTML template loading and rendering
- **Theme Manager**: Controls theme application and switching

### UI Manager

The UI Manager orchestrates the entire user interface:

```javascript
class UIManager {
  constructor() {
    this.activeComponent = null;
    this.components = {};
    this.events = new EventBus();
    this.state = new StateManager();
    this.templates = new TemplateEngine();
    this.themes = new ThemeManager();
  }

  initialize() {
    // Load components from registry
    this.loadComponents();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Load initial component
    this.loadInitialComponent();
    
    // Apply theme
    this.themes.applyTheme(this.state.get('global', 'theme') || 'light');
  }

  loadComponents() {
    // Load components from the registry
    ComponentRegistry.getComponents().forEach(component => {
      this.registerComponent(component);
    });
  }

  registerComponent(component) {
    // Register component
    this.components[component.id] = component;
  }

  activateComponent(componentId) {
    // Deactivate current component
    if (this.activeComponent) {
      this.components[this.activeComponent].deactivate();
    }
    
    // Activate new component
    this.activeComponent = componentId;
    this.components[componentId].activate();
    
    // Update state
    this.state.set('global', 'activeComponent', componentId);
    
    // Emit event
    this.events.emit('componentActivated', { componentId });
  }

  // Additional methods...
}
```

### Component Registry

The Component Registry manages component registration and discovery:

```javascript
class ComponentRegistry {
  static components = {};
  
  static registerComponent(component) {
    // Validate component
    if (!component.id || !component.name || !component.path) {
      console.error('Invalid component', component);
      return false;
    }
    
    // Register component
    this.components[component.id] = component;
    return true;
  }
  
  static getComponent(id) {
    return this.components[id] || null;
  }
  
  static getComponents() {
    return Object.values(this.components);
  }
  
  static async loadComponentsFromServer() {
    try {
      const response = await fetch('/api/components');
      const data = await response.json();
      
      data.components.forEach(component => {
        this.registerComponent(component);
      });
      
      return true;
    } catch (error) {
      console.error('Failed to load components', error);
      return false;
    }
  }
}
```

### Event Bus

The Event Bus provides an event-driven communication system:

```javascript
class EventBus {
  constructor() {
    this.listeners = {};
  }
  
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    
    this.listeners[event].push(callback);
    return () => this.off(event, callback);
  }
  
  off(event, callback) {
    if (!this.listeners[event]) return;
    
    const index = this.listeners[event].indexOf(callback);
    if (index !== -1) {
      this.listeners[event].splice(index, 1);
    }
  }
  
  emit(event, data) {
    if (!this.listeners[event]) return;
    
    this.listeners[event].forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in event listener for ${event}`, error);
      }
    });
  }
  
  once(event, callback) {
    const onceCallback = (data) => {
      this.off(event, onceCallback);
      callback(data);
    };
    
    return this.on(event, onceCallback);
  }
}
```

## Component System

The Component System manages UI components throughout their lifecycle.

### Component Definition

Each component is defined with a standard structure:

```javascript
const ExampleComponent = {
  id: 'example',
  name: 'Example Component',
  description: 'An example component',
  
  // Component lifecycle
  initialize(container, options) {
    this.container = container;
    this.options = options;
    this.state = StateManager.getNamespace(this.id);
    this.events = new EventEmitter();
    
    // Create shadow DOM
    this.shadow = this.container.attachShadow({ mode: 'open' });
    
    // Initialize component
    this.render();
    this.setupEventListeners();
  },
  
  render() {
    // Load template
    TemplateEngine.loadTemplate('example-component')
      .then(template => {
        // Render template with state
        this.shadow.innerHTML = TemplateEngine.render(template, this.state);
        
        // Post-render setup
        this.setupDomReferences();
        this.setupComponentUI();
      });
  },
  
  setupEventListeners() {
    // Set up DOM event listeners
    this.events.on('click', '.example-button', this.handleButtonClick.bind(this));
    
    // Listen for state changes
    StateManager.subscribe(this.id, this.handleStateChange.bind(this));
    
    // Listen for global events
    EventBus.on('globalEvent', this.handleGlobalEvent.bind(this));
  },
  
  // Component methods
  handleButtonClick(event) {
    // Handle button click
    const buttonId = event.target.dataset.id;
    this.state.set('buttonClicked', buttonId);
  },
  
  handleStateChange(newState, oldState) {
    // React to state changes
    if (newState.buttonClicked !== oldState.buttonClicked) {
      this.updateButtonState(newState.buttonClicked);
    }
  },
  
  // Additional methods...
  
  // Cleanup
  destroy() {
    // Clean up event listeners
    this.events.removeAllListeners();
    StateManager.unsubscribe(this.id, this.handleStateChange);
    EventBus.off('globalEvent', this.handleGlobalEvent);
    
    // Remove content
    this.shadow.innerHTML = '';
  }
};
```

### Component Lifecycle

Components follow a defined lifecycle:

1. **Registration**: Component is registered with the system
2. **Initialization**: Component is initialized with its container and options
3. **Rendering**: Component renders its UI
4. **Activation**: Component becomes active and visible
5. **Updates**: Component receives updates and events
6. **Deactivation**: Component becomes inactive
7. **Destruction**: Component is destroyed and resources are released

### Shadow DOM Integration

Components use Shadow DOM for isolation:

```javascript
initialize(container, options) {
  // Create shadow DOM
  this.shadow = container.attachShadow({ mode: 'open' });
  
  // Load styles
  const style = document.createElement('style');
  style.textContent = this.styles;
  this.shadow.appendChild(style);
  
  // Create root element
  this.root = document.createElement('div');
  this.root.className = 'component-root';
  this.shadow.appendChild(this.root);
  
  // Initialize component
  this.render();
}
```

### Component Registration

Components are registered with the system:

```javascript
// Register component
Hephaestus.registerComponent({
  id: 'my-component',
  name: 'My Component',
  description: 'A custom component',
  path: '/components/my-component.html',
  script: '/scripts/my-component.js',
  styles: '/styles/my-component.css',
  initialize: function(container, options) {
    // Component initialization
  },
  render: function() {
    // Component rendering
  },
  destroy: function() {
    // Component cleanup
  }
});
```

## Communication Layer

The Communication Layer manages interaction with backend services.

### HTTP Communication

The system provides a standardized HTTP client:

```javascript
class HttpClient {
  static async get(url, options = {}) {
    return this.request('GET', url, null, options);
  }
  
  static async post(url, data, options = {}) {
    return this.request('POST', url, data, options);
  }
  
  static async put(url, data, options = {}) {
    return this.request('PUT', url, data, options);
  }
  
  static async delete(url, options = {}) {
    return this.request('DELETE', url, null, options);
  }
  
  static async request(method, url, data = null, options = {}) {
    const requestOptions = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      credentials: options.credentials || 'same-origin'
    };
    
    if (data) {
      requestOptions.body = JSON.stringify(data);
    }
    
    try {
      const response = await fetch(url, requestOptions);
      
      // Handle non-OK responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new HttpError(response.status, response.statusText, errorData);
      }
      
      // Handle empty responses
      if (response.status === 204) {
        return null;
      }
      
      // Parse JSON response
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      // Return text for other content types
      return await response.text();
    } catch (error) {
      if (error instanceof HttpError) {
        throw error;
      }
      
      throw new HttpError(0, 'Network Error', { message: error.message });
    }
  }
}

class HttpError extends Error {
  constructor(status, statusText, data) {
    super(`HTTP Error ${status}: ${statusText}`);
    this.status = status;
    this.statusText = statusText;
    this.data = data;
    this.name = 'HttpError';
  }
}
```

### WebSocket Communication

The system provides WebSocket communication:

```javascript
class WebSocketClient {
  constructor(url, options = {}) {
    this.url = url;
    this.options = options;
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
    this.reconnectDelay = options.reconnectDelay || 1000;
    this.listeners = {};
    this.connected = false;
    this.messageQueue = [];
  }
  
  connect() {
    try {
      this.socket = new WebSocket(this.url);
      
      this.socket.onopen = this.handleOpen.bind(this);
      this.socket.onclose = this.handleClose.bind(this);
      this.socket.onerror = this.handleError.bind(this);
      this.socket.onmessage = this.handleMessage.bind(this);
    } catch (error) {
      console.error('WebSocket connection error', error);
      this.scheduleReconnect();
    }
    
    return this;
  }
  
  handleOpen(event) {
    console.log('WebSocket connected');
    this.connected = true;
    this.reconnectAttempts = 0;
    
    // Process queued messages
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
    
    // Notify listeners
    this.emit('open', event);
  }
  
  handleClose(event) {
    console.log('WebSocket closed', event.code, event.reason);
    this.connected = false;
    
    // Notify listeners
    this.emit('close', event);
    
    // Attempt to reconnect if not a clean close
    if (event.code !== 1000) {
      this.scheduleReconnect();
    }
  }
  
  handleError(event) {
    console.error('WebSocket error', event);
    
    // Notify listeners
    this.emit('error', event);
  }
  
  handleMessage(event) {
    let data;
    
    // Parse JSON data
    try {
      data = JSON.parse(event.data);
    } catch (error) {
      data = event.data;
    }
    
    // Notify listeners
    this.emit('message', data);
    
    // Handle specific message types
    if (data && data.type) {
      this.emit(data.type, data);
    }
  }
  
  send(data) {
    if (!this.connected) {
      // Queue message for later
      this.messageQueue.push(data);
      return false;
    }
    
    try {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(message);
      return true;
    } catch (error) {
      console.error('WebSocket send error', error);
      return false;
    }
  }
  
  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Maximum reconnect attempts reached');
      this.emit('reconnect_failed');
      return;
    }
    
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);
    
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      this.emit('reconnect_attempt', this.reconnectAttempts);
      this.connect();
    }, delay);
  }
  
  close(code = 1000, reason = '') {
    if (this.socket) {
      this.socket.close(code, reason);
    }
  }
  
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    
    this.listeners[event].push(callback);
    return this;
  }
  
  off(event, callback) {
    if (!this.listeners[event]) return this;
    
    if (callback) {
      const index = this.listeners[event].indexOf(callback);
      if (index !== -1) {
        this.listeners[event].splice(index, 1);
      }
    } else {
      this.listeners[event] = [];
    }
    
    return this;
  }
  
  emit(event, data) {
    if (!this.listeners[event]) return;
    
    this.listeners[event].forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in WebSocket listener for ${event}`, error);
      }
    });
  }
}
```

### Service Discovery

The system discovers and connects to component services:

```javascript
class ServiceDiscovery {
  static async getServices() {
    try {
      const response = await HttpClient.get('/api/system/services');
      return response.services || [];
    } catch (error) {
      console.error('Failed to discover services', error);
      return [];
    }
  }
  
  static async getServiceUrl(componentId, serviceType = 'api') {
    const services = await this.getServices();
    const service = services.find(s => s.component === componentId && s.id.includes(serviceType));
    
    return service ? service.url : null;
  }
  
  static async connectToService(componentId, serviceType = 'ws') {
    const url = await this.getServiceUrl(componentId, serviceType);
    
    if (!url) {
      throw new Error(`Service not found: ${componentId} (${serviceType})`);
    }
    
    return new WebSocketClient(url).connect();
  }
}
```

## State Management

The State Management system handles UI state persistence and synchronization.

### State Manager

The State Manager provides namespaced state management:

```javascript
class StateManager {
  constructor() {
    this.state = {};
    this.subscribers = {};
    this.persistence = new StatePersistence();
    
    // Load persisted state
    this.loadPersistedState();
  }
  
  loadPersistedState() {
    const persisted = this.persistence.load();
    if (persisted) {
      this.state = persisted;
    }
  }
  
  saveState() {
    this.persistence.save(this.state);
  }
  
  getNamespace(namespace) {
    if (!this.state[namespace]) {
      this.state[namespace] = {};
    }
    
    return this.state[namespace];
  }
  
  get(namespace, key, defaultValue = null) {
    const ns = this.getNamespace(namespace);
    return key in ns ? ns[key] : defaultValue;
  }
  
  set(namespace, key, value) {
    const ns = this.getNamespace(namespace);
    const oldValue = ns[key];
    
    // Skip if value hasn't changed
    if (oldValue === value) return false;
    
    // Update state
    const oldState = { ...ns };
    ns[key] = value;
    
    // Save state
    this.saveState();
    
    // Notify subscribers
    this.notifySubscribers(namespace, ns, oldState);
    
    return true;
  }
  
  update(namespace, updates) {
    const ns = this.getNamespace(namespace);
    const oldState = { ...ns };
    
    // Apply updates
    let changed = false;
    Object.entries(updates).forEach(([key, value]) => {
      if (ns[key] !== value) {
        ns[key] = value;
        changed = true;
      }
    });
    
    // Skip if nothing changed
    if (!changed) return false;
    
    // Save state
    this.saveState();
    
    // Notify subscribers
    this.notifySubscribers(namespace, ns, oldState);
    
    return true;
  }
  
  subscribe(namespace, callback) {
    if (!this.subscribers[namespace]) {
      this.subscribers[namespace] = [];
    }
    
    this.subscribers[namespace].push(callback);
    
    return () => this.unsubscribe(namespace, callback);
  }
  
  unsubscribe(namespace, callback) {
    if (!this.subscribers[namespace]) return;
    
    const index = this.subscribers[namespace].indexOf(callback);
    if (index !== -1) {
      this.subscribers[namespace].splice(index, 1);
    }
  }
  
  notifySubscribers(namespace, newState, oldState) {
    if (!this.subscribers[namespace]) return;
    
    this.subscribers[namespace].forEach(callback => {
      try {
        callback(newState, oldState);
      } catch (error) {
        console.error(`Error in state subscriber for ${namespace}`, error);
      }
    });
  }
}
```

### State Persistence

The State Persistence system handles state storage:

```javascript
class StatePersistence {
  constructor(options = {}) {
    this.storageKey = options.storageKey || 'hephaestus_state';
    this.storage = options.storage || localStorage;
    this.debounceTime = options.debounceTime || 100;
    this.saveTimeout = null;
  }
  
  save(state) {
    // Debounce saves
    clearTimeout(this.saveTimeout);
    this.saveTimeout = setTimeout(() => {
      try {
        const serialized = JSON.stringify(state);
        this.storage.setItem(this.storageKey, serialized);
      } catch (error) {
        console.error('Failed to save state', error);
      }
    }, this.debounceTime);
  }
  
  load() {
    try {
      const serialized = this.storage.getItem(this.storageKey);
      return serialized ? JSON.parse(serialized) : null;
    } catch (error) {
      console.error('Failed to load state', error);
      return null;
    }
  }
  
  clear() {
    try {
      this.storage.removeItem(this.storageKey);
      return true;
    } catch (error) {
      console.error('Failed to clear state', error);
      return false;
    }
  }
}
```

### Component State

Components use isolated state:

```javascript
class ComponentState {
  constructor(componentId, stateManager) {
    this.componentId = componentId;
    this.stateManager = stateManager;
    this.state = this.stateManager.getNamespace(this.componentId);
  }
  
  get(key, defaultValue = null) {
    return this.stateManager.get(this.componentId, key, defaultValue);
  }
  
  set(key, value) {
    return this.stateManager.set(this.componentId, key, value);
  }
  
  update(updates) {
    return this.stateManager.update(this.componentId, updates);
  }
  
  subscribe(callback) {
    return this.stateManager.subscribe(this.componentId, callback);
  }
  
  getAll() {
    return { ...this.state };
  }
}
```

## Template Engine

The Template Engine handles HTML template loading and rendering.

### Template Loading

Templates are loaded from various sources:

```javascript
class TemplateEngine {
  constructor() {
    this.templates = {};
    this.loaders = {
      cache: this.loadFromCache.bind(this),
      inline: this.loadFromInline.bind(this),
      file: this.loadFromFile.bind(this),
      url: this.loadFromUrl.bind(this)
    };
  }
  
  async loadTemplate(templateId, options = {}) {
    // Check cache first
    if (this.templates[templateId] && !options.forceReload) {
      return this.templates[templateId];
    }
    
    // Determine loader
    const loader = options.loader || 'file';
    
    if (!this.loaders[loader]) {
      throw new Error(`Unknown template loader: ${loader}`);
    }
    
    // Load template
    try {
      const template = await this.loaders[loader](templateId, options);
      
      // Cache template
      this.templates[templateId] = template;
      
      return template;
    } catch (error) {
      console.error(`Failed to load template: ${templateId}`, error);
      throw error;
    }
  }
  
  loadFromCache(templateId) {
    return this.templates[templateId] || null;
  }
  
  loadFromInline(templateId) {
    const element = document.getElementById(templateId);
    
    if (!element || element.tagName !== 'TEMPLATE') {
      throw new Error(`Template not found: ${templateId}`);
    }
    
    return element.innerHTML;
  }
  
  async loadFromFile(templateId, options = {}) {
    const basePath = options.basePath || '/components/';
    const extension = options.extension || '.html';
    const url = `${basePath}${templateId}${extension}`;
    
    return this.loadFromUrl(url);
  }
  
  async loadFromUrl(url) {
    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Failed to load template from URL: ${url} (${response.status})`);
      }
      
      return await response.text();
    } catch (error) {
      console.error(`Failed to load template from URL: ${url}`, error);
      throw error;
    }
  }
}
```

### Template Rendering

Templates are rendered with variables:

```javascript
class TemplateRenderer {
  constructor(options = {}) {
    this.options = options;
  }
  
  render(template, context = {}) {
    // Simple variable replacement
    return template.replace(/\{\{\s*([^}]+)\s*\}\}/g, (match, key) => {
      // Split key for nested properties
      const keys = key.trim().split('.');
      let value = context;
      
      // Traverse object
      for (const k of keys) {
        value = value?.[k];
        
        if (value === undefined || value === null) {
          return this.options.nullValue || '';
        }
      }
      
      return value;
    });
  }
  
  // More complex rendering with conditionals, loops, etc.
  renderAdvanced(template, context = {}) {
    // Implementation of more advanced template features
    // - Conditional blocks
    // - Loops
    // - Includes
    // - Filters
  }
}
```

## UI Components

Hephaestus provides several built-in UI components.

### Navigation Component

The Navigation Component provides the main sidebar:

```javascript
const NavigationComponent = {
  id: 'navigation',
  name: 'Navigation',
  
  initialize(container) {
    this.container = container;
    this.shadow = container.attachShadow({ mode: 'open' });
    this.state = new ComponentState('navigation', StateManager);
    
    // Load components
    this.loadComponents();
    
    // Render navigation
    this.render();
    
    // Setup event listeners
    this.setupEventListeners();
  },
  
  async loadComponents() {
    try {
      const response = await HttpClient.get('/api/components');
      this.components = response.components || [];
      
      // Group components by category
      this.categorizedComponents = this.categorizeComponents(this.components);
      
      // Re-render if already rendered
      if (this.isRendered) {
        this.render();
      }
    } catch (error) {
      console.error('Failed to load components', error);
      this.components = [];
      this.categorizedComponents = {};
    }
  },
  
  categorizeComponents(components) {
    const categories = {};
    
    components.forEach(component => {
      const category = component.category || 'Other';
      
      if (!categories[category]) {
        categories[category] = [];
      }
      
      categories[category].push(component);
    });
    
    return categories;
  },
  
  render() {
    // Load and render template
    TemplateEngine.loadTemplate('navigation-component')
      .then(template => {
        const context = {
          categories: this.categorizedComponents,
          activeComponent: this.state.get('activeComponent')
        };
        
        this.shadow.innerHTML = TemplateRenderer.render(template, context);
        this.isRendered = true;
        
        // Set up component references
        this.setupComponentReferences();
      });
  },
  
  setupComponentReferences() {
    this.navItems = this.shadow.querySelectorAll('.nav-item');
  },
  
  setupEventListeners() {
    // Handle navigation item clicks
    this.shadow.addEventListener('click', event => {
      const navItem = event.target.closest('.nav-item');
      
      if (navItem) {
        const componentId = navItem.dataset.componentId;
        this.activateComponent(componentId);
      }
    });
    
    // Handle category toggles
    this.shadow.addEventListener('click', event => {
      const categoryToggle = event.target.closest('.category-toggle');
      
      if (categoryToggle) {
        const categoryId = categoryToggle.dataset.categoryId;
        this.toggleCategory(categoryId);
      }
    });
    
    // Subscribe to state changes
    this.state.subscribe((newState, oldState) => {
      if (newState.activeComponent !== oldState.activeComponent) {
        this.updateActiveNavItem(newState.activeComponent);
      }
    });
  },
  
  activateComponent(componentId) {
    // Update state
    this.state.set('activeComponent', componentId);
    
    // Emit event to load component
    EventBus.emit('loadComponent', { componentId });
  },
  
  toggleCategory(categoryId) {
    const expandedCategories = this.state.get('expandedCategories', []);
    
    if (expandedCategories.includes(categoryId)) {
      // Collapse category
      const newExpanded = expandedCategories.filter(id => id !== categoryId);
      this.state.set('expandedCategories', newExpanded);
    } else {
      // Expand category
      this.state.set('expandedCategories', [...expandedCategories, categoryId]);
    }
    
    // Update UI
    this.updateCategoryState();
  },
  
  updateActiveNavItem(componentId) {
    // Remove active class from all nav items
    this.navItems.forEach(item => {
      item.classList.remove('active');
    });
    
    // Add active class to selected nav item
    const activeItem = this.shadow.querySelector(`.nav-item[data-component-id="${componentId}"]`);
    if (activeItem) {
      activeItem.classList.add('active');
      
      // Ensure category is expanded
      const category = activeItem.closest('.category');
      if (category) {
        const categoryId = category.dataset.categoryId;
        this.ensureCategoryExpanded(categoryId);
      }
    }
  },
  
  ensureCategoryExpanded(categoryId) {
    const expandedCategories = this.state.get('expandedCategories', []);
    
    if (!expandedCategories.includes(categoryId)) {
      this.state.set('expandedCategories', [...expandedCategories, categoryId]);
      this.updateCategoryState();
    }
  },
  
  updateCategoryState() {
    const expandedCategories = this.state.get('expandedCategories', []);
    
    // Update all category elements
    const categories = this.shadow.querySelectorAll('.category');
    categories.forEach(category => {
      const categoryId = category.dataset.categoryId;
      const isExpanded = expandedCategories.includes(categoryId);
      
      category.classList.toggle('expanded', isExpanded);
    });
  }
};
```

### Terminal Component

The Terminal Component provides terminal integration:

```javascript
const TerminalComponent = {
  id: 'terminal',
  name: 'Terminal',
  
  initialize(container) {
    this.container = container;
    this.shadow = container.attachShadow({ mode: 'open' });
    this.state = new ComponentState('terminal', StateManager);
    
    // Render terminal
    this.render();
    
    // Initialize terminal
    this.initializeTerminal();
    
    // Setup event listeners
    this.setupEventListeners();
  },
  
  render() {
    // Load and render template
    TemplateEngine.loadTemplate('terminal-component')
      .then(template => {
        this.shadow.innerHTML = TemplateRenderer.render(template, {});
        
        // Set up component references
        this.terminalContainer = this.shadow.querySelector('.terminal-container');
        this.toolbarContainer = this.shadow.querySelector('.terminal-toolbar');
      });
  },
  
  async initializeTerminal() {
    // Connect to terminal service
    try {
      this.terminalService = await ServiceDiscovery.connectToService('terma', 'ws');
      
      // Create terminal instance
      this.createTerminal();
      
      // Set up terminal events
      this.setupTerminalEvents();
    } catch (error) {
      console.error('Failed to initialize terminal', error);
      
      // Show error message
      this.showTerminalError('Failed to connect to terminal service');
    }
  },
  
  createTerminal() {
    // Get terminal options from state
    const options = this.state.get('terminalOptions', {
      fontFamily: 'monospace',
      fontSize: 14,
      lineHeight: 1.5,
      cursorBlink: true,
      cursorStyle: 'block',
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
        cursor: '#ffffff',
        selection: 'rgba(255, 255, 255, 0.3)'
      }
    });
    
    // Create terminal element
    this.terminal = document.createElement('div');
    this.terminal.className = 'terminal';
    this.terminalContainer.appendChild(this.terminal);
    
    // Initialize terminal with options
    // This would typically use a library like xterm.js
    // For this example, we're using a placeholder
    this.terminal.innerHTML = '<div class="terminal-output"></div>';
    this.output = this.terminal.querySelector('.terminal-output');
    
    // Add input field
    this.input = document.createElement('input');
    this.input.className = 'terminal-input';
    this.input.setAttribute('type', 'text');
    this.input.setAttribute('autocomplete', 'off');
    this.input.setAttribute('spellcheck', 'false');
    this.terminal.appendChild(this.input);
    
    // Focus input
    this.input.focus();
  },
  
  setupTerminalEvents() {
    // Handle input
    this.input.addEventListener('keydown', event => {
      if (event.key === 'Enter') {
        const command = this.input.value;
        this.input.value = '';
        
        // Display command
        this.appendOutput(`> ${command}`);
        
        // Send command to service
        this.sendCommand(command);
      }
    });
    
    // Handle terminal service messages
    this.terminalService.on('message', data => {
      if (data.type === 'output') {
        this.appendOutput(data.content);
      } else if (data.type === 'error') {
        this.appendOutput(`Error: ${data.content}`, 'error');
      }
    });
    
    // Handle connection status
    this.terminalService.on('close', () => {
      this.appendOutput('Terminal connection closed', 'info');
    });
    
    this.terminalService.on('reconnect_attempt', attempt => {
      this.appendOutput(`Reconnecting... (attempt ${attempt})`, 'info');
    });
    
    this.terminalService.on('open', () => {
      this.appendOutput('Terminal connected', 'info');
    });
  },
  
  sendCommand(command) {
    if (!this.terminalService || !this.terminalService.connected) {
      this.appendOutput('Terminal not connected', 'error');
      return;
    }
    
    this.terminalService.send({
      type: 'command',
      content: command
    });
  },
  
  appendOutput(content, type = 'standard') {
    const line = document.createElement('div');
    line.className = `terminal-line terminal-line-${type}`;
    line.textContent = content;
    
    this.output.appendChild(line);
    
    // Scroll to bottom
    this.output.scrollTop = this.output.scrollHeight;
  },
  
  showTerminalError(message) {
    if (this.terminalContainer) {
      this.terminalContainer.innerHTML = `
        <div class="terminal-error">
          <div class="terminal-error-icon">⚠️</div>
          <div class="terminal-error-message">${message}</div>
          <button class="terminal-error-retry">Retry</button>
        </div>
      `;
      
      // Add retry handler
      const retryButton = this.terminalContainer.querySelector('.terminal-error-retry');
      if (retryButton) {
        retryButton.addEventListener('click', () => {
          this.terminalContainer.innerHTML = '';
          this.initializeTerminal();
        });
      }
    }
  },
  
  setupEventListeners() {
    // Handle toolbar actions
    this.toolbarContainer.addEventListener('click', event => {
      const action = event.target.closest('[data-action]');
      
      if (action) {
        const actionType = action.dataset.action;
        
        switch (actionType) {
          case 'clear':
            this.clearTerminal();
            break;
          case 'copy':
            this.copyTerminalContent();
            break;
          case 'settings':
            this.showTerminalSettings();
            break;
        }
      }
    });
  },
  
  clearTerminal() {
    if (this.output) {
      this.output.innerHTML = '';
    }
  },
  
  copyTerminalContent() {
    if (this.output) {
      const content = this.output.textContent;
      
      navigator.clipboard.writeText(content)
        .then(() => {
          this.showToast('Terminal content copied to clipboard');
        })
        .catch(error => {
          console.error('Failed to copy terminal content', error);
          this.showToast('Failed to copy terminal content', 'error');
        });
    }
  },
  
  showTerminalSettings() {
    // Show terminal settings dialog
    // This would typically use a dialog component
  },
  
  showToast(message, type = 'info') {
    // Show toast notification
    // This would typically use a notification component
  },
  
  destroy() {
    // Close terminal service connection
    if (this.terminalService) {
      this.terminalService.close();
    }
    
    // Clean up event listeners
    
    // Remove terminal
    this.shadow.innerHTML = '';
  }
};
```

## Theme System

The Theme System manages theme application and switching.

### Theme Manager

The Theme Manager handles theme loading and application:

```javascript
class ThemeManager {
  constructor() {
    this.themes = {
      light: {
        name: 'Light',
        vars: {
          '--background-color': '#ffffff',
          '--text-color': '#333333',
          '--primary-color': '#0066cc',
          '--secondary-color': '#6c757d',
          '--success-color': '#28a745',
          '--danger-color': '#dc3545',
          '--warning-color': '#ffc107',
          '--info-color': '#17a2b8',
          '--border-color': '#dee2e6',
          '--shadow-color': 'rgba(0, 0, 0, 0.1)'
        }
      },
      dark: {
        name: 'Dark',
        vars: {
          '--background-color': '#1e1e1e',
          '--text-color': '#d4d4d4',
          '--primary-color': '#0078d4',
          '--secondary-color': '#6c757d',
          '--success-color': '#28a745',
          '--danger-color': '#dc3545',
          '--warning-color': '#ffc107',
          '--info-color': '#17a2b8',
          '--border-color': '#444444',
          '--shadow-color': 'rgba(0, 0, 0, 0.5)'
        }
      }
    };
    
    this.currentTheme = 'light';
    
    // Initialize theme from saved preference
    this.initialize();
  }
  
  initialize() {
    // Get saved theme preference
    const savedTheme = localStorage.getItem('theme');
    
    // Check for system preference if no saved preference
    if (!savedTheme) {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.currentTheme = prefersDark ? 'dark' : 'light';
    } else {
      this.currentTheme = savedTheme;
    }
    
    // Apply theme
    this.applyTheme(this.currentTheme);
    
    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
      // Only change if using system preference
      if (!localStorage.getItem('theme')) {
        const newTheme = event.matches ? 'dark' : 'light';
        this.applyTheme(newTheme);
      }
    });
  }
  
  applyTheme(themeName) {
    const theme = this.themes[themeName];
    
    if (!theme) {
      console.error(`Theme not found: ${themeName}`);
      return false;
    }
    
    // Apply CSS variables
    const root = document.documentElement;
    
    Object.entries(theme.vars).forEach(([property, value]) => {
      root.style.setProperty(property, value);
    });
    
    // Set theme attribute
    document.body.setAttribute('data-theme', themeName);
    
    // Update current theme
    this.currentTheme = themeName;
    
    // Save preference
    localStorage.setItem('theme', themeName);
    
    // Emit theme change event
    const event = new CustomEvent('themechange', {
      detail: {
        theme: themeName,
        vars: theme.vars
      }
    });
    
    document.dispatchEvent(event);
    
    return true;
  }
  
  getTheme() {
    return this.currentTheme;
  }
  
  getThemeVariables(themeName = null) {
    const theme = this.themes[themeName || this.currentTheme];
    return theme ? { ...theme.vars } : null;
  }
  
  registerTheme(name, vars) {
    if (this.themes[name]) {
      console.warn(`Theme already exists: ${name}`);
      return false;
    }
    
    this.themes[name] = {
      name,
      vars
    };
    
    return true;
  }
  
  updateTheme(name, vars) {
    if (!this.themes[name]) {
      console.error(`Theme not found: ${name}`);
      return false;
    }
    
    this.themes[name].vars = {
      ...this.themes[name].vars,
      ...vars
    };
    
    // Apply if current theme
    if (this.currentTheme === name) {
      this.applyTheme(name);
    }
    
    return true;
  }
}
```

## Security Considerations

Hephaestus implements several security measures:

### Content Security Policy

The application uses a strict Content Security Policy:

```javascript
// Server-side CSP header
const cspHeader = {
  'Content-Security-Policy': [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "font-src 'self'",
    "connect-src 'self' ws: wss:",
    "frame-src 'none'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'"
  ].join('; ')
};
```

### Input Validation

All user input is validated:

```javascript
class InputValidator {
  static validateString(value, options = {}) {
    const {
      required = false,
      minLength = 0,
      maxLength = Number.MAX_SAFE_INTEGER,
      pattern = null
    } = options;
    
    // Check required
    if (required && (value === undefined || value === null || value === '')) {
      return { valid: false, message: 'Value is required' };
    }
    
    // Skip further validation if not required and empty
    if (!required && (value === undefined || value === null || value === '')) {
      return { valid: true };
    }
    
    // Convert to string
    const strValue = String(value);
    
    // Check length
    if (strValue.length < minLength) {
      return { valid: false, message: `Minimum length is ${minLength}` };
    }
    
    if (strValue.length > maxLength) {
      return { valid: false, message: `Maximum length is ${maxLength}` };
    }
    
    // Check pattern
    if (pattern && !pattern.test(strValue)) {
      return { valid: false, message: 'Invalid format' };
    }
    
    return { valid: true };
  }
  
  static sanitizeHtml(value) {
    // Simple HTML sanitization
    return String(value)
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}
```

### Cross-Origin Resource Sharing

The application implements strict CORS policies:

```javascript
// Server-side CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': process.env.ALLOWED_ORIGINS || 'http://localhost:8080',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Allow-Credentials': 'true',
  'Access-Control-Max-Age': '86400'
};
```

## Performance Considerations

Hephaestus is optimized for performance:

### Resource Loading

Resources are loaded efficiently:

```javascript
class ResourceLoader {
  static loaded = new Set();
  static loading = new Map();
  
  static async loadScript(url, options = {}) {
    // Check if already loaded
    if (this.loaded.has(url)) {
      return true;
    }
    
    // Check if currently loading
    if (this.loading.has(url)) {
      return this.loading.get(url);
    }
    
    // Create loading promise
    const loadPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = url;
      script.async = options.async !== false;
      
      // Add attributes
      if (options.attributes) {
        Object.entries(options.attributes).forEach(([key, value]) => {
          script.setAttribute(key, value);
        });
      }
      
      // Add integrity and crossorigin for CDN resources
      if (options.integrity) {
        script.integrity = options.integrity;
        script.crossOrigin = 'anonymous';
      }
      
      // Handle load events
      script.onload = () => {
        this.loaded.add(url);
        this.loading.delete(url);
        resolve(true);
      };
      
      script.onerror = () => {
        this.loading.delete(url);
        reject(new Error(`Failed to load script: ${url}`));
      };
      
      // Add to document
      document.head.appendChild(script);
    });
    
    // Store loading promise
    this.loading.set(url, loadPromise);
    
    return loadPromise;
  }
  
  static async loadStyle(url, options = {}) {
    // Check if already loaded
    if (this.loaded.has(url)) {
      return true;
    }
    
    // Check if currently loading
    if (this.loading.has(url)) {
      return this.loading.get(url);
    }
    
    // Create loading promise
    const loadPromise = new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = url;
      
      // Add attributes
      if (options.attributes) {
        Object.entries(options.attributes).forEach(([key, value]) => {
          link.setAttribute(key, value);
        });
      }
      
      // Add integrity and crossorigin for CDN resources
      if (options.integrity) {
        link.integrity = options.integrity;
        link.crossOrigin = 'anonymous';
      }
      
      // Handle load events
      link.onload = () => {
        this.loaded.add(url);
        this.loading.delete(url);
        resolve(true);
      };
      
      link.onerror = () => {
        this.loading.delete(url);
        reject(new Error(`Failed to load stylesheet: ${url}`));
      };
      
      // Add to document
      document.head.appendChild(link);
    });
    
    // Store loading promise
    this.loading.set(url, loadPromise);
    
    return loadPromise;
  }
}
```

### Lazy Loading

Components are lazy-loaded:

```javascript
class ComponentLoader {
  static async loadComponent(componentId) {
    try {
      // Get component details
      const component = await ComponentRegistry.getComponent(componentId);
      
      if (!component) {
        throw new Error(`Component not found: ${componentId}`);
      }
      
      // Load resources
      await this.loadComponentResources(component);
      
      // Create component instance
      return this.createComponentInstance(component);
    } catch (error) {
      console.error(`Failed to load component: ${componentId}`, error);
      throw error;
    }
  }
  
  static async loadComponentResources(component) {
    const tasks = [];
    
    // Load script
    if (component.script) {
      tasks.push(ResourceLoader.loadScript(component.script));
    }
    
    // Load style
    if (component.style) {
      tasks.push(ResourceLoader.loadStyle(component.style));
    }
    
    // Wait for all resources to load
    await Promise.all(tasks);
  }
  
  static createComponentInstance(component) {
    // Get component constructor
    const ComponentClass = window[component.className] || window.Hephaestus?.components?.[component.id];
    
    if (!ComponentClass) {
      throw new Error(`Component class not found: ${component.className || component.id}`);
    }
    
    // Create instance
    return new ComponentClass(component);
  }
}
```

### Memory Management

The application implements careful memory management:

```javascript
class MemoryManager {
  static components = new Map();
  
  static registerComponent(componentId, instance) {
    this.components.set(componentId, {
      instance,
      lastUsed: Date.now()
    });
  }
  
  static unregisterComponent(componentId) {
    this.components.delete(componentId);
  }
  
  static cleanupUnusedComponents(maxInactive = 300000) { // 5 minutes
    const now = Date.now();
    
    this.components.forEach((data, componentId) => {
      if (now - data.lastUsed > maxInactive) {
        // Destroy component
        if (typeof data.instance.destroy === 'function') {
          try {
            data.instance.destroy();
          } catch (error) {
            console.error(`Error destroying component: ${componentId}`, error);
          }
        }
        
        // Remove from registry
        this.components.delete(componentId);
      }
    });
  }
  
  static updateComponentUsage(componentId) {
    const data = this.components.get(componentId);
    
    if (data) {
      data.lastUsed = Date.now();
    }
  }
}
```

## Accessibility Considerations

Hephaestus implements accessibility features:

### Keyboard Navigation

The application supports keyboard navigation:

```javascript
class KeyboardManager {
  constructor() {
    this.shortcuts = new Map();
    this.focused = null;
    
    // Set up event listeners
    this.setupEventListeners();
  }
  
  setupEventListeners() {
    // Listen for keydown events
    document.addEventListener('keydown', this.handleKeyDown.bind(this));
    
    // Track focus
    document.addEventListener('focusin', this.handleFocusIn.bind(this));
  }
  
  handleKeyDown(event) {
    // Check for shortcuts
    const shortcut = this.getShortcutKey(event);
    
    if (shortcut && this.shortcuts.has(shortcut)) {
      const handlers = this.shortcuts.get(shortcut);
      
      // Find appropriate handler
      const handler = this.findHandler(handlers);
      
      if (handler) {
        // Prevent default
        event.preventDefault();
        
        // Execute handler
        try {
          handler.callback(event);
        } catch (error) {
          console.error(`Error executing keyboard shortcut: ${shortcut}`, error);
        }
        
        return true;
      }
    }
    
    return false;
  }
  
  handleFocusIn(event) {
    this.focused = event.target;
  }
  
  getShortcutKey(event) {
    const parts = [];
    
    if (event.ctrlKey) parts.push('Ctrl');
    if (event.altKey) parts.push('Alt');
    if (event.shiftKey) parts.push('Shift');
    if (event.metaKey) parts.push('Meta');
    
    // Add key
    if (event.key && event.key !== 'Control' && event.key !== 'Alt' && 
        event.key !== 'Shift' && event.key !== 'Meta') {
      parts.push(event.key);
    }
    
    return parts.join('+');
  }
  
  findHandler(handlers) {
    // Check for global handler
    const globalHandler = handlers.find(h => h.scope === 'global');
    
    // Check for component handler
    if (this.focused) {
      const component = this.getComponentForElement(this.focused);
      
      if (component) {
        const componentHandler = handlers.find(h => h.scope === component);
        
        if (componentHandler) {
          return componentHandler;
        }
      }
    }
    
    return globalHandler;
  }
  
  getComponentForElement(element) {
    // Find shadow root
    let root = element;
    
    while (root && !(root instanceof ShadowRoot)) {
      root = root.parentNode;
      
      if (root instanceof ShadowRoot) {
        // Get host element
        const host = root.host;
        
        // Get component ID
        return host.dataset.componentId;
      }
    }
    
    return null;
  }
  
  registerShortcut(shortcut, callback, options = {}) {
    const { scope = 'global', description = '' } = options;
    
    if (!this.shortcuts.has(shortcut)) {
      this.shortcuts.set(shortcut, []);
    }
    
    this.shortcuts.get(shortcut).push({
      callback,
      scope,
      description
    });
  }
  
  unregisterShortcut(shortcut, callback, scope = 'global') {
    if (!this.shortcuts.has(shortcut)) return;
    
    const handlers = this.shortcuts.get(shortcut);
    const index = handlers.findIndex(h => h.callback === callback && h.scope === scope);
    
    if (index !== -1) {
      handlers.splice(index, 1);
      
      if (handlers.length === 0) {
        this.shortcuts.delete(shortcut);
      }
    }
  }
  
  getShortcuts() {
    const result = [];
    
    this.shortcuts.forEach((handlers, shortcut) => {
      handlers.forEach(handler => {
        result.push({
          shortcut,
          scope: handler.scope,
          description: handler.description
        });
      });
    });
    
    return result;
  }
}
```

### ARIA Support

The application implements ARIA attributes:

```javascript
class AccessibilityHelper {
  static makeAccessible(element, options = {}) {
    const {
      role,
      label,
      description,
      expanded,
      selected,
      checked,
      disabled,
      hidden,
      controls,
      labelledby,
      describedby,
      live,
      atomic,
      relevant,
      busy
    } = options;
    
    // Set role
    if (role) {
      element.setAttribute('role', role);
    }
    
    // Set label
    if (label) {
      element.setAttribute('aria-label', label);
    }
    
    // Set description
    if (description) {
      element.setAttribute('aria-description', description);
    }
    
    // Set state attributes
    if (expanded !== undefined) {
      element.setAttribute('aria-expanded', expanded.toString());
    }
    
    if (selected !== undefined) {
      element.setAttribute('aria-selected', selected.toString());
    }
    
    if (checked !== undefined) {
      element.setAttribute('aria-checked', checked.toString());
    }
    
    if (disabled !== undefined) {
      element.setAttribute('aria-disabled', disabled.toString());
      
      if (disabled) {
        element.setAttribute('tabindex', '-1');
      }
    }
    
    if (hidden !== undefined) {
      element.setAttribute('aria-hidden', hidden.toString());
    }
    
    // Set relationship attributes
    if (controls) {
      element.setAttribute('aria-controls', controls);
    }
    
    if (labelledby) {
      element.setAttribute('aria-labelledby', labelledby);
    }
    
    if (describedby) {
      element.setAttribute('aria-describedby', describedby);
    }
    
    // Set live region attributes
    if (live) {
      element.setAttribute('aria-live', live);
    }
    
    if (atomic !== undefined) {
      element.setAttribute('aria-atomic', atomic.toString());
    }
    
    if (relevant) {
      element.setAttribute('aria-relevant', relevant);
    }
    
    if (busy !== undefined) {
      element.setAttribute('aria-busy', busy.toString());
    }
    
    return element;
  }
  
  static makeButton(element, label, options = {}) {
    // Set role
    element.setAttribute('role', 'button');
    
    // Set label
    if (label) {
      element.setAttribute('aria-label', label);
    }
    
    // Set tabindex
    if (!element.hasAttribute('tabindex') && !options.disabled) {
      element.setAttribute('tabindex', '0');
    }
    
    // Add keyboard handler
    element.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        element.click();
      }
    });
    
    // Apply other options
    return this.makeAccessible(element, options);
  }
}
```

## Deployment and Configuration

Hephaestus is designed for flexible deployment:

### Configuration System

The application uses a hierarchical configuration system:

```javascript
class ConfigurationManager {
  constructor() {
    this.config = {
      system: {
        debug: false,
        environment: 'production',
        baseUrl: window.location.origin,
        apiUrl: `${window.location.origin}/api`,
        wsUrl: `${window.location.origin.replace('http', 'ws')}/ws`
      },
      ui: {
        theme: 'light',
        fontSize: 'medium',
        layout: 'default',
        sidebarPosition: 'left',
        defaultComponent: 'ergon'
      },
      components: {}
    };
    
    // Load configuration
    this.loadConfiguration();
  }
  
  async loadConfiguration() {
    try {
      // Load system configuration
      const systemConfig = await this.fetchSystemConfig();
      
      if (systemConfig) {
        this.config.system = {
          ...this.config.system,
          ...systemConfig
        };
      }
      
      // Load user configuration
      const userConfig = this.loadUserConfig();
      
      if (userConfig) {
        this.config.ui = {
          ...this.config.ui,
          ...userConfig.ui
        };
        
        this.config.components = {
          ...this.config.components,
          ...userConfig.components
        };
      }
      
      // Emit configuration loaded event
      const event = new CustomEvent('configurationloaded', {
        detail: {
          config: this.config
        }
      });
      
      document.dispatchEvent(event);
    } catch (error) {
      console.error('Failed to load configuration', error);
    }
  }
  
  async fetchSystemConfig() {
    try {
      const response = await fetch('/api/system/config');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch system configuration: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch system configuration', error);
      return null;
    }
  }
  
  loadUserConfig() {
    try {
      const saved = localStorage.getItem('user_config');
      
      return saved ? JSON.parse(saved) : null;
    } catch (error) {
      console.error('Failed to load user configuration', error);
      return null;
    }
  }
  
  saveUserConfig() {
    try {
      const userConfig = {
        ui: this.config.ui,
        components: this.config.components
      };
      
      localStorage.setItem('user_config', JSON.stringify(userConfig));
      
      return true;
    } catch (error) {
      console.error('Failed to save user configuration', error);
      return false;
    }
  }
  
  get(path, defaultValue = null) {
    const parts = path.split('.');
    let current = this.config;
    
    for (const part of parts) {
      if (current === undefined || current === null) {
        return defaultValue;
      }
      
      current = current[part];
    }
    
    return current !== undefined ? current : defaultValue;
  }
  
  set(path, value) {
    const parts = path.split('.');
    const last = parts.pop();
    let current = this.config;
    
    for (const part of parts) {
      if (current[part] === undefined) {
        current[part] = {};
      }
      
      current = current[part];
    }
    
    current[last] = value;
    
    // Save if UI or component configuration
    if (path.startsWith('ui.') || path.startsWith('components.')) {
      this.saveUserConfig();
    }
    
    // Emit configuration changed event
    const event = new CustomEvent('configurationchanged', {
      detail: {
        path,
        value
      }
    });
    
    document.dispatchEvent(event);
    
    return true;
  }
  
  reset(path) {
    const parts = path.split('.');
    const defaultConfig = {
      ui: {
        theme: 'light',
        fontSize: 'medium',
        layout: 'default',
        sidebarPosition: 'left',
        defaultComponent: 'ergon'
      }
    };
    
    let defaultValue;
    let current = defaultConfig;
    
    for (const part of parts) {
      if (current === undefined || current === null) {
        defaultValue = undefined;
        break;
      }
      
      current = current[part];
      defaultValue = current;
    }
    
    // Set default value
    this.set(path, defaultValue);
    
    return true;
  }
}
```

## Future Enhancements

Planned future enhancements for Hephaestus include:

### Advanced Visualization

- 3D rendering for complex data visualization
- Interactive data exploration tools
- Advanced graph visualization for knowledge graphs

### Enhanced Accessibility

- Screen reader optimizations
- High contrast themes
- Keyboard navigation improvements
- Focus management enhancements

### Mobile Support

- Responsive design for mobile devices
- Touch-optimized interfaces
- Mobile-specific layouts
- Progressive Web App (PWA) capabilities

### Offline Capabilities

- Offline mode for core functionality
- Local data synchronization
- ServiceWorker for resource caching
- Background synchronization