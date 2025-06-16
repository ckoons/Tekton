"""
Requirement reference models for Metis

This module defines the models for referencing requirements from other Tekton
components, primarily Telos.
"""

from datetime import datetime
from pydantic import Field
from uuid import uuid4
from typing import Optional, List, Dict, Any
from tekton.models.base import TektonBaseModel


class RequirementRef(TektonBaseModel):
    """
    Reference to a requirement from another system (e.g., Telos).
    
    This model allows tasks to be linked to external requirements, providing
    traceability between requirements and implementation tasks.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    requirement_id: str  # ID of the external requirement
    source: str = "telos"  # Source component (default to Telos)
    requirement_type: str  # Type of requirement (e.g., "functional", "non-functional")
    title: str  # Title of the requirement for reference
    relationship: str = "implements"  # Relationship type: implements, related_to, blocks
    description: Optional[str] = None  # Optional context for this reference
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update requirement reference fields.
        
        Args:
            updates: Dictionary of field updates
        """
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Update timestamp
        self.updated_at = datetime.utcnow()


class RequirementSyncStatus(TektonBaseModel):
    """
    Status of requirement synchronization with external systems.
    
    Tracks the last synchronization time and status for auditing and
    troubleshooting purposes.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str  # ID of the task being synchronized
    requirement_id: str  # ID of the requirement being synchronized
    source: str  # Source component (e.g., "telos")
    status: str  # Status of synchronization (success, failed, partial)
    last_sync: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None  # Error message if synchronization failed
    details: Optional[Dict[str, Any]] = None  # Additional details about sync