"""
FastMCP Decorators - Decorator-based approach for MCP implementation.

This module provides decorators for defining tools, capabilities, and processors
in the MCP protocol, inspired by FastMCP's decorator pattern approach.
"""

import functools
import inspect
import json
import uuid
import time
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union, get_type_hints

from pydantic import ValidationError, create_model

logger = logging.getLogger(__name__)

class MCPToolMeta:
    """Metadata for MCP tools."""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        return_type: Optional[Dict[str, Any]] = None,
        schema: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        version: Optional[str] = None,
        endpoint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize tool metadata.
        
        Args:
            name: Tool name
            description: Tool description
            parameters: Parameter specifications
            return_type: Return type specification
            schema: Tool schema (if provided directly)
            tags: Tool tags
            category: Tool category
            version: Tool version
            endpoint: Tool endpoint
            metadata: Additional metadata
        """
        self.id = f"tool-{uuid.uuid4()}"
        self.name = name
        self.description = description
        self.parameters = parameters or {}
        self.return_type = return_type or {}
        self.schema = schema or {}
        self.tags = tags or []
        self.category = category or "utility"
        self.version = version or "1.0.0"
        self.endpoint = endpoint
        self.metadata = metadata or {}
        self.registered_at = None
        self.function = None
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tool metadata to a dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "schema": self.schema or {
                "parameters": self.parameters,
                "return_type": self.return_type
            },
            "tags": self.tags,
            "category": self.category,
            "version": self.version,
            "endpoint": self.endpoint,
            "metadata": self.metadata,
            "registered_at": self.registered_at
        }
        
    def register(self, tool_function: Callable) -> None:
        """
        Register the tool function.
        
        Args:
            tool_function: Function to register
        """
        self.function = tool_function
        self.registered_at = time.time()
        logger.info(f"Tool registered: {self.name} ({self.id})")

def mcp_tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    category: Optional[str] = None,
    version: Optional[str] = None,
    endpoint: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Decorator for MCP tools.
    
    This decorator marks a function as an MCP tool, collecting metadata
    about the tool from the function's signature and docstring.
    
    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)
        tags: Tool tags
        category: Tool category
        version: Tool version
        endpoint: Tool endpoint
        metadata: Additional metadata
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        # Get function signature and docstring
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or ""
        func_name = name or func.__name__
        func_description = description or doc.split("\n\n")[0] if doc else ""
        
        # Get parameter specifications from type hints
        type_hints = get_type_hints(func)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == "self" or param_name == "cls":
                continue
                
            param_type = type_hints.get(param_name, Any)
            param_default = param.default if param.default is not inspect.Parameter.empty else None
            param_required = param.default is inspect.Parameter.empty
            param_annotation = param.annotation if param.annotation is not inspect.Parameter.empty else None
            
            parameters[param_name] = {
                "type": str(param_type),
                "required": param_required,
                "default": param_default
            }
            
            # Add description from docstring if available
            param_desc = _extract_param_description(doc, param_name)
            if param_desc:
                parameters[param_name]["description"] = param_desc
                
        # Get return type
        return_type = {
            "type": str(type_hints.get("return", Any))
        }
        
        # Add return description from docstring if available
        return_desc = _extract_return_description(doc)
        if return_desc:
            return_type["description"] = return_desc
            
        # Create tool metadata
        tool_meta = MCPToolMeta(
            name=func_name,
            description=func_description,
            parameters=parameters,
            return_type=return_type,
            tags=tags or [],
            category=category,
            version=version,
            endpoint=endpoint,
            metadata=metadata or {}
        )
        
        # Set metadata on function
        func._mcp_tool_meta = tool_meta
        
        # Register tool
        tool_meta.register(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
            
        return wrapper
        
    return decorator

def mcp_capability(
    name: str,
    description: Optional[str] = None,
    modality: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Decorator for MCP capabilities.
    
    This decorator adds capability metadata to a function or class,
    indicating what capabilities it provides in the MCP protocol.
    
    Args:
        name: Capability name
        description: Capability description
        modality: Capability modality (text, code, image, etc.)
        metadata: Additional metadata
        
    Returns:
        Decorated function or class
    """
    def decorator(obj: Any) -> Any:
        # Create capability metadata
        capability_meta = {
            "name": name,
            "description": description or f"Capability for {name}",
            "modality": modality,
            "metadata": metadata or {}
        }
        
        # Get or create capabilities list
        if not hasattr(obj, "_mcp_capabilities"):
            obj._mcp_capabilities = []
            
        # Add capability
        obj._mcp_capabilities.append(capability_meta)
        
        return obj
        
    return decorator

