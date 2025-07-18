# Landmark Integration Guide for Tekton Components

## Quick Start

To add landmarks to your Tekton component:

1. **Add landmarks to your imports**:
```python
from landmarks import (
    architecture_decision,
    performance_boundary,
    api_contract,
    danger_zone,
    integration_point,
    state_checkpoint
)
```

2. **Mark your code** with appropriate decorators
3. **Test** that your component still works correctly

## Integration Steps by Component

### 1. Shared Utilities ✅
Already instrumented with landmarks:
- `global_config.py` - Singleton pattern, centralized config decision
- `graceful_shutdown.py` - Shutdown pattern, Hermes integration
- `standard_component.py` - Component lifecycle pattern
- `mcp_helpers.py` - MCP/AI integration pattern

### 2. Hermes (Message Bus)
Priority landmarks to add:
```python
# In hermes/core/message_bus.py
@architecture_decision(
    title="WebSocket pub/sub architecture",
    rationale="Real-time updates with <100ms latency",
    alternatives_considered=["REST polling", "gRPC streaming"],
    impacts=["scalability", "client_complexity"]
)
class MessageBus:
    pass

# In hermes/api/websocket.py
@performance_boundary(
    title="WebSocket message processing",
    sla="<50ms per message",
    optimization_notes="Async processing, batching"
)
async def process_message(message):
    pass
```

### 3. Apollo (Orchestration)
Priority landmarks:
```python
# In apollo/core/action_planner.py
@danger_zone(
    title="Complex action planning logic",
    risk_level="high",
    risks=["Infinite loops", "Resource exhaustion"],
    mitigation="Timeout and resource limits"
)
class ActionPlanner:
    pass

# In apollo/core/token_budget.py
@state_checkpoint(
    title="Token budget tracking",
    state_type="runtime",
    persistence=True,
    consistency_requirements="Atomic updates"
)
class TokenBudget:
    pass
```

### 4. Engram (Memory)
Priority landmarks:
```python
# In engram/core/memory_manager.py
@architecture_decision(
    title="Multi-backend memory storage",
    rationale="Support both FAISS and LanceDB for flexibility",
    alternatives_considered=["Single backend", "Custom implementation"],
    impacts=["complexity", "performance", "flexibility"]
)
class MemoryManager:
    pass

# In engram/api/mcp_server.py
@api_contract(
    title="Memory storage endpoint",
    endpoint="/api/store",
    method="POST",
    request_schema={"content": "string", "metadata": "object"}
)
async def store_memory(request):
    pass
```

### 5. Prometheus (LLM Adapter)
Priority landmarks:
```python
# In prometheus/core/llm_chain.py
@performance_boundary(
    title="LLM request handling",
    sla="<30s timeout",
    optimization_notes="Retry logic, fallback models"
)
async def execute_llm_request(prompt):
    pass

# In prometheus/core/fallback.py
@architecture_decision(
    title="Multi-provider fallback chain",
    rationale="Ensure reliability across provider outages",
    alternatives_considered=["Single provider", "Manual switching"],
    impacts=["reliability", "cost", "complexity"]
)
class FallbackChain:
    pass
```

## Best Practices

### 1. **Landmark Placement Priority**

Mark these first:
- ✅ Architectural decisions (the "why")
- ✅ Performance boundaries (SLAs, timeouts)
- ✅ API contracts (external interfaces)
- ✅ Complex/dangerous code sections
- ✅ Integration points between components
- ✅ State management (singletons, caches)

### 2. **Granularity Guidelines**

- **Classes**: Mark if they embody a pattern or decision
- **Functions**: Mark if they're public APIs or complex logic
- **Methods**: Mark if they have performance requirements or side effects

### 3. **Metadata Standards**

Always include:
- Clear, concise titles
- Rationale for decisions
- Performance SLAs where applicable
- Risk levels for dangerous code
- Integration protocols

### 4. **Testing After Integration**

1. Run component tests to ensure decorators don't break functionality
2. Verify landmarks are registered: `LandmarkRegistry.list(component="YourComponent")`
3. Test that the component starts and operates normally

## Common Patterns to Landmark

### Singleton Pattern
```python
@state_checkpoint(
    title="Component singleton",
    state_type="singleton",
    persistence=False,
    consistency_requirements="Thread-safe access"
)
class ComponentManager:
    _instance = None
```

### API Endpoint
```python
@api_contract(
    title="Health check endpoint",
    endpoint="/health",
    method="GET",
    response_schema={"status": "string", "version": "string"}
)
async def health_check():
    pass
```

### WebSocket Handler
```python
@integration_point(
    title="WebSocket message handler",
    target_component="clients",
    protocol="WebSocket",
    data_flow="Bidirectional message stream"
)
async def handle_websocket(websocket):
    pass
```

### Resource Manager
```python
@danger_zone(
    title="Resource allocation",
    risk_level="medium",
    risks=["Resource leak", "Deadlock"],
    mitigation="Timeout and cleanup handlers"
)
async def allocate_resources():
    pass
```

## Troubleshooting

### Import Errors
If you get import errors, ensure landmarks is in your Python path:
```python
import sys
sys.path.append('/path/to/Tekton')
from landmarks import architecture_decision
```

### Decorator Not Working
- Check that you're decorating the function/class definition, not the call
- Ensure the decorator is above other decorators
- Verify the landmark system is initialized

### Performance Impact
Landmarks have minimal overhead:
- Decorators run once at import time
- No runtime performance impact
- Storage is asynchronous

## Next Steps

1. Start with high-value landmarks (architectural decisions)
2. Add incrementally - don't landmark everything at once
3. Use CI memory to track what's been landmarked
4. Share patterns with the team

Remember: Landmarks are for persistent architectural knowledge, not temporary TODOs!