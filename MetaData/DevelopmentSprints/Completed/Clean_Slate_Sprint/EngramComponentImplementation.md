# Engram Component Implementation Guide

## Overview

This document outlines the implementation plan for the Engram component following the Clean Slate Sprint approach. Engram is Tekton's memory system, responsible for storing, retrieving, and organizing information across components.

## Implementation Strategy

The Engram component will follow the same clean slate approach that was successfully used for the Athena, Ergon, and Hermes components:

1. Start with the component template structure
2. Implement proper BEM naming conventions
3. Ensure component isolation
4. Add HTML panel protection
5. Implement self-contained tab functionality
6. Add debug instrumentation

## Component Structure

### HTML Structure

The Engram component's HTML should follow this structure:

```html
<!-- Engram Component - Memory and Knowledge Management -->
<div class="engram">
    <!-- Component Header with Title -->
    <div class="engram__header">
        <div class="engram__title-container">
            <img src="/images/hexagon.jpg" alt="Tekton" class="engram__icon">
            <h2 class="engram__title">
                <span class="engram__title-main">Engram</span>
                <span class="engram__title-sub">Memory System</span>
            </h2>
        </div>
    </div>
    
    <!-- Engram Menu Bar with Tab Navigation -->
    <div class="engram__menu-bar">
        <div class="engram__tabs">
            <!-- Memory Explorer Tab -->
            <div class="engram__tab engram__tab--active" data-tab="explorer" onclick="engram_switchTab('explorer'); return false;">
                <span class="engram__tab-label">Memory Explorer</span>
            </div>
            <!-- Memory Search Tab -->
            <div class="engram__tab" data-tab="search" onclick="engram_switchTab('search'); return false;">
                <span class="engram__tab-label">Memory Search</span>
            </div>
            <!-- Memory Stats Tab -->
            <div class="engram__tab" data-tab="stats" onclick="engram_switchTab('stats'); return false;">
                <span class="engram__tab-label">Memory Stats</span>
            </div>
            <!-- Memory Chat Tab -->
            <div class="engram__tab" data-tab="chat" onclick="engram_switchTab('chat'); return false;">
                <span class="engram__tab-label">Memory Chat</span>
            </div>
            <!-- Team Chat Tab -->
            <div class="engram__tab" data-tab="teamchat" onclick="engram_switchTab('teamchat'); return false;">
                <span class="engram__tab-label">Team Chat</span>
            </div>
        </div>
        <div class="engram__actions">
            <button id="clear-chat-btn" class="engram__action-button" style="display: none;" onclick="engram_clearChat(); return false;">
                <span class="engram__button-label">Clear</span>
            </button>
        </div>
    </div>
    
    <!-- Engram Content Area -->
    <div class="engram__content">
        <!-- Panels for each tab -->
    </div>
    
    <!-- Footer with Chat Input -->
    <div class="engram__footer">
        <div class="engram__chat-input-container">
            <div class="engram__chat-prompt">></div>
            <input type="text" id="chat-input" class="engram__chat-input" 
                   placeholder="Enter chat message for Engram memory chat, searching, or memory operations">
            <button id="send-button" class="engram__send-button">Send</button>
        </div>
    </div>
</div>
```

### Tab Panels

Define content panels for each tab:

1. **Memory Explorer Panel** - For browsing memory collections and individual memories
2. **Memory Search Panel** - For semantic and keyword search of memories
3. **Memory Stats Panel** - For viewing memory usage statistics and health
4. **Memory Chat Panel** - For chatting with the memory system directly
5. **Team Chat Panel** - For team communication (same as other components)

### CSS Structure

Follow the BEM naming convention used in Athena and Hermes for all CSS classes. Ensure that all styles are scoped to the `.engram` container and follow the established pattern:

```css
/* Container */
.engram {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    background-color: var(--bg-primary, #1e1e2e);
    color: var(--text-primary, #f0f0f0);
}

/* Header */
.engram__header {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 50px; /* Match Athena's header height */
}

/* Menu Bar */
.engram__menu-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 46px; /* Match Athena's menu bar height */
}

/* Content Area */
.engram__content {
    flex: 1;
    overflow: hidden;
    position: relative;
}

/* Footer */
.engram__footer {
    background-color: var(--bg-secondary, #252535);
    border-top: 1px solid var(--border-color, #444444);
    padding: 12px 16px;
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 70px; /* Fixed height to match Athena's footer */
}
```

### JavaScript Structure

Implement the following JavaScript functions:

1. **UI Manager Protection** - To prevent interference from the UI Manager
2. **Tab Switching Function** - Self-contained tab switching
3. **HTML Panel Protection** - To prevent the panel from being hidden
4. **Basic Chat Functionality** - For memory and team chat
5. **Component Initialization** - For proper setup and loading
6. **Component Load Error Handling** - For graceful error management

