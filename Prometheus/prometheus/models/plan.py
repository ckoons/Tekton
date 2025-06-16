"""
Plan Models

This module defines the domain models for plans in the Prometheus/Epimethius Planning System.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import uuid


class ResourceRequirement:
    """Resource requirement model for planning system."""
    
    def __init__(
        self,
        requirement_id: str,
        name: str,
        description: str,
        resource_type: str,  # "human", "compute", "storage", etc.
        quantity: float,
        unit: str,  # "hours", "GB", "cores", etc.
        priority: str = "medium",  # "low", "medium", "high", "critical"
        metadata: Dict[str, Any] = None
    ):
        self.requirement_id = requirement_id
        self.name = name
        self.description = description
        self.resource_type = resource_type
        self.quantity = quantity
        self.unit = unit
        self.priority = priority
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the resource requirement to a dictionary."""
        return {
            "requirement_id": self.requirement_id,
            "name": self.name,
            "description": self.description,
            "resource_type": self.resource_type,
            "quantity": self.quantity,
            "unit": self.unit,
            "priority": self.priority,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceRequirement':
        """Create a resource requirement from a dictionary."""
        requirement = cls(
            requirement_id=data["requirement_id"],
            name=data["name"],
            description=data["description"],
            resource_type=data["resource_type"],
            quantity=data["quantity"],
            unit=data["unit"],
            priority=data.get("priority", "medium"),
            metadata=data.get("metadata", {})
        )
        
        if "created_at" in data:
            requirement.created_at = data["created_at"]
        if "updated_at" in data:
            requirement.updated_at = data["updated_at"]
            
        return requirement


class Milestone:
    """Milestone model representing a significant point in a plan."""

    def __init__(
        self,
        milestone_id: str,
        name: str,
        description: str,
        target_date: datetime,
        criteria: List[str] = None,
        status: str = "not_started",  # "not_started", "in_progress", "completed"
        actual_date: Optional[datetime] = None,
        metadata: Dict[str, Any] = None
    ):
        self.milestone_id = milestone_id
        self.name = name
        self.description = description
        self.target_date = target_date
        self.criteria = criteria or []
        self.status = status
        self.actual_date = actual_date
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the milestone to a dictionary."""
        return {
            "milestone_id": self.milestone_id,
            "name": self.name,
            "description": self.description,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "criteria": self.criteria,
            "status": self.status,
            "actual_date": self.actual_date.isoformat() if self.actual_date else None,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Milestone':
        """Create a milestone from a dictionary."""
        target_date = datetime.fromisoformat(data["target_date"]) if data.get("target_date") else None
        actual_date = datetime.fromisoformat(data["actual_date"]) if data.get("actual_date") else None
        
        milestone = cls(
            milestone_id=data["milestone_id"],
            name=data["name"],
            description=data["description"],
            target_date=target_date,
            criteria=data.get("criteria", []),
            status=data.get("status", "not_started"),
            actual_date=actual_date,
            metadata=data.get("metadata", {})
        )
        
        if "created_at" in data:
            milestone.created_at = data["created_at"]
        if "updated_at" in data:
            milestone.updated_at = data["updated_at"]
            
        return milestone


class Plan:
    """Plan model representing a project plan."""

    def __init__(
        self,
        plan_id: str,
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        methodology: str,  # "agile", "waterfall", etc.
        tasks: Dict[str, Any] = None,  # Task objects will be imported separately
        milestones: List[Milestone] = None,
        requirements: List[str] = None,  # IDs of requirements from Telos
        metadata: Dict[str, Any] = None
    ):
        self.plan_id = plan_id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.methodology = methodology
        self.tasks = tasks or {}
        self.milestones = milestones or []
        self.requirements = requirements or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at
        self.version = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert the plan to a dictionary."""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "methodology": self.methodology,
            "tasks": {task_id: task.to_dict() if hasattr(task, 'to_dict') else task 
                      for task_id, task in self.tasks.items()},
            "milestones": [milestone.to_dict() if hasattr(milestone, 'to_dict') else milestone 
                           for milestone in self.milestones],
            "requirements": self.requirements,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Plan':
        """Create a plan from a dictionary."""
        # Convert date strings to datetime objects
        start_date = datetime.fromisoformat(data["start_date"]) if data.get("start_date") else None
        end_date = datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None
        
        # Create milestones from dictionary data if needed
        milestones = []
        for milestone_data in data.get("milestones", []):
            if isinstance(milestone_data, dict):
                milestones.append(Milestone.from_dict(milestone_data))
            else:
                milestones.append(milestone_data)
        
        # Create the plan
        plan = cls(
            plan_id=data["plan_id"],
            name=data["name"],
            description=data["description"],
            start_date=start_date,
            end_date=end_date,
            methodology=data["methodology"],
            tasks=data.get("tasks", {}),  # Task objects will be imported separately
            milestones=milestones,
            requirements=data.get("requirements", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps and version if provided
        if "created_at" in data:
            plan.created_at = data["created_at"]
        if "updated_at" in data:
            plan.updated_at = data["updated_at"]
        if "version" in data:
            plan.version = data["version"]
            
        return plan

    def update_version(self):
        """Update the plan version and updated_at timestamp."""
        self.version += 1
        self.updated_at = datetime.now().timestamp()

    def add_task(self, task):
        """Add a task to the plan."""
        self.tasks[task.task_id] = task
        self.update_version()

    def add_milestone(self, milestone: Milestone):
        """Add a milestone to the plan."""
        self.milestones.append(milestone)
        self.update_version()

    def add_requirement(self, requirement_id: str):
        """Add a requirement to the plan."""
        if requirement_id not in self.requirements:
            self.requirements.append(requirement_id)
            self.update_version()

    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the plan."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.update_version()
            return True
        return False

    def get_task(self, task_id: str) -> Any:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def get_milestone(self, milestone_id: str) -> Optional[Milestone]:
        """Get a milestone by ID."""
        for milestone in self.milestones:
            if milestone.milestone_id == milestone_id:
                return milestone
        return None

    def update_task(self, task):
        """Update a task in the plan."""
        if task.task_id in self.tasks:
            self.tasks[task.task_id] = task
            self.update_version()
            return True
        return False

    def update_milestone(self, milestone: Milestone) -> bool:
        """Update a milestone in the plan."""
        for i, m in enumerate(self.milestones):
            if m.milestone_id == milestone.milestone_id:
                self.milestones[i] = milestone
                self.update_version()
                return True
        return False

    def get_critical_path(self) -> List[str]:
        """
        Calculate the critical path of the plan.
        
        Returns:
            List of task IDs in the critical path.
        """
        # This is a placeholder for the critical path calculation
        # In a real implementation, this would use a graph algorithm
        # to find the longest path from start to end
        return []

    def calculate_completion_percentage(self) -> float:
        """
        Calculate the completion percentage of the plan.
        
        Returns:
            Completion percentage between 0 and 1.
        """
        if not self.tasks:
            return 0.0
            
        completed_tasks = sum(1 for task in self.tasks.values() 
                              if getattr(task, "status", "") == "completed")
        return completed_tasks / len(self.tasks)

    @staticmethod
    def create_new(
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        methodology: str,
        requirements: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'Plan':
        """
        Create a new plan with a generated ID.
        
        Args:
            name: Name of the plan
            description: Description of the plan
            start_date: Start date of the plan
            end_date: End date of the plan
            methodology: Methodology to use (e.g., "agile", "waterfall")
            requirements: Optional list of requirement IDs
            metadata: Optional metadata
            
        Returns:
            A new Plan instance
        """
        plan_id = f"plan-{uuid.uuid4()}"
        return Plan(
            plan_id=plan_id,
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            methodology=methodology,
            requirements=requirements,
            metadata=metadata
        )