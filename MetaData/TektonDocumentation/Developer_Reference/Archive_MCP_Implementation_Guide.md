# MCP (Model Context Protocol) Implementation Guide

## Overview

The Model Context Protocol (MCP) v2 is a standardized protocol that allows CI assistants to interact with tools and services. In Tekton, MCP enables components to expose their functionality as tools that can be discovered and executed by CI assistants like Claude.

## Architecture

### Central Aggregator Pattern

Tekton uses a centralized MCP architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   CI Assistant  │     │   CI Assistant  │     │   CI Assistant  │
│    (Claude)     │     │   (Other LLM)   │     │    (Local)      │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                         │
         └───────────────────────┴─────────────────────────┘
                                 │
                                 │ MCP v2 Protocol
                                 │
                          ┌──────▼──────┐
                          │   HERMES    │
                          │  MCP Hub    │
                          │  Port 8001  │
                          └──────┬──────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼───────┐       ┌────────▼────────┐     ┌────────▼────────┐
│    Budget     │       │     Engram      │     │     Athena      │
│  Port 8013    │       │   Port 8000     │     │   Port 8005     │
│               │       │                 │     │                 │
│ Tools:        │       │ Tools:          │     │ Tools:          │
│ - cost_analysis│      │ - store_memory  │     │ - query_graph   │
│ - optimization │      │ - recall_memory │     │ - analyze_rels  │
└───────────────┘       └─────────────────┘     └─────────────────┘
```

### Key Components

1. **Hermes** - Central MCP aggregator at `/api/mcp/v2`
   - Collects tools from all components
   - Routes tool execution requests
   - Manages contexts across components

2. **Shared MCP Library** - `/shared/mcp/`
   - Base classes for consistent implementation
   - Standard tools (health, info, config)
   - Hermes client for registration
   - Configuration management

3. **Component MCP Services**
   - Inherit from `MCPService`
   - Register component-specific tools
   - Handle tool execution requests

## Implementation Steps

### 1. Add MCP Dependencies

```python
# In your component's requirements.txt
tekton-shared>=0.1.0  # Includes MCP support
```

### 2. Create MCP Service

```python
# mycomponent/mcp/service.py
from shared.mcp import MCPService, MCPConfig
from shared.mcp.tools import HealthCheckTool, ComponentInfoTool

class MyComponentMCP(MCPService):
    """MCP implementation for MyComponent."""
    
    async def register_default_tools(self):
        """Register component-specific tools."""
        # Register standard tools
        health_tool = HealthCheckTool(
            self.component_name,
            health_check_func=self.check_health
        )
        await self.register_tool(
            name=health_tool.name,
            description=health_tool.description,
            input_schema=health_tool.get_input_schema(),
            handler=health_tool
        )
        
        info_tool = ComponentInfoTool(
            self.component_name,
            self.component_version,
            "Description of my component",
            capabilities=["capability1", "capability2"]
        )
        await self.register_tool(
            name=info_tool.name,
            description=info_tool.description,
            input_schema=info_tool.get_input_schema(),
            handler=info_tool
        )
        
        # Register custom tools
        await self.register_tool(
            name="my_custom_tool",
            description="Does something specific",
            input_schema={
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "Input parameter"
                    }
                },
                "required": ["input"]
            },
            handler=self.handle_custom_tool
        )
    
    async def handle_custom_tool(self, parameters, context=None):
        """Handle custom tool execution."""
        input_data = parameters.get("input")
        # Process the input
        result = await self.process_input(input_data)
        return {"result": result}
    
    async def check_health(self):
        """Custom health check implementation."""
        # Check component-specific health
        return {
            "database": "connected",
            "cache": "healthy",
            "custom_metric": 42
        }
```

### 3. Integrate with FastAPI

```python
# mycomponent/api/app.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from mycomponent.mcp.service import MyComponentMCP
from shared.mcp import MCPConfig

# Global MCP service instance
mcp_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global mcp_service
    
    # Initialize MCP service
    config = MCPConfig.from_env("mycomponent")
    mcp_service = MyComponentMCP(
        component_name="mycomponent",
        component_version="1.0.0",
        hermes_url=config.hermes_url
    )
    
    # Initialize and register with Hermes
    await mcp_service.initialize()
    
    # Store in app state
    app.state.mcp_service = mcp_service
    
    yield
    
    # Cleanup
    await mcp_service.shutdown()

