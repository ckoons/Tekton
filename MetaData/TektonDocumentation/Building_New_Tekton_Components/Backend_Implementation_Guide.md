# Backend Implementation Guide

## Overview

This guide provides detailed instructions for implementing the backend of a Tekton component, including the API server, business logic, CLI, and integrations.

## Project Setup

### 1. Create Directory Structure

```bash
mkdir -p MyComponent/{mycomponent,tests,ui,examples}
cd MyComponent
```

### 2. Create setup.py

```python
from setuptools import setup, find_packages

setup(
    name="mycomponent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "httpx",
        "pydantic",
        "rich",
        "python-dotenv",
        "aiohttp",
    ],
    entry_points={
        "console_scripts": [
            "mycomponent=mycomponent.cli.main:main",
        ],
    },
)
```

### 3. Create requirements.txt

```text
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
rich>=13.0.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
asyncio>=3.4.3
```

## Socket Reuse Requirements

### Why Socket Reuse is Mandatory

All Tekton components MUST use the socket reuse utilities to enable rapid restarts without "Address already in use" errors. This is especially critical on macOS where ports can remain in TIME_WAIT state for 60-120 seconds.

### Implementation Requirements

1. **In `__main__.py`**: Use `run_component_server()` from `shared.utils.socket_server`
2. **In `app.py` (if __name__ == "__main__")**: Use `run_with_socket_reuse()`
3. **Never use plain `uvicorn.run()`**: This will cause port binding issues on restart
4. **No hardcoded port fallbacks**: Always require port from environment

### Socket Reuse Benefits

- Enables `SO_REUSEADDR` socket option
- Configures fast graceful shutdown (3 seconds)
- Prevents "Address already in use" errors
- Allows immediate component restart after shutdown

## Environment Configuration

### Three-Tier Environment Priority

Tekton uses a three-tier environment system with the following priority (highest to lowest):

1. **System Environment Variables** - Set in shell or OS
2. **User Environment** - `~/.env.tekton` (overrides component defaults)
3. **Component Environment** - `ComponentName/.env` (component defaults)

Example:
```bash
# ComponentName/.env (lowest priority)
MYCOMPONENT_PORT=8015
MYCOMPONENT_LOG_LEVEL=INFO

# ~/.env.tekton (overrides component)
MYCOMPONENT_LOG_LEVEL=DEBUG
HERMES_URL=http://localhost:8001

# System environment (highest priority)
export MYCOMPONENT_PORT=8016  # This wins
```

The shared utilities handle this automatically via `get_component_config()`.

## API Implementation

### 1. Create Module Entry Point (__main__.py)

**IMPORTANT**: Every component MUST have a `__main__.py` file in the package root to support the enhanced launcher:

```python
# mycomponent/__main__.py
"""Entry point for python -m mycomponent"""
from mycomponent.api.app import app
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("MYCOMPONENT_PORT", 8015))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

This enables launching via:
- `python -m mycomponent` (REQUIRED for enhanced launcher)
- Direct module execution
- Consistent behavior across all components

### 2. Create app.py

```python
#!/usr/bin/env python3
"""
MyComponent API Server

This module implements the API server for the MyComponent,
following the Single Port Architecture pattern.
"""

import os
import sys
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tekton.models.base import TektonBaseModel

# REQUIRED: Add Tekton root to path
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utilities (NO LONGER OPTIONAL)
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.env_config import get_component_config
from shared.utils.errors import StartupError
from shared.utils.startup import component_startup, StartupMetrics
from shared.utils.shutdown import GracefulShutdown
from shared.utils.health_check import create_health_response
from shared.utils.shutdown_endpoint import add_shutdown_endpoint_to_app

# Import shared API utilities for consistency (REQUIRED as of API Consistency Sprint)
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)

# Component configuration (REQUIRED - API Consistency Standards)
COMPONENT_NAME = "MyComponent"  # Use PascalCase for display
COMPONENT_VERSION = "0.1.0"  # All components must use 0.1.0
COMPONENT_DESCRIPTION = "Brief description of component functionality"

# Use shared logger setup - DO NOT use logging.getLogger()
logger = setup_component_logging(COMPONENT_NAME.lower())

