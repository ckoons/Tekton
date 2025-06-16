"""
Shared API Models

This module defines the shared API models for the Prometheus/Epimethius Planning System.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from pydantic import Field
from tekton.models.base import TektonBaseModel


class TrackingUpdate(TektonBaseModel):
    """Schema for tracking update."""
    plan_id: str = Field(..., description="ID of the plan")
    task_updates: Optional[Dict[str, float]] = Field(None, description="Task progress updates")
    milestone_updates: Optional[Dict[str, str]] = Field(None, description="Milestone status updates")
    issues: Optional[List[Dict[str, Any]]] = Field(None, description="Issues encountered")
    notes: Optional[str] = Field(None, description="Notes on the update")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of the update")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TrackingRequest(TektonBaseModel):
    """Schema for tracking data request."""
    plan_id: str = Field(..., description="ID of the plan")
    include_tasks: Optional[bool] = Field(True, description="Whether to include tasks")
    include_milestones: Optional[bool] = Field(True, description="Whether to include milestones")
    include_issues: Optional[bool] = Field(True, description="Whether to include issues")
    include_history: Optional[bool] = Field(False, description="Whether to include history")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class BurndownRequest(TektonBaseModel):
    """Schema for burndown chart data request."""
    plan_id: str = Field(..., description="ID of the plan")
    chart_type: str = Field("burndown", description="Type of chart", 
                          pattern="^(burndown|burnup|custom)$")
    scope: Optional[str] = Field("all", description="Scope of the chart", 
                               pattern="^(all|tasks|effort|custom)$")
    time_scale: Optional[str] = Field("daily", description="Time scale for the chart", 
                                    pattern="^(daily|weekly|monthly|custom)$")
    include_ideal: Optional[bool] = Field(True, description="Whether to include ideal line")
    include_forecast: Optional[bool] = Field(False, description="Whether to include forecast")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TrackingMetricsRequest(TektonBaseModel):
    """Schema for tracking metrics request."""
    plan_id: str = Field(..., description="ID of the plan")
    metrics: List[str] = Field(..., description="Metrics to include")
    time_range: Optional[Dict[str, Any]] = Field(None, description="Time range for the metrics")
    group_by: Optional[str] = Field(None, description="Group by dimension", 
                                   pattern="^(task|resource|milestone|custom)$")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class LLMAnalysisRequest(TektonBaseModel):
    """Schema for LLM analysis request."""
    content: str = Field(..., description="Content to analyze")
    analysis_type: str = Field(..., description="Type of analysis")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for the response")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class LLMRiskAnalysisRequest(TektonBaseModel):
    """Schema for LLM risk analysis request."""
    plan_id: str = Field(..., description="ID of the plan")
    include_history: Optional[bool] = Field(True, description="Whether to include historical data")
    risk_types: Optional[List[str]] = Field(None, description="Types of risks to analyze")
    max_risks: Optional[int] = Field(5, description="Maximum number of risks to identify", ge=1)
    include_mitigations: Optional[bool] = Field(True, description="Whether to include mitigations")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class StandardResponse(TektonBaseModel):
    """Standard response model."""
    status: str = Field(..., description="Status of the response")
    message: str = Field(..., description="Message describing the response")
    data: Optional[Any] = Field(None, description="Response data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PaginatedResponse(TektonBaseModel):
    """Paginated response model."""
    status: str = Field(..., description="Status of the response")
    message: str = Field(..., description="Message describing the response")
    data: List[Any] = Field(..., description="Response data")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ErrorResponse(TektonBaseModel):
    """Error response model."""
    status: str = Field("error", description="Status of the response")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Any] = Field(None, description="Error details")


class SearchRequest(TektonBaseModel):
    """Search request model."""
    query: str = Field(..., description="Search query")
    entity_types: Optional[List[str]] = Field(None, description="Types of entities to search")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    page: Optional[int] = Field(1, description="Page number", ge=1)
    page_size: Optional[int] = Field(20, description="Page size", ge=1, le=100)
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("asc", description="Sort order", pattern="^(asc|desc)$")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")