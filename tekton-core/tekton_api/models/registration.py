"""
Registration Models for Tekton

Provides standardized models for Hermes component registration.
These models ensure consistent registration across all Tekton components.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import Field, field_validator, ConfigDict, HttpUrl

from .base import TektonBaseModel
from .health import HealthStatus


class ComponentCapability(TektonBaseModel):
    """Capability definition for a component"""
    name: str = Field(..., description="Capability name")
    version: str = Field(..., description="Capability version")
    description: Optional[str] = Field(None, description="Capability description")
    endpoints: List[str] = Field(default_factory=list, description="Related endpoints")
    

class ComponentMetadata(TektonBaseModel):
    """Metadata for a registered component"""
    description: Optional[str] = Field(None, description="Component description")
    capabilities: List[ComponentCapability] = Field(default_factory=list, description="Component capabilities")
    dependencies: List[str] = Field(default_factory=list, description="Required component dependencies")
    tags: List[str] = Field(default_factory=list, description="Component tags")
    documentation_url: Optional[HttpUrl] = Field(None, description="Documentation URL")
    

class ComponentRegistration(TektonBaseModel):
    """Complete registration information for a component"""
    id: UUID = Field(default_factory=uuid4, description="Unique registration ID")
    name: str = Field(..., description="Component name")
    type: str = Field(..., description="Component type")
    version: str = Field(..., description="Component version")
    host: str = Field(..., description="Component host")
    port: int = Field(..., ge=1, le=65535, description="Component port")
    protocol: str = Field("http", description="Communication protocol")
    status: HealthStatus = Field(HealthStatus.UNKNOWN, description="Current status")
    metadata: ComponentMetadata = Field(default_factory=ComponentMetadata, description="Component metadata")
    registered_at: datetime = Field(default_factory=datetime.utcnow, description="Registration timestamp")
    last_heartbeat: Optional[datetime] = Field(None, description="Last heartbeat timestamp")
    heartbeat_interval: int = Field(30, ge=5, le=300, description="Expected heartbeat interval in seconds")
    
    @field_validator('name')
    @classmethod
    def validate_component_name(cls, v: str) -> str:
        """Ensure component name is lowercase"""
        if not v.islower():
            raise ValueError('Component name must be lowercase')
        return v
    
    @field_validator('type')
    @classmethod
    def validate_component_type(cls, v: str) -> str:
        """Ensure component type is lowercase"""
        return v.lower()
    
    @field_validator('protocol')
    @classmethod
    def validate_protocol(cls, v: str) -> str:
        """Validate communication protocol"""
        valid_protocols = {'http', 'https', 'ws', 'wss'}
        if v not in valid_protocols:
            raise ValueError(f'Protocol must be one of: {valid_protocols}')
        return v
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the component"""
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def is_healthy(self) -> bool:
        """Check if component is considered healthy"""
        return self.status == HealthStatus.HEALTHY
    
    @property
    def is_stale(self) -> bool:
        """Check if heartbeat is stale"""
        if not self.last_heartbeat:
            return True
        stale_threshold = self.heartbeat_interval * 3  # 3x the expected interval
        return (datetime.utcnow() - self.last_heartbeat).total_seconds() > stale_threshold
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "rhetor",
                "type": "llm-service",
                "version": "0.1.0",
                "host": "localhost",
                "port": 8003,
                "protocol": "http",
                "status": "healthy",
                "metadata": {
                    "description": "LLM service for Tekton",
                    "capabilities": [
                        {
                            "name": "text-generation",
                            "version": "1.0",
                            "endpoints": ["/api/v1/generate"]
                        }
                    ],
                    "dependencies": ["hermes"],
                    "tags": ["llm", "ai", "core"]
                },
                "registeredAt": "2025-01-06T10:00:00Z",
                "lastHeartbeat": "2025-01-06T10:05:00Z",
                "heartbeatInterval": 30
            }
        }
    )


class RegistrationRequest(TektonBaseModel):
    """Request to register a component with Hermes"""
    name: str = Field(..., description="Component name")
    type: str = Field(..., description="Component type")
    version: str = Field(..., description="Component version")
    host: str = Field("localhost", description="Component host")
    port: int = Field(..., ge=1, le=65535, description="Component port")
    protocol: str = Field("http", description="Communication protocol")
    metadata: Optional[ComponentMetadata] = Field(None, description="Component metadata")
    heartbeat_interval: int = Field(30, ge=5, le=300, description="Heartbeat interval in seconds")
    
    @field_validator('name')
    @classmethod
    def validate_component_name(cls, v: str) -> str:
        """Ensure component name is lowercase"""
        if not v.islower():
            raise ValueError('Component name must be lowercase')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "apollo",
                "type": "action-planner",
                "version": "0.1.0",
                "port": 8009,
                "metadata": {
                    "description": "Action planning and execution component",
                    "capabilities": [
                        {
                            "name": "action-planning",
                            "version": "1.0"
                        }
                    ],
                    "dependencies": ["hermes", "athena"]
                }
            }
        }
    )


class RegistrationResponse(TektonBaseModel):
    """Response from successful registration"""
    success: bool = Field(True, description="Registration success status")
    registration: ComponentRegistration = Field(..., description="Complete registration details")
    message: str = Field(..., description="Registration message")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "registration": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "apollo",
                    "type": "action-planner",
                    "version": "0.1.0",
                    "host": "localhost",
                    "port": 8009,
                    "status": "healthy"
                },
                "message": "Component 'apollo' registered successfully"
            }
        }
    )


class HeartbeatRequest(TektonBaseModel):
    """Request to send heartbeat to Hermes"""
    component_id: UUID = Field(..., description="Component registration ID")
    status: HealthStatus = Field(..., description="Current component status")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Component metrics")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "componentId": "550e8400-e29b-41d4-a716-446655440000",
                "status": "healthy",
                "metrics": {
                    "uptime": 3600,
                    "requests_processed": 1500,
                    "error_rate": 0.02
                }
            }
        }
    )


class HeartbeatResponse(TektonBaseModel):
    """Response from heartbeat update"""
    success: bool = Field(True, description="Heartbeat success status")
    component_id: UUID = Field(..., description="Component registration ID")
    next_heartbeat: datetime = Field(..., description="Expected next heartbeat time")
    message: Optional[str] = Field(None, description="Optional message")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "componentId": "550e8400-e29b-41d4-a716-446655440000",
                "nextHeartbeat": "2025-01-06T10:05:30Z",
                "message": "Heartbeat received"
            }
        }
    )