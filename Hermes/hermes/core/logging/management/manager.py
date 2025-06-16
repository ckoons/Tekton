"""
Log manager for the Tekton Centralized Logging System.

This module provides the LogManager class, which is responsible for managing
log processing, storage, and querying for all Tekton components.
"""

import logging
from typing import Dict, List, Any, Optional, Union

from hermes.core.logging.base.levels import LogLevel
from hermes.core.logging.base.entry import LogEntry
from hermes.core.logging.storage.file_storage import LogStorage

# Standard Python logger for internal use
_internal_logger = logging.getLogger(__name__)


class LogManager:
    """
    Central manager for the Tekton logging system.
    
    This class manages log processing, storage, and querying for
    all Tekton components.
    """
    
    def __init__(self, 
                storage_path: str = None,
                console_output: bool = True,
                console_level: LogLevel = LogLevel.INFO):
        """
        Initialize the log manager.
        
        Args:
            storage_path: Path to store log files
            console_output: Whether to output logs to console
            console_level: Minimum level for console output
        """
        self.storage = LogStorage(storage_path)
        self.console_output = console_output
        self.console_level = console_level
        
        # Set up Python logger for console output
        if console_output:
            # Configure root logger
            root_logger = logging.getLogger()
            
            # Remove existing handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # Add console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(LogLevel.to_python_level(console_level))
            
            # Set formatter
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            
            root_logger.addHandler(console_handler)
        
        _internal_logger.info("Log manager initialized")
    
    def log(self, log_entry: LogEntry) -> bool:
        """
        Process and store a log entry.
        
        Args:
            log_entry: Log entry to process
            
        Returns:
            True if logging successful
        """
        # Store log entry
        storage_success = self.storage.store(log_entry)
        
        # Output to console if enabled
        if self.console_output and log_entry.level.value >= self.console_level.value:
            # Convert to Python log level
            python_level = LogLevel.to_python_level(log_entry.level)
            
            # Create logger for component
            logger = logging.getLogger(log_entry.component)
            
            # Log message
            extra_info = ""
            if log_entry.context:
                extra_info = f" - Context: {log_entry.context}"
            
            logger.log(
                python_level,
                f"{log_entry.message}{extra_info}"
            )
        
        return storage_success
    
    def query(self,
             start_time: Optional[float] = None,
             end_time: Optional[float] = None,
             components: Optional[List[str]] = None,
             levels: Optional[List[LogLevel]] = None,
             limit: int = 100) -> List[LogEntry]:
        """
        Query log entries.
        
        Args:
            start_time: Start time for query (Unix timestamp)
            end_time: End time for query (Unix timestamp)
            components: List of components to include
            levels: List of log levels to include
            limit: Maximum number of entries to return
            
        Returns:
            List of matching log entries
        """
        return self.storage.query(
            start_time=start_time,
            end_time=end_time,
            components=components,
            levels=levels,
            limit=limit
        )