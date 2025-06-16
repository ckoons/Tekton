#!/usr/bin/env python3
"""
Memory Service - Core memory functionality for Engram

This module provides memory storage and retrieval with namespace support, allowing
AI to maintain different types of memories (conversations, thinking, longterm).
"""

# Version and configuration
__version__ = "1.0.0"

# Re-export the main class and essential components
from engram.core.memory.base import MemoryService
from engram.core.memory.compartments import (
    create_compartment,
    activate_compartment,
    deactivate_compartment,
    set_compartment_expiration,
    list_compartments
)
from engram.core.memory.search import search_memory, get_relevant_context

# Export standard namespaces
STANDARD_NAMESPACES = ["conversations", "thinking", "longterm", "projects", "compartments", "session"]

# Import latent space components
from engram.core.memory.latent_space import LatentMemorySpace, LatentSpaceManager, ThoughtState

# Export the main classes
__all__ = [
    "MemoryService",
    "STANDARD_NAMESPACES",
    "create_compartment",
    "activate_compartment",
    "deactivate_compartment",
    "set_compartment_expiration",
    "list_compartments",
    "search_memory",
    "get_relevant_context",
    "LatentMemorySpace",
    "LatentSpaceManager",
    "ThoughtState"
]
