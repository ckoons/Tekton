# CI Tools Integration - Complete Guide

## Overview

The CI Tools Integration brings external coding assistants like Claude Code, Cursor, and Continue into Tekton as first-class Companion Intelligences (CIs). This maintains the "CIs are sockets" philosophy while enabling programmatic control of these tools.

## Key Features

### 1. Socket-Based Integration
- All CI tools communicate via sockets (no keyboard automation)
- Standard JSON message protocol
- Bidirectional communication with proper flow control

### 2. Dynamic Tool Definition
- Define new tools without code changes
- Persistent across Tekton restarts
- Flexible configuration options

### 3. Multi-Instance Support
- Run multiple instances of the same tool
- Named instances for different purposes
- Session isolation for context separation

### 4. Full CI Registry Integration
- Tools appear in `aish list`
- Support for forwarding
- Apollo-Rhetor coordination
- Context state persistence

### 5. Dynamic Port Allocation
- Automatic port assignment
- Support for multiple Tekton stacks
- Configurable port ranges

## Quick Start

### Basic Usage

```bash
# List available tools
aish tools list

# Launch Claude Code
aish tools launch claude-code

# Send a message
aish claude-code "Review this code"

# Check status
aish tools status

# Terminate when done
aish tools terminate claude-code
```

### Multiple Instances

```bash
# Create named instances
aish tools create review-bot --type claude-code
aish tools create test-writer --type claude-code

# Launch them
aish tools launch claude-code --instance review-bot
aish tools launch claude-code --instance test-writer

# Use them
aish review-bot "Review PR #123"
aish test-writer "Write tests for auth module"

# Check what's running
aish tools instances
```

### Forwarding

```bash
# Forward tool output to terminal
aish forward claude-code alice
aish forward review-bot bob json
```

## Dynamic Tool Definition

### Define a New Tool

```bash
# Define OpenAI assistant
aish tools define openai-coder \
    --type generic \
    --executable /usr/local/bin/openai \
    --description "OpenAI GPT-4 coding assistant" \
    --port auto \
    --capabilities "code_generation,debugging,refactoring" \
    --launch-args "--mode stdio --format json" \
    --health-check version \
    --env OPENAI_MODEL=gpt-4

# Launch it
aish tools launch openai-coder

# Use it
aish openai-coder "Generate a REST API"
```

### Tool Definition Options

- `--type <base>`: Base adapter type (generic, claude-code, etc.)
- `--executable <path>`: Path to tool executable
- `--description <text>`: Tool description
- `--port <num|auto>`: Port number or 'auto' for dynamic
- `--capabilities <list>`: Comma-separated capabilities
- `--launch-args <args>`: Launch arguments
- `--health-check <type>`: Health check method
- `--env <key=value>`: Environment variables

### Managing Definitions

```bash
# List defined tools
aish tools defined

# Show tool details
aish tools defined openai-coder

# Remove definition
aish tools undefine openai-coder
```

## Architecture

### Component Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   aish tools    │────▶│  Tool Launcher  │────▶│   CI Tool       │
│    command      │     │   (Singleton)   │     │   Process       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  CI Registry    │     │ Socket Bridge   │────▶│ Tool Adapter    │
│ (Unified View)  │     │  (Port 8400+)   │     │ (Translation)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Key Components

1. **Tool Registry**: Manages tool configurations and state
2. **Tool Launcher**: Singleton that manages tool processes
3. **Socket Bridge**: Handles socket communication
4. **Adapters**: Translate between Tekton and tool protocols
5. **CI Registry Integration**: Makes tools visible as CIs

### Adapter Types

1. **ClaudeCodeAdapter**: Specific to Claude Code
2. **GenericAdapter**: Flexible adapter for stdio tools
3. Future: CursorAdapter, ContinueAdapter, etc.

## Persistence

### Tool State
- Tool definitions saved in `.tekton/ci_tools/custom_tools.json`
- Running state tracked in CI registry
- Context preserved across restarts

### Example Persistence Flow

```bash
# Day 1: Define and use tool
aish tools define my-assistant --type generic --executable /path/to/tool
aish tools launch my-assistant
aish my-assistant "Implement feature X"

# Day 2: After restart
aish list  # Tool still defined
aish my-assistant "Continue with feature X"  # Auto-launches if needed
```

## Configuration

### Dynamic Port Allocation

```bash
# In .env.tekton
CI_TOOLS_PORT_MODE=dynamic      # Enable dynamic ports
CI_TOOLS_PORT_RANGE=50000-60000 # Port range
```

### Multi-Stack Support

```bash
# Stack A
TEKTON_STACK_ID=A
CI_TOOLS_PORT_MODE=dynamic

# Stack B
TEKTON_STACK_ID=B
CI_TOOLS_PORT_MODE=dynamic
```

## Generic Adapter Protocol

The generic adapter expects tools to communicate via stdin/stdout with JSON:

### Input Format
```json
{
  "message": "User message",
  "type": "user",
  "session": "session-id",
  "context": {}
}
```

