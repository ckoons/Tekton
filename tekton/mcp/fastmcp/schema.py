"""
FastMCP Schema - Schema definitions for MCP protocol.

This module provides schema definitions for various MCP objects,
including tools, processors, capabilities, contexts, and messages.
"""

import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import Field, ConfigDict, field_validator, model_validator
from tekton.models.base import TektonBaseModel

class ContentType(str, Enum):
    """Types of content in MCP messages."""
    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    STRUCTURED = "structured"
    AUDIO = "audio"
    VIDEO = "video"
    CANVAS = "canvas"
    FILE = "file"

class ContentSchema(TektonBaseModel):
    """Schema for MCP content items."""
    type: str  # ContentType as string to be more flexible
    format: Optional[str] = None
    data: Any
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = ConfigDict(extra="allow")

class MessageSchema(TektonBaseModel):
    """Schema for MCP messages."""
    id: Optional[str] = Field(default_factory=lambda: f"msg-{uuid.uuid4()}")
    version: str = "mcp/1.0"
    timestamp: Optional[float] = Field(default_factory=time.time)
    source: Dict[str, Any]
    destination: Optional[Dict[str, Any]] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    content: List[ContentSchema]
    processing: Optional[Dict[str, Any]] = Field(default_factory=dict)
    security: Optional[Dict[str, Any]] = Field(default_factory=dict)
        
    model_config = ConfigDict(extra="allow")

class ResponseSchema(MessageSchema):
    """Schema for MCP responses."""
    in_response_to: str
    
    model_config = ConfigDict(extra="allow")

class ParameterSchema(TektonBaseModel):
    """Schema for tool parameters."""
    type: str
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None
    
    model_config = ConfigDict(extra="allow")

class ReturnSchema(TektonBaseModel):
    """Schema for tool return values."""
    type: str
    description: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")

class ToolSchemaContents(TektonBaseModel):
    """Schema for tool specification contents."""
    parameters: Dict[str, ParameterSchema]
    return_type: ReturnSchema
    
    model_config = ConfigDict(extra="allow")

class ToolSchema(TektonBaseModel):
    """Schema for MCP tools."""
    id: Optional[str] = Field(default_factory=lambda: f"tool-{uuid.uuid4()}")
    name: str
    description: str
    input_schema: Union[Dict[str, Any], ToolSchemaContents] = Field(alias="schema")
    tags: Optional[List[str]] = Field(default_factory=list)
    category: Optional[str] = "utility"
    version: Optional[str] = "1.0.0"
    endpoint: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    registered_at: Optional[float] = None
    
    model_config = ConfigDict(
        populate_by_name=True,  # Allow both field name and alias
        extra="allow"  # Allow extra fields
    )

class CapabilitySchema(TektonBaseModel):
    """Schema for MCP capabilities."""
    name: str
    description: Optional[str] = None
    modality: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = ConfigDict(extra="allow")

class ProcessorSchema(TektonBaseModel):
    """Schema for MCP processors."""
    id: Optional[str] = Field(default_factory=lambda: f"processor-{uuid.uuid4()}")
    name: str
    description: str
    capabilities: List[str]
    endpoint: Optional[str] = None
    version: Optional[str] = "1.0.0"
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
        
    model_config = ConfigDict(extra="allow")

class ContextSchema(TektonBaseModel):
    """Schema for MCP contexts."""
    id: Optional[str] = Field(default_factory=lambda: f"ctx-{uuid.uuid4()}")
    data: Dict[str, Any]
    source: Dict[str, Any]
    created_at: Optional[float] = Field(default_factory=time.time)
    updated_at: Optional[float] = Field(default_factory=time.time)
    history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
        
    model_config = ConfigDict(extra="allow")

def validate_schema(schema_type: str, data: Dict[str, Any]) -> bool:
    """
    Validate data against a schema.
    
    Args:
        schema_type: Schema type to validate against
        data: Data to validate
        
    Returns:
        True if valid, False otherwise
    """
    schema_map = {
        "tool": ToolSchema,
        "processor": ProcessorSchema,
        "capability": CapabilitySchema,
        "context": ContextSchema,
        "message": MessageSchema,
        "response": ResponseSchema,
        "content": ContentSchema
    }
    
    schema_class = schema_map.get(schema_type.lower())
    if not schema_class:
        raise ValueError(f"Unknown schema type: {schema_type}")
        
    try:
        schema_class.model_validate(data)
        return True
    except Exception:
        return False

# MCP Request/Response schemas for API endpoints
class MCPRequest(TektonBaseModel):
    """Schema for MCP API requests."""
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = ConfigDict(extra="allow")

class MCPResponse(TektonBaseModel):
    """Schema for MCP API responses."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = ConfigDict(extra="allow")

# Aliases for backward compatibility and external API consistency
MCPTool = ToolSchema
MCPCapability = CapabilitySchema