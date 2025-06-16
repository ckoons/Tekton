"""
MCP Tools - Tool definitions for Engram MCP service.

This module provides tool definitions for the Engram MCP service,
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.mcp_tools")

# --- Memory Operations ---

@mcp_capability(
    name="memory_operations",
    description="Capability for core memory operations",
    modality="memory"
)
@mcp_tool(
    name="MemoryStore",
    description="Store information in Engram's memory system",
    tags=["memory", "store"],
    category="memory_operations"
)
async def memory_store(
    content: str,
    namespace: str = "conversations",
    metadata: Optional[Dict[str, Any]] = None,
    memory_service: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Store information in Engram's memory system.
    
    Args:
        content: Content to store in memory
        namespace: Namespace to store memory in (default: conversations)
        metadata: Additional metadata for the memory
        memory_service: Memory service to use (injected)
        
    Returns:
        Result of memory storage operation
    """
    # Use the new compatibility layer if available
    try:
        from engram.api.mcp_compat import memory_store as compat_store
        params = {
            "text": content,
            "namespace": namespace,
            "metadata": metadata or {}
        }
        return await compat_store(params)
    except ImportError:
        # Fallback to direct memory service
        if not memory_service:
            return {
                "error": "Memory service not provided"
            }
            
        try:
            # Store the memory
            success = await memory_service.add(
                content=content,
                namespace=namespace,
                metadata=metadata
            )
            
            # Return result
            return {
                "success": success,
                "namespace": namespace
            }
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return {
                "error": f"Error storing memory: {str(e)}",
                "success": False
            }

