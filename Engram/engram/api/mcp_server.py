#!/usr/bin/env python3
"""
Engram MCP Server

A server that implements the Multi-Capability Provider (MCP) protocol
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

# Import Engram modules
try:
    # Always import config first
    from engram.core.config import get_config
    
    # Import memory modules and MCP adapter
    from engram.core.memory_manager import MemoryManager
    from engram.core.mcp_adapter import MCPAdapter
except ImportError as e:
    logger.error(f"Failed to import Engram modules: {e}")
    logger.error("Make sure you're running this from the project root or it's installed")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Engram MCP Server",
    description="Multi-Capability Provider server for Engram memory services",
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
        
        # Initialize MCP adapter
        mcp_adapter = MCPAdapter(memory_manager)
        logger.info("MCP adapter initialized")
        
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
        "message": "Engram MCP Server",
        "version": "0.8.0",
        "description": "Multi-Capability Provider for Engram memory services"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    if not memory_manager or not mcp_adapter:
        raise HTTPException(status_code=500, detail="Server not fully initialized")
    
    return {"status": "healthy", "mcp": True}

@app.get("/manifest")
async def get_manifest():
    """Get the MCP capability manifest."""
    if not mcp_adapter:
        raise HTTPException(status_code=500, detail="MCP adapter not initialized")
    
    return await mcp_adapter.get_manifest()

@app.post("/invoke")
async def invoke_capability(request: Dict[str, Any] = Body(...)):
    """Invoke an MCP capability."""
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

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Engram MCP Server")
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
    logger.info(f"Starting Engram MCP server on {mcp_host}:{mcp_port}")
    logger.info(f"Default client ID: {config['client_id']}, Data directory: {config['data_dir']}")
    
    if config.get("debug", False):
        logger.info("Debug mode enabled")
    
    uvicorn.run(app, host=mcp_host, port=mcp_port)

if __name__ == "__main__":
    main()
