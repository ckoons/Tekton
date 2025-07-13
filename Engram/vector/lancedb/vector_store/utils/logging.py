"""
Logging utilities for the LanceDB vector store.

This module provides logging configuration and utility functions.
"""

import logging
from pathlib import Path

# Add Engram to path for imports if needed
def configure_path():
    """Add Engram directory to system path if needed."""
    ENGRAM_DIR = str(Path(__file__).parent.parent.parent.parent.parent)
    import sys
    if ENGRAM_DIR not in sys.path:
        sys.path.insert(0, ENGRAM_DIR)
        get_logger().debug(f"Added {ENGRAM_DIR} to Python path")
        return True
    return False

# Configure logging
def get_logger(name="lancedb_vector_store"):
    """
    Get a configured logger.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if handlers aren't already set up
    if not logger.handlers:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    return logger

# Log versions of dependencies
def log_versions(logger=None):
    """
    Log versions of dependencies.
    
    Args:
        logger: Logger instance to use, or None to create one
    """
    if logger is None:
        logger = get_logger()
    
    try:
        import lancedb
        logger.info(f"LanceDB version: {lancedb.__version__}")
    except (ImportError, AttributeError):
        logger.warning("Failed to get LanceDB version")
    
    try:
        import pyarrow as pa
        logger.info(f"PyArrow version: {pa.__version__}")
    except (ImportError, AttributeError):
        logger.warning("Failed to get PyArrow version")
    
    try:
        import numpy as np
        logger.info(f"NumPy version: {np.__version__}")
    except (ImportError, AttributeError):
        logger.warning("Failed to get NumPy version")
    
    # Check for GPU support
    try:
        import torch
        if torch.cuda.is_available():
            logger.info(f"GPU support available: {torch.cuda.get_device_name(0)}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            logger.info(f"Apple Metal support available")
        else:
            logger.info("No GPU support detected, using CPU")
    except ImportError:
        logger.info("PyTorch not available, using CPU")