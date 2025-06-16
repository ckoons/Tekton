"""
Prometheus Planning API Models

This module defines the API models for the Prometheus planning endpoints.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from pydantic import Field, field_validator
from tekton.models.base import TektonBaseModel


class TaskCreate(TektonBaseModel):
    """Schema for task creation."""
    name: str = Field(..., description="Name of the task", min_length=1)
    description: str = Field(..., description="Description of the task", min_length=1)
    priority: str = Field(..., description="Priority of the task", 
                          pattern="^(low|medium|high|critical)$")
    estimated_effort: float = Field(..., description="Estimated effort for the task", ge=0)
    assigned_resources: Optional[List[str]] = Field(None, description="IDs of assigned resources")
    dependencies: Optional[List[str]] = Field(None, description="IDs of dependency tasks")
    requirements: Optional[List[str]] = Field(None, description="IDs of related requirements")
    start_date: Optional[datetime] = Field(None, description="Planned start date")
    end_date: Optional[datetime] = Field(None, description="Planned end date")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @field_validator('end_date')
    @classmethod
    def end_date_after_start_date(cls, v, info):
        if v and 'start_date' in info.data and info.data['start_date'] and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class TaskUpdate(TektonBaseModel):
    """Schema for task update."""
    name: Optional[str] = Field(None, description="Name of the task", min_length=1)
    description: Optional[str] = Field(None, description="Description of the task", min_length=1)
    status: Optional[str] = Field(None, description="Status of the task", 
                                  pattern="^(not_started|in_progress|completed|blocked|cancelled)$")
    priority: Optional[str] = Field(None, description="Priority of the task", 
                                  pattern="^(low|medium|high|critical)$")
    estimated_effort: Optional[float] = Field(None, description="Estimated effort for the task", ge=0)
    actual_effort: Optional[float] = Field(None, description="Actual effort for the task", ge=0)
    assigned_resources: Optional[List[str]] = Field(None, description="IDs of assigned resources")
    dependencies: Optional[List[str]] = Field(None, description="IDs of dependency tasks")
    requirements: Optional[List[str]] = Field(None, description="IDs of related requirements")
    start_date: Optional[datetime] = Field(None, description="Planned start date")
    end_date: Optional[datetime] = Field(None, description="Planned end date")
    progress: Optional[float] = Field(None, description="Progress of the task", ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @field_validator('end_date')
    @classmethod
    def end_date_after_start_date(cls, v, info):
        if v and 'start_date' in info.data and info.data['start_date'] and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class MilestoneCreate(TektonBaseModel):
    """Schema for milestone creation."""
    name: str = Field(..., description="Name of the milestone", min_length=1)
    description: str = Field(..., description="Description of the milestone", min_length=1)
    target_date: datetime = Field(..., description="Target date for the milestone")
    criteria: Optional[List[str]] = Field(None, description="Completion criteria")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MilestoneUpdate(TektonBaseModel):
    """Schema for milestone update."""
    name: Optional[str] = Field(None, description="Name of the milestone", min_length=1)
    description: Optional[str] = Field(None, description="Description of the milestone", min_length=1)
    target_date: Optional[datetime] = Field(None, description="Target date for the milestone")
    status: Optional[str] = Field(None, description="Status of the milestone", 
                                  pattern="^(not_started|in_progress|completed|missed)$")
    actual_date: Optional[datetime] = Field(None, description="Actual date of milestone achievement")
    criteria: Optional[List[str]] = Field(None, description="Completion criteria")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PlanCreate(TektonBaseModel):
    """Schema for plan creation."""
    name: str = Field(..., description="Name of the plan", min_length=1)
    description: str = Field(..., description="Description of the plan", min_length=1)
    start_date: datetime = Field(..., description="Start date of the plan")
    end_date: datetime = Field(..., description="End date of the plan")
    methodology: str = Field(..., description="Methodology for the plan", 
                           pattern="^(agile|waterfall|hybrid|kanban|custom)$")
    requirements: Optional[List[str]] = Field(None, description="IDs of related requirements")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @field_validator('end_date')
    @classmethod
    def end_date_after_start_date(cls, v, info):
        if v and 'start_date' in info.data and info.data['start_date'] and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class PlanUpdate(TektonBaseModel):
    """Schema for plan update."""
    name: Optional[str] = Field(None, description="Name of the plan", min_length=1)
    description: Optional[str] = Field(None, description="Description of the plan", min_length=1)
    start_date: Optional[datetime] = Field(None, description="Start date of the plan")
    end_date: Optional[datetime] = Field(None, description="End date of the plan")
    methodology: Optional[str] = Field(None, description="Methodology for the plan", 
                                     pattern="^(agile|waterfall|hybrid|kanban|custom)$")
    requirements: Optional[List[str]] = Field(None, description="IDs of related requirements")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @field_validator('end_date')
    @classmethod
    def end_date_after_start_date(cls, v, info):
        if v and 'start_date' in info.data and info.data['start_date'] and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class PlanFromRequirements(TektonBaseModel):
    """Schema for creating a plan from requirements."""
    name: str = Field(..., description="Name of the plan", min_length=1)
    description: Optional[str] = Field(None, description="Description of the plan")
    requirements: List[str] = Field(..., description="IDs of requirements to include in the plan")
    methodology: str = Field(..., description="Methodology for the plan", 
                           pattern="^(agile|waterfall|hybrid|kanban|custom)$")
    start_date: Optional[datetime] = Field(None, description="Start date of the plan")
    duration_days: Optional[int] = Field(None, description="Duration of the plan in days", gt=0)
    allocated_resources: Optional[List[str]] = Field(None, description="IDs of resources to allocate")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Constraints for the plan")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ResourceCreate(TektonBaseModel):
    """Schema for resource creation."""
    name: str = Field(..., description="Name of the resource", min_length=1)
    resource_type: str = Field(..., description="Type of the resource", 
                             pattern="^(human|equipment|service|facility|budget|custom)$")
    capacity: float = Field(..., description="Capacity of the resource", gt=0)
    skills: Optional[List[str]] = Field(None, description="Skills of the resource")
    availability: Optional[Dict[str, Any]] = Field(None, description="Availability of the resource")
    cost_rate: Optional[float] = Field(None, description="Cost rate of the resource", ge=0)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ResourceUpdate(TektonBaseModel):
    """Schema for resource update."""
    name: Optional[str] = Field(None, description="Name of the resource", min_length=1)
    resource_type: Optional[str] = Field(None, description="Type of the resource", 
                                       pattern="^(human|equipment|service|facility|budget|custom)$")
    capacity: Optional[float] = Field(None, description="Capacity of the resource", gt=0)
    skills: Optional[List[str]] = Field(None, description="Skills of the resource")
    availability: Optional[Dict[str, Any]] = Field(None, description="Availability of the resource")
    cost_rate: Optional[float] = Field(None, description="Cost rate of the resource", ge=0)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ResourceAllocation(TektonBaseModel):
    """Schema for resource allocation to a plan."""
    plan_id: str = Field(..., description="ID of the plan")
    allocations: Dict[str, List[Dict[str, Any]]] = Field(
        ..., 
        description="Dictionary mapping resource IDs to task allocations"
    )
    optimization_strategy: Optional[str] = Field(
        None, 
        description="Strategy for optimization", 
        pattern="^(minimize_duration|minimize_cost|balance_workload|custom)$"
    )
    constraints: Optional[Dict[str, Any]] = Field(None, description="Constraints for allocation")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TaskDependency(TektonBaseModel):
    """Schema for task dependency."""
    predecessor_id: str = Field(..., description="ID of the predecessor task")
    successor_id: str = Field(..., description="ID of the successor task")
    dependency_type: str = Field(
        "finish_to_start", 
        description="Type of dependency", 
        pattern="^(finish_to_start|start_to_start|finish_to_finish|start_to_finish)$"
    )
    lag: Optional[int] = Field(0, description="Lag time in days")


class TimelineEntry(TektonBaseModel):
    """Schema for timeline entry."""
    entity_id: str = Field(..., description="ID of the entity (task or milestone)")
    entity_type: str = Field(..., description="Type of the entity", pattern="^(task|milestone)$")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    status: str = Field("scheduled", description="Status of the entry")
    dependencies: Optional[List[str]] = Field(None, description="IDs of dependent entries")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @field_validator('end_date')
    @classmethod
    def end_date_after_start_date(cls, v, info):
        if v and 'start_date' in info.data and info.data['start_date'] and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class TimelineCreate(TektonBaseModel):
    """Schema for timeline creation."""
    plan_id: str = Field(..., description="ID of the plan")
    entries: List[TimelineEntry] = Field(..., description="Timeline entries")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TimelineUpdate(TektonBaseModel):
    """Schema for timeline update."""
    entries: Optional[List[TimelineEntry]] = Field(None, description="Timeline entries to update")
    entries_to_remove: Optional[List[str]] = Field(None, description="Entry IDs to remove")
    entries_to_add: Optional[List[TimelineEntry]] = Field(None, description="New entries to add")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class LLMPlanAnalysis(TektonBaseModel):
    """Schema for LLM-based plan analysis."""
    plan_id: str = Field(..., description="ID of the plan to analyze")
    analysis_type: str = Field(
        ..., 
        description="Type of analysis", 
        pattern="^(risk|quality|completeness|dependencies|resource_allocation|timeline|custom)$"
    )
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for analysis")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for the response")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")