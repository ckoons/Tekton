# State Management Patterns

**Last Updated:** May 26, 2025

This document describes the state management patterns for the Tekton UI framework. This comprehensive state management system provides a centralized, subscription-based architecture for managing component and application state.

## Table of Contents

1. [Overview](#overview)
2. [Key Concepts](#key-concepts)
3. [Core Architecture](#core-architecture)
4. [Using State in Components](#using-state-in-components)
5. [State Persistence](#state-persistence)
6. [State Debugging](#state-debugging)
7. [Best Practices](#best-practices)
8. [Migration Guide](#migration-guide)
9. [Common Patterns](#common-patterns)
10. [Advanced Usage](#advanced-usage)

## Overview

The Tekton State Management Pattern provides a robust solution for managing state across components and the entire application. It supports:

- **Namespaced State:** Isolate component state while allowing sharing when needed
- **Subscription System:** React to state changes with a powerful event system
- **Persistence Layer:** Store state between sessions with configurable persistence
- **Debugging Tools:** Monitor and debug state changes with built-in tools
- **Performance Monitoring:** Track state update performance metrics

The architecture is designed to be:

- **Flexible:** Works with any component structure or pattern
- **Scalable:** Efficiently manages large state trees and many components
- **Debuggable:** Provides comprehensive tools for inspecting and debugging state
- **Performant:** Optimized for fast updates and minimal overhead

## Key Concepts

### State

State represents data that components need to render and function correctly. State can include:

- UI state (active tabs, expanded sections, etc.)
- Form data (input values, validation state, etc.)
- Application data (user settings, preferences, etc.)
- Cached data (API responses, computed values, etc.)

### Namespaces

State is organized into namespaces to prevent collisions and isolate component state:

- **Component Namespaces:** State specific to a component (usually uses component ID)
- **Shared Namespaces:** State shared between multiple components
- **Global Namespace:** Application-wide state accessible to all components

### Subscriptions

Components can subscribe to state changes to react and update accordingly:

- **Fine-grained Subscriptions:** Subscribe to specific keys or paths
- **Batch Updates:** Group multiple updates to prevent unnecessary rerenders
- **Derived State:** Automatically compute values based on other state

### Persistence

State can be persisted between sessions using various storage options:

- **Local Storage:** Persists between browser sessions
- **Session Storage:** Persists within a browser session
- **Custom Adapters:** Extend with custom storage solutions

## Core Architecture

The state management system consists of the following core components:

### StateManager

The central state store that manages all state data and provides APIs for state manipulation:

```javascript
// Access the state manager instance
const stateManager = window.tektonUI.stateManager;

// Get state from a namespace
const userSettings = stateManager.getState('userSettings');

// Update state in a namespace
stateManager.setState('userSettings', { theme: 'dark' });

// Subscribe to state changes
stateManager.subscribe('userSettings', (changes, state) => {
  console.log('Settings changed:', changes);
});
```

### ComponentStateUtils

Provides component-specific utilities for working with state:

```javascript
// Connect a component to the state system
component.utils.componentState.connect(component, {
  namespace: 'profileComponent',
  initialState: { user: null, isEditing: false },
  persist: true
});

// Component state API
component.state.get('user');
component.state.set('isEditing', true);
component.state.subscribe((changes, state) => {
  updateUI(state);
});
```

### StatePersistence

Handles storing and retrieving state across sessions:

```javascript
// Configure persistence for a namespace
stateManager.configurePersistence('userSettings', {
  type: 'localStorage',
  key: 'tekton_user_settings',
  exclude: ['temporaryData']
});

// Export persisted state
const exportedState = stateManager.exportPersistedState();

// Import persisted state
stateManager.importPersistedState(exportedState);
```

### StateDebug

Provides tools for debugging and monitoring state:

```javascript
// Enable state debugging
window.tektonUI.stateDebug.init({ logEnabled: true });

// Take a state snapshot
window.tektonUI.stateDebug.takeSnapshot();

// Toggle the state debugger UI
window.tektonUI.stateDebug.toggle();
```

## Using State in Components

### Connecting Components to State

Components should connect to the state system during initialization:

```javascript
function initComponent() {
  // Connect to state system
  component.utils.componentState.utils.connect(component, {
    namespace: component.id,
    initialState: {
      isLoading: false,
      data: null,
      error: null
    },
    persist: true,
    persistenceType: 'localStorage'
  });
  
  // Load initial data
  loadData();
}
```

### Working with Component State

Once connected, components can use the state API:

```javascript
// Get state values
const data = component.state.get('data');
const isLoading = component.state.get('isLoading');

// Update state
component.state.set('isLoading', true);
component.state.set({
  data: responseData,
  isLoading: false
});

// Check if a state key exists
if (component.state.has('error')) {
  showError(component.state.get('error'));
}

// Toggle a boolean state
component.state.toggle('isExpanded');

// Reset state
component.state.reset();
```

### Subscribing to State Changes

Components can react to state changes with subscriptions:

```javascript
// Subscribe to all state changes
component.state.subscribe((changes, state) => {
  updateUI(state);
});

// Subscribe to specific keys
component.state.subscribe((changes, state) => {
  updateUserInfo(state.user);
}, { keys: ['user'] });

// Register a state effect (runs when state changes)
component.utils.lifecycle.registerStateEffect(
  component,
  ['theme', 'fontSize'],
  (state, changes) => {
    updateTheme(state.theme, state.fontSize);
  }
);
```

### Form Binding

Automatically bind input elements to state:

```javascript
// Create bound handlers
const handlers = component.state.bindInputs({
  'username': 'user.username',
  'email': 'user.email',
  'newsletter': 'preferences.newsletter'
});

// Use handlers with inputs
usernameInput.addEventListener('input', handlers.username);
emailInput.addEventListener('input', handlers.email);
newsletterCheckbox.addEventListener('change', handlers.newsletter);
```

### Derived State

Create computed values based on other state:

```javascript
// Create a derived state
component.state.derived(
  'fullName', 
  ['user.firstName', 'user.lastName'],
  (state) => {
    if (!state.user) return '';
    return `${state.user.firstName || ''} ${state.user.lastName || ''}`.trim();
  }
);

// Use the derived state
const fullName = component.state.get('fullName');
```

## State Persistence

### Configuring Persistence

Configure how state is persisted:

```javascript
// Configure persistence for a namespace
stateManager.configurePersistence('userSettings', {
  type: 'localStorage',
  key: 'tekton_user_settings',
  include: ['theme', 'fontSize', 'language'],
  exclude: ['temporaryData']
});

// Component-level persistence
component.utils.componentState.utils.connect(component, {
  namespace: 'profileComponent',
  persist: true,
  persistenceType: 'localStorage',
  excludeFromPersistence: ['isEditing', 'validationErrors']
});
```

### Persistence Types

The system supports multiple persistence types:

- **localStorage**: Persists data between browser sessions
- **sessionStorage**: Persists data within a browser session
- **memory**: Temporary storage (useful for testing)
- **cookie**: Cookie-based storage (with configurable expiration)
- **custom**: Register custom adapters for specialized storage

### Importing and Exporting State

Import and export state data:

```javascript
// Export all persisted state
const stateData = stateManager.exportPersistedState();

// Save to a file or send to server
saveToFile(JSON.stringify(stateData));

// Import state from data
stateManager.importPersistedState(JSON.parse(loadedData));
```

## State Debugging

### Using the State Debugger

The state debugging tools provide visibility into state changes:

- **State Inspector**: View and filter the current state tree
- **History**: Track state changes over time
- **Snapshots**: Take and compare state snapshots
- **Performance**: Monitor state update performance

Access the debugger with:

```javascript
// Toggle the debugger UI (also available with Ctrl+Shift+S)
window.tektonUI.stateDebug.toggle();

// Take a snapshot of current state
window.tektonUI.stateDebug.takeSnapshot();

// Enable console logging of state changes
window.tektonUI.stateDebug.setLogging(true);

// Clear history and snapshots
window.tektonUI.stateDebug.clear();
```

### Performance Monitoring

Track state update performance:

```javascript
// Enable performance monitoring
window.tektonUI.stateDebug.performanceEnabled = true;

// View performance metrics in the debugger UI
window.tektonUI.stateDebug.toggle();
// Select "Performance" tab
```

## Best Practices

### State Organization

Organize state for maintainability and performance:

1. **Use Namespaces**: Keep component state isolated in namespaces
2. **Flatten Structure**: Avoid deeply nested state objects
3. **Keep State Small**: Only store necessary data in state
4. **Use Semantic Names**: Name state keys clearly and consistently

Example namespace organization:

```
- global: Application-wide state shared by multiple components
- settings: User settings and preferences
- [componentId]: Component-specific state
```

### Component State Patterns

Common patterns for component state:

1. **Initialize Early**: Connect to state system during component initialization
2. **Single Source of Truth**: Use state as the source of truth for UI
3. **Pure Rendering**: Render UI based solely on state
4. **Controlled Inputs**: Bind form inputs to state

### Performance Optimization

Techniques for optimizing state performance:

1. **Batch Updates**: Use transactions for multiple state changes
2. **Fine-grained Subscriptions**: Subscribe only to needed state keys
3. **Memoize Derived Values**: Cache computed values when possible
4. **Debounce Updates**: Debounce rapid state changes

Example of batching updates:

```javascript
// Start a transaction
const commit = component.state.transaction();

// Make multiple updates
component.state.set('field1', value1);
component.state.set('field2', value2);
component.state.set('field3', value3);

// Commit the transaction (triggers one update)
commit();
```

### Sharing State Between Components

Patterns for sharing state:

1. **Shared Namespaces**: Use a common namespace for shared state
2. **Global State**: Use the global namespace for app-wide state
3. **State Providers**: Create service classes that manage specialized state
4. **Message Bus**: Use events for loosely coupled communication

Example of shared state:

```javascript
// Component A configures shared keys
component.utils.componentState.utils.connect(componentA, {
  namespace: 'componentA',
  initialState: { theme: 'dark', language: 'en' },
  sharedKeys: ['theme', 'language']
});

// Component B gets updates automatically
component.utils.componentState.utils.connect(componentB, {
  namespace: 'componentB',
  sharedKeys: ['theme', 'language']
});
```

## Migration Guide

### Migrating from Direct DOM Manipulation

If you're currently using direct DOM manipulation:

1. Move state variables to component state
2. Use state subscriptions to update UI
3. Derive UI from state rather than modifying DOM directly

**Before:**
```javascript
let isOpen = false;

function toggleMenu() {
  isOpen = !isOpen;
  document.querySelector('.menu').classList.toggle('open', isOpen);
}

button.addEventListener('click', toggleMenu);
```

**After:**
```javascript
// Initialize state
component.state.set('isMenuOpen', false);

// Subscribe to state changes
component.state.subscribe((changes) => {
  if ('isMenuOpen' in changes) {
    component.$('.menu').classList.toggle('open', changes.isMenuOpen);
  }
});

// Update state
button.addEventListener('click', () => {
  component.state.toggle('isMenuOpen');
});
```

### Migrating from Local Component State

If you're using component-local state variables:

1. Initialize component state with current values
2. Replace direct property access with state API
3. Update UI based on state subscriptions

**Before:**
```javascript
function initComponent() {
  component.data = {
    user: null,
    isLoading: false,
    error: null
  };
  
  loadUserData();
}

function loadUserData() {
  component.data.isLoading = true;
  updateLoadingUI();
  
  fetchUserData()
    .then(user => {
      component.data.user = user;
      component.data.isLoading = false;
      updateUserUI();
    })
    .catch(error => {
      component.data.error = error;
      component.data.isLoading = false;
      updateErrorUI();
    });
}
```

**After:**
```javascript
function initComponent() {
  // Connect to state system
  component.utils.componentState.utils.connect(component, {
    namespace: component.id,
    initialState: {
      user: null,
      isLoading: false,
      error: null
    }
  });
  
  // Subscribe to state changes
  component.state.subscribe((changes, state) => {
    if ('isLoading' in changes) {
      updateLoadingUI(state.isLoading);
    }
    if ('user' in changes) {
      updateUserUI(state.user);
    }
    if ('error' in changes) {
      updateErrorUI(state.error);
    }
  });
  
  loadUserData();
}

function loadUserData() {
  component.state.set('isLoading', true);
  
  fetchUserData()
    .then(user => {
      component.state.set({
        user: user,
        isLoading: false,
        error: null
      });
    })
    .catch(error => {
      component.state.set({
        error: error,
        isLoading: false
      });
    });
}
```

## Common Patterns

### Theme State

Managing theme state across the application:

```javascript
// Initialize theme state in global namespace
stateManager.setState('global', {
  theme: {
    mode: 'dark',
    primary: '#007bff',
    contrast: 'high'
  }
});

// Configure persistence
stateManager.configurePersistence('global', {
  type: 'localStorage',
  key: 'tekton_global',
  include: ['theme']
});

// Subscribe to theme changes
stateManager.subscribe('global', (changes, state) => {
  if ('theme' in changes || 'theme.mode' in changes) {
    applyTheme(state.theme);
  }
}, { keys: ['theme', 'theme.mode'] });

// Component-specific theme handling
component.utils.lifecycle.registerStateEffect(component,
  ['theme.mode'],
  (state) => {
    component.root.classList.toggle('dark-mode', state.theme.mode === 'dark');
  }
);
```

### Service Registry State (Hermes Example)

The Hermes component provides a real-world example of state management with real-time updates:

```javascript
// Initialize component with state
component.utils.componentState.utils.connect(component, {
  namespace: 'hermes',
  initialState: {
    // UI State
    activeTab: 'registry',
    registryViewMode: 'grid',
    isModalOpen: false,
    
    // Data State
    services: [],
    connections: [],
    messages: [],
    
    // Filters
    messageFilters: {
      types: {
        registration: true,
        heartbeat: true,
        query: true,
        data: true
      },
      components: {}
    }
  },
  persist: true,
  excludeFromPersistence: ['messages', 'isModalOpen'] // Ephemeral data
});

// Service updates trigger state changes
hermesService.addEventListener('servicesUpdated', (event) => {
  component.state.set('services', event.detail.services);
});

// Real-time messages update state
hermesService.addEventListener('messageReceived', (event) => {
  const message = event.detail.message;
  const messages = component.state.get('messages');
  component.state.set('messages', [message, ...messages].slice(0, maxMessageCount));
});

// Use state effects to update UI when state changes
component.utils.lifecycle.registerStateEffect(component, 
  ['services', 'registrySearch', 'registryTypeFilter'], 
  (state) => {
    renderServiceRegistry(
      state.services, 
      state.registrySearch, 
      state.registryTypeFilter
    );
  }
);

// Use transactions for related updates
const commit = component.state.transaction();
component.state.set('isPaused', true);
component.state.set('pauseReason', 'User paused');
component.state.set('pauseTimestamp', new Date().toISOString());
commit(); // Single notification for all three changes
```

### Form State and Validation

Manage form state with validation:

```javascript
// Initialize form state
component.state.set('form', {
  values: {
    username: '',
    email: '',
    password: ''
  },
  errors: {},
  isValid: false,
  isSubmitting: false
});

// Create input handlers
const inputHandlers = component.state.bindInputs({
  'username': 'form.values.username',
  'email': 'form.values.email',
  'password': 'form.values.password'
});

// Add input event listeners
component.$('#username').addEventListener('input', inputHandlers.username);
component.$('#email').addEventListener('input', inputHandlers.email);
component.$('#password').addEventListener('input', inputHandlers.password);

// Create validation effect
component.utils.lifecycle.registerStateEffect(component,
  ['form.values'],
  (state) => {
    const values = state.form.values;
    const errors = {};
    
    // Validate username
    if (!values.username) {
      errors.username = 'Username is required';
    }
    
    // Validate email
    if (!values.email) {
      errors.email = 'Email is required';
    } else if (!isValidEmail(values.email)) {
      errors.email = 'Invalid email format';
    }
    
    // Validate password
    if (!values.password) {
      errors.password = 'Password is required';
    } else if (values.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    }
    
    // Update state with validation results
    component.state.set({
      'form.errors': errors,
      'form.isValid': Object.keys(errors).length === 0
    });
  }
);

// Handle form submission
component.$('#submit-button').addEventListener('click', () => {
  if (!component.state.get('form.isValid')) {
    return;
  }
  
  component.state.set('form.isSubmitting', true);
  
  submitForm(component.state.get('form.values'))
    .then(() => {
      component.state.set({
        'form.isSubmitting': false,
        'form.values': { username: '', email: '', password: '' }
      });
    })
    .catch(error => {
      component.state.set({
        'form.isSubmitting': false,
        'form.submitError': error.message
      });
    });
});
```

### Cached Data

Cache and manage API data:

```javascript
// Initialize cache state
component.state.set('cache', {
  users: {
    data: null,
    lastFetched: null,
    isLoading: false,
    error: null
  },
  products: {
    data: null,
    lastFetched: null,
    isLoading: false,
    error: null
  }
});

// Create fetch function with caching
function fetchData(endpoint, cacheKey, forceRefresh = false) {
  const cache = component.state.get(`cache.${cacheKey}`);
  
  // Check if cache is valid (less than 5 minutes old)
  const cacheValid = cache.data && 
                     cache.lastFetched && 
                     (Date.now() - cache.lastFetched < 5 * 60 * 1000);
  
  // Return cached data if valid and not forcing refresh
  if (cacheValid && !forceRefresh) {
    return Promise.resolve(cache.data);
  }
  
  // Set loading state
  component.state.set(`cache.${cacheKey}.isLoading`, true);
  
  // Fetch new data
  return api.get(endpoint)
    .then(data => {
      component.state.set({
        [`cache.${cacheKey}.data`]: data,
        [`cache.${cacheKey}.lastFetched`]: Date.now(),
        [`cache.${cacheKey}.isLoading`]: false,
        [`cache.${cacheKey}.error`]: null
      });
      return data;
    })
    .catch(error => {
      component.state.set({
        [`cache.${cacheKey}.isLoading`]: false,
        [`cache.${cacheKey}.error`]: error.message
      });
      throw error;
    });
}

// Use cached data
function loadUsers() {
  fetchData('/api/users', 'users')
    .then(users => {
      renderUserList(users);
    })
    .catch(error => {
      showError(error);
    });
}
```

## Advanced Usage

### Custom State Middleware

Implement custom middleware for advanced state processing:

```javascript
// Initialize state manager with middleware
const stateManager = window.tektonUI.stateManager;

// Add logging middleware
stateManager._originalSetState = stateManager.setState;
stateManager.setState = function(namespace, updates, options = {}) {
  console.group(`State Update: ${namespace}`);
  console.log('Previous:', this.getState(namespace));
  console.log('Updates:', updates);
  
  const result = this._originalSetState(namespace, updates, options);
  
  console.log('New State:', this.getState(namespace));
  console.groupEnd();
  
  return result;
};
```

### Custom Persistence Adapters

Create custom persistence adapters:

```javascript
// Register a custom adapter for IndexedDB
window.tektonUI.statePersistence.registerAdapter('indexedDB', {
  _dbName: 'tektonState',
  _dbVersion: 1,
  _storeName: 'state',
  
  // Open or create database
  _openDB: function() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this._dbName, this._dbVersion);
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        db.createObjectStore(this._storeName);
      };
      
      request.onsuccess = (event) => {
        resolve(event.target.result);
      };
      
      request.onerror = (event) => {
        reject(event.target.error);
      };
    });
  },
  
  // Get value from storage
  get: async function(key) {
    try {
      const db = await this._openDB();
      return new Promise((resolve, reject) => {
        const transaction = db.transaction(this._storeName, 'readonly');
        const store = transaction.objectStore(this._storeName);
        const request = store.get(key);
        
        request.onsuccess = () => {
          resolve(request.result);
        };
        
        request.onerror = () => {
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('IndexedDB get error:', error);
      return null;
    }
  },
  
  // Save value to storage
  set: async function(key, value) {
    try {
      const db = await this._openDB();
      return new Promise((resolve, reject) => {
        const transaction = db.transaction(this._storeName, 'readwrite');
        const store = transaction.objectStore(this._storeName);
        const request = store.put(value, key);
        
        request.onsuccess = () => {
          resolve();
        };
        
        request.onerror = () => {
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('IndexedDB set error:', error);
    }
  },
  
  // Remove value from storage
  remove: async function(key) {
    try {
      const db = await this._openDB();
      return new Promise((resolve, reject) => {
        const transaction = db.transaction(this._storeName, 'readwrite');
        const store = transaction.objectStore(this._storeName);
        const request = store.delete(key);
        
        request.onsuccess = () => {
          resolve();
        };
        
        request.onerror = () => {
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('IndexedDB remove error:', error);
    }
  },
  
  // Check if key exists
  exists: async function(key) {
    try {
      const value = await this.get(key);
      return value !== undefined && value !== null;
    } catch (error) {
      return false;
    }
  }
});

// Use the custom adapter
stateManager.configurePersistence('largeDataNamespace', {
  type: 'indexedDB',
  key: 'tekton_large_data'
});
```

### State Time Travel

Implement time travel debugging (undo/redo):

```javascript
// Add time travel capabilities
function setupTimeTravel(stateManager) {
  // Track history
  const history = [];
  let currentIndex = -1;
  
  // Create wrapper for setState
  const originalSetState = stateManager.setState;
  stateManager.setState = function(namespace, updates, options = {}) {
    // Get current state before update
    const prevState = JSON.parse(JSON.stringify(this.getState(namespace)));
    
    // Apply the update
    const result = originalSetState.call(this, namespace, updates, options);
    
    // Don't track silent updates
    if (options.silent || options._timeTravel) {
      return result;
    }
    
    // Trim future history if we're not at the end
    if (currentIndex < history.length - 1) {
      history.splice(currentIndex + 1);
    }
    
    // Add to history
    history.push({
      namespace,
      prevState,
      updates
    });
    currentIndex = history.length - 1;
    
    return result;
  };
  
  // Add undo/redo methods
  stateManager.canUndo = function() {
    return currentIndex >= 0;
  };
  
  stateManager.canRedo = function() {
    return currentIndex < history.length - 1;
  };
  
  stateManager.undo = function() {
    if (!this.canUndo()) return false;
    
    const action = history[currentIndex];
    currentIndex--;
    
    // Restore previous state
    this.setState(action.namespace, action.prevState, { 
      _timeTravel: true,
      silent: false 
    });
    
    return true;
  };
  
  stateManager.redo = function() {
    if (!this.canRedo()) return false;
    
    currentIndex++;
    const action = history[currentIndex];
    
    // Apply the update again
    this.setState(action.namespace, action.updates, { 
      _timeTravel: true,
      silent: false 
    });
    
    return true;
  };
  
  return {
    undo: () => stateManager.undo(),
    redo: () => stateManager.redo(),
    canUndo: () => stateManager.canUndo(),
    canRedo: () => stateManager.canRedo(),
    getHistory: () => history.slice(),
    clearHistory: () => {
      history.length = 0;
      currentIndex = -1;
    }
  };
}

// Use time travel
const timeTravel = setupTimeTravel(window.tektonUI.stateManager);

// Create undo/redo buttons
undoButton.addEventListener('click', () => {
  timeTravel.undo();
  undoButton.disabled = !timeTravel.canUndo();
  redoButton.disabled = !timeTravel.canRedo();
});

redoButton.addEventListener('click', () => {
  timeTravel.redo();
  undoButton.disabled = !timeTravel.canUndo();
  redoButton.disabled = !timeTravel.canRedo();
});
```