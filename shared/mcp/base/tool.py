"""
Base MCP Tool implementation.

This provides a standardized way to define tools that can be exposed via MCP.
"""

from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
import inspect
import logging

from pydantic import BaseModel, Field, create_model
from tekton.models import TektonBaseModel

logger = logging.getLogger(__name__)


class MCPTool(ABC):
    """
    Base class for MCP tools.
    
    This class provides a standardized way to define tools that can be
    exposed through MCP. Each tool should inherit from this class and
    implement the execute method.
    """
    
    # Tool metadata (override in subclasses)
    name: str = "unnamed_tool"
    description: str = "No description provided"
    tags: List[str] = []
    
    def __init__(self):
        """Initialize the tool."""
        self._validate_metadata()
    
    def _validate_metadata(self):
        """Validate that required metadata is provided."""
        if self.name == "unnamed_tool":
            raise ValueError(f"{self.__class__.__name__} must define a 'name' attribute")
        if self.description == "No description provided":
            raise ValueError(f"{self.__class__.__name__} must define a 'description' attribute")
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool with given parameters.
        
        This method should be implemented by each tool to perform its
        specific functionality.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
        """
        pass
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Get the JSON Schema for tool input.
        
        This method introspects the execute method to build a schema.
        Override this method to provide a custom schema.
        
        Returns:
            JSON Schema dictionary
        """
        # Get execute method signature
        sig = inspect.signature(self.execute)
        
        # Build properties from parameters
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            
            # Determine type
            param_type = "string"  # default
            if param.annotation != inspect.Parameter.empty:
                # Map Python types to JSON Schema types
                type_map = {
                    str: "string",
                    int: "integer",
                    float: "number",
                    bool: "boolean",
                    list: "array",
                    dict: "object"
                }
                
                # Handle Optional types
                origin = getattr(param.annotation, "__origin__", None)
                if origin is Union:
                    args = param.annotation.__args__
                    # Filter out NoneType
                    non_none_args = [arg for arg in args if arg is not type(None)]
                    if non_none_args:
                        param_type = type_map.get(non_none_args[0], "string")
                else:
                    param_type = type_map.get(param.annotation, "string")
            
            # Build property schema
            prop_schema = {
                "type": param_type,
                "description": f"Parameter: {param_name}"
            }
            
            # Add to properties
            properties[param_name] = prop_schema
            
            # Check if required
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    def get_spec(self) -> Dict[str, Any]:
        """
        Get the complete tool specification.
        
        Returns:
            Tool specification dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.get_input_schema(),
            "tags": self.tags,
            "metadata": self.get_metadata()
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get additional tool metadata.
        
        Override this method to provide custom metadata.
        
        Returns:
            Metadata dictionary
        """
        return {
            "class": self.__class__.__name__,
            "module": self.__class__.__module__
        }
    
    async def __call__(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make the tool callable.
        
        This allows the tool to be used as a handler function.
        
        Args:
            parameters: Tool parameters
            context: Optional execution context
            
        Returns:
            Tool execution result
        """
        # Extract parameters and pass to execute
        return await self.execute(**parameters)


class SimpleMCPTool(MCPTool):
    """
    Simple MCP tool that can be created from a function.
    
    This is useful for quickly wrapping existing functions as MCP tools.
    """
    
    def __init__(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        """
        Initialize a simple tool from a function.
        
        Args:
            func: The function to wrap
            name: Tool name (defaults to function name)
            description: Tool description (defaults to function docstring)
            tags: Tool tags
        """
        self.func = func
        self.name = name or func.__name__
        self.description = description or (func.__doc__ or "").strip() or "No description"
        self.tags = tags or []
        
        super().__init__()
    
    async def execute(self, **kwargs) -> Any:
        """Execute the wrapped function."""
        # Check if function is async
        if inspect.iscoroutinefunction(self.func):
            return await self.func(**kwargs)
        else:
            return self.func(**kwargs)
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get schema from the wrapped function."""
        # Get function signature
        sig = inspect.signature(self.func)
        
        # Build properties from parameters
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            
            # Determine type
            param_type = "string"  # default
            if param.annotation != inspect.Parameter.empty:
                # Map Python types to JSON Schema types
                type_map = {
                    str: "string",
                    int: "integer",
                    float: "number",
                    bool: "boolean",
                    list: "array",
                    dict: "object"
                }
                param_type = type_map.get(param.annotation, "string")
            
            # Build property schema
            prop_schema = {
                "type": param_type,
                "description": f"Parameter: {param_name}"
            }
            
            # Add to properties
            properties[param_name] = prop_schema
            
            # Check if required
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }


# Import Union for type checking
from typing import Union