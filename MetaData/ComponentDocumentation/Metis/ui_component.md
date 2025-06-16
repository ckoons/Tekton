# Metis UI Component

The Metis UI component provides a user-friendly interface for the Metis task management system within the Tekton Hephaestus UI. It follows the Clean Slate architecture pattern established for all Tekton UI components.

## Component Features

- **Task Management**: Create, edit, delete, and manage tasks with full metadata
- **Multiple Visualization Types**:
  - **List View**: Tabular display with sorting and filtering
  - **Board View**: Kanban-style columns with drag-and-drop functionality
  - **Graph View**: Interactive dependency visualization
- **Dependency Management**: Visualize and manage task dependencies
- **Complexity Analysis**: Analyze and visualize task complexity metrics
- **PRD Parsing**: Extract tasks automatically from PRD documents
- **Chat Integration**:
  - **Workflow Chat**: Task-specific chat interface
  - **Team Chat**: Shared chat across Tekton components
- **Real-time Updates**: Live updates via WebSocket connection

## Component Structure

The Metis UI component follows the Clean Slate architecture pattern with strict component isolation following the Athena pattern exactly:

### HTML Structure

The component consolidates all HTML, CSS, and core JavaScript in a single file for simplicity and isolation:

```html
<!-- Metis Component - Task Management and Visualization -->
<div class="metis">
    <!-- Component Header with Title -->
    <div class="metis__header">
        <div class="metis__title-container">
            <img src="/images/hexagon.jpg" alt="Tekton" class="metis__icon">
            <h2 class="metis__title">
                <span class="metis__title-main">Metis</span>
                <span class="metis__title-sub">Task Management</span>
            </h2>
        </div>
    </div>
    
    <!-- Metis Menu Bar with Tab Navigation -->
    <div class="metis__menu-bar">
        <div class="metis__tabs">
            <div class="metis__tab metis__tab--active" data-tab="tasks" onclick="metis_switchTab('tasks'); return false;">
                <span class="metis__tab-label">Tasks</span>
            </div>
            <!-- Other tabs... -->
        </div>
        <div class="metis__actions">
            <button id="task-add-btn" class="metis__action-button" onclick="metis_addTask(); return false;">
                <span class="metis__button-label">Add Task</span>
            </button>
        </div>
    </div>
    
    <!-- Content areas, tabs, and other UI elements... -->
    
    <!-- Embedded component-specific styles and scripts... -->
</div>
```

### JavaScript Architecture

The component uses a simplified JavaScript approach without Shadow DOM:

```javascript
// Define the component namespace
window.metisComponent = window.metisComponent || {};

// Component state
window.metisComponent.state = {
    activeTab: 'tasks',
    activeView: 'list',
    tasks: [],
    dependencies: [],
    complexityData: {}
};

/**
 * Initialize the component
 */
window.metisComponent.init = function() {
    // Setup event listeners and load data
};

// Tab switching function
window.metis_switchTab = function(tabId) {
    // Tab switching implementation
};

// Other component functions...
```

### Tab System

The component features a tab-based interface with six main tabs:

1. **Tasks Tab**: Primary task management interface with multiple view types
2. **Dependency Tab**: Focused visualization of task dependencies with graph view
3. **Complexity Tab**: Analysis and visualization of task complexity scores
4. **PRD Tab**: Interface for uploading and parsing PRD documents into tasks
5. **Workflow Chat**: Task-specific chat for workflow assistance
6. **Team Chat**: Shared chat across Tekton components

## Tasks Tab

The Tasks tab is the primary interface for task management. It provides three different view types:

### List View
- Tabular display of tasks
- Sortable columns (click header to sort)
- Filtering by status, priority, and search text
- Actions column for task operations
- Task detail panel for viewing and editing

### Board View
- Kanban-style columns for each status
- Drag-and-drop functionality for changing status
- Task cards with key information
- Card count per status

### Graph View
- Network graph visualization of tasks and dependencies
- Interactive navigation (zoom, pan)
- Node selection for detailed information
- Node sizing based on complexity

## Dependency Tab

The Dependency tab focuses on visualizing and managing task dependencies:

- Interactive graph visualization of task dependencies
- Critical path highlighting
- Add/remove dependency controls
- Dependency search and filtering

