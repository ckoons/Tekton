"""Project model for Telos.

This module provides a class for representing requirement projects.
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from telos.core.requirement import Requirement

logger = logging.getLogger(__name__)


class Project:
    """A project containing requirements."""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        project_id: Optional[str] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a project.
        
        Args:
            name: Project name
            description: Project description
            project_id: Unique identifier
            created_at: Creation timestamp
            updated_at: Last update timestamp
            metadata: Additional metadata
        """
        self.name = name
        self.description = description
        self.project_id = project_id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now().timestamp()
        self.updated_at = updated_at or self.created_at
        self.metadata = metadata or {}
        self.requirements: Dict[str, Requirement] = {}
    
    def add_requirement(self, requirement: Requirement) -> str:
        """Add a requirement to the project.
        
        Args:
            requirement: The requirement to add
            
        Returns:
            The requirement ID
        """
        self.requirements[requirement.requirement_id] = requirement
        self.updated_at = datetime.now().timestamp()
        return requirement.requirement_id
    
    def get_requirement(self, requirement_id: str) -> Optional[Requirement]:
        """Get a requirement by ID.
        
        Args:
            requirement_id: The requirement ID
            
        Returns:
            The requirement or None if not found
        """
        return self.requirements.get(requirement_id)
    
    def update_requirement(self, requirement_id: str, **kwargs) -> bool:
        """Update a requirement.
        
        Args:
            requirement_id: The requirement ID
            **kwargs: Attributes to update
            
        Returns:
            Success status
        """
        requirement = self.get_requirement(requirement_id)
        if not requirement:
            return False
        
        requirement.update(**kwargs)
        self.updated_at = datetime.now().timestamp()
        return True
    
    def delete_requirement(self, requirement_id: str) -> bool:
        """Delete a requirement.
        
        Args:
            requirement_id: The requirement ID
            
        Returns:
            Success status
        """
        if requirement_id in self.requirements:
            del self.requirements[requirement_id]
            self.updated_at = datetime.now().timestamp()
            return True
        return False
    
    def get_all_requirements(
        self,
        status: Optional[str] = None,
        requirement_type: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Requirement]:
        """Get all requirements matching the filters.
        
        Args:
            status: Filter by status
            requirement_type: Filter by type
            priority: Filter by priority
            tag: Filter by tag
            
        Returns:
            List of matching requirements
        """
        requirements = list(self.requirements.values())
        
        # Apply filters
        if status:
            requirements = [r for r in requirements if r.status == status]
        
        if requirement_type:
            requirements = [r for r in requirements if r.requirement_type == requirement_type]
        
        if priority:
            requirements = [r for r in requirements if r.priority == priority]
        
        if tag:
            requirements = [r for r in requirements if tag in r.tags]
        
        return requirements
    
    def get_requirement_hierarchy(self) -> Dict[str, List[str]]:
        """Get the hierarchy of requirements.
        
        Returns:
            Dictionary mapping parent IDs to lists of child IDs
        """
        hierarchy = {"root": []}
        
        for req_id, requirement in self.requirements.items():
            parent_id = requirement.parent_id or "root"
            
            if parent_id not in hierarchy:
                hierarchy[parent_id] = []
            
            hierarchy[parent_id].append(req_id)
        
        return hierarchy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the project to a dictionary."""
        return {
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "requirements": {
                req_id: req.to_dict() for req_id, req in self.requirements.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create a project from a dictionary."""
        project = cls(
            name=data["name"],
            description=data.get("description", ""),
            project_id=data.get("project_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            metadata=data.get("metadata")
        )
        
        # Add requirements
        for req_id, req_data in data.get("requirements", {}).items():
            requirement = Requirement.from_dict(req_data)
            project.requirements[req_id] = requirement
        
        return project