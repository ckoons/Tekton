#!/usr/bin/env python3
"""
Utility Helper Functions
This module provides utility functions for the Ollama Bridge.
"""

import os
from typing import Dict, Any, List, Optional

def colorize(text: str, color: str) -> str:
    """
    Add color to a string for terminal output.
    
    Args:
        text: The text to colorize
        color: Color name ('red', 'green', 'yellow', 'blue', 'magenta', 'cyan')
        
    Returns:
        Colorized string
    """
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'reset': '\033[0m'
    }
    
    if color in colors:
        return f"{colors[color]}{text}{colors['reset']}"
    return text

def print_colored(text: str, color: str) -> None:
    """Print text with color."""
    print(colorize(text, color))

def set_environment_variables(args: Any) -> None:
    """Set environment variables based on command line args."""
    # Set client ID for Engram
    os.environ["ENGRAM_CLIENT_ID"] = args.client_id
    
    # Set Hermes integration if enabled
    if getattr(args, 'hermes_integration', False):
        os.environ["ENGRAM_USE_HERMES"] = "1"

def format_chat_message(role: str, message: str, model_name: str = "") -> str:
    """
    Format a chat message for display.
    
    Args:
        role: Message role ('user' or 'assistant')
        message: Message content
        model_name: Model name (for assistant messages)
        
    Returns:
        Formatted message string
    """
    if role == "user":
        return f"\nYou: {message}"
    else:
        model_display = model_name if model_name else "Assistant"
        return f"\n{model_display}: {message}"

def should_save_to_memory(user_input: str, assistant_message: str) -> bool:
    """
    Determine if an interaction should be saved to memory.
    
    Args:
        user_input: User input text
        assistant_message: Assistant response text
        
    Returns:
        True if should save, False otherwise
    """
    # Save significant interactions (longer inputs and outputs)
    return len(user_input) > 20 and len(assistant_message) > 50

def format_memory_for_saving(user_input: str, assistant_message: str, model_name: str) -> str:
    """
    Format an interaction for saving to memory.
    
    Args:
        user_input: User input text
        assistant_message: Assistant response text
        model_name: Name of the model used
        
    Returns:
        Formatted memory text
    """
    # Truncate assistant message if too long
    truncated_response = assistant_message[:100] + "..." if len(assistant_message) > 100 else assistant_message
    return f"User asked: '{user_input}' and {model_name} responded: '{truncated_response}'"