# Rhetor Simplification (July 2025)

## Overview

We simplified Rhetor's CI management by removing the complex discovery service and using direct configuration from `tekton_components.yaml`.

## Changes Made

### 1. Created Simple CI Manager (`rhetor/core/ai_manager.py`)
- Reads components directly from `tekton_components.yaml`
- Calculates CI ports using standard formula: `ai_port = (component_port - 8000) + 45000`
- Simple health checks by attempting socket connection
- Manages "roster" of active CIs

### 2. Simplified Endpoints (`rhetor/api/ai_specialist_endpoints_simple.py`)
- `/api/v1/ai/specialists` - List all CI specialists
- `/api/v1/ai/roster` - Manage hired CIs
- `/api/v1/ai/specialists/{ai_id}/hire` - Add to roster
- `/api/v1/ai/specialists/{ai_id}/fire` - Remove from roster
- `/api/v1/ai/specialists/{ai_id}/message` - Send messages
- `/api/v1/ai/find/{role}` - Find CI by role/category

### 3. Simplified MCP Integration (`rhetor/core/mcp/tools_integration_simple.py`)
- Direct CI communication via `simple_ai`
- Team chat coordination
- Simple role-based routing

### 4. Simplified Streaming (`rhetor/api/specialist_streaming_endpoints_simple.py`)
- Simulated streaming (since CIs don't stream yet)
- Multi-AI queries
- Real-time health monitoring

## Benefits

1. **No Complex Discovery** - Everything uses fixed ports
2. **Single Source of Truth** - `tekton_components.yaml`
3. **Simpler Code** - Removed abstraction layers
4. **Faster Startup** - No discovery overhead
5. **Easier Debugging** - Direct, simple logic

## Migration

### Files Created:
- `rhetor/core/ai_manager.py`
- `rhetor/api/ai_specialist_endpoints_simple.py`
- `rhetor/core/mcp/tools_integration_simple.py`
- `rhetor/api/specialist_streaming_endpoints_simple.py`

### Files Updated:
- `rhetor/api/app.py` - Use simplified versions
- `rhetor/api/team_chat_endpoints.py` - Use simplified integration

### Files to Remove (Old Versions):
- `rhetor/api/ai_specialist_endpoints_unified.py`
- `rhetor/core/mcp/tools_integration_unified.py`
- `rhetor/api/specialist_streaming_endpoints.py`
- `shared/ai/ai_discovery_service.py` (once nothing uses it)

## Testing

The simplified CI manager was tested successfully:
- Lists all 18 CI specialists
- Calculates correct ports
- Health checks work
- Roster management works
- Message sending works
- Role-based discovery works

## Next Steps

1. **Restart Rhetor** to load the simplified endpoints
2. **Remove old files** once confirmed working
3. **Update any remaining imports** in other components

## Key Insight

The entire "discovery" concept was unnecessary complexity. With fixed ports and a single configuration file, we can achieve the same functionality with much simpler code.