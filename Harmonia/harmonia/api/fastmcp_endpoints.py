"""
FastMCP endpoints for Harmonia API.

This module provides REST API endpoints for FastMCP in Harmonia,
following the unified MCP approach for workflow orchestration.
"""

import logging
from typing import Optional
import sys
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

# Import shared workflow endpoint
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
from workflow.endpoint_template import create_workflow_endpoint

from ..core.engine import WorkflowEngine
from ..core.mcp import (
    create_mcp_router,
    add_standard_mcp_endpoints
)
from ..core.mcp.tools import register_tools

# Setup logging
logger = logging.getLogger(__name__)

# Global workflow engine reference
workflow_engine: Optional[WorkflowEngine] = None

# Create the FastMCP router
fastmcp_router = create_mcp_router()

# Add standard MCP endpoints
add_standard_mcp_endpoints(fastmcp_router)

# Dependency to get the workflow engine
async def get_workflow_engine() -> WorkflowEngine:
    """
    Get the workflow engine, ensuring it's initialized.
    
    Returns:
        Workflow engine instance
        
    Raises:
        HTTPException: If the engine is not initialized
    """
    global workflow_engine
    
    if workflow_engine is None:
        raise HTTPException(status_code=503, detail="Workflow engine not initialized")
    
    return workflow_engine

def set_workflow_engine(engine: WorkflowEngine):
    """
    Set the workflow engine for FastMCP.
    
    Args:
        engine: Workflow engine instance
    """
    global workflow_engine
    workflow_engine = engine

# Startup and shutdown event handlers
async def fastmcp_startup():
    """Initialize the FastMCP services on startup."""
    global workflow_engine
    
    if workflow_engine:
        # Register all tools with the workflow engine for dependency injection
        await register_tools(workflow_engine)
        logger.info("FastMCP services initialized for Harmonia")
    else:
        logger.warning("FastMCP startup called but workflow engine not set")

async def fastmcp_shutdown():
    """Shut down the FastMCP services."""
    global workflow_engine
    
    if workflow_engine:
        # Cleanup if needed
        workflow_engine = None
        logger.info("FastMCP services shut down for Harmonia")

# Additional custom endpoints
@fastmcp_router.get("/health")
async def health_check():
    """
    Check FastMCP health for Harmonia.
    
    Returns:
        Health status
    """
    global workflow_engine
    
    try:
        if workflow_engine:
            # Check workflow engine status
            status = "running" if workflow_engine else "not_initialized"
            
            return {
                "status": "ok" if status == "running" else "degraded",
                "component": "harmonia-fastmcp",
                "workflow_engine": status,
                "message": "FastMCP services are healthy" if status == "running" else "Workflow engine not initialized"
            }
        else:
            return {
                "status": "degraded",
                "component": "harmonia-fastmcp",
                "workflow_engine": "not_initialized",
                "message": "Workflow engine not initialized"
            }
    except Exception as e:
        logger.error(f"FastMCP health check failed: {e}")
        return {
            "status": "error",
            "component": "harmonia-fastmcp",
            "message": f"Health check failed: {str(e)}"
        }

@fastmcp_router.get("/workflow-status")
async def get_harmonia_status(
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Get detailed Harmonia workflow engine status.
    
    Args:
        engine: Workflow engine instance
        
    Returns:
        Detailed status information
    """
    try:
        # Get active executions count
        active_executions = len(engine.active_executions) if hasattr(engine, 'active_executions') else 0
        
        # Get components
        components = engine.component_registry.get_components() if engine.component_registry else []
        
        return {
            "status": "running",
            "component": "harmonia",
            "active_executions": active_executions,
            "components": components,
            "component_count": len(components),
            "capabilities": [
                "workflow_definition_management",
                "workflow_execution", 
                "template_management",
                "component_integration"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting Harmonia status: {e}")
        return {
            "status": "error",
            "component": "harmonia",
            "message": f"Status check failed: {str(e)}"
        }

# Add standardized workflow endpoint to the router
workflow_router = create_workflow_endpoint("harmonia") 
for route in workflow_router.routes:
    fastmcp_router.routes.append(route)