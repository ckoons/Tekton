"""
Hermes Memory Adapter for Engram.

This package provides integration between Engram memory and Hermes database services,
allowing Engram to leverage Hermes's centralized database infrastructure.
"""

from .core.service import HermesMemoryService
from .core.imports import HAS_HERMES

# For backwards compatibility, allow this to be imported as MemoryService
MemoryService = HermesMemoryService

__all__ = ['HermesMemoryService', 'MemoryService', 'HAS_HERMES']