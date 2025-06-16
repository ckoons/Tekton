#!/usr/bin/env python3
"""
Logging Models Module

This module provides data models for structured logging.
"""

import os
import sys
import json
import time
import socket
import traceback
from enum import Enum
from typing import Dict, Any, Optional, Union


class LogLevel(Enum):
    """Standard log levels for Tekton components."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(Enum):
    """Standard log categories for Tekton components."""
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    LIFECYCLE = "lifecycle"
    METRICS = "metrics"
    PERFORMANCE = "performance"
    SECURITY = "security"
    REQUEST = "request"
    RESPONSE = "response"
    DEPENDENCY = "dependency"
    RECOVERY = "recovery"
    COMPONENT = "component"
    SYSTEM = "system"


class StructuredLogRecord:
    """Structured log record for standardized logging."""
    
    def __init__(self,
                level: Union[LogLevel, str],
                message: str,
                category: Union[LogCategory, str],
                component_id: str,
                timestamp: Optional[float] = None,
                context: Optional[Dict[str, Any]] = None,
                correlation_id: Optional[str] = None,
                request_id: Optional[str] = None,
                exception: Optional[Exception] = None):
        """
        Initialize a structured log record.
        
        Args:
            level: Log level
            message: Log message
            category: Log category
            component_id: Component ID
            timestamp: Optional timestamp (defaults to current time)
            context: Optional additional context
            correlation_id: Optional correlation ID for tracking requests
            request_id: Optional request ID
            exception: Optional exception
        """
        self.level = level.value if isinstance(level, LogLevel) else level
        self.message = message
        self.category = category.value if isinstance(category, LogCategory) else category
        self.component_id = component_id
        self.timestamp = timestamp or time.time()
        self.context = context or {}
        self.correlation_id = correlation_id
        self.request_id = request_id
        self.exception = exception
        self.hostname = socket.gethostname()
        self.process_id = os.getpid()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "level": self.level,
            "message": self.message,
            "category": self.category,
            "component_id": self.component_id,
            "timestamp": self.timestamp,
            "hostname": self.hostname,
            "process_id": self.process_id
        }
        
        # Add optional fields if present
        if self.context:
            result["context"] = self.context
        if self.correlation_id:
            result["correlation_id"] = self.correlation_id
        if self.request_id:
            result["request_id"] = self.request_id
        if self.exception:
            result["exception"] = {
                "type": type(self.exception).__name__,
                "message": str(self.exception),
                "traceback": traceback.format_exception(type(self.exception), self.exception, self.exception.__traceback__)
            }
            
        return result
        
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StructuredLogRecord':
        """Create from dictionary."""
        return cls(
            level=data.get("level", "info"),
            message=data.get("message", ""),
            category=data.get("category", "general"),
            component_id=data.get("component_id", "unknown"),
            timestamp=data.get("timestamp"),
            context=data.get("context"),
            correlation_id=data.get("correlation_id"),
            request_id=data.get("request_id")
        )