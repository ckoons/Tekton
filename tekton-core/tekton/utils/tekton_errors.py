"""
Tekton Error Handling

This module provides a standardized error hierarchy for Tekton components.
All Tekton components should use these error classes for consistent error
handling and reporting across the system.

Usage:
    from tekton.utils.tekton_errors import (
        TektonError,
        ConfigurationError,
        ConnectionError,
        raise_with_traceback
    )
    
    try:
        # Component logic
    except SomeException as e:
        raise ConfigurationError("Failed to load configuration") from e
"""

import sys
import logging
import traceback
from typing import Dict, Any, Optional, Type, TypeVar, Callable, Union, List

# Set up logger
logger = logging.getLogger(__name__)

# Base error class
class TektonError(Exception):
    """Base class for all Tekton errors."""
    
    def __init__(self, message: str, component_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a Tekton error.
        
        Args:
            message: Error message
            component_id: ID of the component that raised the error
            details: Additional error details (e.g., request parameters, IDs)
        """
        self.message = message
        self.component_id = component_id
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the error
        """
        result = {
            "error": self.__class__.__name__,
            "message": self.message,
            "type": "tekton.error"
        }
        
        if self.component_id:
            result["component_id"] = self.component_id
            
        if self.details:
            result["details"] = self.details
            
        return result
    
    def log(self, logger: Optional[logging.Logger] = None, level: int = logging.ERROR) -> None:
        """
        Log this error.
        
        Args:
            logger: Logger to use (defaults to module logger)
            level: Logging level
        """
        log = logger or logging.getLogger(__name__)
        
        log_message = f"{self.__class__.__name__}: {self.message}"
        if self.component_id:
            log_message = f"[{self.component_id}] {log_message}"
            
        log.log(level, log_message, exc_info=sys.exc_info())


# Configuration errors
class ConfigurationError(TektonError):
    """Raised when there is an error in configuration."""
    pass


class ConfigKeyError(ConfigurationError):
    """Raised when a required configuration key is missing."""
    pass


class ConfigValueError(ConfigurationError):
    """Raised when a configuration value is invalid."""
    pass


class ConfigurationFileError(ConfigurationError):
    """Raised when there is an error with a configuration file."""
    pass


# Connection errors
class ConnectionError(TektonError):
    """Raised when a connection to a service fails."""
    pass


class ServiceUnavailableError(ConnectionError):
    """Raised when a required service is unavailable."""
    pass


class ServiceTimeoutError(ConnectionError):
    """Raised when a service request times out."""
    pass


# Authentication and authorization errors
class AuthenticationError(TektonError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(TektonError):
    """Raised when authorization fails (user doesn't have required permissions)."""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when an authentication token has expired."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when invalid credentials are provided."""
    pass


# HTTP errors
class TektonHTTPError(TektonError):
    """Base class for HTTP-related errors."""
    
    def __init__(
        self,
        message: str,
        component_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        url: Optional[str] = None,
        method: Optional[str] = None
    ):
        """
        Initialize an HTTP error.
        
        Args:
            message: Error message
            component_id: ID of the component that raised the error
            details: Additional error details
            status_code: HTTP status code
            url: Request URL
            method: HTTP method
        """
        self.status_code = status_code
        self.url = url
        self.method = method
        
        # Add to details
        full_details = details.copy() if details else {}
        if status_code:
            full_details["status_code"] = status_code
        if url:
            full_details["url"] = url
        if method:
            full_details["method"] = method
            
        super().__init__(message, component_id, full_details)


class TektonConnectionError(TektonHTTPError):
    """Raised when a connection to an HTTP service fails."""
    pass


class TektonTimeoutError(TektonHTTPError):
    """Raised when an HTTP request times out."""
    pass


class TektonAuthenticationError(TektonHTTPError):
    """Raised when HTTP authentication fails (401)."""
    pass


class TektonAuthorizationError(TektonHTTPError):
    """Raised when HTTP authorization fails (403)."""
    pass


class TektonNotFoundError(TektonHTTPError):
    """Raised when an HTTP resource is not found (404)."""
    pass


class TektonServerError(TektonHTTPError):
    """Raised when an HTTP server error occurs (5xx)."""
    pass


class TektonClientError(TektonHTTPError):
    """Raised when an HTTP client error occurs (4xx) not covered by other classes."""
    pass


class TektonRequestError(TektonHTTPError):
    """Raised when an HTTP request is invalid."""
    pass


# Component-specific errors
class ComponentNotFoundError(TektonError):
    """Raised when a component is not found in service registry."""
    pass


class ComponentNotReadyError(TektonError):
    """Raised when a component is not ready to handle requests."""
    pass


class ComponentUnavailableError(ConnectionError):
    """Raised when a component is unavailable."""
    pass


class CapabilityNotFoundError(TektonError):
    """Raised when a component capability is not found."""
    pass


class CapabilityInvocationError(TektonError):
    """Raised when invoking a component capability fails."""
    pass


# Data errors
class DataValidationError(TektonError):
    """Raised when data validation fails."""
    pass


class DataNotFoundError(TektonError):
    """Raised when requested data is not found."""
    pass


class DataConflictError(TektonError):
    """Raised when there is a data conflict (e.g., unique constraint violation)."""
    pass


# Lifecycle errors
class InitializationError(TektonError):
    """Raised when component initialization fails."""
    pass


class LifecycleError(TektonError):
    """Raised when a component lifecycle operation fails."""
    pass


class ShutdownError(LifecycleError):
    """Raised when component shutdown fails."""
    pass


# Resource errors
class ResourceError(TektonError):
    """Raised when there is an error with a resource."""
    pass


class ResourceUnavailableError(ResourceError):
    """Raised when a resource is unavailable."""
    pass


class ResourceLimitExceededError(ResourceError):
    """Raised when a resource limit is exceeded."""
    pass


class ResourceConflictError(ResourceError):
    """Raised when there is a resource conflict."""
    pass


# Context errors
class ContextError(TektonError):
    """Raised when there is an error with a context."""
    pass


class ContextNotFoundError(ContextError):
    """Raised when a context is not found."""
    pass


class ContextValidationError(ContextError):
    """Raised when context validation fails."""
    pass


# WebSocket errors
class WebSocketError(TektonError):
    """Raised when there is a WebSocket error."""
    pass


class WebSocketConnectionError(WebSocketError):
    """Raised when a WebSocket connection fails."""
    pass


class WebSocketProtocolError(WebSocketError):
    """Raised when there is a WebSocket protocol error."""
    pass


class WebSocketClosedError(WebSocketError):
    """Raised when a WebSocket connection is closed unexpectedly."""
    pass


# Type variable for generic type constraints
T = TypeVar('T')


# Utility functions for error handling
def raise_with_traceback(
    error_cls: Type[TektonError],
    message: str,
    component_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Raise an error with the current traceback.
    
    Args:
        error_cls: Error class
        message: Error message
        component_id: Component ID
        details: Additional error details
        
    Raises:
        The specified error class with the current traceback
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error = error_cls(message, component_id, details)
    
    if exc_type is not None and exc_value is not None and exc_traceback is not None:
        raise error.with_traceback(exc_traceback)
    else:
        raise error


def handle_exception(
    exception: Exception,
    default_error_cls: Type[TektonError] = TektonError,
    default_message: str = "An unexpected error occurred",
    component_id: Optional[str] = None,
    error_mapping: Optional[Dict[Type[Exception], Type[TektonError]]] = None,
    log_level: int = logging.ERROR,
    re_raise: bool = True
) -> Optional[TektonError]:
    """
    Handle an exception by mapping it to a Tekton error.
    
    Args:
        exception: The exception to handle
        default_error_cls: Default error class if no mapping found
        default_message: Default error message if none provided
        component_id: Component ID
        error_mapping: Mapping from exception types to Tekton error classes
        log_level: Level to log the error at
        re_raise: Whether to re-raise the error
        
    Returns:
        The mapped Tekton error, or None if re_raise is True
        
    Raises:
        The mapped Tekton error if re_raise is True
    """
    # Default error mapping
    mapping = {
        ValueError: ConfigValueError,
        KeyError: ConfigKeyError,
        FileNotFoundError: ConfigurationFileError,
        PermissionError: AuthorizationError,
        TimeoutError: ServiceTimeoutError,
        ConnectionError: ConnectionError,
        OSError: ResourceError
    }
    
    # Update with provided mapping
    if error_mapping:
        mapping.update(error_mapping)
    
    # If the exception is already a TektonError, use it
    if isinstance(exception, TektonError):
        error = exception
        # Update component_id if not already set
        if component_id and not error.component_id:
            error.component_id = component_id
    else:
        # Find the most specific matching error class
        error_cls = default_error_cls
        for exc_type, err_cls in mapping.items():
            if isinstance(exception, exc_type):
                error_cls = err_cls
                break
        
        # Create the error
        message = str(exception) or default_message
        error = error_cls(message, component_id)
    
    # Log the error
    logger.log(log_level, f"{error.__class__.__name__}: {error.message}")
    if log_level >= logging.ERROR:
        logger.debug(f"Error details: {traceback.format_exc()}")
    
    # Re-raise or return
    if re_raise:
        raise error from exception
    return error


def create_error_response(
    error: Union[TektonError, Exception],
    include_traceback: bool = False,
    component_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create an error response dictionary suitable for HTTP responses.
    
    Args:
        error: The error to convert
        include_traceback: Whether to include the traceback
        component_id: Component ID to use if not in the error
        
    Returns:
        Error response dictionary
    """
    if isinstance(error, TektonError):
        response = error.to_dict()
        # Update component_id if provided and not in error
        if component_id and not error.component_id:
            response["component_id"] = component_id
    else:
        # Convert standard exception to error response
        response = {
            "error": error.__class__.__name__,
            "message": str(error) or "An unexpected error occurred",
            "type": "error"
        }
        if component_id:
            response["component_id"] = component_id
    
    # Add traceback if requested
    if include_traceback:
        response["traceback"] = traceback.format_exc()
    
    return response


# Error handlers for common operations
def safe_execute(
    func: Callable[..., T],
    *args: Any,
    default: Optional[T] = None,
    error_cls: Type[TektonError] = TektonError,
    error_message: str = "Operation failed",
    component_id: Optional[str] = None,
    log_error: bool = True,
    re_raise: bool = False,
    **kwargs: Any
) -> Optional[T]:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Arguments to pass to the function
        default: Default value to return on error
        error_cls: Error class to use
        error_message: Error message
        component_id: Component ID
        log_error: Whether to log the error
        re_raise: Whether to re-raise the error as a Tekton error
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Function result or default value on error
        
    Raises:
        Specified error class if re_raise is True
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(f"{error_message}: {str(e)}", exc_info=True)
        
        if re_raise:
            # Convert to Tekton error
            if isinstance(e, TektonError):
                raise
            else:
                raise error_cls(f"{error_message}: {str(e)}", component_id) from e
        
        return default