"""
API schemas for Metis

This module defines the Pydantic schemas used for API request and response validation.
These schemas are based on the core data models but adapted for API usage.
"""

from datetime import datetime
from pydantic import Field, field_validator
from typing import Optional, List, Dict, Any
from uuid import uuid4
from tekton.models.base import TektonBaseModel

from metis.models.enums import TaskStatus, Priority, ComplexityLevel


# Base schema for API responses
class ApiResponse(TektonBaseModel):
    """Base model for API responses with standard fields."""
    success: bool = True
    message: Optional[str] = None


# Subtask schemas
class SubtaskCreate(TektonBaseModel):
    """Schema for creating a new subtask."""
    title: str
    description: Optional[str] = None
    status: str = TaskStatus.PENDING.value
    order: int = 0


class SubtaskUpdate(TektonBaseModel):
    """Schema for updating a subtask."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    order: Optional[int] = None


class SubtaskResponse(TektonBaseModel):
    """Schema for subtask response."""
    id: str
    title: str
    description: Optional[str] = None
    status: str
    order: int
    created_at: datetime
    updated_at: datetime


# Complexity schemas
class ComplexityFactorCreate(TektonBaseModel):
    """Schema for creating a complexity factor."""
    name: str
    description: str
    weight: float = 1.0
    score: int = 3
    notes: Optional[str] = None


class ComplexityFactorUpdate(TektonBaseModel):
    """Schema for updating a complexity factor."""
    name: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[float] = None
    score: Optional[int] = None
    notes: Optional[str] = None


class ComplexityFactorResponse(TektonBaseModel):
    """Schema for complexity factor response."""
    id: str
    name: str
    description: str
    weight: float
    score: int
    notes: Optional[str] = None


class ComplexityScoreResponse(TektonBaseModel):
    """Schema for complexity score response."""
    id: str
    factors: List[ComplexityFactorResponse] = []
    overall_score: float
    level: str
    created_at: datetime
    updated_at: datetime


# Requirement reference schemas
class RequirementRefCreate(TektonBaseModel):
    """Schema for creating a requirement reference."""
    requirement_id: str
    source: str = "telos"
    requirement_type: str
    title: str
    relationship: str = "implements"
    description: Optional[str] = None


class RequirementRefUpdate(TektonBaseModel):
    """Schema for updating a requirement reference."""
    requirement_id: Optional[str] = None
    source: Optional[str] = None
    requirement_type: Optional[str] = None
    title: Optional[str] = None
    relationship: Optional[str] = None
    description: Optional[str] = None


class RequirementRefResponse(TektonBaseModel):
    """Schema for requirement reference response."""
    id: str
    requirement_id: str
    source: str
    requirement_type: str
    title: str
    relationship: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Dependency schemas
class DependencyCreate(TektonBaseModel):
    """Schema for creating a dependency between tasks."""
    source_task_id: str
    target_task_id: str
    dependency_type: str = "depends_on"
    description: Optional[str] = None


class DependencyUpdate(TektonBaseModel):
    """Schema for updating a dependency."""
    dependency_type: Optional[str] = None
    description: Optional[str] = None


class DependencyResponse(TektonBaseModel):
    """Schema for dependency response."""
    id: str
    source_task_id: str
    target_task_id: str
    dependency_type: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Task schemas
class TaskCreate(TektonBaseModel):
    """Schema for creating a new task."""
    title: str
    description: str
    status: str = TaskStatus.PENDING.value
    priority: str = Priority.MEDIUM.value
    details: Optional[str] = None
    test_strategy: Optional[str] = None
    dependencies: List[str] = []
    tags: List[str] = []
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    subtasks: List[SubtaskCreate] = []
    requirement_refs: List[RequirementRefCreate] = []
    
    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        """Validate that the status is a valid TaskStatus value."""
        if v not in [s.value for s in TaskStatus]:
            raise ValueError(f"Invalid task status: {v}")
        return v
    
    @field_validator("priority")
    @classmethod
    def priority_must_be_valid(cls, v):
        """Validate that the priority is a valid Priority value."""
        if v not in [p.value for p in Priority]:
            raise ValueError(f"Invalid task priority: {v}")
        return v


class TaskUpdate(TektonBaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    details: Optional[str] = None
    test_strategy: Optional[str] = None
    tags: Optional[List[str]] = None
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    
    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        """Validate that the status is a valid TaskStatus value."""
        if v is not None and v not in [s.value for s in TaskStatus]:
            raise ValueError(f"Invalid task status: {v}")
        return v
    
    @field_validator("priority")
    @classmethod
    def priority_must_be_valid(cls, v):
        """Validate that the priority is a valid Priority value."""
        if v is not None and v not in [p.value for p in Priority]:
            raise ValueError(f"Invalid task priority: {v}")
        return v


class TaskResponse(TektonBaseModel):
    """Schema for task response."""
    id: str
    title: str
    description: str
    status: str
    priority: str
    details: Optional[str] = None
    test_strategy: Optional[str] = None
    dependencies: List[str] = []
    tags: List[str] = []
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    subtasks: List[SubtaskResponse] = []
    requirement_refs: List[RequirementRefResponse] = []
    complexity: Optional[ComplexityScoreResponse] = None
    progress: float


class TaskListResponse(ApiResponse):
    """Schema for task list response."""
    tasks: List[TaskResponse] = []
    total: int = 0
    page: int = 1
    page_size: int = 50


class TaskDetailResponse(ApiResponse):
    """Schema for detailed task response."""
    task: TaskResponse


class DependencyListResponse(ApiResponse):
    """Schema for dependency list response."""
    dependencies: List[DependencyResponse] = []


# Query parameters
class TaskQueryParams(TektonBaseModel):
    """Query parameters for filtering tasks."""
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    tag: Optional[str] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 50


# WebSocket message schemas
class WebSocketMessage(TektonBaseModel):
    """Base schema for WebSocket messages."""
    type: str
    data: Dict[str, Any]


class WebSocketRegistration(TektonBaseModel):
    """Schema for WebSocket registration messages."""
    client_id: str = Field(default_factory=lambda: str(uuid4()))
    subscribe_to: List[str] = ["task_created", "task_updated", "task_deleted"]