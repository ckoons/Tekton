# YetAnotherMCP_Sprint - Implementation Plan

## Overview

This document outlines the detailed implementation plan for the YetAnotherMCP_Sprint, which focuses on standardizing the Model Context Protocol (MCP) implementation across all Tekton components. It provides specific technical details, code changes, and implementation steps for each phase of the sprint.

## Phase 1: Fix Core Issues

### 1.1 Fix Hermes MCP Service Initialization Bug

#### Issue Description
The Hermes MCP service initialization is failing with the error: "object bool can't be used in 'await' expression". This suggests that a function that should return an awaitable is returning a boolean instead.

#### Implementation Steps

1. **Identify the problematic code in `Hermes/hermes/core/mcp_service.py`**:
   ```python
   # Line ~109-120 in mcp_service.py initialize() method
   try:
       logger.info("Initializing MCP service channels")
            
       # Check if message bus is available
       if not self.message_bus:
           logger.error("Message bus not available for MCP service initialization")
           return
                
       # Create tools channel
       await self.message_bus.create_channel(
           'mcp.tools',
           description='Channel for MCP tools'
       )
   ```

2. **Implement the fix**:
   ```python
   # Updated code
   try:
       logger.info("Initializing MCP service channels")
            
       # Check if message bus is available
       if not self.message_bus:
           logger.error("Message bus not available for MCP service initialization")
           return False  # Return boolean without await
                
       # Create tools channel - ensure this returns an awaitable
       result1 = await self.message_bus.create_channel(
           'mcp.tools',
           description='Channel for MCP tools'
       )
   ```

3. **Verify message_bus methods return proper awaitables**:
   - Check the implementation of `message_bus.create_channel()`
   - Ensure it returns a proper coroutine or Future object
   - If it's synchronous, remove the await and handle accordingly

4. **Add comprehensive error handling**:
   - Add detailed error logging for each step
   - Wrap individual channel creation in try/except blocks
   - Add debug logging for initialization steps

5. **Add unit tests**:
   - Create a test for MCP service initialization
   - Mock the message_bus to test various scenarios
   - Verify initialization completes successfully

### 1.2 Update Hermes MCP Router to Use `/api/mcp/v2`

#### Implementation Steps

1. **Update the MCP router in `Hermes/hermes/api/mcp_endpoints.py`**:
   ```python
   # Change router prefix from
   mcp_router = APIRouter(
       prefix="/mcp",  # Old prefix
       tags=["mcp"],
       responses={404: {"description": "Not found"}}
   )
   
   # To
   mcp_router = APIRouter(
       prefix="/api/mcp/v2",  # New standardized prefix
       tags=["mcp"],
       responses={404: {"description": "Not found"}}
   )
   ```

2. **Update the health endpoint**:
   ```python
   @mcp_router.get("/health")
   async def health_check(...):
       # This will now be available at /api/mcp/v2/health
   ```

3. **Update any internal references to MCP endpoints**:
   - Search for any hardcoded references to "/mcp"
   - Update them to use the new "/api/mcp/v2" path
   - Ensure route handling is consistent

4. **Add compatibility layer if needed**:
   ```python
   # Optional: Add legacy route for backward compatibility
   legacy_router = APIRouter(prefix="/mcp", tags=["legacy"])
   app.include_router(legacy_router)
   
   @legacy_router.get("/health")
   async def legacy_health_check(request: Request):
       # Redirect to new endpoint
       return RedirectResponse(url=f"/api/mcp/v2/health")
   ```

### 1.3 Create a Test Script for MCP Connectivity

#### Implementation Steps