def mcp_processor(
    name: Optional[str] = None,
    description: Optional[str] = None,
    capabilities: Optional[List[str]] = None,
    endpoint: Optional[str] = None,
    version: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Decorator for MCP processors.
    
    This decorator marks a class as an MCP processor, collecting metadata
    about the processor from the class's methods and capabilities.
    
    Args:
        name: Processor name (defaults to class name)
        description: Processor description (defaults to class docstring)
        capabilities: Processor capabilities
        endpoint: Processor endpoint
        version: Processor version
        metadata: Additional metadata
        
    Returns:
        Decorated class
    """
    def decorator(cls: Type) -> Type:
        # Get class docstring
        doc = inspect.getdoc(cls) or ""
        cls_name = name or cls.__name__
        cls_description = description or doc.split("\n\n")[0] if doc else ""
        
        # Collect capabilities from methods
        all_capabilities = capabilities or []
        
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if hasattr(attr, "_mcp_capabilities"):
                for capability in attr._mcp_capabilities:
                    all_capabilities.append(capability["name"])
                    
        # Create processor metadata
        processor_meta = {
            "id": f"processor-{uuid.uuid4()}",
            "name": cls_name,
            "description": cls_description,
            "capabilities": list(set(all_capabilities)),  # Deduplicate
            "endpoint": endpoint,
            "version": version or "1.0.0",
            "metadata": metadata or {}
        }
        
        # Set metadata on class
        cls._mcp_processor_meta = processor_meta
        
        return cls
        
    return decorator

def mcp_context(
    name: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Decorator for MCP context handlers.
    
    This decorator marks a class as an MCP context handler, collecting metadata
    about the context handler from the class's methods.
    
    Args:
        name: Context handler name (defaults to class name)
        description: Context handler description (defaults to class docstring)
        metadata: Additional metadata
        
    Returns:
        Decorated class
    """
    def decorator(cls: Type) -> Type:
        # Get class docstring
        doc = inspect.getdoc(cls) or ""
        cls_name = name or cls.__name__
        cls_description = description or doc.split("\n\n")[0] if doc else ""
        
        # Create context metadata
        context_meta = {
            "id": f"context-{uuid.uuid4()}",
            "name": cls_name,
            "description": cls_description,
            "metadata": metadata or {}
        }
        
        # Set metadata on class
        cls._mcp_context_meta = context_meta
        
        return cls
        
    return decorator

def _extract_param_description(docstring: str, param_name: str) -> Optional[str]:
    """
    Extract parameter description from docstring.
    
    Args:
        docstring: Function docstring
        param_name: Parameter name
        
    Returns:
        Parameter description or None if not found
    """
    if not docstring:
        return None
        
    lines = docstring.split("\n")
    param_prefix = f"    {param_name}: "
    
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{param_name}:"):
            return line.split(":", 1)[1].strip()
        if line.strip().startswith("Args:"):
            # Look for parameter in the Args section
            for j in range(i + 1, len(lines)):
                if lines[j].startswith(param_prefix):
                    return lines[j][len(param_prefix):].strip()
                if lines[j].strip() and not lines[j].startswith("    "):
                    # End of Args section
                    break
                    
    return None

def _extract_return_description(docstring: str) -> Optional[str]:
    """
    Extract return description from docstring.
    
    Args:
        docstring: Function docstring
        
    Returns:
        Return description or None if not found
    """
    if not docstring:
        return None
        
    lines = docstring.split("\n")
    
    for i, line in enumerate(lines):
        if line.strip().startswith("Returns:"):
            # Extract description from the Returns section
            if i + 1 < len(lines) and lines[i + 1].startswith("    "):
                return lines[i + 1].strip()
            return line.split(":", 1)[1].strip()
            
    return None