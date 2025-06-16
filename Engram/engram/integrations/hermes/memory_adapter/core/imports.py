"""
Imports for the Hermes Memory Adapter.

This module handles importing required dependencies,
with fallbacks for when Hermes is not available.
"""

import logging
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logger = logging.getLogger("engram.integrations.hermes")

# Import Hermes database client
try:
    from hermes.utils.database_helper import DatabaseClient
    from hermes.core.database_manager import DatabaseBackend
    HAS_HERMES = True
except ImportError:
    logger.warning("Hermes database services not found, using fallback implementation")
    HAS_HERMES = False