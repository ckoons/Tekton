"""
Utility functions for the Tekton Centralized Logging System.

This module provides utility functions for logging, including initialization
and logger creation.
"""

import logging
from typing import Dict, List, Any, Optional, Union

from hermes.core.logging.base.levels import LogLevel
from hermes.core.logging.management.manager import LogManager
from hermes.core.logging.interface.logger import Logger

# Global log manager instance
_global_log_manager: Optional[LogManager] = None


def init_logging(
    storage_path: Optional[str] = None,
    console_output: bool = True,
    console_level: Union[LogLevel, str] = LogLevel.INFO
) -> LogManager:
    """
    Initialize the global logging system.
    
    Args:
        storage_path: Path to store log files
        console_output: Whether to output logs to console
        console_level: Minimum level for console output
        
    Returns:
        LogManager instance
    """
    global _global_log_manager
    
    # Convert string level to LogLevel if needed
    if isinstance(console_level, str):
        console_level = LogLevel.from_string(console_level)
    
    # Create log manager
    _global_log_manager = LogManager(
        storage_path=storage_path,
        console_output=console_output,
        console_level=console_level
    )
    
    return _global_log_manager


def get_logger(
    component: str,
    client_id: Optional[str] = None,
    default_context: Optional[Dict[str, Any]] = None
) -> Logger:
    """
    Get a logger for a component.
    
    Args:
        component: Component name
        client_id: Optional client ID
        default_context: Default context for all log entries
        
    Returns:
        Logger instance
    """
    global _global_log_manager
    
    # Initialize global log manager if not already initialized
    if _global_log_manager is None:
        init_logging()
    
    # Create logger
    return Logger(
        component=component,
        log_manager=_global_log_manager,
        client_id=client_id,
        default_context=default_context
    )