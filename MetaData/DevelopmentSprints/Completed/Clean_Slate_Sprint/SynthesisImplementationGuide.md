# Synthesis Component Implementation Guide

## Overview

This document provides detailed guidance for implementing the Synthesis component following the Clean Slate architecture. Synthesis is Tekton's execution and integration engine, responsible for orchestrating workflows, executing processes, and integrating with external systems.

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

1. **Component HTML**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/synthesis/synthesis-component.html`
2. **Component JavaScript**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/synthesis/synthesis-component.js`
3. **Service JavaScript**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/synthesis/synthesis-service.js` 
4. **Execution Engine**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/synthesis/execution-engine.js`
5. **Workflow Manager**: `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/synthesis/workflow-manager.js`

## HTML Component Structure

The HTML structure should follow the Athena component template exactly, with Synthesis-specific content:

```html
<!-- Synthesis Component - Execution & Integration Engine -->
<div class="synthesis">
    <!-- Component Header with Title -->
    <div class="synthesis__header">
        <div class="synthesis__title-container">
            <img src="/images/hexagon.jpg" alt="Tekton" class="synthesis__icon">
            <h2 class="synthesis__title">
                <span class="synthesis__title-main">Synthesis</span>
                <span class="synthesis__title-sub">Execution Engine</span>
            </h2>
        </div>
    </div>
    
    <!-- Synthesis Menu Bar with Tab Navigation -->
    <div class="synthesis__menu-bar">
        <div class="synthesis__tabs">
            <div class="synthesis__tab synthesis__tab--active" data-tab="executions" onclick="synthesis_switchTab('executions'); return false;">
                <span class="synthesis__tab-label">Executions</span>
            </div>
            <div class="synthesis__tab" data-tab="workflows" onclick="synthesis_switchTab('workflows'); return false;">
                <span class="synthesis__tab-label">Workflows</span>
            </div>
            <div class="synthesis__tab" data-tab="monitoring" onclick="synthesis_switchTab('monitoring'); return false;">
                <span class="synthesis__tab-label">Monitoring</span>
            </div>
            <div class="synthesis__tab" data-tab="history" onclick="synthesis_switchTab('history'); return false;">
                <span class="synthesis__tab-label">History</span>
            </div>
            <div class="synthesis__tab" data-tab="execchat" onclick="synthesis_switchTab('execchat'); return false;">
                <span class="synthesis__tab-label">Execution Chat</span>
            </div>
            <div class="synthesis__tab" data-tab="teamchat" onclick="synthesis_switchTab('teamchat'); return false;">
                <span class="synthesis__tab-label">Team Chat</span>
            </div>
        </div>
        <div class="synthesis__actions">
            <button id="clear-chat-btn" class="synthesis__action-button" style="display: none;" onclick="synthesis_clearChat(); return false;">
                <span class="synthesis__button-label">Clear</span>
            </button>
        </div>
    </div>
    
    <!-- Synthesis Content Area -->
    <div class="synthesis__content">
        <!-- Executions Tab (Default Active Tab) -->
        <div id="executions-panel" class="synthesis__panel synthesis__panel--active">
            <div class="synthesis__executions">
                <div class="synthesis__control-bar">
                    <div class="synthesis__search-container">
                        <input type="text" id="execution-search" class="synthesis__search-input" placeholder="Search executions...">
                        <button id="execution-search-btn" class="synthesis__search-button">Search</button>
                    </div>
                    <div class="synthesis__actions">
                        <button id="new-execution-btn" class="synthesis__action-button">
                            <span class="synthesis__button-icon">+</span>
                            <span class="synthesis__button-label">New Execution</span>
                        </button>
                        <button id="refresh-executions-btn" class="synthesis__action-button">
                            <span class="synthesis__button-label">Refresh</span>
                        </button>
                    </div>
                </div>
                
                <div class="synthesis__executions-list-container">
                    <div id="executions-list-loading" class="synthesis__loading-indicator">
                        <div class="synthesis__spinner"></div>
                        <div class="synthesis__loading-text">Loading executions...</div>
                    </div>
                    <div id="executions-list" class="synthesis__executions-list" style="display: none;">
                        <!-- Sample executions for UI testing -->
                        <div class="synthesis__execution-item synthesis__execution-item--running">
                            <div class="synthesis__execution-header">
                                <div class="synthesis__execution-title">Document Processing Pipeline</div>
                                <div class="synthesis__execution-meta">
                                    <span class="synthesis__execution-id">exec-23a5f9d7</span>
                                    <span class="synthesis__execution-status synthesis__execution-status--running">Running</span>
                                </div>
                            </div>
                            <div class="synthesis__execution-progress">
                                <div class="synthesis__progress-bar">
                                    <div class="synthesis__progress-fill" style="width: 45%"></div>
                                </div>
                                <div class="synthesis__progress-text">45% (Step 5 of 11)</div>
                            </div>
                            <div class="synthesis__execution-actions">
                                <button class="synthesis__button synthesis__button--small">View Details</button>
                                <button class="synthesis__button synthesis__button--small">Cancel</button>
                            </div>
                        </div>
                        
                        <div class="synthesis__execution-item synthesis__execution-item--completed">
                            <div class="synthesis__execution-header">
                                <div class="synthesis__execution-title">System Health Check</div>
                                <div class="synthesis__execution-meta">
                                    <span class="synthesis__execution-id">exec-18e7c3b2</span>
                                    <span class="synthesis__execution-status synthesis__execution-status--completed">Completed</span>
                                </div>
                            </div>
                            <div class="synthesis__execution-progress">
                                <div class="synthesis__progress-bar">
                                    <div class="synthesis__progress-fill" style="width: 100%"></div>
                                </div>
                                <div class="synthesis__progress-text">Completed (8/8 steps)</div>
                            </div>
                            <div class="synthesis__execution-actions">
                                <button class="synthesis__button synthesis__button--small">View Details</button>
                                <button class="synthesis__button synthesis__button--small">Rerun</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="synthesis__execution-details-container" id="execution-details-panel">
                    <div class="synthesis__empty-state">
                        <div class="synthesis__empty-state-content">
                            <h3 class="synthesis__empty-state-title">Select an execution to view details</h3>
                            <p class="synthesis__empty-state-text">Choose an execution from the list above or create a new execution to get started.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Workflows Tab -->
        <div id="workflows-panel" class="synthesis__panel">
            <div class="synthesis__workflows">
                <div class="synthesis__control-bar">
                    <div class="synthesis__filter-container">
                        <div class="synthesis__input-group">
                            <span class="synthesis__input-label">Category</span>
                            <select id="workflow-category-filter" class="synthesis__select">
                                <option value="">All Categories</option>
                                <option value="data-processing">Data Processing</option>
                                <option value="system">System</option>
                                <option value="integration">Integration</option>
                                <option value="analysis">Analysis</option>
                                <option value="deployment">Deployment</option>
                            </select>
                        </div>
                        <div class="synthesis__input-group">
                            <span class="synthesis__input-label">Show</span>
                            <select id="workflow-status-filter" class="synthesis__select">
                                <option value="">All Workflows</option>
                                <option value="active">Active Only</option>
                                <option value="archived">Archived Only</option>
                            </select>
                        </div>
                    </div>
                    <div class="synthesis__actions">
                        <button id="new-workflow-btn" class="synthesis__action-button">
                            <span class="synthesis__button-icon">+</span>
                            <span class="synthesis__button-label">New Workflow</span>
                        </button>
                        <button id="import-workflow-btn" class="synthesis__action-button">
                            <span class="synthesis__button-icon">↓</span>
                            <span class="synthesis__button-label">Import</span>
                        </button>
                    </div>
                </div>
                
                <div class="synthesis__workflows-list-container">
                    <div id="workflows-list-loading" class="synthesis__loading-indicator">
                        <div class="synthesis__spinner"></div>
                        <div class="synthesis__loading-text">Loading workflows...</div>
                    </div>
                    <div id="workflows-list" class="synthesis__workflows-list" style="display: none;">
                        <table class="synthesis__table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Category</th>
                                    <th>Steps</th>
                                    <th>Last Execution</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Sample workflows for UI testing -->
                                <tr class="synthesis__workflow-row">
                                    <td>Document Processing Pipeline</td>
                                    <td>Data Processing</td>
                                    <td>11</td>
                                    <td>2025-05-14 09:45</td>
                                    <td><span class="synthesis__status synthesis__status--active">Active</span></td>
                                    <td>
                                        <button class="synthesis__table-action-btn">Edit</button>
                                        <button class="synthesis__table-action-btn">Run</button>
                                        <button class="synthesis__table-action-btn">Export</button>
                                    </td>
                                </tr>
                                <tr class="synthesis__workflow-row">
                                    <td>System Health Check</td>
                                    <td>System</td>
                                    <td>8</td>
                                    <td>2025-05-14 08:30</td>
                                    <td><span class="synthesis__status synthesis__status--active">Active</span></td>
                                    <td>
                                        <button class="synthesis__table-action-btn">Edit</button>
                                        <button class="synthesis__table-action-btn">Run</button>
                                        <button class="synthesis__table-action-btn">Export</button>
                                    </td>
                                </tr>
                                <tr class="synthesis__workflow-row">
                                    <td>Data Backup Routine</td>
                                    <td>System</td>
                                    <td>5</td>
                                    <td>2025-05-13 23:00</td>
                                    <td><span class="synthesis__status synthesis__status--active">Active</span></td>
                                    <td>
                                        <button class="synthesis__table-action-btn">Edit</button>
                                        <button class="synthesis__table-action-btn">Run</button>
                                        <button class="synthesis__table-action-btn">Export</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Monitoring Tab -->
        <div id="monitoring-panel" class="synthesis__panel">
            <div class="synthesis__monitoring">
                <div class="synthesis__control-bar">
                    <div class="synthesis__filter-container">
                        <div class="synthesis__input-group">
                            <span class="synthesis__input-label">Time Range</span>
                            <select id="monitoring-timerange" class="synthesis__select">
                                <option value="1h">Last Hour</option>
                                <option value="6h">Last 6 Hours</option>
                                <option value="24h" selected>Last 24 Hours</option>
                                <option value="7d">Last 7 Days</option>
                                <option value="30d">Last 30 Days</option>
                            </select>
                        </div>
                        <div class="synthesis__input-group">
                            <span class="synthesis__input-label">Interval</span>
                            <select id="monitoring-interval" class="synthesis__select">
                                <option value="1m">1 Minute</option>
                                <option value="5m" selected>5 Minutes</option>
                                <option value="15m">15 Minutes</option>
                                <option value="1h">1 Hour</option>
                                <option value="6h">6 Hours</option>
                                <option value="1d">1 Day</option>
                            </select>
                        </div>
                    </div>
                    <div class="synthesis__actions">
                        <button id="refresh-monitoring-btn" class="synthesis__action-button">
                            <span class="synthesis__button-label">Refresh</span>
                        </button>
                    </div>
                </div>
                
                <!-- Metrics Dashboard -->
                <div class="synthesis__dashboard">
                    <div class="synthesis__metrics-grid">
                        <div class="synthesis__metric-card">
                            <div class="synthesis__metric-value">12</div>
                            <div class="synthesis__metric-label">Active Executions</div>
                        </div>
                        <div class="synthesis__metric-card">
                            <div class="synthesis__metric-value">158</div>
                            <div class="synthesis__metric-label">Executions Today</div>
                        </div>
                        <div class="synthesis__metric-card">
                            <div class="synthesis__metric-value">94.2%</div>
                            <div class="synthesis__metric-label">Success Rate</div>
                        </div>
                        <div class="synthesis__metric-card">
                            <div class="synthesis__metric-value">4.8s</div>
                            <div class="synthesis__metric-label">Avg. Response Time</div>
                        </div>
                    </div>
                    
                    <div class="synthesis__charts-container">
                        <div class="synthesis__chart-wrapper">
                            <h3 class="synthesis__chart-title">Execution Volume</h3>
                            <div id="execution-volume-chart" class="synthesis__chart"></div>
                        </div>
                        <div class="synthesis__chart-wrapper">
                            <h3 class="synthesis__chart-title">Execution Duration</h3>
                            <div id="execution-duration-chart" class="synthesis__chart"></div>
                        </div>
                        <div class="synthesis__chart-wrapper">
                            <h3 class="synthesis__chart-title">Resource Usage</h3>
                            <div id="resource-usage-chart" class="synthesis__chart"></div>
                        </div>
                        <div class="synthesis__chart-wrapper">
                            <h3 class="synthesis__chart-title">Error Rate</h3>
                            <div id="error-rate-chart" class="synthesis__chart"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- History Tab -->
        <div id="history-panel" class="synthesis__panel">
            <div class="synthesis__history">
                <div class="synthesis__control-bar">
                    <div class="synthesis__filter-container">
                        <div class="synthesis__input-group">
                            <span class="synthesis__input-label">Status</span>
                            <select id="history-status-filter" class="synthesis__select">
                                <option value="">All Statuses</option>
                                <option value="completed">Completed</option>
                                <option value="failed">Failed</option>
                                <option value="cancelled">Cancelled</option>
                            </select>
                        </div>
                        <div class="synthesis__input-group">
                            <span class="synthesis__input-label">Workflow</span>
                            <select id="history-workflow-filter" class="synthesis__select">
                                <option value="">All Workflows</option>
                                <!-- Dynamically populated -->
                            </select>
                        </div>
                        <div class="synthesis__input-group">
                            <span class="synthesis__input-label">Date Range</span>
                            <select id="history-date-filter" class="synthesis__select">
                                <option value="today">Today</option>
                                <option value="yesterday">Yesterday</option>
                                <option value="7days" selected>Last 7 Days</option>
                                <option value="30days">Last 30 Days</option>
                                <option value="custom">Custom Range</option>
                            </select>
                        </div>
                    </div>
                    <div class="synthesis__actions">
                        <button id="export-history-btn" class="synthesis__action-button">
                            <span class="synthesis__button-label">Export</span>
                        </button>
                    </div>
                </div>
                
                <div class="synthesis__history-table-container">
                    <table class="synthesis__table synthesis__history-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Workflow</th>
                                <th>Started</th>
                                <th>Duration</th>
                                <th>Steps</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="history-table-body">
                            <!-- Sample history entries for UI testing -->
                            <tr class="synthesis__history-row">
                                <td>exec-18e7c3b2</td>
                                <td>System Health Check</td>
                                <td>2025-05-14 08:30</td>
                                <td>2m 15s</td>
                                <td>8/8</td>
                                <td><span class="synthesis__status synthesis__status--completed">Completed</span></td>
                                <td>
                                    <button class="synthesis__table-action-btn">Details</button>
                                    <button class="synthesis__table-action-btn">Rerun</button>
                                </td>
                            </tr>
                            <tr class="synthesis__history-row">
                                <td>exec-29b7d3a1</td>
                                <td>Data Backup Routine</td>
                                <td>2025-05-13 23:00</td>
                                <td>12m 08s</td>
                                <td>5/5</td>
                                <td><span class="synthesis__status synthesis__status--completed">Completed</span></td>
                                <td>
                                    <button class="synthesis__table-action-btn">Details</button>
                                    <button class="synthesis__table-action-btn">Rerun</button>
                                </td>
                            </tr>
                            <tr class="synthesis__history-row">
                                <td>exec-15f9e2c7</td>
                                <td>API Integration Test</td>
                                <td>2025-05-13 14:22</td>
                                <td>3m 45s</td>
                                <td>6/12</td>
                                <td><span class="synthesis__status synthesis__status--failed">Failed</span></td>
                                <td>
                                    <button class="synthesis__table-action-btn">Details</button>
                                    <button class="synthesis__table-action-btn">Rerun</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="synthesis__pagination">
                    <button class="synthesis__pagination-btn synthesis__pagination-btn--disabled">&lt;&lt;</button>
                    <button class="synthesis__pagination-btn synthesis__pagination-btn--active">1</button>
                    <button class="synthesis__pagination-btn">2</button>
                    <button class="synthesis__pagination-btn">3</button>
                    <span class="synthesis__pagination-ellipsis">...</span>
                    <button class="synthesis__pagination-btn">12</button>
                    <button class="synthesis__pagination-btn">&gt;&gt;</button>
                </div>
            </div>
        </div>
        
        <!-- Execution Chat Tab -->
        <div id="execchat-panel" class="synthesis__panel">
            <div id="execchat-messages" class="synthesis__chat-messages">
                <!-- Welcome message -->
                <div class="synthesis__message synthesis__message--system">
                    <div class="synthesis__message-content">
                        <div class="synthesis__message-text">
                            <h3 class="synthesis__message-title">Execution Assistant</h3>
                            <p>This chat provides assistance with execution planning and workflow management. Ask questions about:</p>
                            <ul>
                                <li>Creating and managing execution plans</li>
                                <li>Workflow optimization and debugging</li>
                                <li>Integration with external systems</li>
                                <li>Best practices for process execution</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Team Chat Tab -->
        <div id="teamchat-panel" class="synthesis__panel">
            <div id="teamchat-messages" class="synthesis__chat-messages">
                <!-- Welcome message -->
                <div class="synthesis__message synthesis__message--system">
                    <div class="synthesis__message-content">
                        <div class="synthesis__message-text">
                            <h3 class="synthesis__message-title">Tekton Team Chat</h3>
                            <p>This chat is shared across all Tekton components. Use this for team communication and coordination.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Footer with Chat Input -->
    <div class="synthesis__footer">
        <div class="synthesis__chat-input-container">
            <div class="synthesis__chat-prompt">></div>
            <input type="text" id="chat-input" class="synthesis__chat-input" 
                   placeholder="Enter chat message, execution questions, or workflow commands">
            <button id="send-button" class="synthesis__send-button">Send</button>
        </div>
    </div>
</div>
```

