"""
Hermes - Vector Operations and Messaging Framework for Tekton

This module provides vector operations and inter-component messaging for the Tekton ecosystem.
"""

# Version information
__version__ = "0.1.0"

# Import the adapters module to ensure initialization
from . import adapters

from .core.database.database_types import DatabaseType
# Define package exports
from .core.database.database_types import DatabaseBackend
__all__ = ["adapters"]
from .core.database.adapters import VectorDatabaseAdapter
from .api.database.client_base import BaseRequest
from .core.logging.base.levels import LogLevel
from .core.database.manager import DatabaseManager
from .core.logging.base.entry import LogEntry
from .core.database.adapters import GraphDatabaseAdapter