1. **Create a test script in `Hermes/tests/test_mcp_connectivity.py`**:
   ```python
   #!/usr/bin/env python3
   """
   Test script for Hermes MCP connectivity.
   
   This script tests the MCP endpoints and verifies that the service is working correctly.
   """
   
   import asyncio
   import sys
   import logging
   import json
   import aiohttp
   
   # Configure logging
   logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
   logger = logging.getLogger("mcp_test")
   
   # Hermes URL
   HERMES_URL = "http://localhost:8001"
   
   async def test_health_endpoint():
       """Test the MCP health endpoint."""
       async with aiohttp.ClientSession() as session:
           # Test new endpoint
           url = f"{HERMES_URL}/api/mcp/v2/health"
           try:
               async with session.get(url) as resp:
                   if resp.status == 200:
                       data = await resp.json()
                       logger.info(f"✅ MCP health endpoint is working: {json.dumps(data, indent=2)}")
                       return True
                   else:
                       logger.error(f"❌ MCP health endpoint returned status {resp.status}")
                       return False
           except Exception as e:
               logger.error(f"❌ Error connecting to MCP health endpoint: {e}")
               return False
   
   async def test_capabilities_endpoint():
       """Test the MCP capabilities endpoint."""
       async with aiohttp.ClientSession() as session:
           url = f"{HERMES_URL}/api/mcp/v2/capabilities"
           try:
               async with session.get(url) as resp:
                   if resp.status == 200:
                       data = await resp.json()
                       logger.info(f"✅ MCP capabilities endpoint is working")
                       logger.info(f"Found capabilities: {json.dumps(data, indent=2)}")
                       return True
                   else:
                       logger.error(f"❌ MCP capabilities endpoint returned status {resp.status}")
                       return False
           except Exception as e:
               logger.error(f"❌ Error connecting to MCP capabilities endpoint: {e}")
               return False
   
   async def main():
       """Run all tests."""
       logger.info("Testing Hermes MCP connectivity...")
       
       # Test health endpoint
       health_ok = await test_health_endpoint()
       
       # Test capabilities endpoint
       capabilities_ok = await test_capabilities_endpoint()
       
       # Overall status
       if health_ok and capabilities_ok:
           logger.info("✅ All MCP tests passed")
           return 0
       else:
           logger.error("❌ Some MCP tests failed")
           return 1
   
   if __name__ == "__main__":
       exit_code = asyncio.run(main())
       sys.exit(exit_code)
   ```

2. **Create a shell script for easy testing**:
   ```bash
   #!/bin/bash
   # test_mcp.sh - Test MCP connectivity
   
   echo "Testing Hermes MCP connectivity..."
   python3 tests/test_mcp_connectivity.py
   
   exit $?
   ```

3. **Make the script executable**:
   ```bash
   chmod +x tests/test_mcp_connectivity.py
   chmod +x test_mcp.sh
   ```

## Phase 2: Standardize Implementation

### 2.1 Create Shared MCP Library

#### Implementation Steps

1. **Create the directory structure**:
   ```
   tekton/mcp/
   ├── __init__.py
   ├── client.py          # Unified MCP client
   ├── server.py          # Standard MCP server implementation
   ├── decorators.py      # @mcp_tool, @mcp_capability, etc.
   ├── registration.py    # MCP registration utilities
   ├── adapters/          # Adapters for different backends
   │   ├── __init__.py
   │   └── hermes.py      # Hermes-specific adapter
   └── schemas/           # Shared schemas
       ├── __init__.py
       └── v2.py          # v2 schemas
   ```

2. **Implement the base MCP client**:
   ```python
   # tekton/mcp/client.py
   """Unified MCP client for Tekton components."""
   
   import aiohttp
   import json
   import logging
   from typing import Dict, List, Any, Optional, Union
   
   class MCPClient:
       """Unified MCP client for Tekton components."""
       
       def __init__(self, url: str = "http://localhost:8001/api/mcp/v2"):
           """Initialize the MCP client."""
           self.url = url
           self.logger = logging.getLogger("tekton.mcp.client")
           
       async def get_capabilities(self) -> List[Dict[str, Any]]:
           """Get MCP capabilities."""
           async with aiohttp.ClientSession() as session:
               async with session.get(f"{self.url}/capabilities") as resp:
                   if resp.status == 200:
                       return await resp.json()
                   else:
                       self.logger.error(f"Failed to get capabilities: {resp.status}")
                       return []
                       
       async def get_tools(self) -> List[Dict[str, Any]]:
           """Get MCP tools."""
           async with aiohttp.ClientSession() as session:
               async with session.get(f"{self.url}/tools") as resp:
                   if resp.status == 200:
                       return await resp.json()
                   else:
                       self.logger.error(f"Failed to get tools: {resp.status}")
                       return []
                       
       async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
           """Execute a tool."""
           async with aiohttp.ClientSession() as session:
               async with session.post(
                   f"{self.url}/process",
                   json={"tool": tool_name, "parameters": params}
               ) as resp:
                   if resp.status == 200:
                       return await resp.json()
                   else:
                       self.logger.error(f"Failed to execute tool: {resp.status}")
                       return {"error": f"Tool execution failed: {resp.status}"}
   ```

