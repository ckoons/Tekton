"""
Component Client Exceptions

This module provides exception classes for the component client.
"""

from typing import Any, Optional


class ComponentError(Exception):
    """Base error for component client operations."""
    pass


class ComponentNotFoundError(ComponentError):
    """Error raised when a component is not found."""
    pass


class CapabilityNotFoundError(ComponentError):
    """Error raised when a capability is not found."""
    pass


class CapabilityInvocationError(ComponentError):
    """Error raised when a capability invocation fails."""
    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(message)
        self.detail = detail


class ComponentUnavailableError(ComponentError):
    """Error raised when a component is unavailable."""
    pass


class AuthenticationError(ComponentError):
    """Error raised when authentication fails."""
    pass


class AuthorizationError(ComponentError):
    """Error raised when authorization fails."""
    pass