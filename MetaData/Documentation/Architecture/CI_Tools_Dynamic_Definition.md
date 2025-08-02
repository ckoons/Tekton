# CI Tools Dynamic Definition and Persistence

## Overview

CI Tools support dynamic definition through `aish tools define`, allowing users to add new tool types without code changes. Tools persist across Tekton restarts using the existing CI registry infrastructure.

## Dynamic Tool Definition

### Command Syntax

```bash
aish tools define <name> [options]

Options:
  --type <base-type>          Base adapter type (generic, claude-code, etc.)
  --executable <path>         Path to tool executable
  --description <text>        Tool description
  --port <number|auto>        Port number or 'auto' for dynamic allocation
  --capabilities <list>       Comma-separated capabilities
  --launch-args <args>        Launch arguments for the tool
  --health-check <method>     Health check method (ping, version, status)
  --env <key=value>          Environment variables (can be repeated)
```

### Examples

#### Define OpenAI Assistant
```bash
aish tools define openai-coder \
    --type generic \
    --executable /usr/local/bin/openai \
    --description "OpenAI GPT-4 coding assistant" \
    --port auto \
    --capabilities "code_generation,debugging,refactoring" \
    --launch-args "--mode stdio --format json" \
    --health-check ping \
    --env OPENAI_MODEL=gpt-4
```

#### Define Grok Analyzer
```bash
aish tools define grok-analyzer \
    --type generic \
    --executable grok-cli \
    --description "Grok code analysis tool" \
    --port auto \
    --capabilities "code_analysis,pattern_detection" \
    --launch-args "--interactive"
```

#### Define Custom Claude Instance
```bash
aish tools define claude-reviewer \
    --type claude-code \
    --executable claude-code \
    --description "Claude specialized for code review" \
    --port auto \
    --launch-args "--preset review --strict"
```

### Storage Format

Tool definitions are stored in `.tekton/ci_tools/definitions/`:

```json
{
  "name": "openai-coder",
  "base_type": "generic",
  "executable": "/usr/local/bin/openai",
  "description": "OpenAI GPT-4 coding assistant",
  "port": "auto",
  "capabilities": ["code_generation", "debugging", "refactoring"],
  "launch_args": ["--mode", "stdio", "--format", "json"],
  "health_check": "ping",
  "environment": {
    "OPENAI_MODEL": "gpt-4"
  },
  "defined_by": "user",
  "created_at": "2025-08-02T10:00:00Z"
}
```

### Managing Definitions

```bash
# List all defined tools
aish tools defined

# Show definition details
aish tools defined openai-coder

# Update a definition
aish tools define openai-coder --port 8405  # Updates existing

# Remove a definition
aish tools undefine openai-coder
```

## Persistence and State Management

### CI Registry Integration

CI Tools are full participants in the CI registry, with complete state management:

1. **Context State**: Last output, staged prompts, next prompts
2. **Apollo-Rhetor**: Full coordination support
3. **Persistence**: Survives Tekton restarts
4. **Auto-reconnect**: Reconnects to running tools on startup

### State Flow

```
Tool Launch:
  → Register in CI registry
  → Allocate port (dynamic or fixed)
  → Store PID and socket info
  → Mark as running

During Operation:
  → update_ci_last_output() after each exchange
  → Apollo monitors and stages context
  → Rhetor can inject prompts
  → State saved to registry.json

Tekton Restart:
  → Load registry.json
  → Find tool entries
  → Check if process still running
  → Reconnect if alive, mark stopped if not
  → Preserve context state regardless

Tool Termination:
  → Explicit termination only
  → Clean shutdown
  → Mark as stopped
  → Preserve context for history
```

### Persistence Example

```bash
# Day 1: Launch and use
aish tools launch openai-coder --instance helper
aish helper "Implement user authentication"
# Exchange saved automatically to registry

# Day 2: After Tekton restart
aish list
# Shows: helper (running) if process alive
#    or: helper (stopped) if process dead

# Either way, context is preserved:
aish list context helper
# Shows previous exchanges

# If stopped, relaunches automatically:
aish helper "Continue with the auth implementation"
```

## Dynamic Port Allocation

### Configuration

```bash
# In .env.tekton
CI_TOOLS_PORT_MODE=dynamic  # or 'fixed'
CI_TOOLS_PORT_RANGE=50000-60000  # for dynamic allocation
```

### Allocation Strategy

1. **Fixed Ports**: Traditional approach, good for single Tekton instance
2. **Dynamic Ports**: Automatically finds available ports, prevents conflicts
3. **Hybrid**: Some tools fixed, others dynamic

### Multi-Stack Support

For multiple Tekton stacks on the same machine:

```bash
# Stack A (.env.tekton)
TEKTON_STACK_ID=A
CI_TOOLS_PORT_MODE=dynamic

# Stack B (.env.tekton)  
TEKTON_STACK_ID=B
CI_TOOLS_PORT_MODE=dynamic

# No port conflicts - each finds available ports
```

## Generic Adapter

The `generic` base type provides a flexible adapter for any stdio-based tool:

```python
class GenericAdapter(BaseCIToolAdapter):
    """
    Generic adapter for stdio-based tools.
    Expects JSON communication by default.
    """
    
    def translate_to_tool(self, message):
        # Default: JSON with 'message' field
        return json.dumps({
            'message': message.get('content'),
            'context': message.get('context', {})
        })
    
    def translate_from_tool(self, output):
        # Default: Parse JSON or treat as plain text
        try:
            data = json.loads(output)
            return {
                'type': 'response',
                'content': data.get('response', data.get('content', str(data))),
                'metadata': data
            }
        except:
            return {
                'type': 'response',
                'content': output
            }
```

## Best Practices

1. **Use Dynamic Ports**: Prevents conflicts, especially with multiple stacks
2. **Define Capabilities**: Helps with tool discovery and routing
3. **Set Health Checks**: Ensures tools are monitored properly
4. **Use Generic Type**: For new tools without specific adapters
5. **Preserve Context**: Let registry handle persistence automatically

## Migration Path

For existing hardcoded tools:

```bash
# Export existing tool as definition
aish tools export claude-code > claude-code.json

# Modify as needed
edit claude-code.json

# Import as custom definition
aish tools import claude-code-custom < claude-code.json
```

## Future Enhancements

1. **Tool Marketplace**: Share tool definitions
2. **Adapter Plugins**: Python plugins for complex tools
3. **Capability Discovery**: Auto-detect tool capabilities
4. **Performance Profiles**: Optimize based on tool characteristics
5. **Federation**: Share tools across Tekton instances