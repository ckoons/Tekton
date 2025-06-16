"""
Standard router patterns for Tekton components.

This module provides utilities for creating consistent API routers across all components.
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel


class StandardRouters(BaseModel):
    """Container for standard routers used by Tekton components."""
    root: APIRouter
    v1: APIRouter
    
    class Config:
        arbitrary_types_allowed = True


def create_standard_routers(
    component_name: str,
    include_mcp: bool = True,
    additional_tags: Optional[Dict[str, str]] = None
) -> StandardRouters:
    """
    Create standard routers for a Tekton component.
    
    Args:
        component_name: Name of the component
        include_mcp: Whether to include MCP router mount point
        additional_tags: Additional tags for OpenAPI documentation
        
    Returns:
        StandardRouters containing root and v1 routers
    """
    # Create root router for infrastructure endpoints
    root_router = APIRouter(
        tags=["Infrastructure"],
        responses={
            503: {"description": "Service unavailable"},
            500: {"description": "Internal server error"}
        }
    )
    
    # Create versioned router for business logic
    v1_router = APIRouter(
        prefix="/api/v1",
        tags=[f"{component_name} API v1"],
        responses={
            400: {"description": "Bad request"},
            404: {"description": "Not found"},
            500: {"description": "Internal server error"}
        }
    )
    
    # Add any additional tags
    if additional_tags:
        for tag, description in additional_tags.items():
            v1_router.tags.append(tag)
    
    return StandardRouters(root=root_router, v1=v1_router)


def mount_standard_routers(app, routers: StandardRouters) -> None:
    """
    Mount standard routers to a FastAPI application.
    
    Args:
        app: FastAPI application instance
        routers: StandardRouters instance to mount
    """
    app.include_router(routers.root)
    app.include_router(routers.v1)