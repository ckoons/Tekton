"""
MCP Endpoints - Model Context Protocol API for Apollo.

This module provides FastAPI endpoints for Apollo's MCP implementation, 
allowing other components to interact with Apollo's capabilities.
"""

import logging
import time
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Body
from pydantic import BaseModel, Field

# Import FastMCP integration
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

# Get Apollo manager and other dependencies
from apollo.api.dependencies import get_apollo_manager
from apollo.core.apollo_manager import ApolloManager
from apollo.core.action_planner import ActionPlanner
from apollo.core.context_observer import ContextObserver
from apollo.core.message_handler import MessageHandler
from apollo.core.predictive_engine import PredictiveEngine
from apollo.core.protocol_enforcer import ProtocolEnforcer
from apollo.core.token_budget import TokenBudgetManager
from apollo.api.models import APIResponse, ResponseStatus

logger = logging.getLogger(__name__)

# Create router
mcp_router = APIRouter(
    prefix="/mcp",
    tags=["mcp"],
    responses={404: {"description": "Not found"}}
)

# Legacy Pydantic models for backward compatibility
class ApolloMCPRequest(BaseModel):
    """Request model for Apollo MCP API."""
    content: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    
class ApolloMCPResponse(BaseModel):
    """Response model for Apollo MCP API."""
    content: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

# Legacy MCP endpoint for backward compatibility
@mcp_router.post("/process", response_model=ApolloMCPResponse)
async def process_message(
    request: ApolloMCPRequest,
    apollo_manager: ApolloManager = Depends(get_apollo_manager)
) -> ApolloMCPResponse:
    """
    Process an MCP request through Apollo.
    
    This endpoint accepts MCP requests and processes them using Apollo's components.
    """
    try:
        # Process the request
        result = await apollo_manager.process_mcp_request(request.content, request.context)
        
        # Create response
        return ApolloMCPResponse(
            content=result.get("content", {}),
            context=result.get("context"),
            metadata={
                "processed_by": "apollo.mcp",
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing MCP request: {e}")

# FastMCP endpoints
@mcp_router.post("/v2/process", response_model=MCPResponse)
async def process_fastmcp_request(
    request: MCPRequest = Body(...),
    apollo_manager: ApolloManager = Depends(get_apollo_manager)
) -> MCPResponse:
    """
    Process a FastMCP request.
    
    Handles a Model Context Protocol request using FastMCP and returns the result.
    """
    try:
        # Process the MCP request using Apollo manager's FastMCP implementation
        response = await apollo_manager.process_fastmcp_request(request)
        return response
        
    except MCPProcessingError as e:
        logger.error(f"MCP processing error: {e}")
        return MCPResponse(
            status="error",
            error=str(e),
            result=None
        )
        
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        return MCPResponse(
            status="error",
            error=f"Internal server error: {str(e)}",
            result=None
        )

@mcp_router.get("/capabilities")
async def get_capabilities(
    apollo_manager: ApolloManager = Depends(get_apollo_manager)
) -> Dict[str, Any]:
    """
    Get Apollo's MCP capabilities.
    
    This endpoint returns information about Apollo's MCP capabilities,
    including supported content types, tools, and processors.
    """
    capabilities_list = apollo_manager.get_mcp_capabilities()
    
    return {
        "version": "mcp/2.0",
        "component": "apollo",
        "capabilities": [cap.name for cap in capabilities_list],
        "content_types": [
            "text",
            "structured",
            "code"
        ],
        "mcp_version": "fastmcp",
        "detailed_capabilities": [cap.model_dump() for cap in capabilities_list]
    }

@mcp_router.get("/tools")
async def get_tools(
    apollo_manager: ApolloManager = Depends(get_apollo_manager)
) -> Dict[str, Any]:
    """
    Get Apollo's MCP tools.
    
    This endpoint returns information about Apollo's MCP tools.
    """
    tools_list = apollo_manager.get_mcp_tools()
    
    return {
        "version": "mcp/2.0",
        "component": "apollo",
        "tool_count": len(tools_list),
        "tools": [tool.model_dump() for tool in tools_list]
    }

@mcp_router.get("/health")
async def health_check(
    apollo_manager: ApolloManager = Depends(get_apollo_manager)
) -> Dict[str, Any]:
    """
    Health check endpoint for Apollo's MCP implementation.
    
    This endpoint checks if Apollo's MCP implementation is healthy and returns
    information about its current state.
    """
    return {
        "status": "healthy",
        "component": "apollo.mcp",
        "fastmcp_available": True,
        "timestamp": time.time(),
        "components": {
            "action_planner": apollo_manager.action_planner is not None,
            "context_observer": apollo_manager.context_observer is not None,
            "message_handler": apollo_manager.message_handler is not None,
            "predictive_engine": apollo_manager.predictive_engine is not None,
            "protocol_enforcer": apollo_manager.protocol_enforcer is not None,
            "token_budget_manager": apollo_manager.token_budget_manager is not None
        }
    }