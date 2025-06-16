"""
MCP Adapters - Adapters for integrating existing MCP implementations.

This module provides adapters to integrate existing MCP implementations
with the new decorator-based approach, allowing for a smooth transition.
"""

import logging
import inspect
from typing import Any, Dict, List, Optional, Type, Union

# Import FastMCP adapters if available
try:
    from tekton.mcp.fastmcp import (
        adapt_tool,
        adapt_processor,
        adapt_context,
        mcp_processor
    )
    fastmcp_available = True
except ImportError:
    fastmcp_available = False

logger = logging.getLogger(__name__)

async def adapt_legacy_service(mcp_service):
    """
    Adapt the legacy MCP service to the new FastMCP approach.
    
    This function adapts the legacy MCP service to the new FastMCP approach,
    creating FastMCP tools and processors from the existing implementations.
    
    Args:
        mcp_service: Legacy MCP service to adapt
        
    Returns:
        Adapted tools and processors
    """
    if not fastmcp_available:
        logger.warning("FastMCP not available, cannot adapt legacy service")
        return None
        
    logger.info("Adapting legacy MCP service to FastMCP")
    
    adapted_tools = []
    adapted_processors = []
    
    # Adapt tools
    for tool_id, tool_spec in mcp_service.tools.items():
        try:
            adapted_tool = adapt_tool(tool_spec)
            adapted_tools.append(adapted_tool)
            logger.info(f"Adapted tool: {tool_spec.get('name', 'unknown')} ({tool_id})")
        except Exception as e:
            logger.error(f"Error adapting tool {tool_id}: {e}")
            
    # Adapt processors
    for processor_id, processor_spec in mcp_service.processors.items():
        try:
            AdaptedProcessor = adapt_processor(processor_spec)
            adapted_processors.append(AdaptedProcessor)
            logger.info(f"Adapted processor: {processor_spec.get('name', 'unknown')} ({processor_id})")
        except Exception as e:
            logger.error(f"Error adapting processor {processor_id}: {e}")
            
    logger.info(f"Adapted {len(adapted_tools)} tools and {len(adapted_processors)} processors")
    
    return {
        "tools": adapted_tools,
        "processors": adapted_processors
    }

@mcp_processor(
    name="LegacyMCPProcessor",
    description="Adapter for legacy MCP processor",
    capabilities=["mcp_processing", "text", "code", "image", "structured"]
)
class LegacyMCPProcessorAdapter:
    """
    Adapter for legacy MCP processor.
    
    This class adapts a legacy MCP processor to the new FastMCP approach,
    allowing it to be used with the new decorator-based approach.
    """
    
    def __init__(self, legacy_processor):
        """
        Initialize the adapter.
        
        Args:
            legacy_processor: Legacy processor to adapt
        """
        self.legacy_processor = legacy_processor
        self.name = getattr(legacy_processor, "name", "LegacyProcessor")
        self.capabilities = getattr(legacy_processor, "capabilities", [])
        
    async def process(self, message):
        """
        Process a message.
        
        Args:
            message: Message to process
            
        Returns:
            Processing result
        """
        if hasattr(self.legacy_processor, "process") and callable(self.legacy_processor.process):
            return await self.legacy_processor.process(message)
        else:
            logger.warning(f"Legacy processor {self.name} has no process method")
            return {
                "error": f"Legacy processor {self.name} has no process method"
            }