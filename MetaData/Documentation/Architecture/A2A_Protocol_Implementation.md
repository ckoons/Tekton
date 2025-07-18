# A2A Protocol v0.2.1 Implementation in Tekton

## Overview

The Agent-to-Agent (A2A) Protocol v0.2.1 provides a standardized communication framework for autonomous agents within the Tekton ecosystem. This implementation uses JSON-RPC 2.0 as the message format and supports both request-response and streaming communication patterns.

## Architecture

### Core Components

1. **JSON-RPC Layer** (`/tekton/a2a/jsonrpc.py`)
   - Implements JSON-RPC 2.0 specification
   - Handles single requests, batch requests, and notifications
   - Provides error handling and response formatting

2. **Agent Registry** (`/tekton/a2a/agent.py`)
   - Manages agent registration and lifecycle
   - Tracks agent capabilities and status
   - Implements Agent Card format compliance

3. **Task Manager** (`/tekton/a2a/task.py`)
   - Handles task creation, assignment, and lifecycle
   - Supports state transitions with validation
   - Emits events for streaming (Phase 2)

4. **Discovery Service** (`/tekton/a2a/discovery.py`)
   - Provides agent discovery by capability
   - Supports method-based agent lookup
   - Enables dynamic service discovery

5. **Method Dispatcher** (`/tekton/a2a/methods.py`)
   - Routes JSON-RPC methods to handlers
   - Implements standard A2A methods
   - Extensible for custom methods

6. **Streaming Support** (`/tekton/a2a/streaming/`) - Phase 2
   - Server-Sent Events (SSE) for real-time updates
   - WebSocket support for bidirectional communication
   - Event-driven architecture with filters
   - Subscription management for targeted delivery
   - Channel-based pub/sub system

7. **Conversation Manager** (`/tekton/a2a/conversation.py`) - Phase 3
   - Multi-agent conversation support
   - Turn-taking modes: free-form, round-robin, moderated, consensus
   - Role-based participation: moderator, participant, observer
   - Message threading and conversation context

8. **Task Coordinator** (`/tekton/a2a/task_coordination.py`) - Phase 3
   - Advanced workflow patterns: sequential, parallel, pipeline, fan-out/in
   - Task dependency types: FS, SS, FF, SF
   - Conditional execution with rules engine
   - Automatic task scheduling based on dependencies

9. **Security Layer** (`/tekton/a2a/security.py`) - Phase 3
   - JWT token management with access/refresh tokens
   - Role-based access control with 5 roles
   - 20+ granular permissions
   - HMAC-SHA256 message signing
   - Security middleware for request processing

### Integration with Hermes

Hermes serves as the central hub for A2A communication:

1. **A2A Service** (`/Hermes/hermes/core/a2a_service.py`)
   - Bridges Hermes infrastructure with A2A protocol
   - Manages component lifecycle
   - Handles event routing

2. **A2A Endpoints** (`/Hermes/hermes/api/a2a_endpoints.py`)
   - Provides JSON-RPC endpoint at `/api/a2a/v1/`
   - Well-known agent card at `/.well-known/agent.json`
   - SSE streaming at `/api/a2a/v1/stream/events`

## Implementation Phases

### Phase 1: Core Protocol (Completed)

- ✅ JSON-RPC 2.0 message handling
- ✅ Agent registration and discovery
- ✅ Task lifecycle management
- ✅ Method dispatcher with standard methods
- ✅ Integration with Hermes
- ✅ Comprehensive test suite (96 tests)

### Phase 2: Streaming Support (Completed)

- ✅ SSE implementation for unidirectional streaming
- ✅ Event-driven task updates
- ✅ Subscription management
- ✅ Connection filtering
- ✅ WebSocket support for bidirectional streaming
- ✅ Channel-based pub/sub system

### Phase 3: Advanced Features (Completed)

- ✅ Multi-agent conversation support with turn-taking modes
- ✅ Advanced task coordination with workflows and dependencies
- ✅ JWT-based authentication with access/refresh tokens
- ✅ Role-based access control (RBAC) with 5 roles and 20+ permissions
- ✅ Message signing with HMAC-SHA256
- ✅ Security middleware for automatic auth/authz

## Standard A2A Methods

### Agent Methods
- `agent.register` - Register a new agent
- `agent.unregister` - Remove an agent
- `agent.heartbeat` - Update agent heartbeat
- `agent.update_status` - Change agent status
- `agent.get` - Get agent details
- `agent.list` - List all agents

