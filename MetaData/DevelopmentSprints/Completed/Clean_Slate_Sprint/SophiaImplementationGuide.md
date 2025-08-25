# Sophia Component Implementation Guide

## Overview

This document provides detailed guidance for implementing the Sophia component following the Clean Slate architecture. Sophia is Tekton's CI intelligence measurement and continuous improvement system, focusing on metrics collection, analysis, experimentation, and research.

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

1. **Component HTML**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/sophia/sophia-component.html`
2. **Component JavaScript**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/sophia/sophia-component.js`
3. **Service JavaScript**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/sophia/sophia-service.js` 
4. **Intelligence Service**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/sophia/sophia-intelligence-service.js`
5. **Analytics Service**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/sophia/sophia-analytics-service.js`

## HTML Component Structure

The HTML structure should follow the Athena component template exactly, with Sophia-specific content:

```html
<!-- Sophia Component - CI Intelligence & Continuous Improvement -->
<div class="sophia">
    <!-- Component Header with Title -->
    <div class="sophia__header">
        <div class="sophia__title-container">
            <img src="/images/hexagon.jpg" alt="Tekton" class="sophia__icon">
            <h2 class="sophia__title">
                <span class="sophia__title-main">Sophia</span>
                <span class="sophia__title-sub">Intelligence Measurement</span>
            </h2>
        </div>
    </div>
    
    <!-- Sophia Menu Bar with Tab Navigation -->
    <div class="sophia__menu-bar">
        <div class="sophia__tabs">
            <div class="sophia__tab sophia__tab--active" data-tab="metrics" onclick="sophia_switchTab('metrics'); return false;">
                <span class="sophia__tab-label">Metrics</span>
            </div>
            <div class="sophia__tab" data-tab="intelligence" onclick="sophia_switchTab('intelligence'); return false;">
                <span class="sophia__tab-label">Intelligence</span>
            </div>
            <div class="sophia__tab" data-tab="experiments" onclick="sophia_switchTab('experiments'); return false;">
                <span class="sophia__tab-label">Experiments</span>
            </div>
            <div class="sophia__tab" data-tab="recommendations" onclick="sophia_switchTab('recommendations'); return false;">
                <span class="sophia__tab-label">Recommendations</span>
            </div>
            <div class="sophia__tab" data-tab="researchchat" onclick="sophia_switchTab('researchchat'); return false;">
                <span class="sophia__tab-label">Research Chat</span>
            </div>
            <div class="sophia__tab" data-tab="teamchat" onclick="sophia_switchTab('teamchat'); return false;">
                <span class="sophia__tab-label">Team Chat</span>
            </div>
        </div>
        <div class="sophia__actions">
            <button id="clear-chat-btn" class="sophia__action-button" style="display: none;" onclick="sophia_clearChat(); return false;">
                <span class="sophia__button-label">Clear</span>
            </button>
        </div>
    </div>
    
    <!-- Sophia Content Area -->
    <div class="sophia__content">
        <!-- Metrics Tab (Default Active Tab) -->
        <div id="metrics-panel" class="sophia__panel sophia__panel--active">
            <div class="sophia__metrics">
                <div class="sophia__control-bar">
                    <div class="sophia__filter-container">
                        <div class="sophia__input-group">
                            <span class="sophia__input-label">Component</span>
                            <select id="sophia-metrics-component-filter" class="sophia__select">
                                <option value="">All Components</option>
                                <!-- Dynamically populated -->
                            </select>
                        </div>
                        <div class="sophia__input-group">
                            <span class="sophia__input-label">Metric Type</span>
                            <select id="sophia-metrics-type-filter" class="sophia__select">
                                <option value="">All Metrics</option>
                                <option value="performance">Performance</option>
                                <option value="resource">Resource</option>
                                <option value="accuracy">Accuracy</option>
                                <option value="behavioral">Behavioral</option>
                            </select>
                        </div>
                        <div class="sophia__input-group">
                            <span class="sophia__input-label">Time Range</span>
                            <select id="sophia-metrics-timerange" class="sophia__select">
                                <option value="1h">Last Hour</option>
                                <option value="6h">Last 6 Hours</option>
                                <option value="24h" selected>Last 24 Hours</option>
                                <option value="7d">Last 7 Days</option>
                                <option value="30d">Last 30 Days</option>
                            </select>
                        </div>
                    </div>
                    <div class="sophia__actions">
                        <button id="refresh-metrics-btn" class="sophia__action-button">
                            <span class="sophia__button-label">Refresh</span>
                        </button>
                    </div>
                </div>
                
                <!-- Metrics Charts -->
                <div class="sophia__charts-container">
                    <div class="sophia__chart-wrapper">
                        <h3 class="sophia__chart-title">Performance Metrics</h3>
                        <div id="sophia-performance-chart" class="sophia__chart"></div>
                    </div>
                    <div class="sophia__chart-wrapper">
                        <h3 class="sophia__chart-title">Resource Usage</h3>
                        <div id="sophia-resource-chart" class="sophia__chart"></div>
                    </div>
                    <div class="sophia__chart-wrapper">
                        <h3 class="sophia__chart-title">Component Communication</h3>
                        <div id="sophia-communication-chart" class="sophia__chart"></div>
                    </div>
                    <div class="sophia__chart-wrapper">
                        <h3 class="sophia__chart-title">Error Rates</h3>
                        <div id="sophia-error-chart" class="sophia__chart"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Intelligence Tab -->
        <div id="intelligence-panel" class="sophia__panel">
            <div class="sophia__intelligence">
                <div class="sophia__control-bar">
                    <div class="sophia__filter-container">
                        <div class="sophia__input-group">
                            <span class="sophia__input-label">Component</span>
                            <select id="sophia-intelligence-component-filter" class="sophia__select">
                                <option value="">All Components</option>
                                <!-- Dynamically populated -->
                            </select>
                        </div>
                        <div class="sophia__input-group">
                            <span class="sophia__input-label">Dimension</span>
                            <select id="sophia-intelligence-dimension-filter" class="sophia__select">
                                <option value="">All Dimensions</option>
                                <option value="language_processing">Language Processing</option>
                                <option value="reasoning">Reasoning</option>
                                <option value="knowledge">Knowledge</option>
                                <option value="learning">Learning</option>
                                <option value="creativity">Creativity</option>
                                <option value="planning">Planning</option>
                                <option value="problem_solving">Problem Solving</option>
                                <option value="adaptation">Adaptation</option>
                                <option value="collaboration">Collaboration</option>
                                <option value="metacognition">Metacognition</option>
                            </select>
                        </div>
                    </div>
                    <div class="sophia__actions">
                        <button id="add-measurement-btn" class="sophia__action-button">
                            <span class="sophia__button-icon">+</span>
                            <span class="sophia__button-label">New Measurement</span>
                        </button>
                    </div>
                </div>
                
                <!-- Intelligence Dashboard -->
                <div class="sophia__intelligence-dashboard">
                    <div class="sophia__radar-chart-wrapper">
                        <h3 class="sophia__section-title">Component Intelligence Profile</h3>
                        <div id="sophia-radar-chart" class="sophia__chart"></div>
                    </div>
                    <div class="sophia__dimension-details">
                        <h3 class="sophia__section-title">Dimension Details</h3>
                        <div id="sophia-dimension-table" class="sophia__table"></div>
                    </div>
                </div>
                
                <!-- Component Comparison -->
                <div class="sophia__intelligence-comparison">
                    <h3 class="sophia__section-title">Component Comparison</h3>
                    <div class="sophia__comparison-controls">
                        <div class="sophia__input-group sophia__input-group--inline">
                            <span class="sophia__input-label">Compare</span>
                            <select id="sophia-comparison-component1" class="sophia__select">
                                <!-- Dynamically populated -->
                            </select>
                            <span class="sophia__input-label">with</span>
                            <select id="sophia-comparison-component2" class="sophia__select">
                                <!-- Dynamically populated -->
                            </select>
                            <button id="sophia-compare-btn" class="sophia__button sophia__button--primary">Compare</button>
                        </div>
                    </div>
                    <div id="sophia-comparison-chart" class="sophia__chart"></div>
                </div>
            </div>
        </div>
        
        <!-- Experiments Tab -->
        <div id="experiments-panel" class="sophia__panel">
            <div class="sophia__experiments">
                <div class="sophia__control-bar">
                    <div class="sophia__filter-container">
                        <div class="sophia__input-group">
                            <span class="sophia__input-label">Status</span>
                            <select id="sophia-experiments-status-filter" class="sophia__select">
                                <option value="">All Statuses</option>
                                <option value="draft">Draft</option>
                                <option value="scheduled">Scheduled</option>
                                <option value="running">Running</option>
                                <option value="completed">Completed</option>
                                <option value="analyzing">Analyzing</option>
                                <option value="analyzed">Analyzed</option>
                            </select>
                        </div>
                        <div class="sophia__input-group">
                            <span class="sophia__input-label">Type</span>
                            <select id="sophia-experiments-type-filter" class="sophia__select">
                                <option value="">All Types</option>
                                <option value="a_b_test">A/B Test</option>
                                <option value="multivariate">Multivariate</option>
                                <option value="shadow_mode">Shadow Mode</option>
                                <option value="before_after">Before/After</option>
                            </select>
                        </div>
                    </div>
                    <div class="sophia__actions">
                        <button id="new-experiment-btn" class="sophia__action-button">
                            <span class="sophia__button-icon">+</span>
                            <span class="sophia__button-label">New Experiment</span>
                        </button>
                    </div>
                </div>
                
                <!-- Experiments List -->
                <div class="sophia__experiments-list">
                    <div id="experiments-loading" class="sophia__loading-indicator">
                        <div class="sophia__spinner"></div>
                        <div class="sophia__loading-text">Loading experiments...</div>
                    </div>
                    <table class="sophia__table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Type</th>
                                <th>Status</th>
                                <th>Components</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="sophia-experiments-tbody">
                            <!-- Dynamically populated -->
                            <tr class="sophia__table-row">
                                <td>Claude vs GPT Response Quality</td>
                                <td>A/B Test</td>
                                <td><span class="sophia__status sophia__status--completed">Completed</span></td>
                                <td>Terma, Rhetor</td>
                                <td>2025-04-22</td>
                                <td>
                                    <button class="sophia__button sophia__button--small">View</button>
                                    <button class="sophia__button sophia__button--small">Results</button>
                                </td>
                            </tr>
                            <tr class="sophia__table-row">
                                <td>Memory Retrieval Optimization</td>
                                <td>Multivariate</td>
                                <td><span class="sophia__status sophia__status--running">Running</span></td>
                                <td>Engram</td>
                                <td>2025-05-01</td>
                                <td>
                                    <button class="sophia__button sophia__button--small">View</button>
                                    <button class="sophia__button sophia__button--small">Monitor</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Recommendations Tab -->
        <div id="recommendations-panel" class="sophia__panel">
            <div class="sophia__recommendations">
                <div class="sophia__control-bar">
                    <div class="sophia__filter-container">
                        <div class="sophia__input-group">
                            <span class="sophia__input-label">Status</span>
                            <select id="sophia-recommendations-status-filter" class="sophia__select">
                                <option value="">All Statuses</option>
                                <option value="pending">Pending</option>
                                <option value="approved">Approved</option>
                                <option value="in_progress">In Progress</option>
                                <option value="implemented">Implemented</option>
                                <option value="verified">Verified</option>
                                <option value="rejected">Rejected</option>
                            </select>
                        </div>
                        <div class="sophia__input-group">
                            <span class="sophia__input-label">Priority</span>
                            <select id="sophia-recommendations-priority-filter" class="sophia__select">
                                <option value="">All Priorities</option>
                                <option value="critical">Critical</option>
                                <option value="high">High</option>
                                <option value="medium">Medium</option>
                                <option value="low">Low</option>
                            </select>
                        </div>
                        <div class="sophia__input-group">
                            <span class="sophia__input-label">Component</span>
                            <select id="sophia-recommendations-component-filter" class="sophia__select">
                                <option value="">All Components</option>
                                <!-- Dynamically populated -->
                            </select>
                        </div>
                    </div>
                    <div class="sophia__actions">
                        <button id="new-recommendation-btn" class="sophia__action-button">
                            <span class="sophia__button-icon">+</span>
                            <span class="sophia__button-label">New Recommendation</span>
                        </button>
                    </div>
                </div>
                
                <!-- Recommendations List -->
                <div class="sophia__recommendations-list">
                    <div id="recommendations-loading" class="sophia__loading-indicator">
                        <div class="sophia__spinner"></div>
                        <div class="sophia__loading-text">Loading recommendations...</div>
                    </div>
                    <table class="sophia__table">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Type</th>
                                <th>Priority</th>
                                <th>Components</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="sophia-recommendations-tbody">
                            <!-- Dynamically populated -->
                            <tr class="sophia__table-row">
                                <td>Implement Semantic Search for Engram</td>
                                <td>Enhancement</td>
                                <td><span class="sophia__priority sophia__priority--high">High</span></td>
                                <td>Engram</td>
                                <td><span class="sophia__status sophia__status--in-progress">In Progress</span></td>
                                <td>
                                    <button class="sophia__button sophia__button--small">View</button>
                                    <button class="sophia__button sophia__button--small">Update</button>
                                </td>
                            </tr>
                            <tr class="sophia__table-row">
                                <td>Optimize Harmonia Workflow Engine</td>
                                <td>Performance</td>
                                <td><span class="sophia__priority sophia__priority--medium">Medium</span></td>
                                <td>Harmonia</td>
                                <td><span class="sophia__status sophia__status--pending">Pending</span></td>
                                <td>
                                    <button class="sophia__button sophia__button--small">View</button>
                                    <button class="sophia__button sophia__button--small">Approve</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Research Chat Tab -->
        <div id="researchchat-panel" class="sophia__panel">
            <div id="researchchat-messages" class="sophia__chat-messages">
                <!-- Welcome message -->
                <div class="sophia__message sophia__message--system">
                    <div class="sophia__message-content">
                        <div class="sophia__message-text">
                            <h3 class="sophia__message-title">CI Research Assistant</h3>
                            <p>This chat provides assistance with CI research and intelligence measurement. Ask questions about:</p>
                            <ul>
                                <li>Intelligence dimensions and measurements</li>
                                <li>Experiment design and analysis</li>
                                <li>Computational Spectral Analysis</li>
                                <li>Research methodologies and approaches</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Team Chat Tab -->
        <div id="teamchat-panel" class="sophia__panel">
            <div id="teamchat-messages" class="sophia__chat-messages">
                <!-- Welcome message -->
                <div class="sophia__message sophia__message--system">
                    <div class="sophia__message-content">
                        <div class="sophia__message-text">
                            <h3 class="sophia__message-title">Tekton Team Chat</h3>
                            <p>This chat is shared across all Tekton components. Use this for team communication and coordination.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Footer with Chat Input -->
    <div class="sophia__footer">
        <div class="sophia__chat-input-container">
            <div class="sophia__chat-prompt">></div>
            <input type="text" id="chat-input" class="sophia__chat-input" 
                   placeholder="Enter chat message, research questions, or experiment ideas">
            <button id="send-button" class="sophia__send-button">Send</button>
        </div>
    </div>
