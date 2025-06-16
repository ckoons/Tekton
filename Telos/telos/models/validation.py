"""
Validation data models for Telos requirements management.

This module provides Pydantic models for requirement validation.
"""

from typing import Dict, List, Optional, Any
from pydantic import Field
from tekton.models.base import TektonBaseModel

class ValidationCriteria(TektonBaseModel):
    """Model for validation criteria."""
    check_completeness: Optional[bool] = True
    check_verifiability: Optional[bool] = True
    check_clarity: Optional[bool] = True
    check_consistency: Optional[bool] = False
    check_feasibility: Optional[bool] = False
    custom_criteria: Optional[Dict[str, Any]] = None

class ValidationIssue(TektonBaseModel):
    """Model for validation issue."""
    type: str
    message: str
    severity: Optional[str] = "warning"
    suggestion: Optional[str] = None

class RequirementValidationResult(TektonBaseModel):
    """Model for requirement validation result."""
    requirement_id: str
    title: str
    issues: List[ValidationIssue] = Field(default_factory=list)
    passed: bool = True
    score: Optional[float] = None

class ValidationSummary(TektonBaseModel):
    """Model for validation summary."""
    total_requirements: int
    passed: int
    failed: int
    pass_percentage: float
    issues_by_type: Optional[Dict[str, int]] = None

class ValidationModel(TektonBaseModel):
    """Model for validation result."""
    project_id: str
    validation_date: float
    results: List[RequirementValidationResult]
    summary: ValidationSummary
    criteria: ValidationCriteria