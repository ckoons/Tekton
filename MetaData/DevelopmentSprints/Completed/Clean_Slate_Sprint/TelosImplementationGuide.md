# Telos Component Implementation Guide

## Overview

This document provides detailed guidance for implementing the Telos component following the Clean Slate architecture. Telos is Tekton's requirements management system, focusing on tracking, analyzing, and managing project requirements throughout the software development lifecycle.

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

1. **Component HTML**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/telos/telos-component.html`
2. **Component JavaScript**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/telos/telos-component.js`
3. **Service JavaScript**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/telos/telos-service.js` 
4. **Requirements Management**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/telos/requirements-manager.js`

## HTML Component Structure

The HTML structure should follow the Athena component template exactly, with Telos-specific content:

```html
<!-- Telos Component - Requirements Management -->
<div class="telos">
    <!-- Component Header with Title -->
    <div class="telos__header">
        <div class="telos__title-container">
            <img src="/images/hexagon.jpg" alt="Tekton" class="telos__icon">
            <h2 class="telos__title">
                <span class="telos__title-main">Telos</span>
                <span class="telos__title-sub">Requirements Manager</span>
            </h2>
        </div>
    </div>
    
    <!-- Telos Menu Bar with Tab Navigation -->
    <div class="telos__menu-bar">
        <div class="telos__tabs">
            <div class="telos__tab telos__tab--active" data-tab="projects" onclick="telos_switchTab('projects'); return false;">
                <span class="telos__tab-label">Projects</span>
            </div>
            <div class="telos__tab" data-tab="requirements" onclick="telos_switchTab('requirements'); return false;">
                <span class="telos__tab-label">Requirements</span>
            </div>
            <div class="telos__tab" data-tab="traceability" onclick="telos_switchTab('traceability'); return false;">
                <span class="telos__tab-label">Traceability</span>
            </div>
            <div class="telos__tab" data-tab="validation" onclick="telos_switchTab('validation'); return false;">
                <span class="telos__tab-label">Validation</span>
            </div>
            <div class="telos__tab" data-tab="reqchat" onclick="telos_switchTab('reqchat'); return false;">
                <span class="telos__tab-label">Requirements Chat</span>
            </div>
            <div class="telos__tab" data-tab="teamchat" onclick="telos_switchTab('teamchat'); return false;">
                <span class="telos__tab-label">Team Chat</span>
            </div>
        </div>
        <div class="telos__actions">
            <button id="clear-chat-btn" class="telos__action-button" style="display: none;" onclick="telos_clearChat(); return false;">
                <span class="telos__button-label">Clear</span>
            </button>
        </div>
    </div>
    
    <!-- Telos Content Area -->
    <div class="telos__content">
        <!-- Projects Tab (Default Active Tab) -->
        <div id="projects-panel" class="telos__panel telos__panel--active">
            <div class="telos__projects">
                <div class="telos__control-bar">
                    <div class="telos__search-container">
                        <input type="text" id="project-search" class="telos__search-input" placeholder="Search projects...">
                        <button id="project-search-btn" class="telos__search-button">Search</button>
                    </div>
                    <div class="telos__actions">
                        <button id="add-project-btn" class="telos__action-button">
                            <span class="telos__button-icon">+</span>
                            <span class="telos__button-label">New Project</span>
                        </button>
                    </div>
                </div>
                <div class="telos__project-list-container">
                    <div id="project-list-loading" class="telos__loading-indicator">
                        <div class="telos__spinner"></div>
                        <div class="telos__loading-text">Loading projects...</div>
                    </div>
                    <div id="project-list" class="telos__project-list" style="display: none;">
                        <!-- Sample projects for UI testing -->
                        <div class="telos__project-item">
                            <div class="telos__project-info">
                                <div class="telos__project-name">Tekton UI Refactoring</div>
                                <div class="telos__project-meta">
                                    <span class="telos__project-count">24 requirements</span>
                                    <span class="telos__project-status">Active</span>
                                </div>
                            </div>
                            <div class="telos__project-actions">
                                <button class="telos__project-action-btn">View</button>
                                <button class="telos__project-action-btn">Edit</button>
                            </div>
                        </div>
                        <div class="telos__project-item">
                            <div class="telos__project-info">
                                <div class="telos__project-name">Engram Memory System</div>
                                <div class="telos__project-meta">
                                    <span class="telos__project-count">18 requirements</span>
                                    <span class="telos__project-status">Active</span>
                                </div>
                            </div>
                            <div class="telos__project-actions">
                                <button class="telos__project-action-btn">View</button>
                                <button class="telos__project-action-btn">Edit</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Requirements Tab -->
        <div id="requirements-panel" class="telos__panel">
            <div class="telos__requirements">
                <div class="telos__control-bar">
                    <div class="telos__search-container">
                        <input type="text" id="requirement-search" class="telos__search-input" placeholder="Search requirements...">
                        <button id="requirement-search-btn" class="telos__search-button">Search</button>
                    </div>
                    <div class="telos__filter-container">
                        <select id="project-filter" class="telos__filter-select">
                            <option value="all">All Projects</option>
                            <option value="tekton-ui">Tekton UI Refactoring</option>
                            <option value="engram">Engram Memory System</option>
                        </select>
                        <select id="status-filter" class="telos__filter-select">
                            <option value="all">All Statuses</option>
                            <option value="new">New</option>
                            <option value="in-progress">In Progress</option>
                            <option value="completed">Completed</option>
                            <option value="rejected">Rejected</option>
                        </select>
                        <select id="type-filter" class="telos__filter-select">
                            <option value="all">All Types</option>
                            <option value="functional">Functional</option>
                            <option value="non-functional">Non-Functional</option>
                            <option value="constraint">Constraint</option>
                        </select>
                        <button id="apply-filters-btn" class="telos__filter-button">Apply</button>
                    </div>
                    <div class="telos__actions">
                        <button id="new-requirement-btn" class="telos__action-button">
                            <span class="telos__button-icon">+</span>
                            <span class="telos__button-label">New Requirement</span>
                        </button>
                    </div>
                </div>
                <div class="telos__requirements-list-container">
                    <div id="requirements-list-loading" class="telos__loading-indicator">
                        <div class="telos__spinner"></div>
                        <div class="telos__loading-text">Loading requirements...</div>
                    </div>
                    <div id="requirements-list" class="telos__requirements-list" style="display: none;">
                        <table class="telos__requirements-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Title</th>
                                    <th>Project</th>
                                    <th>Type</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Sample requirements for UI testing -->
                                <tr class="telos__requirement-row">
                                    <td>REQ-001</td>
                                    <td>Component Isolation</td>
                                    <td>Tekton UI Refactoring</td>
                                    <td>Functional</td>
                                    <td>High</td>
                                    <td>In Progress</td>
                                    <td>
                                        <button class="telos__table-action-btn">View</button>
                                        <button class="telos__table-action-btn">Edit</button>
                                    </td>
                                </tr>
                                <tr class="telos__requirement-row">
                                    <td>REQ-002</td>
                                    <td>BEM Naming Convention</td>
                                    <td>Tekton UI Refactoring</td>
                                    <td>Constraint</td>
                                    <td>Medium</td>
                                    <td>Completed</td>
                                    <td>
                                        <button class="telos__table-action-btn">View</button>
                                        <button class="telos__table-action-btn">Edit</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Traceability Tab -->
        <div id="traceability-panel" class="telos__panel">
            <div class="telos__traceability">
                <div class="telos__control-bar">
                    <div class="telos__filter-container">
                        <select id="trace-project-filter" class="telos__filter-select">
                            <option value="all">All Projects</option>
                            <option value="tekton-ui">Tekton UI Refactoring</option>
                            <option value="engram">Engram Memory System</option>
                        </select>
                        <button id="trace-apply-filter-btn" class="telos__filter-button">Apply</button>
                    </div>
                    <div class="telos__view-controls">
                        <button id="trace-matrix-btn" class="telos__view-button telos__view-button--active">Matrix View</button>
                        <button id="trace-graph-btn" class="telos__view-button">Graph View</button>
                    </div>
                </div>
                <div class="telos__traceability-container">
                    <div id="traceability-matrix" class="telos__traceability-matrix">
                        <div class="telos__trace-placeholder">
                            <div class="telos__placeholder-content">
                                <h3 class="telos__placeholder-title">Traceability Matrix</h3>
                                <p class="telos__placeholder-text">Select a project and visualization type to view traceability information.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Validation Tab -->
        <div id="validation-panel" class="telos__panel">
            <div class="telos__validation">
                <h3 class="telos__section-title">Requirements Validation</h3>
                <p class="telos__text">Validate requirements against quality criteria and standards.</p>

                <div class="telos__validation-form">
                    <div class="telos__form-group">
                        <label class="telos__form-label">Project</label>
                        <select class="telos__form-select" id="validation-project-select">
                            <option value="">Select a project...</option>
                            <option value="tekton-ui">Tekton UI Refactoring</option>
                            <option value="engram">Engram Memory System</option>
                        </select>
                    </div>

                    <div class="telos__form-group">
                        <label class="telos__form-label">Validation Type</label>
                        <select class="telos__form-select" id="validation-type-select">
                            <option value="all">All Requirements</option>
                            <option value="selected">Selected Requirements</option>
                            <option value="new">New Requirements</option>
                            <option value="changed">Recently Changed</option>
                        </select>
                    </div>

                    <div class="telos__form-group">
                        <label class="telos__form-label">Validation Criteria</label>
                        <div class="telos__checkbox-group">
                            <label class="telos__checkbox-label">
                                <input type="checkbox" class="telos__checkbox" id="validate-completeness" checked> Completeness
                            </label>
                            <label class="telos__checkbox-label">
                                <input type="checkbox" class="telos__checkbox" id="validate-clarity" checked> Clarity
                            </label>
                            <label class="telos__checkbox-label">
                                <input type="checkbox" class="telos__checkbox" id="validate-consistency" checked> Consistency
                            </label>
                            <label class="telos__checkbox-label">
                                <input type="checkbox" class="telos__checkbox" id="validate-testability" checked> Testability
                            </label>
                            <label class="telos__checkbox-label">
                                <input type="checkbox" class="telos__checkbox" id="validate-feasibility"> Feasibility
                            </label>
                        </div>
                    </div>

                    <div class="telos__form-actions">
                        <button class="telos__button telos__button--secondary" id="reset-validation-btn">Reset</button>
                        <button class="telos__button telos__button--primary" id="run-validation-btn">Run Validation</button>
                    </div>
                </div>

                <div class="telos__validation-result" style="margin-top: 20px; display: none;" id="validation-result-container">
                    <h4 class="telos__result-title">Validation Results</h4>
                    <div class="telos__result-content" id="validation-results">
                        <!-- Validation results will appear here -->
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Requirements Chat Tab -->
        <div id="reqchat-panel" class="telos__panel">
            <div id="reqchat-messages" class="telos__chat-messages">
                <!-- Welcome message -->
                <div class="telos__message telos__message--system">
                    <div class="telos__message-content">
                        <div class="telos__message-text">
                            <h3 class="telos__message-title">Requirements Assistant</h3>
                            <p>This chat provides assistance with requirements engineering. Ask questions about:</p>
                            <ul>
                                <li>Requirements drafting and refinement</li>
                                <li>Requirements validation and analysis</li>
                                <li>Traceability and relationships</li>
                                <li>Best practices for requirements management</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Team Chat Tab -->
        <div id="teamchat-panel" class="telos__panel">
            <div id="teamchat-messages" class="telos__chat-messages">
                <!-- Welcome message -->
                <div class="telos__message telos__message--system">
                    <div class="telos__message-content">
                        <div class="telos__message-text">
                            <h3 class="telos__message-title">Tekton Team Chat</h3>
                            <p>This chat is shared across all Tekton components. Use this for team communication and coordination.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Footer with Chat Input -->
    <div class="telos__footer">
        <div class="telos__chat-input-container">
            <div class="telos__chat-prompt">></div>
            <input type="text" id="chat-input" class="telos__chat-input" 
                   placeholder="Enter chat message, requirements query, or validation request">
            <button id="send-button" class="telos__send-button">Send</button>
        </div>
    </div>
</div>
```

