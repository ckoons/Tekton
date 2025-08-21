#!/usr/bin/env python3
"""
Model Configuration Module

This module provides configuration defaults and constants for the models package.
"""

import os
from shared.env import TektonEnviron
from typing import Dict, Any, Optional

# Default configurations for different model providers
DEFAULT_CONFIGS = {
    "anthropic": {
        "api_key": TektonEnviron.get("ANTHROPIC_API_KEY", ""),
        "model": TektonEnviron.get("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "openai": {
        "api_key": TektonEnviron.get("OPENAI_API_KEY", ""),
        "model": TektonEnviron.get("OPENAI_MODEL", "gpt-4o"),
        "embedding_model": "text-embedding-3-large",
        "max_tokens": 1000,
        "temperature": 0.7
    },
    "local": {
        "endpoint": TektonEnviron.get("LOCAL_MODEL_ENDPOINT", "http://localhost:11434"),
        "model": TektonEnviron.get("LOCAL_MODEL", "llama3"),
        "max_tokens": 1000,
        "temperature": 0.7
    }
}

# Model capabilities by provider and model
MODEL_CAPABILITIES = {
    "anthropic": {
        "claude-3-opus-20240229": {
            "max_tokens": 4096,
            "context_window": 200000,
            "supports_streaming": True,
            "supports_vision": True,
            "supports_embeddings": False,
            "supports_json_mode": True
        },
        "claude-3-sonnet-20240229": {
            "max_tokens": 4096,
            "context_window": 200000,
            "supports_streaming": True,
            "supports_vision": True,
            "supports_embeddings": False,
            "supports_json_mode": True
        },
        "claude-3-haiku-20240307": {
            "max_tokens": 4096, 
            "context_window": 200000,
            "supports_streaming": True,
            "supports_vision": True,
            "supports_embeddings": False,
            "supports_json_mode": True
        },
        "claude-3-5-sonnet-20240620": {
            "max_tokens": 4096,
            "context_window": 200000,
            "supports_streaming": True,
            "supports_vision": True,
            "supports_embeddings": False,
            "supports_json_mode": True
        },
        "claude-3-7-sonnet-20240620": {
            "max_tokens": 4096,
            "context_window": 200000,
            "supports_streaming": True,
            "supports_vision": True,
            "supports_embeddings": False,
            "supports_json_mode": True
        }
    },
    "openai": {
        "gpt-4o": {
            "max_tokens": 4096,
            "context_window": 128000,
            "supports_streaming": True,
            "supports_vision": True,
            "supports_embeddings": False,
            "supports_json_mode": True,
            "supports_function_calling": True
        },
        "gpt-4-turbo": {
            "max_tokens": 4096,
            "context_window": 128000,
            "supports_streaming": True,
            "supports_vision": True,
            "supports_embeddings": False,
            "supports_json_mode": True,
            "supports_function_calling": True
        },
        "gpt-4": {
            "max_tokens": 4096,
            "context_window": 8192,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_embeddings": False,
            "supports_json_mode": True,
            "supports_function_calling": True
        },
        "gpt-3.5-turbo": {
            "max_tokens": 4096,
            "context_window": 16385,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_embeddings": False,
            "supports_json_mode": True,
            "supports_function_calling": True
        }
    },
    "local": {
        "llama3": {
            "max_tokens": 4096,
            "context_window": 8192,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_embeddings": True,
            "supports_json_mode": False
        },
        "mixtral": {
            "max_tokens": 4096,
            "context_window": 32768,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_embeddings": True,
            "supports_json_mode": False
        },
        "codellama": {
            "max_tokens": 4096,
            "context_window": 16384,
            "supports_streaming": True,
            "supports_vision": False,
            "supports_embeddings": True,
            "supports_json_mode": False
        }
    }
}


def get_model_config(provider: str, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Get configuration for a specific model.
    
    Args:
        provider: The provider name (anthropic, openai, local)
        model: Optional model name
        
    Returns:
        Configuration dictionary
    """
    config = DEFAULT_CONFIGS.get(provider, {}).copy()
    
    # If model specified, update with model-specific capabilities
    if model and provider in MODEL_CAPABILITIES and model in MODEL_CAPABILITIES[provider]:
        config.update(MODEL_CAPABILITIES[provider][model])
    elif not model and provider in MODEL_CAPABILITIES:
        # Use default model from config
        default_model = config.get("model")
        if default_model in MODEL_CAPABILITIES[provider]:
            config.update(MODEL_CAPABILITIES[provider][default_model])
    
    return config