"""
MCP Endpoints - REST API for Multimodal Cognitive Protocol.

This module provides FastAPI endpoints for multimodal message processing,
tool registration and execution, and context management.
"""

import time
import logging
from typing import Dict, List, Any, Optional, Union

from fastapi import APIRouter, HTTPException, Depends, Header, Request, Body
from fastapi.responses import JSONResponse
from pydantic import Field
from tekton.models import TektonBaseModel, MCPTool, MCPToolCall, MCPToolResponse

logger = logging.getLogger(__name__)

# Create router
mcp_router = APIRouter(
    prefix="/mcp/v2",
    tags=["mcp"],
    responses={404: {"description": "Not found"}}
)


# Pydantic models for API

class ContentItem(TektonBaseModel):
    """Model for MCP content items."""
    type: str
    format: Optional[str] = None
    data: Any
    metadata: Optional[Dict[str, Any]] = None


class MCPMessage(TektonBaseModel):
    """Model for MCP messages."""
    id: Optional[str] = None
    version: str = "mcp/1.0"
    source: Dict[str, Any]
    destination: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    content: List[ContentItem]
    processing: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None


class ToolSpec(TektonBaseModel):
    """Model for tool specifications."""
    id: Optional[str] = None
    name: str
    description: str
    input_schema: Dict[str, Any] = Field(alias="schema")
    tags: Optional[List[str]] = None
    version: Optional[str] = None
    endpoint: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ToolRegistrationResponse(TektonBaseModel):
    """Model for tool registration responses."""
    success: bool
    tool_id: str
    message: Optional[str] = None


class ToolExecutionRequest(TektonBaseModel):
    """Model for tool execution requests."""
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class ProcessorSpec(TektonBaseModel):
    """Model for processor specifications."""
    id: Optional[str] = None
    name: str
    description: str
    capabilities: List[str]
    endpoint: str
    version: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProcessorRegistrationResponse(TektonBaseModel):
    """Model for processor registration responses."""
    success: bool
    processor_id: str
    message: Optional[str] = None


class ContextCreationRequest(TektonBaseModel):
    """Model for context creation requests."""
    data: Dict[str, Any]
    source: Dict[str, Any]
    context_id: Optional[str] = None


class ContextUpdateRequest(TektonBaseModel):
    """Model for context update requests."""
    updates: Dict[str, Any]
    source: Dict[str, Any]
    operation: str = "update"


# Dependency to get MCP service from request state
async def get_mcp_service(request: Request):
    """Get the MCP service from request state."""
    if not hasattr(request.app.state, "mcp_service"):
        logger.error("MCP service not found in app state")
        raise HTTPException(status_code=500, detail="MCP service not initialized")
    
    mcp_service = request.app.state.mcp_service
    
    try:
        # Ensure service is initialized
        await mcp_service.initialize()
    except Exception as e:
        logger.error(f"Error initializing MCP service: {e}")
        # Continue even if initialization fails
        # Some functionality may still work without channels
    
    return mcp_service


# API endpoints

@mcp_router.post("/process")
async def process_message(
    message: MCPMessage,
    mcp_service = Depends(get_mcp_service)
):
    """
    Process an MCP message.
    
    This endpoint processes a multimodal message according to the MCP protocol.
    """
    # Convert Pydantic model to dictionary
    msg_dict = message.dict()
    
    # Add message ID if not provided
    if not message.id:
        msg_dict["id"] = f"msg-{int(time.time() * 1000)}"
    
    # Add timestamp
    msg_dict["timestamp"] = time.time()
    
    # Process message
    result = await mcp_service.process_message(msg_dict)
    
    if "error" in result:
        return JSONResponse(
            content={"error": result["error"]},
            status_code=400
        )
    
    return result


@mcp_router.post("/tools", response_model=ToolRegistrationResponse)
async def register_tool(
    tool_spec: ToolSpec,
    mcp_service = Depends(get_mcp_service)
):
    """
    Register a tool with the MCP service.
    
    This endpoint allows registration of tools that can be used via MCP.
    """
    tool_id = await mcp_service.register_tool(tool_spec.dict(by_alias=True))
    
    if not tool_id:
        raise HTTPException(status_code=400, detail="Tool registration failed")
    
    return ToolRegistrationResponse(
        success=True,
        tool_id=tool_id,
        message="Tool registered successfully"
    )


