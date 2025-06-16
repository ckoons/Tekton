"""
Latent Memory Space Module

This package provides latent space reasoning capabilities for Engram.
It allows for storing, refining, and finalizing thoughts in a
dedicated memory space for iterative reasoning.
"""

from .states import ThoughtState
from .space import LatentMemorySpace
from .manager import LatentSpaceManager

# Export main classes
__all__ = [
    'ThoughtState', 
    'LatentMemorySpace', 
    'LatentSpaceManager'
]