"""
LanceDB vector store package for Engram memory system.

This package provides a vector store implementation using LanceDB for high-performance 
similarity search, working well on both CPU and GPU platforms.
"""

from .base.store import VectorStore
from .embedding.simple import SimpleEmbedding

__all__ = ['VectorStore', 'SimpleEmbedding']