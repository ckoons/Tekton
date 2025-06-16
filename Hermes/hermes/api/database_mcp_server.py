#!/usr/bin/env python3
"""
Database MCP Server

A server that implements the Multi-Capability Provider (MCP) protocol
for providing database services to compatible clients.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("hermes.database_mcp_server")

# Import Hermes modules
from hermes.core.database.manager import DatabaseManager
from hermes.core.database.mcp_adapter import DatabaseMCPAdapter

# Initialize FastAPI app
app = FastAPI(
    title="Hermes Database MCP Server",
    description="Multi-Capability Provider server for Hermes database services",
    version="0.1.0"
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
database_manager = None
mcp_adapter = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global database_manager, mcp_adapter
    
    # Get data directory from environment
    data_dir = os.environ.get("HERMES_DATA_DIR", "~/.tekton/data")
    expanded_data_dir = os.path.expanduser(data_dir)
    
    # Initialize database manager
    try:
        database_manager = DatabaseManager(base_path=expanded_data_dir)
        logger.info(f"Database manager initialized with data directory: {expanded_data_dir}")
        
        # Initialize MCP adapter
        mcp_adapter = DatabaseMCPAdapter(database_manager)
        logger.info("Database MCP adapter initialized")
        
        logger.info("Server startup complete and ready to accept connections")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Re-raise to prevent server from starting with incomplete initialization
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global database_manager
    
    if database_manager:
        await database_manager.close_all_connections()
        logger.info("All database connections closed")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Hermes Database MCP Server",
        "version": "0.1.0",
        "description": "Multi-Capability Provider for Hermes database services"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    if not database_manager or not mcp_adapter:
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
    parser = argparse.ArgumentParser(description="Hermes Database MCP Server")
    parser.add_argument("--port", type=int, default=8002,
                      help="Port to run the server on")
    parser.add_argument("--host", type=str, default="127.0.0.1",
                      help="Host to bind the server to")
    parser.add_argument("--data-dir", type=str, default=None,
                      help="Directory to store database data")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug mode")
    return parser.parse_args()

def main():
    """Main entry point for the CLI command."""
    args = parse_arguments()
    
    # Override with command line arguments if provided
    if args.data_dir:
        os.environ["HERMES_DATA_DIR"] = args.data_dir
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Start the server
    logger.info(f"Starting Hermes Database MCP server on {args.host}:{args.port}")
    logger.info(f"Data directory: {os.environ.get('HERMES_DATA_DIR', '~/.tekton/data')}")
    
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()