"""
Shared API utilities for Tekton components.

This module provides standardized API patterns for consistency across all Tekton components.
"""

from .routers import create_standard_routers, mount_standard_routers, StandardRouters
from .endpoints import (
    create_ready_endpoint,
    create_discovery_endpoint,
    ReadyResponse,
    DiscoveryResponse,
    EndpointInfo
)
from .documentation import get_openapi_configuration

__all__ = [
    'create_standard_routers',
    'mount_standard_routers',
    'StandardRouters',
    'create_ready_endpoint',
    'create_discovery_endpoint',
    'ReadyResponse',
    'DiscoveryResponse',
    'EndpointInfo',
    'get_openapi_configuration'
]