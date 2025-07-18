"""
Introspection module for Claude Code IDE functionality.

Provides real-time Python class and method introspection to prevent
AttributeErrors and method guessing.
"""

from .inspector import TektonInspector
from .cache import IntrospectionCache

__all__ = ['TektonInspector', 'IntrospectionCache']