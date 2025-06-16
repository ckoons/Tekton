#!/usr/bin/env python3
"""
Hermes Memory Adapter - Integrate Engram memory with Hermes database services

This module provides a MemoryService implementation that uses Hermes's
centralized database services for storage, providing enhanced vector
search capabilities and cross-component integration.

This module has been refactored into a more modular structure.
It now serves as a compatibility layer that imports from the new structure.
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.integrations.hermes")

# Import from refactored structure
from engram.integrations.hermes.memory_adapter import HermesMemoryService, MemoryService, HAS_HERMES

# Re-export from the package
__all__ = ['HermesMemoryService', 'MemoryService', 'HAS_HERMES']