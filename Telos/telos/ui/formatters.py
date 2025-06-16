"""
Formatting utilities for requirement display and feedback.

This module provides functions for formatting requirement data and analysis
results for display to users.
"""

from typing import Dict, List, Any
from telos.core.requirement import Requirement


def format_detailed_feedback(
    requirement: Requirement, 
    metrics: Dict[str, Dict[str, Any]], 
    score: float, 
    suggestions: List[str]
) -> str:
    """
    Format detailed feedback for display.
    
    Args:
        requirement: The requirement being analyzed
        metrics: Quality metrics for different criteria
        score: Overall quality score
        suggestions: List of improvement suggestions
        
    Returns:
        Formatted feedback string
    """
    lines = [
        f"## Quality Analysis for '{requirement.title}'",
        "",
        f"Overall Quality Score: {score:.2f}/1.0",
        "",
        "### Criterion Scores:"
    ]
    
    for criterion, info in metrics.items():
        lines.append(f"- {criterion.capitalize()}: {info['score']:.2f}")
    
    lines.extend([
        "",
        "### Improvement Suggestions:"
    ])
    
    if suggestions:
        for suggestion in suggestions:
            lines.append(f"- {suggestion}")
    else:
        lines.append("- No specific suggestions - this requirement is well-formed!")
    
    return "\n".join(lines)


def display_requirement(requirement: Requirement) -> None:
    """
    Display requirement details in a formatted manner.
    
    Args:
        requirement: The requirement to display
    """
    print("\n=== Current Requirement ===")
    print(f"Title: {requirement.title}")
    print(f"Description: {requirement.description}")
    print(f"Type: {requirement.requirement_type}")
    print(f"Priority: {requirement.priority}")
    
    if requirement.tags:
        tags_str = ", ".join(requirement.tags)
        print(f"Tags: {tags_str}")
    else:
        print("Tags: None")
        
    if requirement.parent_id:
        print(f"Parent: {requirement.parent_id}")
        
    if requirement.dependencies:
        deps_str = ", ".join(requirement.dependencies)
        print(f"Dependencies: {deps_str}")
    
    print("========================")