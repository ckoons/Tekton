# Metis UI Component - Claude Code Prompt

## Context

You are Working Claude, tasked with implementing the Metis UI component for the Tekton ecosystem. This component will provide visualization and interaction capabilities for the Metis task management system, offering multiple views of tasks, dependencies, complexity analysis, and PRD parsing results.

**CRITICAL: Use Athena as the golden reference implementation.** The Athena component is the definitive, proven template for all Clean Slate UI components in Tekton. You must study and closely follow Athena's structure, patterns, and implementation details. The Metis component should maintain absolute consistency with Athena's established patterns while implementing Metis-specific functionality.

This implementation follows the Clean Slate architecture pattern established in previous UI development efforts, with Athena, Prometheus, Telos, and Harmonia as successful examples. The component must ensure strict isolation, proper BEM naming, and container-scoped operations. The component will feature a tab-based interface with multiple visualization types and real-time updates via WebSocket.

## Sprint Documentation

Before beginning implementation, please review these documents:

1. [Sprint Plan](./SprintPlan.md): High-level goals, approach, and expected outcomes
2. [Architectural Decisions](./ArchitecturalDecisions.md): Key architectural decisions and their rationale
3. [Implementation Plan](./ImplementationPlan.md): Detailed implementation tasks and phases
4. [Clean Slate UI Implementation](../Clean_Slate_Sprint/CleanSlateUIImplementation.md): UI component architecture and implementation patterns

## Environment Setup

For this implementation, we'll use the existing Clean Slate branch:

```bash
# Start by changing to the Tekton directory
cd Tekton

# Verify and checkout the Clean Slate branch
git checkout sprint/Clean_Slate_051125
git status
```

This approach ensures we're working with the stable Clean Slate implementation as our foundation. Since you'll be the only Claude Code session working on the Tekton project, using this existing branch simplifies the workflow and ensures consistency.

## Implementation Approach

### Phase 1: Foundation and Core Structure

1. **Component Scaffold**
   - Create the basic HTML structure with proper BEM naming
   - Implement CSS with component-scoped styles
   - Set up JavaScript initialization
   - Register the component with the loader

2. **Tab System**
   - Implement the four-tab structure (Tasks, Dependency, Complexity, PRD)
   - Create tab switching functionality
   - Ensure proper tab state management

3. **API Client**
   - Implement the client for Metis backend API
   - Create functions for task CRUD operations
   - Add dependency management functions
   - Implement error handling and retries

4. **WebSocket Connection**
   - Set up real-time updates via WebSocket
   - Handle different event types (task created, updated, deleted, etc.)
   - Implement reconnection logic

5. **Basic Task List View**
   - Create initial list view for tasks
   - Implement filtering and sorting
   - Add task rendering and interactions

### Implementation Guidelines

#### HTML Structure

The HTML structure should follow this pattern:

```html
<div class="metis__container">
  <div class="metis__header">
    <h2 class="metis__title">Metis - Task Management</h2>
  </div>
  
  <!-- Tab Navigation -->
  <div class="metis__tabs">
    <button class="metis__tab-button metis__tab-button--active" data-tab="tasks">Tasks</button>
    <button class="metis__tab-button" data-tab="dependency">Dependency</button>
    <button class="metis__tab-button" data-tab="complexity">Complexity</button>
    <button class="metis__tab-button" data-tab="prd">PRD</button>
  </div>
  
  <!-- Tab Content -->
  <div class="metis__content">
    <!-- Tasks Tab -->
    <div class="metis__tab-content metis__tab-content--active" data-tab="tasks">
      <!-- Task tab content -->
    </div>
    
    <!-- Other tabs -->
    <div class="metis__tab-content" data-tab="dependency">
      <!-- Dependency tab content -->
    </div>
    
    <div class="metis__tab-content" data-tab="complexity">
      <!-- Complexity tab content -->
    </div>
    
    <div class="metis__tab-content" data-tab="prd">
      <!-- PRD tab content -->
    </div>
  </div>
  
  <div class="metis__footer">
    <div class="metis__status">Ready</div>
  </div>
</div>
```

#### JavaScript Structure

JavaScript should follow this pattern:

```javascript
// Component initialization
document.addEventListener('DOMContentLoaded', function() {
  // Get component container
  const container = document.querySelector('.metis__container');
  if (!container) return;
  
  // Initialize component
  initMetisComponent(container);
});

// Main initialization function
function initMetisComponent(container) {
  // Component state
  const state = {
    activeTab: 'tasks',
    activeView: 'list',
    tasks: [],
    // Other state properties
  };
  
  // Initialize features
  initTabs(container, state);
  initApiClient(container, state);
  initWebSocket(container, state);
  
  // Load initial data
  loadInitialData(container, state);
}

// Tab functionality
function initTabs(container, state) {
  const tabButtons = container.querySelectorAll('.metis__tab-button');
  
  // Tab click handler
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      // Get tab name
      const tabName = button.getAttribute('data-tab');
      
      // Update active tab
      setActiveTab(container, state, tabName);
    });
  });
}

// Set active tab
function setActiveTab(container, state, tabName) {
  // Update state
  state.activeTab = tabName;
  
  // Update UI
  const tabButtons = container.querySelectorAll('.metis__tab-button');
  const tabContents = container.querySelectorAll('.metis__tab-content');
  
  // Update tab buttons
  tabButtons.forEach(button => {
    if (button.getAttribute('data-tab') === tabName) {
      button.classList.add('metis__tab-button--active');
    } else {
      button.classList.remove('metis__tab-button--active');
    }
  });
  
  // Update tab contents
  tabContents.forEach(content => {
    if (content.getAttribute('data-tab') === tabName) {
      content.classList.add('metis__tab-content--active');
    } else {
      content.classList.remove('metis__tab-content--active');
    }
  });
  
  // Render tab content
  renderTabContent(container, state);
}

// Other functions...
```