```javascript
// UI Manager Protection
if (window.uiManager) {
    window.uiManager._ignoreComponent = 'engram';
    console.log('[ENGRAM] Set UI Manager to ignore engram component');
}

// Tab Switching Function
window.engram_switchTab = function(tabId) {
    console.log('[ENGRAM] Switching to tab:', tabId);
    
    // Force HTML panel visibility
    const htmlPanelElements = document.querySelectorAll('#html-panel');
    htmlPanelElements.forEach(panel => {
        if (panel) panel.style.display = 'block';
    });
    
    try {
        // Only select elements within engram component
        const engramContainer = document.querySelector('.engram');
        if (!engramContainer) {
            console.error('[ENGRAM] Tab Switch: Cannot find engram container');
            return false;
        }
        
        // Update tab active state
        const tabs = engramContainer.querySelectorAll('.engram__tab');
        tabs.forEach(tab => {
            if (tab.getAttribute('data-tab') === tabId) {
                tab.classList.add('engram__tab--active');
            } else {
                tab.classList.remove('engram__tab--active');
            }
        });
        
        // Update panel visibility
        const panels = engramContainer.querySelectorAll('.engram__panel');
        panels.forEach(panel => {
            const panelId = panel.id;
            if (panelId === tabId + '-panel') {
                panel.style.display = 'block';
                panel.classList.add('engram__panel--active');
            } else {
                panel.style.display = 'none';
                panel.classList.remove('engram__panel--active');
            }
        });
        
        // Update clear button visibility for chat tabs
        const clearButton = engramContainer.querySelector('#clear-chat-btn');
        if (clearButton) {
            clearButton.style.display = (tabId === 'chat' || tabId === 'teamchat') ? 'block' : 'none';
        }
        
        // Update component state
        if (window.engramComponent) {
            window.engramComponent.state = window.engramComponent.state || {};
            window.engramComponent.state.activeTab = tabId;
            
            // Call component-specific methods if available
            if (typeof window.engramComponent.saveComponentState === 'function') {
                window.engramComponent.saveComponentState();
            }
        }
    } catch (err) {
        console.error('[ENGRAM] Error in tab switching:', err);
    }
    
    return false; // Stop event propagation
};

// Clear Chat Function
window.engram_clearChat = function() {
    console.log('[ENGRAM] Clear chat clicked');
    
    try {
        // Get active tab ID within engram container
        const engramContainer = document.querySelector('.engram');
        if (!engramContainer) {
            console.error('[ENGRAM] Clear Chat: Cannot find engram container');
            return false;
        }
        
        const activeTab = engramContainer.querySelector('.engram__tab--active');
        const tabId = activeTab ? activeTab.getAttribute('data-tab') : '';
        
        if (tabId === 'chat' || tabId === 'teamchat') {
            // Get message container within engram container only
            const panel = engramContainer.querySelector('#' + tabId + '-messages');
            if (panel) {
                // Keep welcome message
                const welcomeMsg = panel.querySelector('.engram__message--system');
                if (welcomeMsg) {
                    panel.innerHTML = '';
                    panel.appendChild(welcomeMsg);
                    console.log('[ENGRAM] Cleared chat, kept welcome message');
                } else {
                    panel.innerHTML = '';
                    console.log('[ENGRAM] Cleared chat completely');
                }
            }
        }
    } catch (err) {
        console.error('[ENGRAM] Error clearing chat:', err);
    }
    
    return false; // Stop event propagation
};
```

## Implementation Steps

### Step 1: Create Component Skeleton

Create the basic structure using the template from Athena and Hermes components:

1. Create engram-component.html with basic BEM structure
2. Add component-specific CSS styles within the HTML for now
3. Add bare-bones JavaScript functionality for tab switching

### Step 2: Implement Explorer Panel

Implement the Memory Explorer panel with:

1. Memory collection list
2. Memory browser
3. Memory visualization

### Step 3: Implement Search Panel

Implement the Memory Search panel with:

1. Search input with filtering options
2. Semantic search controls
3. Results display with preview

### Step 4: Implement Stats Panel

Implement the Memory Stats panel with:

1. Memory usage statistics
2. Memory health metrics
3. Visual graphs and charts

### Step 5: Implement Chat Panels

Implement both chat panels with consistent chat UI:

1. Memory Chat panel for interacting with the memory system
2. Team Chat panel matching the Athena/Hermes implementation

### Step 6: Implement Footer and Chat Functionality

Implement chat input functionality:

1. Proper input handling
2. Command processing
3. Chat display and history

### Step 7: Test and Verify

Ensure the component works properly and follows all patterns:

1. Test loading in isolation
2. Test compatibility with other components
3. Verify tab switching works properly
4. Ensure protection from UI Manager interference

## Key Considerations

1. **Visual Consistency**: Ensure the Engram component visually matches Athena and Hermes (header, menu bar, footer heights)
2. **Component Isolation**: Prevent any leaking of styles or behavior to other components
3. **Error Handling**: Gracefully handle loading and runtime errors
4. **Debug Instrumentation**: Add comprehensive logging with component prefix
5. **Performance**: Optimize for performance, especially with memory visualization

## Implementation Schedule

- **Day 1**: Create component skeleton and implement Explorer panel
- **Day 2**: Implement Search and Stats panels
- **Day 3**: Implement Chat panels and footer functionality
- **Day 4**: Testing, fixes, and documentation

## Success Criteria

The implementation will be considered successful when:

1. Engram component loads and displays correctly
2. All tabs function properly without interference
3. Component maintains isolation from other components
4. UI is visually consistent with Athena and Hermes
5. All functionality works as expected
6. No errors or warnings appear in console
7. Debug instrumentation is complete and functional