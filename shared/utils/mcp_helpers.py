"""
FastMCP helper utilities for Tekton components.

Provides standardized functions for creating and managing FastMCP servers,
registering tools, and converting between different tool formats.
"""
import inspect
import logging
from typing import List, Callable, Optional, Dict, Any, TypeVar, get_type_hints
from datetime import datetime
import asyncio

from shared.utils.errors import ComponentError
from landmarks import architecture_decision, integration_point, api_contract

logger = logging.getLogger(__name__)

# Type variable for generic tool functions
T = TypeVar('T', bound=Callable)

# Import FastMCPServer if available
try:
    from fastmcp import FastMCPServer
    FASTMCP_AVAILABLE = True
except ImportError:
    logger.warning("fastmcp not available. Install with: pip install fastmcp")
    FASTMCP_AVAILABLE = False
    
    # Mock FastMCPServer for when it's not available
    class FastMCPServer:
        def __init__(self, name: str, version: str, description: str):
            self.name = name
            self.version = version
            self.description = description
        
        def register_tool(self, tool: Callable):
            pass


@integration_point(
    title="MCP server creation",
    target_component="AI Agents",
    protocol="MCP",
    data_flow="Component tools exposed to CI agents via Model Context Protocol"
)
@architecture_decision(
    title="FastMCP for CI integration",
    rationale="Use FastMCP to expose component capabilities as tools that CI agents can call",
    alternatives_considered=["Custom protocol", "Direct API calls", "Function calling"],
    impacts=["ai_integration", "tool_discovery", "agent_capabilities"],
    decided_by="team"
)
def create_mcp_server(
    component_name: str,
    version: str = "0.1.0",
    description: Optional[str] = None
) -> FastMCPServer:
    """
    Create a standardized FastMCP server for a component.
    
    Args:
        component_name: Name of the component
        version: Version string
        description: Optional custom description
        
    Returns:
        Configured FastMCPServer instance
    """
    if not FASTMCP_AVAILABLE:
        logger.warning(f"Creating mock FastMCP server for {component_name}")
    
    if description is None:
        description = f"FastMCP server for {component_name}"
    
    server = FastMCPServer(
        name=component_name,
        version=version,
        description=description
    )
    
    logger.info(f"Created FastMCP server for {component_name} v{version}")
    return server


def register_mcp_tools(
    server: FastMCPServer,
    tools: List[Callable],
    error_handling: bool = True
) -> int:
    """
    Bulk register tools with a FastMCP server.
    
    Args:
        server: FastMCP server instance
        tools: List of tool functions to register
        error_handling: Whether to wrap tools with error handling
        
    Returns:
        Number of successfully registered tools
    """
    success_count = 0
    
    for tool in tools:
        try:
            if error_handling and hasattr(server, 'name'):
                tool = wrap_tool_with_error_handling(tool, server.name)
            
            server.register_tool(tool)
            success_count += 1
            logger.debug(f"Registered tool: {tool.__name__}")
        except Exception as e:
            logger.error(f"Failed to register {tool.__name__ if hasattr(tool, '__name__') else 'tool'}: {e}")
    
    logger.info(f"Registered {success_count}/{len(tools)} tools")
    return success_count


def convert_tool_to_schema(tool: Callable) -> Dict[str, Any]:
    """
    Convert a Python function to MCP tool schema.
    
    Extracts function signature, docstring, and type hints to create
    a standardized tool schema.
    
    Args:
        tool: Function to convert
        
    Returns:
        MCP-compatible tool schema
    """
    # Get function signature
    sig = inspect.signature(tool)
    type_hints = get_type_hints(tool)
    
    # Parse docstring
    docstring = inspect.getdoc(tool) or "No description available"
    description = docstring.split('\n')[0]  # First line is description
    
    # Build parameter schema
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue
            
        param_type = type_hints.get(param_name, Any)
        param_schema = {"type": "string"}  # Default type
        
        # Map Python types to JSON schema types
        if param_type == int:
            param_schema["type"] = "integer"
        elif param_type == float:
            param_schema["type"] = "number"
        elif param_type == bool:
            param_schema["type"] = "boolean"
        elif param_type == str:
            param_schema["type"] = "string"
        elif hasattr(param_type, '__origin__'):  # Generic types
            if param_type.__origin__ == list:
                param_schema["type"] = "array"
            elif param_type.__origin__ == dict:
                param_schema["type"] = "object"
        
        # Add default value if present
        if param.default != param.empty:
            param_schema["default"] = param.default
        else:
            required.append(param_name)
        
        # Extract parameter description from docstring if available
        # (Simple extraction - looks for "param_name:" in docstring)
        for line in docstring.split('\n'):
            if f"{param_name}:" in line:
                param_desc = line.split(':', 1)[1].strip()
                param_schema["description"] = param_desc
                break
        
        properties[param_name] = param_schema
    
    return {
        "name": tool.__name__,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }


