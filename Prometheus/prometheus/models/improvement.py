"""
Improvement Models

This module defines the domain models for improvements in the Prometheus/Epimethius Planning System.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import uuid


class Improvement:
    """Model for an improvement item identified from retrospectives."""

    def __init__(
        self,
        improvement_id: str,
        title: str,
        description: str,
        source: str,  # "retrospective", "analysis", "manual", etc.
        source_id: Optional[str] = None,  # ID of source (e.g., retro_id)
        priority: str = "medium",  # "low", "medium", "high", "critical"
        status: str = "open",  # "open", "in_progress", "implemented", "verified"
        assignees: List[str] = None,
        due_date: Optional[datetime] = None,
        implementation_plan: Optional[str] = None,
        verification_criteria: Optional[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.improvement_id = improvement_id
        self.title = title
        self.description = description
        self.source = source
        self.source_id = source_id
        self.priority = priority
        self.status = status
        self.assignees = assignees or []
        self.due_date = due_date
        self.implementation_plan = implementation_plan
        self.verification_criteria = verification_criteria
        self.tags = tags or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at
        self.implemented_at = None
        self.verified_at = None
        self.status_history = [
            {
                "status": status,
                "timestamp": self.created_at,
                "comment": "Initial status"
            }
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the improvement to a dictionary."""
        return {
            "improvement_id": self.improvement_id,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "source_id": self.source_id,
            "priority": self.priority,
            "status": self.status,
            "assignees": self.assignees,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "implementation_plan": self.implementation_plan,
            "verification_criteria": self.verification_criteria,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "implemented_at": self.implemented_at,
            "verified_at": self.verified_at,
            "status_history": self.status_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Improvement':
        """Create an improvement from a dictionary."""
        # Convert date strings to datetime objects
        due_date = datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None
        
        # Create the improvement
        improvement = cls(
            improvement_id=data["improvement_id"],
            title=data["title"],
            description=data["description"],
            source=data["source"],
            source_id=data.get("source_id"),
            priority=data.get("priority", "medium"),
            status=data.get("status", "open"),
            assignees=data.get("assignees", []),
            due_date=due_date,
            implementation_plan=data.get("implementation_plan"),
            verification_criteria=data.get("verification_criteria"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps and history if provided
        if "created_at" in data:
            improvement.created_at = data["created_at"]
        if "updated_at" in data:
            improvement.updated_at = data["updated_at"]
        if "implemented_at" in data and data["implemented_at"]:
            improvement.implemented_at = data["implemented_at"]
        if "verified_at" in data and data["verified_at"]:
            improvement.verified_at = data["verified_at"]
        if "status_history" in data:
            improvement.status_history = data["status_history"]
            
        return improvement

    def update_status(self, new_status: str, comment: Optional[str] = None) -> None:
        """
        Update the improvement status with history tracking.
        
        Args:
            new_status: New status
            comment: Optional comment about the status change
        """
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now().timestamp()
        
        # Set implemented_at if status is "implemented" and wasn't before
        if new_status == "implemented" and old_status != "implemented":
            self.implemented_at = self.updated_at
        
        # Set verified_at if status is "verified" and wasn't before
        if new_status == "verified" and old_status != "verified":
            self.verified_at = self.updated_at
        
        # Add to status history
        self.status_history.append({
            "status": new_status,
            "timestamp": self.updated_at,
            "comment": comment or f"Status updated to {new_status}"
        })

    def assign_to(self, assignee: str):
        """Assign the improvement to a person."""
        if assignee not in self.assignees:
            self.assignees.append(assignee)
            self.updated_at = datetime.now().timestamp()

    def unassign_from(self, assignee: str) -> bool:
        """Unassign the improvement from a person."""
        if assignee in self.assignees:
            self.assignees.remove(assignee)
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    def update_priority(self, priority: str):
        """Update the priority of the improvement."""
        self.priority = priority
        self.updated_at = datetime.now().timestamp()

    def update_due_date(self, due_date: datetime):
        """Update the due date of the improvement."""
        self.due_date = due_date
        self.updated_at = datetime.now().timestamp()

    def add_tag(self, tag: str):
        """Add a tag to the improvement."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now().timestamp()

    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the improvement."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    def set_implementation_plan(self, plan: str):
        """Set the implementation plan for the improvement."""
        self.implementation_plan = plan
        self.updated_at = datetime.now().timestamp()

    def set_verification_criteria(self, criteria: str):
        """Set the verification criteria for the improvement."""
        self.verification_criteria = criteria
        self.updated_at = datetime.now().timestamp()

    def is_overdue(self) -> bool:
        """Check if the improvement is overdue."""
        if not self.due_date or self.status in ["implemented", "verified"]:
            return False
        return datetime.now() > self.due_date

    @staticmethod
    def create_new(
        title: str,
        description: str,
        source: str,
        source_id: Optional[str] = None,
        priority: str = "medium",
        assignees: List[str] = None,
        due_date: Optional[datetime] = None,
        implementation_plan: Optional[str] = None,
        verification_criteria: Optional[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'Improvement':
        """
        Create a new improvement with a generated ID.
        
        Args:
            title: Title of the improvement
            description: Description of the improvement
            source: Source of the improvement
            source_id: Optional ID of the source
            priority: Optional priority
            assignees: Optional list of assignees
            due_date: Optional due date
            implementation_plan: Optional implementation plan
            verification_criteria: Optional verification criteria
            tags: Optional list of tags
            metadata: Optional metadata
            
        Returns:
            A new Improvement instance
        """
        improvement_id = f"improvement-{uuid.uuid4()}"
        return Improvement(
            improvement_id=improvement_id,
            title=title,
            description=description,
            source=source,
            source_id=source_id,
            priority=priority,
            assignees=assignees,
            due_date=due_date,
            implementation_plan=implementation_plan,
            verification_criteria=verification_criteria,
            tags=tags,
            metadata=metadata
        )


class ImprovementRecommendation:
    """Model for a recommendation related to an improvement."""

    def __init__(
        self,
        recommendation_id: str,
        improvement_id: str,
        title: str,
        description: str,
        source: str,  # "ai", "human", "system", etc.
        priority: str = "medium",
        status: str = "pending",  # "pending", "accepted", "rejected", "implemented"
        implementation_details: Optional[str] = None,
        estimated_effort: Optional[str] = None,
        estimated_impact: Optional[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.recommendation_id = recommendation_id
        self.improvement_id = improvement_id
        self.title = title
        self.description = description
        self.source = source
        self.priority = priority
        self.status = status
        self.implementation_details = implementation_details
        self.estimated_effort = estimated_effort
        self.estimated_impact = estimated_impact
        self.tags = tags or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at
        self.status_history = [
            {
                "status": status,
                "timestamp": self.created_at,
                "comment": "Initial status"
            }
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the recommendation to a dictionary."""
        return {
            "recommendation_id": self.recommendation_id,
            "improvement_id": self.improvement_id,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "priority": self.priority,
            "status": self.status,
            "implementation_details": self.implementation_details,
            "estimated_effort": self.estimated_effort,
            "estimated_impact": self.estimated_impact,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status_history": self.status_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImprovementRecommendation':
        """Create a recommendation from a dictionary."""
        recommendation = cls(
            recommendation_id=data["recommendation_id"],
            improvement_id=data["improvement_id"],
            title=data["title"],
            description=data["description"],
            source=data["source"],
            priority=data.get("priority", "medium"),
            status=data.get("status", "pending"),
            implementation_details=data.get("implementation_details"),
            estimated_effort=data.get("estimated_effort"),
            estimated_impact=data.get("estimated_impact"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps and history if provided
        if "created_at" in data:
            recommendation.created_at = data["created_at"]
        if "updated_at" in data:
            recommendation.updated_at = data["updated_at"]
        if "status_history" in data:
            recommendation.status_history = data["status_history"]
            
        return recommendation

    def update_status(self, new_status: str, comment: Optional[str] = None) -> None:
        """
        Update the recommendation status with history tracking.
        
        Args:
            new_status: New status
            comment: Optional comment about the status change
        """
        self.status = new_status
        self.updated_at = datetime.now().timestamp()
        
        # Add to status history
        self.status_history.append({
            "status": new_status,
            "timestamp": self.updated_at,
            "comment": comment or f"Status updated to {new_status}"
        })

    @staticmethod
    def create_new(
        improvement_id: str,
        title: str,
        description: str,
        source: str,
        priority: str = "medium",
        implementation_details: Optional[str] = None,
        estimated_effort: Optional[str] = None,
        estimated_impact: Optional[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'ImprovementRecommendation':
        """
        Create a new recommendation with a generated ID.
        
        Args:
            improvement_id: ID of the associated improvement
            title: Title of the recommendation
            description: Description of the recommendation
            source: Source of the recommendation
            priority: Optional priority
            implementation_details: Optional implementation details
            estimated_effort: Optional effort estimation
            estimated_impact: Optional impact estimation
            tags: Optional list of tags
            metadata: Optional metadata
            
        Returns:
            A new ImprovementRecommendation instance
        """
        recommendation_id = f"recommendation-{uuid.uuid4()}"
        return ImprovementRecommendation(
            recommendation_id=recommendation_id,
            improvement_id=improvement_id,
            title=title,
            description=description,
            source=source,
            priority=priority,
            implementation_details=implementation_details,
            estimated_effort=estimated_effort,
            estimated_impact=estimated_impact,
            tags=tags,
            metadata=metadata
        )


class ImprovementPattern:
    """Model for a pattern of improvements identified across multiple retrospectives or projects."""

    def __init__(
        self,
        pattern_id: str,
        name: str,
        description: str,
        category: str,  # "process", "technical", "communication", etc.
        frequency: int = 1,  # Number of times this pattern has been observed
        related_improvements: List[str] = None,  # IDs of related improvements
        suggested_actions: List[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.pattern_id = pattern_id
        self.name = name
        self.description = description
        self.category = category
        self.frequency = frequency
        self.related_improvements = related_improvements or []
        self.suggested_actions = suggested_actions or []
        self.tags = tags or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the improvement pattern to a dictionary."""
        return {
            "pattern_id": self.pattern_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "frequency": self.frequency,
            "related_improvements": self.related_improvements,
            "suggested_actions": self.suggested_actions,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImprovementPattern':
        """Create an improvement pattern from a dictionary."""
        pattern = cls(
            pattern_id=data["pattern_id"],
            name=data["name"],
            description=data["description"],
            category=data["category"],
            frequency=data.get("frequency", 1),
            related_improvements=data.get("related_improvements", []),
            suggested_actions=data.get("suggested_actions", []),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            pattern.created_at = data["created_at"]
        if "updated_at" in data:
            pattern.updated_at = data["updated_at"]
            
        return pattern

    def increment_frequency(self):
        """Increment the frequency of the pattern."""
        self.frequency += 1
        self.updated_at = datetime.now().timestamp()

    def add_related_improvement(self, improvement_id: str):
        """Add a related improvement."""
        if improvement_id not in self.related_improvements:
            self.related_improvements.append(improvement_id)
            self.updated_at = datetime.now().timestamp()

    def add_suggested_action(self, action: str):
        """Add a suggested action."""
        if action not in self.suggested_actions:
            self.suggested_actions.append(action)
            self.updated_at = datetime.now().timestamp()

    def remove_suggested_action(self, action: str) -> bool:
        """Remove a suggested action."""
        if action in self.suggested_actions:
            self.suggested_actions.remove(action)
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    def add_tag(self, tag: str):
        """Add a tag to the pattern."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now().timestamp()

    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the pattern."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    @staticmethod
    def create_new(
        name: str,
        description: str,
        category: str,
        related_improvements: List[str] = None,
        suggested_actions: List[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'ImprovementPattern':
        """
        Create a new improvement pattern with a generated ID.
        
        Args:
            name: Name of the pattern
            description: Description of the pattern
            category: Category of the pattern
            related_improvements: Optional list of related improvement IDs
            suggested_actions: Optional list of suggested actions
            tags: Optional list of tags
            metadata: Optional metadata
            
        Returns:
            A new ImprovementPattern instance
        """
        pattern_id = f"pattern-{uuid.uuid4()}"
        return ImprovementPattern(
            pattern_id=pattern_id,
            name=name,
            description=description,
            category=category,
            related_improvements=related_improvements,
            suggested_actions=suggested_actions,
            tags=tags,
            metadata=metadata
        )