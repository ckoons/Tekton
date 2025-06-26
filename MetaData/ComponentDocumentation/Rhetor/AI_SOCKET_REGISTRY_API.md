# AI Socket Registry API Reference

## Overview

The AI Socket Registry implements the Unix philosophy for AI communication: "AIs are just sockets that read and write." This registry manages AI socket lifecycle and provides transparent header-based routing for team chat and multi-AI collaboration.

## Core Concepts

### Sockets
- Each AI is represented as a socket with a unique ID
- Sockets have a model, prompt, context, and message queue
- Special `team-chat-all` socket broadcasts to all active sockets

### Headers
- Messages are automatically wrapped with routing headers
- `[team-chat-from-X]` - Added when reading from socket X
- `[team-chat-to-Y]` - Added when writing to socket Y
- Headers are transparent to AIs (they only see content)

### Persistence
- Socket state is persisted to Engram for survival across Rhetor restarts
- Local backup when Engram is unavailable
- Namespace: `rhetor_sockets`

## Python API

### Initialization

```python
from rhetor.core.ai_socket_registry import get_socket_registry

# Get singleton instance
registry = await get_socket_registry()
```

### Socket Operations

#### Create Socket

```python
socket_id = await registry.create(
    model="claude-3-sonnet",
    prompt="You are Apollo, focused on prediction",
    context={"role": "predictor"},
    socket_id=None  # Optional, auto-generated if not provided
)
```

**Parameters:**
- `model` (str): AI model identifier
- `prompt` (str): System prompt for the AI
- `context` (dict): Optional context dictionary
- `socket_id` (str, optional): Specific socket ID, auto-generated if None

**Returns:** Socket ID (str)

#### Write to Socket

```python
# Write to specific socket
success = await registry.write(
    socket_id="apollo-123",
    message="What's your prediction?",
    metadata={"priority": "high"}
)

# Broadcast to all sockets
success = await registry.write(
    socket_id="team-chat-all",
    message="Team meeting: How can we improve?",
    metadata={"type": "broadcast"}
)
```

**Parameters:**
- `socket_id` (str): Target socket ID or "team-chat-all" for broadcast
- `message` (str): Message content
- `metadata` (dict, optional): Additional metadata

**Returns:** Success status (bool)

#### Read from Socket

```python
# Read from specific socket
messages = await registry.read("apollo-123")

# Read from all sockets (team chat)
all_messages = await registry.read("team-chat-all")
```

**Parameters:**
- `socket_id` (str): Socket ID or "team-chat-all" for all messages

**Returns:** List of messages with headers

**Message Format:**
```python
{
    "header": "[team-chat-from-apollo-123]",
    "content": "I predict significant advances...",
    "timestamp": "2024-01-01T12:00:00",
    "metadata": {"confidence": 0.85}
}
```

#### Reset Socket

```python
success = await registry.reset("apollo-123")
```

Clears message queue and context while keeping socket alive.

**Parameters:**
- `socket_id` (str): Socket to reset

**Returns:** Success status (bool)

#### Delete Socket

```python
success = await registry.delete("apollo-123")
```

Terminates AI and removes socket from registry.

**Parameters:**
- `socket_id` (str): Socket to delete

**Returns:** Success status (bool)

**Note:** Cannot delete the `team-chat-all` broadcast socket.

#### List Sockets

```python
sockets = await registry.list_sockets()
```

**Returns:** List of socket summaries
```python
[
    {
        "socket_id": "apollo-123",
        "model": "claude-3-sonnet",
        "state": "active",
        "created_at": "2024-01-01T12:00:00",
        "last_activity": "2024-01-01T12:30:00",
        "queue_size": 2
    }
]
```

#### Get Socket Information

```python
info = await registry.get_socket_info("apollo-123")
```

**Returns:** Detailed socket information or None if not found

#### Mark Socket Unresponsive

```python
success = await registry.mark_unresponsive("apollo-123")
```

Marks socket as unresponsive (won't receive new messages).

**Parameters:**
- `socket_id` (str): Socket to mark

**Returns:** Success status (bool)

## Socket States

- `ACTIVE` - Socket is active and can send/receive messages
- `INACTIVE` - Socket is inactive but still registered
- `UNRESPONSIVE` - Socket failed health checks, won't receive messages

## Usage Examples

### Basic Team Chat Flow

```python
# Initialize registry
registry = await get_socket_registry()

# Create AI sockets
apollo = await registry.create("claude-3", "You are Apollo", {"role": "predictor"})
athena = await registry.create("gpt-4", "You are Athena", {"role": "knowledge"})

# User broadcasts question
await registry.write("team-chat-all", "How can we optimize our system?")

# Each AI processes and responds (simulated here)
# In real implementation, AI services would read from their sockets

# Collect all responses
responses = await registry.read("team-chat-all")
for response in responses:
    print(f"{response['header']}: {response['content']}")
```

### Socket Lifecycle Management

```python
# Create socket with specific ID
socket_id = await registry.create(
    model="claude-3",
    prompt="Technical assistant",
    context={"expertise": "python"},
    socket_id="python-expert"
)

# Use the socket
await registry.write(socket_id, "Explain async/await")

# Reset when context gets too large
await registry.reset(socket_id)

# Mark unresponsive if health checks fail
await registry.mark_unresponsive(socket_id)

# Clean up when done
await registry.delete(socket_id)
```

### Persistence and Recovery

```python
# Sockets are automatically persisted
socket_id = await registry.create("claude-3", "Helper", {})

# After Rhetor restart, socket is restored
registry = await get_socket_registry()
info = await registry.get_socket_info(socket_id)
# Socket state is preserved
```

## Error Handling

- Non-existent socket operations return empty lists or False
- Persistence failures are logged but don't break functionality
- Broadcast socket (`team-chat-all`) cannot be deleted
- Unresponsive sockets reject write operations

## Best Practices

1. **Socket Naming**: Use descriptive IDs like `apollo-predictor` or `athena-knowledge`
2. **Message Size**: Keep messages reasonably sized for efficient broadcasting
3. **Cleanup**: Delete sockets when AIs are no longer needed
4. **Health Monitoring**: Regularly check socket responsiveness
5. **Context Management**: Reset sockets periodically to avoid context overflow

## Integration with Team Chat

The socket registry is designed to power Rhetor's team chat functionality:

1. User message → Write to `team-chat-all`
2. All AI sockets receive message with routing headers
3. AIs process and respond to their sockets
4. Rhetor reads from `team-chat-all` to collect responses
5. Responses are synthesized or passed through based on moderation mode

## Unix Philosophy in Practice

```bash
# Conceptual pipeline equivalent
echo "question" | tee apollo athena sophia | rhetor_collect

# Socket registry implementation
await registry.write("team-chat-all", "question")
responses = await registry.read("team-chat-all")
```

The socket registry maintains the simplicity of Unix pipes while adding persistence, headers, and state management necessary for AI orchestration.