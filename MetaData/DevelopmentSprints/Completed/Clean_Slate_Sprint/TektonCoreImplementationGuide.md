# Tekton Core Implementation Guide

## Overview

This document provides detailed guidance for implementing the Tekton Core component following the Clean Slate architecture. Tekton Core is the central project management hub of the Tekton platform, focusing primarily on GitHub project management and providing a unified interface for working with repositories, branches, and development workflows.

## Implementation Approach

The implementation will strictly follow the Clean Slate architecture principles with Athena as the reference model:

1. Implement component with proper BEM naming convention
2. Ensure strict component isolation
3. Use consistent HTML structure and styling with other components
4. Add proper protection from UI Manager interference
5. Implement self-contained tab switching functionality
6. Add comprehensive debug instrumentation

## Required Files

The following files need to be implemented or updated:

1. **Component HTML**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/tekton/tekton-component.html`
2. **Component JavaScript**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/tekton/tekton-component.js`
3. **GitHub Service**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/tekton/github-service.js`
4. **Projects Manager**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/tekton/project-manager.js`

## HTML Component Structure

The HTML structure should follow the Athena component template exactly, with Tekton Core-specific content:

```html
<!-- Tekton Core Component - Project Management -->
<div class="tekton">
    <!-- Component Header with Title -->
    <div class="tekton__header">
        <div class="tekton__title-container">
            <img src="/images/Tekton.png" alt="Tekton" class="tekton__icon">
            <h2 class="tekton__title">
                <span class="tekton__title-main">Tekton</span>
                <span class="tekton__title-sub">Project Management</span>
            </h2>
        </div>
    </div>
    
    <!-- Tekton Menu Bar with Tab Navigation -->
    <div class="tekton__menu-bar">
        <div class="tekton__tabs">
            <div class="tekton__tab tekton__tab--active" data-tab="projects" onclick="tekton_switchTab('projects'); return false;">
                <span class="tekton__tab-label">Projects</span>
            </div>
            <div class="tekton__tab" data-tab="repositories" onclick="tekton_switchTab('repositories'); return false;">
                <span class="tekton__tab-label">Repositories</span>
            </div>
            <div class="tekton__tab" data-tab="branches" onclick="tekton_switchTab('branches'); return false;">
                <span class="tekton__tab-label">Branches</span>
            </div>
            <div class="tekton__tab" data-tab="actions" onclick="tekton_switchTab('actions'); return false;">
                <span class="tekton__tab-label">Actions</span>
            </div>
            <div class="tekton__tab" data-tab="projectchat" onclick="tekton_switchTab('projectchat'); return false;">
                <span class="tekton__tab-label">Project Chat</span>
            </div>
            <div class="tekton__tab" data-tab="teamchat" onclick="tekton_switchTab('teamchat'); return false;">
                <span class="tekton__tab-label">Team Chat</span>
            </div>
        </div>
        <div class="tekton__actions">
            <button id="clear-chat-btn" class="tekton__action-button" style="display: none;" onclick="tekton_clearChat(); return false;">
                <span class="tekton__button-label">Clear</span>
            </button>
        </div>
    </div>
    
    <!-- Tekton Content Area -->
    <div class="tekton__content">
        <!-- Projects Tab (Default Active Tab) -->
        <div id="projects-panel" class="tekton__panel tekton__panel--active">
            <div class="tekton__projects">
                <div class="tekton__control-bar">
                    <div class="tekton__search-container">
                        <input type="text" id="project-search" class="tekton__search-input" placeholder="Search projects...">
                        <button id="project-search-btn" class="tekton__search-button">Search</button>
                    </div>
                    <div class="tekton__actions">
                        <button id="new-project-btn" class="tekton__action-button">
                            <span class="tekton__button-icon">+</span>
                            <span class="tekton__button-label">New Project</span>
                        </button>
                        <button id="import-project-btn" class="tekton__action-button">
                            <span class="tekton__button-icon">↓</span>
                            <span class="tekton__button-label">Import</span>
                        </button>
                    </div>
                </div>
                <div class="tekton__project-list-container">
                    <div id="project-list-loading" class="tekton__loading-indicator">
                        <div class="tekton__spinner"></div>
                        <div class="tekton__loading-text">Loading projects...</div>
                    </div>
                    <div id="project-list" class="tekton__project-list" style="display: none;">
                        <!-- Sample projects for UI testing -->
                        <div class="tekton__project-item">
                            <div class="tekton__project-info">
                                <div class="tekton__project-name">Tekton</div>
                                <div class="tekton__project-meta">
                                    <span class="tekton__project-repo">cskoons/Tekton</span>
                                    <span class="tekton__project-branch">sprint/Clean_Slate_051125</span>
                                </div>
                            </div>
                            <div class="tekton__project-actions">
                                <button class="tekton__project-action-btn">Open</button>
                                <button class="tekton__project-action-btn">Settings</button>
                            </div>
                        </div>
                        <div class="tekton__project-item">
                            <div class="tekton__project-info">
                                <div class="tekton__project-name">Sample Project</div>
                                <div class="tekton__project-meta">
                                    <span class="tekton__project-repo">cskoons/sample-project</span>
                                    <span class="tekton__project-branch">main</span>
                                </div>
                            </div>
                            <div class="tekton__project-actions">
                                <button class="tekton__project-action-btn">Open</button>
                                <button class="tekton__project-action-btn">Settings</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Repositories Tab -->
        <div id="repositories-panel" class="tekton__panel">
            <div class="tekton__repositories">
                <div class="tekton__control-bar">
                    <div class="tekton__search-container">
                        <input type="text" id="repo-search" class="tekton__search-input" placeholder="Search repositories...">
                        <button id="repo-search-btn" class="tekton__search-button">Search</button>
                    </div>
                    <div class="tekton__actions">
                        <button id="clone-repo-btn" class="tekton__action-button">
                            <span class="tekton__button-icon">↓</span>
                            <span class="tekton__button-label">Clone</span>
                        </button>
                        <button id="create-repo-btn" class="tekton__action-button">
                            <span class="tekton__button-icon">+</span>
                            <span class="tekton__button-label">Create</span>
                        </button>
                    </div>
                </div>
                <div class="tekton__repositories-list-container">
                    <div id="repositories-list-loading" class="tekton__loading-indicator">
                        <div class="tekton__spinner"></div>
                        <div class="tekton__loading-text">Loading repositories...</div>
                    </div>
                    <div id="repositories-list" class="tekton__repositories-list" style="display: none;">
                        <table class="tekton__repositories-table">
                            <thead>
                                <tr>
                                    <th>Repository</th>
                                    <th>Owner</th>
                                    <th>Branches</th>
                                    <th>Last Updated</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Sample repositories for UI testing -->
                                <tr class="tekton__repository-row">
                                    <td>Tekton</td>
                                    <td>cskoons</td>
                                    <td>4</td>
                                    <td>Today</td>
                                    <td>
                                        <button class="tekton__table-action-btn">Open</button>
                                        <button class="tekton__table-action-btn">Fork</button>
                                    </td>
                                </tr>
                                <tr class="tekton__repository-row">
                                    <td>sample-project</td>
                                    <td>cskoons</td>
                                    <td>1</td>
                                    <td>Yesterday</td>
                                    <td>
                                        <button class="tekton__table-action-btn">Open</button>
                                        <button class="tekton__table-action-btn">Fork</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Branches Tab -->
        <div id="branches-panel" class="tekton__panel">
            <div class="tekton__branches">
                <div class="tekton__control-bar">
                    <div class="tekton__filter-container">
                        <select id="repo-filter" class="tekton__filter-select">
                            <option value="all">All Repositories</option>
                            <option value="tekton">Tekton</option>
                            <option value="sample">sample-project</option>
                        </select>
                        <button id="apply-filter-btn" class="tekton__filter-button">Apply</button>
                    </div>
                    <div class="tekton__actions">
                        <button id="create-branch-btn" class="tekton__action-button">
                            <span class="tekton__button-icon">+</span>
                            <span class="tekton__button-label">New Branch</span>
                        </button>
                        <button id="merge-branch-btn" class="tekton__action-button">
                            <span class="tekton__button-icon">⋈</span>
                            <span class="tekton__button-label">Merge</span>
                        </button>
                    </div>
                </div>
                <div class="tekton__branches-list-container">
                    <div id="branches-list-loading" class="tekton__loading-indicator">
                        <div class="tekton__spinner"></div>
                        <div class="tekton__loading-text">Loading branches...</div>
                    </div>
                    <div id="branches-list" class="tekton__branches-list" style="display: none;">
                        <table class="tekton__branches-table">
                            <thead>
                                <tr>
                                    <th>Branch</th>
                                    <th>Repository</th>
                                    <th>Status</th>
                                    <th>Last Commit</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Sample branches for UI testing -->
                                <tr class="tekton__branch-row">
                                    <td>main</td>
                                    <td>Tekton</td>
                                    <td>Current</td>
                                    <td>2 days ago</td>
                                    <td>
                                        <button class="tekton__table-action-btn">Checkout</button>
                                        <button class="tekton__table-action-btn">Pull</button>
                                    </td>
                                </tr>
                                <tr class="tekton__branch-row tekton__branch-row--active">
                                    <td>sprint/Clean_Slate_051125</td>
                                    <td>Tekton</td>
                                    <td>Active</td>
                                    <td>Today</td>
                                    <td>
                                        <button class="tekton__table-action-btn">Checkout</button>
                                        <button class="tekton__table-action-btn">Pull</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Actions Tab -->
        <div id="actions-panel" class="tekton__panel">
            <div class="tekton__actions-panel">
                <h3 class="tekton__section-title">GitHub Actions</h3>
                
                <div class="tekton__action-cards">
                    <div class="tekton__action-card">
                        <h4 class="tekton__action-card-title">Repository Operations</h4>
                        <div class="tekton__action-card-content">
                            <button class="tekton__card-action-btn">Clone Repository</button>
                            <button class="tekton__card-action-btn">Create Repository</button>
                            <button class="tekton__card-action-btn">Fork Repository</button>
                        </div>
                    </div>
                    
                    <div class="tekton__action-card">
                        <h4 class="tekton__action-card-title">Branch Management</h4>
                        <div class="tekton__action-card-content">
                            <button class="tekton__card-action-btn">Create Branch</button>
                            <button class="tekton__card-action-btn">Merge Branch</button>
                            <button class="tekton__card-action-btn">Sync Branch</button>
                            <button class="tekton__card-action-btn">Delete Branch</button>
                        </div>
                    </div>
                    
                    <div class="tekton__action-card">
                        <h4 class="tekton__action-card-title">Commit Operations</h4>
                        <div class="tekton__action-card-content">
                            <button class="tekton__card-action-btn">Create Commit</button>
                            <button class="tekton__card-action-btn">Push Changes</button>
                            <button class="tekton__card-action-btn">Pull Changes</button>
                            <button class="tekton__card-action-btn">View History</button>
                        </div>
                    </div>
                    
                    <div class="tekton__action-card">
                        <h4 class="tekton__action-card-title">Pull Requests</h4>
                        <div class="tekton__action-card-content">
                            <button class="tekton__card-action-btn">Create PR</button>
                            <button class="tekton__card-action-btn">List PRs</button>
                            <button class="tekton__card-action-btn">Review PR</button>
                            <button class="tekton__card-action-btn">Merge PR</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Project Chat Tab -->
        <div id="projectchat-panel" class="tekton__panel">
            <div id="projectchat-messages" class="tekton__chat-messages">
                <!-- Welcome message -->
                <div class="tekton__message tekton__message--system">
                    <div class="tekton__message-content">
                        <div class="tekton__message-text">
                            <h3 class="tekton__message-title">Project Management Assistant</h3>
                            <p>This chat provides assistance with GitHub project management. Ask questions about:</p>
                            <ul>
                                <li>Repository management and setup</li>
                                <li>Branch strategies and workflows</li>
                                <li>Pull requests and code reviews</li>
                                <li>Best practices for GitHub projects</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Team Chat Tab -->
        <div id="teamchat-panel" class="tekton__panel">
            <div id="teamchat-messages" class="tekton__chat-messages">
                <!-- Welcome message -->
                <div class="tekton__message tekton__message--system">
                    <div class="tekton__message-content">
                        <div class="tekton__message-text">
                            <h3 class="tekton__message-title">Tekton Team Chat</h3>
                            <p>This chat is shared across all Tekton components. Use this for team communication and coordination.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Footer with Chat Input -->
    <div class="tekton__footer">
        <div class="tekton__chat-input-container">
            <div class="tekton__chat-prompt">></div>
            <input type="text" id="chat-input" class="tekton__chat-input" 
                   placeholder="Enter chat message, project query, or GitHub command">
            <button id="send-button" class="tekton__send-button">Send</button>
        </div>
    </div>
</div>
```

