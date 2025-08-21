"""
FastMCP Schema - Schema definitions for MCP protocol.

This module provides schema definitions for various MCP objects,
including tools, processors, capabilities, contexts, and messages.
"""

import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator

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

class ContentSchema(BaseModel):
    """Schema for MCP content items."""
    type: str  # ContentType as string to be more flexible
    format: Optional[str] = None
    data: Any
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields

class MessageSchema(BaseModel):
    """Schema for MCP messages."""
    id: Optional[str] = None
    version: str = "mcp/1.0"
    timestamp: Optional[float] = None
    source: Dict[str, Any]
    destination: Optional[Dict[str, Any]] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    content: List[ContentSchema]
    processing: Optional[Dict[str, Any]] = Field(default_factory=dict)
    security: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator("id", pre=True, always=True)
    def set_id(cls, v):
        """Set message ID if not provided."""
        return v or f"msg-{uuid.uuid4()}"
        
    @validator("timestamp", pre=True, always=True)
    def set_timestamp(cls, v):
        """Set timestamp if not provided."""
        return v or time.time()
        
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields

class ResponseSchema(MessageSchema):
    """Schema for MCP responses."""
    in_response_to: str
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields

class ParameterSchema(BaseModel):
    """Schema for tool parameters."""
    type: str
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields

class ReturnSchema(BaseModel):
    """Schema for tool return values."""
    type: str
    description: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields

class ToolSchemaContents(BaseModel):
    """Schema for tool specification contents."""
    parameters: Dict[str, ParameterSchema]
    return_type: ReturnSchema
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields

class ToolSchema(BaseModel):
    """Schema for MCP tools."""
    id: Optional[str] = None
    name: str
    description: str
    schema: Union[Dict[str, Any], ToolSchemaContents]
    tags: Optional[List[str]] = Field(default_factory=list)
    category: Optional[str] = "utility"
    version: Optional[str] = "1.0.0"
    endpoint: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    registered_at: Optional[float] = None
    
    @validator("id", pre=True, always=True)
    def set_id(cls, v):
        """Set tool ID if not provided."""
        return v or f"tool-{uuid.uuid4()}"
        
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields

class CapabilitySchema(BaseModel):
    """Schema for MCP capabilities."""
    name: str
    description: Optional[str] = None
    modality: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields

class ProcessorSchema(BaseModel):
    """Schema for MCP processors."""
    id: Optional[str] = None
    name: str
    description: str
    capabilities: List[str]
    endpoint: Optional[str] = None
    version: Optional[str] = "1.0.0"
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator("id", pre=True, always=True)
    def set_id(cls, v):
        """Set processor ID if not provided."""
        return v or f"processor-{uuid.uuid4()}"
        
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields

class ContextSchema(BaseModel):
    """Schema for MCP contexts."""
    id: Optional[str] = None
    data: Dict[str, Any]
    source: Dict[str, Any]
    created_at: Optional[float] = None
    updated_at: Optional[float] = None
    history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator("id", pre=True, always=True)
    def set_id(cls, v):
        """Set context ID if not provided."""
        return v or f"ctx-{uuid.uuid4()}"
        
    @validator("created_at", pre=True, always=True)
    def set_created_at(cls, v):
        """Set created_at if not provided."""
        return v or time.time()
        
    @validator("updated_at", pre=True, always=True)
    def set_updated_at(cls, v):
        """Set updated_at if not provided."""
        return v or time.time()
        
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields

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
        schema_class.validate(data)
        return True
    except Exception:
        return False

# MCP Request/Response schemas for API endpoints
class MCPRequest(BaseModel):
    """Schema for MCP API requests."""
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"

class MCPResponse(BaseModel):
    """Schema for MCP API responses."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"

# Aliases for backward compatibility and external API consistency
MCPTool = ToolSchema
MCPCapability = CapabilitySchema