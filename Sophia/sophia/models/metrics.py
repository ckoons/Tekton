"""
Metrics data models for Sophia API.

This module defines the Pydantic models for metrics-related API requests and responses.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import Field
from tekton.models.base import TektonBaseModel


class MetricSubmission(TektonBaseModel):
    """Model for submitting a new metric."""
    
    metric_id: str = Field(..., description="Unique identifier for the metric type")
    value: Any = Field(..., description="Value of the metric")
    source: Optional[str] = Field(None, description="Source of the metric (e.g., component ID)")
    timestamp: Optional[str] = Field(None, description="ISO timestamp (defaults to current time)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the metric")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the metric")


class MetricQuery(TektonBaseModel):
    """Model for querying metrics."""
    
    metric_id: Optional[str] = Field(None, description="Filter by metric ID")
    source: Optional[str] = Field(None, description="Filter by source")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    start_time: Optional[str] = Field(None, description="Filter by start time (ISO format)")
    end_time: Optional[str] = Field(None, description="Filter by end time (ISO format)")
    limit: int = Field(100, description="Maximum number of results to return")
    offset: int = Field(0, description="Offset for pagination")
    sort: str = Field("timestamp:desc", description="Sorting specification (field:direction)")


class MetricResponse(TektonBaseModel):
    """Model for generic metric operation response."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")


class MetricAggregationQuery(TektonBaseModel):
    """Model for metric aggregation queries."""
    
    metric_id: str = Field(..., description="The metric ID to aggregate")
    aggregation: str = Field("avg", description="Aggregation function (avg, sum, min, max, count, p50, p95, p99)")
    interval: Optional[str] = Field(None, description="Time interval for time-series aggregation (e.g., '1h', '1d')")
    source: Optional[str] = Field(None, description="Filter by source")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    start_time: Optional[str] = Field(None, description="Filter by start time")
    end_time: Optional[str] = Field(None, description="Filter by end time")


class MetricDefinition(TektonBaseModel):
    """Model for metric definitions."""
    
    description: str = Field(..., description="Description of the metric")
    unit: str = Field(..., description="Unit of measurement")
    type: str = Field(..., description="Data type (float, integer, etc.)")
    aggregations: List[str] = Field(..., description="Supported aggregation functions")