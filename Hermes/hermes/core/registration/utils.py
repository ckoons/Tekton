"""
Registration Utilities - Helper functions for the registration system.

This module provides utility functions used in the Unified Registration Protocol.
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional

# Configure logger
logger = logging.getLogger(__name__)

def generate_component_id(name: str, component_type: str) -> str:
    """
    Generate a unique component ID based on name and type.
    
    Args:
        name: Component name
        component_type: Component type
        
    Returns:
        Unique component ID
    """
    base = f"{component_type}-{name.lower().replace(' ', '-')}"
    unique = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for uniqueness
    return f"{base}-{unique}"

def is_token_valid(token_payload: Dict[str, Any]) -> bool:
    """
    Check if a token payload is valid based on expiration time.
    
    Args:
        token_payload: Token payload to check
        
    Returns:
        True if token is valid
    """
    if not token_payload or "exp" not in token_payload:
        return False
        
    current_time = int(time.time())
    return current_time <= token_payload["exp"]

def format_component_info(component_data: Dict[str, Any]) -> str:
    """
    Format component information for display.
    
    Args:
        component_data: Component data to format
        
    Returns:
        Formatted component information string
    """
    name = component_data.get("name", "Unknown")
    component_id = component_data.get("component_id", "Unknown")
    component_type = component_data.get("type", "Unknown")
    version = component_data.get("version", "Unknown")
    capabilities = component_data.get("capabilities", [])
    
    capabilities_str = ", ".join(capabilities) if capabilities else "None"
    
    return f"{name} ({component_id})\nType: {component_type}\nVersion: {version}\nCapabilities: {capabilities_str}"

def calculate_token_lifetime(expires_at: int) -> int:
    """
    Calculate remaining token lifetime in seconds.
    
    Args:
        expires_at: Token expiration timestamp
        
    Returns:
        Remaining token lifetime in seconds (0 if expired)
    """
    current_time = int(time.time())
    remaining = expires_at - current_time
    return max(0, remaining)  # Don't return negative values