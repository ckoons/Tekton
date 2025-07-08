#!/usr/bin/env python3
"""
Purpose Matcher for aish
Handles matching of purpose words to terminals for message routing.
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("aish.purpose_matcher")


def match_purpose(word: str, terminals: List[Dict[str, Any]]) -> List[str]:
    """
    Find terminals whose purpose contains this exact word (case insensitive).
    
    Args:
        word: The word to match (e.g., "Coding")
        terminals: List of terminal info dicts with 'name' and 'purpose' fields
        
    Returns:
        List of terminal names that match, or empty list if none
        
    Example:
        >>> terminals = [
        ...     {"name": "Amy", "purpose": "Coding, Research"},
        ...     {"name": "Bob", "purpose": "Testing"}
        ... ]
        >>> match_purpose("coding", terminals)
        ['Amy']
        >>> match_purpose("research", terminals)
        ['Amy']
        >>> match_purpose("cod", terminals)
        []
    """
    if not word or not terminals:
        return []
    
    matches = []
    word_lower = word.lower().strip()
    
    for terminal in terminals:
        terminal_name = terminal.get("name", "")
        purpose = terminal.get("purpose", "")
        
        if not terminal_name or not purpose:
            continue
            
        # Split purpose by comma and strip whitespace
        purpose_words = [p.strip().lower() for p in purpose.split(",")]
        
        # Check for exact word match
        if word_lower in purpose_words:
            matches.append(terminal_name)
            logger.debug(f"Terminal '{terminal_name}' matches purpose '{word}'")
    
    if not matches:
        logger.debug(f"No terminals found with purpose matching '{word}'")
    
    return matches


def parse_purpose_list(purpose_string: str) -> List[str]:
    """
    Parse a comma-separated purpose string into individual words.
    
    Args:
        purpose_string: CSV string like "Coding, Research, Testing"
        
    Returns:
        List of individual purpose words
    """
    if not purpose_string:
        return []
    
    # Split by comma and clean up each word
    words = [word.strip() for word in purpose_string.split(",")]
    
    # Filter out empty strings
    return [word for word in words if word]