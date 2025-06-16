"""
API Endpoints - REST API for the Hermes Unified Registration Protocol.

This module provides FastAPI endpoints for component registration,
heartbeat monitoring, and service discovery.
"""

import time
import logging
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field, ConfigDict

# Import from shared models
from tekton.models import (
    TektonBaseModel,
    RegistrationRequest,
    RegistrationResponse,
    HeartbeatRequest as BaseHeartbeatRequest,
    HeartbeatResponse as BaseHeartbeatResponse,
    HealthCheckResponse,
    create_health_response
)

from hermes.core.registration import (
    RegistrationManager,
    generate_component_id,
    format_component_info
)
from hermes.core.service_discovery import ServiceRegistry
from hermes.core.message_bus import MessageBus
from hermes.api.singleton_fix import get_shared_registration_manager

# Configure logger
logger = logging.getLogger(__name__)

# Import MCP router
from hermes.api.mcp_endpoints import mcp_router

# Create FastAPI app
app = FastAPI(
    title="Hermes Registration API",
    description="API for the Unified Registration Protocol",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get registration manager
def get_registration_manager():
    """Get the shared registration manager instance."""
    return get_shared_registration_manager()

# Pydantic models for request/response validation

class ComponentRegistrationRequest(TektonBaseModel):
    """Model for component registration requests."""
    component_id: Optional[str] = None
    name: str
    version: str
    component_type: str = Field(..., alias="type")
    endpoint: str
    capabilities: List[str] = []
    metadata: Dict[str, Any] = {}
    
    model_config = ConfigDict(populate_by_name=True)

class ComponentRegistrationResponse(TektonBaseModel):
    """Model for component registration responses."""
    success: bool
    component_id: str
    token: Optional[str] = None
    message: Optional[str] = None

class HeartbeatRequest(TektonBaseModel):
    """Model for heartbeat requests."""
    component_id: str
    status: Dict[str, Any] = {}

class HeartbeatResponse(TektonBaseModel):
    """Model for heartbeat responses."""
    success: bool
    timestamp: float
    message: Optional[str] = None

class ServiceQueryRequest(TektonBaseModel):
    """Model for service query requests."""
    capability: Optional[str] = None
    component_type: Optional[str] = None
    healthy_only: bool = False

class ServiceResponse(TektonBaseModel):
    """Model for service information."""
    component_id: str
    name: str
    version: str
    component_type: str = Field(..., alias="type")
    endpoint: str
    capabilities: List[str]
    metadata: Dict[str, Any]
    healthy: Optional[bool] = None
    last_heartbeat: Optional[float] = None
    
    model_config = ConfigDict(populate_by_name=True)

# API endpoints

@app.post("/register", response_model=ComponentRegistrationResponse)
async def register_component(
    registration: ComponentRegistrationRequest,
    manager: RegistrationManager = Depends(get_registration_manager)
):
    """
    Register a component with the Tekton ecosystem.
    
    This endpoint allows components to register their presence,
    capabilities, and connection information.
    """
    # Generate component ID if not provided
    component_id = registration.component_id
    if not component_id:
        component_id = generate_component_id(
            name=registration.name,
            component_type=registration.component_type
        )
    
    # Register component
    success, token_str = manager.register_component(
        component_id=component_id,
        name=registration.name,
        version=registration.version,
        component_type=registration.component_type,
        endpoint=registration.endpoint,
        capabilities=registration.capabilities,
        metadata=registration.metadata
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Registration failed")
    
    return ComponentRegistrationResponse(
        success=True,
        component_id=component_id,
        token=token_str,
        message="Component registered successfully"
    )

@app.post("/heartbeat", response_model=HeartbeatResponse)
async def send_heartbeat(
    heartbeat: HeartbeatRequest,
    x_authentication_token: str = Header(...),
    manager: RegistrationManager = Depends(get_registration_manager)
):
    """
    Send a heartbeat to indicate a component is still active.
    
    This endpoint allows components to maintain their active status
    and update their health information.
    """
    # Send heartbeat
    success = manager.send_heartbeat(
        component_id=heartbeat.component_id,
        token_str=x_authentication_token,
        status=heartbeat.status
    )
    
    if not success:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    return HeartbeatResponse(
        success=True,
        timestamp=time.time(),
        message="Heartbeat received"
    )

@app.post("/unregister")
async def unregister_component(
    component_id: str,
    x_authentication_token: str = Header(...),
    manager: RegistrationManager = Depends(get_registration_manager)
):
    """
    Unregister a component from the Tekton ecosystem.
    
    This endpoint allows components to cleanly remove themselves
    from the registry when shutting down.
    """
    # Unregister component
    success = manager.unregister_component(
        component_id=component_id,
        token_str=x_authentication_token
    )
    
    if not success:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    return {"success": True, "message": "Component unregistered successfully"}

@app.post("/query", response_model=List[ServiceResponse])
async def query_services(
    query: ServiceQueryRequest,
    manager: RegistrationManager = Depends(get_registration_manager)
):
    """
    Query available services based on criteria.
    
    This endpoint allows components to discover other components
    based on capabilities, type, and health status.
    """
    # Get service registry from manager
    registry = manager.service_registry
    
    # Query services
    if query.capability:
        # Find by capability
        services = registry.find_by_capability(query.capability)
    else:
        # Get all services
        all_services = registry.get_all_services()
        services = [
            {"id": service_id, **service_info}
            for service_id, service_info in all_services.items()
        ]
    
    # Filter by component type if specified
    if query.component_type:
        services = [
            service for service in services
            if service.get("metadata", {}).get("type") == query.component_type
        ]
    
    # Filter by health status if requested
    if query.healthy_only:
        services = [
            service for service in services
            if service.get("healthy", False)
        ]
    
    # Format response
    response = []
    for service in services:
        component_id = service.get("id")
        response.append(ServiceResponse(
            component_id=component_id,
            name=service.get("name", "Unknown"),
            version=service.get("version", "Unknown"),
            type=service.get("metadata", {}).get("type", "Unknown"),
            endpoint=service.get("endpoint", ""),
            capabilities=service.get("capabilities", []),
            metadata=service.get("metadata", {}),
            healthy=service.get("healthy"),
            last_heartbeat=service.get("last_heartbeat")
        ))
    
    return response

@app.get("/components")
async def list_components(
    registration_manager: RegistrationManager = Depends(get_registration_manager),
    capability: Optional[str] = None,
    component_type: Optional[str] = None,
    healthy_only: bool = False
):
    """
    List all registered components.
    
    Query parameters:
    - capability: Filter by capability (optional)
    - component_type: Filter by component type (optional)
    - healthy_only: Only show healthy components (default: false)
    
    Returns a list of all registered components with their current status.
    """
    # Get all registered components from the service registry
    all_components = registration_manager.service_registry.get_all_services()
    
    # Filter based on query parameters
    filtered_components = []
    
    for component_id, component_info in all_components.items():
        # Apply filters
        if capability and capability not in component_info.get("capabilities", []):
            continue
            
        if component_type and component_info.get("type") != component_type:
            continue
            
        if healthy_only:
            # Check if component is healthy (has recent heartbeat)
            last_heartbeat = component_info.get("last_heartbeat", 0)
            current_time = time.time()
            # Consider healthy if heartbeat within last 60 seconds
            if current_time - last_heartbeat > 60:
                continue
        
        # Add component to results
        filtered_components.append({
            "component_id": component_id,
            "name": component_info.get("name"),
            "version": component_info.get("version"),
            "type": component_info.get("type"),
            "port": component_info.get("port"),
            "status": component_info.get("status", "unknown"),
            "capabilities": component_info.get("capabilities", []),
            "endpoint": component_info.get("endpoint"),
            "last_heartbeat": component_info.get("last_heartbeat"),
            "registered_at": component_info.get("registered_at"),
            "metadata": component_info.get("metadata", {})
        })
    
    return {
        "total": len(filtered_components),
        "components": filtered_components
    }

@app.get("/components/{component_name}")
async def get_component_by_name(
    component_name: str,
    registration_manager: RegistrationManager = Depends(get_registration_manager)
):
    """
    Get information about a specific component by name.
    
    Returns detailed information about the component if it exists.
    """
    # Search for component by name
    all_components = registration_manager.service_registry.get_all_services()
    
    for component_id, component_info in all_components.items():
        if component_info.get("name") == component_name:
            return {
                "component_id": component_id,
                "name": component_info.get("name"),
                "version": component_info.get("version"),
                "type": component_info.get("type"),
                "port": component_info.get("port"),
                "status": component_info.get("status", "unknown"),
                "capabilities": component_info.get("capabilities", []),
                "endpoint": component_info.get("endpoint"),
                "last_heartbeat": component_info.get("last_heartbeat"),
                "registered_at": component_info.get("registered_at"),
                "metadata": component_info.get("metadata", {})
            }
    
    raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")

@app.get("/health", response_model=HealthCheckResponse)
async def health_check(
    manager: RegistrationManager = Depends(get_registration_manager)
):
    """
    Check the health of the registration service.
    
    This endpoint allows monitoring systems to verify that
    the registration service is operating correctly.
    """
    # Check registration manager status
    registered_count = len(manager.registry) if hasattr(manager, 'registry') else 0
    
    return create_health_response(
        component_name="hermes",
        port=8001,
        version="0.1.0",
        status="healthy",
        registered=True,  # Hermes is self-registered
        details={
            "registered_components": registered_count,
            "uptime": time.time() - getattr(app.state, 'start_time', time.time())
        }
    )

# Startup and shutdown events

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Registration API starting up")
    # Track startup time for health checks
    app.state.start_time = time.time()
    # In a real implementation, this would initialize the registration manager
    # and any other required services

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Registration API shutting down")
    # In a real implementation, this would clean up resources
    pass

# Include MCP router
app.include_router(mcp_router)