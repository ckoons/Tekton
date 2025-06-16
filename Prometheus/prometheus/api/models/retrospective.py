"""
Epimethius Retrospective API Models

This module defines the API models for the Epimethius retrospective endpoints.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from pydantic import Field
from tekton.models.base import TektonBaseModel


class RetroItemCreate(TektonBaseModel):
    """Schema for retrospective item creation."""
    content: str = Field(..., description="Content of the item", min_length=1)
    category: str = Field(..., description="Category of the item")
    author: Optional[str] = Field(None, description="Author of the item")
    related_task_ids: Optional[List[str]] = Field(None, description="IDs of related tasks")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class RetroItemUpdate(TektonBaseModel):
    """Schema for retrospective item update."""
    content: Optional[str] = Field(None, description="Content of the item", min_length=1)
    category: Optional[str] = Field(None, description="Category of the item")
    votes: Optional[int] = Field(None, description="Number of votes", ge=0)
    related_task_ids: Optional[List[str]] = Field(None, description="IDs of related tasks")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ActionItemCreate(TektonBaseModel):
    """Schema for action item creation."""
    title: str = Field(..., description="Title of the action item", min_length=1)
    description: str = Field(..., description="Description of the action item", min_length=1)
    assignees: Optional[List[str]] = Field(None, description="Assignees of the action item")
    due_date: Optional[datetime] = Field(None, description="Due date of the action item")
    priority: str = Field("medium", description="Priority of the action item", 
                         pattern="^(low|medium|high|critical)$")
    related_retro_items: Optional[List[str]] = Field(None, description="IDs of related retro items")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ActionItemUpdate(TektonBaseModel):
    """Schema for action item update."""
    title: Optional[str] = Field(None, description="Title of the action item", min_length=1)
    description: Optional[str] = Field(None, description="Description of the action item", min_length=1)
    status: Optional[str] = Field(None, description="Status of the action item",
                                 pattern="^(open|in_progress|completed|cancelled)$")
    assignees: Optional[List[str]] = Field(None, description="Assignees of the action item")
    due_date: Optional[datetime] = Field(None, description="Due date of the action item")
    priority: Optional[str] = Field(None, description="Priority of the action item", 
                                   pattern="^(low|medium|high|critical)$")
    related_retro_items: Optional[List[str]] = Field(None, description="IDs of related retro items")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class RetrospectiveCreate(TektonBaseModel):
    """Schema for retrospective creation."""
    plan_id: str = Field(..., description="ID of the plan")
    name: str = Field(..., description="Name of the retrospective", min_length=1)
    format: str = Field(..., description="Format of the retrospective", 
                       pattern="^(start_stop_continue|4_ls|mad_sad_glad|sailboat|custom)$")
    facilitator: str = Field(..., description="Facilitator of the retrospective")
    date: Optional[datetime] = Field(None, description="Date of the retrospective")
    participants: Optional[List[str]] = Field(None, description="Participants of the retrospective")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class RetrospectiveUpdate(TektonBaseModel):
    """Schema for retrospective update."""
    name: Optional[str] = Field(None, description="Name of the retrospective", min_length=1)
    format: Optional[str] = Field(None, description="Format of the retrospective", 
                                 pattern="^(start_stop_continue|4_ls|mad_sad_glad|sailboat|custom)$")
    facilitator: Optional[str] = Field(None, description="Facilitator of the retrospective")
    date: Optional[datetime] = Field(None, description="Date of the retrospective")
    participants: Optional[List[str]] = Field(None, description="Participants of the retrospective")
    status: Optional[str] = Field(None, description="Status of the retrospective", 
                                 pattern="^(draft|in_progress|completed)$")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ExecutionIssueCreate(TektonBaseModel):
    """Schema for execution issue creation."""
    title: str = Field(..., description="Title of the issue", min_length=1)
    description: str = Field(..., description="Description of the issue", min_length=1)
    severity: str = Field(..., description="Severity of the issue", 
                         pattern="^(low|medium|high|critical)$")
    related_task_ids: Optional[List[str]] = Field(None, description="IDs of related tasks")
    reported_by: Optional[str] = Field(None, description="Reporter of the issue")
    reported_date: Optional[datetime] = Field(None, description="Reporting date of the issue")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ExecutionIssueUpdate(TektonBaseModel):
    """Schema for execution issue update."""
    title: Optional[str] = Field(None, description="Title of the issue", min_length=1)
    description: Optional[str] = Field(None, description="Description of the issue", min_length=1)
    severity: Optional[str] = Field(None, description="Severity of the issue", 
                                   pattern="^(low|medium|high|critical)$")
    status: Optional[str] = Field(None, description="Status of the issue", 
                                 pattern="^(open|resolved|mitigated)$")
    resolution: Optional[str] = Field(None, description="Resolution of the issue")
    related_task_ids: Optional[List[str]] = Field(None, description="IDs of related tasks")
    resolved_date: Optional[datetime] = Field(None, description="Resolution date of the issue")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TaskExecutionUpdate(TektonBaseModel):
    """Schema for task execution update."""
    task_id: str = Field(..., description="ID of the task")
    status: Optional[str] = Field(None, description="Status of the task", 
                                 pattern="^(not_started|in_progress|completed|blocked|cancelled)$")
    progress: Optional[float] = Field(None, description="Progress of the task", ge=0, le=1)
    actual_start_date: Optional[datetime] = Field(None, description="Actual start date")
    actual_end_date: Optional[datetime] = Field(None, description="Actual end date")
    actual_effort: Optional[float] = Field(None, description="Actual effort", ge=0)
    assigned_resources: Optional[List[str]] = Field(None, description="IDs of assigned resources")
    blockers: Optional[List[str]] = Field(None, description="IDs of blocker issues")
    notes: Optional[str] = Field(None, description="Notes on the execution")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MilestoneExecutionUpdate(TektonBaseModel):
    """Schema for milestone execution update."""
    milestone_id: str = Field(..., description="ID of the milestone")
    status: Optional[str] = Field(None, description="Status of the milestone", 
                                 pattern="^(not_started|in_progress|completed|missed)$")
    actual_date: Optional[datetime] = Field(None, description="Actual date of milestone achievement")
    notes: Optional[str] = Field(None, description="Notes on the execution")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ExecutionRecordCreate(TektonBaseModel):
    """Schema for execution record creation."""
    plan_id: str = Field(..., description="ID of the plan")
    record_date: Optional[datetime] = Field(None, description="Date of the record")
    task_records: Optional[Dict[str, Any]] = Field(None, description="Task execution records")
    milestone_records: Optional[Dict[str, Any]] = Field(None, description="Milestone execution records")
    issues_encountered: Optional[List[ExecutionIssueCreate]] = Field(None, description="Issues encountered")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ExecutionRecordUpdate(TektonBaseModel):
    """Schema for execution record update."""
    task_updates: Optional[List[TaskExecutionUpdate]] = Field(None, description="Task execution updates")
    milestone_updates: Optional[List[MilestoneExecutionUpdate]] = Field(None, description="Milestone execution updates")
    new_issues: Optional[List[ExecutionIssueCreate]] = Field(None, description="New issues encountered")
    issue_updates: Optional[List[ExecutionIssueUpdate]] = Field(None, description="Updates to existing issues")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class VarianceAnalysisRequest(TektonBaseModel):
    """Schema for variance analysis request."""
    plan_id: str = Field(..., description="ID of the plan")
    execution_record_id: Optional[str] = Field(None, description="ID of the execution record")
    metrics: Optional[List[str]] = Field(None, description="Metrics to include in the analysis")
    analysis_level: Optional[str] = Field("detailed", description="Level of analysis", 
                                        pattern="^(summary|detailed|comprehensive)$")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PerformanceMetricCreate(TektonBaseModel):
    """Schema for performance metric creation."""
    name: str = Field(..., description="Name of the metric", min_length=1)
    description: str = Field(..., description="Description of the metric", min_length=1)
    value: Any = Field(..., description="Value of the metric")
    metric_type: str = Field(..., description="Type of the metric")
    unit: Optional[str] = Field(None, description="Unit of the metric")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of the metric")
    context: Optional[Dict[str, Any]] = Field(None, description="Context of the metric")
    source: Optional[str] = Field(None, description="Source of the metric")
    source_id: Optional[str] = Field(None, description="ID of the source")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PerformanceAnalysisRequest(TektonBaseModel):
    """Schema for performance analysis request."""
    plan_id: str = Field(..., description="ID of the plan")
    analysis_type: str = Field(..., description="Type of analysis", 
                             pattern="^(velocity|bottleneck|trend|comparison|custom)$")
    metrics: Optional[List[str]] = Field(None, description="IDs of metrics to include")
    series: Optional[List[str]] = Field(None, description="IDs of metric series to include")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for the analysis")
    include_recommendations: Optional[bool] = Field(True, description="Whether to include recommendations")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TeamPerformanceRequest(TektonBaseModel):
    """Schema for team performance analysis request."""
    team_id: str = Field(..., description="ID of the team")
    time_range: Optional[Dict[str, Any]] = Field(None, description="Time range for the analysis")
    metrics: Optional[List[str]] = Field(None, description="Metrics to include in the analysis")
    include_plans: Optional[List[str]] = Field(None, description="Plan IDs to include in the analysis")
    exclude_plans: Optional[List[str]] = Field(None, description="Plan IDs to exclude from the analysis")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TrendAnalysisRequest(TektonBaseModel):
    """Schema for trend analysis request."""
    metric_types: List[str] = Field(..., description="Types of metrics to analyze")
    time_range: Dict[str, Any] = Field(..., description="Time range for the analysis")
    group_by: Optional[str] = Field(None, description="Group by dimension", 
                                   pattern="^(team|project|plan|task_type|resource_type|custom)$")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters for the analysis")
    comparison: Optional[Dict[str, Any]] = Field(None, description="Comparison parameters")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class BottleneckAnalysisRequest(TektonBaseModel):
    """Schema for bottleneck analysis request."""
    plan_id: str = Field(..., description="ID of the plan")
    analysis_scope: Optional[str] = Field("all", description="Scope of the analysis", 
                                        pattern="^(all|timeline|resources|tasks|custom)$")
    threshold: Optional[float] = Field(0.8, description="Threshold for bottleneck detection", ge=0, le=1)
    include_recommendations: Optional[bool] = Field(True, description="Whether to include recommendations")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class LLMRetrospectiveAnalysis(TektonBaseModel):
    """Schema for LLM-based retrospective analysis."""
    retrospective_id: str = Field(..., description="ID of the retrospective to analyze")
    analysis_type: str = Field(
        ..., 
        description="Type of analysis", 
        pattern="^(patterns|root_cause|improvement|comparison|custom)$"
    )
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for analysis")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for the response")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")