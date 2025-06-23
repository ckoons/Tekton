# Tekton GUI Styling Rules

## Table of Contents
1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [File Organization](#file-organization)
4. [Right Panel Structure](#right-panel-structure)
5. [Component Implementation](#component-implementation)
6. [Styling Conventions](#styling-conventions)
7. [UI Behaviors](#ui-behaviors)
8. [Environment Variables](#environment-variables)
9. [Implementation Notes](#implementation-notes)

## Overview

This document defines the styling rules and implementation guidelines for the Tekton UI system. It provides a standardized approach to ensure consistency, simplicity, and maintainability across all Tekton components.

## Core Principles

1. **Keep It Simple**: Implement the simplest solution that meets requirements
2. **Maintain Clarity**: Prefer clear, readable code over clever optimizations
3. **File Size Limits**: 
   - Hard limit: 1000 lines per file
   - Target: <500 lines per file
   - Split files that exceed 600 lines
4. **Separation of Concerns**: 
   - Each component in its own directory
   - HTML, CSS, and JS separated into different files
5. **Minimal Dependencies**: Avoid unnecessary libraries and frameworks

## File Organization

### Directory Structure

```
ui/
├── scripts/
│   ├── component-name/           # One directory per component
│   │   ├── html/                 # HTML templates  
│   │   │   ├── main.html         # Main component HTML
│   │   │   ├── tab1.html         # Tab-specific content
│   │   ├── css/                  # Component-specific styles
│   │   │   ├── main.css          # Main styles
│   │   │   ├── tab1.css          # Tab-specific styles
│   │   ├── js/                   # JavaScript functionality
│   │   │   ├── loader.js         # Component initialization
│   │   │   ├── events.js         # Event handlers
│   │   │   ├── api.js            # Backend API communication
```

### File Size Management

When a file exceeds 600 lines:
1. Analyze functionality and identify logical separation points
2. Split into multiple focused files with clear responsibilities
3. Update the component manifest to list all required files
4. Ensure proper load order through the manifest

Example manifest:
```javascript
// athena/manifest.js
export const athenaFiles = [
  'athena/core.js',         // Core functionality
  'athena/graph.js',        // Graph visualization
  'athena/chat.js',         // Chat functionality
  'athena/entities.js',     // Entity management
  'athena/search.js'        // Search functionality
];
```

## Right Panel Structure

Every component's right panel implements this standard structure:

1. **HEADER**: Component identification
   - Shows component name (controlled by SHOW_GREEK_NAMES env var)
   - Consistent styling and position

2. **MENU BAR**: Navigation within component
   - Tab navigation across component sections
   - Action buttons for component-specific operations
   - Consistent styling and behavior

3. **WORKSPACE**: Main content area
   - Tab-specific content that changes based on selected tab
   - Scrollable when content exceeds vertical space

4. **CHAT-INPUT-AREA** (only for LLM chat screens):
   - Fixed position at bottom of panel
   - Text input with send button
   - Consistent styling across all chat interfaces

## Component Implementation

### Component Loader

Each component has a dedicated loader function that:
1. Prepares the right panel
2. Loads HTML content
3. Initializes event handlers
4. Registers the component

Example loader structure:
```javascript
function loadAthenaComponent() {
  // Get HTML panel
  const htmlPanel = document.getElementById('html-panel');
  htmlPanel.innerHTML = '';
  
  // Activate HTML panel
  activatePanel('html');
  
  // Set active component
  setActiveComponent('athena');
  
  // Define HEADER
  const header = createComponentHeader('Athena', 'Knowledge');
  htmlPanel.appendChild(header);
  
  // Define MENU BAR
  const menuBar = createComponentMenuBar('athena', [
    { id: 'chat', label: 'Knowledge Chat', icon: '💬' },
    { id: 'graph', label: 'Knowledge Graph', icon: '🔗' },
    { id: 'entities', label: 'Entities', icon: '📋' }
  ]);
  htmlPanel.appendChild(menuBar);
  
  // Define WORKSPACE
  const workspace = document.createElement('div');
  workspace.className = 'component-workspace';
  workspace.id = 'athena-workspace';
  htmlPanel.appendChild(workspace);
  
  // Initialize default tab
  loadAthenaTab('chat');
  
  // Set up event handlers
  setupAthenaEvents();
}
```

### Tab Management

Tabs are implemented with a simple mechanism:
1. Tab buttons in the MENU BAR
2. Content containers in the WORKSPACE
3. JavaScript to toggle active states

```javascript
function setupTabEvents(componentId, tabButtons) {
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      // Update tab button styles
      tabButtons.forEach(b => b.classList.remove('active'));
      button.classList.add('active');
      
      // Get tab ID
      const tabId = button.dataset.tab;
      
      // Load tab content
      loadComponentTab(componentId, tabId);
    });
  });
}
```

## Styling Conventions

### Colors and Themes

- Follow the existing dark theme with blue accents
- Use Settings component's theme system for consistent colors
- Use CSS variables for theme colors
- Component-specific colors should still coordinate with overall theme

### CSS Naming

- Use BEM (Block Element Modifier) methodology
- Follow existing conventions for class names
- Avoid overly generic class names
- Component-specific styles should use component name as prefix

### UI Elements

- Standard form controls with consistent styling
- Common component patterns for tabs, lists, and controls
- Consistent spacing and alignment
- Focus on readability and clarity

## UI Behaviors

### General Principles

- Simple, direct user interactions
- Immediate feedback for user actions
- No complex animations or transitions
- Basic click/input behaviors with clear outcomes

### Tab Navigation

- Single click to switch tabs
- Visual indication of active tab
- Consistent behavior across components

### Forms and Inputs

- Standard form controls with immediate validation
- Enter key submits forms
- Clear input areas after submission

## Environment Variables

### SHOW_GREEK_NAMES

Controls display of Greek component names:
- `true`: Shows both Greek and functional names (e.g., "Athena - Knowledge")
- `false`: Shows only functional names (e.g., "Knowledge")

Implementation:
```javascript
function createComponentHeader(greekName, functionalName) {
  const header = document.createElement('div');
  header.className = 'component-header';
  
  const titleElement = document.createElement('h1');
  
  if (window.ENV && window.ENV.SHOW_GREEK_NAMES === 'true') {
    titleElement.textContent = `${greekName} - ${functionalName}`;
  } else {
    titleElement.textContent = functionalName;
  }
  
  header.appendChild(titleElement);
  return header;
}
```

## Implementation Notes

### Communication with Backend

- Use Hermes for component-to-component communication
- Simple API calls for backend interactions
- Consistent error handling patterns
- Handle connectivity issues gracefully

### State Management

- Keep state simple and localized
- Avoid complex state management patterns
- Use simple event-based updates where needed
- Separate display logic from business logic

### Performance Considerations

- Minimize DOM operations
- Lazy-load content when appropriate
- Batch updates when possible
- Focus on code readability over micro-optimizations