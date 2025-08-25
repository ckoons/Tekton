# CI Specialists Guide

## Overview

AI Specialists are intelligent assistants integrated into each Tekton component. They provide domain-specific expertise, automated assistance, and intelligent insights tailored to their component's functionality. This guide covers configuration, usage, and best practices for working with CI Specialists.

## Architecture

### Core Components

1. **Specialist Worker** (`shared/ai/specialist_worker.py`)
   - Manages CI lifecycle and communication
   - Handles socket-based messaging
   - Provides unified interface across all specialists

2. **Generic Specialist** (`shared/ai/generic_specialist.py`)
   - Defines personality and expertise for each component
   - Implements domain-specific knowledge
   - Handles specialized queries and tasks

3. **Simple CI Service** (`shared/ai/ai_service_simple.py`)
   - Manages message queues and routing
   - Provides both sync and async communication
   - Handles connection management

### Communication Flow

```
User/Component → simple_ai → ai_service_simple → Socket → CI Specialist
                                                     ↓
                                                LLM Provider
```

## Configuration

### Environment Variables

#### Global Settings

```bash
# Enable/disable CI specialists (default: true)
TEKTON_REGISTER_AI=true

# CI provider selection
TEKTON_AI_PROVIDER=ollama  # Options: ollama, anthropic

# Default model for all specialists
TEKTON_AI_MODEL=llama3.3:70b

# Base port for CI services
TEKTON_AI_PORT_BASE=45000

# Component base port
TEKTON_PORT_BASE=8000
```

#### Component-Specific Overrides

```bash
# Override model for specific components
HERMES_AI_MODEL=llama3.1:70b
ENGRAM_AI_MODEL=qwen2.5-coder:32b
RHETOR_AI_MODEL=claude-3-sonnet-20240229

# Component-specific settings
HERMES_AI_ENABLED=true
ENGRAM_AI_TEMPERATURE=0.7
```

### Port Allocation

AI Specialists use a fixed port system:

| Component | Component Port | CI Port | CI Name |
|-----------|---------------|---------|---------|
| Hermes | 8000 | 45000 | hermes-ai |
| Athena | 8001 | 45001 | athena-ai |
| Ergon | 8002 | 45002 | ergon-ai |
| Engram | 8003 | 45003 | engram-ai |
| Codex | 8004 | 45004 | codex-ai |
| Rhetor | 8005 | 45005 | rhetor-ai |
| Telos | 8006 | 45006 | telos-ai |
| Prometheus | 8007 | 45007 | prometheus-ai |
| Harmonia | 8008 | 45008 | harmonia-ai |
| Sophia | 8009 | 45009 | sophia-ai |
| Metis | 8010 | 45010 | metis-ai |
| Apollo | 8012 | 45012 | apollo-ai |
| Budget | 8013 | 45013 | budget-ai |
| Hephaestus | 8088 | 45088 | hephaestus-ai |

**Formula**: `AI_PORT = TEKTON_AI_PORT_BASE + (COMPONENT_PORT - TEKTON_PORT_BASE)`

## Usage

### Python Integration

#### Synchronous Communication

```python
from shared.ai.simple_ai import ai_send_sync

# Send a message to an CI specialist
response = ai_send_sync(
    ai_name="hermes-ai",
    message="What's the current system health?",
    host="localhost",
    port=45000
)

print(response)
```

#### Asynchronous Communication

```python
from shared.ai.simple_ai import ai_send

# Async example
async def query_specialist():
    response = await ai_send(
        ai_name="engram-ai",
        message="Search for documentation about landmarks",
        host="localhost", 
        port=45003
    )
    return response

# Run async
result = await query_specialist()
```

### Command Line Usage

#### Using aish

```bash
# Direct CI communication through aish
aish ai hermes "What services are currently running?"

# Forward to specific AI
aish forward engram-ai "Find all references to authentication"
```

#### Manual Launch

