"""
Adapters for different LLM providers.
"""

from .base import BaseAdapter
from .rhetor import RhetorAdapter
from .fallback import LocalFallbackAdapter

# Create an alias for backward compatibility
FallbackAdapter = LocalFallbackAdapter

__all__ = ['BaseAdapter', 'RhetorAdapter', 'LocalFallbackAdapter', 'FallbackAdapter']