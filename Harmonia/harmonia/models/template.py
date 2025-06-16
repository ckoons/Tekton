"""
Template models for Harmonia.

This module defines the data models for template functionality,
including parameterization, versioning, and template instantiation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import Field, validator
from tekton.models import TektonBaseModel

from harmonia.models.workflow import WorkflowDefinition


class ParameterDefinition(TektonBaseModel):
    """Definition of a template parameter."""
    
    name: str = Field(..., description="Name of the parameter")
    type: str = Field(..., description="Type of the parameter (string, number, boolean, array, object)")
    description: Optional[str] = Field(None, description="Description of the parameter")
    default: Optional[Any] = Field(None, description="Default value for the parameter")
    required: bool = Field(False, description="Whether the parameter is required")
    enum: Optional[List[Any]] = Field(None, description="List of allowed values for the parameter")
    min_value: Optional[float] = Field(None, description="Minimum value for number parameters")
    max_value: Optional[float] = Field(None, description="Maximum value for number parameters")
    min_length: Optional[int] = Field(None, description="Minimum length for string or array parameters")
    max_length: Optional[int] = Field(None, description="Maximum length for string or array parameters")
    pattern: Optional[str] = Field(None, description="Regex pattern for string parameters")
    
    @validator("type")
    def validate_type(cls, v):
        """Validate parameter type."""
        allowed_types = ["string", "number", "integer", "boolean", "array", "object"]
        if v not in allowed_types:
            raise ValueError(f"Type must be one of: {', '.join(allowed_types)}")
        return v


class TemplateVersion(TektonBaseModel):
    """Version information for a template."""
    
    version: str = Field(..., description="Version identifier (e.g., '1.0.0')")
    workflow_definition: WorkflowDefinition = Field(..., description="Workflow definition for this version")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    is_latest: bool = Field(False, description="Whether this is the latest version")
    changes: Optional[str] = Field(None, description="Description of changes from previous version")


class TemplateCategory(TektonBaseModel):
    """Category for organizing templates."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the category")
    name: str = Field(..., description="Name of the category")
    description: Optional[str] = Field(None, description="Description of the category")
    parent_id: Optional[UUID] = Field(None, description="ID of the parent category")


class Template(TektonBaseModel):
    """Template for creating workflows."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the template")
    name: str = Field(..., description="Human-readable name for the template")
    description: Optional[str] = Field(None, description="Description of the template")
    parameters: Dict[str, ParameterDefinition] = Field(default_factory=dict, description="Parameters for the template")
    current_version: str = Field("1.0.0", description="Current version of the template")
    versions: Dict[str, TemplateVersion] = Field(default_factory=dict, description="All versions of the template")
    category_ids: List[UUID] = Field(default_factory=list, description="Categories this template belongs to")
    tags: List[str] = Field(default_factory=list, description="Tags for this template")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="User who created the template")
    is_public: bool = Field(True, description="Whether the template is public or private")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def get_current_version(self) -> Optional[TemplateVersion]:
        """Get the current version of the template."""
        return self.versions.get(self.current_version)
    
    def get_workflow_definition(self) -> Optional[WorkflowDefinition]:
        """Get the workflow definition for the current version."""
        version = self.get_current_version()
        if version:
            return version.workflow_definition
        return None


class TemplateInstantiation(TektonBaseModel):
    """Information about a template instantiation."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the instantiation")
    template_id: UUID = Field(..., description="ID of the template that was instantiated")
    template_version: str = Field(..., description="Version of the template that was instantiated")
    workflow_id: UUID = Field(..., description="ID of the workflow that was created")
    parameter_values: Dict[str, Any] = Field(default_factory=dict, description="Values provided for parameters")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    created_by: Optional[str] = Field(None, description="User who created the instantiation")