```bash
# Launch a specific CI specialist
python scripts/enhanced_tekton_ai_launcher.py hermes -v --no-cleanup

# Launch with custom model
python scripts/enhanced_tekton_ai_launcher.py rhetor \
    --model claude-3-opus-20240229 \
    --provider anthropic
```

### Service Integration

```python
from shared.ai.ai_service_simple import get_service

# Get the CI service instance
service = get_service()

# Check service status
print(f"Active queues: {len(service.queues)}")
print(f"Active sockets: {len(service.sockets)}")

# Direct service usage (advanced)
response = await service.send_and_wait(
    "athena-ai",
    {"content": "Analyze entity relationships"},
    host="localhost",
    port=45001
)
```

## CI Personalities and Expertise

Each CI specialist has a unique personality and domain expertise:

### Component Specialists

- **Hermes AI**: "The Orchestrator" - Service coordination and health monitoring
- **Engram AI**: "The Memory Keeper" - Memory management and retrieval
- **Rhetor AI**: "The Eloquent Architect" - Prompt engineering and LLM optimization
- **Athena AI**: "The Knowledge Weaver" - Knowledge graphs and relationships
- **Ergon AI**: "The Industrious Builder" - Agent creation and workflow
- **Codex AI**: "The Code Sage" - Code analysis and generation
- **Telos AI**: "The Purposeful Guide" - Requirements and goal management
- **Prometheus AI**: "The Strategic Visionary" - Planning and resource optimization
- **Harmonia AI**: "The Workflow Maestro" - Process orchestration
- **Sophia AI**: "The Wise Teacher" - Learning and improvement
- **Metis AI**: "The Cunning Strategist" - Testing and quality assurance
- **Apollo AI**: "The Insightful Seer" - Monitoring and analytics
- **Budget AI**: "The Resource Guardian" - Cost optimization
- **Hephaestus AI**: "The Master Craftsman" - UI/UX assistance

## Common Use Cases

### 1. Component Health Monitoring

```python
from shared.ai.simple_ai import ai_send_sync

# Query Hermes CI about system health
health_report = ai_send_sync(
    "hermes-ai",
    "Generate a health report for all active components",
    "localhost",
    45000
)
```

### 2. Code Analysis

```python
# Ask Codex CI to analyze code
analysis = ai_send_sync(
    "codex-ai",
    "Analyze the security implications of the authentication module",
    "localhost",
    45004
)
```

### 3. Memory Search

```python
# Use Engram CI for semantic search
results = ai_send_sync(
    "engram-ai",
    "Find all discussions about performance optimization",
    "localhost",
    45003
)
```

### 4. Workflow Automation

```python
# Create a workflow with Ergon AI
workflow = ai_send_sync(
    "ergon-ai",
    "Create an agent to monitor GitHub issues and summarize them daily",
    "localhost",
    45002
)
```

## Troubleshooting

### Common Issues

#### 1. CI Not Responding

**Symptoms**: No response or connection refused

**Solutions**:
```bash
# Check if CI is running
ps aux | grep -E "hermes-ai"

# Check port availability
lsof -i :45000

# Manually launch AI
python scripts/enhanced_tekton_ai_launcher.py hermes --no-cleanup

# Check logs
tail -f /tmp/hermes-ai.log
```

#### 2. Wrong Model Loading

**Symptoms**: CI using unexpected model

**Solutions**:
```bash
# Check configuration
echo $HERMES_AI_MODEL
echo $TEKTON_AI_MODEL

# Override in launch
python scripts/enhanced_tekton_ai_launcher.py hermes \
    --model llama3.1:70b
```

#### 3. Communication Failures

**Symptoms**: Messages not reaching AI

**Solutions**:
```python
# Test basic connectivity
from shared.ai.simple_ai import ai_send_sync

try:
    response = ai_send_sync("hermes-ai", "ping", "localhost", 45000)
    print(f"Success: {response}")
except Exception as e:
    print(f"Failed: {e}")

# Check service status
from shared.ai.ai_service_simple import get_service
service = get_service()
print(f"Service running: {service is not None}")
```

### Debug Commands

