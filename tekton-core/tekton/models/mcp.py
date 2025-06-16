"""
MCP (Model Context Protocol) Models for Tekton

Provides standardized models for MCP tool definitions and interactions.
Compatible with MCP v2 specification.
"""

from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import Field, field_validator, ConfigDict

from .base import TektonBaseModel


class MCPErrorCode(str, Enum):
    """Standard MCP error codes"""
    INVALID_REQUEST = "invalid_request"
    METHOD_NOT_FOUND = "method_not_found"
    INVALID_PARAMS = "invalid_params"
    INTERNAL_ERROR = "internal_error"
    PARSE_ERROR = "parse_error"
    TOOL_NOT_FOUND = "tool_not_found"
    TOOL_EXECUTION_ERROR = "tool_execution_error"


class MCPToolParameter(TektonBaseModel):
    """Parameter definition for an MCP tool"""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (string, number, boolean, object, array)")
    description: Optional[str] = Field(None, description="Parameter description")
    required: bool = Field(False, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value if not provided")
    enum: Optional[List[Any]] = Field(None, description="Allowed values")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate parameter type"""
        valid_types = {'string', 'number', 'integer', 'boolean', 'object', 'array', 'null'}
        if v not in valid_types:
            raise ValueError(f'Invalid type. Must be one of: {valid_types}')
        return v


class MCPTool(TektonBaseModel):
    """Definition of an MCP tool"""
    name: str = Field(..., description="Tool name", pattern=r'^[a-zA-Z][a-zA-Z0-9_-]*$')
    description: str = Field(..., description="Tool description")
    input_schema: Dict[str, Any] = Field(..., description="JSON Schema for tool parameters")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema for tool output")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Tool metadata")
    
    @field_validator('input_schema')
    @classmethod
    def validate_input_schema(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure input schema has required JSON Schema fields"""
        if 'type' not in v:
            v['type'] = 'object'
        if 'properties' not in v and v['type'] == 'object':
            v['properties'] = {}
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "get_weather",
                "description": "Get weather information for a location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name or coordinates"
                        },
                        "units": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "default": "celsius"
                        }
                    },
                    "required": ["location"]
                },
                "metadata": {
                    "category": "weather",
                    "rateLimit": "100/hour"
                }
            }
        }
    )


class MCPToolList(TektonBaseModel):
    """List of available MCP tools"""
    tools: List[MCPTool] = Field(..., description="Available tools")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="List metadata")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tools": [
                    {
                        "name": "list_files",
                        "description": "List files in a directory",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"}
                            }
                        }
                    }
                ],
                "metadata": {
                    "version": "1.0.0",
                    "component": "filesystem"
                }
            }
        }
    )


class MCPToolCall(TektonBaseModel):
    """Request to execute an MCP tool"""
    tool_name: str = Field(..., description="Name of tool to execute", alias="name")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Call metadata")
    
    @field_validator('tool_name')
    @classmethod
    def validate_tool_name(cls, v: str) -> str:
        """Validate tool name format"""
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v):
            raise ValueError('Tool name must start with letter and contain only letters, numbers, underscore, or hyphen')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "get_weather",
                "arguments": {
                    "location": "San Francisco",
                    "units": "fahrenheit"
                },
                "metadata": {
                    "request_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }
    )


class MCPToolResponse(TektonBaseModel):
    """Response from MCP tool execution"""
    tool_name: str = Field(..., description="Name of executed tool", alias="name")
    result: Any = Field(..., description="Tool execution result")
    error: Optional['MCPError'] = Field(None, description="Error if execution failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "get_weather",
                "result": {
                    "temperature": 72,
                    "conditions": "Partly cloudy",
                    "humidity": 65
                },
                "metadata": {
                    "execution_time": 0.123,
                    "cache_hit": False
                }
            }
        }
    )


class MCPError(TektonBaseModel):
    """Error response for MCP operations"""
    code: MCPErrorCode = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "tool_not_found",
                "message": "Tool 'unknown_tool' not found",
                "details": {
                    "available_tools": ["get_weather", "list_files"],
                    "suggestion": "Did you mean 'get_weather'?"
                }
            }
        }
    )


# Update forward reference
MCPToolResponse.model_rebuild()