"""
Tekton Logging Utility

This module provides a standardized logging setup for Tekton components
with consistent formatting, log levels, and configuration.

Usage:
    from tekton.utils.tekton_logging import setup_logging, get_logger
    
    # Basic setup with component name
    logger = setup_logging("mycomponent")
    
    # Advanced setup with file handler and custom format
    logger = setup_logging(
        "mycomponent",
        log_level="DEBUG",
        log_file="/var/log/tekton/mycomponent.log",
        include_json=True,
        include_correlation_id=True
    )
    
    # Get a child logger for a specific module
    module_logger = get_logger("mycomponent.module")
"""

import os
import sys
import json
import time
import logging
import logging.handlers
import socket
import traceback
from functools import wraps
from datetime import datetime
from typing import Dict, Any, Optional, Union, List, Callable, TextIO, Set, Tuple, cast
from pathlib import Path
import uuid
import threading

# Create a thread-local storage for context values
_thread_local = threading.local()

# Store configured loggers to avoid duplicate handlers
_configured_loggers: Set[str] = set()

# Name of the environment variable for global log level
LOG_LEVEL_ENV_VAR = "TEKTON_LOG_LEVEL"

# Name of the environment variable for log file directory
LOG_DIR_ENV_VAR = "TEKTON_LOG_DIR"

# Default log format string
DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] [%(component_id)s] %(message)s"

# Default JSON format includes all fields
DEFAULT_JSON_FIELDS = [
    "timestamp", "level", "component_id", "message", "logger", "thread", 
    "correlation_id", "context", "host"
]


class ContextFilter(logging.Filter):
    """
    Filter that adds context values to log records.
    """
    
    def __init__(self, component_id: str, include_correlation_id: bool = True):
        """
        Initialize filter with component ID.
        
        Args:
            component_id: ID of the component
            include_correlation_id: Whether to include correlation ID
        """
        super().__init__()
        self.component_id = component_id
        self.include_correlation_id = include_correlation_id
        self.hostname = socket.gethostname()
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add context values to the log record.
        
        Args:
            record: Log record to process
            
        Returns:
            True to include the record
        """
        # Add component ID
        record.component_id = self.component_id
        
        # Add hostname
        record.hostname = self.hostname
        
        # Add correlation ID if enabled
        if self.include_correlation_id:
            record.correlation_id = getattr(_thread_local, 'correlation_id', None) or 'unknown'
        
        # Add context dictionary
        record.context = getattr(_thread_local, 'context', {})
        
        return True


class JsonFormatter(logging.Formatter):
    """
    Format log records as JSON.
    """
    
    def __init__(self, fields: Optional[List[str]] = None):
        """
        Initialize JSON formatter.
        
        Args:
            fields: Fields to include in JSON output (None for all)
        """
        super().__init__()
        self.fields = fields or DEFAULT_JSON_FIELDS
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON string
        """
        log_data: Dict[str, Any] = {}
        
        # Add standard fields if requested
        if "timestamp" in self.fields:
            log_data["timestamp"] = datetime.fromtimestamp(record.created).isoformat()
            
        if "level" in self.fields:
            log_data["level"] = record.levelname
            
        if "component_id" in self.fields and hasattr(record, 'component_id'):
            log_data["component_id"] = record.component_id
            
        if "message" in self.fields:
            log_data["message"] = record.getMessage()
            
        if "logger" in self.fields:
            log_data["logger"] = record.name
            
        if "thread" in self.fields:
            log_data["thread"] = record.threadName
            
        if "correlation_id" in self.fields and hasattr(record, 'correlation_id'):
            log_data["correlation_id"] = record.correlation_id
            
        if "context" in self.fields and hasattr(record, 'context'):
            log_data["context"] = record.context
            
        if "host" in self.fields and hasattr(record, 'hostname'):
            log_data["host"] = record.hostname
            
        # Add exception info if present
        if record.exc_info and "exception" in self.fields:
            exception = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            log_data["exception"] = exception
        
        # Add custom fields from record
        for key, value in record.__dict__.items():
            # Skip standard fields already added
            if key in [
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'exc_info', 'exc_text', 'lineno',
                'funcName', 'created', 'msecs', 'relativeCreated', 'thread',
                'threadName', 'processName', 'process', 'message', 'asctime',
                'component_id', 'correlation_id', 'context', 'hostname'
            ]:
                continue
                
            # Skip private fields and callables
            if key.startswith('_') or callable(value):
                continue
                
            # Add custom field if in requested fields or no fields specified
            if key in self.fields or not self.fields:
                try:
                    # Check if the value is JSON serializable
                    json.dumps({key: value})
                    log_data[key] = value
                except TypeError:
                    # If not serializable, use string representation
                    log_data[key] = str(value)
        
        return json.dumps(log_data)


