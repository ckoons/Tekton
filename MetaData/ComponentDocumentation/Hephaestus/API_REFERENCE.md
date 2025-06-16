# Hephaestus API Reference

This document provides a detailed reference for the Hephaestus API, following the Single Port Architecture pattern on port 8080.

## Base URL

All API endpoints are accessible under the base URL:

```
http://<host>:8080/api/
```

## REST API Endpoints

### Component Management API

#### List Available Components

```
GET /api/components
```

Lists all available UI components.

**Response:**

```json
{
  "components": [
    {
      "id": "ergon",
      "name": "Ergon",
      "description": "Task and agent management",
      "path": "/components/ergon.html",
      "status": "active"
    },
    {
      "id": "athena",
      "name": "Athena",
      "description": "Knowledge graph visualization",
      "path": "/components/athena.html",
      "status": "active"
    },
    {
      "id": "terma",
      "name": "Terma",
      "description": "Terminal integration",
      "path": "/components/terma.html",
      "status": "active"
    }
  ]
}
```

#### Get Component Details

```
GET /api/components/{component_id}
```

Retrieves detailed information about a specific component.

**Path Parameters:**

- `component_id` - The ID of the component to retrieve

**Response:**

```json
{
  "id": "ergon",
  "name": "Ergon",
  "description": "Task and agent management",
  "path": "/components/ergon.html",
  "script_path": "/scripts/ergon-component.js",
  "style_path": "/styles/ergon.css",
  "status": "active",
  "version": "1.0.0",
  "dependencies": ["terma"],
  "config": {
    "default_view": "tasks",
    "features": ["task_management", "agent_execution", "history_view"]
  },
  "connections": {
    "backend_service": "http://localhost:8003",
    "websocket": "ws://localhost:8003/ws"
  }
}
```

#### Register Component

```
POST /api/components/register
```

Registers a new UI component.

**Request Body:**

```json
{
  "id": "new-component",
  "name": "New Component",
  "description": "A new UI component",
  "path": "/components/new-component.html",
  "script_path": "/scripts/new-component.js",
  "style_path": "/styles/new-component.css",
  "dependencies": ["terma"],
  "config": {
    "default_view": "main",
    "features": ["feature1", "feature2"]
  }
}
```

**Response:**

```json
{
  "id": "new-component",
  "name": "New Component",
  "status": "registered",
  "registration_time": "2025-05-01T10:15:30Z"
}
```

### UI State Management API

#### Get State

```
GET /api/state/{namespace}
```

Retrieves UI state for a specific namespace.

**Path Parameters:**

- `namespace` - The namespace of the state to retrieve (e.g., "ergon", "global")

**Response:**

```json
{
  "namespace": "ergon",
  "state": {
    "current_view": "tasks",
    "expanded_panels": ["task-123", "task-456"],
    "sort_order": "date_desc",
    "filters": {
      "status": "active",
      "priority": "high"
    }
  },
  "last_updated": "2025-05-01T10:15:30Z"
}
```

#### Update State

```
PUT /api/state/{namespace}
```

Updates UI state for a specific namespace.

**Path Parameters:**

- `namespace` - The namespace of the state to update

**Request Body:**

```json
{
  "state": {
    "current_view": "agents",
    "expanded_panels": ["agent-789"],
    "sort_order": "name_asc",
    "filters": {
      "status": "all",
      "type": "assistant"
    }
  }
}
```

**Response:**

```json
{
  "namespace": "ergon",
  "status": "updated",
  "updated_at": "2025-05-01T10:20:30Z"
}
```

### User Preferences API

#### Get User Preferences

```
GET /api/preferences
```

Retrieves user preferences.

**Response:**

```json
{
  "theme": "dark",
  "font_size": "medium",
  "layout": "default",
  "sidebar_collapsed": false,
  "notifications_enabled": true,
  "default_component": "ergon",
  "terminal_settings": {
    "font_family": "monospace",
    "cursor_style": "block",
    "background_opacity": 0.9
  }
}
```

#### Update User Preferences

```
PUT /api/preferences
```

Updates user preferences.

**Request Body:**

```json
{
  "theme": "light",
  "font_size": "large",
  "sidebar_collapsed": true
}
```

**Response:**

```json
{
  "status": "updated",
  "updated_at": "2025-05-01T10:20:30Z"
}
```

