#!/usr/bin/env python3
"""
Structured Memory Constants

Defines constants, default values, and configurations for the structured memory system.
"""

from typing import Dict, Any

# Default directory structure for memory categories
DEFAULT_MEMORY_CATEGORIES = [
    "personal",
    "projects",
    "facts",
    "preferences",
    "session",
    "private",
]

# Default importance levels and their descriptions
IMPORTANCE_LEVELS = {
    1: "Low importance, general context",
    2: "Somewhat important, specific details",
    3: "Moderately important, useful context",
    4: "Very important, should remember",
    5: "Critical information, must remember"
}

# Default category importance settings
DEFAULT_CATEGORY_IMPORTANCE = {
    "personal": {
        "default_importance": 5,
        "description": "Personal information about the user"
    },
    "projects": {
        "default_importance": 4,
        "description": "Project-specific information and context"
    },
    "facts": {
        "default_importance": 3,
        "description": "General factual information"
    },
    "preferences": {
        "default_importance": 4,
        "description": "User preferences and settings"
    },
    "session": {
        "default_importance": 3,
        "description": "Session-specific context and information"
    },
    "private": {
        "default_importance": 5,
        "description": "Private thoughts and reflections"
    }
}

# Namespace to category mapping for migration
NAMESPACE_TO_CATEGORY_MAP = {
    "conversations": "personal",
    "thinking": "private",
    "longterm": "personal",
    "projects": "projects",
    "compartments": "projects",
    "session": "session"
}

# Default importance mapping for migration
NAMESPACE_IMPORTANCE_MAP = {
    "longterm": 5,
    "thinking": 4,
    "compartment": 4,
    "conversations": 3,
    "projects": 4,
    "session": 3
}