### Output Format
```json
{
  "response": "Tool response",
  "type": "response",
  "metadata": {}
}
```

## Testing

Run comprehensive tests:

```bash
# Run all CI tools tests
cd shared/ci_tools/tests
python run_all_tests.py

# Run specific test suite
python test_tool_definition.py
python test_generic_adapter.py
python test_integration.py
```

## CI Terminal and Tool Wrappers

### Overview

In addition to the high-level CI Tools system, aish provides lower-level wrappers for any program:

- **`ci-terminal`**: PTY-based wrapper for terminal programs (Claude, bash, REPLs)
- **`ci-tool`**: Simple wrapper for non-terminal programs (scripts, servers)

### Delimiter Configuration

Both wrappers support automatic command execution via delimiter configuration:

```bash
# Configure delimiter at launch
aish ci-terminal -n claude-ci -d "\n" -- claude
aish ci-tool -n processor -d "\n\n" -- python script.py

# Send with automatic execution
aish claude-ci "command" -x              # Uses configured delimiter
aish processor "data" -x "\n"            # Override delimiter
```

### CI Terminal Usage

```bash
# Launch Claude with newline delimiter
aish ci-terminal -n claude-ci -d "\n" -- claude &

# Send commands that auto-execute
aish claude-ci "Tell me about Python" -x
aish claude-ci "Explain async/await" --execute

# Send partial input (no execution)
aish claude-ci "Tell me about"
```

### CI Tool Usage

```bash
# Launch Python script with double-newline delimiter  
aish ci-tool -n analyzer -d "\n\n" -- python analyze.py &

# Send commands with execution
aish analyzer "START_BATCH" -x
aish analyzer "PROCESS_FILE data.csv" -x "\n"
```

### Delimiter Options

| Program Type | Common Delimiter | Notes |
|-------------|-----------------|-------|
| Unix shells | `\n` | Standard newline |
| Windows programs | `\r\n` | Carriage return + newline |
| Python REPL | `\n` or `\n\n` | Single for statements, double for blocks |
| Claude/CI tools | `\n` | Usually Unix standard |
| Custom protocols | Varies | Check tool documentation |

### Background Execution

Both wrappers support standard Unix background execution:

```bash
# Launch in background with &
aish ci-terminal -n claude-ci -- claude &
aish ci-tool -n server -- node app.js &

# With output redirection
aish ci-tool -n processor -- python script.py > output.log 2>&1 &
aish ci-terminal -n bash-ci -- bash 2>&1 | tee session.log &
```

### Message Protocol Extension

When using `-x` or `--execute`, the message protocol includes:

```json
{
  "from": "sender_name",
  "content": "message content",
  "type": "message",
  "execute": true,
  "delimiter": "\n"
}
```

## Examples

### Code Review Bot

```bash
# Define review bot
aish tools define review-bot \
    --type claude-code \
    --executable claude-code \
    --description "Specialized code reviewer" \
    --launch-args "--preset review"

# Use for PR reviews
aish review-bot "Review changes in src/auth"
```

### Test Writer

```bash
# Create test writer instance
aish tools create test-writer --type claude-code

# Launch and use
aish tools launch claude-code --instance test-writer
aish test-writer "Generate unit tests for UserService"
```

### Multi-Tool Workflow

```bash
# Morning setup
aish tools launch claude-code
aish tools launch openai-coder
aish tools create reviewer --type claude-code

# Distributed work
aish claude-code "Implement user authentication"
aish openai-coder "Generate API documentation"
aish reviewer "Review the auth implementation"

# Forward to terminals
aish forward claude-code alice
aish forward reviewer bob
```

## Best Practices

1. **Use Named Instances**: For clarity and organization
2. **Dynamic Ports**: Prevents conflicts
3. **Define Capabilities**: Helps with tool discovery
4. **Set Health Checks**: Ensures monitoring
5. **Clean Up**: Terminate tools when done

## Troubleshooting

### Tool Won't Launch
- Check executable path exists
- Verify port not in use
- Check logs: `aish tools status <name>`

### No Response from Tool
- Verify tool supports stdio/socket communication
- Check adapter type matches tool protocol
- Review tool launch arguments

### Port Conflicts
- Enable dynamic port mode
- Use different port ranges for stacks
- Check for other services using ports

## Future Enhancements

1. **Tool Marketplace**: Share tool definitions
2. **Adapter Plugins**: Python plugins for complex tools
3. **Auto-discovery**: Detect tool capabilities
4. **Performance Profiles**: Optimize for tool characteristics
5. **Cross-instance Communication**: Direct tool-to-tool messaging

## Implementation Details

For developers extending the system:

1. **Create New Adapter**: Extend `BaseCIToolAdapter`
2. **Register in Launcher**: Add to `adapter_map`
3. **Define Protocol**: Document input/output format
4. **Add Tests**: Cover adapter functionality

## Summary

The CI Tools Integration successfully brings external coding assistants into Tekton while maintaining architectural principles. Tools are true CIs with full participation in the ecosystem, enabling powerful workflows and team collaboration between human developers and CI assistants.