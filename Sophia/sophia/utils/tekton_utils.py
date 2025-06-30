"""
Tekton Shared Utilities for Sophia

This module provides integration with Tekton's shared utility libraries,
enabling standardized access to HTTP, configuration, logging, WebSocket,
registration, error handling, lifecycle management, authentication,
context management, and CLI functionalities.
"""

import os
import sys
import importlib
import logging
import asyncio
import inspect
import functools
from typing import Dict, Any, Optional, Union, List, Callable, Awaitable, TypeVar, cast

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config

# Type variables for function signatures
T = TypeVar('T')

# Set up initial logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sophia.utils.tekton_utils")

# Available utilities
AVAILABLE_UTILS = [
    "tekton_http",
    "tekton_config",
    "tekton_logging",
    # "tekton_websocket",  # Removed - unused implementation
    "tekton_registration",
    "tekton_errors",
    "tekton_lifecycle",
    "tekton_auth",
    "tekton_context",
    "tekton_cli"
]

# Core settings
SOPHIA_COMPONENT_ID = "sophia"
SOPHIA_COMPONENT_NAME = "Sophia"
SOPHIA_COMPONENT_DESCRIPTION = "Machine learning and continuous improvement component for Tekton"
SOPHIA_COMPONENT_VERSION = "0.1.0"

# Global dictionary to store imported utilities
tekton_utils = {}

def import_tekton_utils() -> Dict[str, Any]:
    """
    Import all available Tekton utilities.
    
    Returns:
        Dictionary mapping utility names to imported modules
    """
    global tekton_utils
    
    if tekton_utils:
        return tekton_utils
        
    logger.info("Importing Tekton shared utilities...")
    
    for util_name in AVAILABLE_UTILS:
        try:
            module_path = f"tekton.utils.{util_name}"
            tekton_utils[util_name] = importlib.import_module(module_path)
            logger.info(f"Successfully imported {util_name}")
        except ImportError as e:
            logger.warning(f"Could not import {util_name}: {e}")
            tekton_utils[util_name] = None
            
    return tekton_utils
    
def has_util(util_name: str) -> bool:
    """
    Check if a specific utility is available.
    
    Args:
        util_name: Name of the utility to check
        
    Returns:
        True if the utility is available
    """
    if not tekton_utils:
        import_tekton_utils()
        
    return util_name in tekton_utils and tekton_utils[util_name] is not None
    
def get_util(util_name: str) -> Any:
    """
    Get a specific utility module.
    
    Args:
        util_name: Name of the utility to get
        
    Returns:
        Utility module or None if not available
    """
    if not tekton_utils:
        import_tekton_utils()
        
    return tekton_utils.get(util_name)
    
# Configuration functions