3. **Implement the server base**:
   ```python
   # tekton/mcp/server.py
   """Standard MCP server implementation."""
   
   from fastapi import APIRouter, Request, Depends, HTTPException
   from typing import Dict, List, Any, Optional, Union, Callable
   
   from .schemas.v2 import MCPRequest, MCPResponse, MCPTool, MCPCapability
   
   def create_mcp_router(
       prefix: str = "/api/mcp/v2",
       tags: List[str] = ["mcp"]
   ) -> APIRouter:
       """Create a standard MCP router."""
       return APIRouter(
           prefix=prefix,
           tags=tags,
           responses={404: {"description": "Not found"}}
       )
       
   def add_standard_endpoints(
       router: APIRouter,
       get_capabilities_func: Callable,
       get_tools_func: Callable,
       process_request_func: Callable,
       component_manager_dependency: Callable
   ):
       """Add standard MCP endpoints to a router."""
       
       @router.get("/health")
       async def health_check(
           component_manager = Depends(component_manager_dependency)
       ):
           """Health check endpoint."""
           return {"status": "healthy"}
           
       @router.get("/capabilities")
       async def get_capabilities(
           component_manager = Depends(component_manager_dependency)
       ):
           """Get capabilities endpoint."""
           return await get_capabilities_func(component_manager)
           
       @router.get("/tools")
       async def get_tools(
           component_manager = Depends(component_manager_dependency)
       ):
           """Get tools endpoint."""
           return await get_tools_func(component_manager)
           
       @router.post("/process")
       async def process_request(
           request: MCPRequest,
           component_manager = Depends(component_manager_dependency)
       ):
           """Process request endpoint."""
           return await process_request_func(component_manager, request)
   ```

4. **Implement the decorators**:
   ```python
   # tekton/mcp/decorators.py
   """Decorators for MCP tools and capabilities."""
   
   import functools
   from typing import Dict, List, Any, Optional, Union, Callable
   
   # Tool registry
   _tools = {}
   _capabilities = {}
   
   def mcp_tool(
       name: str,
       description: str,
       schema: Dict[str, Any],
       tags: Optional[List[str]] = None
   ):
       """Decorator for MCP tools."""
       def decorator(func):
           # Register the tool
           _tools[name] = {
               "name": name,
               "description": description,
               "schema": schema,
               "tags": tags or [],
               "handler": func
           }
           
           @functools.wraps(func)
           def wrapper(*args, **kwargs):
               return func(*args, **kwargs)
               
           return wrapper
       return decorator
       
   def mcp_capability(
       name: str,
       description: str,
       modalities: List[str]
   ):
       """Decorator for MCP capabilities."""
       def decorator(func):
           # Register the capability
           _capabilities[name] = {
               "name": name,
               "description": description,
               "modalities": modalities,
               "handler": func
           }
           
           @functools.wraps(func)
           def wrapper(*args, **kwargs):
               return func(*args, **kwargs)
               
           return wrapper
       return decorator
       
   def get_all_tools() -> List[Dict[str, Any]]:
       """Get all registered tools."""
       return list(_tools.values())
       
   def get_all_capabilities() -> List[Dict[str, Any]]:
       """Get all registered capabilities."""
       return list(_capabilities.values())
   ```

5. **Implement the registration utility**:
   ```python
   # tekton/mcp/registration.py
   """MCP registration utilities."""
   
   from typing import Dict, List, Any, Optional, Union
   
   async def register_mcp_tools(
       hermes_registration,
       tools: List[Dict[str, Any]],
       endpoint: str
   ) -> bool:
       """Register MCP tools with Hermes."""
       # Add MCP tools to component metadata
       metadata = hermes_registration.registration_data.get("metadata", {})
       metadata["mcp"] = {
           "endpoint": endpoint,
           "tools": tools
       }
       
       # Update registration data
       hermes_registration.registration_data["metadata"] = metadata
       
       # Send updated registration to Hermes
       # TODO: Implement update registration method
       
       return True
   ```

### 2.2 Update `hermes_registration.py`

#### Implementation Steps

