# Clean Slate UI Implementation Guide

This document outlines the clean slate approach for implementing UI components in the Tekton system. It explains the architecture decisions, patterns, and best practices established during the Clean Slate Sprint.

## Architecture Overview

The clean slate architecture focuses on:

1. **Component Isolation** - Each UI component is isolated with its own CSS scope and JavaScript functionality
2. **BEM Naming Convention** - Using Block__Element--Modifier pattern for CSS classes
3. **Minimal Component Loading** - Simple, direct HTML injection instead of Shadow DOM
4. **Direct DOM Manipulation** - Component scripts directly modify their own DOM elements only
5. **Proper Container Boundaries** - Components are contained within a RIGHT PANEL container

## Component Structure

Each component follows this standard structure:

### File Organization

```
/Hephaestus/ui/
  /components/
    /component-name/
      component-name-component.html  # Component HTML + CSS
  /scripts/
    /component-name/
      component-name-component.js    # Component JavaScript
```

### HTML Structure

```html
<!-- Component-Name Component -->
<div class="component-name">
  <!-- Component Header -->
  <div class="component-name__header">
    <div class="component-name__title-container">
      <img src="/images/icon.jpg" alt="Component" class="component-name__icon">
      <h2 class="component-name__title">
        <span class="component-name__title-main">Component Name</span>
        <span class="component-name__title-sub">Description</span>
      </h2>
    </div>
  </div>
  
  <!-- Menu Bar with Tab Navigation -->
  <div class="component-name__menu-bar">
    <div class="component-name__tabs">
      <div class="component-name__tab component-name__tab--active" data-tab="tab1">
        <span class="component-name__tab-label">Tab 1</span>
      </div>
      <div class="component-name__tab" data-tab="tab2">
        <span class="component-name__tab-label">Tab 2</span>
      </div>
    </div>
    <div class="component-name__actions">
      <!-- Action buttons -->
    </div>
  </div>
  
  <!-- Component Content Area -->
  <div class="component-name__content">
    <!-- Tab Panels -->
    <div id="tab1-panel" class="component-name__panel component-name__panel--active">
      <!-- Tab 1 content -->
    </div>
    <div id="tab2-panel" class="component-name__panel">
      <!-- Tab 2 content -->
    </div>
  </div>
  
  <!-- Optional Component Footer -->
  <div class="component-name__footer">
    <!-- Footer content -->
  </div>
</div>

<!-- Component Styles -->
<style>
  /* Component styles using BEM naming convention */
  .component-name {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    background-color: var(--bg-primary, #1e1e2e);
    color: var(--text-primary, #f0f0f0);
  }
  
  .component-name__header {
    /* Header styles */
  }
  
  .component-name__title {
    /* Title styles */
  }
  
  /* Chat Panel Structure (Important for proper scrolling) */
  .component-name__panel {
    position: relative; /* Needed for absolute positioning of elements */
    overflow: hidden; /* Prevent double scrollbars */
  }

  .component-name__chat-messages {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 70px; /* Height of the footer */
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
  }

  .component-name__footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 70px;
    padding: 12px 16px;
    background-color: var(--bg-secondary, #252535);
    border-top: 1px solid var(--border-color, #444444);
  }

  /* Additional component-specific styles */
</style>
```

### JavaScript Structure

