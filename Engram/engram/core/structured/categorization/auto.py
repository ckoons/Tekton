#!/usr/bin/env python3
"""
Automatic Memory Categorization

Provides functions for automatically categorizing memory content.
"""

import logging
import re
from typing import Tuple, List, Optional

logger = logging.getLogger("engram.structured.categorization.auto")

async def auto_categorize_memory(content: str) -> Tuple[str, int, List[str]]:
    """
    Automatically categorize memory content based on patterns and keywords.
    
    Args:
        content: The memory content to categorize
        
    Returns:
        Tuple of (category, importance, tags)
    """
    # Default values
    category = "session"
    importance = 3
    tags = []
    
    try:
        # Convert to lowercase for easier matching
        content_lower = content.lower()
        
        # Check for personal memories
        if (
            re.search(r"\b(i feel|i think|i believe|my opinion|personally)\b", content_lower) or
            re.search(r"\b(my experience|in my view|i remember|i recall)\b", content_lower)
        ):
            category = "personal"
            tags.append("personal")
            tags.append("reflection")
            
            # Check for emotional content - higher importance
            if re.search(r"\b(love|hate|excited|sad|angry|happy|worried|anxious)\b", content_lower):
                importance = 4
                tags.append("emotional")
        
        # Check for project related content
        elif (
            re.search(r"\b(project|feature|implementation|code|develop|program)\b", content_lower) or
            re.search(r"\b(design|architecture|refactor|test|debug|fix|issue)\b", content_lower) or
            re.search(r"\b(api|database|server|client|interface|module|class|function)\b", content_lower)
        ):
            category = "projects"
            tags.append("project")
            
            # Identify programming languages
            for lang in ["python", "javascript", "typescript", "rust", "java", "c++", "go"]:
                if re.search(f"\b{lang}\b", content_lower):
                    tags.append(lang)
            
            # Check if it's a critical feature or issue
            if re.search(r"\b(critical|urgent|important|blocking|priority)\b", content_lower):
                importance = 5
                tags.append("critical")
            elif re.search(r"\b(milestone|release|deadline|launch)\b", content_lower):
                importance = 4
                tags.append("milestone")
        
        # Check for factual information
        elif (
            re.search(r"\b(fact|definition|concept|principle|theory|equation)\b", content_lower) or
            re.search(r"\b(algorithm|formula|theorem|law|rule|guideline)\b", content_lower) or
            re.search(r"\b(according to|research shows|studies indicate)\b", content_lower)
        ):
            category = "facts"
            tags.append("fact")
            
            # More important facts get higher importance
            if re.search(r"\b(fundamental|essential|critical|important|key)\b", content_lower):
                importance = 4
                tags.append("fundamental")
            
            # Check for specific domains
            domains = {
                "math": r"\b(math|mathematics|calculus|algebra|geometry|equation)\b",
                "science": r"\b(science|physics|chemistry|biology|astronomy)\b",
                "cs": r"\b(computer science|algorithm|data structure|complexity)\b",
                "history": r"\b(history|historical|century|era|period|ancient|modern)\b"
            }
            
            for domain, pattern in domains.items():
                if re.search(pattern, content_lower):
                    tags.append(domain)
        
        # Check if it's a resource or reference
        elif (
            re.search(r"\b(link|url|website|resource|reference|documentation)\b", content_lower) or
            re.search(r"\b(book|article|paper|publication|tutorial|guide)\b", content_lower) or
            re.search(r"https?://", content_lower)
        ):
            category = "resources"
            tags.append("resource")
            
            # Check resource types
            if "http" in content_lower or "www." in content_lower:
                tags.append("website")
            if re.search(r"\b(book|isbn)\b", content_lower):
                tags.append("book")
            if re.search(r"\b(paper|journal|conference|publication)\b", content_lower):
                tags.append("paper")
            if re.search(r"\b(video|youtube|watch)\b", content_lower):
                tags.append("video")
                
            # Important reference gets higher importance
            if re.search(r"\b(important|valuable|useful|essential|recommended)\b", content_lower):
                importance = 4
                
        # Check for private or sensitive information
        elif (
            re.search(r"\b(password|secret|sensitive|private|confidential)\b", content_lower) or
            re.search(r"\b(api key|token|credential|personal info)\b", content_lower) or
            re.search(r"\b(ssh|aws|login|encrypt)\b", content_lower)
        ):
            category = "private"
            importance = 5  # Security-related content is automatically high importance
            tags.append("sensitive")
            tags.append("security")
            
        # Look for specific importance indicators regardless of category
        if re.search(r"\b(critical|crucial|vital|essential)\b", content_lower):
            importance = max(importance, 5)
        elif re.search(r"\b(important|significant|major|key)\b", content_lower):
            importance = max(importance, 4)
        elif re.search(r"\b(useful|helpful|good to know)\b", content_lower):
            importance = max(importance, 3)
        elif re.search(r"\b(minor|trivial|not important)\b", content_lower):
            importance = min(importance, 2)
            
        # Add general tags based on content
        if re.search(r"\b(todo|task|action item|reminder)\b", content_lower):
            tags.append("todo")
        if re.search(r"\b(idea|concept|suggestion|proposal)\b", content_lower):
            tags.append("idea")
        if re.search(r"\b(question|query|ask|wondering)\b", content_lower):
            tags.append("question")
        if re.search(r"\b(decision|choice|select|choose)\b", content_lower):
            tags.append("decision")
            
        # Ensure we have at least one tag
        if not tags:
            tags.append(category)  # Use category as default tag
            
        logger.info(f"Auto-categorized memory as '{category}' with importance {importance} and tags {tags}")
        return category, importance, tags
    except Exception as e:
        logger.error(f"Error auto-categorizing memory: {e}")
        return "session", 3, ["auto-categorization-failed"]  # Safe defaults