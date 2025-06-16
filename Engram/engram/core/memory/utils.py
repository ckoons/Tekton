#!/usr/bin/env python3
"""
Memory Service Utilities

Utility functions for the memory service including
formatting, timestamp handling, and helper functions.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger("engram.memory.utils")

def format_content(content: Union[str, List[Dict[str, str]]]) -> str:
    """
    Format content into a string.
    
    Args:
        content: The content to format (string or list of message objects)
        
    Returns:
        Formatted content string
    """
    if isinstance(content, list):
        try:
            # Format as conversation
            return "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" 
                for msg in content
            ])
        except Exception as e:
            logger.error(f"Error formatting conversation: {e}")
            return str(content)
    else:
        return content

def generate_memory_id(namespace: str, content: str) -> str:
    """
    Generate a unique ID for a memory.
    
    Args:
        namespace: The namespace for the memory
        content: The content of the memory
        
    Returns:
        Unique memory ID
    """
    return f"{namespace}-{int(time.time())}-{hash(content) % 10000}"

def load_json_file(file_path: Path) -> Dict:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded JSON data or empty dict if error
    """
    if file_path.exists():
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON from {file_path}: {e}")
    return {}

def save_json_file(file_path: Path, data: Dict) -> bool:
    """
    Save JSON data to a file.
    
    Args:
        file_path: Path to save the JSON file
        data: Data to save
        
    Returns:
        Boolean indicating success
    """
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {e}")
        return False

def parse_expiration_date(expiration_str: Optional[str]) -> Optional[datetime]:
    """
    Parse an expiration date string into a datetime object.
    
    Args:
        expiration_str: ISO format date string or None
        
    Returns:
        Datetime object or None if no expiration
    """
    if not expiration_str:
        return None
        
    try:
        return datetime.fromisoformat(expiration_str)
    except Exception as e:
        logger.error(f"Error parsing expiration date: {e}")
        return None

def is_expired(expiration_date: Optional[datetime]) -> bool:
    """
    Check if an expiration date has passed.
    
    Args:
        expiration_date: Datetime object or None
        
    Returns:
        True if expired, False otherwise
    """
    if expiration_date is None:
        return False
        
    return expiration_date < datetime.now()

def truncate_content(content: str, max_length: int = 500) -> str:
    """
    Truncate content to a maximum length.
    
    Args:
        content: Content string to truncate
        max_length: Maximum length
        
    Returns:
        Truncated content string
    """
    if len(content) > max_length:
        return content[:max_length-3] + "..."
    return content