# Ergon Sandbox System Guide

## Overview

The Ergon Sandbox system provides isolated testing environments for Registry solutions, ensuring safe execution without affecting the host system. It implements a pluggable architecture supporting multiple isolation providers, from lightweight filesystem sandboxing to full container isolation.

## Architecture

### Core Components

1. **Abstract Base (`ergon/sandbox/base.py`)**
   - `SandboxProvider`: Abstract interface all providers must implement
   - `SandboxResult`: Standardized result format
   - `SandboxStatus`: Execution state tracking

2. **Providers**
   - **SandboxExecProvider** (`providers/sandbox_exec.py`): macOS native sandbox using sandbox-exec
   - **DockerProvider** (`providers/docker.py`): Full container isolation with Docker

3. **Factory Pattern (`sandbox/factory.py`)**
   - Intelligent provider selection based on requirements
   - Automatic fallback to available providers
   - Health checking and capability discovery

4. **Runner Interface (`sandbox/runner.py`)**
   - High-level API for testing solutions
   - Automatic dependency management
   - Result tracking and Registry updates

## Provider Capabilities

### SandboxExecProvider (macOS)
- **Platform**: macOS only
- **Isolation**: Filesystem isolation with network access
- **Performance**: Lightweight, minimal overhead
- **Use Cases**: Quick tests, simple scripts, API-based solutions

### DockerProvider
- **Platform**: Any with Docker installed
- **Isolation**: Full container isolation
- **Features**: GPU support, persistent volumes, custom images
- **Use Cases**: Complex environments, multi-service solutions

## API Endpoints

### REST API

```python
# Start testing a solution
POST /api/ergon/sandbox/test
{
    "solution_id": "uuid",
    "provider": "docker",  # Optional, auto-selected if not specified
    "timeout": 300,
    "memory_limit": "4g",
    "cpu_limit": 4,
    "environment": {"KEY": "value"}
}

# Execute command with streaming output
POST /api/ergon/sandbox/execute
{
    "sandbox_id": "uuid",
    "command": ["python", "script.py"]  # Optional, uses solution default
}

# Get execution results
GET /api/ergon/sandbox/results/{sandbox_id}

# Clean up sandbox
DELETE /api/ergon/sandbox/{sandbox_id}

# List active sandboxes
GET /api/ergon/sandbox/active

# Check provider health
GET /api/ergon/sandbox/health
```

### WebSocket API

```javascript
// Real-time bidirectional communication
ws://localhost:8102/api/ergon/sandbox/ws/{sandbox_id}

// Send commands
{
    "action": "execute",
    "command": ["python", "test.py"]
}

// Receive output
{
    "type": "output",
    "line": "[stdout] Test passed!"
}
```

## UI Integration

### Test Button
Each Registry solution card includes a Test button that:
1. Creates an isolated sandbox
2. Executes the solution
3. Streams output in real-time
4. Displays results and metrics
5. Updates solution test history

### Output Panel
- Real-time log streaming
- Color-coded output (stdout, stderr, errors)
- Execution status indicators
- Resource usage metrics
- Stop/Clear/Close controls

## Configuration

### Solution Requirements
Solutions can specify sandbox requirements in their Registry metadata:

```json
{
    "content": {
        "requires_network": true,
        "requires_gpu": false,
        "requires_persistence": false,
        "platform": "any",
        "memory_limit": "2g",
        "run_command": ["python", "main.py"],
        "requirements": ["requests", "numpy"],
        "environment": {
            "API_KEY": "${ERGON_API_KEY}"
        }
    }
}
```

### Provider Selection Logic
1. Check user preference (if specified)
2. Evaluate solution requirements
3. For macOS without special needs → sandbox-exec
4. For GPU/persistence/Linux → Docker
5. Fall back to any available provider

## Security

### Filesystem Protection
- **Read-only access** to solution files
- **Write access** only to workspace and output directories
- **No access** to user home directory (except specific caches)
- **Temporary directories** cleaned after execution

### Network Isolation
- sandbox-exec: Network allowed (for API access)
- Docker: Configurable network modes

### Resource Limits
- Memory limits enforced
- CPU limits enforced
- Execution timeouts
- Automatic cleanup on excess

## Usage Examples

### Testing a Registry Solution

```python
# Python example
import requests

# Test a solution
response = requests.post('http://localhost:8102/api/ergon/sandbox/test', json={
    'solution_id': 'abc123',
    'timeout': 60
})

sandbox_id = response.json()['sandbox_id']

# Get results
results = requests.get(f'http://localhost:8102/api/ergon/sandbox/results/{sandbox_id}')
print(results.json())
```

### JavaScript UI Integration

```javascript
// Test button click handler
async function testSolution(solutionId) {
    const response = await fetch('/api/ergon/sandbox/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            solution_id: solutionId,
            timeout: 300
        })
    });
    
    const { sandbox_id } = await response.json();
    
    // Stream output via Server-Sent Events
    const eventSource = new EventSource(`/api/ergon/sandbox/execute?sandbox_id=${sandbox_id}`);
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data.line);
    };
}
```

## Development

### Adding a New Provider

1. Create provider class inheriting from `SandboxProvider`
2. Implement all abstract methods
3. Register in `SandboxFactory._register_providers()`
4. Add capability detection logic

```python
from ergon.sandbox.base import SandboxProvider

class CustomProvider(SandboxProvider):
    async def prepare(self, solution_id, solution_path, config):
        # Create isolation environment
        pass
    
    async def execute(self, sandbox_id, command, timeout):
        # Run command and yield output
        pass
    
    async def get_result(self, sandbox_id):
        # Return execution results
        pass
    
    async def cleanup(self, sandbox_id):
        # Clean up resources
        pass
```

### Debugging

Enable debug logging:
```bash
export ERGON_LOG_LEVEL=DEBUG
python -m ergon
```

Check sandbox status:
```bash
curl http://localhost:8102/api/ergon/sandbox/active
```

## Troubleshooting

### Common Issues

1. **"No sandbox provider available"**
   - On macOS: Ensure sandbox-exec is available
   - On Linux: Install Docker
   - Check provider health: `/api/ergon/sandbox/health`

2. **"Maximum concurrent sandboxes reached"**
   - Default limit is 10 concurrent sandboxes
   - Clean up finished sandboxes: `/api/ergon/sandbox/cleanup-all`

3. **"Execution timeout exceeded"**
   - Increase timeout in test request
   - Check for infinite loops in solution
   - Monitor resource usage

4. **Docker not starting containers**
   - Verify Docker daemon is running: `docker ps`
   - Check Docker permissions
   - Ensure sufficient disk space

## Best Practices

1. **Always specify resource limits** to prevent system exhaustion
2. **Use appropriate providers** - lightweight for simple tests, Docker for complex
3. **Clean up sandboxes** after testing to free resources
4. **Monitor execution logs** for early problem detection
5. **Test locally first** before adding to Registry
6. **Include test commands** in solution metadata
7. **Handle timeouts gracefully** in long-running solutions

## Future Enhancements

- [ ] Kubernetes pod support for cloud deployment
- [ ] WASM runtime for browser-based execution
- [ ] Firecracker microVMs for enhanced isolation
- [ ] Distributed sandbox execution across multiple hosts
- [ ] Sandbox result caching and replay
- [ ] Automated performance profiling
- [ ] Integration with CI/CD pipelines