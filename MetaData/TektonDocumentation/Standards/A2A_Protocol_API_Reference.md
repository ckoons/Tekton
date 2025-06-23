# A2A Protocol v0.2.1 API Reference

## Overview

This document provides a comprehensive API reference for the Agent-to-Agent (A2A) Protocol v0.2.1 implementation in Tekton. All methods use JSON-RPC 2.0 format.

## Base Endpoint

```
POST /api/a2a/v1/
Content-Type: application/json
```

## Authentication

Most methods require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

For message integrity, include an HMAC signature:

```
X-A2A-Signature: <hmac-signature>
```

## Core Data Types

### Agent Card
```typescript
interface AgentCard {
    name: string;
    description: string;
    version: string;
    capabilities: string[];
    supported_methods: string[];
    endpoint: string;
    metadata?: Record<string, any>;
}
```

### Task
```typescript
interface Task {
    id: string;
    name: string;
    description?: string;
    state: "pending" | "assigned" | "in_progress" | "completed" | "failed" | "cancelled";
    priority: "low" | "medium" | "high" | "critical";
    assigned_to?: string;
    progress?: number;
    result?: any;
    error?: string;
    created_at: string;
    updated_at: string;
}
```

### Conversation
```typescript
interface Conversation {
    id: string;
    topic: string;
    description?: string;
    created_by: string;
    state: "created" | "active" | "paused" | "ended";
    turn_taking_mode: "free_form" | "round_robin" | "moderated" | "consensus";
    participants: Record<string, ConversationParticipant>;
}
```

### Workflow
```typescript
interface Workflow {
    id: string;
    name: string;
    pattern: "sequential" | "parallel" | "pipeline" | "fanout" | "fanin" | "conditional" | "loop";
    state: "created" | "running" | "paused" | "completed" | "failed" | "cancelled";
    tasks: Record<string, string>;  // workflow_task_id -> actual_task_id
    dependencies: TaskDependency[];
}
```

## Agent Methods

### agent.register
Register a new agent with the system.

**Parameters:**
- `agent_card` (AgentCard): Agent information

**Returns:** 
- `agent_id` (string): Unique identifier for the agent

**Example:**
```json
{
    "jsonrpc": "2.0",
    "method": "agent.register",
    "params": {
        "agent_card": {
            "name": "DataProcessor",
            "description": "Processes various data formats",
            "version": "1.0.0",
            "capabilities": ["data_processing", "validation"],
            "supported_methods": ["process.csv", "process.json"],
            "endpoint": "http://localhost:8010/"
        }
    },
    "id": 1
}
```

### agent.unregister
Remove an agent from the system.

**Parameters:**
- `agent_id` (string): Agent to unregister

**Returns:** 
- `success` (boolean): Whether unregistration succeeded

### agent.heartbeat
Update agent's last heartbeat timestamp.

**Parameters:**
- `agent_id` (string): Agent sending heartbeat

**Returns:**
- `timestamp` (string): Server timestamp

### agent.update_status
Update agent's operational status.

**Parameters:**
- `agent_id` (string): Agent to update
- `status` (string): New status ("online", "busy", "offline")

**Returns:**
- `success` (boolean): Whether update succeeded

### agent.get
Get detailed information about an agent.

**Parameters:**
- `agent_id` (string): Agent to retrieve

**Returns:**
- Agent object with full details

### agent.list
List all registered agents.

**Parameters:**
- `status` (string, optional): Filter by status
- `capability` (string, optional): Filter by capability

**Returns:**
- Array of agent objects

## Task Methods

### task.create
Create a new task.

**Parameters:**
- `name` (string): Task name
- `description` (string, optional): Task description
- `priority` (string): "low", "medium", "high", or "critical"
- `metadata` (object, optional): Additional task data

**Returns:**
- `task_id` (string): Created task ID

**Example:**
```json
{
    "jsonrpc": "2.0",
    "method": "task.create",
    "params": {
        "name": "Process Customer Data",
        "description": "Validate and transform customer CSV file",
        "priority": "high",
        "metadata": {
            "file_path": "/data/customers.csv",
            "validation_rules": ["email", "phone"]
        }
    },
    "id": 1
}
```

### task.assign
Assign a task to an agent.

**Parameters:**
- `task_id` (string): Task to assign
- `agent_id` (string): Agent to assign to

**Returns:**
- `success` (boolean): Whether assignment succeeded

### task.update_state
Update task state (following valid transitions).

**Parameters:**
- `task_id` (string): Task to update
- `state` (string): New state

**Returns:**
- `success` (boolean): Whether update succeeded

### task.update_progress
Update task completion progress.

**Parameters:**
- `task_id` (string): Task to update
- `progress` (number): Progress percentage (0-100)

**Returns:**
- `success` (boolean): Whether update succeeded

### task.complete
Mark a task as completed with result.

**Parameters:**
- `task_id` (string): Task to complete
- `result` (any, optional): Task result data

