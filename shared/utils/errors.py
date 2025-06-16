"""
Shared error classes for Tekton components.

Provides a hierarchical error system with rich context for debugging
and monitoring across all Tekton services.
"""
from typing import Optional, Dict, Any, List


class TektonError(Exception):
    """
    Base error class for all Tekton components.
    
    Provides consistent error handling with component context,
    error codes, and additional details for debugging.
    """
    
    def __init__(
        self,
        message: str,
        component: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize TektonError.
        
        Args:
            message: Human-readable error message
            component: Name of the component where error occurred
            error_code: Optional error code for categorization
            details: Optional dict with additional error context
        """
        self.message = message
        self.component = component
        self.error_code = error_code
        self.details = details
        super().__init__(f"[{component}] {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "component": self.component,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }
    
    def is_same_error(self, other: 'TektonError') -> bool:
        """Check if two errors are the same type with same code."""
        return (
            isinstance(other, self.__class__) and
            self.component == other.component and
            self.error_code == other.error_code
        )


class StartupError(TektonError):
    """Error during component startup."""
    pass


class ShutdownError(TektonError):
    """Error during component shutdown."""
    pass


class ConfigurationError(TektonError):
    """Invalid configuration or missing required settings."""
    pass


class RegistrationError(TektonError):
    """Failed to register with Hermes or other services."""
    pass


class DependencyError(TektonError):
    """Required dependencies are not available."""
    
    def __init__(
        self,
        message: str,
        component: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None
    ):
        """
        Initialize DependencyError with list of failed dependencies.
        
        Args:
            dependencies: List of dependency names that failed
        """
        super().__init__(message, component, error_code, details)
        self.dependencies = dependencies or []


class ComponentError(TektonError):
    """Generic component-specific error."""
    pass


# Convenience functions for common error scenarios

def startup_timeout_error(component: str, timeout: int) -> StartupError:
    """Create standardized startup timeout error."""
    return StartupError(
        f"Startup timeout after {timeout}s",
        component,
        "STARTUP_TIMEOUT",
        {"timeout_seconds": timeout}
    )


def port_in_use_error(component: str, port: int) -> StartupError:
    """Create standardized port in use error."""
    return StartupError(
        f"Port {port} is already in use",
        component,
        "PORT_IN_USE",
        {"port": port}
    )


def hermes_registration_error(component: str, reason: str) -> RegistrationError:
    """Create standardized Hermes registration error."""
    return RegistrationError(
        f"Failed to register with Hermes: {reason}",
        component,
        "HERMES_REGISTRATION_FAILED",
        {"reason": reason}
    )


def missing_env_var_error(component: str, var_name: str) -> ConfigurationError:
    """Create standardized missing environment variable error."""
    return ConfigurationError(
        f"Required environment variable '{var_name}' is not set",
        component,
        "MISSING_ENV_VAR",
        {"variable": var_name}
    )


def invalid_config_error(
    component: str,
    config_key: str,
    expected: str,
    actual: Any
) -> ConfigurationError:
    """Create standardized invalid configuration error."""
    return ConfigurationError(
        f"Invalid configuration for '{config_key}': expected {expected}, got {actual}",
        component,
        "INVALID_CONFIG",
        {
            "config_key": config_key,
            "expected": expected,
            "actual": actual
        }
    )