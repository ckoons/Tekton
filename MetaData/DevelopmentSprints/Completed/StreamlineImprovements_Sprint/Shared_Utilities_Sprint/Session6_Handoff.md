# Session 6 Handoff: Shutdown Endpoint Implementation

## Summary
Created a standardized shutdown endpoint implementation that can be easily added to Tekton components to enable graceful HTTP-based shutdown.

## What Was Done
1. Investigated existing shutdown patterns across Tekton components
2. Found that most components rely on process signals (SIGTERM/SIGKILL) rather than HTTP endpoints
3. Created `shared/utils/shutdown_endpoint.py` with reusable shutdown endpoint implementation

## Key Files Created
- `/shared/utils/shutdown_endpoint.py` - Standardized shutdown endpoint implementation

## Implementation Pattern

The shutdown endpoint provides:
- POST `/shutdown` - Primary shutdown endpoint
- POST `/api/shutdown` - Alternative endpoint
- GET `/shutdown/status` - Check shutdown support status

### How to Add to a Component

```python
# In your component's app.py file:
from fastapi import FastAPI
from shared.utils.shutdown_endpoint import add_shutdown_endpoint_to_app

app = FastAPI(...)

# Define cleanup tasks (optional)
async def cleanup_database():
    # Close database connections
    pass

async def cleanup_connections():
    # Close WebSocket connections, HTTP sessions, etc.
    pass

# Add shutdown endpoints to the app
add_shutdown_endpoint_to_app(
    app,
    "component_name",
    cleanup_tasks=[cleanup_database, cleanup_connections]
)
```

### Components That Need Shutdown Endpoints
Based on the enhanced_tekton_killer.py script, these components should have shutdown endpoints added:
1. **Athena** - `/Athena/athena/api/app.py`
2. **Apollo** - `/Apollo/apollo/api/app.py`
3. **Telos** - `/Telos/telos/api/app.py`
4. **Budget** - `/Budget/budget/api/app.py`
5. **Engram** - `/Engram/engram/api/server.py` or consolidated_server.py

### Example Implementation for Athena

```python
# In Athena/athena/api/app.py, add after creating the app:

from shared.utils.shutdown_endpoint import add_shutdown_endpoint_to_app

# ... existing code ...

# Add cleanup tasks specific to Athena
async def cleanup_athena():
    """Cleanup Athena-specific resources."""
    if knowledge_graph:
        await knowledge_graph.close()
    if query_engine:
        await query_engine.shutdown()
    # Add any other Athena-specific cleanup

# Add shutdown endpoints
add_shutdown_endpoint_to_app(
    app,
    "athena",
    cleanup_tasks=[cleanup_athena]
)
```

## Benefits
1. **Graceful Shutdown**: Components can clean up resources before terminating
2. **Consistent Interface**: All components use the same shutdown endpoints
3. **Better Integration**: Works seamlessly with enhanced_tekton_killer.py
4. **Resource Cleanup**: Prevents resource leaks and ensures proper cleanup

## Testing
To test the shutdown endpoint:
```bash
# Start the component
./run_athena.sh

# In another terminal, send shutdown request
curl -X POST http://localhost:8009/shutdown

# Or check shutdown status
curl http://localhost:8009/shutdown/status
```

## Next Steps
1. Add the shutdown endpoint to the 5 components listed above
2. Update enhanced_tekton_killer.py to remove these components from the skip list
3. Test shutdown functionality for each component
4. Consider adding shutdown endpoints to other components as needed