@mcp_router.delete("/tools/{tool_id}")
async def unregister_tool(
    tool_id: str,
    mcp_service = Depends(get_mcp_service)
):
    """
    Unregister a tool from the MCP service.
    
    This endpoint allows tools to be removed from the registry.
    """
    success = await mcp_service.unregister_tool(tool_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return {"success": True, "message": "Tool unregistered successfully"}


@mcp_router.post("/tools/{tool_id}/execute")
async def execute_tool(
    tool_id: str,
    execution: ToolExecutionRequest,
    mcp_service = Depends(get_mcp_service)
):
    """
    Execute a tool.
    
    This endpoint executes a registered tool with the provided parameters.
    """
    result = await mcp_service.execute_tool(
        tool_id=tool_id,
        parameters=execution.parameters,
        context=execution.context
    )
    
    if not result.get("success", False):
        error_msg = result.get("error", "Tool execution failed")
        raise HTTPException(status_code=400, detail=error_msg)
    
    return result


@mcp_router.get("/tools")
async def list_tools(
    mcp_service = Depends(get_mcp_service)
):
    """
    List all registered tools.
    
    This endpoint returns a list of all tools registered with the MCP service.
    """
    tools = getattr(mcp_service, "tools", {})
    
    # Return only serializable data to avoid recursion errors
    serializable_tools = []
    for tool_id, tool in tools.items():
        # Create a copy without non-serializable fields
        tool_copy = {
            "id": tool.get("id"),
            "name": tool.get("name"),
            "description": tool.get("description"),
            "schema": tool.get("schema", {}),
            "tags": tool.get("tags", []),
            "version": tool.get("version"),
            "endpoint": tool.get("endpoint"),
            "metadata": tool.get("metadata", {}),
            "registered_at": tool.get("registered_at")
        }
        # Remove None values to keep response clean
        tool_copy = {k: v for k, v in tool_copy.items() if v is not None}
        serializable_tools.append(tool_copy)
    
    return serializable_tools


@mcp_router.get("/tools/{tool_id}")
async def get_tool(
    tool_id: str,
    mcp_service = Depends(get_mcp_service)
):
    """
    Get tool information.
    
    This endpoint retrieves information about a specific tool.
    """
    tool = await mcp_service.get_tool(tool_id)
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return tool


@mcp_router.post("/processors", response_model=ProcessorRegistrationResponse)
async def register_processor(
    processor_spec: ProcessorSpec,
    mcp_service = Depends(get_mcp_service)
):
    """
    Register a processor with the MCP service.
    
    This endpoint allows registration of processors that can handle MCP messages.
    """
    processor_id = await mcp_service.register_processor(processor_spec.dict(by_alias=True))
    
    if not processor_id:
        raise HTTPException(status_code=400, detail="Processor registration failed")
    
    return ProcessorRegistrationResponse(
        success=True,
        processor_id=processor_id,
        message="Processor registered successfully"
    )


@mcp_router.get("/processors/{processor_id}")
async def get_processor(
    processor_id: str,
    mcp_service = Depends(get_mcp_service)
):
    """
    Get processor information.
    
    This endpoint retrieves information about a specific processor.
    """
    processor = await mcp_service.get_processor(processor_id)
    
    if not processor:
        raise HTTPException(status_code=404, detail="Processor not found")
    
    return processor


@mcp_router.post("/contexts")
async def create_context(
    context_request: ContextCreationRequest,
    mcp_service = Depends(get_mcp_service)
):
    """
    Create a new context.
    
    This endpoint creates a new context for multimodal processing.
    """
    context_id = await mcp_service.create_context(
        data=context_request.data,
        source=context_request.source,
        context_id=context_request.context_id
    )
    
    if not context_id:
        raise HTTPException(status_code=400, detail="Context creation failed")
    
    return {"success": True, "context_id": context_id}


@mcp_router.patch("/contexts/{context_id}")
async def update_context(
    context_id: str,
    update_request: ContextUpdateRequest,
    mcp_service = Depends(get_mcp_service)
):
    """
    Update a context.
    
    This endpoint updates an existing context with new information.
    """
    success = await mcp_service.update_context(
        context_id=context_id,
        updates=update_request.updates,
        source=update_request.source,
        operation=update_request.operation
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Context not found")
    
    return {"success": True, "context_id": context_id}


@mcp_router.get("/contexts/{context_id}")
async def get_context(
    context_id: str,
    mcp_service = Depends(get_mcp_service)
):
    """
    Get a context.
    
    This endpoint retrieves information about a specific context.
    """
    context = await mcp_service.get_context(context_id)
    
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    
    return context


@mcp_router.get("/capabilities")
async def get_capabilities():
    """
    Get MCP capabilities.
    
    This endpoint returns information about the capabilities of the MCP service.
    """
    return {
        "version": "mcp/1.0",
        "modalities": ["text", "code", "image", "structured"],
        "supported_formats": {
            "text": ["text/plain", "text/markdown", "text/html"],
            "code": ["text/plain", "text/x-python", "text/javascript"],
            "image": ["image/png", "image/jpeg", "image/gif"],
            "structured": ["application/json", "application/x-yaml"]
        },
        "processing_capabilities": [
            "text_analysis",
            "code_analysis",
            "image_analysis",
            "context_management",
            "cross_modal_reasoning"
        ]
    }

@mcp_router.get("/health")
async def health_check(
    mcp_service = Depends(get_mcp_service)
):
    """
    Health check endpoint for the MCP service.
    
    This endpoint checks if the MCP service is healthy and returns
    information about its current state.
    """
    # Check if channels are initialized
    channels_initialized = getattr(mcp_service, "_channels_initialized", False)
    
    # Get tool and processor counts
    tool_count = len(getattr(mcp_service, "tools", {}))
    processor_count = len(getattr(mcp_service, "processors", {}))
    context_count = len(getattr(mcp_service, "contexts", {}))
    
    return {
        "status": "healthy",
        "channels_initialized": channels_initialized,
        "tool_count": tool_count,
        "processor_count": processor_count,
        "context_count": context_count,
        "timestamp": time.time()
    }