## CSS Styling

The CSS should follow Athena's BEM naming structure, maintaining the same visual appearance and layout but with Synthesis-specific color scheme:

```css
/* Synthesis component styles using BEM naming convention */

/* Container */
.synthesis {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    background-color: var(--bg-primary, #1e1e2e);
    color: var(--text-primary, #f0f0f0);
    /* No absolute positioning - proper component containment */
}

/* Header */
.synthesis__header {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 50px; /* Match header height from Athena */
}

.synthesis__title-container {
    display: flex;
    align-items: center;
}

.synthesis__icon {
    height: 30px;
    width: auto;
    margin-right: 12px;
}

.synthesis__title {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 500;
}

.synthesis__title-sub {
    margin-left: 8px;
    opacity: 0.8;
    font-weight: normal;
}

/* Menu Bar */
.synthesis__menu-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 16px;
    background-color: var(--bg-secondary, #252535);
    border-bottom: 1px solid var(--border-color, #444444);
    height: 46px; /* Match menu bar height from Athena */
}

.synthesis__tabs {
    display: flex;
    gap: 8px;
}

.synthesis__tab {
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

.synthesis__tab:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

.synthesis__tab--active {
    border-bottom-color: var(--color-primary, #2196F3); /* Synthesis blue color */
    font-weight: 500;
}

/* Content Area */
.synthesis__content {
    flex: 1;
    overflow: hidden;
    position: relative;
}

.synthesis__panel {
    display: none;
    height: 100%;
    width: 100%;
    overflow: auto;
    padding: 16px;
}

.synthesis__panel--active {
    display: block;
}

/* Control Bar */
.synthesis__control-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 16px;
    padding: 10px;
    background-color: var(--bg-secondary, #252535);
    border-radius: 4px;
}

.synthesis__search-container {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    min-width: 200px;
}

.synthesis__search-input {
    flex: 1;
    min-width: 200px;
    padding: 6px 12px;
    background-color: var(--bg-element, #2a2a3a);
    border: 1px solid var(--border-color, #444444);
    border-radius: 4px;
    color: var(--text-primary, #f0f0f0);
}

.synthesis__search-button {
    padding: 6px 12px;
    background-color: var(--bg-tertiary, #333345);
    border: 1px solid var(--border-color, #444444);
    border-radius: 4px;
    color: var(--text-primary, #f0f0f0);
    cursor: pointer;
}

.synthesis__filter-container {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.synthesis__input-group {
    display: flex;
    align-items: center;
    gap: 6px;
}

.synthesis__input-label {
    font-size: 0.9rem;
    white-space: nowrap;
}

.synthesis__select {
    padding: 6px 10px;
    background-color: var(--bg-element, #2a2a3a);
    border: 1px solid var(--border-color, #444444);
    border-radius: 4px;
    color: var(--text-primary, #f0f0f0);
}

.synthesis__actions {
    display: flex;
    gap: 8px;
    margin-left: auto;
}

/* Execution List */
.synthesis__executions-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
}

.synthesis__execution-item {
    padding: 12px;
    background-color: var(--bg-secondary, #252535);
    border-radius: 4px;
    border-left: 4px solid transparent;
}

.synthesis__execution-item--running {
    border-left-color: var(--status-running, #2196F3);
}

.synthesis__execution-item--completed {
    border-left-color: var(--status-success, #4CAF50);
}

.synthesis__execution-item--failed {
    border-left-color: var(--status-error, #F44336);
}

.synthesis__execution-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.synthesis__execution-title {
    font-weight: 500;
    font-size: 1rem;
}

.synthesis__execution-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.9rem;
}

.synthesis__execution-id {
    opacity: 0.7;
    font-family: monospace;
}

.synthesis__execution-status {
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 0.85rem;
}

.synthesis__execution-status--running {
    background-color: var(--status-running, #2196F3);
    color: white;
}

.synthesis__execution-status--completed {
    background-color: var(--status-success, #4CAF50);
    color: white;
}

.synthesis__execution-status--failed {
    background-color: var(--status-error, #F44336);
    color: white;
}

.synthesis__execution-progress {
    margin-bottom: 10px;
}

.synthesis__progress-bar {
    height: 8px;
    background-color: var(--bg-element, #2a2a3a);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 5px;
}

.synthesis__progress-fill {
    height: 100%;
    background-color: var(--color-primary, #2196F3);
    border-radius: 4px;
}

.synthesis__progress-text {
    font-size: 0.8rem;
    opacity: 0.8;
    text-align: right;
}

.synthesis__execution-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
}

/* Empty State */
.synthesis__empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    text-align: center;
    background-color: var(--bg-secondary, #252535);
    border-radius: 4px;
    height: 300px;
}

.synthesis__empty-state-title {
    margin-top: 0;
    margin-bottom: 10px;
    font-size: 1.1rem;
    font-weight: 500;
}

.synthesis__empty-state-text {
    margin: 0;
    opacity: 0.8;
}

/* Table Styles */
.synthesis__table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
}

.synthesis__table th,
.synthesis__table td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid var(--border-color, #444444);
}

.synthesis__table th {
    font-weight: 500;
    background-color: var(--bg-tertiary, #333345);
}

.synthesis__workflow-row:hover,
.synthesis__history-row:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

/* Status Indicators */
.synthesis__status {
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 0.8rem;
    display: inline-block;
}

.synthesis__status--active { background-color: #2196F3; color: white; }
.synthesis__status--inactive { background-color: #9E9E9E; color: white; }
.synthesis__status--completed { background-color: #4CAF50; color: white; }
.synthesis__status--failed { background-color: #F44336; color: white; }
.synthesis__status--cancelled { background-color: #FFC107; color: black; }

/* Dashboard Cards */
.synthesis__metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.synthesis__metric-card {
    padding: 16px;
    background-color: var(--bg-secondary, #252535);
    border-radius: 4px;
    text-align: center;
}

.synthesis__metric-value {
    font-size: 2rem;
    font-weight: 500;
    margin-bottom: 6px;
    color: var(--color-primary, #2196F3);
}

.synthesis__metric-label {
    font-size: 0.9rem;
    opacity: 0.8;
}

/* Charts */
.synthesis__charts-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
}

.synthesis__chart-wrapper {
    background-color: var(--bg-secondary, #252535);
    border-radius: 4px;
    padding: 16px;
}

.synthesis__chart-title {
    margin-top: 0;
    margin-bottom: 16px;
    font-size: 1rem;
    font-weight: 500;
}

.synthesis__chart {
    height: 200px;
    width: 100%;
    background-color: var(--bg-element, #2a2a3a);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Buttons */
.synthesis__action-button {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background-color: var(--bg-tertiary, #333345);
    border: 1px solid var(--border-color, #444444);
    border-radius: 4px;
    color: var(--text-primary, #f0f0f0);
    cursor: pointer;
}

.synthesis__action-button:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

.synthesis__button {
    padding: 6px 12px;
    background-color: var(--bg-tertiary, #333345);
    border: 1px solid var(--border-color, #444444);
    border-radius: 4px;
    color: var(--text-primary, #f0f0f0);
    cursor: pointer;
}

.synthesis__button:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

.synthesis__button--small {
    padding: 3px 8px;
    font-size: 0.8rem;
}

.synthesis__button--primary {
    background-color: var(--color-primary, #2196F3);
    border-color: var(--color-primary, #2196F3);
    color: white;
}

.synthesis__table-action-btn {
    padding: 3px 8px;
    background-color: var(--bg-tertiary, #333345);
    border: 1px solid var(--border-color, #444444);
    border-radius: 3px;
    color: var(--text-primary, #f0f0f0);
    font-size: 0.8rem;
    cursor: pointer;
    margin-right: 4px;
}

.synthesis__table-action-btn:hover {
    background-color: var(--bg-hover, #3a3a4a);
}

/* Pagination */
.synthesis__pagination {
    display: flex;
    justify-content: center;
    gap: 4px;
    margin-top: 16px;
}

.synthesis__pagination-btn {
    padding: 6px 10px;
    background-color: var(--bg-tertiary, #333345);
    border: 1px solid var(--border-color, #444444);
    border-radius: 3px;
    color: var(--text-primary, #f0f0f0);
    cursor: pointer;
}

.synthesis__pagination-btn--active {
    background-color: var(--color-primary, #2196F3);
    border-color: var(--color-primary, #2196F3);
    color: white;
}

.synthesis__pagination-btn--disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.synthesis__pagination-ellipsis {
    padding: 6px 4px;
    opacity: 0.7;
}

/* Loading Indicator */
.synthesis__loading-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 0;
}

.synthesis__spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(33, 150, 243, 0.1);
    border-top-color: var(--color-primary, #2196F3);
    border-radius: 50%;
    animation: synthesis-spin 1s linear infinite;
}

@keyframes synthesis-spin {
    to { transform: rotate(360deg); }
}

.synthesis__loading-text {
    margin-top: 12px;
    font-size: 0.9rem;
    color: var(--text-secondary, #aaaaaa);
}

/* Chat Areas */
.synthesis__chat-messages {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 16px;
    height: calc(100% - 32px);
    overflow-y: auto;
}

.synthesis__message {
    max-width: 80%;
}

.synthesis__message--user {
    align-self: flex-end;
}

.synthesis__message--system {
    align-self: center;
    max-width: 600px;
}

.synthesis__message-content {
    padding: 12px;
    background-color: var(--bg-secondary, #252535);
    border-radius: 12px;
}

.synthesis__message--user .synthesis__message-content {
    background-color: var(--color-primary-dark, #1976D2);
    color: white;
    border-radius: 12px 12px 0 12px;
}

.synthesis__message--system .synthesis__message-content {
    background-color: var(--bg-tertiary, #333345);
    border-left: 3px solid var(--color-primary, #2196F3);
    border-radius: 4px;
}

.synthesis__message-title {
    margin-top: 0;
    margin-bottom: 10px;
    font-size: 1rem;
    font-weight: 500;
}

.synthesis__message-text {
    line-height: 1.4;
}

.synthesis__message-text ul {
    margin-top: 6px;
    margin-bottom: 6px;
    padding-left: 20px;
}

/* Footer */
.synthesis__footer {
    padding: 12px 16px;
    background-color: var(--bg-secondary, #252535);
    border-top: 1px solid var(--border-color, #444444);
    height: 70px; /* Match footer height from Athena */
}

.synthesis__chat-input-container {
    display: flex;
    align-items: center;
    gap: 8px;
}

.synthesis__chat-prompt {
    font-family: monospace;
    font-size: 1.2rem;
    color: var(--color-primary, #2196F3);
}

.synthesis__chat-input {
    flex: 1;
    padding: 10px 12px;
    background-color: var(--bg-element, #2a2a3a);
    border: 1px solid var(--border-color, #444444);
    border-radius: 4px;
    color: var(--text-primary, #f0f0f0);
}

.synthesis__chat-input:focus {
    outline: none;
    border-color: var(--color-primary, #2196F3);
}

.synthesis__send-button {
    padding: 10px 16px;
    background-color: var(--color-primary, #2196F3);
    border: none;
    border-radius: 4px;
    color: white;
    cursor: pointer;
    transition: background-color 0.2s;
}

.synthesis__send-button:hover {
    background-color: var(--color-primary-dark, #1976D2);
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
    window.uiManager._ignoreComponent = 'synthesis';
    console.log('[SYNTHESIS] Set UI Manager to ignore synthesis component');
}

// DEFINE TAB SWITCHING FUNCTION
// CRITICAL: This uses no shared code/utilities to avoid conflicts
window.synthesis_switchTab = function(tabId) {
    console.log('[SYNTHESIS] Switching to tab:', tabId);
    
    // Force HTML panel visibility
    const htmlPanelElements = document.querySelectorAll('#html-panel');
    htmlPanelElements.forEach(panel => {
        if (panel) panel.style.display = 'block';
    });
    
    try {
        // Only select elements within synthesis component to avoid conflicts with other components
        const synthesisContainer = document.querySelector('.synthesis');
        if (!synthesisContainer) {
            console.error('[SYNTHESIS] Tab Switch: Cannot find synthesis container');
            return false;
        }
        
        // Update tab active state - ONLY WITHIN SYNTHESIS CONTAINER
        const tabs = synthesisContainer.querySelectorAll('.synthesis__tab');
        tabs.forEach(tab => {
            if (tab.getAttribute('data-tab') === tabId) {
                tab.classList.add('synthesis__tab--active');
            } else {
                tab.classList.remove('synthesis__tab--active');
            }
        });
        
        // Update panel visibility - ONLY WITHIN SYNTHESIS CONTAINER
        const panels = synthesisContainer.querySelectorAll('.synthesis__panel');
        panels.forEach(panel => {
            const panelId = panel.id;
            if (panelId === tabId + '-panel') {
                panel.style.display = 'block';
                panel.classList.add('synthesis__panel--active');
            } else {
                panel.style.display = 'none';
                panel.classList.remove('synthesis__panel--active');
            }
        });
        
        // Update clear button visibility for chat tabs
        const clearButton = synthesisContainer.querySelector('#clear-chat-btn');
        if (clearButton) {
            clearButton.style.display = (tabId === 'execchat' || tabId === 'teamchat') ? 'block' : 'none';
        }
        
        // Update component state
        if (window.synthesisComponent) {
            window.synthesisComponent.state = window.synthesisComponent.state || {};
            window.synthesisComponent.state.activeTab = tabId;
            
            // Call component-specific methods if available
            if (typeof window.synthesisComponent.updateChatPlaceholder === 'function') {
                window.synthesisComponent.updateChatPlaceholder(tabId);
            }
            
            if (typeof window.synthesisComponent.loadTabContent === 'function') {
                window.synthesisComponent.loadTabContent(tabId);
            }
            
            if (typeof window.synthesisComponent.saveComponentState === 'function') {
                window.synthesisComponent.saveComponentState();
            }
        }
    } catch (err) {
        console.error('[SYNTHESIS] Error in tab switching:', err);
    }
    
    return false; // Stop event propagation
};

// CHAT CLEARING FUNCTION
window.synthesis_clearChat = function() {
    console.log('[SYNTHESIS] Clearing chat messages');
    
    try {
        const synthesisContainer = document.querySelector('.synthesis');
        if (!synthesisContainer) {
            console.error('[SYNTHESIS] Clear Chat: Cannot find synthesis container');
            return false;
        }
        
        // Determine which chat to clear based on active tab
        const activeTab = synthesisContainer.querySelector('.synthesis__tab--active');
        if (!activeTab) {
            console.error('[SYNTHESIS] Clear Chat: Cannot determine active tab');
            return false;
        }
        
        const chatType = activeTab.getAttribute('data-tab');
        let chatContainer;
        
        if (chatType === 'execchat') {
            chatContainer = synthesisContainer.querySelector('#execchat-messages');
        } else if (chatType === 'teamchat') {
            chatContainer = synthesisContainer.querySelector('#teamchat-messages');
        }
        
        if (!chatContainer) {
            console.error('[SYNTHESIS] Clear Chat: Cannot find chat container for', chatType);
            return false;
        }
        
        // Keep only the system welcome message
        const welcomeMessage = chatContainer.querySelector('.synthesis__message--system');
        if (welcomeMessage) {
            chatContainer.innerHTML = '';
            chatContainer.appendChild(welcomeMessage);
        } else {
            chatContainer.innerHTML = '';
        }
        
        console.log('[SYNTHESIS] Chat messages cleared for', chatType);
    } catch (err) {
        console.error('[SYNTHESIS] Error in clearing chat:', err);
    }
    
    return false; // Stop event propagation
};
```

