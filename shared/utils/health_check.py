"""
Standardized Health Check Response for Tekton Components

This module now imports from the new Pydantic v2 models in tekton.models.
It maintains backward compatibility by re-exporting the same interface.
"""
from typing import Dict, Any, Optional

# Import from the new shared models
from tekton.models.health import (
    HealthCheckResponse,
    HealthStatus,
    create_health_response as _create_health_response
)

# Re-export for backward compatibility
__all__ = ['HealthCheckResponse', 'create_health_response']


def create_health_response(
    component_name: str,
    port: int,
    version: str,
    status: str = "healthy",
    registered: bool = False,
    details: Optional[Dict[str, Any]] = None
) -> HealthCheckResponse:
    """
    Helper function to create a standardized health response.
    
    This wrapper maintains backward compatibility with the string status parameter
    while the new models use the HealthStatus enum.
    """
    # Convert string status to HealthStatus enum
    health_status = HealthStatus.HEALTHY
    if status.lower() == "degraded":
        health_status = HealthStatus.DEGRADED
    elif status.lower() == "unhealthy":
        health_status = HealthStatus.UNHEALTHY
    elif status.lower() == "unknown":
        health_status = HealthStatus.UNKNOWN
    
    return _create_health_response(
        component_name=component_name,
        port=port,
        version=version,
        status=health_status,
        registered=registered,
        details=details
    )