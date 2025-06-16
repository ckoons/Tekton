# Prometheus Component Implementation Guide

## Overview

This document provides detailed guidance for implementing the Prometheus component following the Clean Slate architecture. Prometheus is Tekton's planning and project management system, focusing on timelines, resource allocation, critical path analysis, and reporting.

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

1. **Component HTML**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/prometheus/prometheus-component.html`
2. **Component JavaScript**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/prometheus/prometheus-component.js`
3. **Service JavaScript**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/prometheus/prometheus-service.js` 
4. **Timeline Service**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/prometheus/prometheus-timeline-service.js`

## HTML Component Structure

The HTML structure should follow the Athena component template exactly, with Prometheus-specific content:

```html
<!-- Prometheus Component - Planning and Resource Management -->
<div class="prometheus">
    <!-- Component Header with Title -->
    <div class="prometheus__header">
        <div class="prometheus__title-container">
            <img src="/images/hexagon.jpg" alt="Tekton" class="prometheus__icon">
            <h2 class="prometheus__title">
                <span class="prometheus__title-main">Prometheus</span>
                <span class="prometheus__title-sub">Planning System</span>
            </h2>
        </div>
    </div>
    
    <!-- Prometheus Menu Bar with Tab Navigation -->
    <div class="prometheus__menu-bar">
        <div class="prometheus__tabs">
            <div class="prometheus__tab prometheus__tab--active" data-tab="planning" onclick="prometheus_switchTab('planning'); return false;">
                <span class="prometheus__tab-label">Planning</span>
            </div>
            <div class="prometheus__tab" data-tab="timeline" onclick="prometheus_switchTab('timeline'); return false;">
                <span class="prometheus__tab-label">Timeline</span>
            </div>
            <div class="prometheus__tab" data-tab="resources" onclick="prometheus_switchTab('resources'); return false;">
                <span class="prometheus__tab-label">Resources</span>
            </div>
            <div class="prometheus__tab" data-tab="analysis" onclick="prometheus_switchTab('analysis'); return false;">
                <span class="prometheus__tab-label">Analysis</span>
            </div>
            <div class="prometheus__tab" data-tab="planningchat" onclick="prometheus_switchTab('planningchat'); return false;">
                <span class="prometheus__tab-label">Planning Chat</span>
            </div>
            <div class="prometheus__tab" data-tab="teamchat" onclick="prometheus_switchTab('teamchat'); return false;">
                <span class="prometheus__tab-label">Team Chat</span>
            </div>
        </div>
        <div class="prometheus__actions">
            <button id="clear-chat-btn" class="prometheus__action-button" style="display: none;" onclick="prometheus_clearChat(); return false;">
                <span class="prometheus__button-label">Clear</span>
            </button>
        </div>
    </div>
    
    <!-- Prometheus Content Area -->
    <div class="prometheus__content">
        <!-- Planning Tab (Default Active Tab) -->
        <div id="planning-panel" class="prometheus__panel prometheus__panel--active">
            <div class="prometheus__planning">
                <div class="prometheus__control-bar">
                    <div class="prometheus__search-container">
                        <input type="text" id="project-search" class="prometheus__search-input" placeholder="Search projects...">
                        <button id="project-search-btn" class="prometheus__search-button">Search</button>
                    </div>
                    <div class="prometheus__actions">
                        <button id="add-project-btn" class="prometheus__action-button">
                            <span class="prometheus__button-icon">+</span>
                            <span class="prometheus__button-label">Add Project</span>
                        </button>
                    </div>
                </div>
                <div class="prometheus__project-list-container">
                    <!-- Project list will be populated here -->
                    <div id="project-list-loading" class="prometheus__loading-indicator">
                        <div class="prometheus__spinner"></div>
                        <div class="prometheus__loading-text">Loading projects...</div>
                    </div>
                    <div id="project-list-items" class="prometheus__project-list" style="display: none;">
                        <!-- Sample projects for UI testing -->
                        <div class="prometheus__project-item">
                            <div class="prometheus__project-status prometheus__project-status--on-track"></div>
                            <div class="prometheus__project-details">
                                <div class="prometheus__project-name">Clean Slate UI Sprint</div>
                                <div class="prometheus__project-dates">May 10 - May 17, 2025</div>
                                <div class="prometheus__project-progress">
                                    <div class="prometheus__progress-bar">
                                        <div class="prometheus__progress-fill" style="width: 65%;"></div>
                                    </div>
                                    <div class="prometheus__progress-text">65% Complete</div>
                                </div>
                            </div>
                            <div class="prometheus__project-actions">
                                <button class="prometheus__project-action-btn">View</button>
                                <button class="prometheus__project-action-btn">Edit</button>
                            </div>
                        </div>
                        <div class="prometheus__project-item">
                            <div class="prometheus__project-status prometheus__project-status--at-risk"></div>
                            <div class="prometheus__project-details">
                                <div class="prometheus__project-name">Component Integration</div>
                                <div class="prometheus__project-dates">May 18 - May 25, 2025</div>
                                <div class="prometheus__project-progress">
                                    <div class="prometheus__progress-bar">
                                        <div class="prometheus__progress-fill" style="width: 30%;"></div>
                                    </div>
                                    <div class="prometheus__progress-text">30% Complete</div>
                                </div>
                            </div>
                            <div class="prometheus__project-actions">
                                <button class="prometheus__project-action-btn">View</button>
                                <button class="prometheus__project-action-btn">Edit</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Timeline Tab -->
        <div id="timeline-panel" class="prometheus__panel">
            <div class="prometheus__timeline">
                <div class="prometheus__control-bar">
                    <div class="prometheus__filter-container">
                        <select id="timeline-view" class="prometheus__filter-select">
                            <option value="day">Day View</option>
                            <option value="week">Week View</option>
                            <option value="month" selected>Month View</option>
                            <option value="quarter">Quarter View</option>
                        </select>
                        <button id="apply-view-btn" class="prometheus__filter-button">Apply</button>
                    </div>
                    <div class="prometheus__filter-container">
                        <select id="timeline-filter" class="prometheus__filter-select">
                            <option value="all">All Projects</option>
                            <option value="active">Active Projects</option>
                            <option value="critical">Critical Path Only</option>
                        </select>
                        <button id="apply-filter-btn" class="prometheus__filter-button">Apply</button>
                    </div>
                </div>
                <div id="timeline-container" class="prometheus__timeline-container">
                    <div id="timeline-placeholder" class="prometheus__timeline-placeholder">
                        <div class="prometheus__placeholder-content">
                            <h3 class="prometheus__placeholder-title">Timeline Visualization</h3>
                            <p class="prometheus__placeholder-text">The project timeline will be displayed here once loaded.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Resources Tab -->
        <div id="resources-panel" class="prometheus__panel">
            <div class="prometheus__resources">
                <div class="prometheus__control-bar">
                    <div class="prometheus__filter-container">
                        <select id="resource-type-filter" class="prometheus__filter-select">
                            <option value="all">All Resources</option>
                            <option value="people">People</option>
                            <option value="equipment">Equipment</option>
                            <option value="budget">Budget</option>
                        </select>
                        <button id="apply-resource-filter-btn" class="prometheus__filter-button">Apply</button>
                    </div>
                    <div class="prometheus__actions">
                        <button id="add-resource-btn" class="prometheus__action-button">
                            <span class="prometheus__button-icon">+</span>
                            <span class="prometheus__button-label">Add Resource</span>
                        </button>
                    </div>
                </div>
                <div class="prometheus__resource-list-container">
                    <div id="resource-list-loading" class="prometheus__loading-indicator">
                        <div class="prometheus__spinner"></div>
                        <div class="prometheus__loading-text">Loading resources...</div>
                    </div>
                    <div id="resource-allocation" class="prometheus__resource-allocation" style="display: none;">
                        <!-- Sample resource allocation chart -->
                        <div class="prometheus__chart-container">
                            <h3 class="prometheus__section-title">Resource Allocation</h3>
                            <div class="prometheus__chart-placeholder">
                                <p>Resource allocation visualization will appear here</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Analysis Tab -->
        <div id="analysis-panel" class="prometheus__panel">
            <div class="prometheus__analysis">
                <h3 class="prometheus__section-title">Critical Path Analysis</h3>
                <p class="prometheus__text">Analyze project timelines and resource constraints to identify the critical path.</p>

                <div class="prometheus__analysis-form">
                    <div class="prometheus__form-group">
                        <label class="prometheus__form-label">Project</label>
                        <select class="prometheus__form-select" id="analysis-project-select">
                            <option value="">Select a project...</option>
                            <option value="clean-slate">Clean Slate UI Sprint</option>
                            <option value="component-integration">Component Integration</option>
                        </select>
                    </div>

                    <div class="prometheus__form-group">
                        <label class="prometheus__form-label">Analysis Type</label>
                        <select class="prometheus__form-select" id="analysis-type-select">
                            <option value="critical-path">Critical Path</option>
                            <option value="resource-constraints">Resource Constraints</option>
                            <option value="risk-assessment">Risk Assessment</option>
                            <option value="bottlenecks">Bottlenecks</option>
                        </select>
                    </div>

                    <div class="prometheus__form-group">
                        <label class="prometheus__form-label">Include Dependencies</label>
                        <div class="prometheus__checkbox-group">
                            <label class="prometheus__checkbox-label">
                                <input type="checkbox" class="prometheus__checkbox" id="include-external"> Include external dependencies
                            </label>
                            <label class="prometheus__checkbox-label">
                                <input type="checkbox" class="prometheus__checkbox" id="include-resource"> Include resource constraints
                            </label>
                        </div>
                    </div>

                    <div class="prometheus__form-actions">
                        <button class="prometheus__button prometheus__button--secondary" id="clear-analysis-btn">Clear</button>
                        <button class="prometheus__button prometheus__button--primary" id="run-analysis-btn">Run Analysis</button>
                    </div>
                </div>

                <div class="prometheus__analysis-result" style="margin-top: 20px; display: none;" id="analysis-result-container">
                    <h4 class="prometheus__result-title">Analysis Results</h4>
                    <div class="prometheus__result-content" id="analysis-results">
                        <!-- Analysis results will appear here -->
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Planning Chat Tab -->
        <div id="planningchat-panel" class="prometheus__panel">
            <div id="planningchat-messages" class="prometheus__chat-messages">
                <!-- Welcome message -->
                <div class="prometheus__message prometheus__message--system">
                    <div class="prometheus__message-content">
                        <div class="prometheus__message-text">
                            <h3 class="prometheus__message-title">Planning Assistant</h3>
                            <p>This chat provides assistance with project planning and timeline management. Ask questions about:</p>
                            <ul>
                                <li>Project scheduling and dependencies</li>
                                <li>Resource allocation optimization</li>
                                <li>Timeline analysis and critical path</li>
                                <li>Risk assessment and mitigation</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Team Chat Tab -->
        <div id="teamchat-panel" class="prometheus__panel">
            <div id="teamchat-messages" class="prometheus__chat-messages">
                <!-- Welcome message -->
                <div class="prometheus__message prometheus__message--system">
                    <div class="prometheus__message-content">
                        <div class="prometheus__message-text">
                            <h3 class="prometheus__message-title">Tekton Team Chat</h3>
                            <p>This chat is shared across all Tekton components. Use this for team communication and coordination.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Footer with Chat Input -->
    <div class="prometheus__footer">
        <div class="prometheus__chat-input-container">
            <div class="prometheus__chat-prompt">></div>
            <input type="text" id="chat-input" class="prometheus__chat-input" 
                   placeholder="Enter chat message, project instructions, or planning queries">
            <button id="send-button" class="prometheus__send-button">Send</button>
        </div>
    </div>
</div>
```