## Isolated Component JavaScript

Create a separate file `synthesis-component.js` that follows the same structure as Athena's component JS:

```javascript
/**
 * Synthesis Execution Engine Component
 * 
 * Provides interfaces for workflow execution, monitoring, and management.
 */

class SynthesisComponent {
    constructor() {
        // Initialize properties
        this.state = {
            activeTab: 'executions',
            executions: [],
            workflows: [],
            loading: {
                executions: false,
                workflows: false,
                monitoring: false,
                history: false
            }
        };
        
        // Initialize services
        this.executionService = new ExecutionEngine();
        this.workflowService = new WorkflowManager();
        
        // Debug output
        console.log('[SYNTHESIS] Component constructed');
    }
    
    async init() {
        console.log('[SYNTHESIS] Initializing component');
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial data
        this.loadExecutions();
        
        // Save state to local storage
        this.saveComponentState();
    }
    
    setupEventListeners() {
        try {
            // Get container to scope DOM queries
            const synthesisContainer = document.querySelector('.synthesis');
            if (!synthesisContainer) {
                console.error('[SYNTHESIS] Could not find synthesis container');
                return;
            }
            
            // Set up chat input for Enter key
            const chatInput = synthesisContainer.querySelector('#chat-input');
            if (chatInput) {
                chatInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        this.handleChatSend();
                    }
                });
            }
            
            // Set up send button for chat
            const sendButton = synthesisContainer.querySelector('#send-button');
            if (sendButton) {
                sendButton.addEventListener('click', () => this.handleChatSend());
            }
            
            // Set up refresh executions button
            const refreshButton = synthesisContainer.querySelector('#refresh-executions-btn');
            if (refreshButton) {
                refreshButton.addEventListener('click', () => this.refreshExecutions());
            }
            
            // Set up refresh monitoring button
            const refreshMonitoringBtn = synthesisContainer.querySelector('#refresh-monitoring-btn');
            if (refreshMonitoringBtn) {
                refreshMonitoringBtn.addEventListener('click', () => this.refreshMonitoring());
            }
            
            // Set up new execution button
            const newExecutionBtn = synthesisContainer.querySelector('#new-execution-btn');
            if (newExecutionBtn) {
                newExecutionBtn.addEventListener('click', () => this.showNewExecutionModal());
            }
            
            // Set up new workflow button
            const newWorkflowBtn = synthesisContainer.querySelector('#new-workflow-btn');
            if (newWorkflowBtn) {
                newWorkflowBtn.addEventListener('click', () => this.showNewWorkflowModal());
            }
            
            // Set up import workflow button
            const importWorkflowBtn = synthesisContainer.querySelector('#import-workflow-btn');
            if (importWorkflowBtn) {
                importWorkflowBtn.addEventListener('click', () => this.showImportWorkflowModal());
            }
            
            // Set up export history button
            const exportHistoryBtn = synthesisContainer.querySelector('#export-history-btn');
            if (exportHistoryBtn) {
                exportHistoryBtn.addEventListener('click', () => this.exportExecutionHistory());
            }
            
            console.log('[SYNTHESIS] Event listeners set up');
        } catch (error) {
            console.error('[SYNTHESIS] Error setting up event listeners:', error);
        }
    }
    
    async loadExecutions() {
        try {
            console.log('[SYNTHESIS] Loading executions');
            this.state.loading.executions = true;
            
            // Update UI to show loading state
            this.toggleLoadingState('executions-list', true);
            
            // In a real implementation, this would call the actual API
            // For now, simulate an API call with a timeout
            setTimeout(() => {
                // Sample data - would come from the API in real implementation
                this.state.executions = [
                    {
                        id: 'exec-23a5f9d7',
                        name: 'Document Processing Pipeline',
                        status: 'running',
                        currentStep: 5,
                        totalSteps: 11,
                        progress: 45,
                        startTime: new Date()
                    },
                    {
                        id: 'exec-18e7c3b2',
                        name: 'System Health Check',
                        status: 'completed',
                        currentStep: 8,
                        totalSteps: 8,
                        progress: 100,
                        startTime: new Date(Date.now() - 3600000),
                        endTime: new Date(Date.now() - 3465000)
                    }
                ];
                
                // Render executions to UI
                this.renderExecutions();
                
                // Update UI to hide loading state
                this.toggleLoadingState('executions-list', false);
                this.state.loading.executions = false;
            }, 800);
        } catch (error) {
            console.error('[SYNTHESIS] Error loading executions:', error);
            this.state.loading.executions = false;
            this.toggleLoadingState('executions-list', false);
        }
    }
    
    renderExecutions() {
        try {
            const synthesisContainer = document.querySelector('.synthesis');
            if (!synthesisContainer) return;
            
            const executionsList = synthesisContainer.querySelector('#executions-list');
            if (!executionsList) return;
            
            // In a real implementation, this would generate HTML for each execution
            // For now, we'll just log that rendering would happen
            console.log('[SYNTHESIS] Rendering executions:', this.state.executions.length);
            
            // Show the executions list
            executionsList.style.display = 'flex';
        } catch (error) {
            console.error('[SYNTHESIS] Error rendering executions:', error);
        }
    }
    
    toggleLoadingState(elementId, isLoading) {
        try {
            const synthesisContainer = document.querySelector('.synthesis');
            if (!synthesisContainer) return;
            
            const loadingElement = synthesisContainer.querySelector(`#${elementId}-loading`);
            const contentElement = synthesisContainer.querySelector(`#${elementId}`);
            
            if (loadingElement && contentElement) {
                if (isLoading) {
                    loadingElement.style.display = 'flex';
                    contentElement.style.display = 'none';
                } else {
                    loadingElement.style.display = 'none';
                    contentElement.style.display = '';
                }
            }
        } catch (error) {
            console.error('[SYNTHESIS] Error toggling loading state:', error);
        }
    }
    
    refreshExecutions() {
        console.log('[SYNTHESIS] Refreshing executions');
        this.loadExecutions();
    }
    
    async loadTabContent(tabId) {
        console.log('[SYNTHESIS] Loading tab content for:', tabId);
        
        // Load data for specific tabs when they are activated
        if (tabId === 'executions' && this.state.executions.length === 0) {
            this.loadExecutions();
        } else if (tabId === 'workflows' && this.state.workflows.length === 0) {
            this.loadWorkflows();
        } else if (tabId === 'monitoring') {
            this.loadMonitoringData();
        } else if (tabId === 'history') {
            this.loadExecutionHistory();
        }
    }
    
    async loadWorkflows() {
        try {
            console.log('[SYNTHESIS] Loading workflows');
            this.state.loading.workflows = true;
            
            // Update UI to show loading state
            this.toggleLoadingState('workflows-list', true);
            
            // In a real implementation, this would call the actual API
            // For now, simulate an API call with a timeout
            setTimeout(() => {
                // Sample data - would come from the API in real implementation
                this.state.workflows = [
                    {
                        id: 'wf-001',
                        name: 'Document Processing Pipeline',
                        category: 'Data Processing',
                        steps: 11,
                        lastExecution: new Date(),
                        status: 'active'
                    },
                    {
                        id: 'wf-002',
                        name: 'System Health Check',
                        category: 'System',
                        steps: 8,
                        lastExecution: new Date(Date.now() - 3600000),
                        status: 'active'
                    },
                    {
                        id: 'wf-003',
                        name: 'Data Backup Routine',
                        category: 'System',
                        steps: 5,
                        lastExecution: new Date(Date.now() - 86400000),
                        status: 'active'
                    }
                ];
                
                // Render workflows to UI
                this.renderWorkflows();
                
                // Update UI to hide loading state
                this.toggleLoadingState('workflows-list', false);
                this.state.loading.workflows = false;
            }, 800);
        } catch (error) {
            console.error('[SYNTHESIS] Error loading workflows:', error);
            this.state.loading.workflows = false;
            this.toggleLoadingState('workflows-list', false);
        }
    }
    
    renderWorkflows() {
        try {
            const synthesisContainer = document.querySelector('.synthesis');
            if (!synthesisContainer) return;
            
            const workflowsList = synthesisContainer.querySelector('#workflows-list');
            if (!workflowsList) return;
            
            // In a real implementation, this would generate HTML for each workflow
            // For now, we'll just log that rendering would happen
            console.log('[SYNTHESIS] Rendering workflows:', this.state.workflows.length);
            
            // Show the workflows list
            workflowsList.style.display = 'block';
        } catch (error) {
            console.error('[SYNTHESIS] Error rendering workflows:', error);
        }
    }
    
    async loadMonitoringData() {
        try {
            console.log('[SYNTHESIS] Loading monitoring data');
            this.state.loading.monitoring = true;
            
            // In a real implementation, this would call the actual API
            // For now, simulate an API call with a timeout
            setTimeout(() => {
                // Render charts for monitoring dashboard
                this.renderMonitoringCharts();
                this.state.loading.monitoring = false;
            }, 800);
        } catch (error) {
            console.error('[SYNTHESIS] Error loading monitoring data:', error);
            this.state.loading.monitoring = false;
        }
    }
    
    renderMonitoringCharts() {
        console.log('[SYNTHESIS] Rendering monitoring charts');
        // In a real implementation, this would use a charting library to render charts
    }
    
    refreshMonitoring() {
        console.log('[SYNTHESIS] Refreshing monitoring data');
        this.loadMonitoringData();
    }
    
    async loadExecutionHistory() {
        try {
            console.log('[SYNTHESIS] Loading execution history');
            this.state.loading.history = true;
            
            // In a real implementation, this would call the actual API
            // For now, we'll just log that data would be loaded
            console.log('[SYNTHESIS] Would load execution history from API');
            this.state.loading.history = false;
        } catch (error) {
            console.error('[SYNTHESIS] Error loading execution history:', error);
            this.state.loading.history = false;
        }
    }
    
    exportExecutionHistory() {
        console.log('[SYNTHESIS] Exporting execution history');
        // In a real implementation, this would generate a CSV or JSON file
    }
    
    // Modal Methods
    
    showNewExecutionModal() {
        console.log('[SYNTHESIS] Showing new execution modal');
        // In a real implementation, this would show a modal for creating a new execution
    }
    
    showNewWorkflowModal() {
        console.log('[SYNTHESIS] Showing new workflow modal');
        // In a real implementation, this would show a modal for creating a new workflow
    }
    
    showImportWorkflowModal() {
        console.log('[SYNTHESIS] Showing import workflow modal');
        // In a real implementation, this would show a modal for importing a workflow
    }
    
    // Chat Functionality
    
    updateChatPlaceholder(tabId) {
        try {
            const synthesisContainer = document.querySelector('.synthesis');
            if (!synthesisContainer) return;
            
            const chatInput = synthesisContainer.querySelector('#chat-input');
            if (!chatInput) return;
            
            if (tabId === 'execchat') {
                chatInput.placeholder = 'Ask about executions, workflows, or integration...';
            } else if (tabId === 'teamchat') {
                chatInput.placeholder = 'Enter team chat message...';
            } else {
                chatInput.placeholder = 'Enter chat message, execution questions, or workflow commands';
            }
        } catch (error) {
            console.error('[SYNTHESIS] Error updating chat placeholder:', error);
        }
    }
    
    handleChatSend() {
        try {
            const synthesisContainer = document.querySelector('.synthesis');
            if (!synthesisContainer) return;
            
            const chatInput = synthesisContainer.querySelector('#chat-input');
            if (!chatInput || !chatInput.value.trim()) return;
            
            const message = chatInput.value.trim();
            chatInput.value = '';
            
            // Determine active chat tab
            const activeTab = this.state.activeTab;
            if (activeTab !== 'execchat' && activeTab !== 'teamchat') {
                console.error('[SYNTHESIS] Cannot send message: no chat tab active');
                return;
            }
            
            this.addChatMessage(message, activeTab, 'user');
            
            // Simulate response for demo
            setTimeout(() => {
                let responseText;
                if (activeTab === 'execchat') {
                    if (message.toLowerCase().includes('workflow')) {
                        responseText = `I can help with workflows. To create a new workflow, click the "New Workflow" button in the Workflows tab. You can also define steps, conditions, and integrations for your workflow.`;
                    } else if (message.toLowerCase().includes('execution')) {
                        responseText = `Executions represent instances of workflows being run. You can monitor active executions in the Executions tab, and view historical executions in the History tab.`;
                    } else {
                        responseText = `To work with the execution engine, you can create workflows with multiple steps, execute them, and monitor their progress. What specific aspect would you like to know more about?`;
                    }
                } else { // teamchat
                    responseText = `Team member response to your message: "${message}"`;
                }
                
                this.addChatMessage(responseText, activeTab, 'assistant');
            }, 1000);
        } catch (error) {
            console.error('[SYNTHESIS] Error handling chat send:', error);
        }
    }
    
    addChatMessage(text, tabId, sender) {
        try {
            const synthesisContainer = document.querySelector('.synthesis');
            if (!synthesisContainer) return;
            
            const messagesContainer = synthesisContainer.querySelector(`#${tabId}-messages`);
            if (!messagesContainer) return;
            
            // Create message element
            const messageDiv = document.createElement('div');
            messageDiv.className = `synthesis__message synthesis__message--${sender}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'synthesis__message-content';
            
            const textDiv = document.createElement('div');
            textDiv.className = 'synthesis__message-text';
            textDiv.textContent = text;
            
            contentDiv.appendChild(textDiv);
            messageDiv.appendChild(contentDiv);
            messagesContainer.appendChild(messageDiv);
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        } catch (error) {
            console.error('[SYNTHESIS] Error adding chat message:', error);
        }
    }
    
    // State Management
    
    saveComponentState() {
        try {
            // Save component state to localStorage
            const stateToSave = {
                activeTab: this.state.activeTab
            };
            
            localStorage.setItem('synthesis_component_state', JSON.stringify(stateToSave));
            console.log('[SYNTHESIS] Component state saved');
        } catch (error) {
            console.error('[SYNTHESIS] Error saving component state:', error);
        }
    }
    
    loadComponentState() {
        try {
            // Load component state from localStorage
            const savedState = localStorage.getItem('synthesis_component_state');
            if (!savedState) return;
            
            const parsedState = JSON.parse(savedState);
            
            // Restore tab if needed
            if (parsedState.activeTab && parsedState.activeTab !== 'executions') {
                this.state.activeTab = parsedState.activeTab;
                window.synthesis_switchTab(parsedState.activeTab);
            }
            
            console.log('[SYNTHESIS] Component state loaded');
        } catch (error) {
            console.error('[SYNTHESIS] Error loading component state:', error);
        }
    }
}

// Initialize and export the component
window.synthesisComponent = new SynthesisComponent();
document.addEventListener('DOMContentLoaded', () => {
    window.synthesisComponent.init();
    window.synthesisComponent.loadComponentState();
});

// Export for module usage
export { SynthesisComponent };
```

## Service JavaScript Files

Create the necessary service files that follow the pattern from Athena:

1. **synthesis-service.js**: For API communication with the Synthesis backend
2. **execution-engine.js**: For execution management and monitoring
3. **workflow-manager.js**: For workflow creation and management

## Implementation Checklist

1. **Component Structure**
   - [ ] Implement basic HTML structure following Athena pattern
   - [ ] Add tab navigation with 6 tabs (Executions, Workflows, Monitoring, History, Execution Chat, Team Chat)
   - [ ] Implement panel structure for each tab

2. **Styling**
   - [ ] Implement CSS with BEM naming (synthesis__*)
   - [ ] Maintain visual consistency with Athena, with Synthesis-specific colors
   - [ ] Ensure all height/spacing matches Athena component

3. **JavaScript**
   - [ ] Implement UI Manager protection
   - [ ] Implement HTML Panel protection
   - [ ] Implement tab switching functionality
   - [ ] Implement chat functionality
   - [ ] Add loading/error handling

4. **Debug Instrumentation**
   - [ ] Add comprehensive logging with [SYNTHESIS] prefix
   - [ ] Add error handling and user feedback
   - [ ] Ensure proper debugging messages

## Synthesis-Specific Features

1. **Executions Panel**: List of active and recent executions with status
2. **Workflows Panel**: Workflow management and editing
3. **Monitoring Panel**: Performance and resource metrics dashboard
4. **History Panel**: Historical execution records and analysis
5. **Execution Chat**: Execution and workflow assistance
6. **Team Chat**: Standard team chat functionality

## Important Notes

1. **Use Athena as Reference**: Always refer to Athena component for patterns and structure
2. **Component Isolation**: Ensure all DOM queries are scoped to the synthesis container
3. **Consistent Naming**: Use 'synthesis__' prefix for all BEM class names
4. **Error Handling**: Implement robust error handling
5. **Debug Messages**: Use '[SYNTHESIS]' prefix for all console logs

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
2. Connect to Synthesis API endpoints
3. Implement execution visualization
4. Add workflow editing functionality
5. Integrate with the shared team chat system

## Critical Implementation Requirements

**IMPORTANT**: This implementation guide MUST be followed exactly without any deviations. If any changes are proposed, they MUST be discussed with Casey (human-in-the-loop) first before implementation. No architectural changes, altered patterns, or extra features are allowed without explicit approval.