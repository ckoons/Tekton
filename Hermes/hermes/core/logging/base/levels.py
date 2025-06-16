"""
Log levels for the Tekton Centralized Logging System.

This module defines standardized log levels for Tekton components.
"""

import logging
from enum import Enum, auto


class LogLevel(Enum):
    """Standardized log levels for Tekton components."""
    
    FATAL = 100   # Component is inoperable causing fatal system error
    ERROR = 80    # Component is inoperable, affecting other functionalities
    WARN = 60     # Unexpected event that may disrupt processes
    INFO = 40     # Event that doesn't affect operations
    NORMAL = 30   # System lifecycle events (startup, shutdown, etc.)
    DEBUG = 20    # Details useful for debugging in test environments
    TRACE = 10    # Full execution visibility
    
    @classmethod
    def from_string(cls, level_str: str) -> 'LogLevel':
        """Convert string representation to LogLevel."""
        try:
            return cls[level_str.upper()]
        except KeyError:
            # Default to INFO if level not recognized
            logging.getLogger(__name__).warning(
                f"Unknown log level: {level_str}, defaulting to INFO"
            )
            return cls.INFO
    
    @classmethod
    def to_python_level(cls, level: 'LogLevel') -> int:
        """Convert Tekton log level to Python logging level."""
        mapping = {
            cls.FATAL: logging.CRITICAL,
            cls.ERROR: logging.ERROR,
            cls.WARN: logging.WARNING,
            cls.INFO: logging.INFO,
            cls.NORMAL: logging.INFO,  # Map to INFO since Python doesn't have NORMAL
            cls.DEBUG: logging.DEBUG,
            cls.TRACE: logging.DEBUG   # Map to DEBUG since Python doesn't have TRACE
        }
        return mapping.get(level, logging.INFO)