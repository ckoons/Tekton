# MCP Integration Guide for Tekton Components

This guide explains how to implement and test MCP (Model Context Protocol) integration in Tekton components. Updated with features from the Rhetor AI Integration Sprint Phase 3/4.

## Overview

Tekton uses a centralized MCP architecture where:
- **Hermes** acts as the central MCP aggregator (port 8001)
- All components register their tools with Hermes
- External clients (like Claude Desktop) connect to Hermes to access all component tools
- Components maintain their own FastMCP implementations while also registering with Hermes
- **NEW**: Live component integration allows MCP tools to interact with running component instances
- **NEW**: AI orchestration support through Rhetor's MCP tools
- **NEW**: Real-time streaming for long-running operations

## Architecture

```
Claude Desktop → Hermes MCP Bridge → Hermes API → Component Tools
                     (STDIO)         (HTTP/8001)     (HTTP/8000+)
```

## Implementing MCP in a Component

### 1. Basic Setup

Every component should have MCP tools organized in a `core/mcp/tools.py` file:

```python
from fastmcp import FastMCP

# Create FastMCP instance
mcp = FastMCP(
    name=f"{COMPONENT_NAME}-mcp-server",
    dependencies=["httpx"]
)

# Define tools using decorators
@mcp.tool(description="Check component health")
async def health_check() -> dict:
    """Check if the component is healthy."""
    return {"status": "healthy", "component": COMPONENT_NAME}

@mcp.tool(description="Get component information")
async def component_info() -> dict:
    """Get basic component information."""
    return {
        "name": COMPONENT_NAME,
        "version": "0.1.0",
        "description": f"{COMPONENT_NAME} component"
    }
```

### 2. Tool Registration Function

Create a `get_all_tools()` function that returns all tools:

```python
def get_all_tools():
    """Get all MCP tools for registration."""
    tools = []
    
    # Add FastMCP decorated tools
    for tool in mcp.list_tools():
        tools.append({
            "id": f"{COMPONENT_NAME}.{tool.name}",
            "name": tool.name,
            "description": tool.description,
            "schema": tool.get_schema()
        })
    
    # Add any additional tools
    tools.extend([
        {
            "id": f"{COMPONENT_NAME}.health_check",
            "name": "health_check",
            "description": "Check component health"
        },
        {
            "id": f"{COMPONENT_NAME}.component_info",
            "name": "component_info",
            "description": "Get component information"
        }
    ])
    
    return tools
```

### 3. MCP Endpoint Setup

In your API app (`api/app.py`), add the MCP endpoints:

```python
from fastapi import FastAPI
from .mcp_endpoints import mcp_router

app = FastAPI()

# Add MCP router
app.include_router(mcp_router, prefix="/api/mcp/v2", tags=["mcp"])
```

Create `api/mcp_endpoints.py`:

```python
from fastapi import APIRouter
from ..core.mcp.tools import get_all_tools, mcp

router = APIRouter()

@router.get("/tools")
async def list_tools():
    """List all available MCP tools."""
    return get_all_tools()

@router.post("/tools/{tool_id}/execute")
async def execute_tool(tool_id: str, request: dict):
    """Execute a specific tool."""
    # Implementation depends on your tool structure
    pass
```

### 4. Hermes Registration

Components automatically register with Hermes on startup. Ensure your startup includes:

```python
# In your main startup
async def register_with_hermes():
    """Register component and tools with Hermes."""
    try:
        # Register component
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://localhost:8001/api/registration/register",
                json={
                    "id": f"{COMPONENT_NAME}-api",
                    "name": COMPONENT_NAME,
                    "type": "service",
                    "status": "running",
                    "endpoint": f"http://localhost:{PORT}",
                    "health_endpoint": f"http://localhost:{PORT}/health"
                }
            )
            
        # Register MCP tools
        tools = get_all_tools()
        for tool in tools:
            await client.post(
                "http://localhost:8001/api/mcp/v2/tools/register",
                json=tool
            )
    except Exception as e:
        logger.error(f"Failed to register with Hermes: {e}")
```

## Testing MCP Integration

### 1. Component-Level Testing

Test your component's MCP tools directly:

```bash
# List tools
curl http://localhost:8000/api/mcp/v2/tools

# Execute a tool
curl -X POST http://localhost:8000/api/mcp/v2/tools/component.health_check/execute \
  -H "Content-Type: application/json" \
  -d '{"parameters": {}}'
```

### 2. Hermes Integration Testing

Use the comprehensive test script:

```bash
# Basic test
./tests/test_mcp_installation.sh

# Comprehensive test (includes all tools)
./tests/test_mcp_installation.sh --comprehensive

# Test specific component
./tests/test_mcp_installation.sh --component engram

# Generate HTML report
./tests/test_mcp_installation.sh --comprehensive --report mcp-test-report.txt
```

### 3. Claude Desktop Testing

1. Install the MCP bridge:
```bash
./scripts/install_tekton_mcps.sh
```

2. Test the bridge directly:
```bash
./tests/test_claude_mcp.sh
```

3. Restart Claude Desktop and verify tools are available

## Common Issues and Solutions

### Tool Not Appearing in Hermes

1. **Check tool registration**: Ensure `get_all_tools()` returns your tools
2. **Verify tool naming**: Tool names should not include the component prefix
3. **Check imports**: Ensure tools.py is properly imported during startup

### Duplicate Tool Registration

- Remove explicit basic tool registration if using FastMCP decorators
- FastMCP automatically handles `health_check` and `component_info`

### Tool Execution Failures

1. **Check tool ID format**: Should be `component.tool_name`
2. **Verify parameters**: Ensure required parameters are provided
3. **Check async handling**: Tools must be properly awaited

### Claude Desktop Connection Issues

1. **Protocol errors**: Ensure stdio bridge returns proper MCP format
2. **Missing methods**: Implement handlers for `prompts/list`, `resources/list`
3. **Check logs**: Bridge logs to stderr, check Claude's debug output

## Advanced Features (Phase 3/4)

### Live Component Integration

MCP tools can now interact with live component state:

```python
from tekton.mcp.fastmcp.decorators import mcp_tool

@mcp_tool(
    name="GetLiveMetrics",
    description="Get real-time metrics from component",
    tags=["monitoring", "live"],
    category="diagnostics"
)
async def get_live_metrics() -> Dict[str, Any]:
    """Get live metrics from running component."""
    # Import here to avoid circular imports
    from mycomponent.api.app import app
    
    if hasattr(app.state, "metrics_collector"):
        metrics = await app.state.metrics_collector.get_current()
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    return {"success": False, "error": "Metrics collector not initialized"}
```

### AI Orchestration Integration

Leverage Rhetor's AI specialists for intelligent tool behavior:

```python
@mcp_tool(
    name="AnalyzeWithAI",
    description="Analyze data using AI specialists",
    tags=["ai", "analysis"],
    category="intelligence"
)
async def analyze_with_ai(
    data: Dict[str, Any],
    specialist_type: str = "data-analyst"
) -> Dict[str, Any]:
    """Use Rhetor AI specialists for analysis."""
    import httpx
    
    async with httpx.AsyncClient() as client:
        # Call Rhetor's AI orchestration tools
        response = await client.post(
            "http://localhost:8003/api/mcp/v2/process",
            json={
                "tool_name": "SendMessageToSpecialist",
                "arguments": {
                    "specialist_id": specialist_type,
                    "message": f"Analyze this data: {json.dumps(data)}",
                    "message_type": "analysis_request"
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "analysis": result.get("result", {}).get("response"),
                "specialist": specialist_type
            }
    
    return {"success": False, "error": "AI service unavailable"}
```

### Streaming Support

Implement SSE streaming for long-running operations:

```python
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import asyncio

# Add streaming endpoint to your MCP router
@router.post("/stream")
async def stream_mcp_tool(request: MCPStreamRequest) -> EventSourceResponse:
    """Stream tool execution with progress updates."""
    tool_name = request.tool_name
    arguments = request.arguments
    
    async def event_generator():
        # Send initial progress
        yield json.dumps({
            "type": "progress",
            "data": {"progress": 0, "message": f"Starting {tool_name}"}
        })
        
        # Execute tool with progress callbacks
        async for event in execute_tool_with_progress(tool_name, arguments):
            yield json.dumps(event)
        
        # Send completion
        yield json.dumps({
            "type": "complete",
            "data": {"message": "Tool execution completed"}
        })
    
    return EventSourceResponse(event_generator())
```

### Dynamic Specialist Creation

Create specialized AI assistants at runtime:

```python
@mcp_tool(
    name="CreateCustomSpecialist",
    description="Create a custom AI specialist for specific tasks",
    tags=["ai", "dynamic"],
    category="specialists"
)
async def create_custom_specialist(
    specialist_name: str,
    base_template: str = "code-reviewer",
    customization: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a custom AI specialist."""
    import httpx
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8003/api/mcp/v2/process",
            json={
                "tool_name": "CreateDynamicSpecialist",
                "arguments": {
                    "template_id": base_template,
                    "specialist_name": specialist_name,
                    "customization": customization or {},
                    "auto_activate": True
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("result", {})
    
    return {"success": False, "error": "Failed to create specialist"}
```