</div>
```

## CSS Styling

The CSS should follow Athena's BEM naming structure, maintaining the same visual appearance and layout but with Sophia-specific color scheme:

```css
/* Sophia component styles using BEM naming convention */

/* Container */
.sophia {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    background-color: var(--bg-primary, #1e1e2e);
    color: var(--text-primary, #f0f0f0);
    /* No absolute positioning - proper component containment */
}

/* Header */
.sophia__header {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 50px; /* Match header height from Athena */
}

.sophia__title-container {
    display: flex;
    align-items: center;
}

.sophia__icon {
    height: 30px;
    width: auto;
    margin-right: 12px;
}

.sophia__title {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 500;
}

.sophia__title-sub {
    margin-left: 8px;
    opacity: 0.8;
    font-weight: normal;
}

/* Menu Bar */
.sophia__menu-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 46px; /* Match menu bar height from Athena */
}

.sophia__tabs {
    display: flex;
    gap: 8px;
}

.sophia__tab {
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

.sophia__tab:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

.sophia__tab--active {
    border-bottom-color: var(--color-primary, #9C27B0); /* Sophia purple color */
    font-weight: 500;
}

/* Content Area */
.sophia__content {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.sophia__panel {
    display: none;
    height: 100%;
    overflow: auto;
    padding: 16px;
}

.sophia__panel--active {
    display: block;
}

/* Control Bar */
.sophia__control-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding: 8px;
    background-color: var(--bg-secondary, #252535);
    border-radius: 4px;
}

.sophia__filter-container {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.sophia__input-group {
    display: flex;
    align-items: center;
    gap: 8px;
}

.sophia__input-label {
    font-size: 0.9rem;
    white-space: nowrap;
}

.sophia__select {
    background-color: var(--bg-element, #2a2a3a);
    color: var(--text-primary, #f0f0f0);
    border: 1px solid var(--border-color, #444444);
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 0.9rem;
}

/* Charts */
.sophia__charts-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
    margin-top: 16px;
}

.sophia__chart-wrapper {
    background-color: var(--bg-secondary, #252535);
    border: 1px solid var(--border-color, #444444);
    border-radius: 4px;
    padding: 12px;
}

.sophia__chart-title {
    margin-top: 0;
    margin-bottom: 12px;
    font-size: 1rem;
    font-weight: 500;
}

.sophia__chart {
    width: 100%;
    height: 200px;
    background-color: var(--bg-element, #2a2a3a);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Tables */
.sophia__table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 16px;
}

.sophia__table th,
.sophia__table td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid var(--border-color, #444444);
}

.sophia__table th {
    font-weight: 500;
    background-color: var(--bg-secondary, #252535);
}

.sophia__table-row:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

/* Status Indicators */
.sophia__status {
    padding: 4px 8px;
    border-radius: 3px;
    font-size: 0.8rem;
    display: inline-block;
}

.sophia__status--completed { background-color: #4CAF50; color: white; }
.sophia__status--running { background-color: #2196F3; color: white; }
.sophia__status--pending { background-color: #FFC107; color: black; }
.sophia__status--in-progress { background-color: #03A9F4; color: white; }

/* Priority Indicators */
.sophia__priority {
    padding: 4px 8px;
    border-radius: 3px;
    font-size: 0.8rem;
    display: inline-block;
}

.sophia__priority--critical { background-color: #F44336; color: white; }
.sophia__priority--high { background-color: #FF5722; color: white; }
.sophia__priority--medium { background-color: #FF9800; color: black; }
.sophia__priority--low { background-color: #8BC34A; color: black; }

/* Buttons */
.sophia__action-button {
    display: flex;
    align-items: center;
    gap: 6px;
    background-color: var(--bg-element, #2a2a3a);
    color: var(--text-primary, #f0f0f0);
    border: 1px solid var(--border-color, #444444);
    border-radius: 4px;
    padding: 6px 12px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.sophia__action-button:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

.sophia__button {
    background-color: var(--bg-element, #2a2a3a);
    color: var(--text-primary, #f0f0f0);
    border: 1px solid var(--border-color, #444444);
    border-radius: 4px;
    padding: 6px 12px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.sophia__button:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

.sophia__button--primary {
    background-color: var(--color-primary, #9C27B0);
    color: white;
    border-color: var(--color-primary, #9C27B0);
}

.sophia__button--small {
    padding: 3px 8px;
    font-size: 0.8rem;
}

/* Loading Indicator */
.sophia__loading-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 0;
}

.sophia__spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-top-color: var(--color-primary, #9C27B0);
    border-radius: 50%;
    animation: sophia-spin 1s linear infinite;
}

@keyframes sophia-spin {
    to { transform: rotate(360deg); }
}

.sophia__loading-text {
    margin-top: 12px;
    font-size: 0.9rem;
    color: var(--text-secondary, #aaaaaa);
}

/* Chat Areas */
.sophia__chat-messages {
    display: flex;
    flex-direction: column;
    gap: 12px;
    overflow-y: auto;
    flex: 1;
    padding-bottom: 16px;
}

.sophia__message {
    display: flex;
    align-items: flex-start;
    gap: 10px;
}

.sophia__message-content {
    background-color: var(--bg-secondary, #252535);
    border-radius: 12px;
    padding: 12px;
    max-width: 80%;
}

.sophia__message--system .sophia__message-content {
    background-color: var(--bg-element, #2a2a3a);
    border-left: 3px solid var(--color-primary, #9C27B0);
    border-radius: 4px;
    max-width: 100%;
    margin-bottom: 16px;
}

.sophia__message-title {
    margin-top: 0;
    margin-bottom: 8px;
    font-size: 1rem;
    font-weight: 500;
}

/* Footer */
.sophia__footer {
    padding: 12px 16px;
    background-color: var(--bg-secondary, #252535);
    border-top: 1px solid var(--border-color, #444444);
}

.sophia__chat-input-container {
    display: flex;
    align-items: center;
    gap: 8px;
}

.sophia__chat-prompt {
    font-weight: bold;
    color: var(--color-primary, #9C27B0);
}

.sophia__chat-input {
    flex: 1;
    background-color: var(--bg-element, #2a2a3a);
    color: var(--text-primary, #f0f0f0);
    border: 1px solid var(--border-color, #444444);
    border-radius: 4px;
    padding: 8px 12px;
    outline: none;
}

.sophia__chat-input:focus {
    border-color: var(--color-primary, #9C27B0);
}

.sophia__send-button {
    background-color: var(--color-primary, #9C27B0);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.sophia__send-button:hover {
    background-color: #7B1FA2; /* Darker purple */
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
    window.uiManager._ignoreComponent = 'sophia';
    console.log('[SOPHIA] Set UI Manager to ignore sophia component');
}

// DEFINE TAB SWITCHING FUNCTION
// CRITICAL: This uses no shared code/utilities to avoid conflicts
window.sophia_switchTab = function(tabId) {
    console.log('[SOPHIA] Switching to tab:', tabId);
    
    // Force HTML panel visibility
    const htmlPanelElements = document.querySelectorAll('#html-panel');
    htmlPanelElements.forEach(panel => {
        if (panel) panel.style.display = 'block';
    });
    
    try {
        // Only select elements within sophia component to avoid conflicts with other components
        const sophiaContainer = document.querySelector('.sophia');
        if (!sophiaContainer) {
            console.error('[SOPHIA] Tab Switch: Cannot find sophia container');
            return false;
        }
        
        // Update tab active state - ONLY WITHIN SOPHIA CONTAINER
        const tabs = sophiaContainer.querySelectorAll('.sophia__tab');
        tabs.forEach(tab => {
            if (tab.getAttribute('data-tab') === tabId) {
                tab.classList.add('sophia__tab--active');
            } else {
                tab.classList.remove('sophia__tab--active');
            }
        });
        
        // Update panel visibility - ONLY WITHIN SOPHIA CONTAINER
        const panels = sophiaContainer.querySelectorAll('.sophia__panel');
        panels.forEach(panel => {
            const panelId = panel.id;
            if (panelId === tabId + '-panel') {
                panel.style.display = 'block';
                panel.classList.add('sophia__panel--active');
            } else {
                panel.style.display = 'none';
                panel.classList.remove('sophia__panel--active');
            }
        });
        
        // Update clear button visibility for chat tabs
        const clearButton = sophiaContainer.querySelector('#clear-chat-btn');
        if (clearButton) {
            clearButton.style.display = (tabId === 'teamchat' || tabId === 'researchchat') ? 'block' : 'none';
        }
        
        // Update chat input placeholder based on active tab
        const chatInput = sophiaContainer.querySelector('#chat-input');
        if (chatInput) {
            if (tabId === 'researchchat') {
                chatInput.placeholder = 'Enter research questions or CI intelligence queries...';
            } else if (tabId === 'teamchat') {
                chatInput.placeholder = 'Enter team chat message...';
            }
        }
        
        // Update component state
        if (window.sophiaComponent) {
            window.sophiaComponent.state = window.sophiaComponent.state || {};
            window.sophiaComponent.state.activeTab = tabId;
            
            // Call component-specific methods if available
            if (typeof window.sophiaComponent.updateChatPlaceholder === 'function') {
                window.sophiaComponent.updateChatPlaceholder(tabId);
            }
            
            if (typeof window.sophiaComponent.loadTabContent === 'function') {
                window.sophiaComponent.loadTabContent(tabId);
            }
            
            if (typeof window.sophiaComponent.saveComponentState === 'function') {
                window.sophiaComponent.saveComponentState();
            }
        }
    } catch (err) {
        console.error('[SOPHIA] Error in tab switching:', err);
    }
    
    return false; // Stop event propagation
};

// CHAT CLEARING FUNCTION - Same pattern as Athena
window.sophia_clearChat = function() {
    console.log('[SOPHIA] Clearing chat');
    
    try {
        // Get the sophia container to scope our operations
        const sophiaContainer = document.querySelector('.sophia');
        if (!sophiaContainer) {
            console.error('[SOPHIA] Clear Chat: Cannot find sophia container');
            return false;
        }
        
        // Determine active chat panel
        const activeTab = sophiaContainer.querySelector('.sophia__tab--active');
        if (!activeTab) {
            console.error('[SOPHIA] Clear Chat: No active tab found');
            return false;
        }
        
        const tabId = activeTab.getAttribute('data-tab');
        if (tabId !== 'teamchat' && tabId !== 'researchchat') {
            console.error('[SOPHIA] Clear Chat: Active tab is not a chat tab');
            return false;
        }
        
        // Clear messages in the active chat panel except for the welcome message
        const chatPanelId = tabId + '-panel';
        const chatPanel = sophiaContainer.querySelector('#' + chatPanelId);
        if (!chatPanel) {
            console.error('[SOPHIA] Clear Chat: Cannot find chat panel');
            return false;
        }
        
        const messagesContainer = chatPanel.querySelector(`#${tabId}-messages`);
        if (!messagesContainer) {
            console.error('[SOPHIA] Clear Chat: Cannot find messages container');
            return false;
        }
        
        // Keep only the first message (welcome message)
        const allMessages = messagesContainer.querySelectorAll('.sophia__message');
        for (let i = 1; i < allMessages.length; i++) {
            allMessages[i].remove();
        }
        
        // Update component state if available
        if (window.sophiaComponent && typeof window.sophiaComponent.clearChatMessages === 'function') {
            window.sophiaComponent.clearChatMessages(tabId);
        }
    } catch (err) {
        console.error('[SOPHIA] Error clearing chat:', err);
    }
    
    return false; // Stop event propagation
};
```

## Isolated Component JavaScript

Create a separate file `sophia-component.js` that follows the same structure as Athena's component JS:

```javascript
/**
 * Sophia Intelligence Measurement Component
 * 
 * Provides interfaces for metrics collection, intelligence measurement,
 * experiment management, and continuous improvement.
 */

class SophiaComponent {
    constructor() {
        // Initialize properties
        this.state = {
            activeTab: 'metrics',
            components: [],
            metrics: {},
            experiments: [],
            recommendations: [],
            loading: {
                metrics: false,
                intelligence: false,
                experiments: false,
                recommendations: false
            }
        };
        
        // Debug output
        console.log('[SOPHIA] Component constructed');
    }
    
    async init() {
        console.log('[SOPHIA] Initializing component');
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial data
        this.loadComponents();
        this.loadMetricsData();
        
        // Save state to local storage
        this.saveComponentState();
    }
    
    setupEventListeners() {
        try {
            // Get container to scope DOM queries
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) {
                console.error('[SOPHIA] Could not find sophia container');
                return;
            }
            
            // Set up send button for chat
            const sendButton = sophiaContainer.querySelector('#send-button');
            if (sendButton) {
                sendButton.addEventListener('click', () => this.handleChatSend());
            }
            
            // Set up chat input for Enter key
            const chatInput = sophiaContainer.querySelector('#chat-input');
            if (chatInput) {
                chatInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        this.handleChatSend();
                    }
                });
            }
            
            // Set up refresh metrics button
            const refreshButton = sophiaContainer.querySelector('#refresh-metrics-btn');
            if (refreshButton) {
                refreshButton.addEventListener('click', () => this.refreshMetrics());
            }
            
            // Setup experiment actions
            const newExperimentBtn = sophiaContainer.querySelector('#new-experiment-btn');
            if (newExperimentBtn) {
                newExperimentBtn.addEventListener('click', () => this.showNewExperimentForm());
            }
            
            // Setup recommendation actions
            const newRecommendationBtn = sophiaContainer.querySelector('#new-recommendation-btn');
            if (newRecommendationBtn) {
                newRecommendationBtn.addEventListener('click', () => this.showNewRecommendationForm());
            }
            
            // Setup intelligence comparison
            const compareBtn = sophiaContainer.querySelector('#sophia-compare-btn');
            if (compareBtn) {
                compareBtn.addEventListener('click', () => this.compareComponents());
            }
            
            // Setup filters
            this.setupFilters(sophiaContainer);
            
            console.log('[SOPHIA] Event listeners set up');
        } catch (error) {
            console.error('[SOPHIA] Error setting up event listeners:', error);
        }
    }
    
    setupFilters(container) {
        // Set up filter change handlers
        // Implementation follows Athena pattern
    }
    
    async loadComponents() {
        try {
            // Load component list for filters
            this.state.loading.components = true;
            
            // Simulate API call or use actual API
            setTimeout(() => {
                this.state.components = [
                    { id: 'athena', name: 'Athena' },
                    { id: 'engram', name: 'Engram' },
                    { id: 'harmonia', name: 'Harmonia' },
                    { id: 'hermes', name: 'Hermes' },
                    { id: 'prometheus', name: 'Prometheus' },
                    { id: 'rhetor', name: 'Rhetor' },
                    { id: 'terma', name: 'Terma' }
                ];
                
                this.updateComponentSelectors();
                this.state.loading.components = false;
            }, 500);
        } catch (error) {
            console.error('[SOPHIA] Error loading components:', error);
            this.state.loading.components = false;
        }
    }
    
    updateComponentSelectors() {
        try {
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            // Update all component selectors with current component list
            const selectors = [
                '#sophia-metrics-component-filter',
                '#sophia-intelligence-component-filter',
                '#sophia-recommendations-component-filter',
                '#sophia-comparison-component1',
                '#sophia-comparison-component2'
            ];
            
            selectors.forEach(selectorId => {
                const selector = sophiaContainer.querySelector(selectorId);
                if (!selector) return;
                
                // Save current selection
                const currentSelection = selector.value;
                
                // Clear existing options (keep first default option)
                while (selector.options.length > 1) {
                    selector.remove(1);
                }
                
                // Add component options
                this.state.components.forEach(component => {
                    const option = document.createElement('option');
                    option.value = component.id;
                    option.text = component.name;
                    selector.add(option);
                });
                
                // Restore selection if it exists
                if (currentSelection) {
                    selector.value = currentSelection;
                }
            });
        } catch (error) {
            console.error('[SOPHIA] Error updating component selectors:', error);
        }
    }
    
    async loadMetricsData() {
        try {
            this.state.loading.metrics = true;
            
            // Simulate API call or use actual API
            setTimeout(() => {
                // Sample data - would be replaced with actual API data
                this.state.metrics = {
                    performance: [
                        { timestamp: '2025-05-01', value: 86, component: 'engram' },
                        { timestamp: '2025-05-02', value: 89, component: 'engram' },
                        { timestamp: '2025-05-03', value: 92, component: 'engram' },
                        { timestamp: '2025-05-04', value: 88, component: 'engram' },
                        { timestamp: '2025-05-05', value: 91, component: 'engram' }
                    ],
                    resource: [
                        { timestamp: '2025-05-01', value: 45, component: 'engram' },
                        { timestamp: '2025-05-02', value: 48, component: 'engram' },
                        { timestamp: '2025-05-03', value: 52, component: 'engram' },
                        { timestamp: '2025-05-04', value: 49, component: 'engram' },
                        { timestamp: '2025-05-05', value: 46, component: 'engram' }
                    ]
                };
                
                this.renderMetricsCharts();
                this.state.loading.metrics = false;
            }, 800);
        } catch (error) {
            console.error('[SOPHIA] Error loading metrics data:', error);
            this.state.loading.metrics = false;
        }
    }
    
    renderMetricsCharts() {
        // Render metrics charts with the data
        console.log('[SOPHIA] Rendering metrics charts');
        
        // Implementation would use appropriate charting library
        // This would be similar to the Athena charts implementation
    }
    
    refreshMetrics() {
        console.log('[SOPHIA] Refreshing metrics');
        this.loadMetricsData();
    }
    
    async loadTabContent(tabId) {
        console.log('[SOPHIA] Loading tab content for:', tabId);
        
        // Load data for specific tabs when they are activated
        if (tabId === 'metrics' && !this.state.metrics.performance) {
            this.loadMetricsData();
        } else if (tabId === 'intelligence') {
            this.loadIntelligenceData();
        } else if (tabId === 'experiments' && this.state.experiments.length === 0) {
            this.loadExperiments();
        } else if (tabId === 'recommendations' && this.state.recommendations.length === 0) {
            this.loadRecommendations();
        }
    }
    
    // Additional methods for other tabs
    async loadIntelligenceData() {
        // Implementation similar to loadMetricsData
    }
    
    async loadExperiments() {
        // Implementation similar to loadMetricsData
    }
    
    async loadRecommendations() {
        // Implementation similar to loadMetricsData
    }
    
    // Chat functionality
    updateChatPlaceholder(tabId) {
        try {
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            const chatInput = sophiaContainer.querySelector('#chat-input');
            if (!chatInput) return;
            
            if (tabId === 'researchchat') {
                chatInput.placeholder = 'Enter research questions or CI intelligence queries...';
            } else if (tabId === 'teamchat') {
                chatInput.placeholder = 'Enter team chat message...';
            } else {
                chatInput.placeholder = 'Enter chat message, research questions, or experiment ideas';
            }
        } catch (error) {
            console.error('[SOPHIA] Error updating chat placeholder:', error);
        }
    }
    
    handleChatSend() {
        try {
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            const chatInput = sophiaContainer.querySelector('#chat-input');
            if (!chatInput || !chatInput.value.trim()) return;
            
            const message = chatInput.value.trim();
            chatInput.value = '';
            
            // Determine active chat tab
            const activeTab = this.state.activeTab;
            if (activeTab !== 'teamchat' && activeTab !== 'researchchat') {
                console.error('[SOPHIA] Cannot send message: no chat tab active');
                return;
            }
            
            this.addChatMessage(message, activeTab, 'user');
            
            // Simulate response for demo
            setTimeout(() => {
                const responseText = activeTab === 'researchchat' 
                    ? `Here's my analysis on your research question: "${message}". The CI intelligence measurements indicate...`
                    : `Team member response to your message: "${message}"`;
                
                this.addChatMessage(responseText, activeTab, 'assistant');
            }, 1000);
        } catch (error) {
            console.error('[SOPHIA] Error handling chat send:', error);
        }
    }
    
    addChatMessage(text, tabId, sender) {
        try {
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            const messagesContainer = sophiaContainer.querySelector(`#${tabId}-messages`);
            if (!messagesContainer) return;
            
            // Create message element
            const messageDiv = document.createElement('div');
            messageDiv.className = `sophia__message sophia__message--${sender}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'sophia__message-content';
            
            const textDiv = document.createElement('div');
            textDiv.className = 'sophia__message-text';
            textDiv.textContent = text;
            
            contentDiv.appendChild(textDiv);
            messageDiv.appendChild(contentDiv);
            messagesContainer.appendChild(messageDiv);
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        } catch (error) {
            console.error('[SOPHIA] Error adding chat message:', error);
        }
    }
    
    clearChatMessages(tabId) {
        // Implementation to clear chat state
    }
    
    // Component state persistence
    saveComponentState() {
        try {
            // Save component state to localStorage
            const stateToSave = {
                activeTab: this.state.activeTab,
                filters: {
                    metrics: {
                        component: document.querySelector('#sophia-metrics-component-filter')?.value,
                        type: document.querySelector('#sophia-metrics-type-filter')?.value,
                        timerange: document.querySelector('#sophia-metrics-timerange')?.value
                    },
                    // Other filter states
                }
            };
            
            localStorage.setItem('sophia_component_state', JSON.stringify(stateToSave));
            console.log('[SOPHIA] Component state saved');
        } catch (error) {
            console.error('[SOPHIA] Error saving component state:', error);
        }
    }
    
    loadComponentState() {
        try {
            // Load component state from localStorage
            const savedState = localStorage.getItem('sophia_component_state');
            if (!savedState) return;
            
            const parsedState = JSON.parse(savedState);
            
            // Restore tab if needed
            if (parsedState.activeTab && parsedState.activeTab !== 'metrics') {
                window.sophia_switchTab(parsedState.activeTab);
            }
            
            // Restore filter values
            if (parsedState.filters?.metrics) {
                const filters = parsedState.filters.metrics;
                
                if (filters.component) {
                    document.querySelector('#sophia-metrics-component-filter').value = filters.component;
                }
                
                if (filters.type) {
                    document.querySelector('#sophia-metrics-type-filter').value = filters.type;
                }
                
                if (filters.timerange) {
                    document.querySelector('#sophia-metrics-timerange').value = filters.timerange;
                }
            }
            
            // Other state restoration
            
            console.log('[SOPHIA] Component state loaded');
        } catch (error) {
            console.error('[SOPHIA] Error loading component state:', error);
        }
    }
}

// Initialize and export the component
window.sophiaComponent = new SophiaComponent();
document.addEventListener('DOMContentLoaded', () => {
    window.sophiaComponent.init();
    window.sophiaComponent.loadComponentState();
});
```

## Service JavaScript Files

Create the necessary service files that follow the pattern from Athena:

1. **sophia-service.js**: For API communication
2. **sophia-intelligence-service.js**: For intelligence visualization and analysis
3. **sophia-analytics-service.js**: For metrics and analytics

## Implementation Checklist

1. **Component Structure**
   - [ ] Implement basic HTML structure following Athena pattern
   - [ ] Add tab navigation with 6 tabs (Metrics, Intelligence, Experiments, Recommendations, Research Chat, Team Chat)
   - [ ] Implement panel structure for each tab

2. **Styling**
   - [ ] Implement CSS with BEM naming (sophia__*)
   - [ ] Maintain visual consistency with Athena, with Sophia-specific colors
   - [ ] Ensure all height/spacing matches Athena component

3. **JavaScript**
   - [ ] Implement UI Manager protection
   - [ ] Implement HTML Panel protection
   - [ ] Implement tab switching functionality
   - [ ] Implement chat functionality
   - [ ] Add loading/error handling

4. **Debug Instrumentation**
   - [ ] Add comprehensive logging with [SOPHIA] prefix
   - [ ] Add error handling and user feedback
   - [ ] Ensure proper debugging messages

## Sophia-Specific Features

1. **Metrics Panel**: Metrics dashboard with filtering and charts
2. **Intelligence Panel**: Intelligence dimension visualization and comparison
3. **Experiments Panel**: Experiment management and results tracking
4. **Recommendations Panel**: Improvement recommendations tracking
5. **Research Chat**: CI research assistant for intelligence questions
6. **Team Chat**: Standard team chat functionality

## Critical Implementation Requirements

**IMPORTANT**: This implementation guide MUST be followed exactly without any deviations. If any changes are proposed, they MUST be discussed with Casey (human-in-the-loop) first before implementation. No architectural changes, altered patterns, or extra features are allowed without explicit approval.

## Important Notes

1. **Use Athena as Reference**: Always refer to Athena component for patterns and structure
2. **Component Isolation**: Ensure all DOM queries are scoped to the sophia container
3. **Consistent Naming**: Use 'sophia__' prefix for all BEM class names
4. **Error Handling**: Implement robust error handling
5. **Debug Messages**: Use '[SOPHIA]' prefix for all console logs

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
2. Connect to Sophia API endpoints
3. Implement intelligence radar visualization
4. Add experiment tracking functionality
5. Integrate with the shared team chat system