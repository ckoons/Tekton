"""
Requirement data models for Telos requirements management.

This module provides Pydantic models for requirement data.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import Field, ConfigDict
from tekton.models.base import TektonBaseModel

class HistoryEntry(TektonBaseModel):
    """Model for requirement history entry."""
    timestamp: float
    action: str
    description: str

class RequirementBase(TektonBaseModel):
    """Base model for requirement data."""
    title: str
    description: str
    requirement_type: str = "functional"
    priority: str = "medium"
    status: str = "new"
    tags: Optional[List[str]] = None
    parent_id: Optional[str] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class RequirementCreate(RequirementBase):
    """Model for requirement creation."""
    created_by: Optional[str] = None

class RequirementUpdate(TektonBaseModel):
    """Model for requirement updates."""
    title: Optional[str] = None
    description: Optional[str] = None
    requirement_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    parent_id: Optional[str] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class RequirementModel(RequirementBase):
    """Model for requirement data."""
    requirement_id: str
    created_at: float
    updated_at: float
    created_by: Optional[str] = None
    history: List[HistoryEntry] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)

class RequirementListItem(TektonBaseModel):
    """Model for requirement list item."""
    requirement_id: str
    title: str
    description: str
    requirement_type: str
    priority: str
    status: str
    created_at: float
    updated_at: float

class RequirementList(TektonBaseModel):
    """Model for requirement list."""
    requirements: List[RequirementListItem]
    count: int

class RequirementRefinement(TektonBaseModel):
    """Model for requirement refinement."""
    feedback: str
    auto_update: Optional[bool] = False

class RequirementRefinementResult(TektonBaseModel):
    """Model for requirement refinement result."""
    requirement_id: str
    original: RequirementModel
    refined: Optional[RequirementModel] = None
    status: str
    message: str
    changes: Optional[List[str]] = None