"""Logging utilities for Terma"""

import logging
import sys
from pathlib import Path

def setup_logging(level=logging.INFO, log_file=None):
    """Set up logging for Terma
    
    Args:
        level: Logging level
        log_file: Optional log file path
    
    Returns:
        The configured logger
    """
    logger = logging.getLogger("terma")
    
    # Check if logger already has handlers to prevent duplicate logs
    if logger.hasHandlers():
        # If the logger already has handlers, just set the level and return it
        logger.setLevel(level)
        return logger
    
    # Otherwise, set up the logger
    logger.setLevel(level)
    
    # Prevent propagation to avoid duplicate logs in parent loggers
    logger.propagate = False
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if requested)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
