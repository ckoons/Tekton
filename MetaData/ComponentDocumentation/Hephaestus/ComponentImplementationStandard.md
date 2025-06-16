# Tekton UI Component Implementation Standard

## Overview

This document defines the standard pattern for implementing UI components in the Tekton system. Following these patterns ensures components are isolated, maintain their functionality when loaded together, and avoid interference.

## Key Principles

1. **Full Component Isolation**: Components must be completely self-contained
2. **No Shared Tab Utilities**: Each component handles its own tab switching
3. **Direct DOM Event Handlers**: Use inline `onclick` handlers with component-specific functions
4. **UI Manager Protection**: Each component must protect itself from UI Manager interference
5. **HTML Panel Protection**: Components must prevent their panels from being hidden

## Implementation Template

All components MUST follow this implementation template, as demonstrated in the `/components/athena/athena-component.html` and `/components/ergon/ergon-component.html` files.

### HTML/CSS Template

```html
<!-- {Component} Component - Brief description -->
<div class="{component}">
    <!-- Component Header -->
    <div class="{component}__header">
        <!-- ... header content ... -->
    </div>
    
    <!-- Tab Navigation -->
    <div class="{component}__menu-bar">
        <div class="{component}__tabs">
            <!-- REQUIRED: Inline onclick with component-prefixed function and return false -->
            <div class="{component}__tab {component}__tab--active" data-tab="tab1" 
                 onclick="{component}_switchTab('tab1'); return false;">
                <span class="{component}__tab-label">Tab 1</span>
            </div>
            <!-- Additional tabs with same pattern -->
        </div>
    </div>
    
    <!-- Content Area with Panels -->
    <div class="{component}__content">
        <!-- Panels with explicit display style -->
        <div id="tab1-panel" class="{component}__panel {component}__panel--active" style="display: block;">
            <!-- Panel content -->
        </div>
        
        <div id="tab2-panel" class="{component}__panel" style="display: none;">
            <!-- Panel content -->
        </div>
    </div>
</div>

<!-- Component Styles (BEM naming convention) -->
<style>
    /* Component container */
    .{component} {
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
    }
    
    /* Panel visibility control */
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
```

### JavaScript Template

```javascript
// COMPONENT SCRIPT - FULLY SELF-CONTAINED
// This prevents interference with other components

// IMMEDIATELY SET UP UI MANAGER PROTECTION
// Tell UI Manager to ignore this component - must be done IMMEDIATELY
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
```

## Common Implementation Issues

### Tab Switching Problems

**Issue**: When multiple components are loaded, tab switching stops working in one or more components.

**Causes**:
1. Shared tab utilities cause conflicts
2. Global event handlers override each other
3. UI Manager interferes with component-specific handlers

**Required Solution**:
1. Use direct inline `onclick` handlers: `onclick="{component}_switchTab('tab1'); return false;"`
2. Use component-specific functions: `{component}_switchTab`
3. Tell UI Manager to ignore the component: `window.uiManager._ignoreComponent = '{component}'`
4. Protect HTML panel from being hidden using property getters/setters

### Panel Visibility Issues

**Issue**: Component panels get hidden unexpectedly.

**Causes**:
1. Other components manipulate the DOM
2. UI Manager tries to control panel visibility

**Required Solution**:
1. Use both CSS classes AND inline styles for panel visibility
2. Protect the HTML panel with property getters/setters
3. Force panel to stay visible with `panel.style.display = 'block'`

## Reference Implementations

1. **Athena Component**: `/components/athena/athena-component.html`
2. **Ergon Component**: `/components/ergon/ergon-component.html`

These components demonstrate the correct implementation pattern that ensures tab switching works reliably even when multiple components are loaded in sequence.

## Validation Process

When implementing a new component, validate that:

1. Tab switching works when this component is loaded first
2. Tab switching works when this component is loaded after other components
3. Tab switching in other components still works after this component is loaded
4. The component correctly protects the HTML panel from being hidden

## Migration Guide for Existing Components

1. Replace event listeners with direct inline `onclick` handlers
2. Add component-specific tab switching function
3. Add UI Manager protection
4. Add HTML panel protection
5. Scope all DOM queries to the component container
6. Test thoroughly with other components

---

*This standard was established after resolving critical tab switching issues between Ergon and Athena components.*