### Task Methods
- `task.create` - Create a new task
- `task.assign` - Assign task to agent
- `task.update_state` - Update task state
- `task.update_progress` - Update task progress
- `task.complete` - Mark task complete
- `task.fail` - Mark task failed
- `task.cancel` - Cancel a task
- `task.get` - Get task details
- `task.list` - List tasks

### Discovery Methods
- `discovery.query` - Query agents by criteria
- `discovery.find_for_method` - Find agents supporting a method
- `discovery.find_for_capability` - Find agents with capability
- `discovery.capability_map` - Get capability to agents mapping
- `discovery.method_map` - Get method to agents mapping

### Channel Methods (Phase 2)
- `channel.subscribe` - Subscribe to a channel
- `channel.unsubscribe` - Unsubscribe from channel
- `channel.publish` - Publish to channel
- `channel.list` - List available channels
- `channel.subscribers` - Get channel subscribers

### Conversation Methods (Phase 3)
- `conversation.create` - Create multi-agent conversation
- `conversation.join` - Join existing conversation
- `conversation.leave` - Leave conversation
- `conversation.send` - Send message in conversation
- `conversation.list` - List conversations
- `conversation.info` - Get conversation details
- `conversation.request_turn` - Request speaking turn
- `conversation.grant_turn` - Grant turn (moderator only)
- `conversation.end` - End conversation

### Workflow Methods (Phase 3)
- `workflow.create` - Create custom workflow
- `workflow.create_sequential` - Create sequential task chain
- `workflow.create_parallel` - Create parallel execution
- `workflow.create_pipeline` - Create data pipeline
- `workflow.create_fanout` - Create fan-out pattern
- `workflow.start` - Start workflow execution
- `workflow.cancel` - Cancel running workflow
- `workflow.info` - Get workflow status
- `workflow.list` - List workflows
- `workflow.add_task` - Add task dynamically
- `workflow.add_dependency` - Add task dependency

### Authentication Methods (Phase 3)
- `auth.login` - Authenticate and get tokens
- `auth.refresh` - Refresh access token
- `auth.logout` - Revoke tokens
- `auth.verify` - Check authentication status

### Hermes-Specific Methods
- `agent.forward` - Forward request to specific agent

## Testing

### Running Tests

```bash
# Run all A2A tests
python tests/run_a2a_all_tests.py

# Run only unit tests
python tests/run_a2a_all_tests.py -u

# Run only integration tests
python tests/run_a2a_all_tests.py -i

# Run manual streaming test
python tests/manual/test_a2a_streaming.py
```

### Test Coverage

- **Unit Tests**: 165+ tests covering:
  - Core protocol components, JSON-RPC handling
  - SSE and WebSocket streaming
  - Channel-based pub/sub
  - Multi-agent conversations (22 tests)
  - Task coordination and workflows (19 tests)
  - Security and authentication (28 tests)
- **Integration Tests**: Hermes integration, end-to-end flows
- **Manual Tests**: SSE streaming, WebSocket connections, subscription management

## Usage Examples

### Basic Agent Registration

```python
# JSON-RPC request
{
    "jsonrpc": "2.0",
    "method": "agent.register",
    "params": {
        "agent_card": {
            "name": "MyAgent",
            "description": "Example agent",
            "version": "1.0.0",
            "capabilities": ["task_processing"],
            "supported_methods": ["custom.method"],
            "endpoint": "http://localhost:8005/"
        }
    },
    "id": 1
}
```

### Creating and Monitoring a Task with SSE

```python
# Create task
{
    "jsonrpc": "2.0",
    "method": "task.create",
    "params": {
        "name": "Process Data",
        "description": "Process user data",
        "priority": "high"
    },
    "id": 1
}

# Connect to SSE stream
GET /api/a2a/v1/stream/events?task_id=task-123

# Receive real-time updates
data: {"type": "task.state_changed", "task_id": "task-123", ...}
data: {"type": "task.progress", "task_id": "task-123", "progress": 0.5, ...}
data: {"type": "task.completed", "task_id": "task-123", ...}
```

### Multi-Agent Conversation (Phase 3)

