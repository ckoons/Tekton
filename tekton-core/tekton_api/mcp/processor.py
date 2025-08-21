"""
Message Processor - Core processing pipeline for MCP messages.

This module provides the processing pipeline for MCP messages,
coordinating content extraction, modality processing, and response generation.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Type, Callable

from tekton.mcp.message import (
    MCPMessage, 
    MCPResponse, 
    MCPContentItem, 
    MCPContentType,
    validate_message
)
from tekton.mcp.context import (
    ContextManager, 
    get_context_manager,
    create_context,
    enhance_context
)
from tekton.mcp.modality import (
    ModalityProcessor,
    TextProcessor,
    CodeProcessor,
    ImageProcessor,
    StructuredDataProcessor
)

logger = logging.getLogger(__name__)

class MessageProcessor:
    """
    Processor for MCP messages.
    
    This class provides a processing pipeline for MCP messages,
    coordinating extraction, modality processing, and response generation.
    """
    
    def __init__(self, context_manager: Optional[ContextManager] = None):
        """
        Initialize the message processor.
        
        Args:
            context_manager: Context manager to use (uses global one if None)
        """
        self.context_manager = context_manager
        
        # Initialize modality processors
        self.modality_processors = {
            "text": TextProcessor(),
            "code": CodeProcessor(),
            "image": ImageProcessor(),
            "structured": StructuredDataProcessor()
        }
        
        logger.info("Message processor initialized")
    
    async def _get_context_manager(self) -> ContextManager:
        """
        Get the context manager, initializing if needed.
        
        Returns:
            Context manager
        """
        if self.context_manager:
            return self.context_manager
        return get_context_manager()
    
    async def process_message(self, message: Union[MCPMessage, Dict[str, Any]]) -> MCPResponse:
        """
        Process an MCP message.
        
        Args:
            message: MCP message to process
            
        Returns:
            Processed response
        """
        # Convert dictionary to MCPMessage if needed
        if isinstance(message, dict):
            try:
                msg = MCPMessage.from_dict(message)
            except Exception as e:
                logger.error(f"Failed to parse message: {e}")
                return self._create_error_response(
                    message_id=message.get("id", "unknown"),
                    error_message=f"Failed to parse message: {e}"
                )
        else:
            msg = message
            
        try:
            # Validate message
            if not validate_message(msg.to_dict()):
                return self._create_error_response(
                    message_id=msg.id,
                    error_message="Invalid MCP message format"
                )
            
            # Extract message context
            context_manager = await self._get_context_manager()
            
            # Create context for this message if not already in context
            context_id = msg.context.get("context_id")
            
            if not context_id or not await context_manager.get_context(context_id):
                # Create new context from message context
                context_id = await context_manager.create_context(
                    data=msg.context,
                    source=msg.source,
                    category="message",
                    metadata={"message_id": msg.id}
                )
                
                # Add context_id to message context
                msg.context["context_id"] = context_id
            
            # Process content items
            processed_items = []
            for item in msg.content:
                try:
                    processed_item = await self._process_content_item(
                        item, 
                        msg.context
                    )
                    processed_items.append(processed_item)
                except Exception as e:
                    logger.error(f"Error processing content item: {e}")
                    # Continue with other items
            
            # Generate response
            response_content = await self._generate_response(
                processed_items,
                msg.context,
                msg.processing.get("response_format", ["text"])
            )
            
            # Create response
            response = msg.create_response(response_content)
            
            # Add tracking information
            response.context["processed_by"] = "tekton.mcp.processor"
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._create_error_response(
                message_id=msg.id,
                error_message=f"Error processing message: {e}"
            )
    
    async def _process_content_item(
        self,
        content_item: MCPContentItem,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a single content item.
        
        Args:
            content_item: Content item to process
            context: Message context
            
        Returns:
            Processed content result
        """
        content_type = content_item.type
        
        # Check if we have a processor for this content type
        if content_type not in self.modality_processors:
            logger.warning(f"No processor found for content type: {content_type}")
            return {
                "original": content_item.to_dict(),
                "processed": False,
                "error": f"No processor for content type: {content_type}"
            }
            
        # Get processor
        processor = self.modality_processors[content_type]
        
        # Process content
        result = await processor.process(content_item, context)
        
        # Return processed result
        return {
            "original": content_item.to_dict(),
            "processed": True,
            "result": result
        }
    
    async def _generate_response(
        self,
        processed_items: List[Dict[str, Any]],
        context: Dict[str, Any],
        response_format: List[str]
    ) -> List[MCPContentItem]:
        """
        Generate a response from processed content items.
        
        Args:
            processed_items: List of processed content items
            context: Message context
            response_format: Requested response formats
            
        Returns:
            List of response content items
        """
        # Default to text response if no items were processed successfully
        if not any(item.get("processed", False) for item in processed_items):
            return [
                MCPContentItem(
                    content_type="text",
                    data="Failed to process message content",
                    format="text/plain",
                    metadata={"role": "error"}
                )
            ]
            
        # Use a text processor to generate a response for now
        # In a more sophisticated implementation, this would use
        # different processors based on the requested formats
        
        if "text" in response_format:
            # Create a simple text response
            return [
                MCPContentItem(
                    content_type="text",
                    data="Message received and processed successfully",
                    format="text/plain",
                    metadata={"role": "assistant"}
                )
            ]
        else:
            # Return the processed results as structured data
            return [
                MCPContentItem(
                    content_type="structured",
                    data={"processed_items": processed_items},
                    format="application/json",
                    metadata={"role": "result"}
                )
            ]
    
    def _create_error_response(
        self,
        message_id: str,
        error_message: str
    ) -> MCPResponse:
        """
        Create an error response.
        
        Args:
            message_id: Original message ID
            error_message: Error message
            
        Returns:
            Error response
        """
        return MCPResponse(
            content=[
                MCPContentItem(
                    content_type="text",
                    data=error_message,
                    format="text/plain",
                    metadata={"role": "error"}
                )
            ],
            source={"component": "mcp.processor"},
            destination={},
            context={"error": True},
            in_response_to=message_id
        )
    
    async def extract_content(
        self,
        message: Union[MCPMessage, Dict[str, Any]],
        content_type: Optional[Union[MCPContentType, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract content items from an MCP message.
        
        Args:
            message: MCP message to extract content from
            content_type: Optional type to filter by
            
        Returns:
            List of extracted content items
        """
        # Convert dictionary to MCPMessage if needed
        if isinstance(message, dict):
            try:
                msg = MCPMessage.from_dict(message)
            except Exception as e:
                logger.error(f"Failed to parse message: {e}")
                return []
        else:
            msg = message
            
        # Extract content items of the specified type or all if None
        if content_type:
            type_str = content_type if isinstance(content_type, str) else content_type.value
            items = msg.get_content_by_type(type_str)
        else:
            items = msg.content
            
        # Convert to dictionaries
        return [item.to_dict() for item in items]


# Global message processor instance for convenience functions
_global_processor: Optional[MessageProcessor] = None

def get_processor() -> MessageProcessor:
    """
    Get the global message processor, creating it if needed.
    
    Returns:
        Global MessageProcessor instance
    """
    global _global_processor
    if _global_processor is None:
        _global_processor = MessageProcessor()
    return _global_processor

async def process_message(message: Union[MCPMessage, Dict[str, Any]]) -> MCPResponse:
    """
    Process an MCP message using the global processor.
    
    Args:
        message: MCP message to process
        
    Returns:
        Processed response
    """
    processor = get_processor()
    return await processor.process_message(message)

async def extract_content(
    message: Union[MCPMessage, Dict[str, Any]],
    content_type: Optional[Union[MCPContentType, str]] = None
) -> List[Dict[str, Any]]:
    """
    Extract content items from an MCP message using the global processor.
    
    Args:
        message: MCP message to extract content from
        content_type: Optional type to filter by
        
    Returns:
        List of extracted content items
    """
    processor = get_processor()
    return await processor.extract_content(message, content_type)