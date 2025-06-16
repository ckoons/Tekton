"""
Base Modality Processor - Base class for content modality processors.

This module defines the base class for modality processors,
which handle different types of content in the MCP protocol.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Type, Callable

from tekton.mcp.message import MCPContentItem

logger = logging.getLogger(__name__)

class ModalityProcessor:
    """
    Base class for modality processors.
    
    This class defines the interface for modality processors,
    which handle different types of content in the MCP protocol.
    """
    
    def __init__(self):
        """Initialize the modality processor."""
        pass
    
    async def process(
        self,
        content_item: MCPContentItem,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a content item.
        
        Args:
            content_item: Content item to process
            context: Processing context
            
        Returns:
            Processing result
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def validate(self, content_item: MCPContentItem) -> bool:
        """
        Validate a content item.
        
        Args:
            content_item: Content item to validate
            
        Returns:
            True if valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_supported_formats(self) -> List[str]:
        """
        Get the formats supported by this processor.
        
        Returns:
            List of supported format strings
        """
        raise NotImplementedError("Subclasses must implement this method")