def get_config(key: str, default: Any = None) -> Any:
    """
    Get a configuration value using tekton_config if available.
    
    Args:
        key: Config key to retrieve
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    if has_util("tekton_config"):
        return tekton_utils["tekton_config"].get_config(key, default)
    else:
        # Fallback to environment variables
        env_key = key.upper().replace(".", "_")
        return os.environ.get(env_key, default)
        
def get_sophia_port() -> int:
    """
    Get the port for Sophia, following Single Port Architecture.
    
    Returns:
        Port number
    """
    config = get_component_config()
    try:
        return config.sophia.port
    except (AttributeError, TypeError):
        return int(os.environ.get("SOPHIA_PORT"))
    
def get_sophia_base_url() -> str:
    """
    Get the base URL for Sophia.
    
    Returns:
        Base URL
    """
    port = get_sophia_port()
    host = get_config("SOPHIA_HOST", "localhost")
    return f"http://{host}:{port}"
    
# Logging functions

def setup_logging(component_name: str = "sophia") -> None:
    """
    Set up logging using tekton_logging if available.

    Args:
        component_name: Name of the component for logging
    """
    if has_util("tekton_logging"):
        tekton_utils["tekton_logging"].setup_logging(component_name)
    else:
        # Fallback logging setup
        level_name = get_config("SOPHIA_LOG_LEVEL", "INFO")
        level = getattr(logging, level_name, logging.INFO)
        
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger using tekton_logging if available.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    if has_util("tekton_logging"):
        return tekton_utils["tekton_logging"].get_logger(name)
    else:
        return logging.getLogger(name)
        
# HTTP client functions

def create_http_client(
    base_url: Optional[str] = None,
    timeout: float = 30.0,
    headers: Optional[Dict[str, str]] = None
) -> Any:
    """
    Create an HTTP client using tekton_http if available.
    
    Args:
        base_url: Base URL for the client
        timeout: Request timeout in seconds
        headers: Default headers for requests
        
    Returns:
        HTTP client
    """
    if has_util("tekton_http"):
        return tekton_utils["tekton_http"].create_client(
            base_url=base_url,
            timeout=timeout,
            headers=headers
        )
    else:
        # Fallback to returning None - caller should handle this
        logger.warning("tekton_http not available, client creation failed")
        return None
        
# Error handling functions

def create_error(
    error_type: str,
    message: str,
    status_code: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
) -> Exception:
    """
    Create a standardized error using tekton_errors if available.
    
    Args:
        error_type: Type of error
        message: Error message
        status_code: HTTP status code for the error
        details: Additional error details
        
    Returns:
        Exception instance
    """
    if has_util("tekton_errors"):
        return tekton_utils["tekton_errors"].create_error(
            error_type=error_type,
            message=message,
            status_code=status_code,
            details=details
        )
    else:
        # Create a basic exception
        exception_class = {
            "not_found": FileNotFoundError,
            "invalid_request": ValueError,
            "unauthorized": PermissionError,
            "service_unavailable": ConnectionError
        }.get(error_type, Exception)
        
        return exception_class(message)
        
def format_error_response(
    error: Exception,
    include_traceback: bool = False
) -> Dict[str, Any]:
    """
    Format an error for API response using tekton_errors if available.
    
    Args:
        error: Exception to format
        include_traceback: Whether to include traceback in response
        
    Returns:
        Error response dictionary
    """
    if has_util("tekton_errors"):
        return tekton_utils["tekton_errors"].format_error_response(
            error=error,
            include_traceback=include_traceback
        )
    else:
        # Basic error response format
        return {
            "error": str(error),
            "error_type": error.__class__.__name__,
            "success": False
        }
        
# WebSocket functions

def create_websocket_manager() -> Any:
    """
    Create a WebSocket manager using tekton_websocket if available.
    
    Returns:
        WebSocket manager or None if not available
    """
    # tekton_websocket has been removed - it was an unused implementation
    # if has_util("tekton_websocket"):
    #     return tekton_utils["tekton_websocket"].WebSocketManager()
    # else:
    logger.warning("tekton_websocket not available (removed - unused implementation)")
    return None
        
# Component lifecycle functions

def get_lifecycle_manager(component_id: str = SOPHIA_COMPONENT_ID) -> Any:
    """
    Get a lifecycle manager using tekton_lifecycle if available.
    
    Args:
        component_id: ID of the component
        
    Returns:
        Lifecycle manager or None if not available
    """
    if has_util("tekton_lifecycle"):
        return tekton_utils["tekton_lifecycle"].ComponentLifecycle(component_id)
    else:
        logger.warning("tekton_lifecycle not available")
        return None
        
# Registration functions

def register_with_hermes(
    component_id: str = SOPHIA_COMPONENT_ID,
    component_name: str = SOPHIA_COMPONENT_NAME,
    component_description: str = SOPHIA_COMPONENT_DESCRIPTION,
    component_version: str = SOPHIA_COMPONENT_VERSION,
    component_type: str = "analysis",
    host: Optional[str] = None,
    port: Optional[int] = None,
    capabilities: Optional[List[str]] = None,
    dependencies: Optional[List[str]] = None,
    hermes_url: Optional[str] = None
) -> bool:
    """
    Register Sophia with Hermes using tekton_registration if available.
    
    Args:
        component_id: ID of the component
        component_name: Name of the component
        component_description: Description of the component
        component_version: Version of the component
        component_type: Type of component
        host: Host for the component
        port: Port for the component
        capabilities: List of capabilities provided by the component
        dependencies: List of dependencies required by the component
        hermes_url: URL for Hermes registration service
        
    Returns:
        True if registration was successful
    """
    if has_util("tekton_registration"):
        # Get values with defaults
        host = host or os.environ.get("SOPHIA_HOST", "localhost")
        port = port or get_sophia_port()
        hermes_url = hermes_url or os.environ.get("HERMES_URL", "http://localhost:8001")
        
        capabilities = capabilities or [
            "metrics", "analysis", "experiments", "recommendations", 
            "intelligence", "research", "ml"
        ]
        
        dependencies = dependencies or ["hermes"]
        
        # Create endpoints
        http_prefix = f"http://{host}:{port}"
        ws_prefix = f"ws://{host}:{port}"
        
        endpoints = {
            "http": {
                "base": http_prefix,
                "health": f"{http_prefix}/health",
                "api": f"{http_prefix}/api"
            },
            "ws": {
                "base": ws_prefix,
                "events": f"{ws_prefix}/ws"
            }
        }
        
        # Build registration data
        registration_data = {
            "component_id": component_id,
            "name": component_name,
            "description": component_description,
            "version": component_version,
            "component_type": component_type,
            "host": host,
            "port": port,
            "endpoints": endpoints,
            "capabilities": capabilities,
            "dependencies": dependencies
        }
        
        return tekton_utils["tekton_registration"].register_component(
            hermes_url=hermes_url,
            registration_data=registration_data
        )
    else:
        logger.warning("tekton_registration not available, using fallback registration")
        
        # Try to use custom registration script
        try:
            from sophia.scripts.register_with_hermes import register_component
            host = host or os.environ.get("SOPHIA_HOST", "localhost")
            port = port or get_sophia_port()
            hermes_url = hermes_url or os.environ.get("HERMES_URL", "http://localhost:8001")
            
            return register_component(
                component_id=component_id,
                name=component_name,
                description=component_description,
                version=component_version,
                host=host,
                port=port,
                hermes_url=hermes_url
            )
        except ImportError:
            logger.error("Failed to import custom registration script")
            return False
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False
            
# Coroutine compatibility
def async_decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """
    A replacement for deprecated asyncio.coroutine decorator.
    This decorator properly handles async functions in Python 3.12+.
    
    Args:
        func: The async function to decorate
        
    Returns:
        Decorated function
    """
    if not asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return func

# Initialize the utilities
import_tekton_utils()