## CSS Styling

The CSS should follow Athena's BEM naming structure, maintaining the same visual appearance and layout but with Prometheus-specific color scheme:

```css
/* Prometheus component styles using BEM naming convention */

/* Container */
.prometheus {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    background-color: var(--bg-primary, #1e1e2e);
    color: var(--text-primary, #f0f0f0);
    /* No absolute positioning - proper component containment */
}

/* Header */
.prometheus__header {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 50px; /* Match header height from Athena */
}

.prometheus__title-container {
    display: flex;
    align-items: center;
}

.prometheus__icon {
    height: 30px;
    width: auto;
    margin-right: 12px;
}

.prometheus__title {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 500;
}

.prometheus__title-sub {
    margin-left: 8px;
    opacity: 0.8;
    font-weight: normal;
}

/* Menu Bar */
.prometheus__menu-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 46px; /* Match menu bar height from Athena */
}

.prometheus__tabs {
    display: flex;
    gap: 8px;
}

.prometheus__tab {
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

.prometheus__tab:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

.prometheus__tab--active {
    border-bottom-color: var(--color-primary, #FF5722); /* Prometheus orange color */
    font-weight: 500;
}

/* Content Area and other styles should follow Athena pattern exactly, but with 'prometheus' prefix */
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
    window.uiManager._ignoreComponent = 'prometheus';
    console.log('[PROMETHEUS] Set UI Manager to ignore prometheus component');
}

// DEFINE TAB SWITCHING FUNCTION
// CRITICAL: This uses no shared code/utilities to avoid conflicts
window.prometheus_switchTab = function(tabId) {
    console.log('[PROMETHEUS] Switching to tab:', tabId);
    
    // Force HTML panel visibility
    const htmlPanelElements = document.querySelectorAll('#html-panel');
    htmlPanelElements.forEach(panel => {
        if (panel) panel.style.display = 'block';
    });
    
    try {
        // Only select elements within prometheus component to avoid conflicts with other components
        const prometheusContainer = document.querySelector('.prometheus');
        if (!prometheusContainer) {
            console.error('[PROMETHEUS] Tab Switch: Cannot find prometheus container');
            return false;
        }
        
        // Update tab active state - ONLY WITHIN PROMETHEUS CONTAINER
        const tabs = prometheusContainer.querySelectorAll('.prometheus__tab');
        tabs.forEach(tab => {
            if (tab.getAttribute('data-tab') === tabId) {
                tab.classList.add('prometheus__tab--active');
            } else {
                tab.classList.remove('prometheus__tab--active');
            }
        });
        
        // Update panel visibility - ONLY WITHIN PROMETHEUS CONTAINER
        const panels = prometheusContainer.querySelectorAll('.prometheus__panel');
        panels.forEach(panel => {
            const panelId = panel.id;
            if (panelId === tabId + '-panel') {
                panel.style.display = 'block';
                panel.classList.add('prometheus__panel--active');
            } else {
                panel.style.display = 'none';
                panel.classList.remove('prometheus__panel--active');
            }
        });
        
        // Update clear button visibility for chat tabs
        const clearButton = prometheusContainer.querySelector('#clear-chat-btn');
        if (clearButton) {
            clearButton.style.display = (tabId === 'teamchat') ? 'block' : 'none';
        }
        
        // Update component state
        if (window.prometheusComponent) {
            window.prometheusComponent.state = window.prometheusComponent.state || {};
            window.prometheusComponent.state.activeTab = tabId;
            
            // Call component-specific methods if available
            if (typeof window.prometheusComponent.updateChatPlaceholder === 'function') {
                window.prometheusComponent.updateChatPlaceholder(tabId);
            }
            
            if (typeof window.prometheusComponent.loadTabContent === 'function') {
                window.prometheusComponent.loadTabContent(tabId);
            }
            
            if (typeof window.prometheusComponent.saveComponentState === 'function') {
                window.prometheusComponent.saveComponentState();
            }
        }
    } catch (err) {
        console.error('[PROMETHEUS] Error in tab switching:', err);
    }
    
    return false; // Stop event propagation
};

// CHAT CLEARING FUNCTION - Same pattern as Athena
window.prometheus_clearChat = function() {
    // Implement following Athena pattern
};

// Other functions - loading component, HTML panel protection, etc. should follow Athena pattern exactly
```

