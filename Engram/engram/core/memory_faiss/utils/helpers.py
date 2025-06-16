#!/usr/bin/env python3
"""
Helper utilities for memory operations
"""

import os
from typing import Dict, List, Any, Optional, Union

# Check if fallback mode is forced (set by environment variable)
USE_FALLBACK = os.environ.get('ENGRAM_USE_FALLBACK', '').lower() in ('1', 'true', 'yes')

def is_valid_namespace(
    namespace: str, 
    valid_namespaces: List[str], 
    compartments: Dict[str, Dict[str, Any]]
) -> bool:
    """
    Check if a namespace is valid.
    
    Args:
        namespace: The namespace to check
        valid_namespaces: List of valid base namespaces
        compartments: Dictionary of compartments
        
    Returns:
        Boolean indicating if the namespace is valid
    """
    # Check standard namespaces
    if namespace in valid_namespaces:
        return True
    
    # Check compartment namespaces
    if namespace.startswith("compartment-"):
        compartment_id = namespace[len("compartment-"):]
        return compartment_id in compartments
    
    return False

def format_memory_for_storage(
    content: Union[str, List[Dict[str, str]]]
) -> str:
    """
    Format memory content for storage.
    
    Args:
        content: Memory content (string or message list)
        
    Returns:
        Formatted string
    """
    if isinstance(content, list):
        try:
            # Format as conversation
            return "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" 
                for msg in content
            ])
        except Exception as e:
            return str(content)
    
    return content