"""
MCP endpoints for Ergon API.

This module provides REST API endpoints for MCP functionality in Ergon.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Union

from fastapi import APIRouter, HTTPException, Depends, Body, Query, Path
from fastapi.responses import JSONResponse

from ..core.mcp_client import MCPClient
from ..utils.mcp_adapter import (
    prepare_text_content,
    prepare_code_content,
    prepare_structured_content,
    extract_text_from_mcp_result,
    extract_data_from_mcp_result
)

# Setup logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(tags=["mcp"])

# Create shared MCP client
mcp_client = MCPClient(client_id="ergon-api", client_name="Ergon API")

# Initialize client when module loads
@router.on_event("startup")
async def initialize_mcp_client():
    """Initialize the MCP client on startup."""
    await mcp_client.initialize()

@router.on_event("shutdown")
async def close_mcp_client():
    """Close the MCP client on shutdown."""
    await mcp_client.close()

@router.post("/process")
async def process_content(
    content: Dict[str, Any] = Body(...),
) -> Dict[str, Any]:
    """
    Process content using MCP.
    
    Args:
        content: Dictionary containing content and processing options
        
    Returns:
        Processing result
    """
    try:
        # Extract content and options
        content_type = content.get("content_type", "text")
        content_data = content.get("content", {})
        processing_options = content.get("processing_options", {})
        context = content.get("context")
        tools = content.get("tools", [])
        
        # Process based on content type
        if content_type == "text":
            result = await mcp_client.process_content(
                content=content_data.get("text", ""),
                content_type="text",
                context=context,
                processing_options=processing_options,
                tools=tools
            )
        elif content_type == "code":
            result = await mcp_client.process_content(
                content=content_data.get("code", ""),
                content_type="code",
                context=context,
                processing_options=processing_options,
                tools=tools
            )
        elif content_type == "image":
            # Expect base64-encoded image
            result = await mcp_client.process_content(
                content=content_data.get("image", ""),
                content_type="image",
                context=context,
                processing_options=processing_options,
                tools=tools
            )
        elif content_type == "structured":
            result = await mcp_client.process_content(
                content=content_data.get("data", {}),
                content_type="structured",
                context=context,
                processing_options=processing_options,
                tools=tools
            )
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"Unsupported content type: {content_type}"}
            )
        
        return result
    except Exception as e:
        logger.error(f"Error processing MCP content: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing error: {str(e)}"}
        )

@router.post("/tools/register")
async def register_tool(
    tool_spec: Dict[str, Any] = Body(...),
) -> Dict[str, Any]:
    """
    Register a tool with MCP.
    
    Args:
        tool_spec: Tool specification
        
    Returns:
        Registration result
    """
    try:
        # Extract tool details
        tool_id = tool_spec.get("tool_id", f"ergon-tool-{uuid.uuid4()}")
        name = tool_spec.get("name", tool_id)
        description = tool_spec.get("description", "")
        parameters = tool_spec.get("parameters", {})
        returns = tool_spec.get("returns", {})
        metadata = tool_spec.get("metadata", {})
        
        # Register tool
        success = await mcp_client.register_tool(
            tool_id=tool_id,
            name=name,
            description=description,
            parameters=parameters,
            returns=returns,
            metadata=metadata
        )
        
        if success:
            return {"success": True, "tool_id": tool_id}
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to register tool"}
            )
    except Exception as e:
        logger.error(f"Error registering tool: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Registration error: {str(e)}"}
        )

@router.delete("/tools/{tool_id}")
async def unregister_tool(
    tool_id: str = Path(..., description="Tool ID to unregister"),
) -> Dict[str, Any]:
    """
    Unregister a tool from MCP.
    
    Args:
        tool_id: ID of the tool to unregister
        
    Returns:
        Unregistration result
    """
    try:
        success = await mcp_client.unregister_tool(tool_id)
        
        if success:
            return {"success": True}
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to unregister tool"}
            )
    except Exception as e:
        logger.error(f"Error unregistering tool: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Unregistration error: {str(e)}"}
        )

@router.post("/tools/execute/{tool_id}")
async def execute_tool(
    tool_id: str = Path(..., description="Tool ID to execute"),
    parameters: Dict[str, Any] = Body(...),
    context: Optional[Dict[str, Any]] = Body(None),
) -> Dict[str, Any]:
    """
    Execute a tool.
    
    Args:
        tool_id: ID of the tool to execute
        parameters: Tool parameters
        context: Optional execution context
        
    Returns:
        Tool execution result
    """
    try:
        result = await mcp_client.execute_tool(
            tool_id=tool_id,
            parameters=parameters,
            context=context
        )
        
        return result
    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Execution error: {str(e)}"}
        )

@router.post("/contexts")
async def create_context(
    context_data: Dict[str, Any] = Body(...),
) -> Dict[str, Any]:
    """
    Create a new context.
    
    Args:
        context_data: Context data
        
    Returns:
        Context creation result
    """
    try:
        # Extract context details
        context_type = context_data.get("context_type", "general")
        content = context_data.get("content", {})
        metadata = context_data.get("metadata", {})
        
        # Create context
        context_id = await mcp_client.create_context(
            context_type=context_type,
            content=content,
            metadata=metadata
        )
        
        if context_id:
            return {"success": True, "context_id": context_id}
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to create context"}
            )
    except Exception as e:
        logger.error(f"Error creating context: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Context creation error: {str(e)}"}
        )

@router.post("/contexts/{context_id}/enhance")
async def enhance_context(
    context_id: str = Path(..., description="Context ID to enhance"),
    enhancement: Dict[str, Any] = Body(...),
) -> Dict[str, Any]:
    """
    Enhance an existing context.
    
    Args:
        context_id: ID of the context to enhance
        enhancement: Enhancement data
        
    Returns:
        Context enhancement result
    """
    try:
        # Extract enhancement details
        content = enhancement.get("content", {})
        operation = enhancement.get("operation", "add")
        
        # Enhance context
        success = await mcp_client.enhance_context(
            context_id=context_id,
            content=content,
            operation=operation
        )
        
        if success:
            return {"success": True}
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to enhance context"}
            )
    except Exception as e:
        logger.error(f"Error enhancing context: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Context enhancement error: {str(e)}"}
        )

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Check MCP client health.
    
    Returns:
        Health status
    """
    # Check if client is initialized
    if mcp_client.session is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "MCP client not initialized"
            }
        )
    
    return {
        "status": "ok",
        "client_id": mcp_client.client_id,
        "client_name": mcp_client.client_name,
        "tools_registered": len(mcp_client.tools)
    }