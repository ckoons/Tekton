#!/usr/bin/env python3
"""
Engram FastMCP Server

A server that implements the Model Context Protocol (MCP) using FastMCP
for providing memory services to compatible clients.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from fastapi import FastAPI, Body, HTTPException, Query, APIRouter, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../.."))
sys.path.insert(0, project_root)

# Add Tekton root to path for shared imports
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Use shared logging setup
from shared.utils.logging_setup import setup_component_logging
logger = setup_component_logging("engram")

# Import FastMCP utilities if available
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        mcp_processor,
        MCPClient
    )
    from tekton.mcp.fastmcp.schema import (
        ToolSchema,
        ProcessorSchema,
        MessageSchema,
        ResponseSchema,
        MCPRequest,
        MCPResponse,
        MCPCapability,
        MCPTool
    )
    from tekton.mcp.fastmcp.adapters import adapt_tool, adapt_processor
    from tekton.mcp.fastmcp.exceptions import MCPProcessingError
    from tekton.mcp.fastmcp.utils.endpoints import (
        create_mcp_router,
        add_standard_mcp_endpoints
    )
    fastmcp_available = True
except ImportError:
    logger.warning("FastMCP not available, some features will be disabled")
    fastmcp_available = False

# Import Engram modules
try:
    # Always import config first
    from engram.core.config import get_config
    
    # Import memory modules and MCP adapter
    from engram.core.memory_manager import MemoryManager
    from engram.core.mcp_adapter import MCPAdapter
    
    # Import FastMCP tools
    if fastmcp_available:
        from engram.core.mcp import (
            get_all_tools,
            get_all_capabilities,
            register_memory_tools,
            register_structured_memory_tools,
            register_nexus_tools
        )
except ImportError as e:
    logger.error(f"Failed to import Engram modules: {e}")
    logger.error("Make sure you're running this from the project root or it's installed")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Engram FastMCP Server",
    description="Model Context Protocol server for Engram memory services using FastMCP",
    version="0.8.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
memory_manager = None
mcp_adapter = None
default_client_id = "claude"

# Create FastMCP router if available
if fastmcp_available:
    mcp_router = create_mcp_router(
        prefix="/mcp",
        tags=["MCP Protocol"]
    )
    app.include_router(mcp_router)
else:
    # Fallback router
    mcp_router = APIRouter(prefix="/mcp", tags=["MCP Protocol"])
    app.include_router(mcp_router)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global memory_manager, mcp_adapter, default_client_id
    
    # Get default client ID from environment
    default_client_id = os.environ.get("ENGRAM_CLIENT_ID", "claude")
    data_dir = os.environ.get("ENGRAM_DATA_DIR", None)
    
    # Initialize memory manager
    try:
        memory_manager = MemoryManager(data_dir=data_dir)
        logger.info(f"Memory manager initialized with data directory: {data_dir or '~/.engram'}")
        
        # Initialize MCP adapter (legacy)
        mcp_adapter = MCPAdapter(memory_manager)
        logger.info("Legacy MCP adapter initialized")
        
        # Initialize FastMCP tools if available
        if fastmcp_available:
            try:
                from tekton.mcp.fastmcp.utils.tooling import ToolRegistry
                
                # Create tool registry
                tool_registry = ToolRegistry()
                
                # Register tools with registry
                await register_memory_tools(memory_manager, tool_registry)
                await register_structured_memory_tools(memory_manager, tool_registry)
                await register_nexus_tools(memory_manager, tool_registry)
                
                logger.info("FastMCP tools registered successfully")
            except Exception as e:
                logger.error(f"Error registering FastMCP tools: {e}")
        
        # Pre-initialize default client
        await memory_manager.get_memory_service(default_client_id)
        await memory_manager.get_structured_memory(default_client_id)
        await memory_manager.get_nexus_interface(default_client_id)
        logger.info(f"Pre-initialized services for default client: {default_client_id}")
        
        logger.info("Server startup complete and ready to accept connections")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Re-raise to prevent server from starting with incomplete initialization
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global memory_manager
    
    if memory_manager:
        await memory_manager.shutdown()
        logger.info("Memory manager shut down")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Engram FastMCP Server",
        "version": "0.8.0",
        "description": "Model Context Protocol for Engram memory services",
        "fastmcp_available": fastmcp_available
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    if not memory_manager or not mcp_adapter:
        raise HTTPException(status_code=500, detail="Server not fully initialized")
    
    return {
        "status": "healthy",
        "mcp": True,
        "fastmcp": fastmcp_available
    }

# Legacy MCP endpoints for backward compatibility

@app.get("/manifest")
async def get_manifest():
    """Get the MCP capability manifest (legacy)."""
    if not mcp_adapter:
        raise HTTPException(status_code=500, detail="MCP adapter not initialized")
    
    return await mcp_adapter.get_manifest()

@app.post("/invoke")
async def invoke_capability(request: Dict[str, Any] = Body(...)):
    """Invoke an MCP capability (legacy)."""
    if not mcp_adapter:
        raise HTTPException(status_code=500, detail="MCP adapter not initialized")
    
    try:
        response = await mcp_adapter.handle_request(request)
        return response
    except Exception as e:
        logger.error(f"Error invoking capability: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to invoke capability: {str(e)}"},
        )

# FastMCP handler functions

async def get_capabilities_func(manager):
    """Get Engram MCP capabilities."""
    if not fastmcp_available:
        return []
        
    return get_all_capabilities(manager)

async def get_tools_func(manager):
    """Get Engram MCP tools."""
    if not fastmcp_available:
        return []
        
    return get_all_tools(manager)

async def process_request_func(manager, request):
    """Process an MCP request."""
    if not fastmcp_available:
        return MCPResponse(
            status="error",
            error="FastMCP not available",
            result=None
        )
    
    try:
        # Check if tool is supported
        tool_name = request.tool
        
        # Define a mapping of tool names to handler functions
        from engram.core.mcp.tools import (
            memory_store, memory_query, get_context,
            structured_memory_add, structured_memory_get, structured_memory_update,
            structured_memory_delete, structured_memory_search,
            nexus_process
        )
        
        tool_handlers = {
            # Memory Operations
            "MemoryStore": memory_store,
            "MemoryQuery": memory_query,
            "GetContext": get_context,
            
            # Structured Memory Operations
            "StructuredMemoryAdd": structured_memory_add,
            "StructuredMemoryGet": structured_memory_get,
            "StructuredMemoryUpdate": structured_memory_update,
            "StructuredMemoryDelete": structured_memory_delete,
            "StructuredMemorySearch": structured_memory_search,
            
            # Nexus Operations
            "NexusProcess": nexus_process
        }
        
        # Check if tool is supported
        if tool_name not in tool_handlers:
            return MCPResponse(
                status="error",
                error=f"Unsupported tool: {tool_name}",
                result=None
            )
        
        # Get the client ID from the request
        client_id = request.client_id or default_client_id
        
        # Call the appropriate handler
        handler = tool_handlers[tool_name]
        
        # Set up dependencies based on the tool
        parameters = request.parameters or {}
        
        if tool_name in ["MemoryStore", "MemoryQuery", "GetContext"]:
            # Get memory service for client
            memory_service = await manager.get_memory_service(client_id)
            parameters["memory_service"] = memory_service
        elif tool_name.startswith("StructuredMemory"):
            # Get structured memory for client
            structured_memory = await manager.get_structured_memory(client_id)
            parameters["structured_memory"] = structured_memory
        elif tool_name == "NexusProcess":
            # Get nexus interface for client
            nexus = await manager.get_nexus_interface(client_id)
            parameters["nexus"] = nexus
            
        # Execute handler
        result = await handler(**parameters)
        
        return MCPResponse(
            status="success",
            result=result,
            error=None
        )
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        return MCPResponse(
            status="error",
            error=f"Error processing request: {str(e)}",
            result=None
        )

# Add standard MCP endpoints if FastMCP is available
if fastmcp_available:
    try:
        # Add standard MCP endpoints to the router
        add_standard_mcp_endpoints(
            router=mcp_router,
            get_capabilities_func=get_capabilities_func,
            get_tools_func=get_tools_func,
            process_request_func=process_request_func,
            component_manager_dependency=lambda: memory_manager
        )
        
        logger.info("Added FastMCP endpoints to Engram API")
    except Exception as e:
        logger.error(f"Error adding FastMCP endpoints: {e}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Engram FastMCP Server")
    parser.add_argument("--client-id", type=str, default=None,
                      help="Default client ID for memory service")
    parser.add_argument("--port", type=int, default=None,
                      help="Port to run the server on")
    parser.add_argument("--host", type=str, default=None,
                      help="Host to bind the server to")
    parser.add_argument("--data-dir", type=str, default=None,
                      help="Directory to store memory data")
    parser.add_argument("--config", type=str, default=None,
                      help="Path to custom config file")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug mode")
    return parser.parse_args()

def main():
    """Main entry point for the CLI command."""
    args = parse_arguments()
    
    # Load configuration
    config = get_config(args.config)
    
    # Override with command line arguments if provided
    if args.client_id:
        config["client_id"] = args.client_id
    if args.data_dir:
        config["data_dir"] = args.data_dir
    if args.port:
        config["mcp_port"] = args.port
    if args.host:
        config["mcp_host"] = args.host
    if args.debug:
        config["debug"] = True
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set environment variables for default client ID and data directory
    os.environ["ENGRAM_CLIENT_ID"] = config["client_id"]
    os.environ["ENGRAM_DATA_DIR"] = config["data_dir"]
    
    # Use MCP port from config or default to 8001 (different from HTTP server)
    mcp_port = config.get("mcp_port", 8001)
    mcp_host = config.get("mcp_host", "127.0.0.1")
    
    # Start the server
    logger.info(f"Starting Engram FastMCP server on {mcp_host}:{mcp_port}")
    logger.info(f"Default client ID: {config['client_id']}, Data directory: {config['data_dir']}")
    
    if config.get("debug", False):
        logger.info("Debug mode enabled")
    
    uvicorn.run(app, host=mcp_host, port=mcp_port)

if __name__ == "__main__":
    main()