1. **Update `shared/utils/hermes_registration.py`**:
   ```python
   # Add MCP registration support
   
   async def register_component_with_mcp(
       self,
       component_name: str,
       port: int,
       version: str,
       capabilities: List[str],
       mcp_tools: Optional[List[Dict[str, Any]]] = None,
       mcp_endpoint: str = "/api/mcp/v2",
       health_endpoint: str = "/health"
   ) -> bool:
       """Register a component with Hermes including MCP capabilities"""
       # Add MCP capability if tools are provided
       if mcp_tools and "mcp" not in capabilities:
           capabilities.append("mcp")
       
       # Create metadata with MCP tools
       metadata = self.registration_data.get("metadata", {}) if self.registration_data else {}
       
       # Add MCP metadata if tools are provided
       if mcp_tools:
           metadata["mcp"] = {
               "endpoint": f"http://localhost:{port}{mcp_endpoint}",
               "tools": mcp_tools
           }
       
       # Register the component
       return await self.register_component(
           component_name=component_name,
           port=port,
           version=version,
           capabilities=capabilities,
           metadata=metadata,
           health_endpoint=health_endpoint
       )
   ```

2. **Add integration with the heartbeat system**:
   ```python
   # Update the heartbeat method to include MCP status
   
   async def heartbeat(self, component_name: str, status: str = "healthy", mcp_status: Optional[str] = None) -> bool:
       """Send heartbeat to Hermes"""
       if not self.is_registered:
           return False
           
       try:
           heartbeat_data = {
               "component_id": component_name,
               "status": {
                   "health": status
               }
           }
           
           # Add MCP status if provided
           if mcp_status:
               heartbeat_data["status"]["mcp"] = mcp_status
           
           async with aiohttp.ClientSession() as session:
               async with session.post(
                   f"{self.hermes_url}/api/heartbeat",
                   json=heartbeat_data,
                   timeout=2
               ) as resp:
                   return resp.status == 200
                   
       except Exception as e:
           logger.debug(f"Heartbeat failed: {e}")
           return False
   ```

### 2.3 Enhance Hermes Tool Registry

#### Implementation Steps

1. **Create a tool registry in Hermes**:
   ```python
   # Add to hermes/core/mcp_service.py
   
   class ToolRegistry:
       """Registry for MCP tools from all components."""
       
       def __init__(self):
           """Initialize the tool registry."""
           self.tools = {}  # tool_id -> tool_spec
           self.component_tools = {}  # component_id -> [tool_id]
           self.logger = logging.getLogger("hermes.core.tool_registry")
           
       async def register_tool(self, component_id: str, tool_spec: Dict[str, Any]) -> str:
           """Register a tool with the registry."""
           # Generate tool ID
           tool_id = f"{component_id}:{tool_spec['name']}"
           
           # Store tool spec
           self.tools[tool_id] = {
               **tool_spec,
               "id": tool_id,
               "component_id": component_id,
               "registered_at": time.time()
           }
           
           # Add to component tools
           if component_id not in self.component_tools:
               self.component_tools[component_id] = []
           self.component_tools[component_id].append(tool_id)
           
           self.logger.info(f"Registered tool {tool_id} from {component_id}")
           
           return tool_id
           
       async def unregister_component_tools(self, component_id: str) -> int:
           """Unregister all tools for a component."""
           if component_id not in self.component_tools:
               return 0
               
           tool_ids = self.component_tools[component_id]
           count = len(tool_ids)
           
           # Remove tools
           for tool_id in tool_ids:
               self.tools.pop(tool_id, None)
               
           # Remove component entry
           self.component_tools.pop(component_id, None)
           
           self.logger.info(f"Unregistered {count} tools for {component_id}")
           
           return count
           
       async def get_all_tools(self) -> List[Dict[str, Any]]:
           """Get all registered tools."""
           return list(self.tools.values())
           
       async def get_component_tools(self, component_id: str) -> List[Dict[str, Any]]:
           """Get all tools for a component."""
           if component_id not in self.component_tools:
               return []
               
           tool_ids = self.component_tools[component_id]
           return [self.tools[tool_id] for tool_id in tool_ids if tool_id in self.tools]
           
       async def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
           """Get a specific tool."""
           return self.tools.get(tool_id)
   ```