app = FastAPI(lifespan=lifespan)

# Optional: Expose local MCP endpoints
@app.get("/mcp/tools")
async def list_tools():
    """List available MCP tools."""
    return mcp_service.list_tools()

@app.post("/mcp/tools/{tool_id}/execute")
async def execute_tool(tool_id: str, parameters: dict):
    """Execute a tool locally."""
    return await mcp_service.execute_tool(tool_id, parameters)
```

### 4. Create Custom Tools

```python
# mycomponent/mcp/tools.py
from shared.mcp.base import MCPTool
from typing import Optional, List

class DataProcessingTool(MCPTool):
    """Tool for processing data."""
    
    name = "process_data"
    description = "Process data with specified algorithm"
    tags = ["data", "processing", "analysis"]
    
    def __init__(self, processor):
        self.processor = processor
        super().__init__()
    
    async def execute(
        self,
        data: List[dict],
        algorithm: str = "default",
        options: Optional[dict] = None
    ) -> dict:
        """
        Process data with specified algorithm.
        
        Args:
            data: List of data items to process
            algorithm: Processing algorithm to use
            options: Optional processing options
            
        Returns:
            Processing results
        """
        # Validate inputs
        if not data:
            return {"error": "No data provided"}
        
        # Process data
        results = await self.processor.process(
            data=data,
            algorithm=algorithm,
            options=options or {}
        )
        
        return {
            "success": True,
            "processed_count": len(results),
            "results": results
        }
    
    def get_input_schema(self):
        """Override to provide detailed schema."""
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Data items to process"
                },
                "algorithm": {
                    "type": "string",
                    "enum": ["default", "fast", "accurate"],
                    "default": "default",
                    "description": "Processing algorithm"
                },
                "options": {
                    "type": "object",
                    "description": "Additional processing options"
                }
            },
            "required": ["data"]
        }
```

## Configuration

### Environment Variables

```bash
# Hermes connection
HERMES_URL=http://localhost:8001
HERMES_HOST=localhost
HERMES_PORT=8001

# MCP settings
MCP_AUTO_REGISTER=true
MCP_ENABLE_DEFAULT_TOOLS=true
MCP_TOOL_PREFIX=mycomponent
MCP_TOOL_TIMEOUT=60
MCP_MAX_CONCURRENT_TOOLS=10

# Context management
MCP_MAX_CONTEXTS=100
MCP_CONTEXT_TTL=3600

# Security
MCP_REQUIRE_AUTH=false
MCP_ALLOWED_ORIGINS=*
```

### Configuration Object

```python
from shared.mcp import MCPConfig

# Load from environment
config = MCPConfig.from_env("mycomponent")

# Or create manually
config = MCPConfig(
    component_name="mycomponent",
    component_version="1.0.0",
    hermes_url="http://localhost:8001",
    enable_default_tools=True,
    tool_timeout=60
)
```

## Best Practices

### 1. Tool Design

- **Clear Naming**: Use descriptive names that indicate function
- **Comprehensive Schemas**: Provide complete JSON schemas with descriptions
- **Error Handling**: Return structured errors, not exceptions
- **Async First**: Use async/await for all I/O operations
- **Idempotency**: Design tools to be safely retryable

### 2. Security

```python
async def handle_sensitive_tool(self, parameters, context=None):
    """Example of secure tool implementation."""
    # Validate permissions
    if context and not context.get("authenticated"):
        return {"error": "Authentication required"}
    
    # Validate inputs
    if not self.validate_input(parameters):
        return {"error": "Invalid input parameters"}
    
    # Rate limiting
    if not await self.check_rate_limit(context):
        return {"error": "Rate limit exceeded"}
    
    # Process safely
    try:
        result = await self.process_secure(parameters)
        return {"success": True, "result": result}
    except Exception as e:
        # Don't expose internal errors
        logger.error(f"Tool error: {e}")
        return {"error": "Processing failed"}
```

### 3. Performance

```python
class CachedTool(MCPTool):
    """Example of tool with caching."""
    
    def __init__(self):
        self.cache = {}
        super().__init__()
    
    async def execute(self, query: str) -> dict:
        # Check cache
        cache_key = self.get_cache_key(query)
        if cache_key in self.cache:
            return {
                "result": self.cache[cache_key],
                "cached": True
            }
        
        # Process and cache
        result = await self.expensive_operation(query)
        self.cache[cache_key] = result
        
        return {
            "result": result,
            "cached": False
        }