# Global state for registration and timing
# IMPORTANT: These MUST be declared at module level for proper cleanup
hermes_registration = None
heartbeat_task = None
start_time = None  # Track startup time for ready endpoint
is_registered_with_hermes = False  # Track registration status

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for MyComponent - REQUIRED pattern for all components"""
    # IMPORTANT: Must declare as global to access module-level variables
    global hermes_registration, heartbeat_task, start_time, is_registered_with_hermes
    
    # Define startup function
    async def mycomponent_startup():
        """Component-specific startup logic"""
        global hermes_registration, heartbeat_task, start_time, is_registered_with_hermes
        
        # Track startup time for ready endpoint
        import time
        start_time = time.time()
        
        try:
            # Get configuration - NEVER hardcode ports
            config = get_component_config()
            port = config.mycomponent.port if hasattr(config, 'mycomponent') else int(os.environ.get("MYCOMPONENT_PORT", 8015))
            
            # Store in app state for access in endpoints
            app.state.port = port
            app.state.start_time = datetime.utcnow()
            
            # Register with Hermes
            hermes_registration = HermesRegistration()
            
            logger.info(f"Attempting to register MyComponent with Hermes on port {port}")
            is_registered_with_hermes = await hermes_registration.register_component(
                component_name=COMPONENT_NAME.lower(),
                port=port,  # NEVER hardcode this value
                version=COMPONENT_VERSION,  # Use the constant
                capabilities=["capability1", "capability2"],  # Update with actual capabilities
                metadata={
                    "description": "MyComponent description",
                    "author": "Tekton Team"
                }
            )
            
            if is_registered_with_hermes:
                logger.info("Successfully registered with Hermes")
                heartbeat_task = asyncio.create_task(
                    heartbeat_loop(hermes_registration, COMPONENT_NAME, interval=30)
                )
            else:
                logger.warning("Failed to register with Hermes - continuing without registration")
                
            # Initialize your component's core functionality here
            # app.state.my_service = MyService()
            # await app.state.my_service.initialize()
            
        except Exception as e:
            logger.error(f"Error during MyComponent startup: {e}", exc_info=True)
            raise StartupError(str(e), COMPONENT_NAME, "STARTUP_FAILED")
    
    # Execute startup with metrics
    try:
        metrics = await component_startup(COMPONENT_NAME, mycomponent_startup, timeout=30)
        logger.info(f"MyComponent started successfully in {metrics.total_time:.2f}s")
    except Exception as e:
        logger.error(f"Failed to start MyComponent: {e}")
        raise
    
    # Create shutdown handler
    shutdown = GracefulShutdown(COMPONENT_NAME)
    
    # Register cleanup tasks
    async def cleanup_hermes():
        """Cleanup Hermes registration"""
        if heartbeat_task:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if hermes_registration and is_registered_with_hermes:
            await hermes_registration.deregister(COMPONENT_NAME.lower())
            logger.info("Deregistered from Hermes")
    
    shutdown.register_cleanup(cleanup_hermes)
    
    # Add other cleanup tasks as needed
    # async def cleanup_service():
    #     if hasattr(app.state, "my_service"):
    #         await app.state.my_service.cleanup()
    # shutdown.register_cleanup(cleanup_service)
    
    # IMPORTANT: Clean up any subprocess/multiprocessing tasks
    # async def cleanup_subprocesses():
    #     """Ensure all child processes are terminated"""
    #     if hasattr(app.state, "subprocess_pool"):
    #         # Terminate all subprocesses
    #         for proc in app.state.subprocess_pool:
    #             proc.terminate()
    #             await asyncio.sleep(0.1)
    #             if proc.poll() is None:
    #                 proc.kill()
    # shutdown.register_cleanup(cleanup_subprocesses)
    
    yield
    
    # Shutdown
    logger.info("Shutting down MyComponent API")
    await shutdown.shutdown_sequence(timeout=10)
    
    # CRITICAL: Socket release delay for macOS
    await asyncio.sleep(0.5)

# Create app with standard configuration (API Consistency Standards)
app = FastAPI(
    **get_openapi_configuration(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION
    ),
    lifespan=lifespan  # REQUIRED - Direct async context manager pattern
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create standard routers (API Consistency Standards)
routers = create_standard_routers(COMPONENT_NAME)

# Root endpoint - use standard router
@routers.root.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": COMPONENT_NAME,
        "version": COMPONENT_VERSION,
        "description": COMPONENT_DESCRIPTION,
        "status": "running",
        "docs": "/api/v1/docs"  # Updated docs URL
    }

# Health check endpoint - use standard router
@routers.root.get("/health", 
    responses={
        200: {"description": "Component is healthy"},
        503: {"description": "Component is unhealthy"},
        207: {"description": "Component is degraded (partial functionality)"}
    })
async def health_check():
    """Health check endpoint using shared utility.
    
    Returns appropriate HTTP status codes:
    - 200: healthy
    - 207: degraded (partial functionality)  
    - 503: unhealthy
    """
    from shared.utils.health_check import create_health_response
    from fastapi.responses import JSONResponse
    
    port = getattr(app.state, 'port', 8015)
    uptime = None
    if hasattr(app.state, "start_time"):
        uptime = (datetime.utcnow() - app.state.start_time).total_seconds()
    
    # Determine health status
    status = "healthy"
    http_status = 200
    
    # Check critical dependencies
    if not hermes_registration or not hermes_registration.is_registered:
        status = "degraded"
        http_status = 207
    
    # Check for critical failures
    # if critical_failure_condition:
    #     status = "unhealthy"
    #     http_status = 503
    
    # Use standardized health response (no JSONResponse wrapper needed)
    return create_health_response(
        component_name=COMPONENT_NAME.lower(),
        port=port,
        version=COMPONENT_VERSION,
        status=status,
        registered=is_registered_with_hermes,
        details={
            "uptime": uptime,
            "dependencies": {
                "hermes": "healthy" if is_registered_with_hermes else "not_registered"
            }
        }
    )

# Add ready endpoint (API Consistency Standards)
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=start_time or 0,
        readiness_check=lambda: hermes_registration is not None  # Custom check
    ),
    methods=["GET"]
)

# Add discovery endpoint (API Consistency Standards)
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION,
        endpoints=[
            EndpointInfo(
                path="/api/v1/example",
                method="GET",
                description="Example endpoint description"
            ),
            # Add your component's endpoints here
        ],
        capabilities=["capability1", "capability2"],  # Your capabilities
        dependencies={
            "hermes": "http://localhost:8001",
            # Add other dependencies
        },
        metadata={
            "documentation": "/api/v1/docs"
        }
    ),
    methods=["GET"]
)

# Business logic endpoints - use v1 router
@routers.v1.get("/example")
async def example_endpoint():
    """Example business logic endpoint under /api/v1/"""
    return {"message": "This endpoint is now at /api/v1/example"}

# Mount standard routers (REQUIRED)
mount_standard_routers(app, routers)

# Import and include MCP router (remains at /api/mcp/v2)
try:
    from mycomponent.api.endpoints.mcp import router as mcp_router
    app.include_router(mcp_router, prefix="/api/mcp/v2", tags=["mcp"])
except ImportError:
    logger.warning("MCP endpoints not available")

# Add shutdown endpoint using shared utility
add_shutdown_endpoint_to_app(app, COMPONENT_NAME.lower())

# Main module requirement
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment - NEVER hardcode
    port = int(os.environ.get("MYCOMPONENT_PORT", 8015))
    
    # Simple direct uvicorn run
    uvicorn.run(app, host="0.0.0.0", port=port)
    
    # OR with argparse for development flexibility:
    # import argparse
    # parser = argparse.ArgumentParser(description=f"{COMPONENT_NAME} API Server")
    # parser.add_argument("--port", type=int, default=port, help="Port to run the server on")
    # parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    # parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    # args = parser.parse_args()
    # 
    # logger.info(f"Starting {COMPONENT_NAME} server on {args.host}:{args.port}")
    # uvicorn.run(
    #     "mycomponent.api.app:app" if args.reload else app,
    #     host=args.host,
    #     port=args.port,
    #     reload=args.reload
    # )
```

### 3. Create MCP Endpoints

```python
# mycomponent/api/endpoints/mcp.py
"""
MCP v2 Endpoints for MyComponent
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException
from tekton.models.base import TektonBaseModel
from pydantic import Field

