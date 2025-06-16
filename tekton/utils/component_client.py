"""
Component Client - Base client for Tekton components.

This module provides a standardized client for interacting with Tekton components
through the Hermes service registry.

This file re-exports functionality from the modular client package.
"""

# Re-export from modular implementation
from .client.exceptions import (
    ComponentError,
    ComponentNotFoundError,
    CapabilityNotFoundError,
    CapabilityInvocationError,
    ComponentUnavailableError,
    AuthenticationError,
    AuthorizationError
)
from .client.models import SecurityContext, RetryPolicy
from .client.client import ComponentClient
from .client.discovery import (
    discover_component,
    discover_components_by_type,
    discover_components_by_capability
)
from .client.factory import (
    create_client,
    create_security_context,
    create_retry_policy
)

# Type variables
from typing import TypeVar
T_Client = TypeVar("T_Client", bound=ComponentClient)

# For backward compatibility
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
    "create_retry_policy",
    "T_Client"
]