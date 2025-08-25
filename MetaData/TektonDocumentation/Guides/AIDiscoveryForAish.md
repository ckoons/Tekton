# CI Discovery for Aish Integration

## Overview

The Tekton CI Platform now provides MCP-like discovery capabilities for CI specialists. This allows aish and other clients to dynamically discover, connect to, and interact with CI specialists without hard-coding connection details.

## Key Features

### 1. Dynamic CI Discovery
- List all available CI specialists
- Filter by role (e.g., planning, code-analysis, messaging)
- Filter by capability (e.g., streaming, structured-output)
- Get real-time health status

### 2. CI Introspection
- Query detailed information about each AI
- Get connection details (host, port)
- Discover supported models and context windows
- View performance metrics

### 3. Role-Based Selection
- Find the best CI for a specific task
- Automatic fallback to alternatives
- Performance-based routing

## Using the Discovery Tool

### Installation
The `ai-discover` tool is available in the Tekton scripts directory:

```bash
# Make sure it's executable
chmod +x $TEKTON_ROOT/scripts/ai-discover

# Add to PATH for convenience
export PATH=$TEKTON_ROOT/scripts:$PATH
```

### Basic Commands

#### List All CIs
```bash
ai-discover list

# Output:
# ✓ prometheus (prometheus-ai)
#    Component: prometheus
#    Roles: planning
#    Socket: localhost:45010
#    Model: llama3.3:70b
```

#### Filter by Role
```bash
ai-discover list --role planning
ai-discover list --role code-analysis
```

#### Get Detailed Information
```bash
ai-discover info apollo-ai

# Output includes:
# - Connection details
# - Supported capabilities
# - Model information
# - Performance metrics
```

#### Find Best CI for Task
```bash
ai-discover best planning
# Returns: prometheus-ai at localhost:45010
```

#### Test Connections
```bash
# Test all CIs
ai-discover test

# Test specific AI
ai-discover test rhetor-ai
```

#### Get JSON Output
```bash
# For programmatic use
ai-discover list --json
ai-discover info apollo-ai --json
```

## Integration with Aish

### Direct Socket Connection
Once you discover an AI, connect directly via socket:

```bash
# Get connection info
INFO=$(ai-discover info prometheus-ai --json)
HOST=$(echo $INFO | jq -r '.connection.host')
PORT=$(echo $INFO | jq -r '.connection.port')

# Send message via socket
echo '{"type": "chat", "content": "Create a plan for building a web app"}' | \
  nc $HOST $PORT
```

### Using in Aish Pipelines
```bash
# Find best CI for task and use it
AI_ID=$(ai-discover best planning --json | jq -r '.id')
echo "Plan this project" | aish --ai $AI_ID
```

### Programmatic Discovery (Python)
```python
import subprocess
import json

def discover_ai_for_role(role):
    """Discover the best CI for a given role."""
    result = subprocess.run(
        ['ai-discover', 'best', role, '--json'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def list_all_ais():
    """List all available CIs."""
    result = subprocess.run(
        ['ai-discover', 'list', '--json'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)['ais']

# Example usage
planning_ai = discover_ai_for_role('planning')
print(f"Best planning AI: {planning_ai['name']} at {planning_ai['connection']}")
```

## CI Roles and Capabilities

### Available Roles
- `code-analysis`: Code review, analysis, and generation
- `planning`: Task planning and project management
- `orchestration`: Coordinating multiple CIs
- `knowledge-synthesis`: Information synthesis and reasoning
- `memory`: Memory and context management
- `messaging`: Communication and chat
- `learning`: Learning and adaptation
- `agent-coordination`: Multi-agent coordination
- `specialist-management`: Managing CI specialists
- `workflow-design`: Designing workflows and processes
- `general`: General-purpose AI

### Capabilities
- `streaming`: Supports streaming responses
- `structured-output`: Can return structured data
- `function-calling`: Supports function/tool calling
- `code-generation`: Can generate code
- `multi-turn`: Supports conversations
- `context-aware`: Maintains context across messages

## Message Protocol

All CIs use a standard JSON message protocol over TCP sockets:

### Basic Chat Request
```json
{
  "type": "chat",
  "content": "Your message here",
  "temperature": 0.7,
  "max_tokens": 4000
}
```

### Response Format
```json
{
  "content": "CI response",
  "model": "llama3.3:70b",
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 200
  }
}
```

### Info Request
```json
{
  "type": "info"
}
```

### Ping Request
```json
{
  "type": "ping"
}
```

## Platform Manifest

Get a complete platform manifest:

```bash
ai-discover manifest --json
```

This returns:
- Platform version
- Discovery service endpoints
- Total number of CIs
- Available roles and capabilities
- Interaction protocol details

## Best Practices

1. **Use Role-Based Discovery**: Instead of hard-coding CI names, discover by role
2. **Check Health**: Always verify CI is healthy before use
3. **Handle Fallbacks**: The registry provides alternatives if primary CI fails
4. **Cache Discovery**: For performance, cache discovery results for a short time
5. **Monitor Performance**: Use the performance metrics to choose optimal CIs

## Troubleshooting

### No CIs Found
```bash
# Check if CI platform is running
tekton-status

# Verify registry file exists
ls ~/.tekton/ai_registry/platform_ai_registry.json
```

### Connection Refused
```bash
# Test specific CI connection
ai-discover test apollo-ai

# Check if port is in use
lsof -i :45007
```

### Discovery Tool Not Found
```bash
# Ensure script is executable
chmod +x $TEKTON_ROOT/scripts/ai-discover

# Run with full path
$TEKTON_ROOT/scripts/ai-discover list
```

## Future Enhancements

1. **WebSocket Support**: For persistent connections
2. **gRPC Interface**: For higher performance
3. **Capability Negotiation**: Dynamic capability discovery
4. **Load Balancing**: Automatic load distribution
5. **Circuit Breakers**: Automatic failure handling

## Related Documentation

- [CI Registry Architecture](../Architecture/AIRegistryArchitecture.md)
- [Unified CI Client](../Architecture/UnifiedAIClient.md)
- [Aish Integration Guide](./AishIntegration.md)