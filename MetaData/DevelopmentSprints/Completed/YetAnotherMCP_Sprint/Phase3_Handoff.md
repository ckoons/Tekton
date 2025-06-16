# YetAnotherMCP Sprint - Phase 3 Handoff

## Sprint Overview
We are implementing MCP (Model Context Protocol) v2 support across all Tekton components to enable AI assistants to interact with component functionality through standardized tools.

## Current Status

### ✅ Phase 1 Complete: Fix Hermes MCP
- Fixed initialization bug where `await` was used on `message_bus.publish()` (not async)
- Fixed router mounting - MCP router must be included in `api_app` from `endpoints.py`
- Updated MCP endpoints to `/api/mcp/v2/*`
- Fixed state sharing between main app and api_app
- All MCP endpoints now working:
  - `/api/mcp/v2/health` ✅
  - `/api/mcp/v2/capabilities` ✅
  - `/api/mcp/v2/tools` ✅
  - `/api/mcp/v2/process` ✅

### ✅ Phase 2 Complete: Create Shared MCP Library
Created `/shared/mcp/` with:
- Base classes (`MCPService`, `MCPTool`)
- Common tools (health, info, config)
- Hermes client for registration
- Configuration management
- Comprehensive documentation

### 🚧 Phase 3: Migrate Components to Shared Library
This is your task - migrate existing Tekton components to use the new shared MCP implementation.

## Phase 3 Implementation Plan

### Components to Migrate (Priority Order)

1. **Athena** (Knowledge Graph) - HIGH PRIORITY
   - Current: Has basic MCP in `/Athena/athena/api/mcp.py`
   - Tools: query_graph, analyze_relationships, find_patterns
   - Action: Refactor to use shared library

2. **Budget** (Cost Management) - HIGH PRIORITY
   - Current: Has MCP in `/Budget/budget/api/mcp_endpoints.py`
   - Tools: analyze_costs, optimize_model_selection, get_usage_stats
   - Action: Migrate to shared patterns

3. **Engram** (Memory System) - HIGH PRIORITY
   - Current: Has FastMCP integration
   - Tools: store_memory, recall_memory, search_memories
   - Action: Keep FastMCP but ensure Hermes registration works

4. **Rhetor** (LLM Service) - MEDIUM PRIORITY
   - Current: Basic MCP structure exists
   - Tools: generate_text, select_model, stream_completion
   - Action: Implement full MCP service

5. **Sophia** (Embeddings) - MEDIUM PRIORITY
   - Current: Minimal MCP support
   - Tools: generate_embedding, semantic_search, cluster_texts
   - Action: Create MCP implementation

6. **Other Components** - LOW PRIORITY
   - Apollo, Ergon, Harmonia, Metis, Prometheus, Synthesis, Telos
   - Most have placeholder MCP or none
   - Action: Add basic MCP with standard tools

### Migration Steps for Each Component

1. **Update Dependencies**
   ```python
   # requirements.txt
   tekton-shared>=0.1.0  # Includes MCP support
   ```

2. **Create MCP Service**
   ```python
   # component/mcp/service.py
   from shared.mcp import MCPService
   from shared.mcp.tools import HealthCheckTool, ComponentInfoTool
   
   class ComponentMCP(MCPService):
       async def register_default_tools(self):
           # Register standard tools
           # Register component-specific tools
   ```

3. **Update app.py**
   ```python
   # Initialize MCP in lifespan
   from shared.mcp import MCPConfig
   mcp_config = MCPConfig.from_env("component")
   mcp_service = ComponentMCP(...)
   await mcp_service.initialize()
   ```

4. **Test Registration**
   - Start Hermes
   - Start component
   - Check `/api/mcp/v2/tools` shows component tools
   - Test tool execution

### Important Patterns to Follow

1. **Don't Hardcode Ports** - Use environment configuration
2. **Use Shared Tools** - Don't reimplement health/info tools
3. **Async Everything** - All tool handlers must be async
4. **Proper Error Handling** - Return structured errors, not exceptions
5. **Test with Hermes** - Ensure registration and discovery work

### Testing Checklist

For each component:
- [ ] Component starts without MCP errors
- [ ] Tools appear in Hermes at `/api/mcp/v2/tools`
- [ ] Health check tool works
- [ ] Component info tool works
- [ ] Custom tools execute successfully
- [ ] Errors return proper JSON responses

### Known Issues to Watch For

1. **Import Errors** - Ensure `shared` is in Python path
2. **Port Conflicts** - Use assigned ports from config
3. **Async/Await** - Remember `message_bus.publish()` is NOT async
4. **Registration Timing** - MCP must initialize after core services

### Files Created/Modified in Phase 1-2

**Phase 1 Fixes:**
- `/Hermes/hermes/core/mcp_service.py` - Fixed await bug
- `/Hermes/hermes/api/mcp_endpoints.py` - Updated router prefix
- `/Hermes/hermes/api/endpoints.py` - Added MCP router inclusion
- `/Hermes/hermes/api/app.py` - Fixed state sharing

**Phase 2 Library:**
- `/shared/mcp/` - Complete MCP implementation
- `/MetaData/TektonDocumentation/MCP_IMPLEMENTATION_GUIDE.md`
- `/MetaData/TektonDocumentation/Building_New_Tekton_Components/Backend_Implementation_Guide.md` - Added MCP section

### Resources

1. **MCP Implementation Guide**: `/MetaData/TektonDocumentation/MCP_IMPLEMENTATION_GUIDE.md`
2. **Shared MCP README**: `/shared/mcp/README.md`
3. **Test Script**: `/Hermes/tests/test_mcp_connectivity.py`
4. **Example Implementation**: Check Phase 1 fixes in Hermes

### Success Criteria

Phase 3 is complete when:
1. All high-priority components (Athena, Budget, Engram) use shared MCP
2. All components register with Hermes successfully
3. Basic tools (health, info) work for all components
4. Component-specific tools are accessible via Hermes
5. No hardcoded ports or URLs
6. All tests pass

### Questions for Session 1

If you need clarification:
1. Component priority can be adjusted based on user needs
2. FastMCP components (like Engram) should keep FastMCP but ensure Hermes registration
3. Focus on working implementations over perfect code
4. Test with real Hermes instance, not mocks

Good luck with Phase 3! The shared library should make this straightforward.