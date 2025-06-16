# Metis User Guide

## Introduction

Metis is the task management system for the Tekton ecosystem. This guide will help you get started with Metis and show you how to use its key features to create, organize, track, and analyze tasks for your projects.

## Getting Started

### Installation

There are multiple ways to install Metis:

#### From Source

```bash
# Clone the repository
git clone https://github.com/example/tekton.git
cd tekton/Metis

# Install Metis and its dependencies
pip install -e .
```

#### With Tekton Installer

```bash
# Run the Tekton installer
./tekton-install.sh --components metis
```

### Starting Metis

You can start Metis in several ways:

```bash
# Start the Metis API server directly
cd Metis
python -m metis

# Using the run script
./run_metis.sh

# Start with Tekton launcher
./scripts/tekton-launch --components metis

# Register with Hermes (required for full ecosystem integration)
python -m Metis/scripts/register_with_hermes.py
```

### Accessing Metis

Once started, Metis is available at:

- **API**: `http://localhost:8011/api/v1`
- **WebSocket**: `ws://localhost:8011/ws`

## Tasks

Tasks in Metis represent discrete units of work to be done and form the core of the task management system.

### Creating a Task

#### Using the API

```python
import requests

# Base URL
base_url = "http://localhost:8011"

# Create a task
response = requests.post(f"{base_url}/api/v1/tasks", json={
    "title": "Implement Authentication",
    "description": "Add user authentication to the application",
    "status": "pending",
    "priority": "high",
    "tags": ["security", "backend"],
    "due_date": "2025-06-01T00:00:00Z"
})
task_id = response.json()["task"]["id"]
```

### Managing Tasks

#### Listing Tasks

```python
# List all tasks
response = requests.get(f"{base_url}/api/v1/tasks")
tasks = response.json()["tasks"]
total = response.json()["total"]

# Filter tasks
response = requests.get(f"{base_url}/api/v1/tasks", params={
    "status": "pending",
    "priority": "high"
})
filtered_tasks = response.json()["tasks"]
```

#### Viewing a Task

```python
# Get task details
response = requests.get(f"{base_url}/api/v1/tasks/{task_id}")
task = response.json()["task"]
```

#### Updating a Task

```python
# Update task
response = requests.put(f"{base_url}/api/v1/tasks/{task_id}", json={
    "status": "in_progress",
    "assignee": "user@example.com"
})
updated_task = response.json()["task"]
```

#### Deleting a Task

```python
# Delete task
response = requests.delete(f"{base_url}/api/v1/tasks/{task_id}")
success = response.json()["success"]
```

### Task Status

Tasks in Metis have the following status values:

- **PENDING**: The task is not yet started
- **IN_PROGRESS**: The task is currently being worked on
- **REVIEW**: The task is completed and waiting for review
- **DONE**: The task is completed and approved
- **BLOCKED**: The task is blocked by dependencies or other factors
- **CANCELLED**: The task has been cancelled

Status transitions are governed by the following rules:

- From **PENDING**: Can move to IN_PROGRESS or CANCELLED
- From **IN_PROGRESS**: Can move to REVIEW, BLOCKED, or CANCELLED
- From **REVIEW**: Can move to IN_PROGRESS, DONE, or CANCELLED
- From **BLOCKED**: Can move to IN_PROGRESS or CANCELLED
- From **DONE**: Can move to IN_PROGRESS (reopen)
- From **CANCELLED**: Can move to PENDING (reactivate)

### Task Priority

Tasks can have the following priority levels:

- **LOW**: Low priority tasks that can be deferred
- **MEDIUM**: Normal priority tasks
- **HIGH**: High priority tasks that should be addressed soon
- **CRITICAL**: Critical tasks that require immediate attention

## Dependencies

Dependencies in Metis represent relationships between tasks, helping you track which tasks block others or need to be completed first.

### Creating Dependencies

```python
# Create a dependency
response = requests.post(f"{base_url}/api/v1/dependencies", json={
    "source_task_id": task1_id,
    "target_task_id": task2_id,
    "dependency_type": "blocks"  # task1 blocks task2
})
dependency_id = response.json()["dependency"]["id"]
```

### Managing Dependencies

#### Listing Dependencies

```python
# List all dependencies
response = requests.get(f"{base_url}/api/v1/dependencies")
dependencies = response.json()["dependencies"]

# Get dependencies for a specific task
response = requests.get(f"{base_url}/api/v1/tasks/{task_id}/dependencies")
task_dependencies = response.json()["dependencies"]
```

#### Updating Dependencies

```python
# Update a dependency
response = requests.put(f"{base_url}/api/v1/dependencies/{dependency_id}", json={
    "dependency_type": "related_to"
})
updated_dependency = response.json()["dependency"]
```

