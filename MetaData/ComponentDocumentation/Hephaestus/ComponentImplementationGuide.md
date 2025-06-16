# Tekton Component Implementation Guide

## Overview
This guide outlines best practices for implementing UI components in the Tekton Hephaestus system following the Clean Slate approach. Following these patterns ensures components are isolated, maintainable, and function correctly.

## Component Structure

Each component should follow this structure:

```
/components/
  /{component-name}/
    {component-name}-component.html  # HTML and CSS 
/scripts/
  /{component-name}/
    {component-name}-component.js    # JavaScript implementation
```

## HTML & CSS Implementation

```html
<!-- {Component} Component - {Brief description} -->
<div class="{component}">
    <!-- Component Header -->
    <div class="{component}__header">
        <!-- Header content -->
    </div>
    
    <!-- Tab Navigation (if needed) -->
    <div class="{component}__menu-bar">
        <div class="{component}__tabs">
            <div class="{component}__tab {component}__tab--active" data-tab="tab1" onclick="{component}_switchTab('tab1'); return false;">
                <span class="{component}__tab-label">Tab 1</span>
            </div>
            <div class="{component}__tab" data-tab="tab2" onclick="{component}_switchTab('tab2'); return false;">
                <span class="{component}__tab-label">Tab 2</span>
            </div>
            <!-- Additional tabs... -->
        </div>
    </div>
    
    <!-- Content Area -->
    <div class="{component}__content">
        <!-- Tab Panels -->
        <div id="tab1-panel" class="{component}__panel {component}__panel--active">
            <!-- Panel content -->
        </div>
        <!-- Additional panels... -->
    </div>
    
    <!-- Footer (if needed) -->
    <div class="{component}__footer">
        <!-- Footer content -->
    </div>
</div>

<!-- Component Styles -->
<style>
    /* Component styles using BEM naming convention */
    .{component} {
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
    }
    
    /* Panel visibility control - REQUIRED for tab switching */
    .{component}__panel {
        display: none;
        height: 100%;
        width: 100%;
        overflow: auto;
    }
    
    .{component}__panel--active {
        display: block;
    }
    
    /* Additional component-specific styles... */
</style>

<!-- Script Implementation - CORRECT PATTERN: SELF-CONTAINED WITH NO SHARED DEPENDENCIES -->
<script type="text/javascript">
// COMPONENT SCRIPT - FULLY SELF-CONTAINED
// This prevents interference with other components

// IMMEDIATELY SET UP UI MANAGER PROTECTION
// Tell UI Manager to ignore this component - must be done IMMEDIATELY to avoid races
if (window.uiManager) {
    window.uiManager._ignoreComponent = '{component}';
    console.log('[{COMPONENT}] Set UI Manager to ignore {component} component');
}

// DEFINE TAB SWITCHING FUNCTION
// CRITICAL: This uses no shared code/utilities to avoid conflicts
window.{component}_switchTab = function(tabId) {
    console.log('[{COMPONENT}] Switching to tab:', tabId);
    
    // Force HTML panel visibility
    const htmlPanelElements = document.querySelectorAll('#html-panel');
    htmlPanelElements.forEach(panel => {
        if (panel) panel.style.display = 'block';
    });
    
    try {
        // Only select elements within this component to avoid conflicts
        const componentContainer = document.querySelector('.{component}');
        if (!componentContainer) {
            console.error('[{COMPONENT}] Tab Switch: Cannot find {component} container');
            return false;
        }
        
        // Update tab active state - ONLY WITHIN THIS COMPONENT'S CONTAINER
        const tabs = componentContainer.querySelectorAll('.{component}__tab');
        tabs.forEach(tab => {
            if (tab.getAttribute('data-tab') === tabId) {
                tab.classList.add('{component}__tab--active');
            } else {
                tab.classList.remove('{component}__tab--active');
            }
        });
        
        // Update panel visibility - ONLY WITHIN THIS COMPONENT'S CONTAINER
        const panels = componentContainer.querySelectorAll('.{component}__panel');
        panels.forEach(panel => {
            const panelId = panel.id;
            if (panelId === tabId + '-panel') {
                panel.style.display = 'block';
                panel.classList.add('{component}__panel--active');
            } else {
                panel.style.display = 'none';
                panel.classList.remove('{component}__panel--active');
            }
        });
        
        // Update component state
        if (window.{component}Component) {
            window.{component}Component.state = window.{component}Component.state || {};
            window.{component}Component.state.activeTab = tabId;
            
            // Call component-specific methods if available
            if (typeof window.{component}Component.saveComponentState === 'function') {
                window.{component}Component.saveComponentState();
            }
        }
    } catch (err) {
        console.error('[{COMPONENT}] Error in tab switching:', err);
    }
    
    return false; // Stop event propagation
};

// LOAD COMPONENT
// Load after defining tab switching to ensure it's available
function {component}_loadComponent() {
    console.log('[{COMPONENT}] Loading component script...');
    
    const timestamp = new Date().getTime();
    const scriptPath = `/scripts/{component}/{component}-component.js?t=${timestamp}`;
    
    const script = document.createElement('script');
    script.src = scriptPath;
    script.async = false;
    script.onload = function() {
        console.log('[{COMPONENT}] Component script loaded successfully');
        
        if (window.{component}Component && typeof window.{component}Component.init === 'function') {
            try {
                window.{component}Component.init();
                console.log('[{COMPONENT}] Component initialized');
            } catch (err) {
                console.error('[{COMPONENT}] Component initialization error:', err);
            }
        } else {
            console.warn('[{COMPONENT}] Component init function not found');
        }
    };
    script.onerror = function() {
        console.error('[{COMPONENT}] Failed to load component script');
    };
    
    document.body.appendChild(script);
}

// HTML PANEL PROTECTION
// Setup explicit protection for the HTML panel to prevent it being hidden
function {component}_protectHtmlPanel() {
    const htmlPanel = document.getElementById('html-panel');
    if (!htmlPanel) {
        console.error('[{COMPONENT}] Cannot find HTML panel to protect');
        return;
    }
    
    console.log('[{COMPONENT}] Protecting HTML panel from being hidden');
    htmlPanel.style.display = 'block'; // Force it to be visible
    
    // Store the original display value
    if (!htmlPanel.hasOwnProperty('_{component}OriginalDisplay')) {
        Object.defineProperty(htmlPanel, '_{component}OriginalDisplay', {
            value: 'block',
            writable: true,
            configurable: true
        });
    }
    
    // Only define the getter/setter if it hasn't already been defined by this component
    if (!htmlPanel.style._{component}Protected) {
        // Mark the display property as protected by this component
        Object.defineProperty(htmlPanel.style, '_{component}Protected', {
            value: true,
            writable: false,
            configurable: true
        });
        
        // Protect the display property
        Object.defineProperty(htmlPanel.style, 'display', {
            get: function() { 
                return htmlPanel._{component}OriginalDisplay; 
            },
            set: function(value) {
                console.log(`[{COMPONENT}] Intercepted attempt to set HTML panel display to: ${value}`);
                if (value === 'none') {
                    console.log('[{COMPONENT}] Blocked attempt to hide HTML panel');
                    htmlPanel._{component}OriginalDisplay = 'block';
                } else {
                    htmlPanel._{component}OriginalDisplay = value;
                }
            },
            configurable: true
        });
    }
}

// SETUP
// Do immediate initialization on script load
{component}_protectHtmlPanel();
{component}_loadComponent();
</script>
```

