"""
Logging Helper - Simplified integration with Centralized Logging System.

This module provides helper functions and utilities for Tekton components to
easily integrate with the Centralized Logging System.
"""

import os
import sys
import logging
import time
import traceback
from typing import Dict, Any, Optional, Union, List, Callable

# Import core logging components
from hermes.core.logging import (
    LogLevel, LogEntry, Logger, LogManager,
    init_logging, get_logger
)

# Global logger cache
_logger_cache: Dict[str, Logger] = {}


def setup_logging(
    component: str,
    client_id: Optional[str] = None,
    storage_path: Optional[str] = None,
    console_output: bool = True,
    console_level: Union[LogLevel, str] = LogLevel.INFO
) -> Logger:
    """
    Set up logging for a component.
    
    This function initializes the logging system if needed and returns
    a Logger instance for the specified component.
    
    Args:
        component: Component name
        client_id: Optional client ID for the component
        storage_path: Path to store log files (default: ~/.tekton/logs)
        console_output: Whether to output logs to console
        console_level: Minimum level for console output
        
    Returns:
        Logger instance
    """
    # Initialize logging if needed
    init_logging(
        storage_path=storage_path,
        console_output=console_output,
        console_level=console_level
    )
    
    # Get logger
    logger = get_logger(
        component=component,
        client_id=client_id
    )
    
    # Store in cache
    _logger_cache[component] = logger
    
    return logger


def get_component_logger(component: str) -> Optional[Logger]:
    """
    Get a logger for a component.
    
    This function returns a cached Logger instance for the specified component,
    or None if no logger has been set up for that component.
    
    Args:
        component: Component name
        
    Returns:
        Logger instance or None
    """
    return _logger_cache.get(component)


def intercept_python_logging(component: str, level_mapping: Optional[Dict[int, LogLevel]] = None) -> None:
    """
    Intercept Python logging and redirect to Tekton logging system.
    
    This function adds a handler to the Python logging system that redirects
    all log messages to the Tekton logging system.
    
    Args:
        component: Component name to use for Tekton logs
        level_mapping: Optional mapping from Python log levels to Tekton log levels
    """
    # Get or create logger
    logger = get_component_logger(component)
    if not logger:
        logger = setup_logging(component)
    
    # Default level mapping
    if level_mapping is None:
        level_mapping = {
            logging.CRITICAL: LogLevel.FATAL,
            logging.ERROR: LogLevel.ERROR,
            logging.WARNING: LogLevel.WARN,
            logging.INFO: LogLevel.INFO,
            logging.DEBUG: LogLevel.DEBUG
        }
    
    # Create custom handler
    class TektonLoggingHandler(logging.Handler):
        def emit(self, record):
            try:
                # Get message
                msg = self.format(record)
                
                # Map level
                tekton_level = LogLevel.INFO
                for python_level, tl in level_mapping.items():
                    if record.levelno >= python_level:
                        tekton_level = tl
                        break
                
                # Create context
                context = {
                    "python_logger": record.name,
                    "python_level": record.levelname,
                    "filename": record.filename,
                    "lineno": record.lineno,
                    "funcName": record.funcName
                }
                
                # Add exception info if available
                if record.exc_info:
                    stack_trace = "".join(traceback.format_exception(*record.exc_info))
                else:
                    stack_trace = None
                
                # Log to Tekton system
                logger._log(
                    level=tekton_level,
                    message=msg,
                    context=context,
                    stack_trace=stack_trace
                )
                
            except Exception:
                self.handleError(record)
    
    # Add handler to root logger
    root_logger = logging.getLogger()
    handler = TektonLoggingHandler()
    root_logger.addHandler(handler)


def patch_stdout_stderr(component: str) -> None:
    """
    Patch sys.stdout and sys.stderr to redirect to Tekton logging system.
    
    This function replaces sys.stdout and sys.stderr with custom file-like
    objects that redirect output to the Tekton logging system.
    
    Args:
        component: Component name to use for Tekton logs
    """
    # Get or create logger
    logger = get_component_logger(component)
    if not logger:
        logger = setup_logging(component)
    
    # Create custom file-like objects
    class StdoutRedirector:
        def write(self, data):
            # Only log non-empty strings
            if data.strip():
                logger.info(data.rstrip(), context={"source": "stdout"})
            
            # Also write to real stdout for debugging
            sys.__stdout__.write(data)
        
        def flush(self):
            sys.__stdout__.flush()
    
    class StderrRedirector:
        def write(self, data):
            # Only log non-empty strings
            if data.strip():
                logger.error(data.rstrip(), context={"source": "stderr"})
            
            # Also write to real stderr for debugging
            sys.__stderr__.write(data)
        
        def flush(self):
            sys.__stderr__.flush()
    
    # Replace stdout and stderr
    sys.stdout = StdoutRedirector()
    sys.stderr = StderrRedirector()


def create_correlation_context() -> str:
    """
    Create a correlation ID for tracking related log entries.
    
    Returns:
        Correlation ID string
    """
    import uuid
    return str(uuid.uuid4())