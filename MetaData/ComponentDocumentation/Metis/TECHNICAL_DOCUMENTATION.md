# Metis Technical Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Core Domain Model](#core-domain-model)
4. [API Reference](#api-reference)
5. [Interfaces](#interfaces)
6. [Integration Points](#integration-points)
7. [WebSocket Communication](#websocket-communication)
8. [Technical Implementation Details](#technical-implementation-details)
9. [Security Considerations](#security-considerations)
10. [Performance Optimizations](#performance-optimizations)
11. [Future Improvements](#future-improvements)

## Introduction

Metis is the task management system for the Tekton ecosystem. It provides a robust platform for creating, organizing, and tracking tasks with support for dependencies, complexity scoring, and real-time updates.

Key features of Metis include:

- **Task Management**: Create, update, organize, and track project tasks
- **Dependency Management**: Support for task dependencies with cycle detection
- **Complexity Analysis**: Automatic complexity scoring for tasks
- **Subtask Support**: Break down complex tasks into manageable subtasks
- **Single Port Architecture**: Consolidated HTTP, WebSocket, and Event communication
- **Real-time Updates**: WebSocket-based updates for collaborative task editing
- **Integration with Telos**: Import requirements from Telos as tasks
- **Integration with Prometheus**: Provide task information for planning
- **REST API**: Full-featured API for programmatic integration

## Architecture Overview

Metis follows a layered architecture pattern that separates concerns and allows for modularity and extensibility:

1. **Core Domain Layer**:
   - Implements the core domain model of task management
   - Contains the business logic for tasks, dependencies, and complexity
   - Manages the persistence and retrieval of task data

2. **API Layer**:
   - Exposes RESTful endpoints for CRUD operations
   - Implements the Single Port Architecture pattern for HTTP, WebSocket, and Event communication
   - Handles authentication, authorization, and validation

3. **Integration Layer**:
   - Connects with other Tekton components like Telos, Prometheus, and Hermes
   - Provides adapters for external systems integration

4. **Client Layer**:
   - Offers a client library for programmatic interaction with Metis
   - Includes WebSocket client for real-time updates

### Single Port Architecture

Metis follows the Tekton Single Port Architecture pattern:
- **Port 8011**: All Metis communications (HTTP, WebSocket, Events)
- **Path-based Routing**:
  - `/api/v1/*`: RESTful API endpoints
  - `/ws`: WebSocket endpoint for real-time updates

## Core Domain Model

### Task

The Task entity represents a discrete unit of work:

```python
class Task:
    """A task represents a unit of work to be done."""
    
    def __init__(
        self,
        title: str,
        description: str = "",
        task_id: Optional[str] = None,
        status: Union[str, TaskStatus] = TaskStatus.PENDING,
        priority: Union[str, Priority] = Priority.MEDIUM,
        assignee: Optional[str] = None,
        created_by: Optional[str] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        subtasks: Optional[List[Dict[str, Any]]] = None,
        requirement_refs: Optional[List[Dict[str, Any]]] = None,
        complexity: Optional[Union[Dict[str, Any], ComplexityScore]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a task."""
        # Implementation
```

### Dependency

The Dependency entity represents a relationship between tasks:

```python
class Dependency:
    """A dependency between two tasks."""
    
    def __init__(
        self,
        source_task_id: str,
        target_task_id: str,
        dependency_id: Optional[str] = None,
        dependency_type: Union[str, DependencyType] = DependencyType.BLOCKS,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a dependency."""
        # Implementation
```

### ComplexityScore

The ComplexityScore entity represents the difficulty level of a task:

```python
class ComplexityScore:
    """A score representing the complexity of a task."""
    
    def __init__(
        self,
        factors: Optional[Dict[str, float]] = None,
        overall_score: Optional[float] = None,
        level: Optional[Union[str, ComplexityLevel]] = None
    ):
        """Initialize a complexity score."""
        # Implementation
```

### Subtask

Subtasks are represented as part of the Task entity:

```python
# Subtask structure
subtask = {
    "id": "unique_subtask_id",
    "title": "Subtask title",
    "description": "Subtask description",
    "status": TaskStatus.PENDING.value,  # or other status
    "created_at": timestamp,
    "updated_at": timestamp
}
```

### TaskManager

The TaskManager class is responsible for managing tasks and dependencies:

```python
class TaskManager:
    """Manager for tasks and dependencies."""
    
    def __init__(self, storage: Optional[Any] = None):
        """Initialize the task manager with optional storage."""
        self.storage = storage or InMemoryStorage()
        self._event_handlers = {}
        
    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        """Create a new task."""
        # Implementation
        
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        # Implementation
        
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        """Update a task."""
        # Implementation
        
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        # Implementation
        
    async def list_tasks(self, **filters) -> Tuple[List[Task], int]:
        """List tasks matching the filters."""
        # Implementation
        
    async def create_dependency(self, dependency_data: Dict[str, Any]) -> Dependency:
        """Create a new dependency between tasks."""
        # Implementation
        
    async def delete_dependency(self, dependency_id: str) -> bool:
        """Delete a dependency."""
        # Implementation
        
    async def list_dependencies(self, **filters) -> Tuple[List[Dependency], int]:
        """List dependencies matching the filters."""
        # Implementation
        
    async def analyze_complexity(self, task_id: str) -> ComplexityScore:
        """Analyze the complexity of a task."""
        # Implementation
        
    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Add an event handler for the specified event type."""
        # Implementation
        
    def remove_event_handler(self, event_type: str, handler: Callable) -> bool:
        """Remove an event handler."""
        # Implementation
        
    def _emit_event(self, event_type: str, data: Any) -> None:
        """Emit an event to all registered handlers."""
        # Implementation
        
    async def save(self) -> bool:
        """Save the current state to persistent storage."""
        # Implementation
        
    async def load(self) -> bool:
        """Load state from persistent storage."""
        # Implementation
```

## API Reference

### Task Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/api/v1/tasks` | List all tasks |
| POST | `/api/v1/tasks` | Create a new task |
| GET | `/api/v1/tasks/{task_id}` | Get a specific task |
| PUT | `/api/v1/tasks/{task_id}` | Update a task |
| DELETE | `/api/v1/tasks/{task_id}` | Delete a task |
| GET | `/api/v1/tasks/{task_id}/subtasks` | Get subtasks for a task |
| POST | `/api/v1/tasks/{task_id}/subtasks` | Add a subtask |
| PUT | `/api/v1/tasks/{task_id}/subtasks/{subtask_id}` | Update a subtask |
| DELETE | `/api/v1/tasks/{task_id}/subtasks/{subtask_id}` | Delete a subtask |

### Dependency Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/api/v1/dependencies` | List all dependencies |
| POST | `/api/v1/dependencies` | Create a new dependency |
| GET | `/api/v1/dependencies/{dependency_id}` | Get a specific dependency |
| PUT | `/api/v1/dependencies/{dependency_id}` | Update a dependency |
| DELETE | `/api/v1/dependencies/{dependency_id}` | Delete a dependency |
| GET | `/api/v1/tasks/{task_id}/dependencies` | Get dependencies for a task |

### Complexity Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/api/v1/tasks/{task_id}/complexity` | Get complexity for a task |
| POST | `/api/v1/tasks/{task_id}/complexity/analyze` | Analyze task complexity |

### Telos Integration Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/api/v1/telos/requirements` | Search for requirements in Telos |
| POST | `/api/v1/telos/requirements/{requirement_id}/import` | Import a requirement as a task |
| POST | `/api/v1/tasks/{task_id}/telos/requirements/{requirement_id}` | Add a requirement reference to a task |

## Interfaces

### HTTP Interface

Metis provides a RESTful HTTP API for synchronous operations. The API follows standard REST conventions and returns JSON responses.

Example request to create a task:

```http
POST /api/v1/tasks
Content-Type: application/json

{
    "title": "Implement User Authentication",
    "description": "Add user authentication to the application",
    "status": "pending",
    "priority": "high",
    "due_date": "2025-06-01T00:00:00Z",
    "tags": ["authentication", "security"]
}
```

Response:

```json
{
    "success": true,
    "task": {
        "id": "task_id",
        "title": "Implement User Authentication",
        "description": "Add user authentication to the application",
        "status": "pending",
        "priority": "high",
        "due_date": "2025-06-01T00:00:00Z",
        "tags": ["authentication", "security"],
        "created_at": 1682456789.123,
        "updated_at": 1682456789.123
    }
}
```

### WebSocket Interface

Metis provides a WebSocket interface for real-time updates:

```javascript
const ws = new WebSocket("ws://localhost:8011/ws");

// Register client
ws.send(JSON.stringify({
    "client_id": "client_123",
    "subscribe_to": ["task_created", "task_updated", "task_deleted"]
}));

// Handle incoming messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Received:", data);
};
```

## Integration Points

### Hermes Integration

Metis integrates with the Hermes service registry for service discovery:

```python
async def register_with_hermes(self, hermes_url=None) -> bool:
    """Register with the Hermes service registry."""
    try:
        self.hermes_client = HermesClient(
            base_url=hermes_url or f"http://localhost:{self.config.HERMES_PORT}",
            service_name="Metis",
            service_version="0.1.0",
            capabilities=["task_management", "dependency_management", "task_tracking", "websocket_updates"]
        )
        
        # Register with Hermes
        success = await self.hermes_client.register()
        if success:
            # Start heartbeat task
            asyncio.create_task(self.hermes_client.heartbeat_task())
        return success
    except Exception as e:
        logger.error(f"Error registering with Hermes: {e}")
        return False
```

### Telos Integration

Metis integrates with Telos for importing requirements as tasks:

```python
class TelosIntegration:
    """Integration with Telos for requirement management."""
    
    def __init__(self, task_manager: TaskManager):
        """Initialize Telos integration."""
        self.task_manager = task_manager
        self.telos_client = None
        
    async def initialize(self, telos_url=None) -> bool:
        """Initialize the Telos client."""
        try:
            self.telos_client = TelosClient(
                base_url=telos_url or f"http://localhost:{self.config.TELOS_PORT}"
            )
            return True
        except Exception as e:
            logger.error(f"Error initializing Telos client: {e}")
            return False
        
    async def import_requirement_as_task(self, requirement_id: str) -> Optional[Task]:
        """Import a requirement from Telos as a task."""
        if not self.telos_client:
            logger.error("Telos client not initialized")
            return None
        
        try:
            # Get requirement from Telos
            requirement = await self.telos_client.get_requirement(requirement_id)
            if not requirement:
                logger.error(f"Requirement {requirement_id} not found in Telos")
                return None
            
            # Create task from requirement
            task_data = {
                "title": requirement.get("title", "Untitled Requirement"),
                "description": requirement.get("description", ""),
                "status": TaskStatus.PENDING.value,
                "priority": self._map_priority(requirement.get("priority", "medium")),
                "tags": ["telos", "requirement", requirement.get("type", "unknown")],
                "requirement_refs": [{
                    "requirement_id": requirement_id,
                    "project_id": requirement.get("project_id"),
                    "title": requirement.get("title"),
                    "url": f"http://localhost:{self.config.TELOS_PORT}/api/projects/{requirement.get('project_id')}/requirements/{requirement_id}"
                }]
            }
            
            # Create the task
            task = await self.task_manager.create_task(task_data)
            return task
        except Exception as e:
            logger.error(f"Error importing requirement {requirement_id}: {e}")
            return None
```

### Prometheus Integration

Metis provides task information to Prometheus for planning:

```python
async def provide_tasks_for_planning(self) -> Dict[str, Any]:
    """Provide task information to Prometheus for planning."""
    # Get pending tasks
    tasks, total = await self.task_manager.list_tasks(status=TaskStatus.PENDING.value)
    
    # Get dependencies for these tasks
    dependencies = []
    for task in tasks:
        task_dependencies = await self.task_manager.list_dependencies(task_id=task.id)
        dependencies.extend(task_dependencies)
    
    # Calculate critical path
    critical_path = self.dependency_resolver.get_critical_path(tasks, dependencies)
    
    return {
        "tasks": [task.to_dict() for task in tasks],
        "dependencies": [dep.to_dict() for dep in dependencies],
        "critical_path": critical_path
    }
```

## WebSocket Communication

Metis implements a WebSocket server for real-time updates:

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    
    # Generate a unique client ID
    client_id = f"client_{int(time.time() * 1000)}"
    subscriptions = []
    
    try:
        # Wait for the initial registration message
        registration = await websocket.receive_json()
        
        # Extract client ID and subscriptions
        client_id = registration.get("client_id", client_id)
        subscriptions = registration.get("subscribe_to", ["task_created", "task_updated", "task_deleted"])
        
        # Add client to active clients
        active_clients[client_id] = {
            "websocket": websocket,
            "subscriptions": subscriptions
        }
        
        # Send registration confirmation
        await websocket.send_json({
            "type": "registration_success",
            "client_id": client_id,
            "subscriptions": subscriptions
        })
        
        # Process incoming messages
        while True:
            # Wait for a message
            message = await websocket.receive_json()
            
            # Process message based on type
            message_type = message.get("type")
            if message_type == "ping":
                # Respond to ping with pong
                await websocket.send_json({"type": "pong", "data": {}})
            elif message_type == "subscribe":
                # Update subscriptions
                new_subscriptions = message.get("subscribe_to", [])
                active_clients[client_id]["subscriptions"] = new_subscriptions
                await websocket.send_json({
                    "type": "subscription_updated",
                    "subscriptions": new_subscriptions
                })
            # Other message types can be handled here
    
    except WebSocketDisconnect:
        # Client disconnected, remove from active clients
        if client_id in active_clients:
            del active_clients[client_id]
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        # Remove client on error
        if client_id in active_clients:
            del active_clients[client_id]
```

### WebSocket Message Types

| Message Type | Direction | Description |
| ------------ | --------- | ----------- |
| `registration_success` | Server → Client | Confirms client registration |
| `task_created` | Server → Client | Notification of a new task |
| `task_updated` | Server → Client | Notification of task updates |
| `task_deleted` | Server → Client | Notification of task deletion |
| `dependency_created` | Server → Client | Notification of a new dependency |
| `dependency_updated` | Server → Client | Notification of dependency updates |
| `dependency_deleted` | Server → Client | Notification of dependency deletion |
| `ping` | Client → Server | Keep-alive ping message |
| `pong` | Server → Client | Keep-alive pong response |
| `subscribe` | Client → Server | Update subscription preferences |
| `subscription_updated` | Server → Client | Confirms subscription changes |
| `error` | Server → Client | Error message |

## Technical Implementation Details

### Storage Layer

Metis uses an in-memory storage layer with persistence:

```python
class InMemoryStorage:
    """In-memory storage for tasks and dependencies."""
    
    def __init__(self, file_path: Optional[str] = None):
        """Initialize the in-memory storage."""
        self._tasks: Dict[str, Task] = {}
        self._dependencies: Dict[str, Dependency] = {}
        self._file_path = file_path
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        
    async def create_task(self, task: Task) -> Task:
        """Create a task."""
        with self._lock:
            if task.id in self._tasks:
                raise ValueError(f"Task with ID {task.id} already exists")
            self._tasks[task.id] = task
            return task
        
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        with self._lock:
            return self._tasks.get(task_id)
        
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        """Update a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            
            for key, value in updates.items():
                setattr(task, key, value)
            
            task.updated_at = time.time()
            self._tasks[task_id] = task
            return task
        
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        with self._lock:
            if task_id not in self._tasks:
                return False
            del self._tasks[task_id]
            
            # Delete associated dependencies
            dependencies_to_delete = []
            for dep_id, dep in self._dependencies.items():
                if dep.source_task_id == task_id or dep.target_task_id == task_id:
                    dependencies_to_delete.append(dep_id)
            
            for dep_id in dependencies_to_delete:
                del self._dependencies[dep_id]
            
            return True
        
    async def list_tasks(self, **filters) -> Tuple[List[Task], int]:
        """List tasks matching the filters."""
        with self._lock:
            tasks = list(self._tasks.values())
            
            # Apply filters
            if filters:
                filtered_tasks = []
                for task in tasks:
                    match = True
                    for key, value in filters.items():
                        if hasattr(task, key):
                            attr_value = getattr(task, key)
                            if isinstance(attr_value, (TaskStatus, Priority)):
                                if attr_value.value != value:
                                    match = False
                                    break
                            elif attr_value != value:
                                match = False
                                break
                    if match:
                        filtered_tasks.append(task)
                tasks = filtered_tasks
            
            # Sort by created_at (newest first)
            tasks.sort(key=lambda t: t.created_at, reverse=True)
            
            return tasks, len(tasks)
        
    async def create_dependency(self, dependency: Dependency) -> Dependency:
        """Create a dependency."""
        with self._lock:
            if dependency.id in self._dependencies:
                raise ValueError(f"Dependency with ID {dependency.id} already exists")
            
            # Ensure tasks exist
            if dependency.source_task_id not in self._tasks:
                raise ValueError(f"Source task {dependency.source_task_id} does not exist")
            if dependency.target_task_id not in self._tasks:
                raise ValueError(f"Target task {dependency.target_task_id} does not exist")
            
            self._dependencies[dependency.id] = dependency
            return dependency
        
    async def save(self) -> bool:
        """Save the current state to a file."""
        if not self._file_path:
            return False
        
        try:
            with self._lock:
                data = {
                    "tasks": [task.to_dict() for task in self._tasks.values()],
                    "dependencies": [dep.to_dict() for dep in self._dependencies.values()]
                }
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
                
                # Write to file
                with open(self._file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return True
        except Exception as e:
            logger.error(f"Error saving state: {e}")
            return False
        
    async def load(self) -> bool:
        """Load state from a file."""
        if not self._file_path or not os.path.exists(self._file_path):
            return False
        
        try:
            with open(self._file_path, 'r') as f:
                data = json.load(f)
            
            with self._lock:
                # Clear current state
                self._tasks.clear()
                self._dependencies.clear()
                
                # Load tasks
                for task_data in data.get("tasks", []):
                    task = Task.from_dict(task_data)
                    self._tasks[task.id] = task
                
                # Load dependencies
                for dep_data in data.get("dependencies", []):
                    dep = Dependency.from_dict(dep_data)
                    self._dependencies[dep.id] = dep
                
                return True
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return False
```

### API Implementation

Metis uses FastAPI for implementing the RESTful API:

```python
# Initialize FastAPI app
app = FastAPI(
    title="Metis API",
    description="Task Management System for Tekton",
    version="0.1.0",
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection for controllers
def get_task_controller() -> TaskController:
    return task_controller

def get_dependency_controller() -> DependencyController:
    return dependency_controller

# Task routes
@app.get("/api/v1/tasks", response_model=TaskListResponse)
async def list_tasks(
    controller: TaskController = Depends(get_task_controller),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """List tasks with optional filters."""
    filters = {}
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority
    if assignee:
        filters["assignee"] = assignee
    
    tasks, total = await controller.list_tasks(
        filters=filters,
        tag=tag,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "tasks": tasks,
        "total": total,
        "page": page,
        "limit": limit
    }

@app.post("/api/v1/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_request: TaskCreateRequest,
    controller: TaskController = Depends(get_task_controller)
):
    """Create a new task."""
    task = await controller.create_task(task_request.dict())
    return {"success": True, "task": task}

@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    controller: TaskController = Depends(get_task_controller)
):
    """Get a task by ID."""
    task = await controller.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"success": True, "task": task}

@app.put("/api/v1/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    updates: TaskUpdateRequest,
    controller: TaskController = Depends(get_task_controller)
):
    """Update a task."""
    task = await controller.update_task(task_id, updates.dict(exclude_unset=True))
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"success": True, "task": task}

@app.delete("/api/v1/tasks/{task_id}", response_model=GenericResponse)
async def delete_task(
    task_id: str,
    controller: TaskController = Depends(get_task_controller)
):
    """Delete a task."""
    success = await controller.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"success": True}
```

### Validation Logic

Metis implements validation for status transitions and circular dependencies:

```python
def validate_status_transition(current_status: TaskStatus, new_status: TaskStatus) -> bool:
    """Validate a task status transition."""
    # Define allowed transitions
    allowed_transitions = {
        TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
        TaskStatus.IN_PROGRESS: [TaskStatus.REVIEW, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
        TaskStatus.REVIEW: [TaskStatus.IN_PROGRESS, TaskStatus.DONE, TaskStatus.CANCELLED],
        TaskStatus.BLOCKED: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
        TaskStatus.DONE: [TaskStatus.IN_PROGRESS],  # Allow reopening
        TaskStatus.CANCELLED: [TaskStatus.PENDING]  # Allow reactivation
    }
    
    # Check if transition is allowed
    return new_status in allowed_transitions.get(current_status, [])

def detect_dependency_cycle(dependencies: List[Dependency], new_dependency: Dependency) -> bool:
    """Detect if adding a new dependency would create a cycle."""
    # Build dependency graph
    graph = {}
    for dep in dependencies:
        if dep.source_task_id not in graph:
            graph[dep.source_task_id] = set()
        graph[dep.source_task_id].add(dep.target_task_id)
    
    # Add the new dependency
    if new_dependency.source_task_id not in graph:
        graph[new_dependency.source_task_id] = set()
    graph[new_dependency.source_task_id].add(new_dependency.target_task_id)
    
    # DFS to detect cycles
    visited = set()
    path = set()
    
    def dfs(node):
        # Mark node as visited and add to current path
        visited.add(node)
        path.add(node)
        
        # Visit neighbors
        neighbors = graph.get(node, set())
        for neighbor in neighbors:
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in path:
                # Cycle detected
                return True
        
        # Remove node from current path
        path.remove(node)
        return False
    
    # Check for cycles
    for node in graph:
        if node not in visited:
            if dfs(node):
                return True
    
    return False
```

## Security Considerations

While the current implementation focuses on functionality, several security considerations should be addressed in a production environment:

1. **Authentication and Authorization**:
   - Implement user authentication for API access
   - Add role-based access control for task operations
   - Secure WebSocket connections with authentication tokens

2. **Input Validation**:
   - Validate all user input to prevent injection attacks
   - Sanitize inputs for XSS prevention in web components

3. **API Security**:
   - Implement rate limiting to prevent abuse
   - Add CORS restrictions for production environments
   - Use HTTPS for all communications

4. **Data Protection**:
   - Encrypt sensitive task data at rest
   - Implement audit logging for all operations
   - Add data backup and recovery mechanisms

## Performance Optimizations

Current performance optimizations include:

1. **WebSocket for Real-time Updates**:
   - Reduces polling overhead for collaborative editing
   - Decreases network traffic compared to HTTP polling

2. **In-Memory Storage with Persistence**:
   - Fast in-memory operations with background persistence
   - Reduces disk I/O operations

3. **Dependency Graph Optimization**:
   - Efficient cycle detection algorithm
   - Incremental dependency graph updates

Future optimizations could include:

1. **Database Integration**:
   - Replace file-based storage with a database for better scalability
   - Implement query optimization for large task sets

2. **Caching Layer**:
   - Add a Redis caching layer for frequently accessed tasks
   - Implement cache invalidation for updates

3. **Batch Operations**:
   - Support bulk create/update/delete operations
   - Optimize for large-scale task management

## Future Improvements

Potential future improvements for Metis include:

1. **Enhanced Visualization**:
   - Gantt chart visualization for tasks and dependencies
   - Network graph for dependency relationships
   - Burndown charts for progress tracking

2. **Extended LLM Integration**:
   - Task summarization and analysis
   - Automatic complexity estimation
   - Dependency suggestion based on task descriptions

3. **Advanced Planning Integration**:
   - Deeper integration with Prometheus
   - Resource allocation and scheduling
   - Critical path analysis

4. **UI Enhancements**:
   - Dashboard view for task metrics
   - Drag-and-drop task organization
   - Collaborative editing with presence indicators

5. **Database Integration**:
   - Support for SQL and NoSQL databases
   - Query optimization for large task sets
   - Data migration utilities