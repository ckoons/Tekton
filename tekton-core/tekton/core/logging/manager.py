#!/usr/bin/env python3
"""
Logging Manager Module

This module provides the LogManager class for centralized logging.
"""

import sys
from typing import Dict, List, Any, Optional, Union

from .models import LogLevel, LogCategory, StructuredLogRecord
from .handlers import LogHandler, ConsoleLogHandler, FileLogHandler, HermesLogHandler

# Global registry of log managers
_log_managers: Dict[str, 'LogManager'] = {}


class LogManager:
    """Manager for centralized logging."""
    
    def __init__(self, component_id: str):
        """
        Initialize log manager.
        
        Args:
            component_id: Component ID
        """
        self.component_id = component_id
        self.handlers: List[LogHandler] = []
        self.correlation_context: Dict[str, str] = {}
        
        # Add default console handler
        self.add_handler(ConsoleLogHandler())
        
    def add_handler(self, handler: LogHandler) -> None:
        """
        Add a log handler.
        
        Args:
            handler: Log handler to add
        """
        self.handlers.append(handler)
        
    def remove_handler(self, handler: LogHandler) -> None:
        """
        Remove a log handler.
        
        Args:
            handler: Log handler to remove
        """
        if handler in self.handlers:
            self.handlers.remove(handler)
    
    def log(self,
           level: Union[LogLevel, str],
           message: str,
           category: Union[LogCategory, str] = LogCategory.COMPONENT,
           context: Optional[Dict[str, Any]] = None,
           correlation_id: Optional[str] = None,
           request_id: Optional[str] = None,
           exception: Optional[Exception] = None) -> None:
        """
        Log a message.
        
        Args:
            level: Log level
            message: Log message
            category: Log category
            context: Optional additional context
            correlation_id: Optional correlation ID for tracking requests
            request_id: Optional request ID
            exception: Optional exception
        """
        # Create log record
        record = StructuredLogRecord(
            level=level,
            message=message,
            category=category,
            component_id=self.component_id,
            context=context,
            correlation_id=correlation_id or self.correlation_context.get("correlation_id"),
            request_id=request_id or self.correlation_context.get("request_id"),
            exception=exception
        )
        
        # Send to all handlers
        for handler in self.handlers:
            handler.handle(record)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        self.log(LogLevel.DEBUG, message, **kwargs)
        
    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        self.log(LogLevel.INFO, message, **kwargs)
        
    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        self.log(LogLevel.WARNING, message, **kwargs)
        
    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        self.log(LogLevel.ERROR, message, **kwargs)
        
    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message."""
        self.log(LogLevel.CRITICAL, message, **kwargs)
        
    def set_correlation_context(self, correlation_id: Optional[str] = None, request_id: Optional[str] = None) -> None:
        """
        Set correlation context for all subsequent logs.
        
        Args:
            correlation_id: Correlation ID
            request_id: Request ID
        """
        if correlation_id:
            self.correlation_context["correlation_id"] = correlation_id
        if request_id:
            self.correlation_context["request_id"] = request_id
            
    def clear_correlation_context(self) -> None:
        """Clear correlation context."""
        self.correlation_context = {}
        
    def exception(self, message: str, exc: Optional[Exception] = None, **kwargs) -> None:
        """
        Log an exception.
        
        Args:
            message: Log message
            exc: Exception (defaults to current exception if in except block)
            **kwargs: Additional arguments for log method
        """
        if exc is None:
            exc_info = sys.exc_info()
            if exc_info[0] is not None:
                exc = exc_info[1]
                
        self.log(LogLevel.ERROR, message, exception=exc, **kwargs)
        
    def shutdown(self) -> None:
        """Shutdown log manager and flush all handlers."""
        for handler in self.handlers:
            if hasattr(handler, "flush"):
                handler.flush()


def get_logger(component_id: str) -> LogManager:
    """
    Get or create a log manager for a component.
    
    Args:
        component_id: Component ID
        
    Returns:
        Log manager for component
    """
    if component_id not in _log_managers:
        _log_managers[component_id] = LogManager(component_id)
    return _log_managers[component_id]


def configure_logging(component_id: str,
                     console: bool = True,
                     file_path: Optional[str] = None,
                     hermes_url: Optional[str] = None,
                     min_level: Union[LogLevel, str] = LogLevel.INFO) -> LogManager:
    """
    Configure logging for a component.
    
    Args:
        component_id: Component ID
        console: Whether to log to console
        file_path: Optional path to log file
        hermes_url: Optional URL of Hermes service
        min_level: Minimum log level
        
    Returns:
        Configured log manager
    """
    # Get or create log manager
    log_manager = get_logger(component_id)
    
    # Remove existing handlers
    log_manager.handlers = []
    
    # Add console handler if enabled
    if console:
        log_manager.add_handler(ConsoleLogHandler(min_level=min_level))
    
    # Add file handler if path provided
    if file_path:
        log_manager.add_handler(FileLogHandler(file_path=file_path, min_level=min_level))
    
    # Add Hermes handler if URL provided
    if hermes_url:
        log_manager.add_handler(HermesLogHandler(hermes_url=hermes_url, min_level=min_level))
    
    return log_manager