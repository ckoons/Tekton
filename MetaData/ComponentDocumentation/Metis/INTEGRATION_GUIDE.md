# Metis Integration Guide

This document provides guidance on integrating Metis with other Tekton components and external systems.

## Integration with Tekton Components

Metis is designed to work seamlessly with other Tekton components, especially Telos (requirements management) and Prometheus (planning system). This section outlines how to integrate Metis with these components.

### Hermes Integration

Metis integrates with Hermes for service registration and discovery. This allows other Tekton components to discover and communicate with Metis.

Key integration points:
- Metis registers with Hermes at startup
- Metis announces its capabilities to Hermes
- Metis discovers other components through Hermes
- Metis sends periodic heartbeats to maintain registration

Configuration:
- `HERMES_PORT`: Port for the Hermes service (default: 8001)
- Service name: "Metis"
- Capabilities: ["task_management", "dependency_management", "task_tracking", "websocket_updates"]

### Telos Integration

Metis integrates with Telos to import requirements as tasks and to maintain links between tasks and requirements.

Key integration points:
- Import requirements from Telos as tasks
- Reference Telos requirements from tasks
- Search for requirements in Telos

API Endpoints:
- `GET /api/v1/telos/requirements`: Search for requirements in Telos
- `POST /api/v1/telos/requirements/{requirement_id}/import`: Import a requirement as a task
- `POST /api/v1/tasks/{task_id}/telos/requirements/{requirement_id}`: Add a reference to a requirement

Configuration:
- `TELOS_PORT`: Port for the Telos service (default: 8008)

### Prometheus Integration

Metis provides task information to Prometheus for planning and scheduling.

Key integration points:
- Prometheus can query Metis for tasks and their dependencies
- Prometheus can update task status based on planning decisions
- Prometheus can add dependencies between tasks

Configuration:
- `PROMETHEUS_PORT`: Port for the Prometheus service (default: 8006)

## Client Integration

### Python Client

Here's an example of how to integrate with Metis from a Python client:

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
            if registration["type"] != "registration_success":
                raise ValueError(f"Failed to register with WebSocket: {registration}")
            
            # Handle messages
            try:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        await event_handler(data["type"], data["data"])
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
            finally:
                if not ws.closed:
                    await ws.close()

# Example usage
async def example():
    client = MetisClient()
    try:
        # List tasks
        tasks = await client.list_tasks(status="pending")
        print(f"Found {tasks['total']} pending tasks")
        
        # Create a task
        new_task = await client.create_task({
            "title": "Example Task",
            "description": "This is an example task",
            "status": "pending",
            "priority": "medium"
        })
        print(f"Created task: {new_task['id']}")
        
        # Update a task
        updated_task = await client.update_task(new_task["id"], {
            "status": "in_progress",
            "priority": "high"
        })
        print(f"Updated task: {updated_task['id']}")
        
        # Example WebSocket event handler
        async def handle_event(event_type, data):
            print(f"Received event: {event_type}")
            print(f"Data: {data}")
        
        # Connect to WebSocket for real-time updates
        # Uncomment to run WebSocket connection
        # await client.connect_websocket(handle_event)
    finally:
        await client.close()

# Run the example
# asyncio.run(example())
```

### JavaScript Client

Here's an example of how to integrate with Metis from a JavaScript client:

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
        ws.send(JSON.stringify({ type: 'ping', data: {} }));
      }
    }, 30000);
    
    return ws;
  }
}

// Example usage
async function example() {
  const client = new MetisClient();
  
  // List tasks
  const tasks = await client.listTasks({ status: 'pending' });
  console.log(`Found ${tasks.total} pending tasks`);
  
  // Create a task
  const newTask = await client.createTask({
    title: 'Example Task',
    description: 'This is an example task',
    status: 'pending',
    priority: 'medium'
  });
  console.log(`Created task: ${newTask.id}`);
  
  // Update a task
  const updatedTask = await client.updateTask(newTask.id, {
    status: 'in_progress',
    priority: 'high'
  });
  console.log(`Updated task: ${updatedTask.id}`);
  
  // Example WebSocket event handler
  function handleEvent(eventType, data) {
    console.log(`Received event: ${eventType}`);
    console.log(`Data:`, data);
  }
  
  // Connect to WebSocket for real-time updates
  // Uncomment to run WebSocket connection
  // const ws = client.connectWebSocket(handleEvent);
}

// Run the example
// example();
```

## Data Model Integration

When integrating with Metis, it's important to understand the core data models:

### Task

The central entity in Metis is the Task. A Task represents a discrete unit of work and has the following key attributes:

- `id`: Unique identifier
- `title`: Short title of the task
- `description`: Detailed description
- `status`: Current status (pending, in_progress, review, done, blocked, cancelled)
- `priority`: Priority level (high, medium, low)
- `dependencies`: List of tasks this task depends on
- `subtasks`: List of smaller sub-units of work
- `requirement_refs`: References to requirements in Telos

### Dependencies

Dependencies represent relationships between tasks. A Dependency has:

- `source_task_id`: ID of the source task
- `target_task_id`: ID of the target task
- `dependency_type`: Type of dependency (blocks, depends_on, related_to)

### Complexity

Complexity represents the difficulty level of a task. A ComplexityScore has:

- `factors`: List of factors contributing to complexity
- `overall_score`: Calculated complexity score
- `level`: Complexity level (trivial, simple, moderate, complex, very_complex)

## Best Practices

1. **Use WebSockets for Real-time Updates**
   - Connect to the WebSocket endpoint to receive real-time updates
   - Subscribe to relevant event types
   - Handle reconnections and maintain heartbeats

2. **Manage Dependencies Carefully**
   - Avoid creating circular dependencies
   - Use appropriate dependency types
   - Remove dependencies when they're no longer relevant

3. **Link Tasks to Requirements**
   - When a task implements a requirement, create a requirement reference
   - Use appropriate relationship types
   - Keep requirement references up to date

4. **Update Task Status Accurately**
   - Follow the allowed status transitions
   - Update status when work begins or completes
   - Set blocked status when dependencies are blocking progress

5. **Use Subtasks for Complex Work**
   - Break down complex tasks into subtasks
   - Update subtask status independently
   - Track progress at the task level based on subtask completion

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure Metis is running
   - Check that the port is correct
   - Verify network connectivity

2. **Authentication Errors**
   - Ensure authentication tokens are valid
   - Check permissions for the requested operation

3. **Invalid Task Status Transitions**
   - Refer to the allowed transitions in the data model
   - Ensure the current status allows the requested transition

4. **Circular Dependencies**
   - Check for cycles in dependency relationships
   - Resolve by removing or rearranging dependencies

### Debugging

1. **Enable Detailed Logging**
   - Set the log level to DEBUG for more detailed logs
   - Check logs for error messages

2. **Use Health Endpoint**
   - Check the health endpoint to verify service status
   - Verify connectivity with dependent services

3. **Test API Endpoints Directly**
   - Use tools like curl or Postman to test API endpoints
   - Verify request and response formats

4. **Monitor WebSocket Connection**
   - Use browser developer tools to monitor WebSocket traffic
   - Check for connection drops or errors