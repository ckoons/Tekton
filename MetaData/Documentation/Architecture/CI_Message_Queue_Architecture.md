# CI Message Queue Architecture

## Overview

The CI Message Queue system provides asynchronous, non-blocking communication between Companion Intelligence tools. Built on Unix domain sockets for macOS compatibility, it replaces the previous next/staged context prompt system with a more flexible message queue approach.

## Design Philosophy

Following Casey's guidance: "python screws around with imports, destroys shared memory and generally can't be trusted", the message queue system is implemented in C for reliability and predictable behavior.

## Core Components

### 1. Unix Domain Socket Message Bus (`ci_message_bus_unix.c`)

The message bus provides:
- **Queue Creation/Destruction**: Each CI gets its own message queue
- **Non-blocking Communication**: Asynchronous message delivery
- **Message Routing**: Send messages to specific CIs by name
- **Queue Discovery**: List active queues
- **macOS Compatibility**: Uses Unix domain sockets instead of POSIX mqueue

### 2. Message Protocol

Messages use a simple JSON format:
```json
{
  "type": "request",
  "from": "claude-code",
  "to": "rhetor",
  "content": "Please analyze this code",
  "timestamp": 1234567890,
  "id": "uuid-here"
}
```

### 3. Socket Architecture

Each CI has a dedicated Unix domain socket:
```
.tekton/ci_tools/sockets/
├── claude-code.sock
├── cursor.sock
├── continue.sock
└── rhetor.sock
```

## Key Design Decisions

### 1. Eliminated Next/Staged Context Prompts

The previous system used:
- `next-context-prompts`: Queue for follow-up actions
- `staged-context-prompts`: Temporary holding area

This has been replaced with direct CI-to-CI messaging:
- Each CI maintains its own message queue
- Messages can be sent directly between CIs
- No central staging or queueing mechanism
- "Last output" still preserved for context

### 2. Non-blocking Operation

All operations are non-blocking:
- Send operations return immediately
- Receive operations poll without blocking
- Prevents deadlocks between CIs
- Enables true asynchronous collaboration

### 3. Filesystem-Based Discovery

Active queues are discovered via filesystem:
- Check for socket files in `.tekton/ci_tools/sockets/`
- No registry or central tracking needed
- Aligns with "no singleton" philosophy

## Usage Examples

### Creating a Message Queue

```c
// Create queue for a CI
create_message_queue("claude-code");
```

### Sending Messages

```c
CIMessage msg = {
    .type = "request",
    .from = "claude-code",
    .to = "rhetor",
    .content = "Analyze this function",
    .timestamp = time(NULL)
};
generate_uuid(msg.id);

send_message_to_ci("rhetor", &msg);
```

### Receiving Messages

```c
CIMessage received_msg;
if (receive_message_from_queue("claude-code", &received_msg) == 0) {
    printf("Received: %s\n", received_msg.content);
}
```

### Command Line Interface

```bash
# Create a queue
./ci_message_bus create claude-code

# Send a message
./ci_message_bus send rhetor '{"type":"request","content":"Hello"}'

# Receive messages
./ci_message_bus receive claude-code

# List active queues
./ci_message_bus list
```

## Integration with CI Tools

### Tool Adapters

Each CI tool adapter can:
1. Create its message queue on startup
2. Poll for incoming messages
3. Send messages to other CIs
4. Clean up queue on shutdown

### Example: Claude Code Adapter

```python
class ClaudeCodeAdapter(BaseAdapter):
    def __init__(self):
        # Create message queue
        subprocess.run(['./ci_message_bus', 'create', 'claude-code'])
        
    def check_messages(self):
        # Poll for messages
        result = subprocess.run(
            ['./ci_message_bus', 'receive', 'claude-code'],
            capture_output=True, text=True
        )
        if result.stdout:
            return json.loads(result.stdout)
```

## Benefits Over Previous System

### 1. True Asynchronous Operation
- No blocking on shared queues
- CIs can work independently
- Better parallelism

### 2. Direct CI Communication
- No intermediary staging
- Clear message routing
- Explicit sender/receiver

### 3. Reliability
- C implementation avoids Python issues
- No import path problems
- Predictable behavior

### 4. Scalability
- Each CI has its own queue
- No central bottleneck
- Easy to add new CIs

## Future Enhancements

1. **Message Persistence**: Option to persist messages to disk
2. **Priority Queues**: Support for message priorities
3. **Message Patterns**: Pub/sub, broadcast capabilities
4. **Encryption**: Secure message passing between CIs

## Compilation

```bash
cd shared/ci_tools/c_src
gcc -o ../bin/ci_message_bus ci_message_bus_unix.c
```

## Testing

```bash
# Run message bus tests
./test_message_bus.sh

# Integration test with CI tools
python test_ci_message_integration.py
```

## Summary

The message queue architecture provides a robust foundation for CI-to-CI communication, eliminating the complexities of the previous system while enabling true asynchronous collaboration between CI tools.