## CSS Styling

The CSS should follow Athena's BEM naming structure, maintaining the same visual appearance and layout but with Tekton-specific color scheme:

```css
/* Tekton component styles using BEM naming convention */

/* Container */
.tekton {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    background-color: var(--bg-primary, #1e1e2e);
    color: var(--text-primary, #f0f0f0);
    /* No absolute positioning - proper component containment */
}

/* Header */
.tekton__header {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 50px; /* Match header height from Athena */
}

.tekton__title-container {
    display: flex;
    align-items: center;
}

.tekton__icon {
    height: 30px;
    width: auto;
    margin-right: 12px;
}

.tekton__title {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 500;
}

.tekton__title-sub {
    margin-left: 8px;
    opacity: 0.8;
    font-weight: normal;
}

/* Menu Bar */
.tekton__menu-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 46px; /* Match menu bar height from Athena */
}

.tekton__tabs {
    display: flex;
    gap: 8px;
}

.tekton__tab {
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

.tekton__tab:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

.tekton__tab--active {
    border-bottom-color: var(--color-primary, #7B1FA2); /* Tekton purple color */
    font-weight: 500;
}

/* Content styles */
.tekton__content {
    flex: 1;
    overflow: hidden;
    position: relative;
}

.tekton__panel {
    display: none;
    height: 100%;
    width: 100%;
    overflow: auto;
    padding: 16px;
}

.tekton__panel--active {
    display: block;
}

/* Table Styles */
.tekton__repositories-table,
.tekton__branches-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
}

.tekton__repositories-table th,
.tekton__branches-table th {
    background-color: var(--bg-secondary, #252535);
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid var(--border-color, #444444);
}

.tekton__repositories-table td,
.tekton__branches-table td {
    padding: 10px;
    border-bottom: 1px solid var(--border-color, #33333f);
}

.tekton__repository-row:hover,
.tekton__branch-row:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

/* Project List Styles */
.tekton__project-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 16px;
}

.tekton__project-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px;
    background-color: var(--bg-secondary, #252535);
    border-radius: 6px;
    border: 1px solid var(--border-color, #444444);
}

.tekton__project-name {
    font-size: 1.1rem;
    font-weight: 500;
    margin-bottom: 4px;
}

.tekton__project-meta {
    font-size: 0.85rem;
    opacity: 0.8;
    display: flex;
    gap: 12px;
}

/* Action Cards */
.tekton__action-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 16px;
    margin-top: 16px;
}

.tekton__action-card {
    background-color: var(--bg-secondary, #252535);
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tekton__action-card-title {
    margin-top: 0;
    margin-bottom: 12px;
    font-size: 1.1rem;
    border-bottom: 1px solid var(--border-color, #444444);
    padding-bottom: 8px;
}

.tekton__action-card-content {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

/* Chat Styles */
.tekton__chat-messages {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 16px;
    height: 100%;
    overflow-y: auto;
}

.tekton__message {
    display: flex;
    flex-direction: column;
    max-width: 90%;
}

.tekton__message--user {
    align-self: flex-end;
}

.tekton__message--system {
    align-self: center;
    max-width: 580px;
}

.tekton__message-content {
    background-color: var(--bg-tertiary, #333345);
    border-radius: 8px;
    padding: 12px 16px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.tekton__message--user .tekton__message-content {
    background-color: var(--color-primary, #7B1FA2);
}

.tekton__message-title {
    margin-top: 0;
    margin-bottom: 8px;
    font-size: 1.1rem;
}

/* Footer */
.tekton__footer {
    padding: 12px 16px;
    background-color: var(--bg-secondary, #252535);
    border-top: 1px solid var(--border-color, #444444);
    height: 70px; /* Match footer height from Athena */
}

.tekton__chat-input-container {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
}

.tekton__chat-prompt {
    font-family: monospace;
    font-size: 1.2rem;
    color: var(--color-primary, #7B1FA2);
}

.tekton__chat-input {
    flex: 1;
    background-color: var(--bg-tertiary, #333345);
    border: 1px solid var(--border-color, #444444);
    color: var(--text-primary, #f0f0f0);
    padding: 10px 12px;
    border-radius: 4px;
    font-size: 0.95rem;
}

.tekton__send-button {
    background-color: var(--color-primary, #7B1FA2);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 16px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.2s ease;
}

.tekton__send-button:hover {
    background-color: var(--color-primary-hover, #9C27B0);
}
```