#### Deleting Dependencies

```python
# Delete a dependency
response = requests.delete(f"{base_url}/api/v1/dependencies/{dependency_id}")
success = response.json()["success"]
```

### Dependency Types

Metis supports the following dependency types:

- **BLOCKS**: The source task blocks the target task
- **DEPENDS_ON**: The source task depends on the target task
- **RELATED_TO**: The tasks are related but don't have a blocking relationship

### Cycle Detection

Metis automatically detects circular dependencies when you try to create a dependency that would form a cycle. For example, if:

- Task A depends on Task B
- Task B depends on Task C

Then creating a dependency where Task C depends on Task A would create a cycle, which is not allowed. Metis will reject the request and return an error.

## Subtasks

Complex tasks can be broken down into smaller subtasks for better tracking and progress reporting.

### Adding Subtasks

```python
# Add a subtask to a task
response = requests.post(f"{base_url}/api/v1/tasks/{task_id}/subtasks", json={
    "title": "Research authentication libraries",
    "description": "Identify and evaluate authentication libraries",
    "status": "pending"
})
subtask_id = response.json()["subtask"]["id"]
```

### Managing Subtasks

#### Listing Subtasks

```python
# Get subtasks for a task
response = requests.get(f"{base_url}/api/v1/tasks/{task_id}/subtasks")
subtasks = response.json()["subtasks"]
```

#### Updating Subtasks

```python
# Update a subtask
response = requests.put(f"{base_url}/api/v1/tasks/{task_id}/subtasks/{subtask_id}", json={
    "status": "done"
})
updated_subtask = response.json()["subtask"]
```

#### Deleting Subtasks

```python
# Delete a subtask
response = requests.delete(f"{base_url}/api/v1/tasks/{task_id}/subtasks/{subtask_id}")
success = response.json()["success"]
```

## Complexity Analysis

Metis provides tools for analyzing and scoring the complexity of tasks, helping teams better understand task difficulty and estimate effort.

### Analyzing Task Complexity

```python
# Analyze task complexity
response = requests.post(f"{base_url}/api/v1/tasks/{task_id}/complexity/analyze")
complexity = response.json()["complexity"]
```

### Complexity Factors

Complexity analysis considers several factors:

- **Dependencies**: Number and nature of dependencies
- **Description Length**: Longer descriptions often indicate more complex tasks
- **Subtasks**: Number of subtasks
- **Tags**: Certain tags may indicate higher complexity
- **Priority**: Higher priority tasks are often more complex

### Complexity Levels

Tasks are assigned one of the following complexity levels:

- **TRIVIAL**: Very simple tasks
- **SIMPLE**: Straightforward tasks with minimal complexity
- **MODERATE**: Average complexity tasks
- **COMPLEX**: Difficult tasks with significant complexity
- **VERY_COMPLEX**: Extremely complex tasks requiring significant effort

## Real-time Updates

Metis provides WebSocket support for real-time updates, allowing applications to receive notifications when tasks or dependencies change.

### Connecting to WebSocket

```javascript
// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8011/ws");

// Register client
ws.onopen = () => {
  ws.send(JSON.stringify({
    client_id: "client_123",
    subscribe_to: ["task_created", "task_updated", "task_deleted"]
  }));
};

// Handle incoming messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === "registration_success") {
    console.log("Successfully registered with WebSocket");
  } else if (data.type === "task_created") {
    console.log("New task created:", data.data);
  } else if (data.type === "task_updated") {
    console.log("Task updated:", data.data);
  } else if (data.type === "task_deleted") {
    console.log("Task deleted:", data.data);
  }
};

// Keep connection alive
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "ping", data: {} }));
  }
}, 30000); // Every 30 seconds
```

### WebSocket Events

You can subscribe to the following event types:

- `task_created`: Triggered when a new task is created
- `task_updated`: Triggered when a task is updated
- `task_deleted`: Triggered when a task is deleted
- `dependency_created`: Triggered when a new dependency is created
- `dependency_updated`: Triggered when a dependency is updated
- `dependency_deleted`: Triggered when a dependency is deleted
- `subtask_created`: Triggered when a subtask is created
- `subtask_updated`: Triggered when a subtask is updated
- `subtask_deleted`: Triggered when a subtask is deleted

## Integration with Telos

Metis integrates with Telos to import requirements as tasks, providing traceability between requirements and their implementation.

### Searching for Requirements

```python
# Search for requirements in Telos
response = requests.get(f"{base_url}/api/v1/telos/requirements", params={
    "status": "approved",
    "type": "functional"
})
requirements = response.json()["requirements"]
```

### Importing Requirements as Tasks

