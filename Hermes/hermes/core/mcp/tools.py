"""
MCP Tools - Tool definitions for Hermes MCP service.

This module provides tool definitions for the Hermes MCP service,
using the FastMCP decorator-based approach.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

# Import FastMCP decorators if available
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        MCPClient
    )
    fastmcp_available = True
except ImportError:
    # Define dummy decorators for backward compatibility
    def mcp_tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
        
    def mcp_capability(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
            
    fastmcp_available = False

logger = logging.getLogger(__name__)

# System Tools

@mcp_capability(
    name="system",
    description="Capability for system operations",
    modality="system"
)
@mcp_tool(
    name="GetComponentStatus",
    description="Get the status of a Tekton component",
    tags=["system", "status"],
    category="system"
)
async def get_component_status(
    component_id: str,
    service_registry: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get the status of a Tekton component.
    
    Args:
        component_id: ID of the component to get status for
        service_registry: Service registry to use (injected)
        
    Returns:
        Component status information
    """
    if not service_registry:
        return {
            "error": "Service registry not provided"
        }
        
    # Get component status
    component = service_registry.get_service(component_id)
    if not component:
        return {
            "error": f"Component not found: {component_id}"
        }
        
    # Get health data
    health_data = {"healthy": component_id in service_registry.health, 
                  "status": "online" if service_registry.health.get(component_id) else "offline"}
    
    return {
        "component_id": component_id,
        "name": component.get("name", "Unknown"),
        "status": "online" if health_data.get("healthy", False) else "offline",
        "last_seen": health_data.get("last_seen"),
        "endpoint": component.get("endpoint"),
        "version": component.get("version"),
        "capabilities": component.get("capabilities", []),
        "health": health_data
    }

@mcp_capability(
    name="system",
    description="Capability for system operations",
    modality="system"
)
@mcp_tool(
    name="ListComponents",
    description="List all Tekton components",
    tags=["system", "components"],
    category="system"
)
async def list_components(
    filter_type: Optional[str] = None,
    service_registry: Optional[Any] = None
) -> Dict[str, Any]:
    """
    List all Tekton components.
    
    Args:
        filter_type: Optional component type to filter by
        service_registry: Service registry to use (injected)
        
    Returns:
        List of components
    """
    if not service_registry:
        return {
            "error": "Service registry not provided"
        }
        
    # Get all components
    components = service_registry.get_all_services()
    
    # Filter by type if specified
    if filter_type:
        components = {
            component_id: component 
            for component_id, component in components.items()
            if component.get("metadata", {}).get("component_type") == filter_type
        }
        
    # Get health data for each component
    result = []
    for component_id, component in components.items():
        health_data = {"healthy": component_id in service_registry.health, 
                      "status": "online" if service_registry.health.get(component_id) else "offline"}
        result.append({
            "component_id": component_id,
            "name": component.get("name", "Unknown"),
            "status": "online" if health_data.get("healthy", False) else "offline",
            "type": component.get("component_type", "unknown"),
            "version": component.get("version"),
            "capabilities": component.get("capabilities", [])
        })
        
    return {
        "components": result,
        "count": len(result)
    }

# Database Tools