```javascript
/**
 * Component-Name Component
 * Description of component functionality
 */

class ComponentNameComponent {
  constructor() {
    this.state = {
      initialized: false,
      activeTab: 'tab1', // Default tab
      tab1Loaded: false,
      tab2Loaded: false
    };
  }
  
  /**
   * Initialize the component
   */
  init() {
    console.log('Initializing Component-Name component');

    // If already initialized, just activate
    if (this.state.initialized) {
      console.log('Component already initialized, just activating');
      return this;
    }

    // Setup component functionality
    this.setupTabs();
    this.setupFeature1();
    this.setupFeature2();

    // Mark as initialized
    this.state.initialized = true;

    console.log('Component-Name component initialized');
    return this;
  }
  
  /**
   * Set up tab switching functionality
   */
  setupTabs() {
    console.log('Setting up Component-Name tabs');

    // Find component container
    const container = document.querySelector('.component-name');
    if (!container) {
      console.error('Component container not found!');
      return;
    }

    // Scope all queries to container using BEM class names
    const tabs = container.querySelectorAll('.component-name__tab');
    const panels = container.querySelectorAll('.component-name__panel');

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        // Update active tab
        tabs.forEach(t => t.classList.remove('component-name__tab--active'));
        tab.classList.add('component-name__tab--active');

        // Show active panel
        const panelId = tab.getAttribute('data-tab') + '-panel';
        panels.forEach(panel => {
          panel.style.display = 'none';
          panel.classList.remove('component-name__panel--active');
        });

        // Use container-scoped query instead of global getElementById
        const activePanel = container.querySelector(`#${panelId}`);
        if (activePanel) {
          activePanel.style.display = 'block';
          activePanel.classList.add('component-name__panel--active');
        }

        // Update the active tab in state
        this.state.activeTab = tab.getAttribute('data-tab');

        // Load tab-specific content if needed
        this.loadTabContent(this.state.activeTab);
      });
    });
  }
  
  /**
   * Load content specific to a tab
   * @param {string} tabId - The ID of the tab to load content for
   */
  loadTabContent(tabId) {
    console.log(`Loading content for ${tabId} tab`);
    
    switch (tabId) {
      case 'tab1':
        if (!this.state.tab1Loaded) {
          this.initializeTab1();
          this.state.tab1Loaded = true;
        }
        break;
      case 'tab2':
        if (!this.state.tab2Loaded) {
          this.initializeTab2();
          this.state.tab2Loaded = true;
        }
        break;
    }
  }
  
  // Additional component-specific methods
}

// Create global instance
window.componentNameComponent = new ComponentNameComponent();

// Add handler to component activation
document.addEventListener('DOMContentLoaded', function() {
  if (window.componentNameComponent) {
    window.componentNameComponent.init();
  }
});
```

## Component Loader

The minimal component loader we implemented is responsible for:

1. Loading component HTML content
2. Executing component scripts
3. Managing component lifecycle
4. Handling component switching

```javascript
class MinimalLoader {
  constructor() {
    // Standard component paths
    this.componentPaths = {
      'test': '/components/test/test-component.html',
      'athena': '/components/athena/athena-component.html',
      'ergon': '/components/ergon/ergon-component.html'
      // Add more components as needed
    };
    
    // Keep track of the current component
    this.currentComponent = null;
  }
  
  async loadComponent(componentId) {
    console.log(`MinimalLoader: Loading component ${componentId}`);
    
    // Get the RIGHT PANEL container
    const container = document.getElementById('html-panel');
    if (!container) {
      console.error('MinimalLoader: RIGHT PANEL (html-panel) not found');
      return null;
    }
    
    // Check for reloading the same component
    if (this.currentComponent === componentId) {
      console.log(`MinimalLoader: ${componentId} is already loaded, skipping`);
      return;
    }
    
    try {
      // Show loading indicator
      container.innerHTML = `<div style="padding: 20px; text-align: center;">Loading ${componentId}...</div>`;
      
      // Determine component path
      const componentPath = this.componentPaths[componentId] || `/components/${componentId}/${componentId}-component.html`;
      
      // Load the HTML
      const response = await fetch(componentPath);
      if (!response.ok) {
        throw new Error(`Failed to load component: ${response.status} ${response.statusText}`);
      }
      
      const html = await response.text();
      
      // Display the component HTML directly in the container
      container.innerHTML = html;
      
      // Update current component
      this.currentComponent = componentId;
      
      // Make sure the container is visible
      container.style.display = 'block';
      
      // Run any scripts in the component
      const scripts = container.querySelectorAll('script');
      scripts.forEach(script => {
        const newScript = document.createElement('script');
        newScript.textContent = script.textContent;
        document.head.appendChild(newScript);
      });
      
      // Initialize component if it has a global instance
      setTimeout(() => {
        const componentInstance = window[`${componentId}Component`];
        if (componentInstance && typeof componentInstance.init === 'function') {
          console.log(`MinimalLoader: Initializing ${componentId} component`);
          componentInstance.init();
        }
      }, 100);
      
      console.log(`MinimalLoader: ${componentId} loaded successfully`);
    } catch (error) {
      console.error(`MinimalLoader: Error loading ${componentId}:`, error);
      container.innerHTML = `
        <div style="padding: 20px; margin: 20px; border: 1px solid #dc3545; border-radius: 8px;">
          <h3 style="color: #dc3545;">Error Loading ${componentId}</h3>
          <p>${error.message}</p>
        </div>
      `;
    }
  }
}