## JavaScript Implementation

```javascript
/**
 * {Component} Component
 * {Brief description} with BEM naming conventions
 */

class {Component}Component {
    constructor() {
        this.state = {
            initialized: false,
            activeTab: 'tab1', // Default tab
            // Component-specific state...
        };
        
        // Component-specific properties...
    }
    
    /**
     * Initialize the component
     */
    init() {
        // Debug instrumentation (can be added at zero-cost)
        if (window.TektonDebug) TektonDebug.info('{component}', 'Initializing {Component} component');
        
        // If already initialized, just activate
        if (this.state.initialized) {
            if (window.TektonDebug) TektonDebug.info('{component}', '{Component} component already initialized, just activating');
            this.activateComponent();
            return this;
        }
        
        // Setup component functionality
        this.setupTabs();
        this.setupEventListeners();
        // Additional setup...
        
        // Mark as initialized
        this.state.initialized = true;
        
        return this;
    }
    
    /**
     * Set up tab switching functionality
     */
    setupTabs() {
        if (window.TektonDebug) TektonDebug.debug('{component}', 'Setting up {Component} tabs');
        
        // Find the component container
        const container = document.querySelector('.{component}');
        if (!container) {
            if (window.TektonDebug) TektonDebug.error('{component}', '{Component} container not found!');
            return;
        }
        
        // Get tabs within the container
        const tabs = container.querySelectorAll('.{component}__tab');
        
        // Add click handlers to tabs
        tabs.forEach(tab => {
            const tabId = tab.getAttribute('data-tab');
            tab.addEventListener('click', () => {
                this.activateTab(tabId);
            });
        });
        
        // Activate the default tab
        const defaultTab = this.state.activeTab || 'tab1';
        this.activateTab(defaultTab);
    }
    
    /**
     * Activate a specific tab - CORRECT IMPLEMENTATION
     * @param {string} tabId - The ID of the tab to activate
     */
    activateTab(tabId) {
        if (window.TektonDebug) TektonDebug.debug('{component}', `Activating tab: ${tabId}`);
        
        // Find the component container
        const container = document.querySelector('.{component}');
        if (!container) {
            if (window.TektonDebug) TektonDebug.error('{component}', '{Component} container not found!');
            return;
        }
        
        // Update active tab - remove active class from all tabs
        container.querySelectorAll('.{component}__tab').forEach(t => {
            t.classList.remove('{component}__tab--active');
        });
        
        // Add active class to the selected tab
        const tabButton = container.querySelector(`.{component}__tab[data-tab="${tabId}"]`);
        if (tabButton) {
            tabButton.classList.add('{component}__tab--active');
        } else {
            if (window.TektonDebug) TektonDebug.error('{component}', `Tab button not found for tab: ${tabId}`);
            return; // Exit early if we can't find the tab
        }
        
        // Hide all panels by removing active class
        container.querySelectorAll('.{component}__panel').forEach(panel => {
            panel.classList.remove('{component}__panel--active');
        });
        
        // Show the specific tab panel by adding active class
        const tabPanel = container.querySelector(`#${tabId}-panel`);
        if (tabPanel) {
            tabPanel.classList.add('{component}__panel--active');
        } else {
            if (window.TektonDebug) TektonDebug.error('{component}', `Panel not found for tab: ${tabId}`);
        }
        
        // Save active tab to state
        this.state.activeTab = tabId;
    }
    
    // Additional component methods...
}