```python
# Import a requirement as a task
response = requests.post(f"{base_url}/api/v1/telos/requirements/{requirement_id}/import")
task = response.json()["task"]
```

### Adding Requirement References

```python
# Add a requirement reference to an existing task
response = requests.post(f"{base_url}/api/v1/tasks/{task_id}/telos/requirements/{requirement_id}")
success = response.json()["success"]
```

## Integration with Prometheus

Metis provides task information to Prometheus for planning and scheduling.

### Task Information for Planning

Prometheus can access task data from Metis for planning purposes. This integration allows Prometheus to consider task dependencies, complexity, and priorities when creating plans.

### Task Updates from Prometheus

Prometheus can update task status based on planning decisions, creating a bidirectional flow of information between task management and planning systems.

## Organizing Tasks

### Using Tags

Tags provide a flexible way to categorize tasks:

```python
# Update task with tags
response = requests.put(f"{base_url}/api/v1/tasks/{task_id}", json={
    "tags": ["frontend", "ui", "responsive"]
})
```

### Filtering by Tags

```python
# Filter tasks by tag
response = requests.get(f"{base_url}/api/v1/tasks", params={
    "tag": "frontend"
})
frontend_tasks = response.json()["tasks"]
```

## Client Libraries

### Python Client Example

Here's a simple Python client for Metis:

```python
import aiohttp
import asyncio
import json

class MetisClient:
    def __init__(self, base_url="http://localhost:8011"):
        self.base_url = base_url
        self._session = None
    
    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def list_tasks(self, **filters):
        session = await self._get_session()
        async with session.get(f"{self.base_url}/api/v1/tasks", params=filters) as response:
            return await response.json()
    
    async def get_task(self, task_id):
        session = await self._get_session()
        async with session.get(f"{self.base_url}/api/v1/tasks/{task_id}") as response:
            return await response.json()
    
    async def create_task(self, task_data):
        session = await self._get_session()
        async with session.post(f"{self.base_url}/api/v1/tasks", json=task_data) as response:
            return await response.json()
    
    async def update_task(self, task_id, task_updates):
        session = await self._get_session()
        async with session.put(f"{self.base_url}/api/v1/tasks/{task_id}", json=task_updates) as response:
            return await response.json()
    
    async def delete_task(self, task_id):
        session = await self._get_session()
        async with session.delete(f"{self.base_url}/api/v1/tasks/{task_id}") as response:
            return await response.json()
    
    # WebSocket connection for real-time updates
    async def connect_websocket(self, event_handler, subscribe_to=None):
        if subscribe_to is None:
            subscribe_to = ["task_created", "task_updated", "task_deleted"]
        
        session = await self._get_session()
        async with session.ws_connect(f"{self.base_url}/ws") as ws:
            # Register with the server
            await ws.send_json({
                "client_id": f"client-{id(self)}",
                "subscribe_to": subscribe_to
            })
            
            # Wait for registration confirmation
            registration = await ws.receive_json()
            if registration.get("type") != "registration_success":
                raise ValueError(f"Failed to register with WebSocket: {registration}")
            
            # Handle messages
            try:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        await event_handler(data.get("type"), data.get("data"))
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
            finally:
                if not ws.closed:
                    await ws.close()
```

### JavaScript Client Example

Here's a simple JavaScript client for Metis:

