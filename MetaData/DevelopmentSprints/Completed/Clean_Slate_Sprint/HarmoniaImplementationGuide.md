# Harmonia Component Implementation Guide

## Overview

This document provides detailed guidance for implementing the Harmonia component following the Clean Slate architecture. Harmonia is Tekton's workflow orchestration engine, responsible for coordinating complex workflows across components, managing state persistence, and handling task sequencing.

## Implementation Approach

The implementation will strictly follow the Clean Slate architecture principles with Athena as the reference model:

1. Implement component with proper BEM naming convention
2. Ensure strict component isolation
3. Use consistent HTML structure and styling with other components
4. Add proper protection from UI Manager interference
5. Implement self-contained tab switching functionality
6. Add comprehensive debug instrumentation

## Required Files

The following files need to be implemented:

1. **Component HTML**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/harmonia/harmonia-component.html`
2. **Component JavaScript**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/harmonia/harmonia-component.js`
3. **Service JavaScript**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/harmonia/harmonia-service.js` 
4. **Workflow Manager**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/harmonia/workflow-manager.js`

## HTML Component Structure

The HTML structure should follow the Athena component template exactly, with Harmonia-specific content:

```html
<!-- Harmonia Component - Workflow Orchestration -->
<div class="harmonia">
    <!-- Component Header with Title -->
    <div class="harmonia__header">
        <div class="harmonia__title-container">
            <img src="/images/hexagon.jpg" alt="Tekton" class="harmonia__icon">
            <h2 class="harmonia__title">
                <span class="harmonia__title-main">Harmonia</span>
                <span class="harmonia__title-sub">Workflow Orchestration</span>
            </h2>
        </div>
    </div>
    
    <!-- Harmonia Menu Bar with Tab Navigation -->
    <div class="harmonia__menu-bar">
        <div class="harmonia__tabs">
            <div class="harmonia__tab harmonia__tab--active" data-tab="workflows" onclick="harmonia_switchTab('workflows'); return false;">
                <span class="harmonia__tab-label">Workflows</span>
            </div>
            <div class="harmonia__tab" data-tab="templates" onclick="harmonia_switchTab('templates'); return false;">
                <span class="harmonia__tab-label">Templates</span>
            </div>
            <div class="harmonia__tab" data-tab="executions" onclick="harmonia_switchTab('executions'); return false;">
                <span class="harmonia__tab-label">Executions</span>
            </div>
            <div class="harmonia__tab" data-tab="monitor" onclick="harmonia_switchTab('monitor'); return false;">
                <span class="harmonia__tab-label">Monitor</span>
            </div>
            <div class="harmonia__tab" data-tab="workflowchat" onclick="harmonia_switchTab('workflowchat'); return false;">
                <span class="harmonia__tab-label">Workflow Chat</span>
            </div>
            <div class="harmonia__tab" data-tab="teamchat" onclick="harmonia_switchTab('teamchat'); return false;">
                <span class="harmonia__tab-label">Team Chat</span>
            </div>
        </div>
        <div class="harmonia__actions">
            <button id="clear-chat-btn" class="harmonia__action-button" style="display: none;" onclick="harmonia_clearChat(); return false;">
                <span class="harmonia__button-label">Clear</span>
            </button>
        </div>
    </div>
    
    <!-- Harmonia Content Area -->
    <div class="harmonia__content">
        <!-- Workflows Tab (Default Active Tab) -->
        <div id="workflows-panel" class="harmonia__panel harmonia__panel--active">
            <div class="harmonia__workflows">
                <div class="harmonia__control-bar">
                    <div class="harmonia__search-container">
                        <input type="text" id="workflow-search" class="harmonia__search-input" placeholder="Search workflows...">
                        <button id="workflow-search-btn" class="harmonia__search-button">Search</button>
                    </div>
                    <div class="harmonia__actions">
                        <button id="add-workflow-btn" class="harmonia__action-button">
                            <span class="harmonia__button-icon">+</span>
                            <span class="harmonia__button-label">New Workflow</span>
                        </button>
                    </div>
                </div>
                <div class="harmonia__workflow-list-container">
                    <div id="workflow-list-loading" class="harmonia__loading-indicator">
                        <div class="harmonia__spinner"></div>
                        <div class="harmonia__loading-text">Loading workflows...</div>
                    </div>
                    <div id="workflow-list" class="harmonia__workflow-list" style="display: none;">
                        <!-- Sample workflows for UI testing -->
                        <div class="harmonia__workflow-item">
                            <div class="harmonia__workflow-info">
                                <div class="harmonia__workflow-name">Data Processing Pipeline</div>
                                <div class="harmonia__workflow-meta">
                                    <span class="harmonia__workflow-tasks">12 tasks</span>
                                    <span class="harmonia__workflow-status">Active</span>
                                </div>
                                <div class="harmonia__workflow-description">Process and analyze data from multiple sources</div>
                            </div>
                            <div class="harmonia__workflow-actions">
                                <button class="harmonia__workflow-action-btn">View</button>
                                <button class="harmonia__workflow-action-btn">Edit</button>
                                <button class="harmonia__workflow-action-btn">Execute</button>
                            </div>
                        </div>
                        <div class="harmonia__workflow-item">
                            <div class="harmonia__workflow-info">
                                <div class="harmonia__workflow-name">Content Generation</div>
                                <div class="harmonia__workflow-meta">
                                    <span class="harmonia__workflow-tasks">8 tasks</span>
                                    <span class="harmonia__workflow-status">Active</span>
                                </div>
                                <div class="harmonia__workflow-description">Generate content using various LLM models</div>
                            </div>
                            <div class="harmonia__workflow-actions">
                                <button class="harmonia__workflow-action-btn">View</button>
                                <button class="harmonia__workflow-action-btn">Edit</button>
                                <button class="harmonia__workflow-action-btn">Execute</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Templates Tab -->
        <div id="templates-panel" class="harmonia__panel">
            <div class="harmonia__templates">
                <div class="harmonia__control-bar">
                    <div class="harmonia__search-container">
                        <input type="text" id="template-search" class="harmonia__search-input" placeholder="Search templates...">
                        <button id="template-search-btn" class="harmonia__search-button">Search</button>
                    </div>
                    <div class="harmonia__filter-container">
                        <select id="template-category-filter" class="harmonia__filter-select">
                            <option value="all">All Categories</option>
                            <option value="data-processing">Data Processing</option>
                            <option value="content-generation">Content Generation</option>
                            <option value="deployment">Deployment</option>
                            <option value="analysis">Analysis</option>
                        </select>
                        <button id="apply-template-filter-btn" class="harmonia__filter-button">Apply</button>
                    </div>
                    <div class="harmonia__actions">
                        <button id="create-template-btn" class="harmonia__action-button">
                            <span class="harmonia__button-icon">+</span>
                            <span class="harmonia__button-label">New Template</span>
                        </button>
                    </div>
                </div>
                <div class="harmonia__template-list-container">
                    <div id="template-list-loading" class="harmonia__loading-indicator">
                        <div class="harmonia__spinner"></div>
                        <div class="harmonia__loading-text">Loading templates...</div>
                    </div>
                    <div id="template-list" class="harmonia__template-list" style="display: none;">
                        <!-- Sample templates for UI testing -->
                        <div class="harmonia__template-item">
                            <div class="harmonia__template-info">
                                <div class="harmonia__template-name">Data Processing Template</div>
                                <div class="harmonia__template-meta">
                                    <span class="harmonia__template-category">Data Processing</span>
                                    <span class="harmonia__template-usage">Used 24 times</span>
                                </div>
                                <div class="harmonia__template-description">Standard pipeline for processing and analyzing data</div>
                            </div>
                            <div class="harmonia__template-actions">
                                <button class="harmonia__template-action-btn">View</button>
                                <button class="harmonia__template-action-btn">Use</button>
                                <button class="harmonia__template-action-btn">Edit</button>
                            </div>
                        </div>
                        <div class="harmonia__template-item">
                            <div class="harmonia__template-info">
                                <div class="harmonia__template-name">Content Generation Template</div>
                                <div class="harmonia__template-meta">
                                    <span class="harmonia__template-category">Content Generation</span>
                                    <span class="harmonia__template-usage">Used 18 times</span>
                                </div>
                                <div class="harmonia__template-description">Template for generating content with various LLMs</div>
                            </div>
                            <div class="harmonia__template-actions">
                                <button class="harmonia__template-action-btn">View</button>
                                <button class="harmonia__template-action-btn">Use</button>
                                <button class="harmonia__template-action-btn">Edit</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Executions Tab -->
        <div id="executions-panel" class="harmonia__panel">
            <div class="harmonia__executions">
                <div class="harmonia__control-bar">
                    <div class="harmonia__filter-container">
                        <select id="execution-workflow-filter" class="harmonia__filter-select">
                            <option value="all">All Workflows</option>
                            <option value="data-processing">Data Processing Pipeline</option>
                            <option value="content-generation">Content Generation</option>
                        </select>
                        <select id="execution-status-filter" class="harmonia__filter-select">
                            <option value="all">All Statuses</option>
                            <option value="running">Running</option>
                            <option value="completed">Completed</option>
                            <option value="failed">Failed</option>
                            <option value="waiting">Waiting</option>
                        </select>
                        <button id="apply-execution-filter-btn" class="harmonia__filter-button">Apply</button>
                    </div>
                    <div class="harmonia__date-filter">
                        <input type="date" id="execution-date-from" class="harmonia__date-input">
                        <span class="harmonia__date-separator">to</span>
                        <input type="date" id="execution-date-to" class="harmonia__date-input">
                    </div>
                </div>
                <div class="harmonia__execution-list-container">
                    <div id="execution-list-loading" class="harmonia__loading-indicator">
                        <div class="harmonia__spinner"></div>
                        <div class="harmonia__loading-text">Loading executions...</div>
                    </div>
                    <div id="execution-list" class="harmonia__execution-list" style="display: none;">
                        <table class="harmonia__executions-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Workflow</th>
                                    <th>Start Time</th>
                                    <th>Duration</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Sample executions for UI testing -->
                                <tr class="harmonia__execution-row">
                                    <td>EXEC-001</td>
                                    <td>Data Processing Pipeline</td>
                                    <td>2025-05-14 08:30:22</td>
                                    <td>12m 34s</td>
                                    <td>
                                        <span class="harmonia__status harmonia__status--completed">Completed</span>
                                    </td>
                                    <td>
                                        <button class="harmonia__table-action-btn">View</button>
                                        <button class="harmonia__table-action-btn">Logs</button>
                                    </td>
                                </tr>
                                <tr class="harmonia__execution-row">
                                    <td>EXEC-002</td>
                                    <td>Content Generation</td>
                                    <td>2025-05-14 09:15:45</td>
                                    <td>Running (5m 22s)</td>
                                    <td>
                                        <span class="harmonia__status harmonia__status--running">Running</span>
                                    </td>
                                    <td>
                                        <button class="harmonia__table-action-btn">View</button>
                                        <button class="harmonia__table-action-btn">Logs</button>
                                        <button class="harmonia__table-action-btn">Stop</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Monitor Tab -->
        <div id="monitor-panel" class="harmonia__panel">
            <div class="harmonia__monitor">
                <div class="harmonia__control-bar">
                    <div class="harmonia__filter-container">
                        <select id="monitor-view" class="harmonia__filter-select">
                            <option value="live">Live View</option>
                            <option value="dashboard">Dashboard</option>
                            <option value="metrics">Metrics</option>
                            <option value="alerts">Alerts</option>
                        </select>
                        <button id="apply-view-btn" class="harmonia__filter-button">Apply</button>
                    </div>
                    <div class="harmonia__refresh-controls">
                        <label for="auto-refresh">Auto-refresh:</label>
                        <select id="auto-refresh" class="harmonia__filter-select">
                            <option value="0">Off</option>
                            <option value="5" selected>5s</option>
                            <option value="15">15s</option>
                            <option value="30">30s</option>
                            <option value="60">1m</option>
                        </select>
                        <button id="refresh-now-btn" class="harmonia__action-button">
                            <span class="harmonia__button-label">Refresh</span>
                        </button>
                    </div>
                </div>
                <div class="harmonia__monitor-container">
                    <div id="monitor-placeholder" class="harmonia__monitor-placeholder">
                        <div class="harmonia__placeholder-content">
                            <h3 class="harmonia__placeholder-title">Workflow Monitoring</h3>
                            <p class="harmonia__placeholder-text">Real-time monitoring of workflow executions will be displayed here.</p>
                        </div>
                    </div>
                    <div id="active-workflows" class="harmonia__active-workflows" style="display: none;">
                        <!-- Active workflows will be displayed here -->
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Workflow Chat Tab -->
        <div id="workflowchat-panel" class="harmonia__panel">
            <div id="workflowchat-messages" class="harmonia__chat-messages">
                <!-- Welcome message -->
                <div class="harmonia__message harmonia__message--system">
                    <div class="harmonia__message-content">
                        <div class="harmonia__message-text">
                            <h3 class="harmonia__message-title">Workflow Assistant</h3>
                            <p>This chat provides assistance with workflow creation and management. Ask questions about:</p>
                            <ul>
                                <li>Creating new workflows and templates</li>
                                <li>Debugging workflow execution issues</li>
                                <li>Optimizing workflow performance</li>
                                <li>Understanding workflow state and transitions</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Team Chat Tab -->
        <div id="teamchat-panel" class="harmonia__panel">
            <div id="teamchat-messages" class="harmonia__chat-messages">
                <!-- Welcome message -->
                <div class="harmonia__message harmonia__message--system">
                    <div class="harmonia__message-content">
                        <div class="harmonia__message-text">
                            <h3 class="harmonia__message-title">Tekton Team Chat</h3>
                            <p>This chat is shared across all Tekton components. Use this for team communication and coordination.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Footer with Chat Input -->
    <div class="harmonia__footer">
        <div class="harmonia__chat-input-container">
            <div class="harmonia__chat-prompt">></div>
            <input type="text" id="chat-input" class="harmonia__chat-input" 
                   placeholder="Enter chat message, workflow questions, or execution queries">
            <button id="send-button" class="harmonia__send-button">Send</button>
        </div>
    </div>
</div>
```