// Create a global instance
window.minimalLoader = new MinimalLoader();
```

## BEM Naming Convention

We've implemented a strict Block Element Modifier (BEM) naming convention for CSS classes to provide namespace isolation for components:

- **Block**: The component name (e.g., `athena`)
- **Element**: Parts within the component, separated by `__` (e.g., `athena__header`)
- **Modifier**: Variations of elements, separated by `--` (e.g., `athena__tab--active`)

### Benefits

1. **Namespace Isolation**: Each component's CSS is isolated from others
2. **Clear Hierarchy**: The relationship between blocks and elements is clear
3. **Reusability**: Components can be moved across the application without style conflicts
4. **Maintenance**: Easy to identify which styles belong to which component

### Example

```css
/* Block */
.athena {
  display: flex;
  flex-direction: column;
}

/* Element */
.athena__header {
  display: flex;
  align-items: center;
}

/* Element */
.athena__tab {
  cursor: pointer;
}

/* Element with modifier */
.athena__tab--active {
  border-bottom: 2px solid #7B1FA2;
}
```

## Implementation Process

When implementing a new component or converting an existing one to the clean slate architecture:

1. **Create Component HTML/CSS**:
   - Use BEM naming for all CSS classes
   - Include all styles within the component HTML file
   - Structure the component with header, menu bar, content area, and footer as needed

2. **Create Component JavaScript**:
   - Scope all DOM queries to the component container
   - Implement proper initialization with state tracking
   - Add tab navigation and content loading if needed
   - Add component-specific functionality

3. **Register the Component**:
   - Add the component path to the component loader
   - Ensure the component can be loaded independently

4. **Test the Component**:
   - Verify proper display in the RIGHT PANEL
   - Test all functionality
   - Ensure there's no interference with other components

## Implementation Examples

The initial implementation examples include:

1. **Test Component**: A minimalist example for testing component loading and display
2. **Athena Component**: A full-featured knowledge graph component with tabs, forms, and interactive features
3. **Ergon Component**: An agent management and LLM integration interface with complex modal forms and chat functionality

These components demonstrate the core principles of the clean slate architecture and can be used as references for implementing additional components.

## Lessons Learned

1. **Direct HTML Injection**: Shadow DOM adds unnecessary complexity - direct HTML injection provides better compatibility and simpler debugging
2. **BEM Naming**: Strict BEM naming convention is essential for component isolation
3. **Component Scoping**: All DOM queries should be scoped to the component container
4. **Minimal Loading**: Simple component loading is more reliable than complex architectures
5. **Proper Initialization**: Components should track their initialization state and handle re-activation gracefully

## Future Improvements

1. **Component Registry**: Develop a central registry for all components
2. **State Management**: Implement a standardized approach to state management
3. **Theme Consistency**: Ensure consistent theme variables across components
4. **Documentation**: Generate comprehensive documentation for all components
5. **Testing Framework**: Add automated tests for component functionality

By following these guidelines and examples, you can create well-isolated, maintainable UI components for the Tekton system.