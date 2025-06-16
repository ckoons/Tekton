# Rhetor Component Implementation Guide

## Overview

This document outlines the implementation plan for the Rhetor component following the Clean Slate Sprint approach. Rhetor is Tekton's writing assistant, responsible for drafting, editing, and formatting text content.

## Implementation Strategy

The Rhetor component will follow the same clean slate approach that was successfully used for the Athena, Ergon, Hermes, and Engram components:

1. Start with the component template structure
2. Implement proper BEM naming conventions
3. Ensure component isolation
4. Add HTML panel protection
5. Implement self-contained tab functionality
6. Add debug instrumentation

## Component Structure

### HTML Structure

The Rhetor component's HTML should follow this structure:

```html
<!-- Rhetor Component - Writing and Editing Assistant -->
<div class="rhetor">
    <!-- Component Header with Title -->
    <div class="rhetor__header">
        <div class="rhetor__title-container">
            <img src="/images/hexagon.jpg" alt="Tekton" class="rhetor__icon">
            <h2 class="rhetor__title">
                <span class="rhetor__title-main">Rhetor</span>
                <span class="rhetor__title-sub">Writing Assistant</span>
            </h2>
        </div>
    </div>
    
    <!-- Rhetor Menu Bar with Tab Navigation -->
    <div class="rhetor__menu-bar">
        <div class="rhetor__tabs">
            <!-- Writing Tab -->
            <div class="rhetor__tab rhetor__tab--active" data-tab="writing" onclick="rhetor_switchTab('writing'); return false;">
                <span class="rhetor__tab-label">Writing</span>
            </div>
            <!-- Templates Tab -->
            <div class="rhetor__tab" data-tab="templates" onclick="rhetor_switchTab('templates'); return false;">
                <span class="rhetor__tab-label">Templates</span>
            </div>
            <!-- Revision Tab -->
            <div class="rhetor__tab" data-tab="revision" onclick="rhetor_switchTab('revision'); return false;">
                <span class="rhetor__tab-label">Revision</span>
            </div>
            <!-- Format Tab -->
            <div class="rhetor__tab" data-tab="format" onclick="rhetor_switchTab('format'); return false;">
                <span class="rhetor__tab-label">Format</span>
            </div>
            <!-- Team Chat Tab -->
            <div class="rhetor__tab" data-tab="teamchat" onclick="rhetor_switchTab('teamchat'); return false;">
                <span class="rhetor__tab-label">Team Chat</span>
            </div>
        </div>
        <div class="rhetor__actions">
            <button id="clear-chat-btn" class="rhetor__action-button" style="display: none;" onclick="rhetor_clearChat(); return false;">
                <span class="rhetor__button-label">Clear</span>
            </button>
        </div>
    </div>
    
    <!-- Rhetor Content Area -->
    <div class="rhetor__content">
        <!-- Panels for each tab -->
    </div>
    
    <!-- Footer with Chat Input -->
    <div class="rhetor__footer">
        <div class="rhetor__chat-input-container">
            <div class="rhetor__chat-prompt">></div>
            <input type="text" id="chat-input" class="rhetor__chat-input" 
                   placeholder="Enter writing instructions, template requests, or team chat messages">
            <button id="send-button" class="rhetor__send-button">Send</button>
        </div>
    </div>
</div>
```

### Tab Panels

Define content panels for each tab:

1. **Writing Panel** - For drafting and editing text content
2. **Templates Panel** - For accessing and using writing templates
3. **Revision Panel** - For reviewing and tracking document revisions
4. **Format Panel** - For applying formatting and styles
5. **Team Chat Panel** - For team communication (same as other components)

### CSS Structure

Follow the BEM naming convention used in other components for all CSS classes. Ensure that all styles are scoped to the `.rhetor` container and follow the established pattern:

```css
/* Container */
.rhetor {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    background-color: var(--bg-primary, #1e1e2e);
    color: var(--text-primary, #f0f0f0);
}

/* Header */
.rhetor__header {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 50px; /* Match header height from other components */
}

/* Menu Bar */
.rhetor__menu-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 46px; /* Match menu bar height from other components */
}

/* Content Area */
.rhetor__content {
    flex: 1;
    overflow: hidden;
    position: relative;
}

/* Footer */
.rhetor__footer {
    background-color: var(--bg-secondary, #252535);
    border-top: 1px solid var(--border-color, #444444);
    padding: 12px 16px;
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 70px; /* Fixed height to match other components */
}
```

### JavaScript Structure

Implement the following JavaScript functions:

1. **UI Manager Protection** - To prevent interference from the UI Manager
2. **Tab Switching Function** - Self-contained tab switching
3. **HTML Panel Protection** - To prevent the panel from being hidden
4. **Basic Chat Functionality** - For team chat
5. **Component Initialization** - For proper setup and loading
6. **Component Load Error Handling** - For graceful error management

