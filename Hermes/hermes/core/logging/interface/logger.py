"""
Logger interface for Tekton components.

This module provides the Logger class, which is the main interface for Tekton
components to log messages at different levels with structured contextual information.
"""

import logging
import uuid
import time
from typing import Dict, List, Any, Optional, Union, Callable

from hermes.core.logging.base.levels import LogLevel
from hermes.core.logging.base.entry import LogEntry
from hermes.core.logging.management.manager import LogManager

# Standard Python logger for internal use
_internal_logger = logging.getLogger(__name__)


class Logger:
    """
    Logger interface for Tekton components.
    
    This class provides methods for logging messages at different levels,
    with structured contextual information.
    """
    
    def __init__(self,
                component: str,
                log_manager: LogManager,
                client_id: Optional[str] = None,
                default_context: Optional[Dict[str, Any]] = None):
        """
        Initialize the logger.
        
        Args:
            component: Component name for log entries
            log_manager: Log manager for storing logs
            client_id: Optional client ID for categorization
            default_context: Default context for all log entries
        """
        self.component = component
        self.log_manager = log_manager
        self.client_id = client_id
        self.default_context = default_context or {}
        
        _internal_logger.info(f"Logger initialized for component {component}")
    
    def _log(self,
           level: LogLevel,
           message: str,
           code: Optional[str] = None,
           context: Optional[Dict[str, Any]] = None,
           effective_timestamp: Optional[float] = None,
           correlation_id: Optional[str] = None,
           stack_trace: Optional[str] = None) -> bool:
        """
        Log a message at the specified level.
        
        Args:
            level: Log level
            message: Log message
            code: Optional event code
            context: Optional context information
            effective_timestamp: Optional effective timestamp
            correlation_id: Optional correlation ID
            stack_trace: Optional stack trace for errors
            
        Returns:
            True if logging successful
        """
        # Combine default context with provided context
        combined_context = self.default_context.copy()
        if context:
            combined_context.update(context)
        
        # Create log entry
        log_entry = LogEntry(
            timestamp=time.time(),
            effective_timestamp=effective_timestamp,
            component=self.component,
            level=level,
            correlation_id=correlation_id or str(uuid.uuid4()),
            client_id=self.client_id,
            message=message,
            code=code,
            context=combined_context,
            stack_trace=stack_trace
        )
        
        # Send to log manager
        return self.log_manager.log(log_entry)
    
    def fatal(self,
            message: str,
            code: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None,
            correlation_id: Optional[str] = None,
            stack_trace: Optional[str] = None) -> bool:
        """
        Log a fatal message.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            stack_trace: Optional stack trace
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.FATAL,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id,
            stack_trace=stack_trace
        )
    
    def error(self,
            message: str,
            code: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None,
            correlation_id: Optional[str] = None,
            stack_trace: Optional[str] = None) -> bool:
        """
        Log an error message.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            stack_trace: Optional stack trace
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.ERROR,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id,
            stack_trace=stack_trace
        )
    
    def warn(self,
           message: str,
           code: Optional[str] = None,
           context: Optional[Dict[str, Any]] = None,
           correlation_id: Optional[str] = None) -> bool:
        """
        Log a warning message.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.WARN,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id
        )
    
    def info(self,
           message: str,
           code: Optional[str] = None,
           context: Optional[Dict[str, Any]] = None,
           correlation_id: Optional[str] = None) -> bool:
        """
        Log an informational message.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.INFO,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id
        )
    
    def normal(self,
             message: str,
             code: Optional[str] = None,
             context: Optional[Dict[str, Any]] = None,
             correlation_id: Optional[str] = None) -> bool:
        """
        Log a normal system event.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.NORMAL,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id
        )
    
    def debug(self,
            message: str,
            code: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None,
            correlation_id: Optional[str] = None) -> bool:
        """
        Log a debug message.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.DEBUG,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id
        )
    
    def trace(self,
            message: str,
            code: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None,
            correlation_id: Optional[str] = None) -> bool:
        """
        Log a trace message.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.TRACE,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id
        )
    
    def with_context(self, context: Dict[str, Any]) -> 'Logger':
        """
        Create a new logger with additional context.
        
        Args:
            context: Context to add to default context
            
        Returns:
            New logger instance with combined context
        """
        # Combine contexts
        combined_context = self.default_context.copy()
        combined_context.update(context)
        
        # Create new logger with combined context
        return Logger(
            component=self.component,
            log_manager=self.log_manager,
            client_id=self.client_id,
            default_context=combined_context
        )
    
    def with_correlation(self, correlation_id: str) -> 'Logger':
        """
        Create a new logger that uses the specified correlation ID.
        
        Args:
            correlation_id: Correlation ID to use for all log entries
            
        Returns:
            New logger instance with specified correlation ID
        """
        logger = Logger(
            component=self.component,
            log_manager=self.log_manager,
            client_id=self.client_id,
            default_context=self.default_context.copy()
        )
        
        # Override the _log method to always use the provided correlation ID
        original_log = logger._log
        
        def _log_with_correlation(
            level: LogLevel,
            message: str,
            code: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None,
            effective_timestamp: Optional[float] = None,
            correlation_id_override: Optional[str] = None,
            stack_trace: Optional[str] = None
        ) -> bool:
            return original_log(
                level=level,
                message=message,
                code=code,
                context=context,
                effective_timestamp=effective_timestamp,
                correlation_id=correlation_id,  # Always use the provided correlation ID
                stack_trace=stack_trace
            )
        
        logger._log = _log_with_correlation
        return logger