@mcp_capability(
    name="memory_operations",
    description="Capability for core memory operations",
    modality="memory"
)
@mcp_tool(
    name="MemoryQuery",
    description="Query Engram's memory system for relevant information",
    tags=["memory", "query", "search"],
    category="memory_operations"
)
async def memory_query(
    query: str,
    namespace: str = "conversations",
    limit: int = 5,
    memory_service: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Query Engram's memory system for relevant information.
    
    Args:
        query: Query text to search for
        namespace: Namespace to search in (default: conversations)
        limit: Maximum number of results to return
        memory_service: Memory service to use (injected)
        
    Returns:
        Search results
    """
    if not memory_service:
        return {
            "error": "Memory service not provided"
        }
        
    try:
        # Query memory
        results = await memory_service.search(
            query=query,
            namespace=namespace,
            limit=limit
        )
        
        # Return results
        return results
    except Exception as e:
        logger.error(f"Error querying memory: {e}")
        return {
            "error": f"Error querying memory: {str(e)}",
            "success": False,
            "results": []
        }

@mcp_capability(
    name="memory_operations",
    description="Capability for core memory operations",
    modality="memory"
)
@mcp_tool(
    name="GetContext",
    description="Get formatted memory context across multiple namespaces",
    tags=["memory", "context"],
    category="memory_operations"
)
async def get_context(
    query: str,
    namespaces: List[str] = ["conversations", "thinking", "longterm"],
    limit: int = 3,
    memory_service: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get formatted memory context across multiple namespaces.
    
    Args:
        query: Query to use for context retrieval
        namespaces: Namespaces to include
        limit: Results per namespace
        memory_service: Memory service to use (injected)
        
    Returns:
        Formatted context from memory
    """
    if not memory_service:
        return {
            "error": "Memory service not provided"
        }
        
    try:
        # Get context
        context = await memory_service.get_relevant_context(
            query=query,
            namespaces=namespaces,
            limit=limit
        )
        
        # Return context
        return {"context": context}
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        return {
            "error": f"Error getting context: {str(e)}",
            "success": False,
            "context": ""
        }

# --- Structured Memory Operations ---

@mcp_capability(
    name="structured_memory",
    description="Capability for structured memory operations",
    modality="memory"
)
@mcp_tool(
    name="StructuredMemoryAdd",
    description="Add a memory to the structured memory system",
    tags=["memory", "structured", "add"],
    category="structured_memory"
)
async def structured_memory_add(
    content: str,
    category: str = "session",
    importance: Optional[int] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    structured_memory: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Add a memory to the structured memory system.
    
    Args:
        content: Content to store
        category: Category for the memory (default: session)
        importance: Importance level (1-5)
        tags: Tags for the memory
        metadata: Additional metadata
        structured_memory: Structured memory service to use (injected)
        
    Returns:
        Result with memory ID
    """
    if not structured_memory:
        return {
            "error": "Structured memory service not provided"
        }
        
    try:
        # Add memory
        memory_id = await structured_memory.add_memory(
            content=content,
            category=category,
            importance=importance,
            tags=tags,
            metadata=metadata
        )
        
        # Return result
        return {
            "success": bool(memory_id),
            "memory_id": memory_id
        }
    except Exception as e:
        logger.error(f"Error adding structured memory: {e}")
        return {
            "error": f"Error adding structured memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="structured_memory",
    description="Capability for structured memory operations",
    modality="memory"
)
@mcp_tool(
    name="StructuredMemoryGet",
    description="Get a memory from the structured memory system by ID",
    tags=["memory", "structured", "get"],
    category="structured_memory"
)
async def structured_memory_get(
    memory_id: str,
    structured_memory: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get a memory from the structured memory system by ID.
    
    Args:
        memory_id: ID of the memory to retrieve
        structured_memory: Structured memory service to use (injected)
        
    Returns:
        Memory content and metadata
    """
    if not structured_memory:
        return {
            "error": "Structured memory service not provided"
        }
        
    try:
        # Get memory
        memory = await structured_memory.get_memory(memory_id)
        
        if not memory:
            return {
                "error": f"Memory with ID {memory_id} not found",
                "success": False
            }
        
        # Return memory
        return {
            "success": True,
            "memory": memory
        }
    except Exception as e:
        logger.error(f"Error retrieving structured memory: {e}")
        return {
            "error": f"Error retrieving structured memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="structured_memory",
    description="Capability for structured memory operations",
    modality="memory"
)
@mcp_tool(
    name="StructuredMemoryUpdate",
    description="Update a memory in the structured memory system",
    tags=["memory", "structured", "update"],
    category="structured_memory"
)
async def structured_memory_update(
    memory_id: str,
    content: Optional[str] = None,
    category: Optional[str] = None,
    importance: Optional[int] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    structured_memory: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Update a memory in the structured memory system.
    
    Args:
        memory_id: ID of the memory to update
        content: New content (optional)
        category: New category (optional)
        importance: New importance level (optional)
        tags: New tags (optional)
        metadata: New metadata (optional)
        structured_memory: Structured memory service to use (injected)
        
    Returns:
        Result of the update operation
    """
    if not structured_memory:
        return {
            "error": "Structured memory service not provided"
        }
        
    try:
        # Create update data
        update_data = {}
        if content is not None:
            update_data["content"] = content
        if category is not None:
            update_data["category"] = category
        if importance is not None:
            update_data["importance"] = importance
        if tags is not None:
            update_data["tags"] = tags
        if metadata is not None:
            update_data["metadata"] = metadata
            
        # No fields to update
        if not update_data:
            return {
                "error": "No update fields provided",
                "success": False
            }
        
        # Update memory
        success = await structured_memory.update_memory(
            memory_id=memory_id,
            **update_data
        )
        
        # Return result
        return {
            "success": success,
            "memory_id": memory_id
        }
    except Exception as e:
        logger.error(f"Error updating structured memory: {e}")
        return {
            "error": f"Error updating structured memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="structured_memory",
    description="Capability for structured memory operations",
    modality="memory"
)
@mcp_tool(
    name="StructuredMemoryDelete",
    description="Delete a memory from the structured memory system",
    tags=["memory", "structured", "delete"],
    category="structured_memory"
)
async def structured_memory_delete(
    memory_id: str,
    structured_memory: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Delete a memory from the structured memory system.
    
    Args:
        memory_id: ID of the memory to delete
        structured_memory: Structured memory service to use (injected)
        
    Returns:
        Result of the delete operation
    """
    if not structured_memory:
        return {
            "error": "Structured memory service not provided"
        }
        
    try:
        # Delete memory
        success = await structured_memory.delete_memory(memory_id)
        
        # Return result
        return {
            "success": success,
            "memory_id": memory_id
        }
    except Exception as e:
        logger.error(f"Error deleting structured memory: {e}")
        return {
            "error": f"Error deleting structured memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="structured_memory",
    description="Capability for structured memory operations",
    modality="memory"
)
@mcp_tool(
    name="StructuredMemorySearch",
    description="Search for memories in the structured memory system",
    tags=["memory", "structured", "search"],
    category="structured_memory"
)
async def structured_memory_search(
    query: str,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    min_importance: Optional[int] = None,
    limit: int = 10,
    structured_memory: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Search for memories in the structured memory system.
    
    Args:
        query: Search query
        category: Category to filter by (optional)
        tags: Tags to filter by (optional)
        min_importance: Minimum importance level (optional)
        limit: Maximum number of results
        structured_memory: Structured memory service to use (injected)
        
    Returns:
        Search results
    """
    if not structured_memory:
        return {
            "error": "Structured memory service not provided"
        }
        
    try:
        # Search memories
        results = await structured_memory.search_memories(
            query=query,
            category=category,
            tags=tags,
            min_importance=min_importance,
            limit=limit
        )
        
        # Return results
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error searching structured memories: {e}")
        return {
            "error": f"Error searching structured memories: {str(e)}",
            "success": False,
            "results": []
        }

# --- Nexus Operations ---

@mcp_capability(
    name="nexus_operations",
    description="Capability for Nexus processing operations",
    modality="agent"
)
@mcp_tool(
    name="NexusProcess",
    description="Process a message through the Nexus interface",
    tags=["nexus", "process", "message"],
    category="nexus_operations"
)
async def nexus_process(
    message: str,
    is_user: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
    auto_agency: Optional[bool] = None,
    nexus: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Process a message through the Nexus interface.
    
    Args:
        message: Message to process
        is_user: Whether the message is from the user
        metadata: Additional message metadata
        auto_agency: Whether to use automatic agency
        nexus: Nexus interface to use (injected)
        
    Returns:
        Processing result
    """
    if not nexus:
        return {
            "error": "Nexus interface not provided"
        }
        
    try:
        # Process message
        result = await nexus.process_message(
            message=message,
            is_user=is_user,
            metadata=metadata,
            auto_agency=auto_agency
        )
        
        # Return result
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error processing message through Nexus: {e}")
        return {
            "error": f"Error processing message through Nexus: {str(e)}",
            "success": False
        }

# --- Registration Functions ---

async def register_memory_tools(memory_manager, tool_registry):
    """Register memory tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, skipping memory tool registration")
        return
        
    try:
        # Get memory service
        client_id = getattr(memory_manager, "default_client_id", "claude")
        memory_service = await memory_manager.get_memory_service(client_id)
        
        # Add memory service to tool kwargs
        memory_store.memory_service = memory_service
        memory_query.memory_service = memory_service
        get_context.memory_service = memory_service
        
        # Register tools with tool registry
        await tool_registry.register_tool(memory_store._mcp_tool_meta.to_dict())
        await tool_registry.register_tool(memory_query._mcp_tool_meta.to_dict())
        await tool_registry.register_tool(get_context._mcp_tool_meta.to_dict())
        
        logger.info("Registered memory tools with MCP service")
    except Exception as e:
        logger.error(f"Error registering memory tools: {e}")

async def register_structured_memory_tools(memory_manager, tool_registry):
    """Register structured memory tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, skipping structured memory tool registration")
        return
        
    try:
        # Get structured memory service
        client_id = getattr(memory_manager, "default_client_id", "claude")
        structured_memory = await memory_manager.get_structured_memory(client_id)
        
        # Add structured memory to tool kwargs
        structured_memory_add.structured_memory = structured_memory
        structured_memory_get.structured_memory = structured_memory
        structured_memory_update.structured_memory = structured_memory
        structured_memory_delete.structured_memory = structured_memory
        structured_memory_search.structured_memory = structured_memory
        
        # Register tools with tool registry
        await tool_registry.register_tool(structured_memory_add._mcp_tool_meta.to_dict())
        await tool_registry.register_tool(structured_memory_get._mcp_tool_meta.to_dict())
        await tool_registry.register_tool(structured_memory_update._mcp_tool_meta.to_dict())
        await tool_registry.register_tool(structured_memory_delete._mcp_tool_meta.to_dict())
        await tool_registry.register_tool(structured_memory_search._mcp_tool_meta.to_dict())
        
        logger.info("Registered structured memory tools with MCP service")
    except Exception as e:
        logger.error(f"Error registering structured memory tools: {e}")

async def register_nexus_tools(memory_manager, tool_registry):
    """Register nexus tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, skipping nexus tool registration")
        return
        
    try:
        # Get nexus interface
        client_id = getattr(memory_manager, "default_client_id", "claude")
        nexus = await memory_manager.get_nexus_interface(client_id)
        
        # Add nexus to tool kwargs
        nexus_process.nexus = nexus
        
        # Register tools with tool registry
        await tool_registry.register_tool(nexus_process._mcp_tool_meta.to_dict())
        
        logger.info("Registered nexus tools with MCP service")
    except Exception as e:
        logger.error(f"Error registering nexus tools: {e}")

def get_all_tools(memory_manager=None):
    """Get all Engram MCP tools."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, returning empty tools list")
        return []
        
    from tekton.mcp.fastmcp.schema import MCPTool
    
    tools = []
    
    # Memory tools
    tools.append(memory_store._mcp_tool_meta.to_dict())
    tools.append(memory_query._mcp_tool_meta.to_dict())
    tools.append(get_context._mcp_tool_meta.to_dict())
    
    # Structured memory tools
    tools.append(structured_memory_add._mcp_tool_meta.to_dict())
    tools.append(structured_memory_get._mcp_tool_meta.to_dict())
    tools.append(structured_memory_update._mcp_tool_meta.to_dict())
    tools.append(structured_memory_delete._mcp_tool_meta.to_dict())
    tools.append(structured_memory_search._mcp_tool_meta.to_dict())
    
    # Nexus tools
    tools.append(nexus_process._mcp_tool_meta.to_dict())
    
    return tools

def get_all_capabilities(memory_manager=None):
    """Get all Engram MCP capabilities."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, returning empty capabilities list")
        return []
        
    from tekton.mcp.fastmcp.schema import MCPCapability
    
    capabilities = []
    
    # Add unique capabilities
    capability_names = set()
    
    # Memory operations capability
    if "memory_operations" not in capability_names:
        capabilities.append(MCPCapability(
            name="memory_operations",
            description="Capability for core memory operations",
            modality="memory"
        ))
        capability_names.add("memory_operations")
    
    # Structured memory capability
    if "structured_memory" not in capability_names:
        capabilities.append(MCPCapability(
            name="structured_memory",
            description="Capability for structured memory operations",
            modality="memory"
        ))
        capability_names.add("structured_memory")
    
    # Nexus operations capability
    if "nexus_operations" not in capability_names:
        capabilities.append(MCPCapability(
            name="nexus_operations",
            description="Capability for Nexus processing operations",
            modality="agent"
        ))
        capability_names.add("nexus_operations")
    
    return capabilities