**Returns:**
- `success` (boolean): Whether completion succeeded

### task.fail
Mark a task as failed with error.

**Parameters:**
- `task_id` (string): Task to fail
- `error` (string): Error description

**Returns:**
- `success` (boolean): Whether update succeeded

### task.cancel
Cancel a task.

**Parameters:**
- `task_id` (string): Task to cancel

**Returns:**
- `success` (boolean): Whether cancellation succeeded

### task.get
Get task details.

**Parameters:**
- `task_id` (string): Task to retrieve

**Returns:**
- Task object with full details

### task.list
List tasks with optional filters.

**Parameters:**
- `state` (string, optional): Filter by state
- `assigned_to` (string, optional): Filter by assignee
- `priority` (string, optional): Filter by priority

**Returns:**
- Array of task objects

## Discovery Methods

### discovery.query
Query agents by various criteria.

**Parameters:**
- `name` (string, optional): Filter by name pattern
- `capabilities` (string[], optional): Required capabilities
- `status` (string, optional): Required status

**Returns:**
- Array of matching agents

### discovery.find_for_method
Find agents supporting a specific method.

**Parameters:**
- `method` (string): Method name

**Returns:**
- Array of agent IDs supporting the method

### discovery.find_for_capability
Find agents with a specific capability.

**Parameters:**
- `capability` (string): Capability name

**Returns:**
- Array of agent IDs with the capability

## Channel Methods (Phase 2)

### channel.subscribe
Subscribe to a channel for messages.

**Parameters:**
- `channel` (string): Channel name
- `agent_id` (string): Subscribing agent

**Returns:**
- `success` (boolean): Whether subscription succeeded

### channel.unsubscribe
Unsubscribe from a channel.

**Parameters:**
- `channel` (string): Channel name
- `agent_id` (string): Unsubscribing agent

**Returns:**
- `success` (boolean): Whether unsubscription succeeded

### channel.publish
Publish a message to a channel.

**Parameters:**
- `channel` (string): Channel name
- `message` (any): Message content
- `sender_id` (string): Sending agent

**Returns:**
- `delivered_to` (number): Number of subscribers who received the message

### channel.list
List available channels.

**Returns:**
- Array of channel names

### channel.subscribers
Get subscribers for a channel.

**Parameters:**
- `channel` (string): Channel name

**Returns:**
- Array of subscriber agent IDs

## Conversation Methods (Phase 3)

### conversation.create
Create a new multi-agent conversation.

**Parameters:**
- `topic` (string): Conversation topic
- `description` (string, optional): Detailed description
- `turn_taking_mode` (string): Mode for turn management
  - "free_form": Anyone can speak anytime
  - "round_robin": Sequential turns
  - "moderated": Moderator controls who speaks
  - "consensus": Group must agree on next speaker

**Returns:**
- `conversation_id` (string): Created conversation ID

**Example:**
```json
{
    "jsonrpc": "2.0",
    "method": "conversation.create",
    "params": {
        "topic": "Architecture Review",
        "description": "Review proposed microservices architecture",
        "turn_taking_mode": "moderated"
    },
    "id": 1
}
```

### conversation.join
Join an existing conversation.

**Parameters:**
- `conversation_id` (string): Conversation to join
- `role` (string): Participant role
  - "moderator": Can control turn-taking
  - "participant": Can speak when allowed
  - "observer": Can only listen

**Returns:**
- `success` (boolean): Whether join succeeded

### conversation.leave
Leave a conversation.

**Parameters:**
- `conversation_id` (string): Conversation to leave

**Returns:**
- `success` (boolean): Whether leave succeeded

### conversation.send
Send a message in a conversation.

**Parameters:**
- `conversation_id` (string): Target conversation
- `content` (string): Message content
- `reply_to` (string, optional): Message ID being replied to

**Returns:**
- `message_id` (string): Sent message ID

### conversation.request_turn
Request permission to speak (for moderated mode).

**Parameters:**
- `conversation_id` (string): Target conversation

**Returns:**
- `request_id` (string): Turn request ID

### conversation.grant_turn
Grant speaking turn to a participant (moderator only).

**Parameters:**
- `conversation_id` (string): Target conversation
- `agent_id` (string): Agent to grant turn to

**Returns:**
- `success` (boolean): Whether grant succeeded

## Workflow Methods (Phase 3)

### workflow.create
Create a custom workflow with full control.

**Parameters:**
- `name` (string): Workflow name
- `pattern` (string): Workflow pattern
- `tasks` (object, optional): Initial tasks
- `dependencies` (array, optional): Task dependencies

**Returns:**
- `workflow_id` (string): Created workflow ID

### workflow.create_sequential
Create a sequential task chain.

**Parameters:**
- `name` (string): Workflow name
- `task_ids` (string[]): Ordered list of task IDs

**Returns:**
- `workflow_id` (string): Created workflow ID