@mcp_capability(
    name="database",
    description="Capability for database operations",
    modality="data"
)
@mcp_tool(
    name="QueryVectorDatabase",
    description="Query the vector database",
    tags=["database", "vector", "search"],
    category="database"
)
async def query_vector_database(
    text: str,
    collection: Optional[str] = None,
    limit: int = 5,
    database_manager: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Query the vector database.
    
    Args:
        text: Text to search for
        collection: Optional collection to search in
        limit: Maximum number of results
        database_manager: Database manager to use (injected)
        
    Returns:
        Search results
    """
    if not database_manager:
        return {
            "error": "Database manager not provided"
        }
        
    try:
        # Get vector adapter
        vector_adapter = await database_manager.get_adapter("vector")
        if not vector_adapter:
            return {
                "error": "Vector database not available"
            }
            
        # Search for similar vectors
        results = await vector_adapter.search(
            text=text,
            collection=collection,
            limit=limit
        )
        
        return {
            "query": text,
            "collection": collection,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error querying vector database: {e}")
        return {
            "error": f"Error querying vector database: {e}"
        }

@mcp_capability(
    name="database",
    description="Capability for database operations",
    modality="data"
)
@mcp_tool(
    name="StoreVectorData",
    description="Store data in the vector database",
    tags=["database", "vector", "store"],
    category="database"
)
async def store_vector_data(
    text: str,
    metadata: Dict[str, Any],
    collection: Optional[str] = None,
    database_manager: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Store data in the vector database.
    
    Args:
        text: Text to store
        metadata: Metadata to store with the text
        collection: Optional collection to store in
        database_manager: Database manager to use (injected)
        
    Returns:
        Storage result
    """
    if not database_manager:
        return {
            "error": "Database manager not provided"
        }
        
    try:
        # Get vector adapter
        vector_adapter = await database_manager.get_adapter("vector")
        if not vector_adapter:
            return {
                "error": "Vector database not available"
            }
            
        # Store vector data
        doc_id = await vector_adapter.add(
            text=text,
            metadata=metadata,
            collection=collection
        )
        
        return {
            "success": True,
            "doc_id": doc_id,
            "collection": collection
        }
    except Exception as e:
        logger.error(f"Error storing vector data: {e}")
        return {
            "error": f"Error storing vector data: {e}"
        }

# Messaging Tools

@mcp_capability(
    name="messaging",
    description="Capability for messaging operations",
    modality="communication"
)
@mcp_tool(
    name="PublishMessage",
    description="Publish a message to a channel",
    tags=["messaging", "publish"],
    category="messaging"
)
async def publish_message(
    channel: str,
    message: Dict[str, Any],
    message_bus: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Publish a message to a channel.
    
    Args:
        channel: Channel to publish to
        message: Message to publish
        message_bus: Message bus to use (injected)
        
    Returns:
        Publish result
    """
    if not message_bus:
        return {
            "error": "Message bus not provided"
        }
        
    try:
        # Publish message
        await message_bus.publish(channel, message)
        
        return {
            "success": True,
            "channel": channel,
            "message_type": message.get("type", "unknown")
        }
    except Exception as e:
        logger.error(f"Error publishing message: {e}")
        return {
            "error": f"Error publishing message: {e}"
        }

@mcp_capability(
    name="messaging",
    description="Capability for messaging operations",
    modality="communication"
)
@mcp_tool(
    name="CreateChannel",
    description="Create a new message channel",
    tags=["messaging", "channel"],
    category="messaging"
)
async def create_channel(
    channel: str,
    description: str,
    message_bus: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Create a new message channel.
    
    Args:
        channel: Channel name
        description: Channel description
        message_bus: Message bus to use (injected)
        
    Returns:
        Creation result
    """
    if not message_bus:
        return {
            "error": "Message bus not provided"
        }
        
    try:
        # Create channel
        await message_bus.create_channel(channel, description=description)
        
        return {
            "success": True,
            "channel": channel,
            "description": description
        }
    except Exception as e:
        logger.error(f"Error creating channel: {e}")
        return {
            "error": f"Error creating channel: {e}"
        }

# Registration functions

async def register_system_tools(service_registry, tool_registry):
    """Register system tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, using legacy tool registration")
        return
        
    # Register tools with tool registry
    tool1_dict = get_component_status._mcp_tool_meta.to_dict()
    tool1_dict['function'] = get_component_status
    tool1_id = await tool_registry.register_tool(tool1_dict)
    
    tool2_dict = list_components._mcp_tool_meta.to_dict()
    tool2_dict['function'] = list_components
    tool2_id = await tool_registry.register_tool(tool2_dict)
    
    # Register local handlers if tool_registry has a tool_executor
    if hasattr(tool_registry, 'tool_executor'):
        tool_registry.tool_executor.register_local_handler(tool1_id, get_component_status)
        tool_registry.tool_executor.register_local_handler(tool2_id, list_components)
    
    logger.info("Registered system tools with MCP service")

async def register_database_tools(database_manager, tool_registry):
    """Register database tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, using legacy tool registration")
        return
        
    # Register tools with tool registry
    tool1_dict = query_vector_database._mcp_tool_meta.to_dict()
    tool1_dict['function'] = query_vector_database
    tool1_id = await tool_registry.register_tool(tool1_dict)
    
    tool2_dict = store_vector_data._mcp_tool_meta.to_dict()
    tool2_dict['function'] = store_vector_data
    tool2_id = await tool_registry.register_tool(tool2_dict)
    
    # Register local handlers if tool_registry has a tool_executor
    if hasattr(tool_registry, 'tool_executor'):
        tool_registry.tool_executor.register_local_handler(tool1_id, query_vector_database)
        tool_registry.tool_executor.register_local_handler(tool2_id, store_vector_data)
    
    logger.info("Registered database tools with MCP service")

async def register_messaging_tools(message_bus, tool_registry):
    """Register messaging tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, using legacy tool registration")
        return
        
    # Register tools with tool registry
    tool1_dict = publish_message._mcp_tool_meta.to_dict()
    tool1_dict['function'] = publish_message
    tool1_id = await tool_registry.register_tool(tool1_dict)
    
    tool2_dict = create_channel._mcp_tool_meta.to_dict()
    tool2_dict['function'] = create_channel
    tool2_id = await tool_registry.register_tool(tool2_dict)
    
    # Register local handlers if tool_registry has a tool_executor
    if hasattr(tool_registry, 'tool_executor'):
        tool_registry.tool_executor.register_local_handler(tool1_id, publish_message)
        tool_registry.tool_executor.register_local_handler(tool2_id, create_channel)
    
    logger.info("Registered messaging tools with MCP service")


# Getter functions for hermes_self_bridge

def get_system_tools(service_registry: Any) -> List[Dict[str, Any]]:
    """Get system tools for internal use."""
    tools = []
    
    # Create wrapper functions that include the service_registry
    async def _get_component_status(**kwargs):
        return await get_component_status(service_registry=service_registry, **kwargs)
    
    async def _list_components(**kwargs):
        return await list_components(service_registry=service_registry, **kwargs)
    
    # Copy metadata from original functions
    _get_component_status._mcp_tool_meta = get_component_status._mcp_tool_meta
    _list_components._mcp_tool_meta = list_components._mcp_tool_meta
    
    tools.append(_get_component_status)
    tools.append(_list_components)
    
    return tools


def get_database_tools(database_manager: Any) -> List[Dict[str, Any]]:
    """Get database tools for internal use."""
    tools = []
    
    # Create wrapper functions that include the database_manager
    async def _query_vector_database(**kwargs):
        return await query_vector_database(database_manager=database_manager, **kwargs)
    
    async def _store_vector_data(**kwargs):
        return await store_vector_data(database_manager=database_manager, **kwargs)
    
    # Copy metadata from original functions
    _query_vector_database._mcp_tool_meta = query_vector_database._mcp_tool_meta
    _store_vector_data._mcp_tool_meta = store_vector_data._mcp_tool_meta
    
    tools.append(_query_vector_database)
    tools.append(_store_vector_data)
    
    return tools


def get_messaging_tools(message_bus: Any) -> List[Dict[str, Any]]:
    """Get messaging tools for internal use."""
    tools = []
    
    # Create wrapper functions that include the message_bus
    async def _publish_message(**kwargs):
        return await publish_message(message_bus=message_bus, **kwargs)
    
    async def _create_channel(**kwargs):
        return await create_channel(message_bus=message_bus, **kwargs)
    
    # Copy metadata from original functions
    _publish_message._mcp_tool_meta = publish_message._mcp_tool_meta
    _create_channel._mcp_tool_meta = create_channel._mcp_tool_meta
    
    tools.append(_publish_message)
    tools.append(_create_channel)
    
    return tools