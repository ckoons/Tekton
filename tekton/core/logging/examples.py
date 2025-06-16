#!/usr/bin/env python3
"""
Logging Examples Module

This module provides examples of using the logging system.
"""

from .models import LogLevel, LogCategory
from .manager import configure_logging


def run_examples():
    """Run examples of logging usage."""
    # Configure logging
    logger = configure_logging(
        component_id="example.component",
        console=True,
        file_path="/tmp/example-component.log",
        min_level=LogLevel.DEBUG
    )
    
    # Log messages
    logger.debug("This is a debug message")
    logger.info("This is an info message", category=LogCategory.STARTUP)
    logger.warning("This is a warning message", context={"key": "value"})
    logger.error("This is an error message", category=LogCategory.SYSTEM)
    
    # Log with correlation context
    logger.set_correlation_context(correlation_id="123456", request_id="abcdef")
    logger.info("This is a message with correlation context")
    logger.clear_correlation_context()
    
    # Log exception
    try:
        1 / 0
    except Exception as e:
        logger.exception("An error occurred", category=LogCategory.SYSTEM)
        
    # Shutdown
    logger.shutdown()


if __name__ == "__main__":
    run_examples()