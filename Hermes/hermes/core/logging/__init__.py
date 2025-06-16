"""
Centralized Logging System - Core logging functionality for Tekton components.

This module implements the Centralized Logging System (CLS) for Tekton components,
providing structured, schema-versioned logging with effective timestamps and
comprehensive indexing capabilities.

This module has been refactored into a more modular structure.
It now serves as a compatibility layer that imports from the new structure.
"""

import json
import logging
import time
import uuid
import os
import datetime
import threading
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable, Set, Tuple
from enum import Enum, auto
from dataclasses import dataclass, field, asdict

# Import from refactored structure
from hermes.core.logging.base.levels import LogLevel
from hermes.core.logging.base.entry import LogEntry
from hermes.core.logging.storage.file_storage import LogStorage
from hermes.core.logging.management.manager import LogManager
from hermes.core.logging.interface.logger import Logger
from hermes.core.logging.utils.helpers import init_logging, get_logger

# Re-export all classes and functions for backward compatibility
__all__ = [
    'LogLevel',
    'LogEntry',
    'LogStorage',
    'LogManager',
    'Logger',
    'init_logging',
    'get_logger'
]

# Standard Python logger for internal use
_internal_logger = logging.getLogger(__name__)