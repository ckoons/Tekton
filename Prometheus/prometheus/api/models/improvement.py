"""
Epimethius Improvement API Models

This module defines the API models for the Epimethius improvement endpoints.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from pydantic import Field
from tekton.models.base import TektonBaseModel


class ImprovementCreate(TektonBaseModel):
    """Schema for improvement creation."""
    title: str = Field(..., description="Title of the improvement", min_length=1)
    description: str = Field(..., description="Description of the improvement", min_length=1)
    source: str = Field(..., description="Source of the improvement", 
                       pattern="^(retrospective|analysis|manual|pattern|custom)$")
    source_id: Optional[str] = Field(None, description="ID of the source")
    priority: str = Field("medium", description="Priority of the improvement", 
                         pattern="^(low|medium|high|critical)$")
    assignees: Optional[List[str]] = Field(None, description="Assignees of the improvement")
    due_date: Optional[datetime] = Field(None, description="Due date of the improvement")
    implementation_plan: Optional[str] = Field(None, description="Implementation plan")
    verification_criteria: Optional[str] = Field(None, description="Verification criteria")
    tags: Optional[List[str]] = Field(None, description="Tags for the improvement")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ImprovementUpdate(TektonBaseModel):
    """Schema for improvement update."""
    title: Optional[str] = Field(None, description="Title of the improvement", min_length=1)
    description: Optional[str] = Field(None, description="Description of the improvement", min_length=1)
    priority: Optional[str] = Field(None, description="Priority of the improvement", 
                                   pattern="^(low|medium|high|critical)$")
    status: Optional[str] = Field(None, description="Status of the improvement", 
                                 pattern="^(open|in_progress|implemented|verified)$")
    assignees: Optional[List[str]] = Field(None, description="Assignees of the improvement")
    due_date: Optional[datetime] = Field(None, description="Due date of the improvement")
    implementation_plan: Optional[str] = Field(None, description="Implementation plan")
    verification_criteria: Optional[str] = Field(None, description="Verification criteria")
    tags: Optional[List[str]] = Field(None, description="Tags for the improvement")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ImprovementStatusUpdate(TektonBaseModel):
    """Schema for improvement status update."""
    status: str = Field(..., description="New status of the improvement", 
                       pattern="^(open|in_progress|implemented|verified)$")
    comment: Optional[str] = Field(None, description="Comment about the status change")


class ImprovementPatternCreate(TektonBaseModel):
    """Schema for improvement pattern creation."""
    name: str = Field(..., description="Name of the pattern", min_length=1)
    description: str = Field(..., description="Description of the pattern", min_length=1)
    category: str = Field(..., description="Category of the pattern", 
                         pattern="^(process|technical|communication|resource|quality|custom)$")
    related_improvements: Optional[List[str]] = Field(None, description="IDs of related improvements")
    suggested_actions: Optional[List[str]] = Field(None, description="Suggested actions")
    tags: Optional[List[str]] = Field(None, description="Tags for the pattern")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ImprovementPatternUpdate(TektonBaseModel):
    """Schema for improvement pattern update."""
    name: Optional[str] = Field(None, description="Name of the pattern", min_length=1)
    description: Optional[str] = Field(None, description="Description of the pattern", min_length=1)
    category: Optional[str] = Field(None, description="Category of the pattern", 
                                   pattern="^(process|technical|communication|resource|quality|custom)$")
    frequency: Optional[int] = Field(None, description="Frequency of the pattern", ge=1)
    related_improvements: Optional[List[str]] = Field(None, description="IDs of related improvements")
    suggested_actions: Optional[List[str]] = Field(None, description="Suggested actions")
    tags: Optional[List[str]] = Field(None, description="Tags for the pattern")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ImprovementSuggestionRequest(TektonBaseModel):
    """Schema for improvement suggestion request."""
    source_type: str = Field(..., description="Type of source for suggestions", 
                           pattern="^(retrospective|performance|pattern|history|custom)$")
    source_id: Optional[str] = Field(None, description="ID of the source")
    limit: Optional[int] = Field(5, description="Maximum number of suggestions", ge=1)
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters for suggestions")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ImprovementProgressRequest(TektonBaseModel):
    """Schema for improvement progress request."""
    source_type: Optional[str] = Field(None, description="Type of source for improvements", 
                                     pattern="^(retrospective|performance|pattern|all)$")
    source_id: Optional[str] = Field(None, description="ID of the source")
    status: Optional[List[str]] = Field(None, description="Statuses to include")
    time_range: Optional[Dict[str, Any]] = Field(None, description="Time range for the progress")
    group_by: Optional[str] = Field(None, description="Group by dimension", 
                                   pattern="^(status|priority|source|assignee|tag|custom)$")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class LLMImprovementSuggestion(TektonBaseModel):
    """Schema for LLM-based improvement suggestion."""
    context_type: str = Field(..., description="Type of context for suggestions", 
                            pattern="^(retrospective|performance|execution|history|custom)$")
    context_id: str = Field(..., description="ID of the context")
    analysis_depth: Optional[str] = Field("comprehensive", description="Depth of analysis", 
                                        pattern="^(simple|comprehensive|deep)$")
    max_suggestions: Optional[int] = Field(5, description="Maximum number of suggestions", ge=1)
    focus_areas: Optional[List[str]] = Field(None, description="Areas to focus on")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class LLMRootCauseAnalysis(TektonBaseModel):
    """Schema for LLM-based root cause analysis."""
    issue_id: str = Field(..., description="ID of the issue to analyze")
    context_ids: Optional[List[str]] = Field(None, description="IDs of additional context")
    analysis_depth: Optional[str] = Field("comprehensive", description="Depth of analysis", 
                                        pattern="^(simple|comprehensive|deep)$")
    suggest_solutions: Optional[bool] = Field(True, description="Whether to suggest solutions")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")