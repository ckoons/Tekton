#!/usr/bin/env python3
"""
Structured Memory Utilities

Utility functions for the structured memory system.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger("engram.structured.utils")

def generate_memory_id(category: str, content: str) -> str:
    """
    Generate a unique ID for a memory.
    
    Args:
        category: The memory category
        content: The memory content
        
    Returns:
        Unique memory ID with category prefix
    """
    timestamp = int(time.time())
    return f"{category}-{timestamp}-{hash(content) % 10000}"

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Loaded JSON data or empty dict if file doesn't exist
    """
    if file_path.exists():
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON from {file_path}: {e}")
    return {}

def save_json_file(file_path: Path, data: Dict[str, Any]) -> bool:
    """
    Save JSON data to a file.
    
    Args:
        file_path: Path to save JSON file
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

def format_memory_digest(memories: List[Dict[str, Any]]) -> List[str]:
    """
    Format memories for a digest.
    
    Args:
        memories: List of memory dictionaries
        
    Returns:
        List of formatted memory strings
    """
    formatted = []
    
    for memory in memories:
        # Create visual importance indicator
        importance_str = "★" * memory["importance"]
        
        # Format timestamp
        timestamp = memory.get("metadata", {}).get("timestamp", "")
        if timestamp:
            try:
                date_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                date_str = "Unknown date"
        else:
            date_str = "Unknown date"
        
        # Format memory line
        formatted.append(f"- {importance_str} {memory['content']} ({date_str})")
    
    return formatted

def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 5) -> List[str]:
    """
    Extract potential keywords from text.
    
    Args:
        text: Input text
        min_length: Minimum word length to consider
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
    """
    # Common words to filter out
    common_words = {
        "this", "that", "what", "with", "from", "have", "there", "they", 
        "their", "should", "would", "could", "about", "which", "where",
        "when", "how", "why", "who", "will", "more", "much", "such",
        "than", "then", "these", "those", "some", "very", "just"
    }
    
    # Extract words and filter
    words = text.lower().split()
    keywords = [word for word in words if len(word) > min_length and word not in common_words]
    
    # Remove duplicates and limit number
    unique_keywords = list(dict.fromkeys(keywords))
    return unique_keywords[:max_keywords]