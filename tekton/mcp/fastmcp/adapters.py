"""
FastMCP Adapters - Adapters for integrating existing MCP implementations.

This module provides adapters to integrate existing MCP implementations
with the new decorator-based approach, allowing for a smooth transition.
"""

import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Type, Union

from tekton.mcp.message import MCPMessage, MCPResponse, MCPContentItem
from tekton.mcp.tool_registry import ToolRegistry
from tekton.mcp.fastmcp.decorators import MCPToolMeta, mcp_tool, mcp_processor

logger = logging.getLogger(__name__)

def adapt_tool(tool_func_or_spec: Union[Callable, Dict[str, Any]], component_manager: Optional[Any] = None) -> Callable:
    """
    Adapt an existing tool specification or function to the decorator pattern.

    This function creates a decorated function from either:
    1. An existing tool specification dictionary (legacy)
    2. A function with MCP metadata (new pattern)

    Args:
        tool_func_or_spec: Either a function with MCP metadata or existing tool specification
        component_manager: Optional component manager for dependency injection

    Returns:
        Decorated function
    """
    # Handle both function and tool_spec inputs
    if callable(tool_func_or_spec):
        # New pattern: function with MCP metadata
        function = tool_func_or_spec

        # Check if function has MCP metadata
        if hasattr(function, "_mcp_tool_meta"):
            # Function already decorated, just inject component manager if needed
            if component_manager and hasattr(function, '__self__') is False:
                # Create a wrapper that preserves metadata and injects component_manager
                import functools

                @functools.wraps(function)
                async def wrapped_function(*args, **kwargs):
                    # Inject component_manager if the function expects it
                    import inspect
                    sig = inspect.signature(function)
                    if 'component_manager' in sig.parameters:
                        kwargs['component_manager'] = component_manager
                    return await function(*args, **kwargs) if inspect.iscoroutinefunction(function) else function(*args, **kwargs)

                # Preserve the MCP metadata
                wrapped_function._mcp_tool_meta = function._mcp_tool_meta
                return wrapped_function
            return function
        else:
            # Function lacks metadata, can't adapt
            logger.error(f"Function {function.__name__} missing MCP metadata, cannot adapt")
            raise ValueError(f"Function {function.__name__} missing MCP metadata")

    else:
        # Legacy pattern: tool specification dictionary
        tool_spec = tool_func_or_spec
        tool_id = tool_spec.get("id")
        name = tool_spec.get("name", "Unnamed Tool")
        description = tool_spec.get("description", "")
        schema = tool_spec.get("schema", {})
        tags = tool_spec.get("tags", [])
        metadata = tool_spec.get("metadata", {})
        function = tool_spec.get("function")

        # Check if function is provided
        if not function:
            logger.warning(f"Tool {name} does not have a function")

            # Create a dummy function
            async def dummy_function(**kwargs):
                logger.warning(f"Dummy function called for tool {name}")
                return {
                    "error": "This is a dummy function for an adapted tool"
                }

            function = dummy_function

        # Create decorated function for legacy pattern
        @mcp_tool(
            name=name,
            description=description,
            tags=tags,
            metadata=metadata
        )
        async def adapted_tool(**kwargs):
            # Call original function
            return await function(**kwargs) if inspect.iscoroutinefunction(function) else function(**kwargs)

        # Manually set ID to maintain identity
        if tool_id:
            adapted_tool._mcp_tool_meta.id = tool_id

        # Copy schema
        adapted_tool._mcp_tool_meta.schema = schema

        return adapted_tool

def adapt_processor(processor_spec: Dict[str, Any]) -> Type:
    """
    Adapt an existing processor specification to the decorator pattern.
    
    This function creates a decorated class from an existing processor
    specification, enabling backward compatibility.
    
    Args:
        processor_spec: Existing processor specification
        
    Returns:
        Decorated class
    """
    # Extract processor metadata
    processor_id = processor_spec.get("id")
    name = processor_spec.get("name", "Unnamed Processor")
    description = processor_spec.get("description", "")
    capabilities = processor_spec.get("capabilities", [])
    endpoint = processor_spec.get("endpoint")
    metadata = processor_spec.get("metadata", {})
    
    # Create processor class
    @mcp_processor(
        name=name,
        description=description,
        capabilities=capabilities,
        endpoint=endpoint,
        metadata=metadata
    )
    class AdaptedProcessor:
        """
        Adapted processor class.
        
        This class adapts an existing processor specification to the new
        decorator-based pattern.
        """
        
        def __init__(self):
            """Initialize adapted processor."""
            self.original_spec = processor_spec
            
        async def process(self, message: Union[Dict[str, Any], MCPMessage]) -> Union[Dict[str, Any], MCPResponse]:
            """
            Process a message.
            
            Args:
                message: Message to process
                
            Returns:
                Processing result
            """
            logger.warning(f"Adapted processor {name} called with no implementation")
            
            # Create a dummy response
            if isinstance(message, dict):
                # Create a response from dictionary
                return {
                    "id": f"response-{message.get('id', 'unknown')}",
                    "in_response_to": message.get("id", "unknown"),
                    "content": [
                        {
                            "type": "text",
                            "data": f"Adapted processor {name} has no implementation",
                            "metadata": {"role": "system"}
                        }
                    ]
                }
            else:
                # Create a response from MCPMessage
                return message.create_response([
                    MCPContentItem(
                        content_type="text",
                        data=f"Adapted processor {name} has no implementation",
                        metadata={"role": "system"}
                    )
                ])
                
    # Manually set ID to maintain identity
    if processor_id:
        AdaptedProcessor._mcp_processor_meta["id"] = processor_id
        
    return AdaptedProcessor

def adapt_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapt an existing context to the new format.
    
    This function adapts an existing context to the new format
    used by the decorator-based approach.
    
    Args:
        context: Existing context
        
    Returns:
        Adapted context
    """
    # Extract context metadata
    context_id = context.get("id")
    data = context.get("data", {})
    source = context.get("source", {})
    
    # Create adapted context
    adapted_context = {
        "id": context_id,
        "data": data,
        "source": source,
        "metadata": {
            "adapted": True,
            "original_format": "mcp/legacy"
        }
    }
    
    return adapted_context

def adapt_legacy_registry(registry: ToolRegistry) -> List[Callable]:
    """
    Adapt a legacy tool registry to the new format.
    
    This function adapts tools from a legacy tool registry to the new
    decorator-based approach.
    
    Args:
        registry: Legacy tool registry
        
    Returns:
        List of adapted tool functions
    """
    adapted_tools = []
    
    # Get all tools from registry
    for tool_id, tool_spec in registry.tools.items():
        try:
            # Adapt tool
            adapted_tool = adapt_tool(tool_spec)
            adapted_tools.append(adapted_tool)
        except Exception as e:
            logger.error(f"Error adapting tool {tool_id}: {e}")
            
    return adapted_tools