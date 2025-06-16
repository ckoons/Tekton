"""
Models package for handling external AI model interactions.

This package provides adapters and management for various AI model providers 
including Anthropic, OpenAI, and local models.
"""

from .manager import ModelManager, get_model_manager, initialize_from_env
from .adapters.base import ModelAdapter, ModelCapability, AdapterHealthStatus

__all__ = [
    'ModelManager',
    'get_model_manager',
    'initialize_from_env',
    'ModelAdapter',
    'ModelCapability',
    'AdapterHealthStatus'
]