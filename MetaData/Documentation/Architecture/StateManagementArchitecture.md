# State Management Architecture

**Last Updated:** May 10, 2025

## Overview

This document outlines the architecture for the State Management Pattern to be implemented in Phase 7 of the Tekton project. The State Management system will provide a consistent, reactive approach to managing application state across components while supporting persistence, synchronization, and inter-component communication.

## Table of Contents

1. [Architecture Goals](#architecture-goals)
2. [Core Concepts](#core-concepts)
3. [State Management Layers](#state-management-layers)
4. [Component Integration](#component-integration)
5. [Persistence Strategy](#persistence-strategy)
6. [Synchronization Mechanisms](#synchronization-mechanisms)
7. [Implementation Approach](#implementation-approach)
8. [Migration Strategy](#migration-strategy)
9. [Implementation Timeline](#implementation-timeline)

## Architecture Goals

The State Management architecture aims to achieve the following goals:

1. **Unified State Model**: Provide a consistent approach to state management across the entire application
2. **Component Integration**: Seamlessly integrate with the Shadow DOM component architecture
3. **Reactivity**: Support reactive updates to UI when state changes
4. **Persistence**: Enable state persistence across page reloads and sessions
5. **Synchronization**: Allow state synchronization across components and instances
6. **Performance**: Minimize performance impact while providing rich state management features
7. **Type Safety**: Support TypeScript interfaces for state structures
8. **Debugging**: Enable debugging and visualization of state changes

## Core Concepts

### State Store

The central concept is a hierarchical state store that manages both global and component-specific state:

```
StateStore
├── Global State (application-wide)
│   ├── user
│   ├── theme
│   ├── settings
│   └── system
└── Component State (per component)
    ├── rhetor
    ├── budget
    ├── terma
    └── [other components]
```

### State Actions

State is modified through actions that describe the change:

```typescript
interface StateAction {
  type: string;          // Action identifier
  payload?: any;         // Action data
  path: string[];        // Path to state node
  componentId?: string;  // Source component (optional)
  meta?: {               // Additional metadata
    timestamp: number;
    source: 'user' | 'system' | 'api';
    transactionId?: string;
  };
}
```

### State Selectors

Components access state through selectors that describe what portion of state they need:

```typescript
function selectTheme(state) {
  return state.global.theme;
}

function selectComponentConfig(state, componentId) {
  return state.components[componentId]?.config;
}
```

### State Subscribers

Components can subscribe to state changes with selector functions:

```typescript
const unsubscribe = stateManager.subscribe(
  selectTheme,
  (newTheme, oldTheme) => {
    updateTheme(newTheme);
  }
);
```

## State Management Layers

### 1. Core State Store

The foundation of the architecture is a reactive state store:

```javascript
class StateStore {
  constructor(initialState = {}) {
    this.state = initialState;
    this.listeners = [];
    this.middlewares = [];
  }
  
  // Get current state
  getState() {
    return this.state;
  }
  
  // Update state with an action
  dispatch(action) {
    // Apply middlewares
    const processedAction = this.applyMiddlewares(action);
    
    // Previous state for comparison
    const prevState = this.state;
    
    // Apply state update
    this.state = this.reducer(this.state, processedAction);
    
    // Notify subscribers
    this.notifyListeners(this.state, prevState, processedAction);
    
    return processedAction;
  }
  
  // Subscribe to state changes
  subscribe(selector, listener) {
    const subscription = { selector, listener };
    this.listeners.push(subscription);
    
    // Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter(l => l !== subscription);
    };
  }
  
  // Internal methods
  reducer(state, action) {
    // State update logic based on action
  }
  
  notifyListeners(newState, prevState, action) {
    this.listeners.forEach(({ selector, listener }) => {
      const newSelection = selector(newState);
      const prevSelection = selector(prevState);
      
      // Only notify if selection changed
      if (!isEqual(newSelection, prevSelection)) {
        listener(newSelection, prevSelection, action);
      }
    });
  }
  
  applyMiddlewares(action) {
    return this.middlewares.reduce((act, middleware) => {
      return middleware(act, this.state) || act;
    }, action);
  }
  
  // Add middleware for pre-processing actions
  addMiddleware(middleware) {
    this.middlewares.push(middleware);
    return this;
  }
}
```

### 2. State Persistence Layer

The persistence layer handles saving and restoring state:

```javascript
class StatePersistenceManager {
  constructor(stateStore, options = {}) {
    this.store = stateStore;
    this.options = {
      storage: localStorage,
      key: 'tekton_state',
      debounce: 500,
      whitelist: ['global.settings', 'global.theme'],
      ...options
    };
    
    this.initialize();
  }
  
  initialize() {
    // Load persisted state on initialization
    this.loadPersistedState();
    
    // Set up save debounce
    this.debouncedSave = debounce(this.saveState.bind(this), this.options.debounce);
    
    // Subscribe to state changes
    this.unsubscribe = this.store.subscribe(
      state => state, // Full state selector
      this.handleStateChange.bind(this)
    );
  }
  
  handleStateChange(newState) {
    this.debouncedSave(newState);
  }
  
  saveState(state) {
    // Extract only whitelisted paths
    const persistedState = this.extractPersistedState(state);
    
    // Save to storage
    try {
      const serialized = JSON.stringify(persistedState);
      this.options.storage.setItem(this.options.key, serialized);
    } catch (error) {
      console.error('Error persisting state:', error);
    }
  }
  
  loadPersistedState() {
    try {
      const serialized = this.options.storage.getItem(this.options.key);
      if (serialized) {
        const persistedState = JSON.parse(serialized);
        
        // Dispatch action to restore state
        this.store.dispatch({
          type: '@@state/RESTORE',
          payload: persistedState
        });
      }
    } catch (error) {
      console.error('Error loading persisted state:', error);
    }
  }
  
  extractPersistedState(state) {
    // Extract only whitelisted paths
    // Implementation depends on state structure
  }
  
  destroy() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  }
}
```

### 3. State Synchronization Layer

The synchronization layer handles sharing state across components, tabs, or sessions:

```javascript
class StateSyncManager {
  constructor(stateStore, options = {}) {
    this.store = stateStore;
    this.options = {
      channel: 'tekton_state_sync',
      whitelist: ['global.settings', 'global.user'],
      ...options
    };
    
    this.initialize();
  }
  
  initialize() {
    // Subscribe to state changes
    this.unsubscribe = this.store.subscribe(
      state => state, // Full state selector
      this.handleStateChange.bind(this)
    );
    
    // Listen for broadcast channel messages
    this.channel = new BroadcastChannel(this.options.channel);
    this.channel.addEventListener('message', this.handleSyncMessage.bind(this));
  }
  
  handleStateChange(newState, oldState, action) {
    // Don't sync internal or already synced actions
    if (action.type.startsWith('@@sync/') || action.meta?.sync) {
      return;
    }
    
    // Check if action affects whitelisted paths
    if (this.shouldSyncAction(action)) {
      // Send sync message
      this.channel.postMessage({
        action,
        timestamp: Date.now(),
        source: 'state-sync'
      });
    }
  }
  
  handleSyncMessage(event) {
    const { action, timestamp } = event.data;
    
    if (!action) return;
    
    // Dispatch synced action to store
    this.store.dispatch({
      ...action,
      meta: {
        ...(action.meta || {}),
        sync: true,
        timestamp
      }
    });
  }
  
  shouldSyncAction(action) {
    // Check if action affects whitelisted paths
    // Implementation depends on action structure
  }
  
  destroy() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
    
    if (this.channel) {
      this.channel.close();
    }
  }
}
```

### 4. State Development Tools

Tools for debugging and visualizing state changes:

```javascript
class StateDevTools {
  constructor(stateStore) {
    this.store = stateStore;
    this.history = [];
    this.maxHistory = 50;
    
    this.initialize();
  }
  
  initialize() {
    // Subscribe to state changes
    this.unsubscribe = this.store.subscribe(
      state => state,
      this.trackStateChange.bind(this)
    );
    
    // Register devtools middleware
    this.store.addMiddleware(this.devToolsMiddleware.bind(this));
    
    // Expose API for developer console
    window.__TEKTON_STATE_DEVTOOLS__ = {
      getState: () => this.store.getState(),
      getHistory: () => this.history,
      dispatch: (action) => this.store.dispatch(action),
      jumpToState: (index) => this.jumpToState(index)
    };
  }
  
  trackStateChange(newState, oldState, action) {
    // Add to history
    this.history.push({
      action,
      state: { ...newState },
      timestamp: Date.now()
    });
    
    // Limit history size
    if (this.history.length > this.maxHistory) {
      this.history.shift();
    }
    
    // Log to console if enabled
    if (this.options?.logActions) {
      console.log('Action:', action.type, action);
      console.log('New State:', newState);
    }
  }
  
  devToolsMiddleware(action) {
    // Handle special devtools actions
    if (action.type === '@@devtools/JUMP_TO_STATE') {
      // Implementation to restore historical state
      return {
        type: '@@devtools/STATE_RESTORED',
        payload: action.payload
      };
    }
    
    return action;
  }
  
  jumpToState(index) {
    if (index >= 0 && index < this.history.length) {
      const targetState = this.history[index].state;
      
      this.store.dispatch({
        type: '@@devtools/JUMP_TO_STATE',
        payload: targetState
      });
    }
  }
  
  destroy() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
    
    delete window.__TEKTON_STATE_DEVTOOLS__;
  }
}
```

## Component Integration

The State Management system integrates with the Shadow DOM component architecture as follows:

### 1. Component State Hook

Components connect to the state store through a state hook:

```javascript
function useComponentState(component, initialState = {}) {
  // Register component state
  stateManager.registerComponent(component.id, initialState);
  
  // Add component cleanup
  component.registerCleanup(() => {
    stateManager.unregisterComponent(component.id);
  });
  
  // Return component state API
  return {
    getState: () => stateManager.getComponentState(component.id),
    
    setState: (updates) => stateManager.dispatch({
      type: `${component.id}/setState`,
      payload: updates,
      path: ['components', component.id]
    }),
    
    subscribe: (selector, listener) => {
      // Wrap selector to scope to component state
      const wrappedSelector = (state) => {
        const componentState = state.components[component.id];
        return selector(componentState);
      };
      
      // Subscribe with wrapped selector
      return stateManager.subscribe(wrappedSelector, listener);
    },
    
    dispatch: (action) => stateManager.dispatch({
      ...action,
      componentId: component.id
    })
  };
}
```

### 2. Component Implementation

Components use the state hook as follows:

```javascript
(function(component) {
  'use strict';
  
  // Component state
  const state = useComponentState(component, {
    loading: false,
    items: [],
    selectedId: null,
    error: null
  });
  
  // Initialize component
  function initComponent() {
    // Set up event listeners
    setupEventListeners();
    
    // Subscribe to state changes
    state.subscribe(
      s => s.selectedId,
      (newId, oldId) => {
        updateSelectedItem(newId);
      }
    );
    
    // Load initial data
    loadData();
  }
  
  // Load data from API
  async function loadData() {
    // Update loading state
    state.setState({ loading: true, error: null });
    
    try {
      const response = await fetch('/api/items');
      const items = await response.json();
      
      // Update state with items
      state.setState({ items, loading: false });
    } catch (error) {
      state.setState({ 
        error: error.message,
        loading: false 
      });
    }
  }
  
  // Handle item selection
  function handleItemSelect(id) {
    state.setState({ selectedId: id });
  }
  
  // Set up event listeners
  function setupEventListeners() {
    component.on('click', '.item', function() {
      const id = this.dataset.id;
      handleItemSelect(id);
    });
    
    component.on('click', '.refresh-button', function() {
      loadData();
    });
  }
  
  // Update UI based on selected item
  function updateSelectedItem(id) {
    // Remove active class from all items
    component.$$('.item').forEach(item => {
      item.classList.remove('item--active');
    });
    
    // Add active class to selected item
    if (id) {
      const selectedItem = component.$(`.item[data-id="${id}"]`);
      if (selectedItem) {
        selectedItem.classList.add('item--active');
      }
    }
  }
  
  // Initialize the component
  initComponent();
  
})(component);
```

### 3. Global State Access

Components can access global state through the state manager:

```javascript
// Get global theme
const theme = stateManager.select(state => state.global.theme);

// Subscribe to theme changes
const unsubscribeTheme = stateManager.subscribe(
  state => state.global.theme,
  (newTheme) => updateTheme(newTheme)
);

// Update global state
stateManager.dispatch({
  type: 'theme/set',
  payload: 'dark',
  path: ['global', 'theme']
});
```

## Persistence Strategy

The State Management system supports several persistence strategies:

### 1. Local Storage

The default persistence uses localStorage for cross-session persistence:

```javascript
const persistenceManager = new StatePersistenceManager(stateStore, {
  storage: localStorage,
  key: 'tekton_app_state',
  whitelist: [
    'global.theme',
    'global.settings',
    'components.profile'
  ]
});
```

### 2. Session Storage

For session-only persistence:

```javascript
const sessionPersistence = new StatePersistenceManager(stateStore, {
  storage: sessionStorage,
  key: 'tekton_session_state',
  whitelist: [
    'components.rhetor.history',
    'components.terma.commandHistory'
  ]
});
```

### 3. IndexedDB

For larger or more complex state:

```javascript
const idbPersistence = new IndexedDBPersistenceManager(stateStore, {
  dbName: 'tekton_state',
  storeName: 'app_state',
  whitelist: [
    'components.codex.codebase',
    'components.engram.memories'
  ]
});
```

### 4. Server Synchronization

For user-specific state that should persist across devices:

```javascript
const serverSync = new ServerStateSyncManager(stateStore, {
  apiUrl: '/api/state',
  whitelist: [
    'global.user.preferences',
    'components.profile.settings'
  ],
  syncInterval: 60000 // 1 minute
});
```

## Synchronization Mechanisms

The system supports several synchronization mechanisms:

### 1. BroadcastChannel API

For cross-tab synchronization:

```javascript
const tabSync = new BroadcastChannelSyncManager(stateStore, {
  channel: 'tekton_state_sync',
  whitelist: [
    'global.theme',
    'global.settings'
  ]
});
```

### 2. WebSocket

For real-time synchronization with server and other clients:

```javascript
const wsSync = new WebSocketSyncManager(stateStore, {
  url: 'wss://api.example.com/state-sync',
  reconnectInterval: 5000,
  whitelist: [
    'components.chat.messages',
    'components.collaboration.cursors'
  ]
});
```

### 3. Service Workers

For offline support and background synchronization:

```javascript
const workerSync = new ServiceWorkerSyncManager(stateStore, {
  scriptUrl: '/state-sync-worker.js',
  syncTag: 'state-sync',
  whitelist: [
    'components.tasks.items',
    'components.notes.content'
  ]
});
```

## Implementation Approach

The State Management system will be implemented in the following phases:

### Phase 1: Core State Store

1. Implement the core StateStore class
2. Create state selectors and action creators
3. Implement basic component integration
4. Add development tools for debugging

### Phase 2: Component Integration

1. Create the component state hook
2. Update component loader to inject state hook
3. Implement component state initialization
4. Migrate one component (Settings) to use state management

### Phase 3: Persistence Implementation

1. Implement the StatePersistenceManager
2. Add persistence options for different storage types
3. Create whitelisting and path resolution
4. Implement state restoration on page load

### Phase 4: Synchronization Implementation

1. Create the BroadcastChannelSyncManager for cross-tab sync
2. Implement WebSocketSyncManager for server sync
3. Add conflict resolution strategies
4. Support offline operation and reconnection

### Phase 5: Migration and Refinement

1. Migrate remaining components to use state management
2. Refine APIs based on usage patterns
3. Optimize performance for large state trees
4. Enhance developer tools and documentation

## Migration Strategy

The migration to the new State Management Pattern will follow these steps:

1. **Initial Setup**: Implement core state management infrastructure without changing components
2. **Parallel Operation**: Run both old and new state management in parallel
3. **Component Migration**: Migrate components one by one, starting with simpler ones
4. **Testing and Validation**: Test each migrated component thoroughly
5. **Service Migration**: Update services to use state management
6. **Legacy Removal**: Remove old state management code after all components are migrated

## Implementation Timeline

| Phase | Description | Estimated Duration | Target Completion |
|-------|-------------|-------------------|-------------------|
| 1 | Core State Store | 1 week | May 17, 2025 |
| 2 | Component Integration | 1 week | May 24, 2025 |
| 3 | Persistence Implementation | 1 week | May 31, 2025 |
| 4 | Synchronization Implementation | 1 week | June 7, 2025 |
| 5 | Migration and Refinement | 2 weeks | June 21, 2025 |

## See Also

- [Component Isolation Architecture](./ComponentIsolationArchitecture.md) - Shadow DOM isolation architecture
- [UI Component Communication](./UIComponentCommunication.md) - Component communication patterns
- [Component Integration Patterns](./ComponentIntegrationPatterns.md) - Standardized patterns for component integration