## Isolated Component JavaScript

Create a separate file `prometheus-component.js` that follows the same structure as Athena's component JS:

```javascript
/**
 * Prometheus Planning System Component
 * 
 * Provides a comprehensive interface for project planning, timeline management,
 * resource allocation, and critical path analysis.
 */

import { PrometheusClient } from './prometheus-service.js';
import { TimelineVisualization } from './prometheus-timeline-service.js';

class PrometheusComponent {
    constructor() {
        this.client = new PrometheusClient();
        this.state = {
            activeTab: 'planning',
            projects: [],
            resources: [],
            loading: false
        };
        
        console.log('[PROMETHEUS] Component constructed');
    }
    
    async init() {
        console.log('[PROMETHEUS] Initializing component');
        this.setupEventListeners();
        this.loadProjects();
    }
    
    setupEventListeners() {
        // Set up event listeners for buttons, etc.
        // Follow Athena pattern with prometheus-specific elements
    }
    
    async loadProjects() {
        // Load project data from API
        try {
            this.state.loading = true;
            const projects = await this.client.getProjects();
            this.state.projects = projects;
            this.renderProjects();
        } catch (error) {
            console.error('[PROMETHEUS] Error loading projects:', error);
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
window.prometheusComponent = new PrometheusComponent();
export { PrometheusComponent };
```

