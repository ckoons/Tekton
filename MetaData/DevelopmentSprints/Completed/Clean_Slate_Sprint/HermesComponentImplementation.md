# Hermes Component Implementation Guide

This document outlines the implementation plan for the Hermes component as part of the Clean Slate Sprint. Hermes serves as the message and data handling component of the Tekton system.

## Overview

The Hermes component is responsible for:

1. Managing communication with the LLM adapter service
2. Handling data transformations and validations
3. Providing message streaming capabilities
4. Managing connection state and reconnection logic

## Implementation Steps

Follow these steps when implementing the Hermes component:

### 1. Component Structure

Create the following files:

- `/components/hermes/hermes-component.html` - Component HTML using BEM naming
- `/scripts/hermes/hermes-component.js` - Component JavaScript with container-scoped queries
- `/scripts/hermes/hermes-service.js` - Service layer for LLM and data handling
- `/scripts/hermes/hermes-llm-service.js` - Specialized LLM adapter service
- `/styles/hermes/hermes-component.css` - Component CSS with BEM naming

### 2. HTML Implementation

Follow the pattern established by the Ergon and Athena components:

```html
<!-- Hermes Component - Message and Data Handling -->
<div class="hermes">
    <!-- Component Header with Title -->
    <div class="hermes__header">
        <div class="hermes__title-container">
            <img src="/images/hexagon.jpg" alt="Tekton" class="hermes__icon">
            <h2 class="hermes__title">
                <span class="hermes__title-main">Hermes</span>
                <span class="hermes__title-sub">Messages/Data</span>
            </h2>
        </div>
    </div>
    
    <!-- Hermes Menu Bar with Tab Navigation -->
    <div class="hermes__menu-bar">
        <div class="hermes__tabs">
            <div class="hermes__tab hermes__tab--active" data-tab="connections">
                <span class="hermes__tab-label">Connections</span>
            </div>
            <div class="hermes__tab" data-tab="llm">
                <span class="hermes__tab-label">LLM Settings</span>
            </div>
            <div class="hermes__tab" data-tab="data">
                <span class="hermes__tab-label">Data Formats</span>
            </div>
            <div class="hermes__tab" data-tab="logs">
                <span class="hermes__tab-label">Message Logs</span>
            </div>
            <div class="hermes__tab" data-tab="chat">
                <span class="hermes__tab-label">Test Chat</span>
            </div>
        </div>
        <div class="hermes__actions">
            <button id="refresh-connections-btn" class="hermes__action-button">
                <span class="hermes__button-label">Refresh</span>
            </button>
        </div>
    </div>
    
    <!-- Hermes Content Area -->
    <div class="hermes__content">
        <!-- Tab panels go here, one for each tab above -->
        <!-- Use the pattern: id="{tabId}-panel" class="hermes__panel hermes__panel--active" -->
    </div>
    
    <!-- Footer with Chat Input (if needed) -->
    <div class="hermes__footer">
        <div class="hermes__chat-input-container">
            <div class="hermes__chat-prompt">></div>
            <input type="text" id="chat-input" class="hermes__chat-input" 
                   placeholder="Enter test message for LLM">
            <button id="send-button" class="hermes__send-button">Send</button>
        </div>
    </div>
</div>

<!-- Add component-specific styles -->
<style>
    /* Hermes component styles using BEM naming convention */
    /* Follow the pattern established in ergon-component.html */
</style>

<script>
// Use direct script inclusion to ensure proper loading
// This is an inline script that will be executed by the minimal-loader when the component HTML is loaded

// Create a dynamically inserted script with error handling to load the component
const timestamp = new Date().getTime(); // Cache busting
const scriptPath = `/scripts/hermes/hermes-component.js?t=${timestamp}`;

console.log('Loading Hermes component script from:', scriptPath);

// Create and insert the script element directly in the page
const script = document.createElement('script');
script.src = scriptPath;
script.async = false; // Use false for more reliable loading order

// Set up load and error handlers
script.onload = function() {
    console.log('Hermes component script loaded successfully');
    // Initialize the component once loaded
    if (window.hermesComponent && typeof window.hermesComponent.init === 'function') {
        console.log('Initializing Hermes component');
        window.hermesComponent.init();
    } else {
        console.error('Hermes component not properly loaded - window.hermesComponent object is missing or init method not available');
        console.log('Available global objects:', Object.keys(window).filter(k => k.toLowerCase().includes('component')));
    }
};

script.onerror = function(error) {
    console.error('Failed to load Hermes component script:', error);
};

// Add the script to the document
document.body.appendChild(script);
</script>
```

### 3. JavaScript Implementation

Create the main component class following the pattern from Ergon:

