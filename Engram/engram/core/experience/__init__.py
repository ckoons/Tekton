"""
ESR Experience Layer - Making memory feel natural for CIs.

This module provides the experience layer that transforms mechanical
storage into natural, emotionally-tagged, temporally-aware memories.
"""

from .experience_layer import ExperienceManager, MemoryExperience
from .emotional_context import EmotionalContext, EmotionalTag
from .memory_promises import MemoryPromise, PromiseResolver
from .working_memory import WorkingMemory, ThoughtBuffer

__all__ = [
    'ExperienceManager',
    'MemoryExperience', 
    'EmotionalContext',
    'EmotionalTag',
    'MemoryPromise',
    'PromiseResolver',
    'WorkingMemory',
    'ThoughtBuffer'
]