def setup_logging(
    component_id: str,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
    include_timestamp: bool = True,
    include_json: bool = False,
    json_fields: Optional[List[str]] = None,
    include_correlation_id: bool = True,
    propagate: bool = False,
    log_to_console: bool = True,
    log_to_file: bool = True,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    encoding: str = 'utf8',
    console_stream: TextIO = sys.stdout,
    create_dir: bool = True
) -> logging.Logger:
    """
    Set up logging for a Tekton component.
    
    Args:
        component_id: Component identifier
        log_level: Logging level (default from TEKTON_LOG_LEVEL or INFO)
        log_file: Path to log file (default from TEKTON_LOG_DIR/<component_id>.log or None)
        format_string: Custom format string
        include_timestamp: Whether to include timestamp in format
        include_json: Whether to use JSON formatting for logs
        json_fields: Fields to include in JSON output (None for default)
        include_correlation_id: Whether to include correlation ID in logs
        propagate: Whether to propagate logs to parent loggers
        log_to_console: Whether to log to console
        log_to_file: Whether to log to file
        max_bytes: Maximum size in bytes before log rotation
        backup_count: Number of backup log files to keep
        encoding: Encoding for log files
        console_stream: Stream to use for console logging
        create_dir: Whether to create log directories if they don't exist
        
    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(component_id)
    
    # Skip if already configured
    if component_id in _configured_loggers:
        return logger
    
    # Determine log level from args, env, or default to INFO
    if log_level is None:
        from shared.env import TektonEnviron
        log_level = TektonEnviron.get(LOG_LEVEL_ENV_VAR, 'INFO')
        
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Remove existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    if include_json:
        formatter = JsonFormatter(fields=json_fields)
    else:
        if format_string is None:
            format_string = DEFAULT_FORMAT
            
        if not include_timestamp and '%(asctime)s' in format_string:
            # Remove timestamp from format
            format_string = format_string.replace('%(asctime)s', '').strip()
            
        formatter = logging.Formatter(format_string)
    
    # Create and add context filter
    context_filter = ContextFilter(component_id, include_correlation_id)
    logger.addFilter(context_filter)
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(console_stream)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_to_file and (log_file or TektonEnviron.get(LOG_DIR_ENV_VAR)):
        # Determine log file path
        if log_file is None:
            log_dir = TektonEnviron.get(LOG_DIR_ENV_VAR, '/var/log/tekton')
            log_file = os.path.join(log_dir, f"{component_id}.log")
        
        # Create directory if needed
        if create_dir:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Set propagation
    logger.propagate = propagate
    
    # Mark as configured
    _configured_loggers.add(component_id)
    
    # Log startup message
    logger.info(f"Logging initialized for {component_id} at level {log_level}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    If the parent logger has been configured with setup_logging(),
    this logger will inherit its configuration.
    
    Args:
        name: Logger name (use dot notation for hierarchy)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Set correlation ID for the current thread.
    
    Args:
        correlation_id: Correlation ID to set (None for auto-generated)
        
    Returns:
        The correlation ID
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
        
    _thread_local.correlation_id = correlation_id
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """
    Get correlation ID for the current thread.
    
    Returns:
        Current correlation ID or None if not set
    """
    return getattr(_thread_local, 'correlation_id', None)


def clear_correlation_id() -> None:
    """Clear correlation ID for the current thread."""
    if hasattr(_thread_local, 'correlation_id'):
        delattr(_thread_local, 'correlation_id')


def set_context(key: str, value: Any) -> None:
    """
    Set a context value for the current thread.
    
    Args:
        key: Context key
        value: Context value (must be JSON serializable)
    """
    if not hasattr(_thread_local, 'context'):
        _thread_local.context = {}
        
    _thread_local.context[key] = value


def get_context(key: str, default: Any = None) -> Any:
    """
    Get a context value for the current thread.
    
    Args:
        key: Context key
        default: Default value if key not found
        
    Returns:
        Context value or default
    """
    if not hasattr(_thread_local, 'context'):
        return default
        
    return _thread_local.context.get(key, default)


def clear_context() -> None:
    """Clear all context values for the current thread."""
    if hasattr(_thread_local, 'context'):
        delattr(_thread_local, 'context')


def with_correlation_id(func: Optional[Callable] = None, id_generator: Optional[Callable[[], str]] = None) -> Callable:
    """
    Decorator to set a correlation ID for the function call.
    
    Args:
        func: Function to decorate
        id_generator: Function to generate correlation ID (None for UUID)
        
    Returns:
        Decorated function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate a correlation ID if not already set
            current_id = get_correlation_id()
            if current_id is None:
                if id_generator:
                    new_id = id_generator()
                else:
                    new_id = str(uuid.uuid4())
                set_correlation_id(new_id)
            
            try:
                return f(*args, **kwargs)
            finally:
                # Clear only if we set it
                if current_id is None:
                    clear_correlation_id()
        
        return wrapper
    
    # Allow for direct use or with arguments
    if func is None:
        return decorator
    return decorator(func)


