# CI Tools Lifecycle Management

## Overview

CI Tools in Tekton support full lifecycle management, allowing you to create, launch, monitor, and terminate tool instances. This enables scenarios like running multiple Claude Code instances for different purposes (review bot, refactoring assistant, etc.).

## Key Concepts

### Tool vs Instance

- **Tool**: The base CI tool type (claude-code, cursor, continue)
- **Instance**: A specific running copy of a tool with its own name and session

For example:
- `claude-code` is a tool type
- `review-bot` could be an instance of claude-code
- `refactor-helper` could be another instance of claude-code

## Lifecycle Commands

### Basic Tool Management

```bash
# List available CI tools
aish tools list

# Show status of all tools
aish tools status

# Show status of specific tool/instance
aish tools status claude-code
aish tools status review-bot

# Show tool capabilities
aish tools capabilities claude-code
```

### Launching Tools

```bash
# Launch default instance
aish tools launch claude-code

# Launch with session ID
aish tools launch claude-code --session pr-review

# Launch with instance name
aish tools launch claude-code --instance review-bot

# Launch with both
aish tools launch claude-code --session pr-123 --instance review-bot
```

### Creating Named Instances

```bash
# Create a named instance
aish tools create review-bot --type claude-code
aish tools create refactor-helper --type claude-code
aish tools create debug-assistant --type cursor

# Launch the named instance
aish tools launch claude-code --instance review-bot
```

### Managing Instances

```bash
# List all running instances
aish tools instances

# Terminate specific instance
aish tools terminate review-bot

# Terminate default instance
aish tools terminate claude-code
```

## Usage Patterns

### Single Instance (Default)

The simplest usage - one instance per tool type:

```bash
# Launch
aish tools launch claude-code

# Use
aish claude-code "Review this code"

# Terminate
aish tools terminate claude-code
```

### Multiple Instances

Run multiple instances for different purposes:

```bash
# Create specialized instances
aish tools create review-bot --type claude-code
aish tools create test-writer --type claude-code

# Launch them
aish tools launch claude-code --instance review-bot
aish tools launch claude-code --instance test-writer

# Use them separately
aish review-bot "Review PR #123"
aish test-writer "Generate tests for auth module"

# Check status
aish tools instances

# Terminate when done
aish tools terminate review-bot
aish tools terminate test-writer
```

### Session Management

Sessions provide context isolation:

```bash
# Launch with specific session
aish tools launch claude-code --session feature-auth

# Multiple instances with different sessions
aish tools launch claude-code --session frontend --instance ui-helper
aish tools launch claude-code --session backend --instance api-helper
```

## Instance Registry

When you create an instance, it becomes available as a CI in the registry:

```bash
# After creating review-bot
aish list type tool
# Shows: claude-code, cursor, continue, review-bot

# Direct messaging works
aish review-bot "Start reviewing the authentication module"
```

## Forwarding with Instances

Instances can be forwarded just like any other CI:

```bash
# Forward instance output to terminal
aish forward review-bot alice
aish forward test-writer bob json
```

## Best Practices

1. **Use descriptive instance names**: `review-bot`, `test-writer`, `refactor-helper`
2. **Create instances for specific roles**: Separate concerns by purpose
3. **Use sessions for context**: Group related work in sessions
4. **Clean up when done**: Terminate instances to free resources
5. **Monitor status**: Check `aish tools instances` regularly

## Example Workflow

```bash
# Morning setup
aish tools create pr-reviewer --type claude-code
aish tools create test-helper --type claude-code
aish tools create doc-writer --type cursor

# Launch for specific tasks
aish tools launch claude-code --instance pr-reviewer --session pr-456
aish tools launch claude-code --instance test-helper
aish tools launch cursor --instance doc-writer

# Work with them
aish pr-reviewer "Review the changes in src/auth"
aish test-helper "Write unit tests for the new API endpoints"
aish doc-writer "Update the API documentation"

# Check what's running
aish tools instances

# End of day cleanup
aish tools terminate pr-reviewer
aish tools terminate test-helper
aish tools terminate doc-writer
```

## Integration with Apollo-Rhetor

Each instance participates in the Apollo-Rhetor coordination:
- Apollo monitors patterns across all instances
- Rhetor can inject context into any instance
- Performance metrics tracked per instance
- Context sharing between instances of same session

## Technical Details

### Port Allocation
- Each tool type has a base port (8400-8449)
- Multiple instances share the same port via socket multiplexing
- The socket bridge handles routing to correct instance

### Process Management
- Each instance runs as a separate process
- Clean startup and shutdown procedures
- Automatic cleanup on Tekton exit
- Health monitoring per instance

### State Persistence
- Instance configurations saved in `.tekton/ci_tools/`
- Sessions can be resumed after restart
- Context preserved per instance

## Future Enhancements

1. **Instance Templates**: Pre-configured instances for common tasks
2. **Auto-scaling**: Spin up instances based on workload
3. **Instance Pools**: Reusable instance pools for efficiency
4. **Cross-instance Communication**: Direct messaging between instances
5. **Instance Metrics**: Detailed performance tracking per instance