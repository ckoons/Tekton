"""
Shared logging setup utility for Tekton components.

This provides a simple, standardized way to set up logging across all Tekton
components, extracting the common patterns found throughout the codebase.

Usage:
    from shared.utils.logging_setup import setup_component_logging
    
    # Basic setup
    logger = setup_component_logging("mycomponent")
    
    # With custom level
    logger = setup_component_logging("mycomponent", log_level="DEBUG")
"""

import os
import logging
import sys
from typing import Optional, List


def setup_component_logging(
    component_name: str,
    log_level: Optional[str] = None,
    format_string: Optional[str] = None,
    suppress_external: bool = True
) -> logging.Logger:
    """
    Set up standardized logging for a Tekton component.
    
    This function:
    - Configures basic logging with consistent format
    - Sets log level from environment or parameter
    - Suppresses noisy external library logs
    - Returns a logger for the component
    
    Args:
        component_name: Name of the component (e.g., "athena", "hermes")
        log_level: Override log level (defaults to env var or INFO)
        format_string: Custom format string (defaults to Tekton standard)
        suppress_external: Whether to suppress external library logs
        
    Returns:
        Logger instance for the component
    """
    # Determine log level
    if log_level is None:
        # Check component-specific env var first
        env_var = f"{component_name.upper()}_LOG_LEVEL"
        log_level = os.environ.get(env_var)
        
        # Fall back to global Tekton log level
        if log_level is None:
            log_level = os.environ.get("TEKTON_LOG_LEVEL", "INFO")
    
    # Use standard format if not provided
    if format_string is None:
        # Import format utilities
        try:
            from shared.utils.tekton_log_formats import get_format_for_component, FORMATS
            # Check for environment variable override
            format_type = os.environ.get(f"{component_name.upper()}_LOG_FORMAT") or \
                         os.environ.get("TEKTON_LOG_FORMAT", "standard")
            if format_type in FORMATS:
                format_string = FORMATS[format_type]
            else:
                format_string = get_format_for_component(component_name)
        except ImportError:
            # Fallback if formats module not available
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure basic logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=format_string,
        stream=sys.stdout
    )
    
    # Suppress noisy external loggers
    if suppress_external:
        suppress_external_loggers()
    
    # Create and return component logger
    logger = logging.getLogger(component_name)
    logger.info(f"Initialized {component_name} logging at level {log_level}")
    
    return logger


def suppress_external_loggers(
    additional_loggers: Optional[List[str]] = None
) -> None:
    """
    Suppress noisy external library loggers.
    
    This reduces log spam from common libraries used in Tekton components.
    
    Args:
        additional_loggers: Additional logger names to suppress
    """
    # Common noisy loggers across Tekton components
    noisy_loggers = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "werkzeug",
        "httpx",
        "httpcore",
        "anthropic",
        "openai",
        "aiohttp",
        "asyncio",
        "watchdog",
        "fsevents",
        "urllib3",
        "requests",
        "botocore",
        "boto3",
        "sqlalchemy.engine",
        "alembic"
    ]
    
    # Add any additional loggers
    if additional_loggers:
        noisy_loggers.extend(additional_loggers)
    
    # Set all to WARNING or ERROR level
    for logger_name in noisy_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)
    
    # Special handling for particularly verbose loggers
    for logger_name in ["uvicorn.access", "werkzeug"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.ERROR)


def get_child_logger(parent_logger: logging.Logger, module_name: str) -> logging.Logger:
    """
    Get a child logger for a specific module within a component.
    
    Args:
        parent_logger: The parent component logger
        module_name: Name of the module
        
    Returns:
        Child logger instance
    """
    return parent_logger.getChild(module_name)


def setup_debug_logging() -> None:
    """
    Enable debug logging for all Tekton components.
    
    This is useful for development and troubleshooting.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        stream=sys.stdout
    )
    
    # Don't suppress external loggers in debug mode
    # But still reduce the most verbose ones
    for logger_name in ["uvicorn.access", "werkzeug"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)


# Convenience function for components that just want a simple logger
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    This is a simple wrapper around logging.getLogger() for components
    that don't need the full setup.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)