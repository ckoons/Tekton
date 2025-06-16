#!/usr/bin/env python3
"""
Logging Manager Module

Manages component request logging and metrics recording.
"""

import logging
from typing import Dict, Any, Optional

from ...logging_integration import LogCategory, LogLevel

logger = logging.getLogger(__name__)


class LoggingManager:
    """
    Manages component request logging and metrics recording.
    """
    
    def __init__(self, logger, metrics_manager):
        """
        Initialize logging manager.
        
        Args:
            logger: Logger instance
            metrics_manager: Metrics manager instance
        """
        self.logger = logger
        self.metrics_manager = metrics_manager
        
    def log_request(self, 
                  endpoint: str, 
                  method: str, 
                  status_code: int, 
                  duration: float,
                  request_id: Optional[str] = None,
                  correlation_id: Optional[str] = None,
                  context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a request.
        
        Args:
            endpoint: Request endpoint
            method: HTTP method
            status_code: HTTP status code
            duration: Request duration in seconds
            request_id: Optional request ID
            correlation_id: Optional correlation ID
            context: Optional additional context
        """
        # Determine log level based on status code
        level = LogLevel.INFO
        if status_code >= 500:
            level = LogLevel.ERROR
        elif status_code >= 400:
            level = LogLevel.WARNING
            
        # Log request
        self.logger.log(
            level=level,
            message=f"{method} {endpoint} {status_code} ({duration*1000:.0f}ms)",
            category=LogCategory.REQUEST,
            request_id=request_id,
            correlation_id=correlation_id,
            context=context
        )
        
        # Record metrics
        self.metrics_manager.record_request(
            endpoint=endpoint,
            duration=duration,
            status_code=status_code,
            is_error=status_code >= 400
        )
