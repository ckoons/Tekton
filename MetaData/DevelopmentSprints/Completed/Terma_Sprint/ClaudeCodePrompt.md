# Terma Implementation Sprint - Phase 1

## Context

You are implementing Terma, an intelligent terminal interface for the Tekton ecosystem. Terma provides natural language terminal control with safety, learning, and integration capabilities.

## Your Mission

Implement Phase 1 of Terma, focusing on core terminal control and basic API setup.

## Architecture Overview

Terma acts as an intelligent wrapper around terminal operations:
- **AsyncShell**: Manages shell processes asynchronously
- **ProcessManager**: Tracks and controls spawned processes
- **RhetorWrapper**: Translates natural language to commands (Phase 2)
- **SafetyChecker**: Prevents destructive operations
- **PatternLearner**: Learns from successful commands

## Phase 1 Implementation Tasks

### 1. Create Project Structure
```
Terma/
├── terma/
│   ├── __init__.py
│   ├── api/
│   ├── core/
│   ├── integrations/
│   ├── learning/
│   └── safety/
├── tests/
├── requirements.txt
├── setup.py
└── README.md
```

### 2. Implement AsyncShell (`terma/core/async_shell.py`)

Create an async wrapper around shell processes that:
- Supports bash, zsh, and PowerShell
- Streams output asynchronously
- Handles stdin/stdout/stderr separately
- Provides timeout control
- Maintains process state

Key methods:
- `start()`: Initialize shell process
- `execute(command: str, timeout: Optional[float])`: Run command
- `terminate()`: Clean shutdown
- `_stream_output()`: Async generator for output

### 3. Implement ProcessManager (`terma/core/process_manager.py`)

Track and control all spawned processes:
- Monitor resource usage
- Handle process lifecycle
- Provide process listing
- Enable force termination

### 4. Create Basic API (`terma/api/app.py`)

FastAPI application with:
- `POST /execute`: Execute a command
- `GET /status`: Get shell and process status
- `POST /terminate/{pid}`: Stop a specific process
- WebSocket `/stream`: Real-time output streaming

### 5. Add Models (`terma/api/models.py`)

Pydantic models for:
- CommandRequest
- CommandResult
- ProcessStatus
- ShellStatus

### 6. Basic Tests (`tests/test_shell.py`)

Test:
- Shell initialization
- Command execution
- Output streaming
- Process termination
- Error handling

## Important Considerations

1. **Security**: Sanitize all inputs before shell execution
2. **Performance**: Use async/await throughout for non-blocking operations
3. **Error Handling**: Gracefully handle shell crashes and command failures
4. **Logging**: Use Tekton's logging standards
5. **Cross-Platform**: Abstract platform-specific shell differences

## Example Usage

```python
# Initialize Terma
shell = AsyncShell(shell_type='bash')
await shell.start()

# Execute command
result = await shell.execute('ls -la', timeout=30)
print(result.stdout)

# Stream long-running command
async for line in shell.execute_streaming('tail -f /var/log/system.log'):
    print(line)

# Cleanup
await shell.terminate()
```

## Success Criteria

- AsyncShell successfully executes commands and returns output
- ProcessManager tracks all spawned processes accurately
- API endpoints respond correctly
- Tests pass for basic operations
- No blocking operations in async code

## Next Phase Preview

Phase 2 will add:
- Rhetor integration for natural language
- Command translation from intent
- Output parsing to structured data
- Safety analysis

Focus on getting a solid foundation that future phases can build upon.

## Resources

- Existing Tekton components for reference
- Python asyncio documentation
- FastAPI WebSocket guide
- The `asyncio.subprocess` module

Remember: This is the foundation for an intelligent terminal. Make it robust, safe, and extensible.