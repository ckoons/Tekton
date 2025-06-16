#!/usr/bin/env python3
"""
Structured Memory - File-based memory management with organization and importance ranking

This module has been refactored into a more modular structure.
It now serves as a compatibility layer that imports from the new structure.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.structured_memory")

# Import the main StructuredMemory class and related components
from engram.core.structured.base import StructuredMemory
from engram.core.structured.categorization import auto_categorize_memory

# Re-export the main class
__all__ = ["StructuredMemory"]