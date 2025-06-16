"""
Workflow data models for Harmonia.

This module defines the Pydantic data models for workflow definitions,
including workflows, tasks, dependencies, and related entities.
"""

from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import Field, field_validator
from tekton.models import TektonBaseModel


class TaskType(str, Enum):
    """Types of tasks that can be executed in a workflow."""
    
    STANDARD = "standard"
    DECISION = "decision"
    PARALLEL = "parallel"
    JOIN = "join"
    LOOP = "loop"
    MAP = "map"
    EVENT = "event"
    WAIT = "wait"
    WEBHOOK = "webhook"
    CUSTOM = "custom"


class TaskStatus(str, Enum):
    """Status of a task execution."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELED = "canceled"
    WAITING = "waiting"


class WorkflowStatus(str, Enum):
    """Status of a workflow execution."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELED = "canceled"


class RetryPolicy(TektonBaseModel):
    """Configuration for automatic retries."""
    
    max_retries: int = Field(3, description="Maximum number of retry attempts")
    initial_delay: float = Field(1.0, description="Initial delay in seconds before first retry")
    max_delay: float = Field(60.0, description="Maximum delay in seconds between retries")
    backoff_multiplier: float = Field(2.0, description="Multiplier for exponential backoff")
    retry_on: List[str] = Field(default_factory=list, description="List of error types to retry on")
    
    @field_validator("max_retries")
    def validate_max_retries(cls, v):
        """Validate max_retries is non-negative."""
        if v < 0:
            raise ValueError("max_retries must be non-negative")
        return v
    
    @field_validator("initial_delay", "max_delay", "backoff_multiplier")
    def validate_positive(cls, v, info):
        """Validate numeric fields are positive."""
        if v <= 0:
            raise ValueError(f"{info.field_name} must be positive")
        return v


class TaskDefinition(TektonBaseModel):
    """Definition of a task in a workflow."""
    
    id: str = Field(..., description="Unique identifier for the task")
    name: str = Field(..., description="Human-readable name for the task")
    type: TaskType = Field(TaskType.STANDARD, description="Type of the task")
    component: str = Field(..., description="Component that will execute this task")
    action: str = Field(..., description="Action to perform on the component")
    input: Dict[str, Any] = Field(default_factory=dict, description="Input parameters for the task")
    depends_on: List[str] = Field(default_factory=list, description="Tasks that must complete before this task")
    retry_policy: Optional[RetryPolicy] = Field(None, description="Retry policy for this task")
    timeout: Optional[int] = Field(None, description="Timeout in seconds for this task")
    description: Optional[str] = Field(None, description="Description of the task")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the task")
    
    @field_validator("id")
    def validate_id(cls, v):
        """Validate task ID format."""
        if not v or not v.strip():
            raise ValueError("Task ID cannot be empty")
        if " " in v:
            raise ValueError("Task ID cannot contain spaces")
        return v


class WorkflowDefinition(TektonBaseModel):
    """Definition of a workflow."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the workflow")
    name: str = Field(..., description="Human-readable name for the workflow")
    version: str = Field("1.0.0", description="Version of the workflow definition")
    description: Optional[str] = Field(None, description="Description of the workflow")
    tasks: Dict[str, TaskDefinition] = Field(..., description="Tasks in the workflow")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for workflow input")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for workflow output")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the workflow")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing workflows")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class TaskExecution(TektonBaseModel):
    """Execution state of a task."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the task execution")
    task_id: str = Field(..., description="ID of the task being executed")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Current status of the task")
    start_time: Optional[datetime] = Field(None, description="Time when the task started executing")
    end_time: Optional[datetime] = Field(None, description="Time when the task finished executing")
    input: Dict[str, Any] = Field(default_factory=dict, description="Resolved input for the task")
    output: Dict[str, Any] = Field(default_factory=dict, description="Output of the task execution")
    error: Optional[str] = Field(None, description="Error message if task failed")
    retries: int = Field(0, description="Number of retry attempts made")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the execution")


class WorkflowExecution(TektonBaseModel):
    """Execution state of a workflow."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the workflow execution")
    workflow_id: UUID = Field(..., description="ID of the workflow being executed")
    status: WorkflowStatus = Field(WorkflowStatus.PENDING, description="Current status of the workflow")
    start_time: datetime = Field(default_factory=datetime.now, description="Time when the workflow started executing")
    end_time: Optional[datetime] = Field(None, description="Time when the workflow finished executing")
    input: Dict[str, Any] = Field(default_factory=dict, description="Input provided to the workflow")
    output: Dict[str, Any] = Field(default_factory=dict, description="Output produced by the workflow")
    task_executions: Dict[str, TaskExecution] = Field(default_factory=dict, description="Executions of tasks in the workflow")
    error: Optional[str] = Field(None, description="Error message if workflow failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the execution")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class WorkflowTemplate(TektonBaseModel):
    """Template for creating workflow definitions."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the template")
    name: str = Field(..., description="Human-readable name for the template")
    description: Optional[str] = Field(None, description="Description of the template")
    version: str = Field("1.0.0", description="Version of the template")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for customizing the template")
    workflow_definition: WorkflowDefinition = Field(..., description="Base workflow definition")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing templates")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class Webhook(TektonBaseModel):
    """Webhook configuration for triggering workflows."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the webhook")
    name: str = Field(..., description="Human-readable name for the webhook")
    description: Optional[str] = Field(None, description="Description of the webhook")
    url_path: str = Field(..., description="URL path for the webhook")
    workflow_id: UUID = Field(..., description="ID of the workflow to trigger")
    input_mapping: Dict[str, str] = Field(default_factory=dict, description="Mapping from webhook payload to workflow input")
    secret: Optional[str] = Field(None, description="Secret for validating webhook requests")
    enabled: bool = Field(True, description="Whether the webhook is enabled")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the webhook")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")