## Complexity Tab

The Complexity tab provides analysis and visualization of task complexity:

- Complexity score distribution chart
- Detailed breakdown of complexity factors
- Analyze complexity button for tasks
- Comparative analysis of task complexity

## PRD Tab

The PRD tab allows for automatic task extraction from PRD documents:

- File upload interface for PRD documents (drag & drop supported)
- Parse button to extract tasks
- Preview of extracted tasks
- Import functionality for generated tasks

## Workflow Chat Tab

The Workflow Chat tab provides a dedicated interface for task-related conversations:

- Task-specific chat interface for workflow assistance
- AI-powered responses to task-related queries
- Persistent chat history within the session
- Clear button to reset the conversation

## Team Chat Tab

The Team Chat tab offers a shared communication channel across Tekton components:

- Shared chat interface visible from all Tekton components
- Team-wide communication and coordination
- Consistent chat experience matching Athena's implementation
- Clear button to reset the conversation

## API Integration

The component integrates with the Metis backend API endpoints:

```javascript
// Example API calls
const tasks = await fetch('/api/v1/tasks').then(res => res.json());
await fetch('/api/v1/tasks', {
  method: 'POST',
  body: JSON.stringify(taskData)
});
```

## WebSocket Integration

The component connects to the Metis WebSocket endpoint for real-time updates:

```javascript
// Example WebSocket integration
const ws = new WebSocket('ws://localhost:8XXX/ws');
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'TASK_CREATED') {
    // Handle task creation
  }
};
```

## Styling

The component uses BEM-named CSS classes for consistent styling:

```css
.metis__container { /* Component container */ }
.metis__header { /* Component header */ }
.metis__tab { /* Tab element */ }
.metis__panel { /* Tab panel */ }
.metis__task-table { /* Task list table */ }
.metis__task-card { /* Task card element */ }
```

## Installation

The Metis UI component is registered in the Hephaestus component registry:

```json
{
  "id": "metis",
  "name": "Metis",
  "description": "Task management and visualization",
  "icon": "📋",
  "defaultMode": "html",
  "capabilities": [
    "task_management",
    "dependency_visualization",
    "complexity_analysis",
    "prd_parsing",
    "component_isolation",
    "state_management"
  ],
  "componentPath": "components/metis/metis-component.html",
  "scripts": [
    "scripts/metis/metis-component.js"
  ],
  "usesShadowDom": false
}
```

## Architecture Decisions

1. **Direct DOM Integration**: No Shadow DOM, following the Athena pattern exactly
2. **Self-Contained Component**: All HTML, CSS, and core JS in a single file
3. **BEM Naming**: Clear and consistent class naming convention (metis__element--modifier)
4. **Tab-Based Interface**: Organized access to different functionality
5. **Multiple View Types**: Different visualizations for different needs
6. **Chat Integration**: Workflow and team chat interfaces with shared footer
7. **HTML Panel Protection**: Explicit DOM protection to ensure HTML panel visibility
8. **Global Function Namespace**: Global functions with component prefix (metis_functionName)
9. **Unified Menu Bar Height**: Consistent 46px height for all menu bars

## Usage

To use the Metis UI component in the Tekton Hephaestus UI:

1. Ensure the Metis backend is running
2. Open the Tekton UI in a browser
3. Click the Metis icon in the navigation sidebar
4. The component will load automatically

## Development

For local development:

1. Make changes to component files
2. Reload the Hephaestus UI to see changes
3. The component uses vanilla JavaScript without build steps

## Key Implementation Notes

- DOM queries are scoped to the component container to avoid conflicts
- All function names are prefixed with `metis_` to avoid global namespace conflicts
- Global component state is stored in the `window.metisComponent.state` object
- Event listeners are scoped to the component elements
- HTML Panel is protected from being hidden by the UI manager
- Chat footer visibility is toggled based on active tab
- Consolidated search and filter controls in the secondary menu bar
- Main content area adjusts to accommodate footer when in chat tabs

## Resources

- [Metis Backend Documentation](../README.md)
- [API Reference](./api_reference.md)
- [Integration Guide](./integration_guide.md)
- [Athena Reference Component](/Athena/ui/athena-component.html)