```javascript
class MetisClient {
  constructor(baseUrl = 'http://localhost:8011') {
    this.baseUrl = baseUrl;
  }
  
  async listTasks(filters = {}) {
    const queryParams = new URLSearchParams(filters);
    const response = await fetch(`${this.baseUrl}/api/v1/tasks?${queryParams}`);
    return response.json();
  }
  
  async getTask(taskId) {
    const response = await fetch(`${this.baseUrl}/api/v1/tasks/${taskId}`);
    return response.json();
  }
  
  async createTask(taskData) {
    const response = await fetch(`${this.baseUrl}/api/v1/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(taskData)
    });
    return response.json();
  }
  
  async updateTask(taskId, taskUpdates) {
    const response = await fetch(`${this.baseUrl}/api/v1/tasks/${taskId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(taskUpdates)
    });
    return response.json();
  }
  
  async deleteTask(taskId) {
    const response = await fetch(`${this.baseUrl}/api/v1/tasks/${taskId}`, {
      method: 'DELETE'
    });
    return response.json();
  }
  
  // WebSocket connection for real-time updates
  connectWebSocket(eventHandler, subscribeTo = ['task_created', 'task_updated', 'task_deleted']) {
    const ws = new WebSocket(`ws://${this.baseUrl.replace('http://', '')}/ws`);
    
    ws.onopen = () => {
      // Register with the server
      ws.send(JSON.stringify({
        client_id: `client-${Date.now()}`,
        subscribe_to: subscribeTo
      }));
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      eventHandler(data.type, data.data);
    };
    
    // Handle ping/pong for keep-alive
    setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);
    
    return ws;
  }
}
```

## Best Practices

### Writing Good Task Descriptions

1. **Be Specific**: Clearly state what needs to be done
2. **Include Context**: Provide background information
3. **Define Success Criteria**: Specify when the task is considered complete
4. **Add References**: Link to relevant resources or documentation
5. **Break Down Complex Tasks**: Use subtasks for complex work

### Managing Dependencies

1. **Identify Critical Dependencies**: Focus on dependencies that block progress
2. **Avoid Circular Dependencies**: Ensure tasks don't depend on each other
3. **Keep Dependencies Up to Date**: Update as work progresses
4. **Use Appropriate Dependency Types**: Choose the right type for the relationship

### Task Status Management

1. **Update Status Regularly**: Keep task status current
2. **Follow Status Transitions**: Use the defined workflow
3. **Use Blocked Status Appropriately**: Mark tasks as blocked when they can't proceed
4. **Complete Subtasks**: Update subtask status as work progresses

### Using Complexity Analysis

1. **Review Complexity Scores**: Understand the factors contributing to complexity
2. **Plan Based on Complexity**: Allocate resources based on task complexity
3. **Break Down Complex Tasks**: Divide very complex tasks into smaller ones
4. **Balance Workload**: Distribute complex tasks across team members

## Troubleshooting

### Common Issues

1. **Connection Problems**:
   - Check that the Metis server is running
   - Verify the port is correct (default: 8011)
   - Ensure network connectivity

2. **Permission Errors**:
   - Verify you have the correct permissions
   - Check that you're authenticated if authentication is enabled

3. **Dependency Issues**:
   - Check for circular dependencies
   - Ensure the referenced tasks exist

4. **WebSocket Connection Issues**:
   - Verify WebSocket URL
   - Check client registration message format
   - Implement reconnection logic

### Debugging

1. **Enable Debug Logging**:
   ```bash
   # Run with debug logging
   METIS_LOG_LEVEL=DEBUG python -m metis
   ```

2. **Check API Responses**:
   - Examine response status codes and error messages
   - Use request headers like `X-Request-ID` for tracking

3. **WebSocket Debugging**:
   - Use browser developer tools to monitor WebSocket traffic
   - Look for connection issues and message formatting problems

4. **Integration Troubleshooting**:
   - Verify Hermes registration
   - Check Telos availability for requirement imports
   - Confirm Prometheus connectivity for planning integration

## API Reference Summary

Here's a quick reference of key Metis API endpoints:

### Task Endpoints

```
GET    /api/v1/tasks                            # List tasks
POST   /api/v1/tasks                            # Create task
GET    /api/v1/tasks/{task_id}                  # Get task
PUT    /api/v1/tasks/{task_id}                  # Update task
DELETE /api/v1/tasks/{task_id}                  # Delete task
GET    /api/v1/tasks/{task_id}/subtasks         # List subtasks
POST   /api/v1/tasks/{task_id}/subtasks         # Create subtask
PUT    /api/v1/tasks/{task_id}/subtasks/{id}    # Update subtask
DELETE /api/v1/tasks/{task_id}/subtasks/{id}    # Delete subtask
```

### Dependency Endpoints

```
GET    /api/v1/dependencies                    # List dependencies
POST   /api/v1/dependencies                    # Create dependency
GET    /api/v1/dependencies/{dependency_id}    # Get dependency
PUT    /api/v1/dependencies/{dependency_id}    # Update dependency
DELETE /api/v1/dependencies/{dependency_id}    # Delete dependency
GET    /api/v1/tasks/{task_id}/dependencies   # Get task dependencies
```

### Complexity Endpoints

```
GET    /api/v1/tasks/{task_id}/complexity         # Get complexity
POST   /api/v1/tasks/{task_id}/complexity/analyze # Analyze complexity
```

### Telos Integration Endpoints

```
GET    /api/v1/telos/requirements                               # Search requirements
POST   /api/v1/telos/requirements/{requirement_id}/import       # Import requirement
POST   /api/v1/tasks/{task_id}/telos/requirements/{requirement_id} # Add requirement ref
```

## Conclusion

Metis provides a comprehensive system for managing tasks throughout the project lifecycle. By following this guide, you should be able to effectively create, organize, track, and analyze tasks, ensuring they serve as a reliable foundation for your project's success.

For more detailed information, refer to the [Technical Documentation](./TECHNICAL_DOCUMENTATION.md), [API Reference](./API_REFERENCE.md), and [Integration Guide](./INTEGRATION_GUIDE.md).