## JavaScript Implementation

The JavaScript should follow Athena's pattern with these key features:

1. **UI Manager Protection** - Prevent interference from UI Manager
2. **HTML Panel Protection** - Keep the HTML panel visible
3. **Tab Switching** - Handle tab switching with component isolation
4. **Team Chat** - Implement shared team chat functionality
5. **Error Handling** - Robust error handling and debugging support

```javascript
// SIMPLIFIED COMPONENT SCRIPT - FULLY SELF-CONTAINED
// This version minimizes interference with other components

// IMMEDIATELY SET UP UI MANAGER PROTECTION
// Tell UI Manager to ignore this component - must be done IMMEDIATELY to avoid races
if (window.uiManager) {
    window.uiManager._ignoreComponent = 'tekton';
    console.log('[TEKTON] Set UI Manager to ignore tekton component');
}

// DEFINE TAB SWITCHING FUNCTION
// CRITICAL: This uses no shared code/utilities to avoid conflicts
window.tekton_switchTab = function(tabId) {
    console.log('[TEKTON] Switching to tab:', tabId);
    
    // Force HTML panel visibility
    const htmlPanelElements = document.querySelectorAll('#html-panel');
    htmlPanelElements.forEach(panel => {
        if (panel) panel.style.display = 'block';
    });
    
    try {
        // Only select elements within tekton component to avoid conflicts with other components
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) {
            console.error('[TEKTON] Tab Switch: Cannot find tekton container');
            return false;
        }
        
        // Update tab active state - ONLY WITHIN TEKTON CONTAINER
        const tabs = tektonContainer.querySelectorAll('.tekton__tab');
        tabs.forEach(tab => {
            if (tab.getAttribute('data-tab') === tabId) {
                tab.classList.add('tekton__tab--active');
            } else {
                tab.classList.remove('tekton__tab--active');
            }
        });
        
        // Update panel visibility - ONLY WITHIN TEKTON CONTAINER
        const panels = tektonContainer.querySelectorAll('.tekton__panel');
        panels.forEach(panel => {
            const panelId = panel.id;
            if (panelId === tabId + '-panel') {
                panel.style.display = 'block';
                panel.classList.add('tekton__panel--active');
            } else {
                panel.style.display = 'none';
                panel.classList.remove('tekton__panel--active');
            }
        });
        
        // Update clear button visibility for chat tabs
        const clearButton = tektonContainer.querySelector('#clear-chat-btn');
        if (clearButton) {
            clearButton.style.display = (tabId === 'projectchat' || tabId === 'teamchat') ? 'block' : 'none';
        }
        
        // Update component state
        if (window.tektonComponent) {
            window.tektonComponent.state = window.tektonComponent.state || {};
            window.tektonComponent.state.activeTab = tabId;
            
            // Call component-specific methods if available
            if (typeof window.tektonComponent.updateChatPlaceholder === 'function') {
                window.tektonComponent.updateChatPlaceholder(tabId);
            }
            
            if (typeof window.tektonComponent.loadTabContent === 'function') {
                window.tektonComponent.loadTabContent(tabId);
            }
            
            if (typeof window.tektonComponent.saveComponentState === 'function') {
                window.tektonComponent.saveComponentState();
            }
        }
    } catch (err) {
        console.error('[TEKTON] Error in tab switching:', err);
    }
    
    return false; // Stop event propagation
};

// CHAT CLEARING FUNCTION
window.tekton_clearChat = function() {
    console.log('[TEKTON] Clearing chat messages');
    
    try {
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) {
            console.error('[TEKTON] Clear Chat: Cannot find tekton container');
            return false;
        }
        
        // Determine which chat to clear based on active tab
        const activeTab = tektonContainer.querySelector('.tekton__tab--active');
        if (!activeTab) {
            console.error('[TEKTON] Clear Chat: Cannot determine active tab');
            return false;
        }
        
        const chatType = activeTab.getAttribute('data-tab');
        let chatContainer;
        
        if (chatType === 'projectchat') {
            chatContainer = tektonContainer.querySelector('#projectchat-messages');
        } else if (chatType === 'teamchat') {
            chatContainer = tektonContainer.querySelector('#teamchat-messages');
        }
        
        if (!chatContainer) {
            console.error('[TEKTON] Clear Chat: Cannot find chat container for', chatType);
            return false;
        }
        
        // Keep only the system welcome message
        const welcomeMessage = chatContainer.querySelector('.tekton__message--system');
        if (welcomeMessage) {
            chatContainer.innerHTML = '';
            chatContainer.appendChild(welcomeMessage);
        } else {
            chatContainer.innerHTML = '';
        }
        
        console.log('[TEKTON] Chat messages cleared for', chatType);
    } catch (err) {
        console.error('[TEKTON] Error in clearing chat:', err);
    }
    
    return false; // Stop event propagation
};
```

