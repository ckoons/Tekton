"""
Standard endpoint implementations for Tekton components.

This module provides ready-to-use endpoint implementations for common API patterns.
"""
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from fastapi import HTTPException
from pydantic import BaseModel, Field

from tekton.models.base import TektonBaseModel


class ReadyResponse(TektonBaseModel):
    """Standard readiness check response."""
    ready: bool = Field(..., description="Whether the component is ready")
    component: str = Field(..., description="Component name")
    version: str = Field(..., description="Component version")
    initialization_time: float = Field(..., description="Time taken to initialize (seconds)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class EndpointInfo(TektonBaseModel):
    """Information about a single endpoint."""
    path: str = Field(..., description="Endpoint path")
    method: str = Field(..., description="HTTP method")
    description: str = Field(..., description="Endpoint description")
    tags: Optional[List[str]] = Field(default=None, description="Endpoint tags")


class DiscoveryResponse(TektonBaseModel):
    """Standard service discovery response."""
    component: str = Field(..., description="Component name")
    version: str = Field(..., description="Component version")
    description: str = Field(..., description="Component description")
    endpoints: List[EndpointInfo] = Field(..., description="Available endpoints")
    capabilities: List[str] = Field(..., description="Component capabilities")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Component dependencies")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


def create_ready_endpoint(
    component_name: str,
    component_version: str,
    start_time: float,
    readiness_check: Optional[Callable[[], bool]] = None
) -> Callable:
    """
    Create a ready endpoint for a component.
    
    Args:
        component_name: Name of the component
        component_version: Version of the component
        start_time: Component start time (from time.time())
        readiness_check: Optional function to check if component is ready
        
    Returns:
        Async endpoint function
    """
    async def ready_endpoint() -> ReadyResponse:
        """Check if the component is ready to serve requests."""
        # Default readiness is True unless a custom check is provided
        is_ready = True
        if readiness_check:
            try:
                is_ready = readiness_check()
            except Exception as e:
                is_ready = False
        
        initialization_time = time.time() - start_time
        
        if not is_ready:
            raise HTTPException(status_code=503, detail="Component not ready")
        
        return ReadyResponse(
            ready=is_ready,
            component=component_name,
            version=component_version,
            initialization_time=initialization_time
        )
    
    return ready_endpoint


def create_discovery_endpoint(
    component_name: str,
    component_version: str,
    component_description: str,
    endpoints: List[EndpointInfo],
    capabilities: List[str],
    dependencies: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Create a service discovery endpoint for a component.
    
    Args:
        component_name: Name of the component
        component_version: Version of the component
        component_description: Description of the component
        endpoints: List of available endpoints
        capabilities: List of component capabilities
        dependencies: Optional component dependencies
        metadata: Optional additional metadata
        
    Returns:
        Async endpoint function
    """
    async def discovery_endpoint() -> DiscoveryResponse:
        """Provide service discovery information."""
        return DiscoveryResponse(
            component=component_name,
            version=component_version,
            description=component_description,
            endpoints=endpoints,
            capabilities=capabilities,
            dependencies=dependencies or {},
            metadata=metadata or {}
        )
    
    return discovery_endpoint