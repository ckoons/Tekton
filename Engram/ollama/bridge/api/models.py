#!/usr/bin/env python3
"""
Ollama Model Management and Capabilities
This module provides functions for working with Ollama model capabilities.
"""

import sys
import os
from typing import Dict, List, Any, Optional

# Import system prompts module for model capabilities
try:
    # Try local import first
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, script_dir)
    
    from ollama_system_prompts import (
        get_memory_system_prompt,
        get_communication_system_prompt, 
        get_combined_system_prompt,
        get_model_capabilities,
        MODEL_CAPABILITIES
    )
    SYSTEM_PROMPTS_AVAILABLE = True
except ImportError:
    print("Warning: Ollama system prompts not available")
    SYSTEM_PROMPTS_AVAILABLE = False
    
    # Provide fallback definitions
    MODEL_CAPABILITIES = {
        "default": {
            "memory_cmds": ["REMEMBER", "SEARCH", "RETRIEVE", "CONTEXT", "SEMANTIC", "FORGET"],
            "comm_cmds": ["SEND", "CHECK"],
            "supports_vector": False,
            "persona": "Echo"
        }
    }
    
    def get_model_capabilities(model_name: str) -> Dict:
        """Fallback for getting model capabilities."""
        return MODEL_CAPABILITIES["default"]
    
    def get_memory_system_prompt(model_name: str) -> str:
        """Fallback for memory system prompt."""
        return """You have access to a memory system that can store and retrieve information.
To use this system, include special commands in your responses:

- To store information: REMEMBER: {information to remember}
- To search for information: SEARCH: {search term}
- To retrieve recent memories: RETRIEVE: {number of memories}
- To get context-relevant memories: CONTEXT: {context description}
- To find semantically similar memories: SEMANTIC: {query}

Your memory commands will be processed automatically. The command format is flexible:
- Standard format: REMEMBER: information
- Markdown format: **REMEMBER**: information
- With or without colons: REMEMBER information

Always place memory commands on their own line to ensure they are processed correctly.
When you use these commands, they will be processed and removed from your visible response."""
    
    def get_communication_system_prompt(model_name: str, available_models: Optional[List[str]] = None) -> str:
        """Fallback for communication system prompt."""
        return """You are Echo, an AI assistant with the ability to communicate with other AI models.
Your messages to other AIs are stored in memory for asynchronous communication.

To communicate with other AIs, use these commands in your responses:

- To send a message: SEND TO [AI_NAME]: {message}
- To check for messages: CHECK MESSAGES FROM [AI_NAME]

Available AIs for communication:
- Claude

Communication commands will be processed automatically and then removed from your visible response."""
    
    def get_combined_system_prompt(model_name: str, available_models: Optional[List[str]] = None) -> str:
        """Fallback for combined system prompt."""
        memory = get_memory_system_prompt(model_name)
        comm = get_communication_system_prompt(model_name, available_models)
        return f"""You are Echo, an AI assistant with access to a memory system and communication network.
You can store information in memory and communicate with other AI models.

=== MEMORY CAPABILITIES ===
{memory}

=== COMMUNICATION CAPABILITIES ===
{comm}

Remember that you have a distinct identity as Echo when communicating with other AI models.
Your communications should reflect your unique perspective and capabilities."""

def get_system_prompt(model_name: str, prompt_type: str = "combined", 
                     available_models: Optional[List[str]] = None,
                     custom_system_prompt: str = "") -> str:
    """
    Get the appropriate system prompt based on prompt type and model.
    
    Args:
        model_name: The name of the Ollama model
        prompt_type: Type of system prompt ("memory", "communication", "combined")
        available_models: Optional list of available AI models for communication
        custom_system_prompt: Optional custom system prompt to use instead
        
    Returns:
        String containing the system prompt
    """
    if custom_system_prompt:
        return custom_system_prompt
        
    if prompt_type == "memory":
        return get_memory_system_prompt(model_name)
    elif prompt_type == "communication":
        return get_communication_system_prompt(model_name, available_models)
    else:  # default to combined
        return get_combined_system_prompt(model_name, available_models)

def get_model_persona(model_name: str) -> str:
    """Get the persona name for a given model."""
    try:
        capabilities = get_model_capabilities(model_name)
        return capabilities.get("persona", "Echo")
    except Exception:
        return "Echo"