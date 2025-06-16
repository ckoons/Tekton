#!/usr/bin/env python3
"""
Logging Handlers Module

This module provides handlers for processing log records.
"""

import os
import time
import logging
import traceback
from typing import Dict, Any, Optional, Union

from .models import LogLevel, StructuredLogRecord

# Configure default logger
logger = logging.getLogger("tekton.logging.handlers")


class LogHandler:
    """Base class for log handlers."""
    
    def __init__(self, min_level: Union[LogLevel, str] = LogLevel.INFO):
        """
        Initialize log handler.
        
        Args:
            min_level: Minimum log level to handle
        """
        self.min_level = min_level.value if isinstance(min_level, LogLevel) else min_level
        self._level_ranks = {
            LogLevel.DEBUG.value: 0,
            LogLevel.INFO.value: 1,
            LogLevel.WARNING.value: 2,
            LogLevel.ERROR.value: 3,
            LogLevel.CRITICAL.value: 4
        }
        
    def handle(self, record: StructuredLogRecord) -> None:
        """
        Handle a log record.
        
        Args:
            record: Log record to handle
        """
        # Check if record meets minimum level
        record_level_rank = self._level_ranks.get(record.level, 0)
        min_level_rank = self._level_ranks.get(self.min_level, 0)
        
        if record_level_rank >= min_level_rank:
            self._handle_record(record)
    
    def _handle_record(self, record: StructuredLogRecord) -> None:
        """
        Handle a log record (to be implemented by subclasses).
        
        Args:
            record: Log record to handle
        """
        raise NotImplementedError("Subclasses must implement _handle_record")


class ConsoleLogHandler(LogHandler):
    """Log handler that writes to console."""
    
    def __init__(self, 
                min_level: Union[LogLevel, str] = LogLevel.INFO,
                use_colors: bool = True):
        """
        Initialize console log handler.
        
        Args:
            min_level: Minimum log level to handle
            use_colors: Whether to use colors in output
        """
        super().__init__(min_level)
        self.use_colors = use_colors
        self.colors = {
            LogLevel.DEBUG.value: "\033[36m",     # Cyan
            LogLevel.INFO.value: "\033[32m",      # Green
            LogLevel.WARNING.value: "\033[33m",   # Yellow
            LogLevel.ERROR.value: "\033[31m",     # Red
            LogLevel.CRITICAL.value: "\033[35m",  # Magenta
            "reset": "\033[0m"
        }
        
    def _handle_record(self, record: StructuredLogRecord) -> None:
        """
        Write log record to console.
        
        Args:
            record: Log record to handle
        """
        # Format timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.timestamp))
        
        # Format level with color if enabled
        level = record.level.upper()
        if self.use_colors:
            level_color = self.colors.get(record.level, self.colors["reset"])
            level = f"{level_color}{level}{self.colors['reset']}"
        
        # Format message
        message = f"{timestamp} [{level}] {record.component_id} [{record.category}] - {record.message}"
        
        # Add context if present
        if record.context:
            context_str = " ".join(f"{k}={v}" for k, v in record.context.items())
            message += f" {context_str}"
            
        # Add correlation ID if present
        if record.correlation_id:
            message += f" (correlation_id={record.correlation_id})"
            
        # Add request ID if present
        if record.request_id:
            message += f" (request_id={record.request_id})"
            
        # Print message
        print(message)
        
        # Print exception if present
        if record.exception and hasattr(record.exception, "__traceback__"):
            if self.use_colors:
                print(f"{self.colors[LogLevel.ERROR.value]}Exception:{self.colors['reset']}")
                traceback.print_exception(type(record.exception), record.exception, record.exception.__traceback__)
            else:
                print("Exception:")
                traceback.print_exception(type(record.exception), record.exception, record.exception.__traceback__)


class FileLogHandler(LogHandler):
    """Log handler that writes to a file."""
    
    def __init__(self, 
                file_path: str,
                min_level: Union[LogLevel, str] = LogLevel.INFO,
                rotation_size: int = 10 * 1024 * 1024,  # 10 MB
                max_files: int = 5):
        """
        Initialize file log handler.
        
        Args:
            file_path: Path to log file
            min_level: Minimum log level to handle
            rotation_size: Size in bytes at which to rotate logs
            max_files: Maximum number of log files to keep
        """
        super().__init__(min_level)
        self.file_path = file_path
        self.rotation_size = rotation_size
        self.max_files = max_files
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Check if rotation is needed on startup
        self._check_rotation()
        
    def _check_rotation(self) -> None:
        """Check if log file rotation is needed."""
        # Check if file exists and needs rotation
        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) >= self.rotation_size:
            self._rotate_logs()
    
    def _rotate_logs(self) -> None:
        """Rotate log files."""
        # Remove oldest log file if max_files is reached
        for i in range(self.max_files - 1, 0, -1):
            old_path = f"{self.file_path}.{i}"
            new_path = f"{self.file_path}.{i+1}"
            
            if os.path.exists(old_path):
                if i == self.max_files - 1:
                    # Remove oldest log file
                    os.remove(old_path)
                else:
                    # Rename log file
                    os.rename(old_path, new_path)
        
        # Rename current log file
        if os.path.exists(self.file_path):
            os.rename(self.file_path, f"{self.file_path}.1")
            
    def _handle_record(self, record: StructuredLogRecord) -> None:
        """
        Write log record to file.
        
        Args:
            record: Log record to handle
        """
        # Convert record to JSON
        json_record = record.to_json() + "\n"
        
        # Check if rotation is needed
        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) + len(json_record) >= self.rotation_size:
            self._rotate_logs()
        
        # Write to file
        with open(self.file_path, "a") as f:
            f.write(json_record)


class HermesLogHandler(LogHandler):
    """Log handler that forwards logs to Hermes service."""
    
    def __init__(self, 
                hermes_url: str,
                min_level: Union[LogLevel, str] = LogLevel.INFO,
                batch_size: int = 10,
                flush_interval: float = 5.0):
        """
        Initialize Hermes log handler.
        
        Args:
            hermes_url: URL of Hermes service
            min_level: Minimum log level to handle
            batch_size: Maximum number of logs to batch before sending
            flush_interval: Maximum time in seconds before flushing logs
        """
        super().__init__(min_level)
        self.hermes_url = hermes_url
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.log_buffer = []
        self.last_flush_time = time.time()
        
    def _handle_record(self, record: StructuredLogRecord) -> None:
        """
        Buffer log record for sending to Hermes.
        
        Args:
            record: Log record to handle
        """
        # Add record to buffer
        self.log_buffer.append(record.to_dict())
        
        # Check if batch is full or flush interval has passed
        if len(self.log_buffer) >= self.batch_size or time.time() - self.last_flush_time >= self.flush_interval:
            self.flush()
    
    def flush(self) -> None:
        """Flush buffered log records to Hermes."""
        if not self.log_buffer:
            return
            
        try:
            # Send logs to Hermes (use async in real implementation)
            # This is a placeholder for actual HTTP request to Hermes
            logger.debug(f"Would send {len(self.log_buffer)} logs to Hermes at {self.hermes_url}")
            
            # Clear buffer and update flush time
            self.log_buffer = []
            self.last_flush_time = time.time()
            
        except Exception as e:
            logger.error(f"Failed to send logs to Hermes: {e}")