```

### 4. Testing

```python
import pytest
from mycomponent.mcp.service import MyComponentMCP

@pytest.mark.asyncio
async def test_mcp_initialization():
    """Test MCP service initialization."""
    mcp = MyComponentMCP("test", "1.0.0")
    await mcp.initialize()
    
    # Check tools are registered
    tools = mcp.list_tools()
    assert len(tools) > 0
    assert any(t["name"] == "health_check" for t in tools)

@pytest.mark.asyncio
async def test_custom_tool():
    """Test custom tool execution."""
    mcp = MyComponentMCP("test", "1.0.0")
    await mcp.initialize()
    
    # Execute tool
    result = await mcp.execute_tool(
        "test.my_custom_tool",
        {"input": "test data"}
    )
    
    assert result["success"]
    assert "result" in result
```

## Troubleshooting

### Common Issues

1. **Tools not appearing in Hermes**
   - Check Hermes is running: `curl http://localhost:8001/health`
   - Verify registration: Check component logs for registration errors
   - Ensure `MCP_AUTO_REGISTER=true`

2. **Tool execution failures**
   - Check tool handler is async
   - Verify input schema matches parameters
   - Check component logs for exceptions

3. **Connection errors**
   - Verify `HERMES_URL` is correct
   - Check network connectivity
   - Ensure Hermes MCP service is initialized

### Debug Endpoints

```python
# Add debug endpoints to your component
@app.get("/debug/mcp/status")
async def mcp_status():
    """Get MCP service status."""
    return {
        "initialized": mcp_service is not None,
        "tool_count": len(mcp_service.tools) if mcp_service else 0,
        "hermes_url": mcp_service.hermes_url if mcp_service else None,
        "capabilities": mcp_service.get_capabilities() if mcp_service else {}
    }

@app.get("/debug/mcp/tools")
async def debug_tools():
    """Get detailed tool information."""
    if not mcp_service:
        return {"error": "MCP service not initialized"}
    
    return {
        tool_id: {
            "spec": tool["spec"],
            "has_handler": tool["handler"] is not None
        }
        for tool_id, tool in mcp_service.tools.items()
    }
```

## Advanced Topics

### Context Management

```python
# Create persistent context
context_id = await mcp_service.create_context(
    data={
        "user_id": "user123",
        "session_id": "session456",
        "preferences": {"theme": "dark"}
    }
)

# Update context
await mcp_service.update_context(
    context_id,
    {"last_action": "processed_data"}
)

# Use context in tools
async def handle_contextual_tool(self, parameters, context=None):
    if context:
        user_prefs = context.get("data", {}).get("preferences", {})
        # Adjust behavior based on preferences
```

### Tool Composition

```python
class ComposedTool(MCPTool):
    """Tool that uses other tools."""
    
    def __init__(self, mcp_service):
        self.mcp = mcp_service
        super().__init__()
    
    async def execute(self, workflow: List[dict]) -> dict:
        """Execute a workflow of tools."""
        results = []
        
        for step in workflow:
            tool_id = step["tool"]
            params = step["parameters"]
            
            # Execute tool
            result = await self.mcp.execute_tool(tool_id, params)
            results.append(result)
            
            # Check for errors
            if not result.get("success"):
                return {
                    "success": False,
                    "error": f"Step {tool_id} failed",
                    "results": results
                }
        
        return {
            "success": True,
            "results": results
        }
```

## Migration Guide

For components with existing tool implementations:

1. **Identify existing tools** - List current functionality to expose
2. **Map to MCP tools** - Convert to MCPTool subclasses
3. **Update schemas** - Ensure JSON Schema compliance
4. **Add standard tools** - Include health, info, config tools
5. **Test with Hermes** - Verify registration and execution
6. **Update documentation** - Document available tools

## Resources

- [MCP v2 Specification](https://github.com/anthropics/mcp)
- [Shared MCP Library](/shared/mcp/README.md)
- [Hermes MCP Documentation](/MetaData/ComponentDocumentation/Hermes/MCP_INTEGRATION.md)
- [Example Implementation](https://github.com/tekton/examples/mcp)