## CSS Styling

The CSS should follow Athena's BEM naming structure, maintaining the same visual appearance and layout but with Telos-specific color scheme:

```css
/* Telos component styles using BEM naming convention */

/* Container */
.telos {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    background-color: var(--bg-primary, #1e1e2e);
    color: var(--text-primary, #f0f0f0);
    /* No absolute positioning - proper component containment */
}

/* Header */
.telos__header {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 50px; /* Match header height from Athena */
}

.telos__title-container {
    display: flex;
    align-items: center;
}

.telos__icon {
    height: 30px;
    width: auto;
    margin-right: 12px;
}

.telos__title {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 500;
}

.telos__title-sub {
    margin-left: 8px;
    opacity: 0.8;
    font-weight: normal;
}

/* Menu Bar */
.telos__menu-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 46px; /* Match menu bar height from Athena */
}

.telos__tabs {
    display: flex;
    gap: 8px;
}

.telos__tab {
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

.telos__tab:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

.telos__tab--active {
    border-bottom-color: var(--color-primary, #3498db); /* Telos blue color */
    font-weight: 500;
}

/* Content Area and other styles should follow Athena pattern exactly, but with 'telos' prefix */
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
    window.uiManager._ignoreComponent = 'telos';
    console.log('[TELOS] Set UI Manager to ignore telos component');
}

// DEFINE TAB SWITCHING FUNCTION
// CRITICAL: This uses no shared code/utilities to avoid conflicts
window.telos_switchTab = function(tabId) {
    console.log('[TELOS] Switching to tab:', tabId);
    
    // Force HTML panel visibility
    const htmlPanelElements = document.querySelectorAll('#html-panel');
    htmlPanelElements.forEach(panel => {
        if (panel) panel.style.display = 'block';
    });
    
    try {
        // Only select elements within telos component to avoid conflicts with other components
        const telosContainer = document.querySelector('.telos');
        if (!telosContainer) {
            console.error('[TELOS] Tab Switch: Cannot find telos container');
            return false;
        }
        
        // Update tab active state - ONLY WITHIN TELOS CONTAINER
        const tabs = telosContainer.querySelectorAll('.telos__tab');
        tabs.forEach(tab => {
            if (tab.getAttribute('data-tab') === tabId) {
                tab.classList.add('telos__tab--active');
            } else {
                tab.classList.remove('telos__tab--active');
            }
        });
        
        // Update panel visibility - ONLY WITHIN TELOS CONTAINER
        const panels = telosContainer.querySelectorAll('.telos__panel');
        panels.forEach(panel => {
            const panelId = panel.id;
            if (panelId === tabId + '-panel') {
                panel.style.display = 'block';
                panel.classList.add('telos__panel--active');
            } else {
                panel.style.display = 'none';
                panel.classList.remove('telos__panel--active');
            }
        });
        
        // Update clear button visibility for chat tabs
        const clearButton = telosContainer.querySelector('#clear-chat-btn');
        if (clearButton) {
            clearButton.style.display = (tabId === 'reqchat' || tabId === 'teamchat') ? 'block' : 'none';
        }
        
        // Update component state
        if (window.telosComponent) {
            window.telosComponent.state = window.telosComponent.state || {};
            window.telosComponent.state.activeTab = tabId;
            
            // Call component-specific methods if available
            if (typeof window.telosComponent.updateChatPlaceholder === 'function') {
                window.telosComponent.updateChatPlaceholder(tabId);
            }
            
            if (typeof window.telosComponent.loadTabContent === 'function') {
                window.telosComponent.loadTabContent(tabId);
            }
            
            if (typeof window.telosComponent.saveComponentState === 'function') {
                window.telosComponent.saveComponentState();
            }
        }
    } catch (err) {
        console.error('[TELOS] Error in tab switching:', err);
    }
    
    return false; // Stop event propagation
};

// CHAT CLEARING FUNCTION - Same pattern as Athena
window.telos_clearChat = function() {
    // Implement following Athena pattern
};

// Other functions - loading component, HTML panel protection, etc. should follow Athena pattern exactly
```

