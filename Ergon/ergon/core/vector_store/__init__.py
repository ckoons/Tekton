"""
Vector store module for Ergon.

This module provides vector storage capabilities for the Ergon component.
"""

from .faiss_store import FAISSDocumentStore

__all__ = ['FAISSDocumentStore']