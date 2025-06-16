#!/usr/bin/env python3
"""
Ollama MCP Server

A server that implements the Multi-Capability Provider (MCP) protocol
for providing Ollama language model services to compatible clients.
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
    
    # Import Ollama MCP adapter
    from engram.core.ollama_mcp_adapter import OllamaMCPAdapter
except ImportError as e:
    logger.error(f"Failed to import Engram modules: {e}")
    logger.error("Make sure you're running this from the project root or it's installed")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Ollama MCP Server",
    description="Multi-Capability Provider server for Ollama language model services",
    version="1.0.0"
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
ollama_adapter = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global ollama_adapter
    
    # Get Ollama host from environment or use default
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    
    # Initialize Ollama MCP adapter
    try:
        ollama_adapter = OllamaMCPAdapter(host=ollama_host)
        logger.info(f"Ollama MCP adapter initialized with host: {ollama_host}")
        logger.info(f"Available models: {', '.join(ollama_adapter.available_models[:5] if len(ollama_adapter.available_models) > 5 else ollama_adapter.available_models)}")
        
        logger.info("Server startup complete and ready to accept connections")
    except Exception as e:
        logger.error(f"Failed to initialize Ollama adapter: {e}")
        # Re-raise to prevent server from starting with incomplete initialization
        raise

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Ollama MCP Server",
        "version": "1.0.0",
        "description": "Multi-Capability Provider for Ollama language model services"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    if not ollama_adapter:
        raise HTTPException(status_code=500, detail="Server not fully initialized")
    
    return {"status": "healthy", "mcp": True, "models_available": len(ollama_adapter.available_models) > 0}

@app.get("/manifest")
async def get_manifest():
    """Get the MCP capability manifest."""
    if not ollama_adapter:
        raise HTTPException(status_code=500, detail="Ollama adapter not initialized")
    
    return await ollama_adapter.get_manifest()

@app.post("/invoke")
async def invoke_capability(request: Dict[str, Any] = Body(...)):
    """Invoke an MCP capability."""
    if not ollama_adapter:
        raise HTTPException(status_code=500, detail="Ollama adapter not initialized")
    
    try:
        response = await ollama_adapter.handle_request(request)
        return response
    except Exception as e:
        logger.error(f"Error invoking capability: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to invoke capability: {str(e)}"},
        )

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ollama MCP Server")
    parser.add_argument("--port", type=int, default=None,
                      help="Port to run the server on")
    parser.add_argument("--host", type=str, default=None,
                      help="Host to bind the server to")
    parser.add_argument("--ollama-host", type=str, default=None,
                      help="Ollama API host URL")
    parser.add_argument("--client-id", type=str, default=None,
                      help="Default client ID for memory service")
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
    if args.port:
        config["ollama_mcp_port"] = args.port
    if args.host:
        config["ollama_mcp_host"] = args.host
    if args.ollama_host:
        os.environ["OLLAMA_HOST"] = args.ollama_host
    if args.debug:
        config["debug"] = True
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set environment variables for default client ID
    if "client_id" in config:
        os.environ["ENGRAM_CLIENT_ID"] = config["client_id"]
    
    # Use Ollama MCP port from config or default to 8002 (different from HTTP and MCP servers)
    ollama_mcp_port = config.get("ollama_mcp_port", 8002)
    ollama_mcp_host = config.get("ollama_mcp_host", "127.0.0.1")
    
    # Start the server
    logger.info(f"Starting Ollama MCP server on {ollama_mcp_host}:{ollama_mcp_port}")
    if "client_id" in config:
        logger.info(f"Default client ID for memory integration: {config['client_id']}")
    
    if config.get("debug", False):
        logger.info("Debug mode enabled")
    
    uvicorn.run(app, host=ollama_mcp_host, port=ollama_mcp_port)

if __name__ == "__main__":
    main()