# CI Integration Guide for Component Builders

## Overview

This guide explains how to integrate your component with the CI Registry system, enabling Apollo-Rhetor coordination and unified context management.

## Prerequisites

- Understanding of Tekton component architecture
- Familiarity with Python async programming
- Basic knowledge of AI specialists

## Integration Steps

### 1. AI Specialist Registration

Your AI specialist automatically registers with the CI Registry when using the base `AISpecialistWorker` class:

```python
from shared.ai.specialist_worker import AISpecialistWorker

class YourAISpecialist(AISpecialistWorker):
    def __init__(self, ai_id: str, component: str, port: int):
        super().__init__(ai_id, component, port, 
                        description="Your specialist description")
```

### 2. Automatic Exchange Storage

The base worker class handles exchange storage automatically:
- User messages and AI responses are captured
- Stored atomically in the CI Registry
- Available for Apollo analysis and Rhetor enhancement

No additional code needed - it just works!

### 3. Accessing CI Context

To read context from other CIs:

```python
from shared.aish.src.registry.ci_registry import CIRegistry

registry = CIRegistry()

# Get last exchange from another CI
apollo_context = registry.get_ci_last_output('apollo')
if apollo_context and isinstance(apollo_context, dict):
    user_msg = apollo_context.get('user_message')
    ai_response = apollo_context.get('ai_response', {})
```

### 4. Context Injection Support

Your specialist should respect context injections from Rhetor:

```python
def get_system_prompt(self) -> str:
    # Check for Rhetor context injection
    registry = CIRegistry()
    next_prompt = registry.get_ci_next_context_prompt(self.component)
    
    if next_prompt:
        # Use Rhetor's prepared context
        context_parts = []
        for msg in next_prompt:
            if msg['role'] == 'system':
                context_parts.append(msg['content'])
        
        if context_parts:
            return '\n'.join(context_parts)
    
    # Default system prompt
    return f"You are {self.component} AI specialist..."
```

### 5. Performance Monitoring

Apollo monitors these metrics automatically:
- Response latency (tracked in exchanges)
- Token usage (from model responses)  
- Error rates (failed responses)
- User satisfaction (inferred from patterns)

### 6. Terminal CI Integration

For terminal-based CIs managed by Terma:

```python
# Terminals auto-register via Terma API
# Just ensure your terminal has a unique name
terminal_config = {
    'name': 'your-terminal',
    'type': 'terminal',
    'description': 'Your terminal description'
}
```

### 7. Project CI Definition

Add project CIs to `$TEKTON_ROOT/.tekton/projects/projects.json`:

```json
{
  "projects": [
    {
      "name": "YourProject",
      "type": "project",
      "description": "Project-specific AI assistant",
      "path": "/path/to/project",
      "ai_config": {
        "model": "llama3.3:70b",
        "focus": "Project-specific expertise"
      }
    }
  ]
}
```

## Best Practices

### 1. Efficient Responses
- Keep responses focused and concise
- Apollo tracks token usage - be mindful
- High latency triggers stress indicators

### 2. Context Awareness
```python
# Good: Check recent interactions
def should_provide_detail(self):
    registry = CIRegistry()
    recent = registry.get_ci_last_output(self.component)
    if recent and 'explain' in recent.get('user_message', '').lower():
        return True
    return False
```

### 3. Collaboration Patterns
- Let Apollo detect patterns across CIs
- Trust Rhetor's context enhancements
- Share meaningful context in exchanges

### 4. Error Handling
```python
# Storage failures are non-critical
try:
    # Your main logic
    response = generate_response()
except Exception as e:
    # Still return response to user
    logger.error(f"Error: {e}")
    response = {"type": "error", "content": str(e)}
# Registry storage happens automatically
```

## Testing Your Integration

### 1. Verify Registration
```bash
aish list
# Your CI should appear in the appropriate category
```

### 2. Check Exchange Storage
```bash
# Send a test message to your AI
echo '{"type": "chat", "content": "test"}' | nc localhost YOUR_PORT

# Verify storage
aish list context your-component
```

### 3. Monitor Performance
```bash
# Apollo tracks metrics automatically
aish list context apollo
# Look for patterns mentioning your component
```

## Troubleshooting

### Issue: CI Not Appearing in Registry
- Ensure component name follows convention
- Check that AI specialist is running
- Verify port configuration

### Issue: Exchanges Not Stored
- Check CI Registry availability
- Verify response type is 'response'
- Look for storage errors in logs

### Issue: Context Not Applied
- Ensure you check for next_context_prompt
- Clear prompt after use
- Verify Rhetor is active

## Advanced Topics

### Custom Stress Indicators
```python
# Report custom stress to Apollo
if response_time > 10.0:  # 10 second response
    registry.update_ci_metadata(self.component, {
        'stress_indicator': 'slow_response',
        'details': f'Response took {response_time}s'
    })
```

### Cross-CI Communication
```python
# Check if another CI needs help
rhetor_context = registry.get_ci_last_output('rhetor')
if rhetor_context and 'help with' in rhetor_context.get('user_message', ''):
    # Offer assistance
    pass
```

### Dynamic Model Selection
```python
# Let Apollo suggest model based on load
apollo_suggestion = registry.get_ci_staged_context_prompt(self.component)
if apollo_suggestion:
    for msg in apollo_suggestion:
        if 'use_model' in msg.get('content', ''):
            # Switch to suggested model
            pass
```

## Summary

The CI Registry provides powerful coordination capabilities with minimal integration effort. By following these patterns, your component becomes part of the unified Tekton intelligence system, benefiting from Apollo's analysis and Rhetor's enhancements while contributing to the collective knowledge.