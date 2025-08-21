"""
MCP Endpoint Utilities for Tekton Components.

This module provides common utilities for creating and including
FastMCP endpoints in Tekton components.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import JSONResponse

from tekton.mcp.fastmcp.schema import (
    MCPRequest,
    MCPResponse,
    MCPCapability,
    MCPTool
)

logger = logging.getLogger(__name__)

def create_mcp_router(
    prefix: str = "/mcp",
    tags: List[str] = ["mcp"],
    dependencies: List[Depends] = None
) -> APIRouter:
    """
    Create a standard MCP router for a Tekton component.
    
    Args:
        prefix: URL prefix for the router
        tags: FastAPI tags for the router
        dependencies: Optional dependencies for all endpoints
        
    Returns:
        Configured APIRouter for MCP endpoints
    """
    dependencies = dependencies or []
    
    router = APIRouter(
        prefix=prefix,
        tags=tags,
        dependencies=dependencies,
        responses={404: {"description": "Not found"}}
    )
    
    return router


def include_mcp_router(
    app: Any, 
    mcp_router: APIRouter,
    component_name: str
) -> None:
    """
    Include an MCP router in a FastAPI application.
    
    Args:
        app: FastAPI application
        mcp_router: MCP router to include
        component_name: Name of the component (for logging)
    """
    try:
        app.include_router(mcp_router)
        logger.info(f"Added MCP router to {component_name}")
    except Exception as e:
        logger.error(f"Failed to include MCP router for {component_name}: {e}")
        # Continue without MCP router rather than failing the application startup
        pass


def add_standard_mcp_endpoints(
    router: APIRouter,
    get_capabilities_func: Any = None,
    get_tools_func: Any = None,
    process_request_func: Any = None,
    component_manager_dependency: Depends = None
) -> APIRouter:
    """
    Add standard MCP endpoints to a router.
    
    Args:
        router: APIRouter to add endpoints to
        get_capabilities_func: Function to get capabilities
        get_tools_func: Function to get tools
        process_request_func: Function to process requests
        component_manager_dependency: Dependency to get component manager
        
    Returns:
        Router with added endpoints
    """
    
    @router.get("/health")
    async def mcp_health():
        """MCP health check endpoint."""
        return {"status": "healthy", "message": "MCP service is running"}
    
    @router.get("/capabilities")
    async def get_capabilities():
        """Get component MCP capabilities."""
        if get_capabilities_func:
            if component_manager_dependency:
                manager = await component_manager_dependency()
                capabilities = get_capabilities_func(manager)
            else:
                # Call without component manager
                capabilities = get_capabilities_func(None)
            
            # Ensure capabilities is a list of dicts
            if capabilities and isinstance(capabilities, list):
                return {
                    "capabilities": capabilities,
                    "count": len(capabilities)
                }
            else:
                return {
                    "capabilities": [],
                    "count": 0,
                    "message": "No capabilities returned"
                }
        else:
            return {
                "capabilities": [],
                "count": 0,
                "message": "No capabilities function configured"
            }
    
    @router.get("/tools")
    async def get_tools():
        """Get component MCP tools."""
        if get_tools_func:
            if component_manager_dependency:
                manager = await component_manager_dependency()
                tools = get_tools_func(manager)
            else:
                # Call without component manager
                tools = get_tools_func(None)
            
            # Ensure tools is a list of dicts
            if tools and isinstance(tools, list):
                return {
                    "tools": tools,
                    "count": len(tools)
                }
            else:
                return {
                    "tools": [],
                    "count": 0,
                    "message": "No tools returned"
                }
        else:
            return {
                "tools": [],
                "count": 0,
                "message": "No tools function configured"
            }
    
    @router.post("/process")
    async def process_request(
        request: MCPRequest = Body(...)
    ):
        """Process an MCP request."""
        try:
            if process_request_func:
                if component_manager_dependency:
                    manager = await component_manager_dependency()
                    response = await process_request_func(manager, request)
                else:
                    # Call without component manager, passing request data directly
                    response = await process_request_func(request.dict(), None)
                return response
            else:
                return {
                    "status": "error",
                    "error": "MCP request processing not configured",
                    "result": None
                }
        except Exception as e:
            logger.error(f"Error processing MCP request: {e}")
            return {
                "status": "error",
                "error": f"Error processing request: {str(e)}",
                "result": None
            }
    
    return router


# Alias for backward compatibility
add_mcp_endpoints = add_standard_mcp_endpoints