### Tool Progress Indicators

All AI orchestration tools now support progress indicators:

```python
@mcp_tool(
    name="ProcessBatch",
    description="Process batch with progress updates",
    progress_indicator=True  # Enable progress support
)
async def process_batch(items: List[str]) -> Dict[str, Any]:
    """Process items with progress updates."""
    results = []
    total = len(items)
    
    for i, item in enumerate(items):
        # Process item
        result = await process_single_item(item)
        results.append(result)
        
        # Emit progress (if streaming context available)
        if hasattr(asyncio.current_task(), 'progress_callback'):
            await asyncio.current_task().progress_callback({
                "progress": int((i + 1) / total * 100),
                "message": f"Processed {item}",
                "current": i + 1,
                "total": total
            })
    
    return {
        "success": True,
        "processed": len(results),
        "results": results
    }
```

## Best Practices

1. **Tool Naming**: Use descriptive, action-oriented names
2. **Tool Descriptions**: Provide clear, concise descriptions
3. **Parameter Validation**: Use Pydantic models for parameters
4. **Error Handling**: Return meaningful error messages
5. **Testing**: Test both direct and through-Hermes execution
6. **Live Integration**: Always check component state before accessing
7. **AI Usage**: Consider token costs when using AI orchestration
8. **Streaming**: Use for operations > 2 seconds
9. **Progress Updates**: Provide meaningful progress messages
10. **Error Recovery**: Handle AI service unavailability gracefully

## Example Implementation

See these components for reference implementations:
- **Engram**: Memory-related tools with complex parameters
- **Athena**: Knowledge graph tools with search capabilities
- **Rhetor**: LLM management tools with model selection, AI orchestration (Phase 3/4)
- **Synthesis**: Multi-component orchestration tools

### Rhetor's AI Orchestration Tools (Phase 3/4)

Rhetor now provides 30 MCP tools including:

#### Model Management Tools
- `GetAvailableModels` - List all available LLM models
- `SetDefaultModel` - Set the default model for operations
- `GetModelCapabilities` - Get detailed model capabilities
- `TestModelConnection` - Test connectivity to model providers
- `GetModelPerformance` - Get performance metrics for models
- `ManageModelRotation` - Configure model rotation strategies

#### Prompt Engineering Tools
- `CreatePromptTemplate` - Create reusable prompt templates
- `OptimizePrompt` - Optimize prompts for better performance
- `ValidatePromptSyntax` - Validate prompt syntax and structure
- `GetPromptHistory` - Retrieve prompt usage history
- `AnalyzePromptPerformance` - Analyze prompt effectiveness
- `ManagePromptLibrary` - Manage prompt template library

#### Context Management Tools
- `AnalyzeContextUsage` - Analyze context window usage
- `OptimizeContextWindow` - Optimize context for token efficiency
- `TrackContextHistory` - Track context changes over time
- `CompressContext` - Compress context to save tokens

#### AI Specialist Tools
- `ListAISpecialists` - List all available AI specialists
- `ActivateAISpecialist` - Activate a specialist for use
- `SendMessageToSpecialist` - Send messages to specialists
- `OrchestrateTeamChat` - Orchestrate multi-specialist conversations
- `GetSpecialistConversationHistory` - Get conversation history
- `ConfigureAIOrchestration` - Configure orchestration settings

#### Dynamic Specialist Tools (Phase 4B)
- `ListSpecialistTemplates` - List available specialist templates
- `CreateDynamicSpecialist` - Create specialists from templates
- `CloneSpecialist` - Clone existing specialists
- `ModifySpecialist` - Modify specialist configurations
- `DeactivateSpecialist` - Deactivate specialists
- `GetSpecialistMetrics` - Get specialist performance metrics

#### Streaming Tools (Phase 4A)
- `SendMessageToSpecialistStream` - Stream specialist responses
- `OrchestrateTeamChatStream` - Stream team chat conversations

## Debugging

Enable debug logging in the stdio bridge:
```python
logging.basicConfig(level=logging.DEBUG)
```

Check component logs:
```bash
tail -f .tekton/logs/component-name.log
```

Test Hermes aggregation:
```bash
curl http://localhost:8001/api/mcp/v2/tools | jq '.[] | select(.name | contains("your_tool"))'
```