## Isolated Component JavaScript

Create a separate file `tekton-component.js` that follows the same structure as Athena's component JS:

```javascript
/**
 * Tekton Core Component
 * 
 * Provides a comprehensive interface for GitHub project management,
 * including repositories, branches, pull requests, and project workflows.
 */

import { GitHubService } from './github-service.js';
import { ProjectManager } from './project-manager.js';

class TektonComponent {
    constructor() {
        this.gitHubService = new GitHubService();
        this.projectManager = new ProjectManager(this.gitHubService);
        this.state = {
            activeTab: 'projects',
            projects: [],
            repositories: [],
            branches: [],
            loading: false
        };
        
        console.log('[TEKTON] Component constructed');
    }
    
    async init() {
        console.log('[TEKTON] Initializing component');
        this.setupEventListeners();
        this.loadProjects();
    }
    
    setupEventListeners() {
        // Find our component container
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) {
            console.error('[TEKTON] Cannot find tekton container for setting up event listeners');
            return;
        }
        
        // Set up chat input
        const chatInput = tektonContainer.querySelector('#chat-input');
        const sendButton = tektonContainer.querySelector('#send-button');
        
        if (chatInput && sendButton) {
            // Send message on button click
            sendButton.addEventListener('click', () => this.sendChatMessage());
            
            // Send message on Enter key
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendChatMessage();
                }
            });
        }
        
        // Set up Projects tab events
        const newProjectBtn = tektonContainer.querySelector('#new-project-btn');
        if (newProjectBtn) {
            newProjectBtn.addEventListener('click', () => this.createNewProject());
        }
        
        const importProjectBtn = tektonContainer.querySelector('#import-project-btn');
        if (importProjectBtn) {
            importProjectBtn.addEventListener('click', () => this.importProject());
        }
        
        // Set up Repositories tab events
        const cloneRepoBtn = tektonContainer.querySelector('#clone-repo-btn');
        if (cloneRepoBtn) {
            cloneRepoBtn.addEventListener('click', () => this.cloneRepository());
        }
        
        const createRepoBtn = tektonContainer.querySelector('#create-repo-btn');
        if (createRepoBtn) {
            createRepoBtn.addEventListener('click', () => this.createRepository());
        }
        
        // Set up Branches tab events
        const createBranchBtn = tektonContainer.querySelector('#create-branch-btn');
        if (createBranchBtn) {
            createBranchBtn.addEventListener('click', () => this.createBranch());
        }
        
        const mergeBranchBtn = tektonContainer.querySelector('#merge-branch-btn');
        if (mergeBranchBtn) {
            mergeBranchBtn.addEventListener('click', () => this.mergeBranch());
        }
    }
    
    async loadProjects() {
        console.log('[TEKTON] Loading projects');
        try {
            // Toggle loading indicator
            this.toggleLoading('project-list', true);
            
            // Fetch projects from the project manager
            const projects = await this.projectManager.getProjects();
            this.state.projects = projects;
            
            // Update the UI with projects
            this.renderProjects();
        } catch (error) {
            console.error('[TEKTON] Error loading projects:', error);
            this.showErrorMessage('Failed to load projects');
        } finally {
            // Hide loading indicator
            this.toggleLoading('project-list', false);
        }
    }
    
    renderProjects() {
        console.log('[TEKTON] Rendering projects:', this.state.projects.length);
        // In a real implementation, this would render actual project data
    }
    
    // Chat Functionality
    
    sendChatMessage() {
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) return;
        
        const chatInput = tektonContainer.querySelector('#chat-input');
        if (!chatInput || !chatInput.value.trim()) return;
        
        const message = chatInput.value.trim();
        const activeTab = this.state.activeTab;
        
        if (activeTab === 'projectchat' || activeTab === 'teamchat') {
            this.addChatMessage(message, activeTab);
            chatInput.value = '';
        }
    }
    
    addChatMessage(message, chatType) {
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) return;
        
        let chatContainer;
        if (chatType === 'projectchat') {
            chatContainer = tektonContainer.querySelector('#projectchat-messages');
        } else if (chatType === 'teamchat') {
            chatContainer = tektonContainer.querySelector('#teamchat-messages');
        }
        
        if (!chatContainer) return;
        
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = 'tekton__message tekton__message--user';
        
        messageEl.innerHTML = `
            <div class="tekton__message-content">
                <div class="tekton__message-text">${message}</div>
            </div>
        `;
        
        // Add to chat container
        chatContainer.appendChild(messageEl);
        
        // Auto-scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // In a real implementation, this would send the message to an actual chat service
        // and potentially generate a response
    }
    
    // Helper methods
    
    toggleLoading(elementId, isLoading) {
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) return;
        
        const loadingIndicator = tektonContainer.querySelector(`#${elementId}-loading`);
        const contentElement = tektonContainer.querySelector(`#${elementId}`);
        
        if (loadingIndicator && contentElement) {
            if (isLoading) {
                loadingIndicator.style.display = 'flex';
                contentElement.style.display = 'none';
            } else {
                loadingIndicator.style.display = 'none';
                contentElement.style.display = '';
            }
        }
    }
    
    showErrorMessage(message) {
        console.error('[TEKTON] Error:', message);
        // In a real implementation, this would show an error UI
    }
    
    updateChatPlaceholder(tabId) {
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) return;
        
        const chatInput = tektonContainer.querySelector('#chat-input');
        if (!chatInput) return;
        
        if (tabId === 'projectchat') {
            chatInput.placeholder = 'Ask about GitHub projects, repositories, branches...';
        } else if (tabId === 'teamchat') {
            chatInput.placeholder = 'Chat with your team...';
        } else {
            chatInput.placeholder = 'Enter chat message, project query, or GitHub command';
        }
    }
    
    loadTabContent(tabId) {
        console.log(`[TEKTON] Loading content for ${tabId} tab`);
        
        switch (tabId) {
            case 'projects':
                this.loadProjects();
                break;
            case 'repositories':
                this.loadRepositories();
                break;
            case 'branches':
                this.loadBranches();
                break;
            case 'actions':
                // Nothing to load for actions tab
                break;
        }
    }
    
    async loadRepositories() {
        console.log('[TEKTON] Loading repositories');
        try {
            this.toggleLoading('repositories-list', true);
            const repositories = await this.gitHubService.getRepositories();
            this.state.repositories = repositories;
            this.renderRepositories();
        } catch (error) {
            console.error('[TEKTON] Error loading repositories:', error);
            this.showErrorMessage('Failed to load repositories');
        } finally {
            this.toggleLoading('repositories-list', false);
        }
    }
    
    async loadBranches() {
        console.log('[TEKTON] Loading branches');
        try {
            this.toggleLoading('branches-list', true);
            const branches = await this.gitHubService.getBranches();
            this.state.branches = branches;
            this.renderBranches();
        } catch (error) {
            console.error('[TEKTON] Error loading branches:', error);
            this.showErrorMessage('Failed to load branches');
        } finally {
            this.toggleLoading('branches-list', false);
        }
    }
    
    renderRepositories() {
        console.log('[TEKTON] Rendering repositories:', this.state.repositories.length);
        // In a real implementation, this would render actual repository data
    }
    
    renderBranches() {
        console.log('[TEKTON] Rendering branches:', this.state.branches.length);
        // In a real implementation, this would render actual branch data
    }
    
    // GitHub operations
    
    createNewProject() {
        console.log('[TEKTON] Creating new project');
        // In a real implementation, this would show a new project dialog
    }
    
    importProject() {
        console.log('[TEKTON] Importing project');
        // In a real implementation, this would show an import project dialog
    }
    
    cloneRepository() {
        console.log('[TEKTON] Cloning repository');
        // In a real implementation, this would show a clone repository dialog
    }
    
    createRepository() {
        console.log('[TEKTON] Creating repository');
        // In a real implementation, this would show a create repository dialog
    }
    
    createBranch() {
        console.log('[TEKTON] Creating branch');
        // In a real implementation, this would show a create branch dialog
    }
    
    mergeBranch() {
        console.log('[TEKTON] Merging branch');
        // In a real implementation, this would show a merge branch dialog
    }
    
    saveComponentState() {
        // Save component state to localStorage or similar for persistence
        console.log('[TEKTON] Saving component state');
        try {
            const stateToSave = {
                activeTab: this.state.activeTab
            };
            localStorage.setItem('tektonComponentState', JSON.stringify(stateToSave));
        } catch (error) {
            console.error('[TEKTON] Error saving component state:', error);
        }
    }
    
    loadComponentState() {
        // Load component state from localStorage or similar
        console.log('[TEKTON] Loading component state');
        try {
            const savedState = localStorage.getItem('tektonComponentState');
            if (savedState) {
                const parsedState = JSON.parse(savedState);
                if (parsedState.activeTab) {
                    this.state.activeTab = parsedState.activeTab;
                    tekton_switchTab(this.state.activeTab);
                }
            }
        } catch (error) {
            console.error('[TEKTON] Error loading component state:', error);
        }
    }
}