### System API

#### Get System Status

```
GET /api/system/status
```

Retrieves the status of all Tekton components.

**Response:**

```json
{
  "system": {
    "status": "healthy",
    "uptime": 3600,
    "version": "1.0.0"
  },
  "components": [
    {
      "id": "ergon",
      "status": "active",
      "url": "http://localhost:8003",
      "health": "healthy"
    },
    {
      "id": "athena",
      "status": "active",
      "url": "http://localhost:8002",
      "health": "healthy"
    },
    {
      "id": "hermes",
      "status": "active",
      "url": "http://localhost:8000",
      "health": "healthy"
    }
  ]
}
```

#### Get Component Services

```
GET /api/system/services
```

Retrieves information about available component services.

**Response:**

```json
{
  "services": [
    {
      "id": "ergon-api",
      "component": "ergon",
      "url": "http://localhost:8003/api",
      "description": "Ergon REST API"
    },
    {
      "id": "ergon-ws",
      "component": "ergon",
      "url": "ws://localhost:8003/ws",
      "description": "Ergon WebSocket API"
    },
    {
      "id": "athena-api",
      "component": "athena",
      "url": "http://localhost:8002/api",
      "description": "Athena REST API"
    }
  ]
}
```

### Templates API

#### List Templates

```
GET /api/templates
```

Lists all available UI templates.

**Response:**

```json
{
  "templates": [
    {
      "id": "task-card",
      "description": "Task card template",
      "path": "/templates/task-card.html"
    },
    {
      "id": "agent-card",
      "description": "Agent card template",
      "path": "/templates/agent-card.html"
    },
    {
      "id": "dialog",
      "description": "Standard dialog template",
      "path": "/templates/dialog.html"
    }
  ]
}
```

#### Get Template

```
GET /api/templates/{template_id}
```

Retrieves a specific UI template.

**Path Parameters:**

- `template_id` - The ID of the template to retrieve

**Response:**

```json
{
  "id": "task-card",
  "description": "Task card template",
  "content": "<div class=\"task-card\">\n  <div class=\"task-card__header\">\n    <h3 class=\"task-card__title\">{{title}}</h3>\n  </div>\n  <div class=\"task-card__body\">\n    <p class=\"task-card__description\">{{description}}</p>\n  </div>\n  <div class=\"task-card__footer\">\n    <span class=\"task-card__status\">{{status}}</span>\n    <button class=\"task-card__action\">{{action}}</button>\n  </div>\n</div>"
}
```

### Assets API

#### List Assets

```
GET /api/assets
```

Lists all available UI assets.

**Response:**

```json
{
  "assets": {
    "images": [
      {
        "id": "logo",
        "path": "/images/logo.png",
        "description": "Tekton logo"
      },
      {
        "id": "icon-task",
        "path": "/images/icons/task.svg",
        "description": "Task icon"
      }
    ],
    "scripts": [
      {
        "id": "utils",
        "path": "/scripts/utils.js",
        "description": "Utility functions"
      },
      {
        "id": "state-manager",
        "path": "/scripts/state-manager.js",
        "description": "State management system"
      }
    ],
    "styles": [
      {
        "id": "main",
        "path": "/styles/main.css",
        "description": "Main stylesheet"
      },
      {
        "id": "themes",
        "path": "/styles/themes.css",
        "description": "Theme definitions"
      }
    ]
  }
}
```

### Health Check

```
GET /health
```

