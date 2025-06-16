#!/usr/bin/env python3
"""
Structured Memory Base

Provides the main StructuredMemory class for file-based memory management
with organization and importance ranking.

This module has been refactored into a modular structure. This file is kept for
backward compatibility.
"""

# Re-export from the refactored structure
from engram.core.structured.memory.base import StructuredMemory

import logging
logger = logging.getLogger("engram.structured.base")