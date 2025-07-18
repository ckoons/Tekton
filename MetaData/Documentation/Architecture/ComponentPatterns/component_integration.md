# Hephaestus Component Integration Guide

This document explains how to properly integrate new components into the Hephaestus UI system.

## Component Integration Process

### 1. Component File Structure

Create the necessary directories and files for your component:

```
Hephaestus/
  ui/
    components/
      mycomponent/          # Directory for your component HTML
        mycomponent.html    # Main component HTML template
    scripts/
      mycomponent/          # Directory for your component JS
        mycomponent.js      # Main component JavaScript
    styles/
      mycomponent/          # Directory for your component CSS
        mycomponent.css     # Main component CSS
```

### 2. Register Your Component

Add your component to the component registry JSON file at `ui/server/component_registry.json`:

```json
{
  "components": [
    // ... other components
    {
      "id": "mycomponent",
      "name": "My Component",
      "description": "Description of my component",
      "icon": "🔧",
      "defaultMode": "html",
      "capabilities": ["feature1", "feature2"],
      "componentPath": "components/mycomponent/mycomponent.html",
      "scripts": [
        "scripts/mycomponent/mycomponent.js"
      ],
      "styles": [
        "styles/mycomponent/mycomponent.css"
      ]
    }
  ]
}
```

### 3. Add to Navigation Menu

Add your component to the navigation menu in `ui/index.html`:

```html
<li class="nav-item" data-component="mycomponent">
  <span class="nav-label">My Component - Description</span>
  <span class="status-indicator"></span>
</li>
```

### 4. Dynamic Component Loading

The UI Manager will now automatically load your component based on the registry data. When a user clicks on your component tab, the UI Manager:

1. Checks the registry for your component definition
2. Creates a container for your component
3. Loads your HTML template into the container
4. Loads associated stylesheets
5. Loads associated scripts
6. Activates the HTML panel to display your component

## Troubleshooting Component Loading

If your component doesn't load properly:

1. Check browser console for loading errors
2. Verify that all paths in the registry are correct
3. Make sure your HTML, CSS, and JS files exist in the correct locations
4. Restart the Hephaestus server to clear any cached files
5. Use the Network tab in browser dev tools to see which files are failing to load

## Component Best Practices

1. **HTML Structure**:
   - Use a single root element for your component
   - Add a unique class or ID to your root element
   - Follow the tab pattern for multi-view components

2. **CSS Structure**:
   - Follow the BEM naming convention for CSS classes
   - Use CSS variables for theming compatibility
   - Include responsive design for different viewport sizes

3. **JavaScript Structure**:
   - Initialize your component with an event listener for DOMContentLoaded
   - Use namespaced objects to avoid global namespace pollution
   - Register event handlers for interactive elements
   - Connect to Tekton services as needed

## Example Component HTML

```html
<!-- My Component UI Template -->
<div class="my-component-container">
  <!-- Tabbed Navigation -->
  <div class="my-component-tabs">
    <div class="tab-button active" data-tab="feature1">Feature 1</div>
    <div class="tab-button" data-tab="feature2">Feature 2</div>
    <div class="tab-button" data-tab="settings">Settings</div>
  </div>

  <!-- Feature 1 Tab Content -->
  <div class="tab-content active" id="feature1-content">
    <div class="my-component-section-header">
      <h2>Feature 1</h2>
      <div class="my-component-controls">
        <button class="control-button primary-button" id="feature1-action">Action</button>
      </div>
    </div>
    
    <!-- Feature 1 content goes here -->
    <div class="feature1-container">
      <!-- Feature 1 UI elements -->
    </div>
  </div>

  <!-- Feature 2 Tab Content -->
  <div class="tab-content" id="feature2-content">
    <!-- Feature 2 content -->
  </div>

  <!-- Settings Tab Content -->
  <div class="tab-content" id="settings-content">
    <!-- Settings content -->
  </div>
</div>
```

## Example Component JavaScript

```javascript
/**
 * My Component JavaScript
 * Controller for the My Component UI component in Hephaestus
 */

// Initialize component
document.addEventListener('DOMContentLoaded', () => {
  initMyComponent();
});

/**
 * Initialize the My Component
 */
function initMyComponent() {
  setupTabNavigation();
  initFeature1();
  initFeature2();
  initSettings();
}

/**
 * Set up tab navigation for the component
 */
function setupTabNavigation() {
  const tabButtons = document.querySelectorAll('.my-component-tabs .tab-button');
  const tabContents = document.querySelectorAll('.tab-content');
  
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const tabName = button.getAttribute('data-tab');
      
      // Deactivate all tabs
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabContents.forEach(content => content.classList.remove('active'));
      
      // Activate selected tab
      button.classList.add('active');
      document.getElementById(`${tabName}-content`).classList.add('active');
    });
  });
}
```

## Example Component CSS

```css
/* My Component Styles */

.my-component-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  font-family: var(--font-family-sans);
}

/* Tabs Navigation */
.my-component-tabs {
  display: flex;
  background-color: var(--bg-color-secondary);
  border-bottom: 1px solid var(--border-color);
}

.my-component-tabs .tab-button {
  padding: var(--spacing-md);
  cursor: pointer;
  border-bottom: 3px solid transparent;
  color: var(--text-color-secondary);
  font-weight: 500;
  transition: all 0.3s ease;
}

.my-component-tabs .tab-button:hover {
  color: var(--text-color-primary);
  background-color: rgba(var(--primary-rgb), 0.05);
}

.my-component-tabs .tab-button.active {
  color: var(--text-color-primary);
  border-bottom-color: var(--color-primary);
  background-color: rgba(var(--primary-rgb), 0.05);
}

/* Tab Content */
.tab-content {
  display: none;
  padding: var(--spacing-lg);
  flex: 1;
  overflow-y: auto;
}

.tab-content.active {
  display: block;
}
```

## Connecting to Tekton Services

To connect your component to Tekton services:

1. **WebSocket Connection**:
   ```javascript
   // Use the existing WebSocket manager
   if (window.websocketManager) {
     websocketManager.sendMessage({
       type: "COMMAND",
       source: "UI",
       target: "mycomponent",
       timestamp: new Date().toISOString(),
       payload: {
         command: "process_command",
         data: { /* command data */ }
       }
     });
   }
   ```

2. **Fetch API for HTTP Requests**:
   ```javascript
   // Make HTTP requests to backend services
   fetch('/api/mycomponent/data')
     .then(response => response.json())
     .then(data => {
       // Process data
     })
     .catch(error => {
       console.error('Error fetching data:', error);
     });
   ```