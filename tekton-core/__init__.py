"""Tekton Core - Shared components for the Tekton system.

This package provides core functionality shared across all Tekton components,
including hardware-optimized vector database implementations.
"""

__version__ = "0.1.0"

# Export hardware detection
from tekton.core.vector_store import get_vector_store, HardwareType, detect_hardware
