#!/usr/bin/env python3
"""
Memory Service - Core memory functionality for Engram

This module has been refactored into a more modular structure.
It now serves as a compatibility layer that imports from the new structure.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.memory")

# Resolve circular import by directly importing from specific submodules
from engram.core.memory.base import MemoryService
from engram.core.memory.compartments import (
    create_compartment,
    activate_compartment,
    deactivate_compartment,
    set_compartment_expiration,
    list_compartments
)
from engram.core.memory.search import search_memory, get_relevant_context

# Standard namespaces for compatibility
STANDARD_NAMESPACES = ["conversations", "thinking", "longterm", "projects", "compartments", "session"]

# Vector database configuration for backward compatibility
from engram.core.memory.config import (
    HAS_VECTOR_DB,
    VECTOR_DB_NAME,
    VECTOR_DB_VERSION,
    USE_FALLBACK
)

# Export public symbols
__all__ = [
    "MemoryService",
    "STANDARD_NAMESPACES",
    "HAS_VECTOR_DB",
    "VECTOR_DB_NAME",
    "VECTOR_DB_VERSION",
    "USE_FALLBACK",
    "create_compartment",
    "activate_compartment",
    "deactivate_compartment",
    "set_compartment_expiration",
    "list_compartments",
    "search_memory",
    "get_relevant_context"
]