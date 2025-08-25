# Hephaestus UI Implementation Guide

**⚠️ UPDATE (June 2025)**: The UI architecture has evolved. While the component structure patterns below remain valid, the loading mechanism has changed. Components are now loaded dynamically via `minimal-loader.js`. See the [CSS-First Architecture Documentation](/MetaData/TektonDocumentation/Architecture/CSSFirstArchitecture.md) for current implementation details.

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Component Structure](#component-structure)
4. [Implementation Process](#implementation-process)
5. [File Organization](#file-organization)
6. [Standardized Patterns](#standardized-patterns)
7. [Debugging and Testing](#debugging-and-testing)
8. [Best Practices](#best-practices)

## Overview

This document provides guidance on implementing UI components for the Hephaestus interface using the simplified approach. Hephaestus serves as a lightweight UI container for Tekton components, providing a consistent user experience while allowing each component to maintain its specialized functionality.

## Architecture

### Key Principles

1. **Simplicity**: The UI follows a "Keep It Simple" philosophy with minimal complexity.
2. **Consistency**: All components follow the same structural pattern.
3. **Separation**: Clear separation between the left navigation panel and right content panel.
4. **Lightweight**: Hephaestus is a UI container only, with no direct LLM dependencies.
5. **Integration**: Components connect to Tekton ecosystem via Hermes for services.

### System Structure

Hephaestus consists of two primary UI regions:

1. **Left Panel**: Navigation between components
   - Component selection
   - Status indicators
   - Footer controls (Settings, Profile, etc.)
   
2. **Right Panel**: Component-specific interface with standardized structure
   - HEADER: Component identification
   - MENU BAR: Component-specific tabs and controls
   - WORKSPACE: Main content area
   - CHAT-INPUT-AREA: (Optional) For LLM interfaces

## Component Structure

Every Tekton component's UI follows this structure:

### 1. HEADER
```html
<div class="component-header">
  <h1 class="component-title">Component Name</h1>
  <div class="component-actions">
    <!-- Optional component-level actions -->
  </div>
</div>
```

### 2. MENU BAR
```html
<div class="component-menu-bar">
  <div class="tab-buttons">
    <button class="tab-button active" data-tab="tab1">Tab 1</button>
    <button class="tab-button" data-tab="tab2">Tab 2</button>
    <!-- Additional tabs as needed -->
  </div>
  <div class="menu-actions">
    <!-- Optional action buttons -->
    <button class="action-button" id="action1">Action</button>
  </div>
</div>
```

### 3. WORKSPACE
```html
<div class="component-workspace">
  <div class="tab-content active" id="tab1-content">
    <!-- Tab 1 content -->
  </div>
  <div class="tab-content" id="tab2-content">
    <!-- Tab 2 content -->
  </div>
  <!-- Additional tab content as needed -->
</div>
```

### 4. CHAT-INPUT-AREA (Only for LLM components)
```html
<div class="chat-input-area">
  <textarea class="chat-input" placeholder="Type your message..."></textarea>
  <button class="send-button">Send</button>
</div>
```

## Implementation Process

### Step 1: Component Analysis
1. Identify core functionality
2. Determine required tabs
3. Define data needs and interactions
4. Plan backend communication

### Step 2: Create Component Directory Structure
```
ui/scripts/component-name/
├── html/
│   ├── main.html
│   ├── tab1.html
│   ├── tab2.html
├── css/
│   ├── main.css
│   ├── tab1.css
│   ├── tab2.css
├── js/
│   ├── loader.js
│   ├── events.js
│   ├── api.js
```

### Step 3: Implement Component Loader
```javascript
// File: component-name/js/loader.js

function loadComponent() {
  // Get and prepare HTML panel
  const htmlPanel = document.getElementById('html-panel');
  htmlPanel.innerHTML = '';
  
  // Set active component
  window.activeComponent = 'component-name';
  
  // Create component structure
  const componentHTML = `
    <!-- HEADER -->
    <div class="component-header">...</div>
    
    <!-- MENU BAR -->
    <div class="component-menu-bar">...</div>
    
    <!-- WORKSPACE -->
    <div class="component-workspace">...</div>
    
    <!-- CHAT-INPUT-AREA (if needed) -->
    <div class="chat-input-area">...</div>
  `;
  
  // Add to panel
  htmlPanel.innerHTML = componentHTML;
  
  // Setup events
  setupComponentEvents();
  
  // Load default tab
  loadComponentTab('default-tab');
}
```

### Step 4: Implement Tab Functionality
```javascript
// File: component-name/js/events.js

function setupComponentEvents() {
  // Setup tab switching
  const tabButtons = document.querySelectorAll('.tab-button');
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      // Update active tab button
      tabButtons.forEach(b => b.classList.remove('active'));
      button.classList.add('active');
      
      // Load tab content
      const tabId = button.dataset.tab;
      loadComponentTab(tabId);
    });
  });
  
  // Setup other event handlers
  setupActionButtonHandlers();
  setupFormHandlers();
  // etc.
}

function loadComponentTab(tabId) {
  // Hide all tab content
  const tabContents = document.querySelectorAll('.tab-content');
  tabContents.forEach(content => content.classList.remove('active'));
  
  // Show selected tab content
  const selectedContent = document.getElementById(`${tabId}-content`);
  if (selectedContent) {
    selectedContent.classList.add('active');
  }
  
  // Load any dynamic content for this tab
  loadTabData(tabId);
}
```

### Step 5: Implement Backend Communication
```javascript
// File: component-name/js/api.js

async function fetchComponentData() {
  try {
    const response = await fetch('/api/component-name/data');
    if (!response.ok) {
      throw new Error('Failed to fetch data');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching component data:', error);
    showError('Failed to load component data. Please try again.');
    return null;
  }
}

function setupHermesConnection() {
  // Connect to Hermes for component-specific services
  if (window.hermesConnector) {
    hermesConnector.registerComponent('component-name', {
      onMessage: handleHermesMessage,
      capabilities: ['capability1', 'capability2']
    });
  }
}

function handleHermesMessage(message) {
  // Process messages from Hermes
  const { type, payload } = message;
  
  switch (type) {
    case 'DATA_UPDATE':
      updateComponentData(payload);
      break;
    case 'STATUS_CHANGE':
      updateComponentStatus(payload);
      break;
    // Handle other message types
  }
}
```

## File Organization

### Component Manifest
Each component should include a manifest file that lists all required files:

```javascript
// File: component-name/manifest.js

export const componentFiles = {
  js: [
    'component-name/js/loader.js',
    'component-name/js/events.js',
    'component-name/js/api.js'
  ],
  css: [
    'component-name/css/main.css',
    'component-name/css/tab1.css',
    'component-name/css/tab2.css'
  ],
  html: [
    'component-name/html/main.html',
    'component-name/html/tab1.html',
    'component-name/html/tab2.html'
  ]
};
```

### File Size Management
When a file exceeds 600 lines:
1. Identify logical separation points
2. Split into multiple focused files
3. Update component manifest
4. Ensure proper loading order

## Standardized Patterns

### Tab Navigation
```javascript
function setupTabNavigation(componentId) {
  const tabButtons = document.querySelectorAll(`#${componentId}-tabs .tab-button`);
  const tabContents = document.querySelectorAll(`#${componentId}-workspace .tab-content`);
  
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const tabId = button.dataset.tab;
      
      // Update active button
      tabButtons.forEach(b => b.classList.remove('active'));
      button.classList.add('active');
      
      // Update active content
      tabContents.forEach(content => content.classList.remove('active'));
      document.getElementById(`${tabId}-content`).classList.add('active');
    });
  });
}
```

### Error Handling
```javascript
function showComponentError(message, level = 'error') {
  const errorContainer = document.createElement('div');
  errorContainer.className = `component-error ${level}`;
  errorContainer.innerHTML = `
    <div class="error-icon">${level === 'error' ? '⚠️' : 'ℹ️'}</div>
    <div class="error-message">${message}</div>
    <button class="error-close">×</button>
  `;
  
  // Add to component workspace
  const workspace = document.querySelector('.component-workspace');
  if (workspace) {
    workspace.prepend(errorContainer);
    
    // Auto-remove after delay if not an error
    if (level !== 'error') {
      setTimeout(() => {
        errorContainer.remove();
      }, 5000);
    }
    
    // Add close button handler
    const closeButton = errorContainer.querySelector('.error-close');
    if (closeButton) {
      closeButton.addEventListener('click', () => {
        errorContainer.remove();
      });
    }
  }
}
```

### Loading Indicators
```javascript
function showLoading(containerId, message = 'Loading...') {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  const loadingElement = document.createElement('div');
  loadingElement.className = 'loading-indicator';
  loadingElement.innerHTML = `
    <div class="loading-spinner"></div>
    <div class="loading-message">${message}</div>
  `;
  
  container.appendChild(loadingElement);
  return loadingElement;
}

function hideLoading(loadingElement) {
  if (loadingElement && loadingElement.parentNode) {
    loadingElement.parentNode.removeChild(loadingElement);
  }
}
```

## Debugging and Testing

### Component Testing
1. Test component loading
2. Verify tab switching
3. Test all interactive elements
4. Verify data loading and display
5. Test error handling
6. Check responsive behavior

### Console Logging
Include clear, meaningful logs:

```javascript
console.log('[ComponentName] Initializing component');
console.log('[ComponentName] Loading tab:', tabId);
console.error('[ComponentName] Error fetching data:', error);
```

### Event Debugging
Use event listeners with logging:

```javascript
function debugEventListeners(componentId) {
  const component = document.getElementById(componentId);
  if (!component) return;
  
  const elements = component.querySelectorAll('button, a, input, select');
  elements.forEach(element => {
    element.addEventListener('click', (event) => {
      console.log('[Debug] Clicked:', element, 'Event:', event);
    });
  });
}
```

## Projects Chat Implementation Example

### Complete Feature Implementation

The Projects Chat feature serves as an excellent example of the documentation-first development process and simple implementation patterns:

#### 1. Architecture Documentation First
- **Socket architecture**: Defined port assignment strategy (base + 100)
- **On-demand CI lifecycle**: Documented CI creation patterns
- **Integration points**: Mapped connections to existing systems

#### 2. Implementation Documentation
- **HTML structure**: Minimal changes, reuse existing patterns
- **CSS implementation**: Simple show/hide logic, consistent styling
- **JavaScript**: Minimal functions, clear data structures
- **Backend integration**: Single API endpoint, socket communication

#### 3. User and Training Documentation
- **User guide**: Clear instructions for project selection and communication
- **CI training**: How CIs use the system for project coordination
- **Troubleshooting**: Common issues and solutions

#### 4. Key Implementation Patterns

**Simple Data Structure**:
```javascript
// List of dicts as requested - simple and effective
const projectCIs = [
    {
        project_name: "Tekton",
        ci_socket: "numa-ai", 
        socket_port: 42016
    },
    {
        project_name: "Claude-Code",
        ci_socket: "project-claude-code-ai",
        socket_port: 42100
    }
];
```

**Socket Communication**:
```javascript
// Reuse existing aish MessageHandler patterns
async function sendToProjectCI(projectName, message, projectCI) {
    const response = await fetch('/api/projects/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            project_name: projectName,
            message: message,
            ci_socket: projectCI.ci_socket
        })
    });
    // Handle response...
}
```

**CSS-Only Tab Switching**:
```css
/* Show submenu when Projects Chat tab is active */
#tekton-tab-projectschat:checked ~ .tekton .tekton__submenu-bar {
    display: flex !important;
}

