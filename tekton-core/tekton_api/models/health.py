"""
Health and Status Models for Tekton

Provides standardized health check and status models for all components.
Replaces the old shared/utils/health_check.py with Pydantic v2 models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator, ConfigDict

from .base import TektonBaseModel


class HealthStatus(str, Enum):
    """Component health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentInfo(TektonBaseModel):
    """Basic component information"""
    name: str = Field(..., description="Component name")
    version: str = Field(..., description="Component version")
    description: Optional[str] = Field(None, description="Component description")
    
    @field_validator('name')
    @classmethod
    def validate_component_name(cls, v: str) -> str:
        """Ensure component name is lowercase"""
        if not v.islower():
            raise ValueError('Component name must be lowercase')
        return v
    
    @field_validator('version')
    @classmethod
    def validate_version_format(cls, v: str) -> str:
        """Validate semantic version format"""
        import re
        if not re.match(r'^\d+\.\d+\.\d+(-[\w\d]+)?$', v):
            raise ValueError('Version must follow semantic versioning (e.g., 1.0.0)')
        return v


class DependencyStatus(TektonBaseModel):
    """Status of a component dependency"""
    name: str = Field(..., description="Dependency name")
    status: HealthStatus = Field(..., description="Dependency health status")
    message: Optional[str] = Field(None, description="Status message")
    endpoint: Optional[str] = Field(None, description="Dependency endpoint")
    last_check: Optional[datetime] = Field(None, description="Last health check time")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "hermes",
                "status": "healthy",
                "message": "Connected and responding",
                "endpoint": "http://localhost:8001",
                "lastCheck": "2025-01-06T10:00:00Z"
            }
        }
    )


class HealthCheckResponse(TektonBaseModel):
    """Standard health check response for all Tekton components"""
    status: HealthStatus = Field(..., description="Overall health status")
    component: str = Field(..., description="Component name")
    version: str = Field(..., description="Component version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    uptime: Optional[float] = Field(None, ge=0, description="Uptime in seconds")
    port: int = Field(..., ge=8000, le=9999, description="Component port")
    registered_with_hermes: bool = Field(False, description="Hermes registration status")
    dependencies: List[DependencyStatus] = Field(default_factory=list, description="Dependency statuses")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Component-specific metrics")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    
    @field_validator('component')
    @classmethod
    def validate_component_name(cls, v: str) -> str:
        """Ensure component name is lowercase"""
        if not v.islower():
            raise ValueError('Component name must be lowercase')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "component": "rhetor",
                "version": "0.1.0",
                "timestamp": "2025-01-06T10:00:00Z",
                "uptime": 3600.5,
                "port": 8003,
                "registeredWithHermes": True,
                "dependencies": [
                    {
                        "name": "hermes",
                        "status": "healthy",
                        "message": "Connected"
                    }
                ],
                "metrics": {
                    "requests_total": 1500,
                    "active_connections": 5
                },
                "details": {
                    "providers_available": 6,
                    "models_loaded": ["gpt-4", "claude-3"]
                }
            }
        }
    )


class StatusResponse(TektonBaseModel):
    """Extended status response with more detailed information"""
    health: HealthCheckResponse = Field(..., description="Basic health information")
    component_info: ComponentInfo = Field(..., description="Component details")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Current configuration")
    capabilities: List[str] = Field(default_factory=list, description="Component capabilities")
    endpoints: Dict[str, str] = Field(default_factory=dict, description="Available endpoints")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "health": {
                    "status": "healthy",
                    "component": "rhetor",
                    "version": "0.1.0",
                    "timestamp": "2025-01-06T10:00:00Z",
                    "port": 8003,
                    "registeredWithHermes": True
                },
                "componentInfo": {
                    "name": "rhetor",
                    "version": "0.1.0",
                    "description": "LLM service for Tekton"
                },
                "configuration": {
                    "max_tokens": 4096,
                    "timeout": 30
                },
                "capabilities": [
                    "text-generation",
                    "streaming",
                    "multiple-providers"
                ],
                "endpoints": {
                    "health": "/health",
                    "generate": "/api/v1/generate",
                    "models": "/api/v1/models"
                }
            }
        }
    )


def create_health_response(
    component_name: str,
    port: int,
    version: str,
    status: HealthStatus = HealthStatus.HEALTHY,
    registered: bool = False,
    uptime: Optional[float] = None,
    dependencies: Optional[List[DependencyStatus]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    details: Optional[Dict[str, Any]] = None
) -> HealthCheckResponse:
    """
    Helper function to create a standardized health response.
    
    This maintains compatibility with the old health_check.py interface
    while using the new Pydantic v2 models.
    """
    return HealthCheckResponse(
        status=status,
        component=component_name,
        version=version,
        port=port,
        registered_with_hermes=registered,
        uptime=uptime,
        dependencies=dependencies or [],
        metrics=metrics or {},
        details=details or {}
    )