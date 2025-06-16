"""
Task Models

This module defines the domain models for tasks in the Prometheus/Epimethius Planning System.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import uuid


class Task:
    """Task model representing a work item in a plan."""

    def __init__(
        self,
        task_id: str,
        name: str,
        description: str,
        status: str,  # "not_started", "in_progress", "completed", etc.
        priority: str,  # "low", "medium", "high", "critical"
        estimated_effort: float,
        actual_effort: float = 0.0,
        assigned_resources: List[str] = None,
        dependencies: List[str] = None,
        requirements: List[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metadata: Dict[str, Any] = None
    ):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.status = status
        self.priority = priority
        self.estimated_effort = estimated_effort
        self.actual_effort = actual_effort
        self.assigned_resources = assigned_resources or []
        self.dependencies = dependencies or []
        self.requirements = requirements or []
        self.start_date = start_date
        self.end_date = end_date
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at
        self.progress = 0.0  # 0.0 to 1.0 representing completion percentage

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "estimated_effort": self.estimated_effort,
            "actual_effort": self.actual_effort,
            "assigned_resources": self.assigned_resources,
            "dependencies": self.dependencies,
            "requirements": self.requirements,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "progress": self.progress
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create a task from a dictionary."""
        # Convert date strings to datetime objects
        start_date = datetime.fromisoformat(data["start_date"]) if data.get("start_date") else None
        end_date = datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None
        
        # Create the task
        task = cls(
            task_id=data["task_id"],
            name=data["name"],
            description=data["description"],
            status=data["status"],
            priority=data["priority"],
            estimated_effort=data["estimated_effort"],
            actual_effort=data.get("actual_effort", 0.0),
            assigned_resources=data.get("assigned_resources", []),
            dependencies=data.get("dependencies", []),
            requirements=data.get("requirements", []),
            start_date=start_date,
            end_date=end_date,
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps and progress if provided
        if "created_at" in data:
            task.created_at = data["created_at"]
        if "updated_at" in data:
            task.updated_at = data["updated_at"]
        if "progress" in data:
            task.progress = data["progress"]
            
        return task

    def update_status(self, status: str):
        """Update the task status."""
        self.status = status
        self.updated_at = datetime.now().timestamp()
        
        # Update progress based on status
        if status == "not_started":
            self.progress = 0.0
        elif status == "completed":
            self.progress = 1.0
            self.actual_effort = self.actual_effort or self.estimated_effort  # Set actual effort if not set

    def update_progress(self, progress: float):
        """Update the task progress."""
        self.progress = max(0.0, min(1.0, progress))  # Ensure progress is between 0 and 1
        self.updated_at = datetime.now().timestamp()
        
        # Update status based on progress
        if self.progress == 0.0:
            self.status = "not_started"
        elif self.progress == 1.0:
            self.status = "completed"
        else:
            self.status = "in_progress"

    def add_dependency(self, task_id: str):
        """Add a dependency to the task."""
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)
            self.updated_at = datetime.now().timestamp()

    def remove_dependency(self, task_id: str) -> bool:
        """Remove a dependency from the task."""
        if task_id in self.dependencies:
            self.dependencies.remove(task_id)
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    def assign_resource(self, resource_id: str):
        """Assign a resource to the task."""
        if resource_id not in self.assigned_resources:
            self.assigned_resources.append(resource_id)
            self.updated_at = datetime.now().timestamp()

    def unassign_resource(self, resource_id: str) -> bool:
        """Unassign a resource from the task."""
        if resource_id in self.assigned_resources:
            self.assigned_resources.remove(resource_id)
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    def is_blocked(self, completed_tasks: Set[str]) -> bool:
        """
        Check if the task is blocked by dependencies.
        
        Args:
            completed_tasks: Set of completed task IDs
            
        Returns:
            True if the task is blocked, False otherwise
        """
        for dependency in self.dependencies:
            if dependency not in completed_tasks:
                return True
        return False

    def calculate_earliest_start(self, task_end_dates: Dict[str, datetime]) -> Optional[datetime]:
        """
        Calculate the earliest start date based on dependencies.
        
        Args:
            task_end_dates: Dictionary mapping task IDs to end dates
            
        Returns:
            Earliest possible start date
        """
        if not self.dependencies:
            return self.start_date
            
        latest_end = None
        for dependency in self.dependencies:
            if dependency in task_end_dates:
                end_date = task_end_dates[dependency]
                if latest_end is None or end_date > latest_end:
                    latest_end = end_date
        
        return latest_end

    @staticmethod
    def create_new(
        name: str,
        description: str,
        priority: str,
        estimated_effort: float,
        assigned_resources: List[str] = None,
        dependencies: List[str] = None,
        requirements: List[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metadata: Dict[str, Any] = None
    ) -> 'Task':
        """
        Create a new task with a generated ID.
        
        Args:
            name: Name of the task
            description: Description of the task
            priority: Priority of the task
            estimated_effort: Estimated effort for the task
            assigned_resources: Optional list of assigned resource IDs
            dependencies: Optional list of dependency task IDs
            requirements: Optional list of requirement IDs
            start_date: Optional start date
            end_date: Optional end date
            metadata: Optional metadata
            
        Returns:
            A new Task instance
        """
        task_id = f"task-{uuid.uuid4()}"
        return Task(
            task_id=task_id,
            name=name,
            description=description,
            status="not_started",
            priority=priority,
            estimated_effort=estimated_effort,
            assigned_resources=assigned_resources,
            dependencies=dependencies,
            requirements=requirements,
            start_date=start_date,
            end_date=end_date,
            metadata=metadata
        )