```bash
# View all CI processes
ps aux | grep -E "ai|specialist"

# Check port alignment
python scripts/check_port_alignment.py

# Test CI communication
python tests/test_unified_ai_communication.py

# Monitor CI logs
tail -f /tmp/*-ai.log
```

### Performance Tuning

#### Model Selection

Choose models based on task requirements:
- **Fast responses**: `llama3.2:3b`, `phi3:mini`
- **Balanced**: `llama3.3:70b`, `mixtral:8x7b`
- **High quality**: `claude-3-opus`, `gpt-4`

#### Temperature Settings

```python
# Lower temperature for factual responses
factual_response = ai_send_sync(
    "athena-ai",
    "List all entity types",
    "localhost",
    45001,
    temperature=0.1
)

# Higher temperature for creative tasks
creative_response = ai_send_sync(
    "ergon-ai",
    "Suggest innovative workflow improvements",
    "localhost",
    45002,
    temperature=0.8
)
```

## Best Practices

### 1. Use Appropriate Specialists

Match queries to specialist expertise:
- System questions → Hermes AI
- Memory/search → Engram AI
- Code tasks → Codex AI
- UI/UX → Hephaestus AI

### 2. Structure Queries Clearly

```python
# Good: Specific and contextual
response = ai_send_sync(
    "rhetor-ai",
    """Optimize this prompt for Claude:
    'Analyze the security vulnerabilities in this Python code:
    [code snippet here]'
    
    Focus on: clarity, specificity, and actionable output.""",
    "localhost",
    45005
)

# Poor: Vague and without context
response = ai_send_sync("rhetor-ai", "fix prompt", "localhost", 45005)
```

### 3. Handle Errors Gracefully

```python
from shared.ai.simple_ai import ai_send_sync
import logging

def query_with_fallback(ai_name, message, port):
    try:
        return ai_send_sync(ai_name, message, "localhost", port)
    except ConnectionError:
        logging.warning(f"{ai_name} not available, using fallback")
        # Fallback logic here
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None
```

### 4. Monitor Resource Usage

```bash
# Check CI memory usage
ps aux | grep -E "ai|specialist" | awk '{print $2, $4, $11}'

# Monitor GPU usage (if applicable)
nvidia-smi

# Check model sizes
ls -lah ~/.ollama/models/manifests/registry.ollama.ai/library/
```

## Advanced Topics

### Custom Specialist Development

Create specialized CI behaviors:

```python
# In component's ai_config.py
CUSTOM_SYSTEM_PROMPT = """You are the Redis Cache Specialist.
Your expertise includes:
- Cache optimization strategies
- TTL management
- Memory efficiency
- Cache invalidation patterns
"""

CUSTOM_EXPERTISE = {
    "cache_patterns": [
        "write-through",
        "write-behind", 
        "cache-aside"
    ],
    "specializations": [
        "Redis optimization",
        "Memcached configuration",
        "Distributed caching"
    ]
}
```

### Team Chat Integration

AI specialists can participate in team discussions:

```python
# Broadcast to all CIs
from shared.ai.simple_ai import ai_send_sync

team_response = ai_send_sync(
    "team",  # Special identifier for team chat
    "What are the current system bottlenecks?",
    "localhost",
    45000  # Any CI port works for team
)
```

### Integration with External Tools

```python
# Example: AI-driven monitoring alert
async def ai_enhanced_alert(component, metric, value):
    analysis = await ai_send(
        f"{component}-ai",
        f"Analyze this metric anomaly: {metric}={value}",
        "localhost",
        45000 + (component_port - 8000)
    )
    
    if "critical" in analysis.lower():
        send_urgent_notification(analysis)
```

## Related Documentation

- [Simple CI Communication Architecture](/MetaData/TektonDocumentation/Architecture/SimpleAICommunication.md)
- [AI Registry Architecture](/MetaData/TektonDocumentation/Architecture/AIRegistry.md)
- [Unified CI Communication Tests](/tests/test_unified_ai_communication.py)
- [Enhanced CI Launcher Script](/scripts/enhanced_tekton_ai_launcher.py)