2. **Integrate the tool registry with the registration process**:
   ```python
   # Update hermes/core/registration.py
   
   async def register_component(self, registration_data: Dict[str, Any]) -> Dict[str, Any]:
       """Register a component with Hermes."""
       # Existing registration code...
       
       # Check for MCP tools
       mcp_data = registration_data.get("metadata", {}).get("mcp")
       if mcp_data and "tools" in mcp_data:
           # Get tool registry
           tool_registry = self.app.state.tool_registry
           
           # Register each tool
           component_id = registration_data["name"]
           tools = mcp_data["tools"]
           
           for tool_spec in tools:
               await tool_registry.register_tool(component_id, tool_spec)
               
           self.logger.info(f"Registered {len(tools)} MCP tools for {component_id}")
       
       # Continue with registration...
   ```

3. **Update the unregistration process**:
   ```python
   # Update hermes/core/registration.py
   
   async def unregister_component(self, component_id: str) -> bool:
       """Unregister a component from Hermes."""
       # Existing unregistration code...
       
       # Unregister MCP tools
       tool_registry = self.app.state.tool_registry
       await tool_registry.unregister_component_tools(component_id)
       
       # Continue with unregistration...
   ```

## Phase 3: Integration and Testing

### 3.1 Update Component MCP Implementations

#### Implementation Steps

1. **Create a migration guide for components**:
   ```markdown
   # MCP Migration Guide
   
   This guide explains how to update your component to use the standardized MCP implementation.
   
   ## Step 1: Update MCP Endpoints
   
   Change your MCP endpoints from `/mcp` to `/api/mcp/v2`:
   
   ```python
   # Old
   mcp_router = APIRouter(
       prefix="/mcp",
       tags=["mcp"]
   )
   
   # New
   mcp_router = APIRouter(
       prefix="/api/mcp/v2",
       tags=["mcp"]
   )
   ```
   
   ## Step 2: Use the Shared MCP Library
   
   ```python
   # Import the shared library
   from tekton.mcp.server import create_mcp_router, add_standard_endpoints
   from tekton.mcp.decorators import mcp_tool, mcp_capability
   
   # Create the router
   mcp_router = create_mcp_router()
   
   # Add standard endpoints
   add_standard_endpoints(
       router=mcp_router,
       get_capabilities_func=your_get_capabilities_func,
       get_tools_func=your_get_tools_func,
       process_request_func=your_process_request_func,
       component_manager_dependency=lambda: your_component_manager
   )
   ```
   
   ## Step 3: Update Registration
   
   ```python
   # Import the registration utility
   from shared.utils.hermes_registration import HermesRegistration
   
   # Register with MCP tools
   registration = HermesRegistration(hermes_url)
   await registration.register_component_with_mcp(
       component_name="your_component",
       port=your_port,
       version="1.0.0",
       capabilities=["your_capability", "mcp"],
       mcp_tools=your_tools
   )
   ```
   
   ## Step 4: Use the Standardized Heartbeat
   
   ```python
   # Start heartbeat loop
   asyncio.create_task(
       heartbeat_loop(
           registration=registration,
           component_name="your_component",
           interval=30
       )
   )
   ```
   ```

2. **Update at least one component as an example**:
   - Engram is a good candidate since it already has a comprehensive MCP implementation
   - Update Engram to use the shared library and standard registration

### 3.2 Update `install_tekton_mcps.sh`

#### Implementation Steps

1. **Update the `install_tekton_mcps.sh` script**:
   ```bash
   #!/bin/bash
   # Script to install Tekton MCPs for Claude
   # Installs Hermes as the central MCP that provides access to all Tekton components
   
   # Main function
   main() {
       echo "Installing Tekton MCP (via Hermes) for Claude..."
       
       # First, remove any existing Tekton MCP
       echo "Removing existing Tekton MCPs..."
       claude mcp remove tekton 2>/dev/null || true
       
       # Install Hermes as MCP using the standard endpoint
       echo "Installing Hermes as MCP at http://localhost:8001/api/mcp/v2..."
       claude mcp add tekton -s user http://localhost:8001/api/mcp/v2
       
       echo ""
       echo "Installation complete! Tekton MCP installed via Hermes."
       echo "All Tekton components registered with Hermes are now accessible to Claude."
   }
   
   # Run the main function
   main
   ```

2. **Test the script with Claude**:
   - Run the script
   - Verify that Claude can connect to the MCP endpoint
   - Verify that Claude can access tools from registered components

### 3.3 Documentation and Testing

#### Implementation Steps