def log_execution_time(logger: Optional[Union[logging.Logger, str]] = None, level: int = logging.DEBUG) -> Callable:
    """
    Decorator to log function execution time.
    
    Args:
        logger: Logger to use (string for logger name, None for function's module)
        level: Logging level for the execution time message
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Determine which logger to use
            log_instance = None
            if logger is None:
                log_instance = logging.getLogger(func.__module__)
            elif isinstance(logger, str):
                log_instance = logging.getLogger(logger)
            else:
                log_instance = logger
            
            # Log start message
            log_instance.debug(f"Starting {func.__name__}")
            
            # Measure execution time
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log execution time
            log_instance.log(level, f"Executed {func.__name__} in {execution_time:.4f} seconds")
            
            return result
        
        return wrapper
    
    return decorator


def configure_werkzeug_logger() -> None:
    """Configure Werkzeug logger to be less verbose."""
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)


def configure_asyncio_logger() -> None:
    """Configure asyncio logger to be less verbose."""
    asyncio_logger = logging.getLogger('asyncio')
    asyncio_logger.setLevel(logging.WARNING)


def configure_uvicorn_logger() -> None:
    """Configure uvicorn logger to be less verbose."""
    uvicorn_logger = logging.getLogger('uvicorn')
    uvicorn_logger.setLevel(logging.WARNING)
    uvicorn_access_logger = logging.getLogger('uvicorn.access')
    uvicorn_access_logger.setLevel(logging.WARNING)


def configure_all_external_loggers() -> None:
    """Configure all known external loggers to be less verbose."""
    configure_werkzeug_logger()
    configure_asyncio_logger()
    configure_uvicorn_logger()
    
    # Additional loggers that can be noisy
    for logger_name in ['aiohttp', 'requests', 'urllib3', 'botocore', 'boto3']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)