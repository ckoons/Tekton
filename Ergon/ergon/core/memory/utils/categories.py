"""
Memory categories for Ergon's memory system.

This module defines the different categories of memories and provides
utilities for categorizing content.
"""

from typing import Dict, Tuple, List, Set
import re
import logging

logger = logging.getLogger(__name__)

class MemoryCategory:
    """Define memory categories with default importance levels."""
    
    # Core categories
    PERSONAL = "personal"    # Personal details about the user
    FACTUAL = "factual"      # Factual information learned
    SESSION = "session"      # Current session details
    PROJECT = "project"      # Project-specific information
    PREFERENCE = "preference"  # User preferences
    SYSTEM = "system"        # System-related memories
    
    # All categories as a set
    ALL_CATEGORIES = {PERSONAL, FACTUAL, SESSION, PROJECT, PREFERENCE, SYSTEM}
    
    # Default importance by category (1-5 scale)
    DEFAULT_IMPORTANCE: Dict[str, int] = {
        PERSONAL: 4,
        FACTUAL: 3,
        SESSION: 2,
        PROJECT: 3,
        PREFERENCE: 4,
        SYSTEM: 3
    }
    
    # Categorization patterns
    PATTERNS: Dict[str, List[str]] = {
        PERSONAL: [
            r"my name is", r"i am", r"i'm", r"my (family|spouse|partner|child|children)", 
            r"i was born", r"i live in", r"my birthday", r"my hobby", r"my job"
        ],
        PREFERENCE: [
            r"i (like|love|prefer|hate|dislike)", r"my favorite", r"i('m| am) interested in",
            r"i('d| would) prefer", r"i('d| would) rather", r"i don't want"
        ],
        PROJECT: [
            r"project", r"task", r"work(ing)? on", r"develop(ing|ment)?", r"implement(ing|ation)?",
            r"build(ing)?", r"creat(e|ing)", r"design(ing)?"
        ],
        FACTUAL: [
            r"fact", r"information", r"data", r"statistic", r"study", r"research", 
            r"published", r"according to", r"established", r"known"
        ]
    }
    
    @classmethod
    def get_default_importance(cls, category: str) -> int:
        """Get the default importance for a category."""
        return cls.DEFAULT_IMPORTANCE.get(category, 2)
    
    @classmethod
    def is_valid_category(cls, category: str) -> bool:
        """Check if a category is valid."""
        return category in cls.ALL_CATEGORIES
    
    @classmethod
    def categorize(cls, content: str) -> Tuple[str, int]:
        """Auto-categorize content and assign default importance."""
        # Simple rules-based categorization
        content_lower = content.lower()
        
        # Check each category's patterns
        for category, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    return category, cls.DEFAULT_IMPORTANCE[category]
        
        # Default to session with medium importance
        return cls.SESSION, cls.DEFAULT_IMPORTANCE[cls.SESSION]