1. **Create comprehensive documentation**:
   ```markdown
   # Tekton MCP Architecture
   
   This document describes the standardized Model Context Protocol (MCP) architecture used by Tekton components.
   
   ## Overview
   
   Tekton uses a standardized MCP implementation with Hermes as the central aggregator. This architecture provides:
   
   - A single endpoint for clients to connect to
   - Consistent tool discovery and execution
   - Standardized registration and heartbeat
   - Shared code for all components
   
   ## Endpoint Structure
   
   All MCP endpoints use the `/api/mcp/v2` path:
   
   - `/api/mcp/v2/health` - Health check endpoint
   - `/api/mcp/v2/capabilities` - Get capabilities endpoint
   - `/api/mcp/v2/tools` - Get tools endpoint
   - `/api/mcp/v2/process` - Process request endpoint
   
   ## Registration Process
   
   Components register with Hermes using the standard registration process, including their MCP tools:
   
   ```python
   await registration.register_component_with_mcp(
       component_name="your_component",
       port=your_port,
       version="1.0.0",
       capabilities=["your_capability", "mcp"],
       mcp_tools=your_tools
   )
   ```
   
   ## Client Integration
   
   Clients like Claude connect to the Hermes MCP endpoint:
   
   ```bash
   claude mcp add tekton -s user http://localhost:8001/api/mcp/v2
   ```
   
   ## Architecture Diagram
   
   ```
   +---------+
   | Claude  |
   +---------+
        |
        | (MCP Connection)
        v
   +---------+     +----------+     +---------+
   | Hermes  |---->| Component|---->| Service |
   +---------+     +----------+     +---------+
        |
        | (MCP Connection)
        v
   +---------+     +---------+
   | Engram  |---->| Memory  |
   +---------+     +---------+
   ```
   ```

2. **Create end-to-end tests**:
   ```python
   #!/usr/bin/env python3
   """
   End-to-end test for Tekton MCP integration with Claude.
   
   This script tests the full MCP integration from Claude to Hermes to components.
   """
   
   import asyncio
   import sys
   import logging
   import json
   import subprocess
   import aiohttp
   
   # Configure logging
   logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
   logger = logging.getLogger("e2e_test")
   
   # Hermes URL
   HERMES_URL = "http://localhost:8001"
   
   async def test_hermes_mcp_endpoint():
       """Test the Hermes MCP endpoint."""
       async with aiohttp.ClientSession() as session:
           url = f"{HERMES_URL}/api/mcp/v2/health"
           try:
               async with session.get(url) as resp:
                   if resp.status == 200:
                       data = await resp.json()
                       logger.info(f"✅ Hermes MCP endpoint is working: {json.dumps(data, indent=2)}")
                       return True
                   else:
                       logger.error(f"❌ Hermes MCP endpoint returned status {resp.status}")
                       return False
           except Exception as e:
               logger.error(f"❌ Error connecting to Hermes MCP endpoint: {e}")
               return False
   
   async def test_claude_mcp_integration():
       """Test Claude MCP integration."""
       # Run the installation script
       logger.info("Installing Tekton MCP for Claude...")
       result = subprocess.run(["./install_tekton_mcps.sh"], capture_output=True, text=True)
       
       if result.returncode != 0:
           logger.error(f"❌ Failed to install Tekton MCP for Claude: {result.stderr}")
           return False
           
       logger.info(f"✅ Installed Tekton MCP for Claude")
       
       # TODO: Add more tests for Claude interaction
       
       return True
   
   async def main():
       """Run all tests."""
       logger.info("Running end-to-end MCP integration tests...")
       
       # Test Hermes MCP endpoint
       hermes_ok = await test_hermes_mcp_endpoint()
       
       # Test Claude integration
       claude_ok = await test_claude_mcp_integration()
       
       # Overall status
       if hermes_ok and claude_ok:
           logger.info("✅ All end-to-end tests passed")
           return 0
       else:
           logger.error("❌ Some end-to-end tests failed")
           return 1
   
   if __name__ == "__main__":
       exit_code = asyncio.run(main())
       sys.exit(exit_code)
   ```

## Conclusion

This implementation plan provides a detailed roadmap for standardizing the MCP implementation across Tekton components. By following this plan, we will achieve a more consistent, reliable, and maintainable MCP architecture that simplifies client integration and component development.

The plan is divided into three phases, with clear deliverables for each phase. The focus is on fixing the core issues first, then standardizing the implementation, and finally integrating and testing the full system.

The integration with the OneHeartbeat Sprint is handled through the enhanced registration and heartbeat process, ensuring that both critical infrastructure systems work together effectively.