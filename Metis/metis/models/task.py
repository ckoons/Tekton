"""
Task model for Metis

This module defines the core Task model for the Metis system.
"""

from datetime import datetime
from pydantic import Field, field_validator
from uuid import uuid4
from typing import Optional, List, Dict, Any, Set
from tekton.models.base import TektonBaseModel

from metis.models.enums import TaskStatus, Priority
from metis.models.complexity import ComplexityScore
from metis.models.subtask import Subtask
from metis.models.requirement import RequirementRef


class Task(TektonBaseModel):
    """
    Core Task model for Metis.
    
    Tasks are the primary unit of work in the Metis system, representing
    discrete pieces of work that need to be completed.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    status: str = TaskStatus.PENDING.value
    priority: str = Priority.MEDIUM.value
    details: Optional[str] = None  # Implementation details
    test_strategy: Optional[str] = None  # Testing approach
    dependencies: List[str] = []  # List of task IDs this task depends on
    complexity: Optional[ComplexityScore] = None
    subtasks: List[Subtask] = []
    tags: List[str] = []
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    requirement_refs: List[RequirementRef] = []
    
    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        """Validate that the status is a valid TaskStatus value."""
        if v not in [s.value for s in TaskStatus]:
            raise ValueError(f"Invalid task status: {v}")
        return v
    
    @field_validator("priority")
    @classmethod
    def priority_must_be_valid(cls, v):
        """Validate that the priority is a valid Priority value."""
        if v not in [p.value for p in Priority]:
            raise ValueError(f"Invalid task priority: {v}")
        return v
    
    def update_status(self, new_status: str) -> bool:
        """
        Update the task status with validation.
        
        Args:
            new_status: New status value
            
        Returns:
            bool: True if status was updated, False if transition was invalid
            
        Raises:
            ValueError: If the new status is not a valid TaskStatus value
        """
        # Validate status value
        if new_status not in [s.value for s in TaskStatus]:
            raise ValueError(f"Invalid task status: {new_status}")
        
        # Check if transition is valid
        if not TaskStatus.is_valid_transition(self.status, new_status):
            return False
        
        # Update status and timestamp
        self.status = new_status
        self.updated_at = datetime.utcnow()
        return True
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update task fields with validation.
        
        Args:
            updates: Dictionary of field updates
        """
        # Handle status updates with validation
        if "status" in updates and updates["status"] != self.status:
            if not self.update_status(updates["status"]):
                raise ValueError(
                    f"Invalid status transition from {self.status} to {updates['status']}"
                )
            # Remove status from updates dict since we've already handled it
            del updates["status"]
        
        # Handle priority updates with validation
        if "priority" in updates:
            if updates["priority"] not in [p.value for p in Priority]:
                raise ValueError(f"Invalid task priority: {updates['priority']}")
        
        # Update other fields
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Update timestamp
        self.updated_at = datetime.utcnow()
    
    def add_subtask(self, subtask: Subtask) -> None:
        """
        Add a subtask to the task.
        
        Args:
            subtask: Subtask to add
        """
        # Set order to end of list if not specified
        if subtask.order == 0 and self.subtasks:
            subtask.order = max(s.order for s in self.subtasks) + 1
        
        self.subtasks.append(subtask)
        self.updated_at = datetime.utcnow()
    
    def update_subtask(self, subtask_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a subtask by ID.
        
        Args:
            subtask_id: ID of the subtask to update
            updates: Dictionary of field updates
            
        Returns:
            bool: True if subtask was found and updated, False otherwise
        """
        for i, subtask in enumerate(self.subtasks):
            if subtask.id == subtask_id:
                subtask.update(updates)
                self.subtasks[i] = subtask
                self.updated_at = datetime.utcnow()
                return True
        
        return False
    
    def remove_subtask(self, subtask_id: str) -> bool:
        """
        Remove a subtask by ID.
        
        Args:
            subtask_id: ID of the subtask to remove
            
        Returns:
            bool: True if subtask was found and removed, False otherwise
        """
        for i, subtask in enumerate(self.subtasks):
            if subtask.id == subtask_id:
                self.subtasks.pop(i)
                self.updated_at = datetime.utcnow()
                return True
        
        return False
    
    def add_requirement_ref(self, req_ref: RequirementRef) -> None:
        """
        Add a requirement reference to the task.
        
        Args:
            req_ref: Requirement reference to add
        """
        self.requirement_refs.append(req_ref)
        self.updated_at = datetime.utcnow()
    
    def update_requirement_ref(self, ref_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a requirement reference by ID.
        
        Args:
            ref_id: ID of the requirement reference to update
            updates: Dictionary of field updates
            
        Returns:
            bool: True if reference was found and updated, False otherwise
        """
        for i, ref in enumerate(self.requirement_refs):
            if ref.id == ref_id:
                ref.update(updates)
                self.requirement_refs[i] = ref
                self.updated_at = datetime.utcnow()
                return True
        
        return False
    
    def remove_requirement_ref(self, ref_id: str) -> bool:
        """
        Remove a requirement reference by ID.
        
        Args:
            ref_id: ID of the requirement reference to remove
            
        Returns:
            bool: True if reference was found and removed, False otherwise
        """
        for i, ref in enumerate(self.requirement_refs):
            if ref.id == ref_id:
                self.requirement_refs.pop(i)
                self.updated_at = datetime.utcnow()
                return True
        
        return False
    
    def has_dependency(self, task_id: str) -> bool:
        """
        Check if task has a dependency on another task.
        
        Args:
            task_id: ID of the dependency task to check
            
        Returns:
            bool: True if task has this dependency, False otherwise
        """
        return task_id in self.dependencies
    
    def add_dependency(self, task_id: str) -> bool:
        """
        Add a dependency to the task.
        
        Args:
            task_id: ID of the task to depend on
            
        Returns:
            bool: True if dependency was added, False if it already existed
        """
        if task_id in self.dependencies:
            return False
        
        self.dependencies.append(task_id)
        self.updated_at = datetime.utcnow()
        return True
    
    def remove_dependency(self, task_id: str) -> bool:
        """
        Remove a dependency from the task.
        
        Args:
            task_id: ID of the dependency to remove
            
        Returns:
            bool: True if dependency was removed, False if it wasn't found
        """
        if task_id not in self.dependencies:
            return False
        
        self.dependencies.remove(task_id)
        self.updated_at = datetime.utcnow()
        return True
    
    def get_progress(self) -> float:
        """
        Calculate the progress of the task based on subtasks.
        
        Returns:
            float: Progress percentage (0-100)
        """
        if not self.subtasks:
            # If no subtasks, use status
            if self.status == TaskStatus.DONE.value:
                return 100.0
            elif self.status == TaskStatus.REVIEW.value:
                return 90.0
            elif self.status == TaskStatus.IN_PROGRESS.value:
                return 50.0
            else:
                return 0.0
        
        # With subtasks, calculate progress based on completed subtasks
        completed = sum(1 for s in self.subtasks if s.status == TaskStatus.DONE.value)
        return (completed / len(self.subtasks)) * 100.0