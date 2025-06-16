"""Helper functions for the Rhetor CLI.

This module provides utility functions for formatting and displaying
information in the Rhetor CLI.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any


def format_timestamp(timestamp: float) -> str:
    """Format a timestamp as a human-readable date.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Formatted date string
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def parse_key_value_pairs(pairs_str: str) -> Dict[str, str]:
    """Parse a string of key=value pairs separated by commas.
    
    Args:
        pairs_str: String in the format "key1=value1,key2=value2,..."
        
    Returns:
        Dictionary of key-value pairs
    """
    result = {}
    if not pairs_str:
        return result
        
    for pair in pairs_str.split(","):
        key, value = pair.split("=", 1)
        result[key.strip()] = value.strip()
    
    return result