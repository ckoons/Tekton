"""
Storage module for Tekton core.

This module defines the standardized storage interfaces used across
Tekton components, supporting vector, graph, and key-value storage.
"""

from .base import (
    BaseStorage,
    BaseVectorStorage,
    BaseGraphStorage,
    BaseKVStorage,
    StorageNamespace
)

__all__ = [
    "BaseStorage",
    "BaseVectorStorage",
    "BaseGraphStorage",
    "BaseKVStorage",
    "StorageNamespace"
]