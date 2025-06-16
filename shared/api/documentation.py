"""
OpenAPI documentation configuration for Tekton components.

This module provides utilities for consistent API documentation setup.
"""
from typing import Dict, Any, Optional, List


def get_openapi_configuration(
    component_name: str,
    component_version: str,
    component_description: Optional[str] = None,
    contact: Optional[Dict[str, str]] = None,
    license_info: Optional[Dict[str, str]] = None,
    servers: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Get standard OpenAPI configuration for a Tekton component.
    
    Args:
        component_name: Name of the component
        component_version: Version of the component
        component_description: Optional component description
        contact: Optional contact information
        license_info: Optional license information
        servers: Optional server configurations
        
    Returns:
        Dictionary of FastAPI configuration parameters
    """
    # Default description if none provided
    if not component_description:
        component_description = f"{component_name} - Tekton Component"
    
    # Default contact information
    if not contact:
        contact = {
            "name": "Tekton Team",
            "url": "https://github.com/Tekton",
            "email": "support@tekton.io"
        }
    
    # Default license
    if not license_info:
        license_info = {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    
    # Build configuration
    config = {
        "title": f"{component_name} API",
        "description": component_description,
        "version": component_version,
        "docs_url": "/api/v1/docs",
        "redoc_url": "/api/v1/redoc",
        "openapi_url": "/api/v1/openapi.json",
        "openapi_tags": get_default_tags(component_name),
        "contact": contact,
        "license_info": license_info
    }
    
    # Add servers if provided
    if servers:
        config["servers"] = servers
    
    return config


def get_default_tags(component_name: str) -> List[Dict[str, str]]:
    """
    Get default OpenAPI tags for a component.
    
    Args:
        component_name: Name of the component
        
    Returns:
        List of tag definitions
    """
    return [
        {
            "name": "Infrastructure",
            "description": "Health checks, readiness probes, and system endpoints"
        },
        {
            "name": f"{component_name} API v1",
            "description": f"Main API endpoints for {component_name}"
        },
        {
            "name": "Discovery",
            "description": "Service discovery and capability information"
        }
    ]


def add_custom_responses(responses: Dict[int, Dict[str, str]]) -> Dict[int, Dict[str, Any]]:
    """
    Add standard error response schemas to custom responses.
    
    Args:
        responses: Custom response definitions
        
    Returns:
        Enhanced response definitions with schemas
    """
    standard_responses = {
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    }
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    }
                }
            }
        },
        503: {
            "description": "Service Unavailable",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    }
                }
            }
        }
    }
    
    # Merge custom responses with standards
    for status_code, response in responses.items():
        if status_code in standard_responses:
            standard_responses[status_code]["description"] = response.get(
                "description", 
                standard_responses[status_code]["description"]
            )
    
    return standard_responses