// Create global instance
window.tektonComponent = new TektonComponent();

// Initialize the component when the script loads
window.tektonComponent.init();
```

## Service JavaScript Files

Create the necessary service files that follow the pattern from Athena:

1. **github-service.js**: For GitHub API communication via MCP functions
2. **project-manager.js**: For project management functionality

### GitHub Service

```javascript
/**
 * GitHub Service
 * Provides an interface to GitHub functionality via MCP functions
 */
export class GitHubService {
    constructor() {
        console.log('[TEKTON] GitHubService initialized');
    }
    
    async getRepositories() {
        console.log('[TEKTON] Getting repositories');
        try {
            // In a real implementation, this would use MCP functions to fetch repositories
            // Example of using MCP function:
            // const result = await window.mcp.github.searchRepositories({ q: 'user:cskoons' });
            
            // For now, return mock data
            return [
                { name: 'Tekton', owner: 'cskoons', branches: 4, updated: new Date() },
                { name: 'sample-project', owner: 'cskoons', branches: 1, updated: new Date(Date.now() - 86400000) }
            ];
        } catch (error) {
            console.error('[TEKTON] Error getting repositories:', error);
            throw error;
        }
    }
    
    async getBranches() {
        console.log('[TEKTON] Getting branches');
        try {
            // In a real implementation, this would use MCP functions to fetch branches
            // Example of using MCP function:
            // const result = await window.mcp.github.listBranches({ owner: 'cskoons', repo: 'Tekton' });
            
            // For now, return mock data
            return [
                { name: 'main', repository: 'Tekton', status: 'Current', lastCommit: new Date(Date.now() - 172800000) },
                { name: 'sprint/Clean_Slate_051125', repository: 'Tekton', status: 'Active', lastCommit: new Date() }
            ];
        } catch (error) {
            console.error('[TEKTON] Error getting branches:', error);
            throw error;
        }
    }
    