```python
# Create conversation
{
    "jsonrpc": "2.0",
    "method": "conversation.create",
    "params": {
        "topic": "System Design Discussion",
        "description": "Discussing new feature architecture",
        "turn_taking_mode": "round_robin"
    },
    "id": 1
}

# Join conversation
{
    "jsonrpc": "2.0",
    "method": "conversation.join",
    "params": {
        "conversation_id": "conv-123",
        "role": "participant"
    },
    "id": 2
}

# Send message
{
    "jsonrpc": "2.0",
    "method": "conversation.send",
    "params": {
        "conversation_id": "conv-123",
        "content": "I propose using a microservices architecture"
    },
    "id": 3
}
```

### Task Workflow (Phase 3)

```python
# Create pipeline workflow
{
    "jsonrpc": "2.0",
    "method": "workflow.create_pipeline",
    "params": {
        "name": "Data Processing Pipeline",
        "stages": [
            "data-extraction",
            "data-validation", 
            "data-transformation",
            "data-loading"
        ]
    },
    "id": 1
}

# Add task with dependencies
{
    "jsonrpc": "2.0",
    "method": "workflow.add_task",
    "params": {
        "workflow_id": "workflow-123",
        "task": {
            "name": "Validate Schema",
            "stage": "data-validation"
        },
        "dependencies": [{
            "predecessor_id": "extract-task",
            "type": "finish_to_start"
        }]
    },
    "id": 2
}
```

### Authenticated Request (Phase 3)

```python
# Login to get tokens
{
    "jsonrpc": "2.0",
    "method": "auth.login",
    "params": {
        "agent_id": "my-agent",
        "password": "secure-password"
    },
    "id": 1
}
# Response: {"access_token": "...", "refresh_token": "...", "role": "agent"}

# Use token in subsequent requests
POST /api/a2a/v1/
Headers:
  Authorization: Bearer <access_token>
  X-A2A-Signature: <message-signature>

{
    "jsonrpc": "2.0",
    "method": "task.create",
    "params": {...},
    "id": 2
}
```

## Development Guidelines

### Adding New Methods

1. Define method handler in appropriate module
2. Register with method dispatcher
3. Add tests for the new method
4. Update documentation

### Extending Streaming

1. Create new event types in `events.py`
2. Add event emission in relevant components
3. Update filters if needed
4. Test with SSE client

### Debugging

- Enable debug logging: `export LOG_LEVEL=DEBUG`
- Check Hermes logs for A2A service messages
- Use manual test scripts for interactive testing
- Monitor SSE connections at `/api/a2a/v1/stream/connections`

## Migration from Legacy A2A

The new implementation is not backwards compatible. Key changes:

1. **Message Format**: Custom format → JSON-RPC 2.0
2. **Agent Registration**: Direct registration → Agent Cards
3. **Task Management**: Simple states → Full lifecycle
4. **Discovery**: Basic listing → Advanced querying
5. **Streaming**: Not supported → SSE/WebSocket

## Security Features (Phase 3)

The A2A protocol now includes comprehensive security:

1. **Authentication**
   - JWT-based authentication with access/refresh tokens
   - Token expiration and revocation support
   - Secure token storage and management

2. **Authorization**
   - Role-based access control (RBAC) with 5 roles:
     - Admin: Full system access
     - Operator: Task and workflow management
     - Agent: Task execution and conversation participation
     - Observer: Read-only access
     - Guest: Minimal permissions
   - 20+ granular permissions for fine-grained control
   - Resource-level permissions for specific items

3. **Message Security**
   - HMAC-SHA256 message signing
   - Timestamp validation to prevent replay attacks
   - Agent identity verification

4. **Security Middleware**
   - Automatic authentication/authorization for all requests
   - Exempt methods for public endpoints
   - Permission decorators for method protection

## Future Enhancements

1. **Performance Optimizations**
   - Connection pooling for agent communication
   - Event batching for high-volume scenarios
   - Caching layer for frequently accessed data
   - Lazy loading of large resources

2. **Reliability**
   - Message persistence for guaranteed delivery
   - Retry mechanisms with exponential backoff
   - Circuit breakers for failing agents
   - Dead letter queues for failed messages

3. **Monitoring & Observability**
   - Distributed tracing support
   - Metrics collection (latency, throughput, errors)
   - Health check endpoints
   - Performance profiling hooks

4. **Advanced Features**
   - PKI-based message signing (beyond HMAC)
   - Federated authentication (OAuth2/OIDC)
   - Multi-tenancy support
   - GraphQL interface alongside JSON-RPC