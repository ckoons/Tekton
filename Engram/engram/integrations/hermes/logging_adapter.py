#!/usr/bin/env python3
"""
Hermes Logging Adapter for Engram

This module provides integration between Engram and Hermes's centralized logging system,
enabling structured logging and log aggregation across Tekton components.
"""

import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

# Configure default logging for this module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.integrations.hermes.logging")

# Import Hermes logging system
try:
    from hermes.core.logging import LogManager, LogLevel, LogEntry
    HAS_HERMES_LOGGING = True
except ImportError:
    logger.warning("Hermes logging system not found, using fallback implementation")
    HAS_HERMES_LOGGING = False


class LoggingAdapter:
    """
    Logging adapter for Engram using Hermes's centralized logging system.
    
    This class provides structured logging capabilities with integration
    to Hermes's aggregated logging across Tekton components.
    """
    
    def __init__(self, 
                client_id: str = "default", 
                log_file: Optional[str] = None,
                console_level: str = "INFO",
                file_level: str = "DEBUG"):
        """
        Initialize the logging adapter.
        
        Args:
            client_id: Unique identifier for this client
            log_file: Path to log file (default: ~/tekton/logs/engram_{client_id}.log)
            console_level: Logging level for console output (default: INFO)
            file_level: Logging level for file output (default: DEBUG)
        """
        self.client_id = client_id
        
        # Set up log file path
        if log_file:
            self.log_file = Path(log_file)
        else:
            log_dir = Path(os.environ.get('TEKTON_LOG_DIR', 
                                          os.path.join(os.environ.get('TEKTON_ROOT', os.path.expanduser('~')), 
                                                      '.tekton', 'logs')))
            log_dir.mkdir(parents=True, exist_ok=True)
            self.log_file = log_dir / f"engram_{client_id}.log"
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert string log levels to logging constants
        self.console_level = self._get_log_level(console_level)
        self.file_level = self._get_log_level(file_level)
        
        # Initialize Hermes log manager if available
        self.hermes_available = HAS_HERMES_LOGGING
        self.log_manager = None
        
        if self.hermes_available:
            try:
                # Initialize the LogManager
                self.log_manager = LogManager(
                    component_id=f"engram.{client_id}",
                    log_file=str(self.log_file)
                )
                logger.info(f"Initialized Hermes log manager for Engram ({client_id})")
            except Exception as e:
                logger.error(f"Error initializing Hermes log manager: {e}")
                self.hermes_available = False
        
        # Set up fallback logging if Hermes is not available
        if not self.hermes_available:
            # Configure a custom logger
            self.fallback_logger = logging.getLogger(f"engram.{client_id}")
            self.fallback_logger.setLevel(logging.DEBUG)  # Capture all logs
            
            # Remove existing handlers
            for handler in self.fallback_logger.handlers[:]:
                self.fallback_logger.removeHandler(handler)
            
            # Create handlers
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.console_level)
            
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(self.file_level)
            
            # Create formatter
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            # Add handlers to logger
            self.fallback_logger.addHandler(console_handler)
            self.fallback_logger.addHandler(file_handler)
            
            logger.info(f"Set up fallback logging to {self.log_file}")
    
    def log(self, 
           level: str, 
           message: str, 
           context: Optional[Dict[str, Any]] = None,
           component: Optional[str] = None,
           source_file: Optional[str] = None,
           source_line: Optional[int] = None) -> bool:
        """
        Log a message with the specified level.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: The log message
            context: Optional additional context as key-value pairs
            component: Optional component name for sub-component logging
            source_file: Optional source file where the log was generated
            source_line: Optional line number where the log was generated
            
        Returns:
            Boolean indicating success
        """
        # Get numeric log level
        numeric_level = self._get_log_level(level)
        
        # Prepare context
        if context is None:
            context = {}
        
        timestamp = datetime.now().isoformat()
        context["timestamp"] = timestamp
        context["client_id"] = self.client_id
        
        if component:
            context["component"] = component
        
        if source_file:
            context["source_file"] = source_file
            if source_line:
                context["source_line"] = source_line
        
        # Log via Hermes if available
        if self.hermes_available:
            try:
                # Create a log entry
                log_entry = LogEntry(
                    level=self._to_hermes_level(level),
                    message=message,
                    context=context,
                    timestamp=timestamp
                )
                
                # Log the entry
                self.log_manager.log(log_entry)
                
                return True
            except Exception as e:
                logger.error(f"Error logging to Hermes: {e}")
                # Fall back to local logging
        
        # Use fallback logger
        try:
            # Format context if present
            context_str = ""
            if context:
                context_str = " - " + " - ".join([f"{k}={v}" for k, v in context.items()])
            
            # Get the logging method for the given level
            log_method = getattr(self.fallback_logger, level.lower())
            
            # Call the method with the message and context
            log_method(f"{message}{context_str}")
            
            return True
        except Exception as e:
            logger.error(f"Error logging to fallback logger: {e}")
            return False
    
    def debug(self, message: str, **kwargs) -> bool:
        """Log a DEBUG message."""
        return self.log("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs) -> bool:
        """Log an INFO message."""
        return self.log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> bool:
        """Log a WARNING message."""
        return self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs) -> bool:
        """Log an ERROR message."""
        return self.log("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> bool:
        """Log a CRITICAL message."""
        return self.log("CRITICAL", message, **kwargs)
    
    def get_logs(self, 
                level: Optional[str] = None, 
                component: Optional[str] = None,
                limit: int = 100,
                start_time: Optional[str] = None,
                end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get logs filtered by level, component, and time range.
        
        Args:
            level: Minimum log level to include (default: all levels)
            component: Filter logs by component (default: all components)
            limit: Maximum number of logs to return
            start_time: ISO format timestamp for start of range
            end_time: ISO format timestamp for end of range
            
        Returns:
            List of log entries as dictionaries
        """
        # Get logs via Hermes if available
        if self.hermes_available:
            try:
                # Convert level to Hermes format if provided
                hermes_level = self._to_hermes_level(level) if level else None
                
                # Get logs from Hermes
                log_entries = self.log_manager.get_logs(
                    level=hermes_level,
                    component=component,
                    limit=limit,
                    start_time=start_time,
                    end_time=end_time
                )
                
                # Convert to standard format
                result = []
                for entry in log_entries:
                    result.append({
                        "level": entry.level.name,
                        "message": entry.message,
                        "timestamp": entry.timestamp,
                        "context": entry.context
                    })
                
                return result
            except Exception as e:
                logger.error(f"Error getting logs from Hermes: {e}")
                # Fall back to local log file
        
        # Use fallback implementation reading the log file
        try:
            # Read the log file
            logs = []
            numeric_level = self._get_log_level(level) if level else 0
            
            with open(self.log_file, "r") as f:
                for line in f:
                    try:
                        # Parse the log line
                        parts = line.strip().split(" - ", 3)
                        if len(parts) >= 4:
                            timestamp_str = parts[0]
                            logger_name = parts[1]
                            log_level = parts[2]
                            message = parts[3]
                            
                            # Filter by level
                            if level and self._get_log_level(log_level) < numeric_level:
                                continue
                            
                            # Filter by component
                            if component and component not in logger_name:
                                continue
                            
                            # Filter by time range
                            if start_time and timestamp_str < start_time:
                                continue
                            
                            if end_time and timestamp_str > end_time:
                                continue
                            
                            # Add to result
                            logs.append({
                                "level": log_level,
                                "message": message,
                                "timestamp": timestamp_str,
                                "context": {"logger": logger_name}
                            })
                    except Exception as e:
                        # Skip malformed lines
                        continue
            
            # Sort by timestamp (newest first) and limit results
            logs.sort(key=lambda x: x["timestamp"], reverse=True)
            return logs[:limit]
        except Exception as e:
            logger.error(f"Error reading fallback log file: {e}")
            return []
    
    def _get_log_level(self, level: str) -> int:
        """Convert string log level to numeric value."""
        if isinstance(level, int):
            return level
            
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        return level_map.get(level.upper(), logging.INFO)
    
    def _to_hermes_level(self, level: Union[str, int]) -> "LogLevel":
        """Convert standard log level to Hermes LogLevel."""
        if not self.hermes_available:
            return level
            
        if isinstance(level, int):
            # Convert numeric level to string
            level_map = {
                logging.DEBUG: "DEBUG",
                logging.INFO: "INFO",
                logging.WARNING: "WARNING",
                logging.ERROR: "ERROR",
                logging.CRITICAL: "CRITICAL"
            }
            level = level_map.get(level, "INFO")
        
        # Convert string to Hermes LogLevel
        level_map = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR,
            "CRITICAL": LogLevel.CRITICAL
        }
        
        return level_map.get(level.upper(), LogLevel.INFO)


# For integration testing
def main():
    """Main function for testing the logging adapter."""
    # Initialize the logging adapter
    log_adapter = LoggingAdapter(client_id="test")
    
    # Log some messages
    log_adapter.debug("This is a debug message")
    log_adapter.info("This is an info message", context={"system": "file_system"})
    log_adapter.warning("This is a warning message", component="storage")
    log_adapter.error("This is an error message", source_file=__file__, source_line=306)
    log_adapter.critical("This is a critical message", context={"error_code": 500})
    
    # Get recent logs
    logs = log_adapter.get_logs(level="WARNING", limit=10)
    
    print("\nRecent WARNING+ logs:")
    for log in logs:
        print(f"{log['timestamp']} - {log['level']} - {log['message']}")


if __name__ == "__main__":
    # Run the test
    main()