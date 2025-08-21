"""
Tekton Shared Models

This package provides standardized Pydantic v2 models used across all Tekton components.
These models ensure consistent data validation, serialization, and API contracts.
"""

from .base import (
    TektonBaseModel,
    ErrorResponse,
    SuccessResponse,
    ValidationErrorDetail,
    APIResponse
)
from .health import (
    HealthStatus,
    HealthCheckResponse,
    StatusResponse,
    DependencyStatus,
    ComponentInfo,
    create_health_response
)
from .mcp import (
    MCPTool,
    MCPToolList,
    MCPToolCall,
    MCPToolResponse,
    MCPError,
    MCPErrorCode
)
from .registration import (
    ComponentRegistration,
    RegistrationRequest,
    RegistrationResponse,
    HeartbeatRequest,
    HeartbeatResponse
)

__all__ = [
    # Base models
    "TektonBaseModel",
    "ErrorResponse",
    "SuccessResponse",
    "ValidationErrorDetail",
    "APIResponse",
    # Health models
    "HealthStatus",
    "HealthCheckResponse",
    "StatusResponse",
    "DependencyStatus",
    "ComponentInfo",
    "create_health_response",
    # MCP models
    "MCPTool",
    "MCPToolList",
    "MCPToolCall",
    "MCPToolResponse",
    "MCPError",
    "MCPErrorCode",
    # Registration models
    "ComponentRegistration",
    "RegistrationRequest",
    "RegistrationResponse",
    "HeartbeatRequest",
    "HeartbeatResponse",
]