Checks the health status of the Hephaestus component.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "components": {
    "ui_server": "healthy",
    "component_registry": "healthy",
    "template_engine": "healthy",
    "static_assets": "healthy"
  }
}
```

## WebSocket API

### UI Events

```
WebSocket: ws://<host>:8080/ws/ui
```

Provides real-time updates about UI events.

**Connection URL Parameters:**

- None

**Messages:**

UI State Change:
```json
{
  "type": "state_change",
  "timestamp": "2025-05-01T10:15:30Z",
  "data": {
    "namespace": "ergon",
    "changes": {
      "current_view": "agents",
      "expanded_panels": ["agent-789"]
    }
  }
}
```

Component Event:
```json
{
  "type": "component_event",
  "timestamp": "2025-05-01T10:15:30Z",
  "data": {
    "component_id": "ergon",
    "event_type": "task_created",
    "payload": {
      "task_id": "task-789",
      "title": "New Task"
    }
  }
}
```

System Notification:
```json
{
  "type": "notification",
  "timestamp": "2025-05-01T10:15:30Z",
  "data": {
    "level": "info",
    "title": "Deployment Completed",
    "message": "The deployment has completed successfully.",
    "duration": 5000
  }
}
```

### Component Communication

```
WebSocket: ws://<host>:8080/ws/components
```

Enables real-time communication between UI components.

**Connection URL Parameters:**

- None

**Messages:**

Component Message:
```json
{
  "type": "component_message",
  "timestamp": "2025-05-01T10:15:30Z",
  "data": {
    "source": "ergon",
    "target": "terma",
    "action": "execute_command",
    "payload": {
      "command": "git status"
    }
  }
}
```

Component Response:
```json
{
  "type": "component_response",
  "timestamp": "2025-05-01T10:15:31Z",
  "data": {
    "source": "terma",
    "target": "ergon",
    "action": "execute_command",
    "status": "success",
    "payload": {
      "output": "On branch main\nYour branch is up to date with 'origin/main'.\n\nNothing to commit, working tree clean"
    }
  }
}
```

## Front-End API

Hephaestus provides a JavaScript API for component integration and communication.

### Component Registration

```javascript
// Register a component
Hephaestus.registerComponent({
  id: 'my-component',
  name: 'My Component',
  initialize: function(root, options) {
    // Initialize component
    this.root = root;
    this.options = options;
    this.render();
  },
  render: function() {
    // Render component
    this.root.innerHTML = `
      <div class="my-component">
        <h2>${this.options.title}</h2>
        <div class="my-component__content">
          Content goes here
        </div>
      </div>
    `;
  },
  destroy: function() {
    // Clean up resources
    this.root.innerHTML = '';
  }
});
```

### State Management

```javascript
// Get state
const state = Hephaestus.getState('my-component');

// Update state
Hephaestus.setState('my-component', {
  current_view: 'details',
  selected_item: 'item-123'
});

// Subscribe to state changes
Hephaestus.subscribeToState('my-component', (newState, oldState) => {
  // Handle state change
  if (newState.current_view !== oldState.current_view) {
    // View changed, update UI
  }
});
```

### Component Communication

```javascript
// Send message to another component
Hephaestus.sendMessage({
  target: 'other-component',
  action: 'show_item',
  payload: {
    item_id: 'item-123'
  }
});

// Listen for messages
Hephaestus.onMessage('show_item', (message) => {
  // Handle message
  const itemId = message.payload.item_id;
  // Show the item
});
```

### UI Utilities

```javascript
// Show notification
Hephaestus.showNotification({
  level: 'success',
  title: 'Item Created',
  message: 'The item was created successfully',
  duration: 3000
});

// Show dialog
Hephaestus.showDialog({
  title: 'Confirm Action',
  content: 'Are you sure you want to delete this item?',
  buttons: [
    {
      text: 'Cancel',
      action: 'cancel',
      style: 'secondary'
    },
    {
      text: 'Delete',
      action: 'confirm',
      style: 'danger'
    }
  ],
  onAction: (action) => {
    if (action === 'confirm') {
      // Handle confirmation
    }
  }
});

// Toggle theme
Hephaestus.setTheme('dark');

// Get current theme
const currentTheme = Hephaestus.getTheme();
```

### WebSocket Integration

```javascript
// Connect to component service
const ws = Hephaestus.connectWebSocket({
  service: 'ergon-ws',
  onOpen: () => {
    console.log('Connected to Ergon service');
  },
  onMessage: (message) => {
    // Handle message
  },
  onClose: () => {
    console.log('Disconnected from Ergon service');
  }
});

// Send message
ws.send(JSON.stringify({
  type: 'request',
  action: 'get_tasks',
  payload: {
    status: 'active'
  }
}));

// Close connection
ws.close();
```

## Error Responses

All API endpoints return standard error responses in the following format:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "theme",
        "message": "Theme must be 'light' or 'dark'"
      }
    ]
  }
}
```

Common error codes:

- `validation_error`: Request validation failed
- `not_found`: Resource not found
- `already_exists`: Resource already exists
- `permission_denied`: Permission denied
- `component_error`: Component-specific error
- `internal_error`: Internal server error