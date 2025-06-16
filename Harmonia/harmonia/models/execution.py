"""
Execution models for Harmonia.

This module defines the data models for workflow execution,
including execution history, metrics, and event handling.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import Field, validator
from tekton.models import TektonBaseModel

from harmonia.models.workflow import WorkflowStatus, TaskStatus


class EventType(str, Enum):
    """Types of events in workflow execution."""
    
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_PAUSED = "workflow_paused"
    WORKFLOW_RESUMED = "workflow_resumed"
    WORKFLOW_CANCELED = "workflow_canceled"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_SKIPPED = "task_skipped"
    CHECKPOINT_CREATED = "checkpoint_created"
    RETRY_ATTEMPTED = "retry_attempted"
    TIMEOUT_OCCURRED = "timeout_occurred"
    STATE_CHANGED = "state_changed"
    ERROR_OCCURRED = "error_occurred"
    WEBHOOK_RECEIVED = "webhook_received"
    CUSTOM = "custom"


class ExecutionEvent(TektonBaseModel):
    """Event that occurred during workflow execution."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the event")
    execution_id: UUID = Field(..., description="ID of the workflow execution")
    timestamp: datetime = Field(default_factory=datetime.now, description="Time when the event occurred")
    event_type: EventType = Field(..., description="Type of the event")
    task_id: Optional[str] = Field(None, description="ID of the task (if event is task-related)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details about the event")
    message: Optional[str] = Field(None, description="Human-readable message about the event")


class ExecutionMetrics(TektonBaseModel):
    """Metrics collected during workflow execution."""
    
    execution_id: UUID = Field(..., description="ID of the workflow execution")
    total_duration: timedelta = Field(..., description="Total execution time")
    task_durations: Dict[str, timedelta] = Field(default_factory=dict, description="Duration of each task")
    task_wait_times: Dict[str, timedelta] = Field(default_factory=dict, description="Wait time for each task")
    retry_counts: Dict[str, int] = Field(default_factory=dict, description="Number of retries for each task")
    error_counts: Dict[str, int] = Field(default_factory=dict, description="Number of errors for each task")
    resource_usage: Dict[str, Any] = Field(default_factory=dict, description="Resource usage metrics")
    data_metrics: Dict[str, Any] = Field(default_factory=dict, description="Data-related metrics")
    checkpoint_count: int = Field(0, description="Number of checkpoints created")
    average_task_duration: Optional[float] = Field(None, description="Average task duration in seconds")
    
    @property
    def total_duration_seconds(self) -> float:
        """Get the total duration in seconds."""
        return self.total_duration.total_seconds()
    
    @property
    def critical_path(self) -> List[str]:
        """Get the critical path (tasks that determined the total duration)."""
        # Simple heuristic based on task durations
        # In a real implementation, this would analyze the actual execution path
        sorted_tasks = sorted(
            self.task_durations.items(),
            key=lambda x: x[1].total_seconds(),
            reverse=True
        )
        return [task_id for task_id, _ in sorted_tasks[:5]]


class Checkpoint(TektonBaseModel):
    """Checkpoint of workflow execution state."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the checkpoint")
    execution_id: UUID = Field(..., description="ID of the workflow execution")
    timestamp: datetime = Field(default_factory=datetime.now, description="Time when the checkpoint was created")
    workflow_status: WorkflowStatus = Field(..., description="Status of the workflow")
    task_statuses: Dict[str, TaskStatus] = Field(default_factory=dict, description="Status of each task")
    completed_tasks: List[str] = Field(default_factory=list, description="IDs of completed tasks")
    state_data: Dict[str, Any] = Field(..., description="Saved state data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    description: Optional[str] = Field(None, description="Description of the checkpoint")


class ExecutionHistory(TektonBaseModel):
    """History of a workflow execution."""
    
    execution_id: UUID = Field(..., description="ID of the workflow execution")
    events: List[ExecutionEvent] = Field(default_factory=list, description="Events that occurred during execution")
    checkpoints: List[Checkpoint] = Field(default_factory=list, description="Checkpoints created during execution")
    metrics: Optional[ExecutionMetrics] = Field(None, description="Metrics collected during execution")
    
    def add_event(self, event: ExecutionEvent) -> None:
        """Add an event to the history."""
        self.events.append(event)
    
    def add_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Add a checkpoint to the history."""
        self.checkpoints.append(checkpoint)
    
    def get_latest_checkpoint(self) -> Optional[Checkpoint]:
        """Get the most recent checkpoint."""
        if not self.checkpoints:
            return None
        return max(self.checkpoints, key=lambda c: c.timestamp)
    
    def get_events_by_type(self, event_type: EventType) -> List[ExecutionEvent]:
        """Get all events of a specific type."""
        return [event for event in self.events if event.event_type == event_type]
    
    def get_events_for_task(self, task_id: str) -> List[ExecutionEvent]:
        """Get all events related to a specific task."""
        return [event for event in self.events if event.task_id == task_id]


class ExecutionSummary(TektonBaseModel):
    """Summary of a workflow execution."""
    
    id: UUID = Field(..., description="ID of the workflow execution")
    workflow_id: UUID = Field(..., description="ID of the workflow")
    workflow_name: str = Field(..., description="Name of the workflow")
    status: WorkflowStatus = Field(..., description="Current status of the execution")
    start_time: datetime = Field(..., description="Time when the execution started")
    end_time: Optional[datetime] = Field(None, description="Time when the execution ended")
    duration: Optional[timedelta] = Field(None, description="Total duration of the execution")
    task_count: int = Field(0, description="Total number of tasks in the workflow")
    completed_tasks: int = Field(0, description="Number of completed tasks")
    failed_tasks: int = Field(0, description="Number of failed tasks")
    has_error: bool = Field(False, description="Whether the execution has an error")
    error_message: Optional[str] = Field(None, description="Error message if execution failed")
    
    @property
    def completion_percentage(self) -> float:
        """Calculate the percentage of completed tasks."""
        if self.task_count == 0:
            return 0.0
        return (self.completed_tasks / self.task_count) * 100.0
    
    @property
    def is_complete(self) -> bool:
        """Check if the execution is complete."""
        return self.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELED]