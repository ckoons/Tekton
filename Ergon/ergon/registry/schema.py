"""
Registry Schema Validation Module

Provides JSON schema validation for Registry entries and operations.
Ensures data integrity and consistency across all Registry operations.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, validator, ValidationError


class SolutionType(str, Enum):
    """Valid types for Registry solutions"""
    SOLUTION = "solution"
    CONTAINER = "container"
    TOOL = "tool"
    CONFIG = "config"


class SourceInfo(BaseModel):
    """Source information linking to TektonCore projects"""
    project_id: Optional[str] = Field(None, description="TektonCore project ID")
    sprint_id: Optional[str] = Field(None, description="Development sprint ID")
    location: str = Field(..., description="Local path or GitHub URL")
    
    @validator('location')
    def validate_location(cls, v):
        """Validate location is either a path or URL"""
        if not v:
            raise ValueError("Location cannot be empty")
        # Basic validation - either starts with / or http(s)://
        if not (v.startswith('/') or v.startswith('http://') or v.startswith('https://')):
            raise ValueError("Location must be an absolute path or HTTP(S) URL")
        return v


class RegistryEntry(BaseModel):
    """Complete Registry entry schema"""
    id: Optional[str] = Field(None, description="UUID for the entry")
    type: SolutionType = Field(..., description="Type of the solution")
    version: str = Field(..., description="Semantic version")
    name: str = Field(..., description="Human-readable name")
    created: Optional[datetime] = Field(None, description="Creation timestamp")
    updated: Optional[datetime] = Field(None, description="Last update timestamp")
    meets_standards: bool = Field(False, description="Standards compliance status")
    lineage: List[str] = Field(default_factory=list, description="Parent solution IDs")
    source: Optional[SourceInfo] = Field(None, description="Source information")
    content: Dict[str, Any] = Field(default_factory=dict, description="Type-specific content")
    description: Optional[str] = Field(None, description="Solution description")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    
    @validator('version')
    def validate_semver(cls, v):
        """Validate semantic versioning format"""
        # Basic semver pattern: MAJOR.MINOR.PATCH with optional pre-release and build
        pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
        if not re.match(pattern, v):
            raise ValueError(f"Invalid semantic version: {v}")
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name is not empty and reasonable length"""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        if len(v) > 200:
            raise ValueError("Name too long (max 200 characters)")
        return v.strip()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class StandardsCheckRequest(BaseModel):
    """Request model for standards checking"""
    solution_id: str = Field(..., description="Solution ID to check")
    standards_to_apply: Optional[List[str]] = Field(None, description="Specific standards to check")
    auto_create_sprint: bool = Field(True, description="Auto-create refactor sprint if non-compliant")


class StandardsCheckResult(BaseModel):
    """Result of standards compliance check"""
    solution_id: str
    meets_standards: bool
    compliance_percentage: float = Field(ge=0, le=100)
    violations: List[Dict[str, str]] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    refactor_sprint_id: Optional[str] = None


class SearchQuery(BaseModel):
    """Search query parameters"""
    type: Optional[SolutionType] = None
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    meets_standards: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


def validate_registry_entry(data: Dict[str, Any]) -> tuple[bool, Optional[RegistryEntry], Optional[str]]:
    """
    Validate a registry entry against the schema
    
    Args:
        data: Dictionary containing entry data
    
    Returns:
        Tuple of (is_valid, validated_entry, error_message)
    """
    try:
        entry = RegistryEntry(**data)
        return True, entry, None
    except ValidationError as e:
        error_msg = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
        return False, None, error_msg


def validate_partial_update(data: Dict[str, Any]) -> tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validate partial update data (not all fields required)
    
    Args:
        data: Dictionary containing partial update data
    
    Returns:
        Tuple of (is_valid, validated_data, error_message)
    """
    try:
        # Only validate provided fields
        if 'type' in data and data['type'] not in [t.value for t in SolutionType]:
            return False, {}, f"Invalid type: {data['type']}"
        
        if 'version' in data:
            entry = RegistryEntry(
                type=SolutionType.SOLUTION,  # Dummy value for validation
                version=data['version'],
                name="dummy"  # Dummy value for validation
            )
        
        if 'source' in data:
            SourceInfo(**data['source'])
        
        # Update timestamp
        data['updated'] = datetime.utcnow().isoformat()
        
        return True, data, None
    except ValidationError as e:
        error_msg = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
        return False, {}, error_msg


def create_minimal_entry(name: str, type: str = "solution", version: str = "1.0.0") -> Dict[str, Any]:
    """
    Create a minimal valid registry entry
    
    Args:
        name: Solution name
        type: Solution type
        version: Semantic version
    
    Returns:
        Dictionary with minimal valid entry data
    """
    return {
        "name": name,
        "type": type,
        "version": version,
        "meets_standards": False,
        "lineage": [],
        "content": {},
        "tags": []
    }


def enrich_entry_for_storage(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich entry data with defaults before storage
    
    Args:
        data: Entry data to enrich
    
    Returns:
        Enriched entry data
    """
    # Ensure all required fields have defaults
    enriched = data.copy()
    
    # Add timestamps if not present
    now = datetime.utcnow().isoformat()
    if 'created' not in enriched:
        enriched['created'] = now
    if 'updated' not in enriched:
        enriched['updated'] = now
    
    # Ensure lists exist
    if 'lineage' not in enriched:
        enriched['lineage'] = []
    if 'tags' not in enriched:
        enriched['tags'] = []
    
    # Ensure content dict exists
    if 'content' not in enriched:
        enriched['content'] = {}
    
    # Default standards compliance
    if 'meets_standards' not in enriched:
        enriched['meets_standards'] = False
    
    return enriched


# Export models and functions
__all__ = [
    'SolutionType',
    'SourceInfo',
    'RegistryEntry',
    'StandardsCheckRequest',
    'StandardsCheckResult',
    'SearchQuery',
    'validate_registry_entry',
    'validate_partial_update',
    'create_minimal_entry',
    'enrich_entry_for_storage'
]