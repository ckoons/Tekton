# Shared MCP Implementation

This package provides a standardized implementation of the Model Context Protocol (MCP) v2 for all Tekton components.

## Overview

The shared MCP library makes it easy for Tekton components to:
- Expose tools and capabilities to CI assistants
- Register with Hermes as the central MCP aggregator
- Handle tool execution requests
- Manage contexts and state

## Quick Start

### Basic Usage

```python
from shared.mcp import MCPService, MCPConfig
from shared.mcp.tools import HealthCheckTool, ComponentInfoTool

class MyComponentMCP(MCPService):
    """MCP implementation for MyComponent."""
    
    async def register_default_tools(self):
        """Register component-specific tools."""
        # Register standard tools
        health_tool = HealthCheckTool(self.component_name)
        await self.register_tool(
            name=health_tool.name,
            description=health_tool.description,
            input_schema=health_tool.get_input_schema(),
            handler=health_tool
        )
        
        # Register custom tool
        await self.register_tool(
            name="my_custom_tool",
            description="Does something specific to my component",
            input_schema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "First parameter"}
                },
                "required": ["param1"]
            },
            handler=self.handle_custom_tool
        )
    
    async def handle_custom_tool(self, parameters, context=None):
        """Handle custom tool execution."""
        param1 = parameters.get("param1")
        # Do something with the parameter
        return {"result": f"Processed: {param1}"}

# Initialize and run
async def main():
    config = MCPConfig.from_env("mycomponent")
    mcp = MyComponentMCP(
        component_name="mycomponent",
        component_version="1.0.0",
        hermes_url=config.hermes_url
    )
    await mcp.initialize()
```

### Using the Hermes Client

```python
from shared.mcp.client import HermesMCPClient

# Create client
client = HermesMCPClient(
    hermes_url="http://localhost:8001",
    component_name="mycomponent",
    component_version="1.0.0"
)

# Register a tool
tool_id = await client.register_tool(
    name="my_tool",
    description="My tool description",
    input_schema={
        "type": "object",
        "properties": {
            "input": {"type": "string"}
        }
    },
    handler=my_tool_handler
)

# Execute a remote tool
result = await client.execute_remote_tool(
    tool_id="othercomponent.their_tool",
    parameters={"param": "value"}
)
```

### Creating Custom Tools

```python
from shared.mcp.base import MCPTool

class MyCustomTool(MCPTool):
    """Custom tool implementation."""
    
    name = "my_custom_tool"
    description = "Does something custom"
    tags = ["custom", "example"]
    
    async def execute(self, input_text: str, options: dict = None) -> dict:
        """Execute the tool."""
        # Process input
        result = process_input(input_text, options)
        
        return {
            "output": result,
            "metadata": {"processed_at": time.time()}
        }
```

## Architecture

### Base Classes

- **MCPService**: Base class for implementing MCP services
- **MCPTool**: Base class for defining tools
- **SimpleMCPTool**: Wrapper for converting functions to tools

### Standard Tools

- **HealthCheckTool**: Standard health check implementation
- **ComponentInfoTool**: Component information tool
- **GetConfigTool**: Configuration retrieval tool
- **SetConfigTool**: Configuration update tool

### Client

- **HermesMCPClient**: Client for registering with and connecting to Hermes

### Configuration

- **MCPConfig**: Configuration management with environment variable support

## Configuration

MCP behavior can be configured through environment variables:

```bash
# Hermes connection
HERMES_URL=http://localhost:8001
MCP_HERMES_TIMEOUT=30
MCP_AUTO_REGISTER=true

# Tool settings
MCP_ENABLE_DEFAULT_TOOLS=true
MCP_TOOL_PREFIX=mycomponent
MCP_TOOL_TIMEOUT=60

# Context settings
MCP_MAX_CONTEXTS=100
MCP_CONTEXT_TTL=3600

# Performance
MCP_MAX_CONCURRENT_TOOLS=10

# Security
MCP_REQUIRE_AUTH=false
MCP_ALLOWED_ORIGINS=*
```

## Integration with FastAPI

```python
from fastapi import FastAPI, Depends
from shared.mcp import MCPService

app = FastAPI()
mcp_service = MyComponentMCP(...)

@app.on_event("startup")
async def startup():
    await mcp_service.initialize()

@app.on_event("shutdown")
async def shutdown():
    await mcp_service.shutdown()

@app.get("/mcp/tools")
async def list_tools():
    return mcp_service.list_tools()

@app.post("/mcp/tools/{tool_id}/execute")
async def execute_tool(tool_id: str, parameters: dict):
    return await mcp_service.execute_tool(tool_id, parameters)
```

## Best Practices

1. **Tool Naming**: Use descriptive names that indicate the tool's function
2. **Input Schemas**: Always provide complete JSON schemas for tool inputs
3. **Error Handling**: Tools should return structured error responses
4. **Async Implementation**: Use async/await for all I/O operations
5. **Context Management**: Clean up contexts when no longer needed
6. **Security**: Validate all inputs and implement appropriate access controls

## Testing

```python
import pytest
from shared.mcp import MCPService

@pytest.mark.asyncio
async def test_tool_registration():
    mcp = MyComponentMCP("test", "1.0.0")
    await mcp.initialize()
    
    tools = mcp.list_tools()
    assert len(tools) > 0
    
    # Test tool execution
    result = await mcp.execute_tool(
        "test.my_tool",
        {"param": "value"}
    )
    assert result["success"]
```