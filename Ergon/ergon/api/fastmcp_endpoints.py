"""
FastMCP endpoints for Ergon API.

This module provides REST API endpoints for FastMCP in Ergon,
following the unified MCP approach.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from ..core.a2a_client import A2AClient
from ..core.mcp import (
    create_mcp_router,
    add_standard_mcp_endpoints,
    register_tools
)

# Setup logging
logger = logging.getLogger(__name__)

# Global state
a2a_client: Optional[A2AClient] = None

# Create the FastMCP router
fastmcp_router = create_mcp_router()

# Add standard MCP endpoints
add_standard_mcp_endpoints(fastmcp_router)

# Dependency to get the A2A client
async def get_a2a_client() -> A2AClient:
    """
    Get the A2A client, initializing it if necessary.
    
    Returns:
        A2A client instance
    """
    global a2a_client
    
    if not a2a_client:
        a2a_client = A2AClient(
            agent_id="ergon-fastmcp",
            agent_name="Ergon FastMCP Service",
            capabilities=["agent_management", "workflow_management", "task_management"]
        )
        await a2a_client.initialize()
        await a2a_client.register()
        
        # Register all tools with the client for dependency injection
        await register_tools(a2a_client)
    
    return a2a_client

# Startup and shutdown event handlers
async def fastmcp_startup():
    """Initialize the FastMCP services on startup."""
    # Ensure the A2A client is initialized
    await get_a2a_client()
    logger.info("FastMCP services initialized")

async def fastmcp_shutdown():
    """Shut down the FastMCP services."""
    global a2a_client
    
    if a2a_client:
        await a2a_client.close()
        a2a_client = None
        logger.info("FastMCP services shut down")

# Additional custom endpoints can be added here
@fastmcp_router.get("/health")
async def health_check():
    """
    Check FastMCP health.
    
    Returns:
        Health status
    """
    global a2a_client
    
    try:
        # Check if A2A client is initialized
        if a2a_client and a2a_client.initialized:
            # Try to discover agents as a health check
            await a2a_client.discover_agents()
            
            return {
                "status": "ok",
                "component": "ergon-fastmcp",
                "message": "FastMCP services are healthy"
            }
        else:
            return {
                "status": "degraded",
                "component": "ergon-fastmcp",
                "message": "A2A client not initialized"
            }
    except Exception as e:
        logger.error(f"FastMCP health check failed: {e}")
        return {
            "status": "error",
            "component": "ergon-fastmcp",
            "message": f"Health check failed: {str(e)}"
        }