// Create global instance
window.{component}Component = new {Component}Component();
```

## Debug Instrumentation

Tekton includes a lightweight debug instrumentation system that allows you to add logging with zero overhead in production environments. To use it:

1. Check for the existence of the `TektonDebug` object before using it (conditional instrumentation)
2. Use the appropriate log level (TRACE, DEBUG, INFO, WARN, ERROR, FATAL)
3. Always include the component name as the first parameter
4. Include contextual data where helpful

```javascript
// Example debug instrumentation
if (window.TektonDebug) TektonDebug.debug('componentName', 'Message', optionalData);
```

When the debug system is disabled (default), these calls have virtually zero overhead. When enabled, they provide rich contextual information.

## Best Practices

### Component Isolation
- Each component should be fully contained within its root element
- Use BEM naming to prevent CSS conflicts (`{component}__element--modifier`)
- Scope all DOM operations to the component container
- Avoid global state or direct DOM manipulation outside the component
- Protect against UI Manager interference with `_ignoreComponent`

### Script Loading
- Use the pattern shown above - self-contained script with component-specific namespacing
- Use direct inline onclick handlers to prevent event bubbling issues
- Always return false from click handlers to stop event propagation
- Define tab-switching logic BEFORE loading the component JS

### Tab Switching
- Use namespaced functions like `{component}_switchTab()` for all tab operations
- Tabs must have `data-tab` attribute matching panel IDs (`data-tab="tab1"` → `id="tab1-panel"`)
- Panels must have CSS classes for visibility control (`.{component}__panel--active`)
- Use CSS classes AND inline display property for showing/hiding panels
- Always scope DOM queries to the component container
- Always add `onclick="{component}_switchTab('tabId'); return false;"` to tabs

### HTML Panel Protection
- Immediately protect the HTML panel from being hidden
- Use component-specific property names (e.g., `_{component}Protected`)
- Add property getters/setters to prevent hiding the panel
- Block attempts to set display to 'none'

### UI Manager Protection
- Immediately set `window.uiManager._ignoreComponent = '{component}'` at the top of the script
- This prevents UI Manager from interfering with component tab switching

### Debugging
- Use the conditional debug instrumentation pattern
- Check for `window.TektonDebug` before using it
- Include component name with all debug calls
- Add contextual data for complex operations

## Minimal Loader Integration
The minimal-loader.js script handles component loading and initialization. It:
1. Fetches the component HTML
2. Adds it to the DOM
3. Executes any script tags found in the component
4. Calls `init()` on the component if available

Your component must expose a global `{component}Component` object with an `init()` method to work correctly with the loader.

## Troubleshooting
- **Component not loading**: Check browser console for script loading errors
- **Tabs not working**: Verify panel IDs match data-tab attributes exactly
- **CSS issues**: Ensure proper BEM naming and containment
- **Initialization problems**: Verify the global component object and init() method

## Component Issues & Solutions

### Common Component Issues

1. **Tab Switching Fails Between Components**
   - **Cause**: Shared code and tab switching utilities cause conflicts
   - **Solution**: Use self-contained tab switching with direct onclick handlers
   
2. **HTML Panel Gets Hidden**
   - **Cause**: Other components or UI Manager try to hide the HTML panel
   - **Solution**: Use property getters/setters to protect the display property

3. **UI Manager Interference**
   - **Cause**: UI Manager tries to manage components through its activateComponent method
   - **Solution**: Set _ignoreComponent flag to prevent interference

4. **Global Namespace Pollution**
   - **Cause**: Components use generic function names that conflict
   - **Solution**: Use component-specific namespaced functions (`{component}_functionName`)

## Example Components
- See `/components/ergon/ergon-component.html` for a working example of isolated tabs
- Reference `/components/athena/athena-component.html` for another implementation
- Both components use the same pattern for tab isolation and HTML panel protection