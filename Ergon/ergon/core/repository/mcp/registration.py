"""
Tool registration module for MCP integration.

This module handles registering, unregistering, and updating tools
in the Ergon repository for use through MCP interfaces.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Callable, Union
from functools import wraps

from ergon.core.database.engine import get_db
from ergon.core.repository.models import Tool, ComponentType
from ergon.core.repository.repository import RepositoryService

logger = logging.getLogger(__name__)

# Global registry of MCP-compatible tools
_mcp_tool_registry: Dict[str, Dict[str, Any]] = {}

def register_tool(
    name: str,
    description: str,
    function: Callable,
    schema: Dict[str, Any],
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    version: str = "0.1.0",
    update_if_exists: bool = True
) -> Dict[str, Any]:
    """
    Register a tool with the MCP tool registry.
    
    Args:
        name: Unique name for the tool
        description: Description of what the tool does
        function: Callable that implements the tool
        schema: JSON schema defining the tool's parameters
        tags: Optional list of tags for categorizing the tool
        metadata: Optional additional metadata
        version: Tool version
        update_if_exists: Whether to update if the tool already exists
        
    Returns:
        Tool registration information
    
    Raises:
        ValueError: If the tool already exists and update_if_exists is False
    """
    global _mcp_tool_registry
    
    # Check if tool already exists
    if name in _mcp_tool_registry and not update_if_exists:
        raise ValueError(f"Tool '{name}' is already registered")
    
    # Validate schema
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dictionary")
    
    if "name" not in schema or "parameters" not in schema:
        raise ValueError("Schema must contain 'name' and 'parameters' keys")
    
    # Create tool entry
    tool_entry = {
        "name": name,
        "description": description,
        "schema": schema,
        "function": function,
        "tags": tags or [],
        "metadata": metadata or {},
        "version": version
    }
    
    # Add to registry
    _mcp_tool_registry[name] = tool_entry
    
    # Log the registration
    logger.info(f"Registered MCP tool: {name} (v{version})")
    
    # Also save in repository database 
    try:
        repo = RepositoryService()
        
        # Extract parameters from schema
        parameters = []
        if "properties" in schema.get("parameters", {}):
            for param_name, param_schema in schema["parameters"]["properties"].items():
                param = {
                    "name": param_name,
                    "description": param_schema.get("description", ""),
                    "type": param_schema.get("type", "string"),
                    "required": param_name in schema["parameters"].get("required", []),
                    "default_value": json.dumps(param_schema.get("default")) if "default" in param_schema else None
                }
                parameters.append(param)
        
        # Convert tags to capabilities
        capabilities = [{"name": tag, "description": ""} for tag in (tags or [])]
        
        # See if tool already exists in DB
        existing_tool = repo.get_component_by_name(name)
        
        if existing_tool and isinstance(existing_tool, Tool):
            # Update existing tool
            repo.update_component(
                existing_tool.id,
                {
                    "description": description,
                    "version": version,
                    "implementation_type": "mcp",
                }
            )
            # DB cascade will handle parameters and capabilities
        else:
            # Create new tool in repository
            repo.create_tool(
                name=name,
                description=description,
                entry_point=name,
                implementation_type="mcp",
                capabilities=capabilities,
                parameters=parameters,
                metadata=metadata or {},
                version=version
            )
                
        logger.debug(f"Saved MCP tool '{name}' to repository database")
    except Exception as e:
        logger.error(f"Error saving MCP tool '{name}' to database: {str(e)}")
    
    # Return a copy without the function
    result = tool_entry.copy()
    result.pop("function")
    return result


def unregister_tool(name: str) -> bool:
    """
    Unregister a tool from the MCP tool registry.
    
    Args:
        name: Name of the tool to unregister
        
    Returns:
        True if tool was unregistered, False if not found
    """
    global _mcp_tool_registry
    
    if name not in _mcp_tool_registry:
        return False
    
    # Remove from registry
    _mcp_tool_registry.pop(name)
    logger.info(f"Unregistered MCP tool: {name}")
    
    # Mark as inactive in database
    try:
        repo = RepositoryService()
        tool = repo.get_component_by_name(name)
        if tool:
            repo.delete_component(tool.id)
            logger.debug(f"Marked MCP tool '{name}' as inactive in repository database")
    except Exception as e:
        logger.error(f"Error removing MCP tool '{name}' from database: {str(e)}")
    
    return True


def update_tool_registry(tools: List[Dict[str, Any]]) -> int:
    """
    Update the tool registry with a list of tools.
    
    Args:
        tools: List of tool definitions to register
        
    Returns:
        Number of tools registered
    """
    count = 0
    for tool in tools:
        try:
            register_tool(
                name=tool["name"],
                description=tool["description"],
                function=tool["function"],
                schema=tool["schema"],
                tags=tool.get("tags"),
                metadata=tool.get("metadata"),
                version=tool.get("version", "0.1.0")
            )
            count += 1
        except Exception as e:
            logger.error(f"Error registering tool '{tool.get('name', 'unknown')}': {str(e)}")
    
    return count


def get_registered_tools() -> Dict[str, Dict[str, Any]]:
    """
    Get all registered MCP tools.
    
    Returns:
        Dictionary of registered tools (without function references)
    """
    result = {}
    
    for name, tool in _mcp_tool_registry.items():
        tool_copy = tool.copy()
        tool_copy.pop("function", None)
        result[name] = tool_copy
    
    return result


def get_tool(name: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific tool by name.
    
    Args:
        name: Name of the tool to retrieve
        
    Returns:
        Tool information or None if not found
    """
    if name not in _mcp_tool_registry:
        return None
    
    return _mcp_tool_registry[name]


def mcp_tool(
    name: str,
    description: str,
    schema: Dict[str, Any],
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    version: str = "0.1.0"
) -> Callable:
    """
    Decorator to register a function as an MCP tool.
    
    Args:
        name: Tool name
        description: Tool description
        schema: JSON schema for parameters
        tags: Optional tags for the tool
        metadata: Optional metadata
        version: Tool version
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        register_tool(
            name=name,
            description=description,
            function=func,
            schema=schema,
            tags=tags,
            metadata=metadata,
            version=version
        )
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator