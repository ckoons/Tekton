#!/usr/bin/env python3
"""
External Model Integration Module

This module provides a standardized interface for working with external AI models,
with adapters for common model providers like Anthropic, OpenAI, and local models.
It includes intelligent routing and fallback capabilities for improved reliability.
"""

import warnings

# Re-export from new module structure
from .models import (
    ModelAdapter,
    ModelCapability,
    AdapterHealthStatus,
    get_model_manager,
    initialize_from_env
)
from .models.adapters import (
    AnthropicAdapter,
    OpenAIAdapter,
    LocalModelAdapter
)
from .models.manager import ModelManager

# Show deprecation warning
warnings.warn(
    "The external_models module is deprecated and will be removed in a future version. "
    "Please use the new models package instead.",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility
__all__ = [
    'ModelAdapter',
    'ModelCapability',
    'AdapterHealthStatus',
    'AnthropicAdapter',
    'OpenAIAdapter',
    'LocalModelAdapter',
    'ModelManager',
    'get_model_manager',
    'initialize_from_env'
]