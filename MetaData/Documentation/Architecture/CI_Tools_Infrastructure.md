# CI Tools Infrastructure Architecture

## Overview

The CI Tools Infrastructure provides a robust, Unix-philosophy-based system for integrating and managing Companion Intelligence (CI) development tools like Claude Code, Cursor, Continue, and custom tools. The architecture has evolved from Python-based singleton patterns to a C-based foundation with filesystem state management.

## Key Design Decisions

### 1. C-Based Core Infrastructure

We moved from Python to C for critical components because:
- **Reliability**: C provides predictable process management without Python's import/module complexities
- **No Singleton Issues**: Different import paths in Python created multiple "singleton" instances
- **Direct System Control**: Better handling of pipes, signals, and process lifecycle
- **Trust**: As noted, "Python screws around with imports, destroys shared memory and generally can't be trusted"

### 2. Filesystem-Based State Management

Instead of in-memory singletons:
- PID files track running processes
- JSON files store tool configurations
- Filesystem provides the single source of truth
- No complex state synchronization needed

### 3. Message Queue Architecture

Replaced next/staged context prompts with:
- Non-blocking Unix domain socket queues
- CI-to-CI messaging without shared memory complexity
- Each CI has its own message queue
- Asynchronous, reliable message delivery

## Core Components

### 1. C Tool Launcher (`ci_tool_launcher.c`)

The reliable process management foundation:

```c
// Key features:
- Handles stdin/stdout/stderr properly
- Supports both stdio and socket bridge modes  
- Signal handling for clean shutdown
- Dynamic port allocation
- Proper process detachment
```

**Compilation**:
```bash
cd shared/ci_tools/c_src
gcc -o ../bin/ci_tool_launcher ci_tool_launcher.c
```

### 2. C Message Bus (`ci_message_bus_unix.c`)

Unix domain socket-based message bus for CI-CI communication:

```c
// Key features:
- Create/destroy message queues
- Send/receive messages between CIs
- List active queues
- Non-blocking operation
- macOS compatible (no POSIX mqueue)
```

**Compilation**:
```bash
gcc -o ../bin/ci_message_bus ci_message_bus_unix.c
```

### 3. Simple Tool Launcher (Python)

Manages tool lifecycle without singletons:

```python
class SimpleToolLauncherV2:
    # Filesystem-based tracking
    # No singleton pattern
    # Uses C launcher for process management
    # Handles port allocation
```

## Tool Integration

### Claude Code Integration

Successfully integrated with Claude Max subscription:
- Uses `--print` mode (no JSON output to avoid API charges)
- Each message is self-contained (no session state)
- Context included in each request
- No token/cost tracking needed

**Configuration** (`.tekton/ci_tools/tools.json`):
```json
{
  "claude-code": {
    "display_name": "Claude Code",
    "type": "tool",
    "port": "auto",
    "description": "Claude AI coding assistant",
    "executable": "/Users/cskoons/.claude/local/claude",
    "launch_args": ["--print"],
    "health_check": "version"
  }
}
```

### Tool Adapter Pattern

Each tool has an adapter that:
- Translates between Tekton and tool-specific formats
- Handles both JSON and plain text modes
- Manages tool lifecycle
- Provides consistent interface

## Message Flow

### 1. Tool Launch
```
aish claude-code "message"
  → unified_sender.py
  → ToolLauncher.launch_tool()
  → ci_tool_launcher (C binary)
  → Tool process starts
```

### 2. Message Handling
```
User message
  → Adapter.translate_to_tool()
  → Process stdin (or socket)
  → Tool processes
  → Process stdout
  → Adapter.translate_from_tool()
  → Response to user
```

### 3. CI-CI Communication
```
CI A wants to message CI B
  → ci_message_bus send B message
  → Message queued in B's socket
  → B receives when ready
  → Non-blocking, reliable
```

## Directory Structure

```
.tekton/ci_tools/
├── tools.json          # Tool configurations
├── running/           # PID files for running tools
│   └── <tool>.json    # PID, port, session info
└── sockets/           # Unix domain sockets
    └── <ci>.sock      # Message queue socket

shared/ci_tools/
├── c_src/             # C source code
├── bin/               # Compiled binaries
├── adapters/          # Tool-specific adapters
├── simple_launcher_v2.py
└── base_adapter.py
```

## Key Improvements Over Previous Architecture

### 1. Eliminated Python Import Issues
- No more singleton pattern failures
- No module path confusion  
- Filesystem is the single source of truth

### 2. Reliable Process Management
- C launcher handles process lifecycle
- Proper signal handling
- Clean shutdown procedures

### 3. True CI-CI Communication
- Message queues replace shared memory
- Non-blocking, asynchronous
- Scales to many CIs

### 4. Cost-Effective Claude Integration
- Uses Claude Max subscription
- No API charges
- Simple, stateless operation

## Usage Examples

### Launch a Tool
```python
from shared.ci_tools.simple_launcher_v2 import SimpleToolLauncherV2
launcher = SimpleToolLauncherV2()
launcher.launch_tool('claude-code', session_id='sprint-1')
```

### Send CI-CI Message
```bash
./ci_message_bus send rhetor '{"type":"analysis","content":"Please review"}'
```

### Check Tool Status
```python
status = launcher.get_tool_status('claude-code')
# {'running': True, 'pid': 12345, 'port': 50001, ...}
```

## Future Enhancements

1. **Socket Bridge Mode**: Full implementation for tools requiring persistent connections
2. **Tool Discovery**: Automatic detection of installed AI coding tools
3. **Performance Metrics**: Track tool usage and performance
4. **Auto-Recovery**: Restart failed tools automatically

## Philosophy

Following Unix principles:
- **Do One Thing Well**: Each component has a single responsibility
- **Compose Simply**: Tools connect via standard protocols
- **Text Streams**: JSON over pipes/sockets
- **Filesystem as Database**: Simple, reliable state management

The infrastructure treats CIs as first-class citizens, not just tools, providing them with reliable communication channels and stable execution environments.