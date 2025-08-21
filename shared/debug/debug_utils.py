"""
Tekton Debug Utilities

This module provides lightweight debug instrumentation for Python modules in Tekton.
It allows instrumentation with minimal overhead that can evolve over time without
requiring code changes in the instrumented modules.

Usage:
    from debug_utils import debug_log

    # Then in your code:
    debug_log.debug("component_name", "Debug message")
    debug_log.info("component_name", "Info message", {"extra": "data"})
"""

import os
from shared.env import TektonEnviron
import sys
import json
import logging
import inspect
import traceback
from datetime import datetime
from functools import wraps
from enum import Enum
from typing import Any, Dict, Optional, Callable, Union

# Define log levels
class LogLevel(Enum):
    TRACE = 5     # Custom level below DEBUG
    DEBUG = 10    # Same as logging.DEBUG
    INFO = 20     # Same as logging.INFO
    WARN = 30     # Same as logging.WARNING
    ERROR = 40    # Same as logging.ERROR
    FATAL = 50    # Same as logging.CRITICAL
    OFF = 60      # Higher than any standard level to disable logging

# Configure from environment
TEKTON_DEBUG_ENABLED = TektonEnviron.get("TEKTON_DEBUG", "false").lower() in ["true", "1", "yes"]
TEKTON_LOG_LEVEL = TektonEnviron.get("TEKTON_LOG_LEVEL", "INFO").upper()
TEKTON_LOG_FILE = TektonEnviron.get("TEKTON_LOG_FILE", "")
TEKTON_LOG_FORMAT = TektonEnviron.get("TEKTON_LOG_FORMAT", "text")  # "text" or "json"

class DebugLog:
    """Lightweight debug logging with minimal overhead when disabled"""
    
    def __init__(self):
        # Configure based on environment
        self.enabled = TEKTON_DEBUG_ENABLED
        
        # Set default log level
        try:
            self.default_level = LogLevel[TEKTON_LOG_LEVEL]
        except KeyError:
            self.default_level = LogLevel.INFO
            
        # Component-specific log levels
        self.component_levels = {}
        
        # Setup Python logger if enabled
        if self.enabled:
            self._setup_logger()
        
    def _setup_logger(self):
        """Set up the Python logger if enabled"""
        self.logger = logging.getLogger("tekton")
        
        # Map our custom levels to Python logging levels
        logging.addLevelName(LogLevel.TRACE.value, "TRACE")
        
        # Set the base level to allow all our messages through
        self.logger.setLevel(LogLevel.TRACE.value)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        
        # File handler if specified
        if TEKTON_LOG_FILE:
            try:
                file_handler = logging.FileHandler(TEKTON_LOG_FILE)
                
                if TEKTON_LOG_FORMAT == "json":
                    file_handler.setFormatter(JsonLogFormatter())
                else:
                    file_handler.setFormatter(logging.Formatter(
                        '%(asctime)s [%(levelname)s] [%(component)s] %(message)s'
                    ))
                
                self.logger.addHandler(file_handler)
            except Exception as e:
                sys.stderr.write(f"Failed to set up log file: {str(e)}\n")
        
        # Set up formatter
        if TEKTON_LOG_FORMAT == "json":
            console_handler.setFormatter(JsonLogFormatter())
        else:
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] [%(component)s] %(message)s'
            ))
        
        self.logger.addHandler(console_handler)
    
    def should_log(self, level: LogLevel, component: str) -> bool:
        """Check if a log message should be emitted based on settings"""
        if not self.enabled:
            return False
            
        # Get threshold for this component or global default
        threshold = self.component_levels.get(component, self.default_level)
        
        # Log if level meets or exceeds threshold
        return level.value >= threshold.value
    
    def _log(self, level: LogLevel, component: str, message: str, 
             data: Optional[Any] = None, caller_info: Optional[Dict] = None):
        """Internal logging method that handles both enabled and disabled states"""
        # Skip if disabled or below threshold
        if not self.should_log(level, component):
            return False
            
        # Get caller information if not provided
        if not caller_info:
            frame = inspect.currentframe().f_back.f_back  # Skip _log and the specific level method
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            caller_info = {
                "file": filename,
                "line": lineno,
                "function": frame.f_code.co_name
            }
            
        # Create extra fields for the logger
        extra = {
            "component": component,
            "timestamp": datetime.now().isoformat(),
            "caller": caller_info
        }
        
        # Add data if provided
        if data:
            if isinstance(data, dict):
                extra["data"] = data
            else:
                extra["data"] = {"value": str(data)}
        
        # Convert to Python logging level
        py_level = level.value
        
        # Log through standard Python logger
        self.logger.log(py_level, message, extra=extra)
        
        return True
    
    # Convenience methods for each log level
    def trace(self, component: str, message: str, data: Optional[Any] = None):
        """Log a TRACE level message (most verbose)"""
        return self._log(LogLevel.TRACE, component, message, data)
    
    def debug(self, component: str, message: str, data: Optional[Any] = None):
        """Log a DEBUG level message"""
        return self._log(LogLevel.DEBUG, component, message, data)
    
    def info(self, component: str, message: str, data: Optional[Any] = None):
        """Log an INFO level message"""
        return self._log(LogLevel.INFO, component, message, data)
    
    def warn(self, component: str, message: str, data: Optional[Any] = None):
        """Log a WARN level message"""
        return self._log(LogLevel.WARN, component, message, data)
    
    def error(self, component: str, message: str, data: Optional[Any] = None):
        """Log an ERROR level message"""
        return self._log(LogLevel.ERROR, component, message, data)
    
    def fatal(self, component: str, message: str, data: Optional[Any] = None):
        """Log a FATAL level message (most severe)"""
        return self._log(LogLevel.FATAL, component, message, data)
    
    def exception(self, component: str, message: str, exc_info=None):
        """Log an exception with traceback"""
        if not self.should_log(LogLevel.ERROR, component):
            return False
            
        if exc_info is None:
            exc_info = sys.exc_info()
            
        exc_type, exc_value, exc_tb = exc_info
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        
        return self._log(LogLevel.ERROR, component, message, {
            "exception_type": exc_type.__name__ if exc_type else "Unknown",
            "exception_message": str(exc_value),
            "traceback": tb_str
        })
    
    def set_component_level(self, component: str, level: Union[str, LogLevel]):
        """Set log level for a specific component"""
        if isinstance(level, str):
            try:
                level = LogLevel[level.upper()]
            except KeyError:
                # Invalid level, fallback to default
                return False
                
        self.component_levels[component] = level
        return True
    
    def set_enabled(self, enabled: bool):
        """Enable or disable logging"""
        was_enabled = self.enabled
        self.enabled = enabled
        
        # Set up logger if newly enabled
        if enabled and not was_enabled:
            self._setup_logger()
            
        return True