```javascript
// UI Manager Protection
if (window.uiManager) {
    window.uiManager._ignoreComponent = 'rhetor';
    console.log('[RHETOR] Set UI Manager to ignore rhetor component');
}

// Tab Switching Function
window.rhetor_switchTab = function(tabId) {
    console.log('[RHETOR] Switching to tab:', tabId);
    
    // Force HTML panel visibility
    const htmlPanelElements = document.querySelectorAll('#html-panel');
    htmlPanelElements.forEach(panel => {
        if (panel) panel.style.display = 'block';
    });
    
    try {
        // Only select elements within rhetor component
        const rhetorContainer = document.querySelector('.rhetor');
        if (!rhetorContainer) {
            console.error('[RHETOR] Tab Switch: Cannot find rhetor container');
            return false;
        }
        
        // Update tab active state
        const tabs = rhetorContainer.querySelectorAll('.rhetor__tab');
        tabs.forEach(tab => {
            if (tab.getAttribute('data-tab') === tabId) {
                tab.classList.add('rhetor__tab--active');
            } else {
                tab.classList.remove('rhetor__tab--active');
            }
        });
        
        // Update panel visibility
        const panels = rhetorContainer.querySelectorAll('.rhetor__panel');
        panels.forEach(panel => {
            const panelId = panel.id;
            if (panelId === tabId + '-panel') {
                panel.style.display = 'block';
                panel.classList.add('rhetor__panel--active');
            } else {
                panel.style.display = 'none';
                panel.classList.remove('rhetor__panel--active');
            }
        });
        
        // Update clear button visibility for chat tabs
        const clearButton = rhetorContainer.querySelector('#clear-chat-btn');
        if (clearButton) {
            clearButton.style.display = (tabId === 'chat' || tabId === 'teamchat') ? 'block' : 'none';
        }
        
        // Update component state
        if (window.rhetorComponent) {
            window.rhetorComponent.state = window.rhetorComponent.state || {};
            window.rhetorComponent.state.activeTab = tabId;
            
            // Call component-specific methods if available
            if (typeof window.rhetorComponent.saveComponentState === 'function') {
                window.rhetorComponent.saveComponentState();
            }
        }
    } catch (err) {
        console.error('[RHETOR] Error in tab switching:', err);
    }
    
    return false; // Stop event propagation
};

// Clear Chat Function
window.rhetor_clearChat = function() {
    console.log('[RHETOR] Clear chat clicked');
    
    try {
        // Get active tab ID within rhetor container
        const rhetorContainer = document.querySelector('.rhetor');
        if (!rhetorContainer) {
            console.error('[RHETOR] Clear Chat: Cannot find rhetor container');
            return false;
        }
        
        const activeTab = rhetorContainer.querySelector('.rhetor__tab--active');
        const tabId = activeTab ? activeTab.getAttribute('data-tab') : '';
        
        if (tabId === 'teamchat') {
            // Get message container within rhetor container only
            const panel = rhetorContainer.querySelector('#' + tabId + '-messages');
            if (panel) {
                // Keep welcome message
                const welcomeMsg = panel.querySelector('.rhetor__message--system');
                if (welcomeMsg) {
                    panel.innerHTML = '';
                    panel.appendChild(welcomeMsg);
                    console.log('[RHETOR] Cleared chat, kept welcome message');
                } else {
                    panel.innerHTML = '';
                    console.log('[RHETOR] Cleared chat completely');
                }
            }
        }
    } catch (err) {
        console.error('[RHETOR] Error clearing chat:', err);
    }
    
    return false; // Stop event propagation
};
```

## Implementation Steps

### Step 1: Create Component Skeleton

Create the basic structure using the template from previous components:

1. Create rhetor-component.html with basic BEM structure
2. Add component-specific CSS styles within the HTML
3. Add bare-bones JavaScript functionality for tab switching

### Step 2: Implement Writing Panel

Implement the Writing panel with:

1. Text editor area
2. Formatting options
3. Document controls (save, export, etc.)

### Step 3: Implement Templates Panel

Implement the Templates panel with:

1. Template list
2. Template preview
3. Apply template functionality

### Step 4: Implement Revision Panel

Implement the Revision panel with:

1. Document history
2. Version comparison
3. Revert/restore functionality

### Step 5: Implement Format Panel

Implement the Format panel with:

1. Text formatting options
2. Style presets
3. Export format options

### Step 6: Implement Team Chat Panel

Implement the Team Chat panel with consistent chat UI:

1. Team Chat panel matching the implementation in other components

### Step 7: Test and Verify

Ensure the component works properly and follows all patterns:

1. Test loading in isolation
2. Test compatibility with other components
3. Verify tab switching works properly
4. Ensure protection from UI Manager interference

## Key Considerations

1. **Visual Consistency**: Ensure the Rhetor component visually matches other components (header, menu bar, footer heights)
2. **Component Isolation**: Prevent any leaking of styles or behavior to other components
3. **Error Handling**: Gracefully handle loading and runtime errors
4. **Debug Instrumentation**: Add comprehensive logging with component prefix
5. **Performance**: Optimize for performance, especially with text editing and formatting

## Implementation Schedule

- **Day 1**: Create component skeleton and implement Writing panel
- **Day 2**: Implement Templates and Revision panels
- **Day 3**: Implement Format panel and Team Chat panel
- **Day 4**: Testing, fixes, and documentation

## Success Criteria

The implementation will be considered successful when:

1. Rhetor component loads and displays correctly
2. All tabs function properly without interference
3. Component maintains isolation from other components
4. UI is visually consistent with other components
5. All functionality works as expected
6. No errors or warnings appear in console
7. Debug instrumentation is complete and functional

## Reference Components

Use these components as reference for implementation patterns:

1. **Athena Component**: For the overall structure and tab switching
2. **Hermes Component**: For chat functionality
3. **Engram Component**: For panel organization and content display
4. **Debug Instrumentation**: Use the debug-shim.js pattern for logging

These reference implementations provide proven patterns to follow for a successful Rhetor component implementation.