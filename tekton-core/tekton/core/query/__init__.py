"""
Query module for Tekton core.

This module defines the standardized query interfaces and modes
used across Tekton components.
"""

from .modes import QueryMode, QueryParameters

__all__ = ["QueryMode", "QueryParameters"]