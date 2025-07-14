"""
File-based storage for Tekton Centralized Logging System.

This module provides a file-based storage implementation for log entries,
organized by date and component.
"""

import os
import json
import time
import threading
import datetime
import logging
from typing import Dict, List, Any, Optional
from shared.env import TektonEnviron

from hermes.core.logging.base.entry import LogEntry
from hermes.core.logging.base.levels import LogLevel

# Standard Python logger for internal use
_internal_logger = logging.getLogger(__name__)


class LogStorage:
    """
    Storage interface for log entries.
    
    This class provides methods for storing and retrieving log entries
    from a persistent storage backend.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the log storage.
        
        Args:
            storage_path: Path to store log files (defaults to ~/.tekton/logs)
        """
        self.storage_path = storage_path or TektonEnviron.get('TEKTON_LOG_DIR', 
                                                            os.path.join(TektonEnviron.get('TEKTON_ROOT'), 
                                                                        '.tekton', 'logs'))
        os.makedirs(self.storage_path, exist_ok=True)
        
        # In-memory cache for recent logs (limited size)
        self.cache: List[LogEntry] = []
        self.cache_size = 1000
        self.cache_lock = threading.RLock()
        
        _internal_logger.info(f"Log storage initialized at {self.storage_path}")
    
    def store(self, log_entry: LogEntry) -> bool:
        """
        Store a log entry.
        
        Args:
            log_entry: Log entry to store
            
        Returns:
            True if storage successful
        """
        try:
            # Add to in-memory cache
            with self.cache_lock:
                self.cache.append(log_entry)
                # Trim cache if needed
                if len(self.cache) > self.cache_size:
                    self.cache = self.cache[-self.cache_size:]
            
            # Store to file
            # Group logs by date for easier management
            date_str = datetime.datetime.fromtimestamp(
                log_entry.timestamp
            ).strftime("%Y-%m-%d")
            
            # Create date directory if it doesn't exist
            date_dir = os.path.join(self.storage_path, date_str)
            os.makedirs(date_dir, exist_ok=True)
            
            # Determine log file name based on component
            component_name = log_entry.component.replace("/", "_")
            log_file = os.path.join(date_dir, f"{component_name}.jsonl")
            
            # Append to log file
            with open(log_file, "a") as f:
                f.write(log_entry.to_json() + "\n")
            
            return True
            
        except Exception as e:
            _internal_logger.error(f"Error storing log entry: {e}")
            return False
    
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
        # Set default values
        now = time.time()
        start_time = start_time or (now - 86400)  # Default to last 24 hours
        end_time = end_time or now
        
        # For simple queries, check the in-memory cache first
        with self.cache_lock:
            matching_entries = []
            
            for entry in reversed(self.cache):
                # Check if entry is within time range
                if entry.timestamp < start_time or entry.timestamp > end_time:
                    continue
                
                # Check if entry is from specified components
                if components and entry.component not in components:
                    continue
                
                # Check if entry has specified levels
                if levels and entry.level not in levels:
                    continue
                
                matching_entries.append(entry)
                
                # Limit results
                if len(matching_entries) >= limit:
                    break
            
            # If we have enough entries from cache, return them
            if len(matching_entries) >= limit:
                return matching_entries
        
        # If not enough entries in cache, check log files
        # Convert timestamps to dates
        start_date = datetime.datetime.fromtimestamp(start_time).date()
        end_date = datetime.datetime.fromtimestamp(end_time).date()
        current_date = start_date
        
        # Iterate through dates
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            date_dir = os.path.join(self.storage_path, date_str)
            
            # Check if directory exists
            if os.path.exists(date_dir):
                # Get log files
                log_files = []
                
                if components:
                    # Only include specified components
                    for component in components:
                        component_name = component.replace("/", "_")
                        file_path = os.path.join(date_dir, f"{component_name}.jsonl")
                        if os.path.exists(file_path):
                            log_files.append(file_path)
                else:
                    # Include all components
                    log_files = [
                        os.path.join(date_dir, f) for f in os.listdir(date_dir)
                        if f.endswith(".jsonl")
                    ]
                
                # Process log files
                for file_path in log_files:
                    try:
                        with open(file_path, "r") as f:
                            for line in f:
                                try:
                                    entry = LogEntry.from_json(line.strip())
                                    
                                    # Check if entry is within time range
                                    if entry.timestamp < start_time or entry.timestamp > end_time:
                                        continue
                                    
                                    # Check if entry has specified levels
                                    if levels and entry.level not in levels:
                                        continue
                                    
                                    matching_entries.append(entry)
                                    
                                    # Limit results
                                    if len(matching_entries) >= limit:
                                        break
                                        
                                except json.JSONDecodeError:
                                    continue
                                    
                        # Check if we have enough entries
                        if len(matching_entries) >= limit:
                            break
                            
                    except Exception as e:
                        _internal_logger.error(f"Error reading log file {file_path}: {e}")
            
            # Move to next date
            current_date += datetime.timedelta(days=1)
            
            # Check if we have enough entries
            if len(matching_entries) >= limit:
                break
        
        # Sort entries by timestamp (newest first)
        matching_entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        return matching_entries[:limit]