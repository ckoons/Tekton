"""MCP Adapter utilities for Ergon.

This module provides helper functions for working with the MCP protocol,
including content preparation and tool registration utilities.
"""

import os
import logging
import base64
from typing import Dict, List, Any, Optional, Union, BinaryIO, Callable

from .hermes_helper import register_with_hermes

logger = logging.getLogger(__name__)

def prepare_text_content(text: str) -> Dict[str, Any]:
    """
    Prepare text content for MCP processing.
    
    Args:
        text: Text content
        
    Returns:
        Prepared MCP content
    """
    return {
        "content_type": "text",
        "content": {"text": text}
    }

def prepare_code_content(code: str, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Prepare code content for MCP processing.
    
    Args:
        code: Code content
        language: Programming language
        
    Returns:
        Prepared MCP content
    """
    content = {"text": code}
    if language:
        content["language"] = language
        
    return {
        "content_type": "code",
        "content": content
    }

def prepare_structured_content(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare structured data for MCP processing.
    
    Args:
        data: Structured data
        
    Returns:
        Prepared MCP content
    """
    return {
        "content_type": "structured",
        "content": {"data": data}
    }

def prepare_image_content(image: Union[bytes, BinaryIO, str]) -> Dict[str, Any]:
    """
    Prepare image content for MCP processing.
    
    Args:
        image: Image content (bytes, file-like object, or path)
        
    Returns:
        Prepared MCP content
    """
    if isinstance(image, str) and os.path.exists(image):
        # Path to an image file
        with open(image, "rb") as f:
            image_data = f.read()
    elif isinstance(image, bytes):
        # Raw bytes
        image_data = image
    elif hasattr(image, "read"):
        # File-like object
        image_data = image.read()
        if not isinstance(image_data, bytes):
            raise ValueError("File-like object must contain binary data")
    else:
        raise ValueError(f"Unsupported image type: {type(image)}")
    
    # Encode as base64
    encoded = base64.b64encode(image_data).decode("utf-8")
    
    return {
        "content_type": "image",
        "content": {"image": encoded, "format": "base64"}
    }

async def register_mcp_tool(
    tool_id: str,
    name: str,
    description: str,
    parameters: Dict[str, Any],
    returns: Dict[str, Any],
    handler: Optional[Callable] = None,
    client: Optional[Any] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Register a tool with the MCP service.
    
    Args:
        tool_id: Unique identifier for the tool
        name: Human-readable name for the tool
        description: Tool description
        parameters: Tool parameters
        returns: Tool return value description
        handler: Function to handle tool invocations
        client: MCP client instance
        metadata: Additional metadata
        
    Returns:
        True if registration was successful
    """
    if client:
        # If we have a client instance, use it
        return await client.register_tool(
            tool_id=tool_id,
            name=name,
            description=description,
            parameters=parameters,
            returns=returns,
            handler=handler,
            metadata=metadata
        )
    else:
        # Otherwise, register the tool as a service with Hermes
        service_id = f"mcp-tool-{tool_id}"
        capabilities = ["mcp_tool"]
        
        tool_metadata = {
            "tool_id": tool_id,
            "description": description,
            "parameters": parameters,
            "returns": returns,
            **(metadata or {})
        }
        
        return await register_with_hermes(
            service_id=service_id,
            name=name,
            capabilities=capabilities,
            metadata=tool_metadata
        )

def extract_text_from_mcp_result(result: Dict[str, Any]) -> Optional[str]:
    """
    Extract text content from an MCP processing result.
    
    Args:
        result: MCP processing result
        
    Returns:
        Extracted text, or None if no text is found
    """
    if not result:
        return None
        
    # Check for error
    if "error" in result:
        logger.error(f"Error in MCP result: {result['error']}")
        return None
        
    # Try to find text content
    content = result.get("result", {}).get("content", {})
    
    if "text" in content:
        return content["text"]
    elif isinstance(content, str):
        return content
    elif isinstance(result.get("result"), str):
        return result["result"]
    else:
        logger.warning(f"Could not extract text from MCP result: {result}")
        return None

def extract_data_from_mcp_result(result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract structured data from an MCP processing result.
    
    Args:
        result: MCP processing result
        
    Returns:
        Extracted data, or None if no data is found
    """
    if not result:
        return None
        
    # Check for error
    if "error" in result:
        logger.error(f"Error in MCP result: {result['error']}")
        return None
        
    # Try to find structured data
    content = result.get("result", {}).get("content", {})
    
    if "data" in content:
        return content["data"]
    elif isinstance(content, dict):
        return content
    elif isinstance(result.get("result"), dict):
        return result["result"]
    else:
        logger.warning(f"Could not extract data from MCP result: {result}")
        return None