## Service JavaScript Files

Create the necessary service files that follow the pattern from Athena:

1. **prometheus-service.js**: For API communication
2. **prometheus-timeline-service.js**: For timeline visualization

## Implementation Checklist

1. **Component Structure**
   - [ ] Implement basic HTML structure following Athena pattern
   - [ ] Add tab navigation with 6 tabs (Planning, Timeline, Resources, Analysis, Planning Chat, Team Chat)
   - [ ] Implement panel structure for each tab

2. **Styling**
   - [ ] Implement CSS with BEM naming (prometheus__*)
   - [ ] Maintain visual consistency with Athena, with Prometheus-specific colors
   - [ ] Ensure all height/spacing matches Athena component

3. **JavaScript**
   - [ ] Implement UI Manager protection
   - [ ] Implement HTML Panel protection
   - [ ] Implement tab switching functionality
   - [ ] Implement team chat functionality
   - [ ] Add loading/error handling

4. **Debug Instrumentation**
   - [ ] Add comprehensive logging with [PROMETHEUS] prefix
   - [ ] Add error handling and user feedback
   - [ ] Ensure proper debugging messages

## Prometheus-Specific Features

1. **Planning Panel**: Project list with status indicators
2. **Timeline Panel**: Timeline visualization with different views
3. **Resources Panel**: Resource allocation and management
4. **Analysis Panel**: Critical path analysis and bottleneck identification
5. **Planning Chat**: Planning-specific chat assistant
6. **Team Chat**: Standard team chat functionality

## Critical Implementation Requirements

**IMPORTANT**: This implementation guide MUST be followed exactly without any deviations. If any changes are proposed, they MUST be discussed with Casey (human-in-the-loop) first before implementation. No architectural changes, altered patterns, or extra features are allowed without explicit approval.

## Important Notes

1. **Use Athena as Reference**: Always refer to Athena component for patterns and structure
2. **Component Isolation**: Ensure all DOM queries are scoped to the prometheus container
3. **Consistent Naming**: Use 'prometheus__' prefix for all BEM class names
4. **Error Handling**: Implement robust error handling
5. **Debug Messages**: Use '[PROMETHEUS]' prefix for all console logs

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
2. Connect to Prometheus API endpoints
3. Implement actual timeline visualization
4. Add resource allocation visualization
5. Implement critical path analysis functionality