"""
Component Client Package

This package provides a standardized client for interacting with Tekton components
through the Hermes service registry.
"""

from .exceptions import (
    ComponentError,
    ComponentNotFoundError,
    CapabilityNotFoundError,
    CapabilityInvocationError,
    ComponentUnavailableError,
    AuthenticationError,
    AuthorizationError
)
from .models import SecurityContext, RetryPolicy
from .client import ComponentClient
from .discovery import (
    discover_component,
    discover_components_by_type,
    discover_components_by_capability
)
from .factory import (
    create_client,
    create_security_context,
    create_retry_policy
)

__all__ = [
    "ComponentError",
    "ComponentNotFoundError",
    "CapabilityNotFoundError",
    "CapabilityInvocationError",
    "ComponentUnavailableError",
    "AuthenticationError",
    "AuthorizationError",
    "SecurityContext",
    "RetryPolicy",
    "ComponentClient",
    "discover_component",
    "discover_components_by_type",
    "discover_components_by_capability",
    "create_client",
    "create_security_context",
    "create_retry_policy"
]