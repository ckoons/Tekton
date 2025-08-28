"""
Memory Middleware for CI Memory Integration
Provides transparent memory injection and extraction for Claude and other CIs.
"""

from .hook_manager import HookManager
from .memory_injector import MemoryInjector
from .memory_extractor import MemoryExtractor
from .habit_trainer import HabitTrainer
from .memory_phases import MemoryPhaseManager

__all__ = [
    'HookManager',
    'MemoryInjector',
    'MemoryExtractor',
    'HabitTrainer',
    'MemoryPhaseManager'
]