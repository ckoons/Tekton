"""
Enum definitions for Metis models

This module defines the various enum types used throughout the Metis system,
providing standardized values for status, priority, and complexity.
"""

from enum import Enum, auto
from typing import Dict, Any, List


class TaskStatus(str, Enum):
    """
    Task status enum representing the current state of a task.
    
    Using string values for serialization compatibility.
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    
    @classmethod
    def allowed_transitions(cls) -> Dict[str, List[str]]:
        """
        Get allowed status transitions.
        
        Returns:
            Dict[str, List[str]]: Dictionary of current status to allowed next statuses
        """
        return {
            cls.PENDING.value: [cls.IN_PROGRESS.value, cls.CANCELLED.value],
            cls.IN_PROGRESS.value: [cls.REVIEW.value, cls.BLOCKED.value, cls.CANCELLED.value],
            cls.REVIEW.value: [cls.DONE.value, cls.IN_PROGRESS.value, cls.CANCELLED.value],
            cls.DONE.value: [cls.IN_PROGRESS.value],  # Reopen if needed
            cls.BLOCKED.value: [cls.IN_PROGRESS.value, cls.CANCELLED.value],
            cls.CANCELLED.value: [cls.PENDING.value]  # Reactivate if needed
        }
    
    @classmethod
    def is_valid_transition(cls, current: str, next_status: str) -> bool:
        """
        Check if a status transition is valid.
        
        Args:
            current: Current task status
            next_status: Proposed next status
            
        Returns:
            bool: True if transition is valid, False otherwise
        """
        if current == next_status:
            return True  # No change is always valid
            
        transitions = cls.allowed_transitions()
        return next_status in transitions.get(current, [])


class Priority(str, Enum):
    """
    Task priority enum representing the importance of a task.
    
    Using string values for serialization compatibility.
    """
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ComplexityLevel(str, Enum):
    """
    Complexity level enum representing the difficulty of a task.
    
    Using string values for serialization compatibility.
    """
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"
    
    @classmethod
    def to_score(cls, level: str) -> int:
        """
        Convert complexity level to numeric score for calculations.
        
        Args:
            level: Complexity level string
            
        Returns:
            int: Numeric score representing complexity (1-5)
        """
        scores = {
            cls.TRIVIAL.value: 1,
            cls.SIMPLE.value: 2,
            cls.MODERATE.value: 3,
            cls.COMPLEX.value: 4,
            cls.VERY_COMPLEX.value: 5
        }
        return scores.get(level, 3)  # Default to moderate if unknown
    
    @classmethod
    def from_score(cls, score: int) -> str:
        """
        Convert numeric score to complexity level.
        
        Args:
            score: Numeric score (1-5)
            
        Returns:
            str: Complexity level string
        """
        levels = {
            1: cls.TRIVIAL.value,
            2: cls.SIMPLE.value,
            3: cls.MODERATE.value,
            4: cls.COMPLEX.value,
            5: cls.VERY_COMPLEX.value
        }
        # Clamp to valid range
        clamped_score = max(1, min(5, score))
        return levels[clamped_score]