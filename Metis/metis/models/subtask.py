"""
Subtask models for Metis

This module defines the subtask data models for the Metis system.
Subtasks are smaller units of work within a parent task.
"""

from datetime import datetime
from pydantic import Field
from uuid import uuid4
from typing import Optional, List, Dict, Any
from tekton.models.base import TektonBaseModel

from metis.models.enums import TaskStatus
from metis.models.complexity import ComplexityScore


class Subtask(TektonBaseModel):
    """
    Subtask model representing a smaller unit of work within a parent task.
    
    Subtasks have simplified attributes compared to full tasks and are
    always associated with a parent task.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    parent_task_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str = TaskStatus.PENDING.value
    order: int = 0  # Position within list of subtasks
    estimated_hours: float = 1.0  # Estimated time to complete
    complexity: Optional[ComplexityScore] = None  # Complexity analysis
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update subtask fields.
        
        Args:
            updates: Dictionary of field updates
        """
        # Check if status is being updated and validate the transition
        if "status" in updates and updates["status"] != self.status:
            if not TaskStatus.is_valid_transition(self.status, updates["status"]):
                raise ValueError(
                    f"Invalid status transition from {self.status} to {updates['status']}"
                )
        
        # Update fields
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Update timestamp
        self.updated_at = datetime.utcnow()


class SubtaskTemplate(TektonBaseModel):
    """
    Template for creating a set of related subtasks.
    
    Used to create consistent subtask structures for similar tasks.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    subtasks: List[Dict[str, Any]] = []  # Subtask definitions (title, description, etc.)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def create_subtasks(self) -> List[Subtask]:
        """
        Create subtask instances from this template.
        
        Returns:
            List[Subtask]: List of subtasks created from the template
        """
        result = []
        
        for i, subtask_def in enumerate(self.subtasks):
            # Create subtask with order based on position in list
            subtask = Subtask(
                title=subtask_def.get("title", "Untitled Subtask"),
                description=subtask_def.get("description"),
                order=i
            )
            result.append(subtask)
            
        return result