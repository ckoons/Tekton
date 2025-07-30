# CI Registry and Apollo-Rhetor Architecture

## Overview

The CI Registry is the central coordination system for all Conversational Interfaces (CIs) in the Tekton ecosystem. It manages three types of CIs:

1. **Greek Chorus CIs** - The foundational AI specialists (Apollo, Rhetor, Athena, etc.)
2. **Terminal CIs** - User-facing terminal interfaces managed by Terma
3. **Project CIs** - Project-specific AI assistants

## Architecture Components

### CI Registry (`shared/aish/src/registry/ci_registry.py`)

The registry serves as the single source of truth for:
- CI discovery and metadata
- Context state management
- Apollo-Rhetor coordination
- Performance and stress monitoring data

### Storage Structure

```
$TEKTON_ROOT/.tekton/aish/ci-registry/
├── registry.json          # Main registry file with CI metadata and context state
└── registry.lock         # Lock file for thread-safe updates
```

#### Registry JSON Structure
```json
{
  "context_state": {
    "apollo": {
      "last_output": {
        "user_message": "User's question...",
        "ai_response": {
          "type": "response",
          "ai_id": "apollo-ai",
          "content": "AI's response...",
          "model": "mistral:latest",
          "usage": {"total_tokens": 432},
          "latency": 7.703
        },
        "timestamp": 1753898264.57367
      },
      "next_context_prompt": [...],      // Prompt to inject on next turn
      "staged_context_prompt": [...]     // Staged by Apollo for future use
    }
  }
}
```

## Apollo-Rhetor Coordination Pattern

### 1. Context Monitoring (Apollo)
Apollo continuously monitors all CI interactions to:
- Analyze conversation patterns
- Detect stress indicators (long responses, high token usage)
- Identify opportunities for context enhancement
- Build predictive models of user needs

### 2. Context Preparation (Apollo)
When Apollo detects a pattern or need:
```python
# Apollo stages context for potential future use
registry.set_ci_staged_context_prompt("rhetor", [
    {"role": "system", "content": "Focus on performance optimization"},
    {"role": "assistant", "content": "I'll help optimize your code..."}
])
```

### 3. Context Injection (Rhetor)
Rhetor decides when to activate staged context:
```python
# Rhetor moves staged -> next for immediate injection
registry.set_ci_next_from_staged("rhetor")

# The next interaction will include the prepared context
next_prompt = registry.get_ci_next_context_prompt("rhetor")
```

### 4. Performance Monitoring
Both Apollo and Rhetor track:
- **Response Latency** - How long CIs take to respond
- **Token Usage** - Efficiency of responses
- **User Satisfaction** - Inferred from conversation flow
- **CI Stress** - When CIs are struggling with complex queries

## AI Specialist Integration

### Worker Process Updates
Every AI specialist automatically stores exchanges:

```python
# In specialist_worker.py after each response
if response.get('type') == 'response':
    exchange = {
        'user_message': message.get('content', ''),
        'ai_response': response,
        'timestamp': time.time()
    }
    ci_registry.update_ci_last_output(self.component.title(), exchange)
```

### Benefits
1. **Unified Context** - All CIs share conversation history
2. **Performance Tracking** - Latency and token usage per CI
3. **Adaptive Behavior** - Apollo learns patterns across all CIs
4. **Coordinated Responses** - Rhetor can enhance any CI's context

## Command Line Interface

### View Context Summary
```bash
aish list context
```
Shows all CIs with first 30 chars of last user message

### View Detailed Context
```bash
aish list context apollo
```
Shows full exchange including:
- Complete user message
- Full AI response
- Model used
- Token count
- Response latency
- Timestamp

## Integration Points

### 1. AI Specialists
- Auto-register in CI registry on startup
- Store every exchange automatically
- Respect injected context from Rhetor

### 2. Terminal Interfaces
- Register via Terma API
- Track command history
- Monitor terminal stress (rapid commands, errors)

### 3. Project CIs
- Defined in `projects.json`
- Custom context per project
- Apollo learns project-specific patterns

### 4. Hephaestus UI
- Visual representation of CI states
- Real-time stress indicators
- Context injection interface

## Best Practices

### For Component Builders
1. Always use `TektonEnviron` for configuration
2. Let the registry handle all state persistence
3. Trust Apollo's staging recommendations
4. Implement Rhetor's context injections

### For CI Developers
1. Keep responses focused and efficient
2. Store meaningful context in exchanges
3. Monitor your CI's performance metrics
4. Collaborate with Apollo for optimization

## Security Considerations

1. **File-based Locking** - Prevents concurrent write corruption
2. **Local Storage Only** - No sensitive data leaves the system
3. **Atomic Updates** - Complete exchanges stored together
4. **Graceful Degradation** - CIs work even if registry fails

## Future Enhancements

1. **Distributed Registry** - For multi-machine Tekton deployments
2. **ML-based Predictions** - Apollo learning from historical patterns
3. **Automatic Scaling** - Spin up additional CIs under stress
4. **Cross-CI Routing** - Automatic handoff between specialists