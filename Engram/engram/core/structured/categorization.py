#!/usr/bin/env python3
"""
Structured Memory Categorization

Provides automatic categorization and tagging of memory content.
"""

import logging
from typing import List, Tuple

logger = logging.getLogger("engram.structured.categorization")

async def auto_categorize_memory(content: str) -> Tuple[str, int, List[str]]:
    """
    Automatically categorize memory based on content analysis.
    
    Args:
        content: The memory content to analyze
        
    Returns:
        Tuple of (category, importance, tags)
    """
    # Initialize with defaults
    category = "session"
    importance = 3
    tags = []
    
    try:
        # Basic keyword matching for demonstration
        # These rules would be enhanced with more sophisticated NLP in production
        content_lower = content.lower()
        
        # Check for personal information patterns - highest priority
        personal_patterns = ["name is", "my name", "i am", "i'm", "i live", "address", "phone", "email"]
        has_personal = any(term in content_lower for term in personal_patterns)
        
        # Check for preferences
        preference_patterns = ["prefer", "like", "dislike", "favorite", "rather", "instead"]
        has_preferences = any(term in content_lower for term in preference_patterns)
        
        # Check for project information
        project_patterns = ["project", "working on", "task", "implement", "design", "feature"]
        has_project = any(term in content_lower for term in project_patterns)
        
        # Check for factual information
        fact_patterns = ["fact", "actually", "remember that", "keep in mind"]
        has_facts = any(term in content_lower for term in fact_patterns)
        
        # Prioritize categories (personal > preferences > projects > facts > session)
        if has_personal:
            category = "personal"
            importance = 5
            tags.append("personal-info")
        elif has_preferences:
            category = "preferences"
            importance = 4
            tags.append("preference")
        elif has_project:
            category = "projects"
            importance = 4
            tags.append("project")
        elif has_facts:
            category = "facts"
            importance = 3
            tags.append("fact")
            
        # Add coding related tags
        if any(term in content_lower for term in ["code", "python", "javascript", "programming", "function", "class"]):
            tags.append("coding")
            
        # Add communication tags
        if any(term in content_lower for term in ["call", "meeting", "discuss", "talk", "conversation"]):
            tags.append("communication")
            
        # Adjust importance based on emphasis cues
        if any(term in content_lower for term in ["important", "critical", "essential", "remember", "don't forget", "key"]):
            importance = min(importance + 1, 5)
            
        if any(term in content_lower for term in ["very important", "most important", "crucial", "vital"]):
            importance = 5
            
        return category, importance, tags
    except Exception as e:
        logger.error(f"Error auto-categorizing memory: {e}")
        return "session", 3, []

def get_categorization_patterns() -> Dict[str, List[str]]:
    """
    Get pattern dictionaries for categorization.
    
    Returns:
        Dictionary of pattern lists by category
    """
    return {
        "personal": ["name is", "my name", "i am", "i'm", "i live", "address", "phone", "email"],
        "preferences": ["prefer", "like", "dislike", "favorite", "rather", "instead"],
        "projects": ["project", "working on", "task", "implement", "design", "feature"],
        "facts": ["fact", "actually", "remember that", "keep in mind"],
        "coding": ["code", "python", "javascript", "programming", "function", "class"],
        "communication": ["call", "meeting", "discuss", "talk", "conversation"],
        "importance_up": ["important", "critical", "essential", "remember", "don't forget", "key"],
        "importance_max": ["very important", "most important", "crucial", "vital"]
    }