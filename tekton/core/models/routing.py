#!/usr/bin/env python3
"""
Model Routing Module

This module provides functions for intelligently routing requests to the most
appropriate model based on task type, model capabilities, and health.
"""

import logging
from typing import Dict, List, Any, Optional, Callable

# Configure logger
logger = logging.getLogger("tekton.models.routing")

# Define model preferences for different task types
MODEL_PREFERENCES = {
    "code": [
        # Models best for code generation
        (lambda name: "claude" in name and "opus" in name),  # Claude Opus
        (lambda name: "gpt-4" in name or "gpt4" in name),  # GPT-4 family
        (lambda name: "codellama" in name),  # CodeLlama
        (lambda name: "claude" in name),  # Any Claude
        (lambda name: "local" in name)  # Any local model
    ],
    "creative": [
        # Models best for creative tasks
        (lambda name: "claude" in name and "opus" in name),  # Claude Opus
        (lambda name: "gpt-4" in name or "gpt4" in name),  # GPT-4 family
        (lambda name: "claude" in name),  # Any Claude
        (lambda name: "llama" in name),  # Any Llama
        (lambda name: "local" in name)  # Any local model
    ],
    "analytical": [
        # Models best for analytical tasks
        (lambda name: "claude" in name and "opus" in name),  # Claude Opus
        (lambda name: "gpt-4" in name or "gpt4" in name),  # GPT-4 family
        (lambda name: "claude" in name),  # Any Claude
        (lambda name: "mixtral" in name),  # Mixtral
        (lambda name: "local" in name)  # Any local model
    ],
    # Add more task types as needed
    "embeddings": [
        # Models best for embeddings
        (lambda name: "openai" in name and "embedding" in name),  # OpenAI embeddings
        (lambda name: "local" in name and "llama" in name),  # Local Llama models
        (lambda name: "local" in name),  # Any local model
        (lambda name: "openai" in name)  # Any OpenAI model
    ]
}


def select_model_for_task(
    task_type: Optional[str],
    available_adapters: List[str],
    model_capabilities: Dict[str, Dict[str, Any]]
) -> Optional[str]:
    """
    Select the best model for a specific task.
    
    Args:
        task_type: The type of task (code, creative, analytical, etc.)
        available_adapters: List of available adapter names
        model_capabilities: Dictionary of model capabilities
        
    Returns:
        The name of the selected adapter, or None if no suitable adapter found
    """
    if not task_type:
        task_type = "analytical"  # Default to analytical
        
    # Filter for embedding-capable models if task is embeddings
    if task_type == "embeddings":
        available_adapters = [
            name for name in available_adapters
            if model_capabilities.get(name, {}).get("supports_embeddings", False)
        ]
        
    # Get task-specific preferences
    if task_type in MODEL_PREFERENCES:
        predicates = MODEL_PREFERENCES[task_type]
    else:
        # Default to analytical preferences if task type not specified
        predicates = MODEL_PREFERENCES["analytical"]
    
    # Find the best adapter based on preferences
    for predicate in predicates:
        for name in available_adapters:
            if predicate(name):
                return name
    
    # If no match found, return None
    return None