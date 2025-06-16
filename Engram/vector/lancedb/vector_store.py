#!/usr/bin/env python
"""
LanceDB vector store implementation for Engram memory system.
This provides similar functionality to the FAISS vector store
but uses LanceDB for better cross-platform performance.

This module has been refactored into a more modular structure.
It now serves as a compatibility layer that imports from the new structure.
"""

import os
import json
import time
import logging
import numpy as np
import pyarrow as pa
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("lancedb_vector_store")

# Add Engram to path for imports
ENGRAM_DIR = str(Path(__file__).parent.parent.parent)
import sys
if ENGRAM_DIR not in sys.path:
    sys.path.insert(0, ENGRAM_DIR)
    logger.debug(f"Added {ENGRAM_DIR} to Python path")

# Import from refactored structure
from vector.lancedb.vector_store import VectorStore, SimpleEmbedding

# Re-export classes for backward compatibility
__all__ = [
    'VectorStore',
    'SimpleEmbedding'
]