## Isolated Component JavaScript

Create a separate file `telos-component.js` that follows the same structure as Athena's component JS:

```javascript
/**
 * Telos Requirements Management Component
 * 
 * Provides a comprehensive interface for managing project requirements,
 * including creation, validation, traceability, and requirement refinement.
 */

import { TelosClient } from './telos-service.js';
import { RequirementsManager } from './requirements-manager.js';

class TelosComponent {
    constructor() {
        this.client = new TelosClient();
        this.requirementsManager = new RequirementsManager(this.client);
        this.state = {
            activeTab: 'projects',
            projects: [],
            requirements: [],
            loading: false
        };
        
        console.log('[TELOS] Component constructed');
    }
    
    async init() {
        console.log('[TELOS] Initializing component');
        this.setupEventListeners();
        this.loadProjects();
    }
    
    setupEventListeners() {
        // Set up event listeners for buttons, etc.
        // Follow Athena pattern with telos-specific elements
    }
    
    async loadProjects() {
        // Load project data from API
        try {
            this.state.loading = true;
            const projects = await this.client.getProjects();
            this.state.projects = projects;
            this.renderProjects();
        } catch (error) {
            console.error('[TELOS] Error loading projects:', error);
        } finally {
            this.state.loading = false;
        }
    }
    
    renderProjects() {
        // Render projects to DOM
    }
    
    // Add other methods following Athena pattern
}

// Initialize and export the component
window.telosComponent = new TelosComponent();
export { TelosComponent };
```