```javascript
/**
 * Hermes Component
 * Message and data handling interface with BEM naming conventions
 */

class HermesComponent {
    constructor() {
        this.state = {
            initialized: false,
            activeTab: 'connections', // Default tab
            connections: {},
            llmSettings: {},
            messages: []
        };
        
        // Configure logging level
        this.logLevel = 'info';
    }
    
    /**
     * Initialize the component
     */
    init() {
        // Legacy logging
        console.log('Initializing Hermes component');
        
        // Debug instrumentation
        if (window.TektonDebug) TektonDebug.info('hermesComponent', 'Initializing component');
        
        // If already initialized, just activate
        if (this.state.initialized) {
            console.log('Hermes component already initialized, just activating');
            if (window.TektonDebug) TektonDebug.debug('hermesComponent', 'Already initialized, just activating');
            this.activateComponent();
            return this;
        }
        
        // Setup component functionality
        this.setupTabs();
        this.setupEventListeners();
        this.loadConnectionData();
        
        // Apply Greek name handling
        this.handleGreekNames();
        
        // Mark as initialized
        this.state.initialized = true;
        
        return this;
    }
    
    /**
     * Activate the component interface
     */
    activateComponent() {
        console.log('Activating Hermes component');
        
        // Restore component state
        this.restoreComponentState();
    }
    
    /**
     * Handle Greek vs modern naming based on SHOW_GREEK_NAMES env var
     */
    handleGreekNames() {
        // Find the Hermes container (scope all DOM operations to this container)
        const container = document.querySelector('.hermes');
        if (!container) {
            console.error('Hermes container not found!');
            return;
        }
        
        // Get the title element
        const titleElement = container.querySelector('.hermes__title-main');
        const subtitleElement = container.querySelector('.hermes__title-sub');
        
        if (!titleElement || !subtitleElement) {
            return;
        }
        
        // Check environment setting
        if (window.ENV && window.ENV.SHOW_GREEK_NAMES === 'false') {
            // Hide the Greek name
            titleElement.style.display = 'none';
            // Make the modern name more prominent
            subtitleElement.style.fontWeight = 'bold';
            subtitleElement.style.fontSize = '1.5rem';
        }
    }
    
    /**
     * Set up tab switching functionality
     */
    setupTabs() {
        console.log('Setting up Hermes tabs');
        if (window.TektonDebug) TektonDebug.debug('hermesComponent', 'Setting up Hermes tabs');
        
        // Find the Hermes container (scope all DOM operations to this container)
        const container = document.querySelector('.hermes');
        if (!container) {
            console.error('Hermes container not found!');
            if (window.TektonDebug) TektonDebug.error('hermesComponent', 'Hermes container not found during tab setup');
            return;
        }
        
        // Get tabs within the container
        const tabs = container.querySelectorAll('.hermes__tab');
        console.log(`Found ${tabs.length} tabs:`, Array.from(tabs).map(t => t.getAttribute('data-tab')));
        
        // Add click handlers to tabs
        tabs.forEach(tab => {
            const tabId = tab.getAttribute('data-tab');
            console.log(`Setting up click handler for tab: ${tabId}`);
            
            tab.addEventListener('click', () => {
                console.log(`Tab clicked: ${tabId}`);
                this.activateTab(tabId);
            });
        });
        
        // Activate the default tab
        const defaultTab = this.state.activeTab || 'connections';
        console.log(`Activating default tab: ${defaultTab}`);
        this.activateTab(defaultTab);
    }
    
    /**
     * Activate a specific tab
     * @param {string} tabId - The ID of the tab to activate
     */
    activateTab(tabId) {
        console.log(`Direct DOM: Activating tab: ${tabId}`);
        if (window.TektonDebug) TektonDebug.debug('hermesComponent', `Activating tab: ${tabId}`);
        
        // Find the Hermes container (scope all DOM operations to this container)
        const container = document.querySelector('.hermes');
        if (!container) {
            console.error('Hermes container not found!');
            if (window.TektonDebug) TektonDebug.error('hermesComponent', 'Hermes container not found!');
            return;
        }
        
        // Update active tab - remove active class from all tabs
        container.querySelectorAll('.hermes__tab').forEach(t => {
            t.classList.remove('hermes__tab--active');
        });
        
        // Add active class to the selected tab
        const tabButton = container.querySelector(`.hermes__tab[data-tab="${tabId}"]`);
        if (tabButton) {
            tabButton.classList.add('hermes__tab--active');
            if (window.TektonDebug) TektonDebug.trace('hermesComponent', `Tab button found for ${tabId}`, {element: tabButton.outerHTML});
        } else {
            console.error(`Tab button not found for tab: ${tabId}`);
            if (window.TektonDebug) TektonDebug.error('hermesComponent', `Tab button not found for tab: ${tabId}`);
            return; // Exit early if we can't find the tab
        }
        
        // Get all panels and log what we find
        const panels = container.querySelectorAll('.hermes__panel');
        console.log(`Found ${panels.length} panels`);
        
        // Apply CSS style overrides directly to elements
        panels.forEach(panel => {
            // First remove the active class
            panel.classList.remove('hermes__panel--active');
            
            // Then hide it with direct style manipulation
            panel.style.display = 'none';
            console.log(`Panel ${panel.id} hidden`);
        });
        
        // Show the specific tab panel
        const tabPanel = container.querySelector(`#${tabId}-panel`);
        if (tabPanel) {
            tabPanel.classList.add('hermes__panel--active');
            
            // Directly set display style - this is the key change
            tabPanel.style.display = 'block';
            console.log(`Panel ${tabPanel.id} shown with direct style.display = 'block'`);
            
            if (window.TektonDebug) TektonDebug.debug('hermesComponent', `Panel activated for tab: ${tabId}`);
        } else {
            console.error(`Panel not found for tab: ${tabId}`);
            if (window.TektonDebug) TektonDebug.error('hermesComponent', `Panel not found for tab: ${tabId}`);
        }
        
        // Save active tab to state
        this.state.activeTab = tabId;
        this.saveComponentState();
        console.log(`Tab activation for ${tabId} complete`);
    }
    
    // Add more methods following the Ergon pattern
    
    /**
     * Simple logging function
     * @param {string} level - Log level ('debug', 'info', 'warn', 'error')
     * @param {string} message - The message to log
     */
    log(level, message) {
        // Only log if level is at or above configured level
        const levels = { debug: 0, info: 1, warn: 2, error: 3 };
        if (levels[level] >= levels[this.logLevel]) {
            console.log(`[Hermes:${level}] ${message}`);
        }
    }
}

