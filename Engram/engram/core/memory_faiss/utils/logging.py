#!/usr/bin/env python3
"""
Logging configuration utilities
"""

import logging
from typing import Optional

def setup_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Get logger
    logger = logging.getLogger(name)
    
    return logger