#### CSS Structure

CSS should follow BEM naming and component scoping:

```css
/* Component container */
.metis__container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  color: var(--text-color, #f0f0f0);
  background-color: var(--background-color, #1a1a1a);
  font-family: var(--font-family, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif);
}

/* Component header */
.metis__header {
  padding: 10px 20px;
  border-bottom: 1px solid var(--border-color, #333);
}

.metis__title {
  margin: 0;
  font-size: 1.5rem;
}

/* Tab system */
.metis__tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color, #333);
}

.metis__tab-button {
  padding: 10px 20px;
  background: none;
  border: none;
  color: var(--text-color, #f0f0f0);
  cursor: pointer;
}

.metis__tab-button--active {
  background-color: var(--active-tab-bg, #333);
  border-bottom: 2px solid var(--accent-color, #007acc);
}

/* Tab content */
.metis__content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.metis__tab-content {
  display: none;
  height: 100%;
  overflow: auto;
  padding: 20px;
}

.metis__tab-content--active {
  display: block;
}

/* Other styles... */
```

### Development Standards

- **BEM Naming**: All CSS classes follow `block__element--modifier` pattern
- **Component Isolation**: DOM queries scoped to component container
- **Progressive Enhancement**: Build core functionality first, then add features
- **Error Handling**: Provide meaningful error messages and fallbacks
- **Performance**: Optimize rendering for large datasets
- **Accessibility**: Ensure keyboard navigation and screen reader support

### API Integration

The component will interact with these Metis backend API endpoints:

- `GET /api/v1/tasks`: List tasks with filtering
- `POST /api/v1/tasks`: Create new task
- `GET /api/v1/tasks/{task_id}`: Get specific task
- `PUT /api/v1/tasks/{task_id}`: Update task
- `DELETE /api/v1/tasks/{task_id}`: Delete task
- `GET /api/v1/tasks/{task_id}/dependencies`: List dependencies
- `POST /api/v1/tasks/{task_id}/dependencies`: Add dependency
- `DELETE /api/v1/tasks/{task_id}/dependencies/{dependency_id}`: Remove dependency
- `POST /api/v1/tasks/{task_id}/analyze-complexity`: Analyze task complexity
- `GET /api/v1/tasks/complexity-report`: Get complexity report
- `POST /api/v1/prd/parse`: Parse PRD document into tasks

The API client should discover the Metis service through Hermes and handle authentication and error cases.

### WebSocket Integration

The component will connect to the Metis WebSocket endpoint at `/ws` and handle these events:

- `TASK_CREATED`: New task was created
- `TASK_UPDATED`: Task was updated
- `TASK_DELETED`: Task was deleted
- `DEPENDENCY_ADDED`: New dependency was added
- `DEPENDENCY_REMOVED`: Dependency was removed
- `COMPLEXITY_UPDATED`: Complexity score was updated

The WebSocket client should handle reconnection and ensure state consistency with server updates.

## Key Visualization Types

### List View

The list view should:
- Display tasks in a tabular format
- Support sorting by different columns
- Allow filtering by various criteria
- Support grouping by status, priority, etc.
- Allow bulk operations on selected tasks

### Board View

The board view should:
- Display tasks in columns based on status
- Support drag-and-drop between columns
- Show task cards with key information
- Allow column customization
- Support swimlanes for additional categorization

### Graph View

The graph view should:
- Visualize tasks as nodes and dependencies as edges
- Allow interactive navigation (zoom, pan)
- Support node selection and highlighting
- Show critical paths
- Allow filtering to focus on specific tasks

## Tab-Specific Requirements

### Tasks Tab

- Primary task management interface
- Switches between list, board, and graph views
- Controls for task creation, filtering, sorting
- Task detail panel for editing

### Dependency Tab

- Focused visualization of task dependencies
- Interactive dependency graph
- Critical path highlighting
- Dependency creation and validation

### Complexity Tab

- Visualization of task complexity scores
- Factor breakdown charts
- Comparative analysis
- Resource allocation visualization

### PRD Tab

- Document upload interface
- PRD content preview
- Task generation workflow
- Generated task preview and editing

## Testing Requirements

- Component loads correctly in Hephaestus
- Tab switching works correctly
- Task data loads and displays properly
- All visualization types render correctly
- Real-time updates via WebSocket work
- Task operations (create, update, delete) function properly
- Performance is acceptable with large datasets
- Error handling works as expected

## Documentation Requirements

Create or update these documentation files:

- `README.md`: Component overview and basic usage
- `docs/api_integration.md`: API interaction details
- `docs/visualization_types.md`: View types documentation
- `docs/tab_functionality.md`: Specialized tab documentation

## Next Steps

1. Review Clean Slate architecture documentation
2. Set up the initial component scaffold
3. Implement the tab system
4. Create the API client
5. Implement basic task list view

## Questions

If you have any questions or need clarification, please ask before proceeding with implementation. It's important to ensure alignment with the Clean Slate architecture and Tekton UI standards.