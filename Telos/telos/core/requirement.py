"""Requirement model for Telos.

This module provides a class for representing user requirements.
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class Requirement:
    """A user requirement or goal."""
    
    def __init__(
        self,
        title: str,
        description: str,
        requirement_id: Optional[str] = None,
        requirement_type: str = "functional",
        priority: str = "medium",
        status: str = "new",
        created_by: Optional[str] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a requirement.
        
        Args:
            title: Short title for the requirement
            description: Detailed description
            requirement_id: Unique identifier
            requirement_type: Type of requirement (functional, non-functional, constraint, etc.)
            priority: Priority level (low, medium, high, critical)
            status: Current status (new, accepted, in-progress, completed, rejected)
            created_by: ID or name of creator
            created_at: Creation timestamp
            updated_at: Last update timestamp
            tags: Tags for categorization
            parent_id: ID of parent requirement if this is a sub-requirement
            dependencies: IDs of requirements this depends on
            metadata: Additional metadata
        """
        self.title = title
        self.description = description
        self.requirement_id = requirement_id or str(uuid.uuid4())
        self.requirement_type = requirement_type
        self.priority = priority
        self.status = status
        self.created_by = created_by
        self.created_at = created_at or datetime.now().timestamp()
        self.updated_at = updated_at or self.created_at
        self.tags = tags or []
        self.parent_id = parent_id
        self.dependencies = dependencies or []
        self.metadata = metadata or {}
        self.history: List[Dict[str, Any]] = []
        
        # Add the initial state to history
        self._add_history_entry("created", "Requirement created")
    
    def update(self, **kwargs) -> None:
        """Update requirement attributes.
        
        Args:
            **kwargs: Attributes to update
        """
        changes = []
        for key, value in kwargs.items():
            if hasattr(self, key) and getattr(self, key) != value:
                old_value = getattr(self, key)
                setattr(self, key, value)
                changes.append(f"{key}: {old_value} -> {value}")
        
        if changes:
            self.updated_at = datetime.now().timestamp()
            self._add_history_entry("updated", "Updated attributes: " + ", ".join(changes))
    
    def _add_history_entry(self, action: str, description: str) -> None:
        """Add an entry to the requirement history.
        
        Args:
            action: The action performed
            description: Description of the change
        """
        self.history.append({
            "timestamp": datetime.now().timestamp(),
            "action": action,
            "description": description
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the requirement to a dictionary."""
        return {
            "requirement_id": self.requirement_id,
            "title": self.title,
            "description": self.description,
            "requirement_type": self.requirement_type,
            "priority": self.priority,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": self.tags,
            "parent_id": self.parent_id,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "history": self.history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Requirement':
        """Create a requirement from a dictionary."""
        requirement = cls(
            title=data["title"],
            description=data["description"],
            requirement_id=data.get("requirement_id"),
            requirement_type=data.get("requirement_type", "functional"),
            priority=data.get("priority", "medium"),
            status=data.get("status", "new"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            tags=data.get("tags"),
            parent_id=data.get("parent_id"),
            dependencies=data.get("dependencies"),
            metadata=data.get("metadata")
        )
        
        # Add history if present
        if "history" in data:
            requirement.history = data["history"]
        
        return requirement