## CSS Styling

The CSS should follow Athena's BEM naming structure, maintaining the same visual appearance and layout but with Harmonia-specific color scheme:

```css
/* Harmonia component styles using BEM naming convention */

/* Container */
.harmonia {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    background-color: var(--bg-primary, #1e1e2e);
    color: var(--text-primary, #f0f0f0);
    /* No absolute positioning - proper component containment */
}

/* Header */
.harmonia__header {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 50px; /* Match header height from Athena */
}

.harmonia__title-container {
    display: flex;
    align-items: center;
}

.harmonia__icon {
    height: 30px;
    width: auto;
    margin-right: 12px;
}

.harmonia__title {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 500;
}

.harmonia__title-sub {
    margin-left: 8px;
    opacity: 0.8;
    font-weight: normal;
}

/* Menu Bar */
.harmonia__menu-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 46px; /* Match menu bar height from Athena */
}

.harmonia__tabs {
    display: flex;
    gap: 8px;
}

.harmonia__tab {
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

.harmonia__tab:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

.harmonia__tab--active {
    border-bottom-color: var(--color-primary, #9C27B0); /* Harmonia purple color */
    font-weight: 500;
}

/* Content Area and other styles should follow Athena pattern exactly, but with 'harmonia' prefix */
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
    window.uiManager._ignoreComponent = 'harmonia';
    console.log('[HARMONIA] Set UI Manager to ignore harmonia component');
}

// DEFINE TAB SWITCHING FUNCTION
// CRITICAL: This uses no shared code/utilities to avoid conflicts
window.harmonia_switchTab = function(tabId) {
    console.log('[HARMONIA] Switching to tab:', tabId);
    
    // Force HTML panel visibility
    const htmlPanelElements = document.querySelectorAll('#html-panel');
    htmlPanelElements.forEach(panel => {
        if (panel) panel.style.display = 'block';
    });
    
    try {
        // Only select elements within harmonia component to avoid conflicts with other components
        const harmoniaContainer = document.querySelector('.harmonia');
        if (!harmoniaContainer) {
            console.error('[HARMONIA] Tab Switch: Cannot find harmonia container');
            return false;
        }
        
        // Update tab active state - ONLY WITHIN HARMONIA CONTAINER
        const tabs = harmoniaContainer.querySelectorAll('.harmonia__tab');
        tabs.forEach(tab => {
            if (tab.getAttribute('data-tab') === tabId) {
                tab.classList.add('harmonia__tab--active');
            } else {
                tab.classList.remove('harmonia__tab--active');
            }
        });
        
        // Update panel visibility - ONLY WITHIN HARMONIA CONTAINER
        const panels = harmoniaContainer.querySelectorAll('.harmonia__panel');
        panels.forEach(panel => {
            const panelId = panel.id;
            if (panelId === tabId + '-panel') {
                panel.style.display = 'block';
                panel.classList.add('harmonia__panel--active');
            } else {
                panel.style.display = 'none';
                panel.classList.remove('harmonia__panel--active');
            }
        });
        
        // Update clear button visibility for chat tabs
        const clearButton = harmoniaContainer.querySelector('#clear-chat-btn');
        if (clearButton) {
            clearButton.style.display = (tabId === 'workflowchat' || tabId === 'teamchat') ? 'block' : 'none';
        }
        
        // Update component state
        if (window.harmoniaComponent) {
            window.harmoniaComponent.state = window.harmoniaComponent.state || {};
            window.harmoniaComponent.state.activeTab = tabId;
            
            // Call component-specific methods if available
            if (typeof window.harmoniaComponent.updateChatPlaceholder === 'function') {
                window.harmoniaComponent.updateChatPlaceholder(tabId);
            }
            
            if (typeof window.harmoniaComponent.loadTabContent === 'function') {
                window.harmoniaComponent.loadTabContent(tabId);
            }
            
            if (typeof window.harmoniaComponent.saveComponentState === 'function') {
                window.harmoniaComponent.saveComponentState();
            }
        }
    } catch (err) {
        console.error('[HARMONIA] Error in tab switching:', err);
    }
    
    return false; // Stop event propagation
};

// CHAT CLEARING FUNCTION - Same pattern as Athena
window.harmonia_clearChat = function() {
    // Implement following Athena pattern
};

// Other functions - loading component, HTML panel protection, etc. should follow Athena pattern exactly
```

