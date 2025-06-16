"""
Engram Core Module

This package contains the core functionality of the Engram memory system, including:
- Memory service for persistent storage
- Structured memory with organization and importance ranking
- Nexus interface for AI assistants
- FAISS-based vector storage for efficient semantic search
- Latent space reasoning for iterative thought refinement
"""

__version__ = "0.3.0"

# Import the FAISS-based memory implementation
from engram.core.memory_faiss import MemoryService
from engram.core.memory import LatentMemorySpace, LatentSpaceManager, ThoughtState
from engram.core.latent_interface import LatentInterface
from engram.core.engram_component import EngramComponent

__all__ = [
    "MemoryService", 
    "LatentMemorySpace", 
    "LatentSpaceManager", 
    "ThoughtState",
    "LatentInterface",
    "EngramComponent"
]