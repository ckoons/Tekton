"""
Model adapters for different AI providers.

This package contains adapters for various AI model providers including
Anthropic, OpenAI, and local models.
"""

from .base import ModelAdapter, ModelCapability, AdapterHealthStatus
from .anthropic import AnthropicAdapter
from .openai import OpenAIAdapter
from .local import LocalModelAdapter

__all__ = [
    'ModelAdapter',
    'ModelCapability',
    'AdapterHealthStatus',
    'AnthropicAdapter',
    'OpenAIAdapter', 
    'LocalModelAdapter'
]