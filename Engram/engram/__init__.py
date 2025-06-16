"""
Engram - Persistent Memory Traces Across Sessions

A lightweight system providing AI with persistent memory traces,
enabling continuous conversation and growth across sessions.

Simple usage:
    from engram import Memory
    
    mem = Memory()
    await mem.store("Important thought")
    results = await mem.recall("thought")
"""

__version__ = "0.7.0"

# Export the simple API as the primary interface
from .simple import Memory, MemoryItem, quick_memory

__all__ = ['Memory', 'MemoryItem', 'quick_memory']