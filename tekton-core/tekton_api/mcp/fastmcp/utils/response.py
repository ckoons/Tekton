"""
MCP Response Utilities for Tekton Components.

This module provides common utilities for creating and standardizing
MCP responses across Tekton components.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union

from tekton.mcp.fastmcp.schema import MCPResponse

logger = logging.getLogger(__name__)

def create_mcp_response(
    result: Any = None,
    status: str = "success",
    error: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> MCPResponse:
    """
    Create a standardized MCP response.
    
    Args:
        result: Response result data
        status: Response status ('success' or 'error')
        error: Optional error message
        metadata: Optional response metadata
        
    Returns:
        Standardized MCPResponse
    """
    # Standard metadata added to all responses
    standard_metadata = {
        "timestamp": time.time(),
    }
    
    # Merge with provided metadata
    if metadata:
        standard_metadata.update(metadata)
    
    # Create response
    response = MCPResponse(
        status=status,
        error=error,
        result=result
    )
    
    return response