**Example:**
```json
{
    "jsonrpc": "2.0",
    "method": "workflow.create_sequential",
    "params": {
        "name": "Data ETL Pipeline",
        "task_ids": ["extract-123", "transform-456", "load-789"]
    },
    "id": 1
}
```

### workflow.create_parallel
Create parallel task execution.

**Parameters:**
- `name` (string): Workflow name
- `task_ids` (string[]): Tasks to run in parallel

**Returns:**
- `workflow_id` (string): Created workflow ID

### workflow.create_pipeline
Create a data pipeline workflow.

**Parameters:**
- `name` (string): Workflow name
- `stages` (string[]): Pipeline stage names

**Returns:**
- `workflow_id` (string): Created workflow ID

### workflow.add_task
Add a task to an existing workflow.

**Parameters:**
- `workflow_id` (string): Target workflow
- `task` (object): Task details
- `dependencies` (array, optional): Task dependencies

**Dependency Types:**
- `finish_to_start`: Task starts after predecessor finishes
- `start_to_start`: Task starts when predecessor starts
- `finish_to_finish`: Task finishes when predecessor finishes
- `start_to_finish`: Task finishes when predecessor starts

**Returns:**
- `workflow_task_id` (string): Task ID within workflow

### workflow.start
Start workflow execution.

**Parameters:**
- `workflow_id` (string): Workflow to start

**Returns:**
- `success` (boolean): Whether start succeeded

### workflow.cancel
Cancel a running workflow.

**Parameters:**
- `workflow_id` (string): Workflow to cancel

**Returns:**
- `success` (boolean): Whether cancellation succeeded

## Authentication Methods (Phase 3)

### auth.login
Authenticate and receive access tokens.

**Parameters:**
- `agent_id` (string): Agent identifier
- `password` (string): Agent password

**Returns:**
- `access_token` (string): JWT access token (24-hour expiry)
- `refresh_token` (string): JWT refresh token (30-day expiry)
- `role` (string): Assigned role
- `permissions` (string[]): Granted permissions

**Example:**
```json
{
    "jsonrpc": "2.0",
    "method": "auth.login",
    "params": {
        "agent_id": "data-processor",
        "password": "secure-password-123"
    },
    "id": 1
}
```

### auth.refresh
Refresh an expired access token.

**Parameters:**
- `refresh_token` (string): Valid refresh token

**Returns:**
- `access_token` (string): New access token
- `refresh_token` (string): New refresh token

### auth.logout
Revoke authentication tokens.

**Parameters:**
- `access_token` (string, optional): Token to revoke
- `refresh_token` (string, optional): Token to revoke

**Returns:**
- `success` (boolean): Whether logout succeeded

### auth.verify
Verify current authentication status.

**Returns:**
- `authenticated` (boolean): Whether request is authenticated
- `agent_id` (string): Authenticated agent
- `role` (string): Current role
- `permissions` (string[]): Current permissions

## Error Codes

The A2A protocol uses standard JSON-RPC error codes plus custom codes:

### Standard Codes
- `-32700`: Parse error
- `-32600`: Invalid Request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error

### A2A Custom Codes
- `-32000`: Agent not found
- `-32001`: Task not found
- `-32002`: Unauthorized
- `-32003`: Capability not supported
- `-32004`: Invalid task state transition
- `-32005`: Rate limit exceeded
- `-32006`: Operation timeout
- `-32007`: Conversation not found

## Streaming APIs

### Server-Sent Events (SSE)

Connect to receive real-time events:

```
GET /api/a2a/v1/stream/events
```

Query parameters:
- `agent_id`: Filter events for specific agent
- `task_id`: Filter events for specific task
- `channel`: Subscribe to specific channel
- `conversation_id`: Filter conversation events

Event format:
```
event: task.state_changed
data: {"task_id": "task-123", "old_state": "pending", "new_state": "assigned"}
```

### WebSocket

Connect for bidirectional communication:

```
ws://localhost:8001/api/a2a/v1/ws
```

Message format follows JSON-RPC 2.0 specification.

## Security

### Roles and Permissions

**Admin Role:**
- All permissions

**Operator Role:**
- Task and workflow management
- Conversation creation
- Channel publishing

**Agent Role:**
- Task creation and updates
- Conversation participation
- Channel pub/sub

**Observer Role:**
- Read-only access to all resources

**Guest Role:**
- Minimal permissions (agent viewing only)

### Message Signing

For secure communication, sign messages with HMAC-SHA256:

1. Create canonical JSON representation (sorted keys)
2. Add `agent_id` and `timestamp` fields
3. Generate HMAC-SHA256 signature
4. Include in `X-A2A-Signature` header

## Rate Limiting

API endpoints have the following rate limits:

- Authentication: 10 requests per minute
- Task creation: 100 requests per minute
- General methods: 1000 requests per minute

Exceeded limits return error code `-32005`.