## Service JavaScript Files

Create the necessary service files that follow the pattern from Athena:

1. **telos-service.js**: For API communication
2. **requirements-manager.js**: For requirements management

## Implementation Checklist

1. **Component Structure**
   - [ ] Implement basic HTML structure following Athena pattern
   - [ ] Add tab navigation with 6 tabs (Projects, Requirements, Traceability, Validation, Requirements Chat, Team Chat)
   - [ ] Implement panel structure for each tab

2. **Styling**
   - [ ] Implement CSS with BEM naming (telos__*)
   - [ ] Maintain visual consistency with Athena, with Telos-specific colors
   - [ ] Ensure all height/spacing matches Athena component

3. **JavaScript**
   - [ ] Implement UI Manager protection
   - [ ] Implement HTML Panel protection
   - [ ] Implement tab switching functionality
   - [ ] Implement team chat functionality
   - [ ] Add loading/error handling

4. **Debug Instrumentation**
   - [ ] Add comprehensive logging with [TELOS] prefix
   - [ ] Add error handling and user feedback
   - [ ] Ensure proper debugging messages

## Telos-Specific Features

1. **Projects Panel**: List of requirement projects
2. **Requirements Panel**: Table view of requirements with filtering
3. **Traceability Panel**: Matrix and graph visualization of requirement relationships
4. **Validation Panel**: Requirements validation against quality criteria
5. **Requirements Chat**: Requirements-specific assistance
6. **Team Chat**: Standard team chat functionality

## Important Notes

1. **Use Athena as Reference**: Always refer to Athena component for patterns and structure
2. **Component Isolation**: Ensure all DOM queries are scoped to the telos container
3. **Consistent Naming**: Use 'telos__' prefix for all BEM class names
4. **Error Handling**: Implement robust error handling
5. **Debug Messages**: Use '[TELOS]' prefix for all console logs

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
2. Connect to Telos API endpoints
3. Implement project and requirement management functionality
4. Add traceability visualization
5. Implement requirements validation functionality

## Critical Implementation Requirements

**IMPORTANT**: This implementation guide MUST be followed exactly without any deviations. If any changes are proposed, they MUST be discussed with Casey (human-in-the-loop) first before implementation. No architectural changes, altered patterns, or extra features are allowed without explicit approval.