    async createRepository(options) {
        console.log('[TEKTON] Creating repository:', options);
        try {
            // In a real implementation, this would use MCP functions to create a repository
            // Example of using MCP function:
            // const result = await window.mcp.github.createRepository({ 
            //     name: options.name,
            //     description: options.description,
            //     private: options.private
            // });
            
            return { success: true, name: options.name };
        } catch (error) {
            console.error('[TEKTON] Error creating repository:', error);
            throw error;
        }
    }
    
    async cloneRepository(options) {
        console.log('[TEKTON] Cloning repository:', options);
        try {
            // In a real implementation, this would use MCP functions or backend API to clone a repository
            return { success: true, repository: options.repository };
        } catch (error) {
            console.error('[TEKTON] Error cloning repository:', error);
            throw error;
        }
    }
    
    async createBranch(options) {
        console.log('[TEKTON] Creating branch:', options);
        try {
            // In a real implementation, this would use MCP functions to create a branch
            // Example of using MCP function:
            // const result = await window.mcp.github.createBranch({ 
            //     owner: options.owner,
            //     repo: options.repo,
            //     branch: options.branch,
            //     from_branch: options.baseBranch
            // });
            
            return { success: true, branch: options.branch };
        } catch (error) {
            console.error('[TEKTON] Error creating branch:', error);
            throw error;
        }
    }
    
