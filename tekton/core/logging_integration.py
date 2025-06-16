#!/usr/bin/env python3
"""
Centralized Logging Integration Module

This module provides standardized logging integration for all Tekton components,
enabling centralized log collection, filtering, and aggregation.

This file re-exports functionality from the modular logging package.
"""

# Re-export from modular implementation
from .logging.models import LogLevel, LogCategory, StructuredLogRecord
from .logging.handlers import LogHandler, ConsoleLogHandler, FileLogHandler, HermesLogHandler
from .logging.manager import LogManager, get_logger, configure_logging

# For backward compatibility
__all__ = [
    "LogLevel",
    "LogCategory",
    "StructuredLogRecord",
    "LogHandler",
    "ConsoleLogHandler",
    "FileLogHandler",
    "HermesLogHandler",
    "LogManager",
    "get_logger",
    "configure_logging"
]

# Example usage is now in logging/examples.py