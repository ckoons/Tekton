"""
Resource Models

This module defines the domain models for resources in the Prometheus/Epimethius Planning System.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import uuid


class Resource:
    """Resource model representing a resource that can be assigned to tasks."""

    def __init__(
        self,
        resource_id: str,
        name: str,
        resource_type: str,  # "human", "equipment", "service", etc.
        capacity: float,  # e.g., hours per day or units available
        skills: List[str] = None,
        availability: Dict[str, Any] = None,  # e.g., {"weekdays": [1, 2, 3, 4, 5], "hours": [9, 17]}
        cost_rate: Optional[float] = None,  # Cost per unit (e.g., hourly rate)
        metadata: Dict[str, Any] = None
    ):
        self.resource_id = resource_id
        self.name = name
        self.resource_type = resource_type
        self.capacity = capacity
        self.skills = skills or []
        self.availability = availability or {}
        self.cost_rate = cost_rate
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the resource to a dictionary."""
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "resource_type": self.resource_type,
            "capacity": self.capacity,
            "skills": self.skills,
            "availability": self.availability,
            "cost_rate": self.cost_rate,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resource':
        """Create a resource from a dictionary."""
        resource = cls(
            resource_id=data["resource_id"],
            name=data["name"],
            resource_type=data["resource_type"],
            capacity=data["capacity"],
            skills=data.get("skills", []),
            availability=data.get("availability", {}),
            cost_rate=data.get("cost_rate"),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            resource.created_at = data["created_at"]
        if "updated_at" in data:
            resource.updated_at = data["updated_at"]
            
        return resource

    def add_skill(self, skill: str):
        """Add a skill to the resource."""
        if skill not in self.skills:
            self.skills.append(skill)
            self.updated_at = datetime.now().timestamp()

    def remove_skill(self, skill: str) -> bool:
        """Remove a skill from the resource."""
        if skill in self.skills:
            self.skills.remove(skill)
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    def update_capacity(self, capacity: float):
        """Update the resource capacity."""
        self.capacity = capacity
        self.updated_at = datetime.now().timestamp()

    def update_availability(self, availability: Dict[str, Any]):
        """Update the resource availability."""
        self.availability = availability
        self.updated_at = datetime.now().timestamp()

    def update_cost_rate(self, cost_rate: float):
        """Update the resource cost rate."""
        self.cost_rate = cost_rate
        self.updated_at = datetime.now().timestamp()

    def has_skill(self, skill: str) -> bool:
        """Check if the resource has a skill."""
        return skill in self.skills

    def calculate_cost(self, hours: float) -> float:
        """
        Calculate the cost for a given number of hours.
        
        Args:
            hours: Number of hours to calculate cost for
            
        Returns:
            Cost for the given hours
        """
        if self.cost_rate is None:
            return 0.0
        return hours * self.cost_rate

    @staticmethod
    def create_new(
        name: str,
        resource_type: str,
        capacity: float,
        skills: List[str] = None,
        availability: Dict[str, Any] = None,
        cost_rate: Optional[float] = None,
        metadata: Dict[str, Any] = None
    ) -> 'Resource':
        """
        Create a new resource with a generated ID.
        
        Args:
            name: Name of the resource
            resource_type: Type of resource
            capacity: Capacity of the resource
            skills: Optional list of skills
            availability: Optional availability dictionary
            cost_rate: Optional cost rate
            metadata: Optional metadata
            
        Returns:
            A new Resource instance
        """
        resource_id = f"resource-{uuid.uuid4()}"
        return Resource(
            resource_id=resource_id,
            name=name,
            resource_type=resource_type,
            capacity=capacity,
            skills=skills,
            availability=availability,
            cost_rate=cost_rate,
            metadata=metadata
        )


class ResourceAllocation:
    """Resource allocation model representing the assignment of a resource to a task."""

    def __init__(
        self,
        allocation_id: str,
        resource_id: str,
        task_id: str,
        start_date: datetime,
        end_date: datetime,
        allocated_hours: float,
        allocation_type: str = "full",  # "full", "partial", "overtime"
        status: str = "planned",  # "planned", "active", "completed", "cancelled"
        metadata: Dict[str, Any] = None
    ):
        self.allocation_id = allocation_id
        self.resource_id = resource_id
        self.task_id = task_id
        self.start_date = start_date
        self.end_date = end_date
        self.allocated_hours = allocated_hours
        self.allocation_type = allocation_type
        self.status = status
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the allocation to a dictionary."""
        return {
            "allocation_id": self.allocation_id,
            "resource_id": self.resource_id,
            "task_id": self.task_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "allocated_hours": self.allocated_hours,
            "allocation_type": self.allocation_type,
            "status": self.status,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceAllocation':
        """Create an allocation from a dictionary."""
        # Convert date strings to datetime objects
        start_date = datetime.fromisoformat(data["start_date"]) if data.get("start_date") else None
        end_date = datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None
        
        allocation = cls(
            allocation_id=data["allocation_id"],
            resource_id=data["resource_id"],
            task_id=data["task_id"],
            start_date=start_date,
            end_date=end_date,
            allocated_hours=data["allocated_hours"],
            allocation_type=data.get("allocation_type", "full"),
            status=data.get("status", "planned"),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            allocation.created_at = data["created_at"]
        if "updated_at" in data:
            allocation.updated_at = data["updated_at"]
            
        return allocation

    def update_status(self, status: str):
        """Update the allocation status."""
        self.status = status
        self.updated_at = datetime.now().timestamp()

    def update_hours(self, allocated_hours: float):
        """Update the allocated hours."""
        self.allocated_hours = allocated_hours
        self.updated_at = datetime.now().timestamp()

    def calculate_utilization(self, available_hours: float) -> float:
        """
        Calculate resource utilization percentage.
        
        Args:
            available_hours: Total available hours for the resource
            
        Returns:
            Utilization percentage (0.0 to 1.0+)
        """
        if available_hours <= 0:
            return 0.0
        return self.allocated_hours / available_hours

    @staticmethod
    def create_new(
        resource_id: str,
        task_id: str,
        start_date: datetime,
        end_date: datetime,
        allocated_hours: float,
        allocation_type: str = "full",
        status: str = "planned",
        metadata: Dict[str, Any] = None
    ) -> 'ResourceAllocation':
        """
        Create a new resource allocation with a generated ID.
        
        Args:
            resource_id: ID of the resource
            task_id: ID of the task
            start_date: Start date of allocation
            end_date: End date of allocation
            allocated_hours: Number of hours allocated
            allocation_type: Type of allocation
            status: Status of allocation
            metadata: Optional metadata
            
        Returns:
            A new ResourceAllocation instance
        """
        allocation_id = f"allocation-{uuid.uuid4()}"
        return ResourceAllocation(
            allocation_id=allocation_id,
            resource_id=resource_id,
            task_id=task_id,
            start_date=start_date,
            end_date=end_date,
            allocated_hours=allocated_hours,
            allocation_type=allocation_type,
            status=status,
            metadata=metadata
        )