    async mergeBranch(options) {
        console.log('[TEKTON] Merging branch:', options);
        try {
            // In a real implementation, this would use MCP functions to merge branches
            // Example of using MCP function:
            // const result = await window.mcp.github.mergeBranch({ 
            //     owner: options.owner,
            //     repo: options.repo,
            //     base: options.targetBranch,
            //     head: options.sourceBranch
            // });
            
            return { success: true };
        } catch (error) {
            console.error('[TEKTON] Error merging branch:', error);
            throw error;
        }
    }
    
    // Additional GitHub operations would be implemented here
}
```

### Project Manager

```javascript
/**
 * Project Manager
 * Manages Tekton projects and their mapping to GitHub repositories
 */
export class ProjectManager {
    constructor(gitHubService) {
        this.gitHubService = gitHubService;
        console.log('[TEKTON] ProjectManager initialized');
    }
    
    async getProjects() {
        console.log('[TEKTON] Getting projects');
        try {
            // In a real implementation, this would fetch projects from a backend service
            // For now, return mock data
            return [
                { 
                    name: 'Tekton', 
                    repository: 'cskoons/Tekton', 
                    branch: 'sprint/Clean_Slate_051125' 
                },
                { 
                    name: 'Sample Project', 
                    repository: 'cskoons/sample-project', 
                    branch: 'main' 
                }
            ];
        } catch (error) {
            console.error('[TEKTON] Error getting projects:', error);
            throw error;
        }
    }
    