/* Show panel when Projects Chat tab is active */  
#tekton-tab-projectschat:checked ~ .tekton #projectschat-panel {
    display: flex;
    flex-direction: column;
}
```

#### 5. Documentation-First Benefits

**Clear Implementation Path**:
- Architecture decisions documented before coding
- Implementation details planned with specific code examples
- User experience designed with clear workflows
- Training materials prepared for CI adoption

**Reduced Development Risk**:
- Edge cases identified in documentation phase
- Integration points mapped to existing systems
- Error handling planned with specific scenarios
- Performance considerations documented upfront

**Maintainable Code**:
- Implementation follows documented patterns
- Code matches architectural decisions
- Future enhancements planned and documented
- Knowledge transfer facilitated by comprehensive docs

#### 6. "Simple, Works, Hard to Screw Up" Philosophy

**Simple**:
- Reuse existing HTML/CSS patterns
- Minimal JavaScript functions
- Single API endpoint
- Clear data structures

**Works**:
- Leverages proven socket communication
- Integrates with existing project management
- Follows established UI patterns
- Tested against real use cases

**Hard to Screw Up**:
- Clear error handling paths
- Consistent with existing patterns
- Well-documented decision points
- Maintainable code structure

## Best Practices

1. **Keep It Simple**:
   - Implement the simplest solution that meets requirements
   - Avoid premature optimization
   - Focus on readability over cleverness

2. **File Management**:
   - Keep files under 500 lines whenever possible
   - Never exceed 1000 lines per file
   - Split files that reach 600+ lines

3. **Consistent Naming**:
   - Use BEM methodology for CSS classes 
   - Prefix component-specific functions and classes
   - Follow established naming patterns

4. **Communication Patterns**:
   - Use Hermes for component-to-component communication
   - Implement simple event-driven updates
   - Handle errors and loading states consistently

5. **Progressive Enhancement**:
   - Build core functionality first
   - Add advanced features incrementally
   - Maintain backward compatibility

6. **Performance**:
   - Minimize DOM manipulations
   - Use event delegation where appropriate
   - Batch updates when possible
   - Avoid excessive re-renders