logger = logging.getLogger(__name__)

router = APIRouter()

# MCP v2 Models
class Tool(TektonBaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

class ToolList(TektonBaseModel):
    """Response for tool listing"""
    tools: List[Tool]

class ToolCall(TektonBaseModel):
    """Request to call a tool"""
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class ToolResponse(TektonBaseModel):
    """Response from tool execution"""
    content: List[Dict[str, Any]]
    isError: bool = False

# Define available tools
AVAILABLE_TOOLS = [
    Tool(
        name="example_tool",
        description="An example tool that demonstrates MCP integration",
        inputSchema={
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "Input parameter"}
            },
            "required": ["input"]
        }
    )
]

@router.post("/v2/tools/list", response_model=ToolList)
async def list_tools() -> ToolList:
    """List available MCP tools."""
    return ToolList(tools=AVAILABLE_TOOLS)

@router.post("/v2/tools/call", response_model=ToolResponse)
async def call_tool(request: ToolCall) -> ToolResponse:
    """Execute an MCP tool."""
    try:
        if request.name == "example_tool":
            # Implement your tool logic here
            result = f"Processed: {request.arguments.get('input', '')}"
            return ToolResponse(
                content=[{"type": "text", "text": result}]
            )
        else:
            raise HTTPException(status_code=404, detail=f"Tool {request.name} not found")
            
    except Exception as e:
        logger.error(f"Error executing tool {request.name}: {e}")
        return ToolResponse(
            content=[{"type": "text", "text": str(e)}],
            isError=True
        )