def wrap_tool_with_error_handling(tool: T, component_name: str) -> T:
    """
    Wrap a tool function with standardized error handling.
    
    Args:
        tool: Tool function to wrap
        component_name: Name of the component for error reporting
        
    Returns:
        Wrapped tool function
    """
    if asyncio.iscoroutinefunction(tool):
        async def async_wrapper(*args, **kwargs):
            try:
                return await tool(*args, **kwargs)
            except Exception as e:
                logger.error(f"[{component_name}] Tool {tool.__name__} failed: {e}")
                return {
                    "error": True,
                    "message": str(e),
                    "tool": tool.__name__,
                    "component": component_name
                }
        
        # Preserve function metadata
        async_wrapper.__name__ = tool.__name__
        async_wrapper.__doc__ = tool.__doc__
        return async_wrapper
    else:
        def sync_wrapper(*args, **kwargs):
            try:
                return tool(*args, **kwargs)
            except Exception as e:
                logger.error(f"[{component_name}] Tool {tool.__name__} failed: {e}")
                return {
                    "error": True,
                    "message": str(e),
                    "tool": tool.__name__,
                    "component": component_name
                }
        
        # Preserve function metadata
        sync_wrapper.__name__ = tool.__name__
        sync_wrapper.__doc__ = tool.__doc__
        return sync_wrapper


def create_standard_tools(component_name: str, port: int) -> List[Callable]:
    """
    Create standard tools that every component should have.
    
    Args:
        component_name: Name of the component
        port: Port number the component is running on
        
    Returns:
        List of standard tool functions
    """
    async def health_check() -> Dict[str, Any]:
        """Get component health status."""
        return {
            "status": "healthy",
            "component": component_name,
            "port": port,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def component_info() -> Dict[str, Any]:
        """Get detailed component information."""
        return {
            "name": component_name,
            "port": port,
            "capabilities": [],
            "version": "0.1.0",
            "uptime_seconds": 0  # Would be calculated in real implementation
        }
    
    return [health_check, component_info]


class MCPToolRegistry:
    """Registry for managing MCP tools."""
    
    def __init__(self):
        """Initialize empty tool registry."""
        self._tools: Dict[str, Callable] = {}
    
    def register(self, name: str, tool: Callable):
        """Register a tool in the registry."""
        self._tools[name] = tool
        logger.debug(f"Registered tool: {name}")
    
    def get(self, name: str) -> Optional[Callable]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[Dict[str, str]]:
        """List all registered tools with descriptions."""
        tools = []
        for name, tool in self._tools.items():
            doc = inspect.getdoc(tool) or "No description"
            tools.append({
                "name": name,
                "description": doc.split('\n')[0]  # First line only
            })
        return tools
    
    def clear(self):
        """Clear all registered tools."""
        self._tools.clear()
    
    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self._tools)


def convert_metis_tool(
    metis_schema: Dict[str, Any],
    implementation: Callable
) -> Callable:
    """
    Convert a Metis-style tool definition to a callable with proper metadata.
    
    Metis uses a specific schema format that needs to be adapted for FastMCP.
    
    Args:
        metis_schema: Metis tool schema with name, description, parameters
        implementation: The actual function implementation
        
    Returns:
        Wrapped function with proper metadata
    """
    # Create wrapper with Metis metadata
    if asyncio.iscoroutinefunction(implementation):
        async def metis_wrapper(**kwargs):
            return await implementation(**kwargs)
    else:
        def metis_wrapper(**kwargs):
            return implementation(**kwargs)
    
    # Apply metadata from Metis schema
    metis_wrapper.__name__ = metis_schema["name"]
    
    # Build docstring from schema
    doc_lines = [metis_schema["description"]]
    
    if "parameters" in metis_schema and "properties" in metis_schema["parameters"]:
        doc_lines.append("\nArgs:")
        for param, param_schema in metis_schema["parameters"]["properties"].items():
            param_desc = param_schema.get("description", "No description")
            param_type = param_schema.get("type", "any")
            doc_lines.append(f"    {param} ({param_type}): {param_desc}")
    
    metis_wrapper.__doc__ = "\n".join(doc_lines)
    
    return metis_wrapper