## Isolated Component JavaScript

Create a separate file `harmonia-component.js` that follows the same structure as Athena's component JS:

```javascript
/**
 * Harmonia Workflow Orchestration Component
 * 
 * Provides a comprehensive interface for workflow management, including
 * creation, execution, monitoring, and template management.
 */

import { HarmoniaClient } from './harmonia-service.js';
import { WorkflowManager } from './workflow-manager.js';

class HarmoniaComponent {
    constructor() {
        this.client = new HarmoniaClient();
        this.workflowManager = new WorkflowManager(this.client);
        this.state = {
            activeTab: 'workflows',
            workflows: [],
            templates: [],
            executions: [],
            loading: false
        };
        
        console.log('[HARMONIA] Component constructed');
    }
    
    async init() {
        console.log('[HARMONIA] Initializing component');
        this.setupEventListeners();
        this.loadWorkflows();
    }
    
    setupEventListeners() {
        // Set up event listeners for buttons, etc.
        // Follow Athena pattern with harmonia-specific elements
    }
    
    async loadWorkflows() {
        // Load workflow data from API
        try {
            this.state.loading = true;
            const workflows = await this.client.getWorkflows();
            this.state.workflows = workflows;
            this.renderWorkflows();
        } catch (error) {
            console.error('[HARMONIA] Error loading workflows:', error);
        } finally {
            this.state.loading = false;
        }
    }
    
    renderWorkflows() {
        // Render workflows to DOM
    }
    
    // Add other methods following Athena pattern
}

// Initialize and export the component
window.harmoniaComponent = new HarmoniaComponent();
export { HarmoniaComponent };
```

## Service JavaScript Files

Create the necessary service files that follow the pattern from Athena:

1. **harmonia-service.js**: For API communication
2. **workflow-manager.js**: For workflow management

## Implementation Checklist

1. **Component Structure**
   - [ ] Implement basic HTML structure following Athena pattern
   - [ ] Add tab navigation with 6 tabs (Workflows, Templates, Executions, Monitor, Workflow Chat, Team Chat)
   - [ ] Implement panel structure for each tab

2. **Styling**
   - [ ] Implement CSS with BEM naming (harmonia__*)
   - [ ] Maintain visual consistency with Athena, with Harmonia-specific colors
   - [ ] Ensure all height/spacing matches Athena component

3. **JavaScript**
   - [ ] Implement UI Manager protection
   - [ ] Implement HTML Panel protection
   - [ ] Implement tab switching functionality
   - [ ] Implement team chat functionality
   - [ ] Add loading/error handling

4. **Debug Instrumentation**
   - [ ] Add comprehensive logging with [HARMONIA] prefix
   - [ ] Add error handling and user feedback
   - [ ] Ensure proper debugging messages

## Harmonia-Specific Features

1. **Workflows Panel**: List of workflow definitions and management
2. **Templates Panel**: Reusable workflow templates
3. **Executions Panel**: History of workflow executions
4. **Monitor Panel**: Real-time workflow execution monitoring
5. **Workflow Chat**: Workflow-specific assistance
6. **Team Chat**: Standard team chat functionality

## Important Notes

1. **Use Athena as Reference**: Always refer to Athena component for patterns and structure
2. **Component Isolation**: Ensure all DOM queries are scoped to the harmonia container
3. **Consistent Naming**: Use 'harmonia__' prefix for all BEM class names
4. **Error Handling**: Implement robust error handling
5. **Debug Messages**: Use '[HARMONIA]' prefix for all console logs

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
2. Connect to Harmonia API endpoints
3. Implement workflow management functionality
4. Add execution monitoring features
5. Implement template management

## Critical Implementation Requirements

**IMPORTANT**: This implementation guide MUST be followed exactly without any deviations. If any changes are proposed, they MUST be discussed with Casey (human-in-the-loop) first before implementation. No architectural changes, altered patterns, or extra features are allowed without explicit approval.