class JsonLogFormatter(logging.Formatter):
    """Formatter that outputs JSON strings"""
    
    def format(self, record):
        # Create log entry as dictionary
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "component": getattr(record, "component", "unknown"),
            "message": record.getMessage()
        }
        
        # Add exception info if available
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        # Add data if available
        if hasattr(record, "data"):
            log_entry["data"] = record.data
            
        # Add caller info if available
        if hasattr(record, "caller"):
            log_entry["caller"] = record.caller
            
        # Convert to JSON
        return json.dumps(log_entry)


# Create singleton instance
debug_log = DebugLog()


# Decorator for instrumenting functions
def log_function(level: Union[str, LogLevel] = LogLevel.DEBUG, include_args: bool = True):
    """
    Decorator to log function entry and exit
    
    Args:
        level: The log level to use
        include_args: Whether to include function arguments in the log
        
    Example:
        @log_function(level=LogLevel.DEBUG, include_args=True)
        def my_function(arg1, arg2):
            # Function code...
    """
    if isinstance(level, str):
        try:
            level = LogLevel[level.upper()]
        except KeyError:
            level = LogLevel.DEBUG
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Skip if debugging disabled
            if not debug_log.enabled:
                return func(*args, **kwargs)
                
            # Get component name (module name or parent class)
            frame = inspect.currentframe()
            module_name = func.__module__
            
            # Check if method of a class (has self parameter)
            component = module_name
            if args and hasattr(args[0], '__class__'):
                component = args[0].__class__.__name__
                
            # Log function entry
            if include_args:
                # Format arguments safely
                args_str = ', '.join([repr(a) for a in args[1:]] if component != module_name else [repr(a) for a in args])
                kwargs_str = ', '.join([f"{k}={repr(v)}" for k, v in kwargs.items()])
                params = f"{args_str}{', ' if args_str and kwargs_str else ''}{kwargs_str}"
                debug_log._log(level, component, f"ENTER {func.__name__}({params})")
            else:
                debug_log._log(level, component, f"ENTER {func.__name__}()")
                
            # Call the function
            try:
                result = func(*args, **kwargs)
                
                # Log function exit
                if include_args:
                    debug_log._log(level, component, f"EXIT {func.__name__} → {repr(result)}")
                else:
                    debug_log._log(level, component, f"EXIT {func.__name__}")
                    
                return result
            except Exception as e:
                # Log exception
                debug_log.exception(component, f"EXCEPTION in {func.__name__}: {str(e)}")
                raise
                
        return wrapper
    return decorator