    async createProject(options) {
        console.log('[TEKTON] Creating project:', options);
        try {
            // In a real implementation, this would create a project and link to a repository
            // For now, just return mock data
            return { 
                success: true, 
                project: { 
                    name: options.name, 
                    repository: options.repository || null, 
                    branch: options.branch || 'main' 
                } 
            };
        } catch (error) {
            console.error('[TEKTON] Error creating project:', error);
            throw error;
        }
    }
    
    async importProject(options) {
        console.log('[TEKTON] Importing project:', options);
        try {
            // In a real implementation, this would import an existing repository as a project
            
            // First, clone or connect to the repository
            await this.gitHubService.cloneRepository({
                repository: options.repository,
                directory: options.directory
            });
            
            // Then create a project record
            return await this.createProject({
                name: options.name || options.repository.split('/').pop(),
                repository: options.repository,
                branch: options.branch || 'main'
            });
        } catch (error) {
            console.error('[TEKTON] Error importing project:', error);
            throw error;
        }
    }
    
    async getProjectDetails(projectId) {
        console.log('[TEKTON] Getting project details:', projectId);
        try {
            // In a real implementation, this would fetch detailed project information
            // For now, return mock data
            return {
                name: 'Tekton',
                repository: 'cskoons/Tekton',
                branch: 'sprint/Clean_Slate_051125',
                lastActive: new Date(),
                components: [
                    'Athena',
                    'Engram',
                    'Hermes',
                    'Ergon',
                    'Rhetor'
                ]
            };
        } catch (error) {
            console.error('[TEKTON] Error getting project details:', error);
            throw error;
        }
    }
    
    // Additional project management operations would be implemented here
}
```

## Implementation Checklist

1. **Component Structure**
   - [ ] Implement basic HTML structure following Athena pattern
   - [ ] Add tab navigation with 6 tabs (Projects, Repositories, Branches, Actions, Project Chat, Team Chat)
   - [ ] Implement panel structure for each tab

2. **Styling**
   - [ ] Implement CSS with BEM naming (tekton__*)
   - [ ] Maintain visual consistency with Athena, with Tekton-specific colors
   - [ ] Ensure all height/spacing matches Athena component

3. **JavaScript**
   - [ ] Implement UI Manager protection
   - [ ] Implement HTML Panel protection
   - [ ] Implement tab switching functionality
   - [ ] Implement team chat functionality
   - [ ] Add loading/error handling

4. **GitHub Integration**
   - [ ] Implement GitHub service with MCP functions
   - [ ] Implement project manager functionality
   - [ ] Connect UI controls to GitHub operations

5. **Debug Instrumentation**
   - [ ] Add comprehensive logging with [TEKTON] prefix
   - [ ] Add error handling and user feedback
   - [ ] Ensure proper debugging messages

## Tekton Core-Specific Features

1. **Projects Panel**: List of GitHub projects being managed by Tekton
2. **Repositories Panel**: List of GitHub repositories with management options
3. **Branches Panel**: Branch management across repositories
4. **Actions Panel**: Common GitHub operations (clone, fork, merge, etc.)
5. **Project Chat**: GitHub project-specific assistance
6. **Team Chat**: Standard team chat functionality

## Important Notes

1. **Use Athena as Reference**: Always refer to Athena component for patterns and structure
2. **Component Isolation**: Ensure all DOM queries are scoped to the tekton container
3. **Consistent Naming**: Use 'tekton__' prefix for all BEM class names
4. **Error Handling**: Implement robust error handling
5. **Debug Messages**: Use '[TEKTON]' prefix for all console logs

## Testing

Test the component thoroughly to ensure:

1. It loads properly without errors
2. Tab switching works correctly
3. It doesn't interfere with other components
4. All features work as expected
5. It follows the Clean Slate architecture principles

## Next Steps After Implementation

After initial implementation:

1. Add placeholder content for each tab
2. Connect to GitHub API endpoints via MCP functions
3. Implement project and repository management functionality
4. Add branch visualization and management
5. Implement GitHub actions functionality

## Critical Implementation Requirements

**IMPORTANT**: This implementation guide MUST be followed exactly without any deviations. If any changes are proposed, they MUST be discussed with Casey (human-in-the-loop) first before implementation. No architectural changes, altered patterns, or extra features are allowed without explicit approval.