```

## CLI Implementation

### 1. Create CLI Main

```python
# mycomponent/cli/main.py
#!/usr/bin/env python3
"""
MyComponent CLI

Command-line interface for interacting with MyComponent.
"""

import asyncio
import logging
from typing import Optional

import click
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
logger = logging.getLogger(__name__)

# Default API URL
DEFAULT_API_URL = f"http://localhost:{os.environ.get('MYCOMPONENT_PORT', 8015)}"

class MyComponentClient:
    """Client for interacting with MyComponent API."""
    
    def __init__(self, base_url: str = DEFAULT_API_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def get_health(self) -> Dict[str, Any]:
        """Get health status."""
        response = await self.client.get(f"{self.base_url}/health")
        return response.json()
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()

@click.group()
@click.option('--api-url', default=DEFAULT_API_URL, help='MyComponent API URL')
@click.pass_context
def cli(ctx, api_url):
    """MyComponent CLI - Command line interface for MyComponent."""
    ctx.ensure_object(dict)
    ctx.obj['client'] = MyComponentClient(api_url)

@cli.command()
@click.pass_context
async def status(ctx):
    """Check MyComponent status."""
    client = ctx.obj['client']
    try:
        health = await client.get_health()
        
        # Create status table
        table = Table(title="MyComponent Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Status", health['status'])
        table.add_row("Version", health['version'])
        table.add_row("Port", str(health['port']))
        table.add_row("Uptime", f"{health.get('uptime', 0):.2f}s")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        await client.close()

@cli.command()
@click.argument('input_text')
@click.pass_context
async def process(ctx, input_text):
    """Process input through MyComponent."""
    client = ctx.obj['client']
    try:
        # Example command implementation
        console.print(Panel(f"Processing: {input_text}", title="MyComponent"))
        # Add actual processing logic here
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        await client.close()

def main():
    """Main entry point for CLI."""
    cli()

if __name__ == "__main__":
    main()
```

## MCP (Model Context Protocol) Implementation

### 1. Add MCP Dependencies

Update your `requirements.txt`:

```text
# Existing requirements...
# Add MCP support (included in tekton-shared)
tekton-shared>=0.1.0
```

### 2. Create MCP Service

```python
# mycomponent/mcp/__init__.py
from .service import MyComponentMCP

__all__ = ["MyComponentMCP"]
```

```python
# mycomponent/mcp/service.py
"""
MCP implementation for MyComponent.
"""
from shared.mcp import MCPService, MCPConfig
from shared.mcp.tools import HealthCheckTool, ComponentInfoTool
from typing import Dict, Any

class MyComponentMCP(MCPService):
    """MCP service implementation for MyComponent."""
    
    def __init__(self, core_service, **kwargs):
        """Initialize with reference to core service."""
        self.core_service = core_service
        super().__init__(**kwargs)
    
    async def register_default_tools(self):
        """Register component-specific tools."""
        # Register standard health check
        health_tool = HealthCheckTool(
            self.component_name,
            health_check_func=self.check_component_health
        )
        await self.register_tool(
            name=health_tool.name,
            description=health_tool.description,
            input_schema=health_tool.get_input_schema(),
            handler=health_tool
        )
        
        # Register component info
        info_tool = ComponentInfoTool(
            self.component_name,
            self.component_version,
            "Description of MyComponent functionality",
            capabilities=["capability1", "capability2", "capability3"]
        )
        await self.register_tool(
            name=info_tool.name,
            description=info_tool.description,
            input_schema=info_tool.get_input_schema(),
            handler=info_tool
        )
        
        # Register custom component tools
        await self.register_tool(
            name="process_data",
            description="Process data using MyComponent logic",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Data to process"
                    },
                    "options": {
                        "type": "object",
                        "description": "Processing options"
                    }
                },
                "required": ["data"]
            },
            handler=self.handle_process_data
        )
    
    async def check_component_health(self) -> Dict[str, Any]:
        """Custom health check implementation."""
        # Check core service health
        service_status = await self.core_service.health_check()
        
        return {
            "service": service_status,
            "mcp_tools": len(self.tools),
            "active_contexts": len(self.contexts)
        }
    
    async def handle_process_data(self, parameters: Dict[str, Any], context=None):
        """Handle data processing tool."""
        data = parameters.get("data", [])
        options = parameters.get("options", {})
        
        try:
            # Use core service to process
            result = await self.core_service.process_batch(data, options)
            
            return {
                "success": True,
                "processed_count": len(result),
                "results": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

### 3. Integrate MCP with FastAPI

Update your `app.py` to include MCP initialization:

```python
# mycomponent/api/app.py
from mycomponent.mcp import MyComponentMCP
from shared.mcp import MCPConfig

# Global MCP service
mcp_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with MCP support."""
    global mcp_service
    
    # ... existing initialization ...
    
    # Initialize MCP service
    mcp_config = MCPConfig.from_env("mycomponent")
    mcp_service = MyComponentMCP(
        core_service=app.state.core_service,
        component_name="mycomponent",
        component_version=COMPONENT_VERSION,
        hermes_url=mcp_config.hermes_url
    )
    
    # Initialize and register with Hermes
    await mcp_service.initialize()
    
    # Store in app state
    app.state.mcp_service = mcp_service
    
    yield
    
    # Cleanup
    if mcp_service:
        await mcp_service.shutdown()
```

### 4. Optional: Expose Local MCP Endpoints

If you want to test MCP tools locally:

```python
# Add to your router configuration
@routers.v1.get("/mcp/tools")
async def list_mcp_tools(request: Request):
    """List available MCP tools."""
    mcp_service = request.app.state.mcp_service
    if not mcp_service:
        raise HTTPException(status_code=503, detail="MCP service not initialized")
    
    return mcp_service.list_tools()

@routers.v1.post("/mcp/tools/{tool_name}/execute")
async def execute_mcp_tool(
    tool_name: str,
    parameters: dict,
    request: Request
):
    """Execute an MCP tool locally."""
    mcp_service = request.app.state.mcp_service
    if not mcp_service:
        raise HTTPException(status_code=503, detail="MCP service not initialized")
    
    tool_id = f"mycomponent.{tool_name}"
    result = await mcp_service.execute_tool(tool_id, parameters)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result
```

### 5. Create Custom Tools

For complex tools, create separate tool classes:

```python
# mycomponent/mcp/tools.py
from shared.mcp.base import MCPTool
from typing import List, Optional

class AnalysisToolMCP(MCPTool):
    """Advanced analysis tool for MyComponent."""
    
    name = "analyze_patterns"
    description = "Analyze patterns in provided data"
    tags = ["analysis", "patterns", "advanced"]
    
    def __init__(self, analyzer_service):
        self.analyzer = analyzer_service
        super().__init__()
    
    async def execute(
        self,
        dataset: List[dict],
        pattern_type: str = "statistical",
        confidence_threshold: float = 0.8
    ) -> dict:
        """
        Execute pattern analysis.
        
        Args:
            dataset: List of data points to analyze
            pattern_type: Type of pattern analysis
            confidence_threshold: Minimum confidence for patterns
            
        Returns:
            Analysis results with discovered patterns
        """
        # Validate inputs
        if not dataset:
            return {"error": "No data provided for analysis"}
        
        # Run analysis
        patterns = await self.analyzer.find_patterns(
            data=dataset,
            method=pattern_type,
            min_confidence=confidence_threshold
        )
        
        return {
            "success": True,
            "pattern_count": len(patterns),
            "patterns": patterns,
            "metadata": {
                "analyzed_items": len(dataset),
                "pattern_type": pattern_type,
                "threshold": confidence_threshold
            }
        }
```

### 6. Testing MCP Implementation

```python
# tests/test_mcp.py
import pytest
from mycomponent.mcp import MyComponentMCP
from mycomponent.core import MyService

@pytest.mark.asyncio
async def test_mcp_initialization():
    """Test MCP service initialization."""
    # Create mock core service
    core_service = MyService()
    
    # Initialize MCP
    mcp = MyComponentMCP(
        core_service=core_service,
        component_name="test",
        component_version="1.0.0"
    )
    
    await mcp.initialize()
    
    # Verify tools are registered
    tools = mcp.list_tools()
    assert len(tools) >= 3  # health, info, and custom tools
    
    # Find specific tool
    process_tool = next(
        (t for t in tools if t["name"] == "process_data"),
        None
    )
    assert process_tool is not None
    assert "data" in process_tool["input_schema"]["properties"]

@pytest.mark.asyncio
async def test_tool_execution():
    """Test executing an MCP tool."""
    core_service = MyService()
    mcp = MyComponentMCP(
        core_service=core_service,
        component_name="test",
        component_version="1.0.0"
    )
    
    await mcp.initialize()
    
    # Execute tool
    result = await mcp.execute_tool(
        "test.process_data",
        {
            "data": [{"id": 1, "value": "test"}],
            "options": {"mode": "fast"}
        }
    )
    
    assert result["success"] is True
    assert "results" in result
```

### 7. MCP Configuration

Configure MCP behavior through environment variables:

```bash
# .env.mycomponent
# MCP Configuration
MCP_AUTO_REGISTER=true
MCP_ENABLE_DEFAULT_TOOLS=true
MCP_TOOL_TIMEOUT=60
MCP_MAX_CONCURRENT_TOOLS=10

# Hermes connection (auto-detected from Tekton config)
# HERMES_URL=http://localhost:8001
```

## Core Business Logic

### 1. Create Core Module

```python
# mycomponent/core/my_service.py
"""
Core business logic for MyComponent
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class MyService:
    """Main service class for MyComponent functionality."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize the service."""
        logger.info("Initializing MyService")
        # Add initialization logic here
        self.initialized = True
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data."""
        if not self.initialized:
            raise RuntimeError("Service not initialized")
            
        # Implement your core business logic here
        result = {
            "processed_at": datetime.utcnow().isoformat(),
            "input": input_data,
            "output": "Processed successfully"
        }
        
        return result
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up MyService")
        # Add cleanup logic here
        self.initialized = False
```

## Launch Scripts

### 1. Create setup.sh

```bash
#!/bin/bash
# Setup script for MyComponent

set -e  # Exit on error

# Ensure the script is run from the MyComponent directory
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -U pip
pip install -r requirements.txt

# Install package in development mode
echo "Installing MyComponent in development mode..."
pip install -e .

# Make run script executable
chmod +x run_mycomponent.sh

echo "MyComponent setup complete!"
echo "Run './run_mycomponent.sh' to start the MyComponent server."
```

### 2. Create run_mycomponent.sh

```bash
#!/bin/bash
# Launch script for MyComponent - follows Tekton standards

# ANSI color codes for visibility
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Component name and port configuration
COMPONENT_NAME="MyComponent"
COMPONENT_MODULE="mycomponent"
PORT_VAR="MYCOMPONENT_PORT"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set up Python path to include component and Tekton root
export PYTHONPATH="$SCRIPT_DIR:$(dirname "$SCRIPT_DIR"):$PYTHONPATH"

# Get port from environment (NO hardcoded ports!)
PORT="${!PORT_VAR}"
if [ -z "$PORT" ]; then
    echo -e "${RED}Error: $PORT_VAR not set${NC}"
    echo "Please set the port in your environment or .env file"
    exit 1
fi

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}Error: Port $PORT is already in use${NC}"
    echo "Another service is using this port. Check with: lsof -i :$PORT"
    exit 1
fi

# Create log directory if it doesn't exist
LOG_DIR="$HOME/.tekton/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$COMPONENT_MODULE.log"

# Activate virtual environment if present
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Start the component
echo -e "${GREEN}Starting $COMPONENT_NAME on port $PORT...${NC}"
echo "Logging to: $LOG_FILE"

# Run the component with proper module path
python -m $COMPONENT_MODULE.api.app "$@" 2>&1 | tee -a "$LOG_FILE" &
PID=$!

# Health check loop (30 second timeout)
echo -e "${YELLOW}Waiting for $COMPONENT_NAME to start...${NC}"
for i in {1..30}; do
    if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $COMPONENT_NAME is running!${NC}"
        echo -e "${GREEN}API Documentation: http://localhost:$PORT/docs${NC}"
        echo -e "${GREEN}Health Check: http://localhost:$PORT/health${NC}"
        echo -e "${GREEN}Process ID: $PID${NC}"
        exit 0
    fi
    sleep 1
    echo -n "."
done

echo -e "\n${RED}✗ $COMPONENT_NAME failed to start within 30 seconds${NC}"
echo "Check the logs at: $LOG_FILE"
exit 1
```

## Status Endpoint Requirements

All components MUST provide status information for `tekton-status`:

### Standard Status Response

```python
@app.get("/status")
async def get_status():
    """Status endpoint for tekton-status integration."""
    return {
        "component": COMPONENT_NAME,
        "status": "running",
        "version": "0.1.0",
        "port": getattr(app.state, 'port', int(os.environ.get("MYCOMPONENT_PORT"))),
        "registered": hermes_registration.is_registered if hermes_registration else False,
        "uptime": (datetime.utcnow() - app.state.start_time).total_seconds() if hasattr(app.state, "start_time") else 0,
        "capabilities": ["capability1", "capability2"],  # List your MCP tools/capabilities
        "health": {
            "api": "healthy",
            "dependencies": {
                "hermes": "healthy" if hermes_registration and hermes_registration.is_registered else "disconnected"
            }
        }
    }
```

## Shutdown Endpoint Requirements

All components MUST implement the shutdown endpoint using the shared utility:

### Adding the Shutdown Endpoint

```python
# This is done in app.py after creating the FastAPI app
from shared.utils.shutdown_endpoint import add_shutdown_endpoint_to_app

# Create app with lifespan
app = FastAPI(
    title="MyComponent API",
    description="API for MyComponent",
    version="0.1.0",
    lifespan=lifespan  # REQUIRED
)

# Add CORS middleware
app.add_middleware(CORSMiddleware, ...)

# Add routes
app.include_router(mcp.router, prefix="/mcp", tags=["mcp"])

# REQUIRED: Add shutdown endpoint
add_shutdown_endpoint_to_app(app, "mycomponent")
```

### Shutdown Endpoint Behavior

The shutdown endpoint (POST `/shutdown`) will:
1. Initiate graceful shutdown of the component
2. Trigger the shutdown sequence in the lifespan context
3. Ensure proper cleanup of resources
4. Return a response confirming shutdown initiation

### Usage by tekton-kill

The `tekton-kill` script uses this endpoint to gracefully shutdown components:

```bash
# How tekton-kill stops a component
curl -X POST http://localhost:$PORT/shutdown

# Component will:
# 1. Stop accepting new requests
# 2. Complete in-flight requests
# 3. Cancel heartbeat task
# 4. Deregister from Hermes
# 5. Clean up resources
# 6. Exit gracefully
```

## Common Patterns

### Error Handling

```python
from fastapi import HTTPException
from tekton.models.base import TektonBaseModel

class ErrorResponse(TektonBaseModel):
    error: str
    component: str = "mycomponent"
    timestamp: str
    details: Optional[Dict[str, Any]] = None

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )
```

### Dependency Injection

```python
# mycomponent/api/dependencies.py
from typing import Optional
from fastapi import Depends, HTTPException

async def get_my_service() -> MyService:
    """Dependency to get MyService instance."""
    if not hasattr(app.state, "my_service"):
        raise HTTPException(status_code=503, detail="Service not initialized")
    return app.state.my_service

# Usage in endpoints
@router.post("/process")
async def process_data(
    data: Dict[str, Any],
    service: MyService = Depends(get_my_service)
):
    result = await service.process(data)
    return result
```

## Best Practices

1. **Always use async/await** for I/O operations
2. **Log appropriately** - INFO for normal operations, ERROR for failures
3. **Handle errors gracefully** - Return proper HTTP status codes
4. **Use dependency injection** - Don't access app.state directly in endpoints
5. **Document everything** - Use docstrings and type hints
6. **Follow naming conventions** - Lowercase with underscores for modules
7. **Keep it simple** - No complex abstractions

## Future Enhancements

These features are planned but not yet standardized:

1. **Rate Limiting** - No standard implementation yet
   ```python
   # Future pattern (not implemented):
   # from shared.utils.rate_limit import rate_limit
   # @rate_limit(calls=100, period=60)  # 100 calls per minute
   ```

2. **Request Validation** - Currently handled by Pydantic models
3. **Authentication** - No standard auth pattern yet
4. **Metrics Collection** - Basic health/status only for now

## ⚠️ Common Mistakes to Avoid

> **WARNING: These are the most common errors when building components**
> - **DON'T** forget to create `__main__.py` in package root - REQUIRED for launcher
> - **DON'T** put `if __name__ == "__main__":` in app.py - only in `__main__.py`
> - **DON'T** use `@app.on_event("startup")` or `@app.on_event("shutdown")` - they're deprecated
> - **DON'T** import from `tekton.utils.port_config` - it doesn't exist
> - **DON'T** hardcode port values anywhere (port=8000, etc.)
> - **DON'T** forget the `await asyncio.sleep(0.5)` in shutdown for macOS
> - **DON'T** use `setup_component_logger` - it's `setup_component_logging`
> - **DON'T** skip the shutdown endpoint - it's required for tekton-kill
> - **DON'T** use `logging.getLogger()` - use `setup_component_logging()`
> - **DON'T** create custom logging/startup/shutdown utilities - use shared ones
> - **DON'T** use plain uvicorn.run() - always use socket_server utilities for proper port reuse
> - **DON'T** forget to declare heartbeat_task as global in lifespan
> - **DON'T** create subprocess/multiprocessing without proper cleanup
> - **DON'T** forget to import socket_server utilities in __main__.py and app.py

## Troubleshooting Common Issues

### Import Error: 'setup_component_logger'
- **Issue**: `ImportError: cannot import name 'setup_component_logger'`
- **Fix**: Use `setup_component_logging` (with 'ing' at the end)

### Component Not Registering with Hermes
- **Check**: Is the port hardcoded in the registration call?
- **Fix**: Use `port=port` variable from config, not `port=8000`

### Socket Already in Use on macOS
- **Issue**: Port binding fails on restart
- **Fix**: Ensure `await asyncio.sleep(0.5)` is at the end of shutdown

### FastAPI Startup Errors
- **Issue**: `TypeError: 'async_generator' object is not callable`
- **Fix**: Ensure you're using the lifespan pattern correctly with `@asynccontextmanager`

## Migrating from Old Patterns

### Before (Deprecated):
```python
@app.on_event("startup")
async def startup_event():
    logger.info("Starting component")
    # startup code
    app.state.hermes = HermesRegistration()
    await app.state.hermes.register_component(...)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down")
    # shutdown code
    await app.state.hermes.deregister(...)

app = FastAPI()
```

### After (Modern):
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting component")
    async def startup_logic():
        # startup code
        global hermes_registration
        hermes_registration = HermesRegistration()
        await hermes_registration.register_component(...)
    
    metrics = await component_startup("mycomponent", startup_logic, timeout=30)
    logger.info(f"Started in {metrics.total_time:.2f}s")
    
    yield
    
    # Shutdown
    logger.info("Shutting down")
    shutdown = GracefulShutdown("mycomponent")
    await shutdown.shutdown_sequence(timeout=10)
    await asyncio.sleep(0.5)  # CRITICAL!

app = FastAPI(lifespan=lifespan)
```

## Summary: Tekton Component Integration Standards

Based on the completed Shared Utilities Sprint, here are the mandatory requirements for all new components:

### 1. **Required Imports**
```python
# Shared utilities (from Shared Utilities Sprint)
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.env_config import get_component_config
from shared.utils.errors import StartupError
from shared.utils.startup import component_startup, StartupMetrics
from shared.utils.shutdown import GracefulShutdown
from shared.utils.health_check import create_health_response
from shared.utils.shutdown_endpoint import add_shutdown_endpoint_to_app

# Shared API utilities (from API Consistency Sprint)
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)
```

### 2. **Launch Script Requirements**
- ANSI color codes for visibility
- Port checking with `lsof`
- Logging to `~/.tekton/logs/`
- Health check loop with timeout
- Display service endpoints when started

### 3. **API Requirements**
- Use lifespan pattern (no `@app.on_event`)
- Use `get_openapi_configuration()` for FastAPI app creation
- Create standard routers with `create_standard_routers()`
- Mount routers with `mount_standard_routers()`
- Implement `/health` endpoint with `create_health_response`
- Implement `/ready` endpoint with `create_ready_endpoint()`
- Implement `/api/v1/discovery` endpoint with `create_discovery_endpoint()`
- Move all business logic endpoints under `/api/v1/` prefix
- MCP endpoints remain at `/api/mcp/v2` (do not change)
- Implement `/status` endpoint for tekton-status
- Add shutdown endpoint with `add_shutdown_endpoint_to_app(app, component_name)`
- Include socket release delay (0.5s) after shutdown
- All components must use version "0.1.0"

### 4. **Configuration Requirements**
- Never hardcode ports
- Use `get_component_config()` for all settings
- Support three-tier environment system
- Set up logging with `setup_component_logging()`

### 5. **Service Registration**
- Register with Hermes on startup
- Send heartbeats every 30 seconds
- Deregister on shutdown
- Handle registration failures gracefully

### 6. **Testing Your Component**
```bash
# Component should:
./run_mycomponent.sh         # Start successfully
./tekton-status              # Show as healthy
curl http://localhost:PORT/health  # Return health status
curl -X POST http://localhost:PORT/shutdown  # Shutdown gracefully
```

## API Consistency Standards (As of API Consistency Sprint)

All Tekton components must follow these API standards for consistency:

### Endpoint Structure
```
/                    # Root endpoint
/health              # Health check (infrastructure)
/ready               # Readiness check (infrastructure)
/status              # Status for tekton-status (infrastructure)
/shutdown            # Graceful shutdown (infrastructure)
/api/v1/             # All business logic endpoints
/api/v1/discovery    # Service discovery endpoint
/api/v1/docs         # OpenAPI documentation
/api/mcp/v2/         # MCP endpoints (unchanged)
```

### Standard Router Usage
```python
# Create routers
routers = create_standard_routers(COMPONENT_NAME)

# Use routers for endpoints
@routers.root.get("/")           # Infrastructure endpoints
@routers.v1.get("/endpoint")     # Business logic endpoints

# Mount routers
mount_standard_routers(app, routers)
```

### Required Endpoints
Every component MUST implement:
1. `/health` - Component health status
2. `/ready` - Component readiness status
3. `/api/v1/discovery` - Service discovery information
4. `/status` - Status information for tekton-status
5. `/shutdown` - Graceful shutdown endpoint

### Example Discovery Endpoint
```python
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION,
        endpoints=[
            EndpointInfo(path="/api/v1/example", method="GET", description="Example endpoint"),
        ],
        capabilities=["capability1", "capability2"],
        dependencies={"hermes": "http://localhost:8001"},
        metadata={"documentation": "/api/v1/docs"}
    ),
    methods=["GET"]
)
```

---

*Next: [UI Implementation Guide](./UI_Implementation_Guide.md)*