// Create global instance
window.hermesComponent = new HermesComponent();
```

### 4. CSS Implementation

Create the component CSS following the BEM naming pattern. Start with the basic structure and expand from there:

```css
/* Hermes component styles using BEM naming convention */

/* Container */
.hermes {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    background-color: var(--bg-primary, #1e1e2e);
    color: var(--text-primary, #f0f0f0);
}

/* Header */
.hermes__header {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
}

/* Menu Bar */
.hermes__menu-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
}

.hermes__tabs {
    display: flex;
    gap: 8px;
}

.hermes__tab {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background-color: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-primary, #f0f0f0);
    cursor: pointer;
    transition: all 0.2s ease;
}

.hermes__tab:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

.hermes__tab--active {
    border-bottom-color: var(--color-primary, #4285F4); /* Blue for Hermes */
    font-weight: 500;
}

/* Content Area */
.hermes__content {
    flex: 1;
    overflow: hidden;
    position: relative;
}

.hermes__panel {
    display: none;
    height: 100%;
    width: 100%;
    overflow: auto;
    position: relative; /* Needed for footer positioning */
}

.hermes__panel--active {
    display: block;
}

/* Add additional specific styles for various panels and elements */
```

### 5. Debug Instrumentation

Ensure debug instrumentation is added to key functions:

1. Always check for TektonDebug presence
2. Use consistent component name 'hermesComponent'
3. Use appropriate log levels (trace, debug, info, warn, error, fatal)
4. Include useful context data where appropriate

Example:
```javascript
if (window.TektonDebug) TektonDebug.debug('hermesComponent', 'Loading connection data', {url: apiUrl});
```

### 6. Testing

Follow these testing steps:

1. Test tab switching functionality
2. Verify that all panels display correctly
3. Test event handlers and UI interactions
4. Verify debug instrumentation works when enabled
5. Check for any console errors
6. Ensure styles are contained within the component
7. Test with different window sizes

## Special Considerations for Hermes

1. **LLM Connection Handling**:
   - Implement proper connection status indicators
   - Add reconnection logic with exponential backoff
   - Handle streaming message chunks

2. **Server Communication**:
   - Use WebSocket for streaming responses
   - Implement message queueing for offline operation
   - Add proper error handling for network issues

3. **Performance**:
   - Optimize message handling for real-time performance
   - Use efficient data structures for message storage
   - Implement pagination for message logs

## Implementation Checklist

- [ ] Create component HTML structure with tabs and panels
- [ ] Implement CSS with BEM naming conventions
- [ ] Create main component JS class with initialization
- [ ] Implement tab switching functionality
- [ ] Add event handlers for UI interactions
- [ ] Create service layer for LLM operations
- [ ] Implement connection status management
- [ ] Add message handling and storage
- [ ] Implement debug instrumentation
- [ ] Test all functionality
- [ ] Document the component

## Reference

For more information, see these related documents:

- [Component Implementation Guide](../../../Hephaestus/ui/docs/ComponentImplementationGuide.md)
- [Clean Slate UI Implementation](./CleanSlateUIImplementation.md)
- [Debug Instrumentation Guide](../../../MetaData/TektonDocumentation/DeveloperGuides/Debugging/ComponentInstrumentation.md)