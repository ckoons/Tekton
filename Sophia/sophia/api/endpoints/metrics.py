"""
Metrics API endpoints for Sophia.

This module defines the API endpoints for metrics collection and analysis in Sophia.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from datetime import datetime

from sophia.core.metrics_engine import get_metrics_engine
from sophia.models.metrics import (
    MetricSubmission,
    MetricQuery,
    MetricResponse,
    MetricAggregationQuery,
    MetricDefinition
)

# Create router
router = APIRouter()

# ------------------------
# Metrics API Routes
# ------------------------

@router.post("/explain", response_model=Dict[str, Any])
async def explain_metrics(
    metrics_data: Dict[str, Any] = Body(..., description="Metrics data to explain"),
    audience: str = Query("technical", description="Target audience: technical, executive, or general")
):
    """
    Generate natural language explanation of metrics data.
    Translates technical metrics into clear, accessible explanations.
    """
    try:
        # TODO: Replace with Rhetor client
        explanation = "LLM explanation not available - needs Rhetor integration"
        return {
            "explanation": explanation,
            "metrics": metrics_data,
            "audience": audience
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to explain metrics: {str(e)}"
        )

@router.post("/", response_model=MetricResponse)
async def submit_metric(
    submission: MetricSubmission,
    metrics_engine = Depends(get_metrics_engine)
):
    """Submit a new metric."""
    try:
        result = await metrics_engine.record_metric(
            metric_id=submission.metric_id,
            value=submission.value,
            source=submission.source,
            timestamp=submission.timestamp,
            context=submission.context,
            tags=submission.tags
        )
        
        if result:
            return MetricResponse(
                success=True,
                message="Metric recorded successfully"
            )
        else:
            return MetricResponse(
                success=False,
                message="Failed to record metric"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record metric: {str(e)}"
        )

@router.get("/", response_model=List[Dict[str, Any]])
async def query_metrics(
    metric_id: Optional[str] = None,
    source: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated list of tags"),
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    sort: str = "timestamp:desc",
    metrics_engine = Depends(get_metrics_engine)
):
    """Query metrics with filtering."""
    try:
        # Parse tags from comma-separated string if provided
        tag_list = tags.split(",") if tags else None
        
        # Create query object
        query = MetricQuery(
            metric_id=metric_id,
            source=source,
            tags=tag_list,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
            sort=sort
        )
        
        # Execute query
        metrics = await metrics_engine.query_metrics(query)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query metrics: {str(e)}"
        )

@router.post("/aggregate", response_model=Dict[str, Any])
async def aggregate_metrics(
    aggregation_query: MetricAggregationQuery,
    metrics_engine = Depends(get_metrics_engine)
):
    """Aggregate metrics for analysis."""
    try:
        result = await metrics_engine.aggregate_metrics(aggregation_query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to aggregate metrics: {str(e)}"
        )

@router.get("/available", response_model=Dict[str, Dict[str, Any]])
async def get_available_metrics(
    metrics_engine = Depends(get_metrics_engine)
):
    """Get all available metric definitions."""
    try:
        return metrics_engine.get_available_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available metrics: {str(e)}"
        )

@router.get("/{metric_id}/definition", response_model=MetricDefinition)
async def get_metric_definition(
    metric_id: str = Path(..., description="ID of the metric"),
    metrics_engine = Depends(get_metrics_engine)
):
    """Get definition for a specific metric."""
    try:
        definition = metrics_engine.get_metric_definition(metric_id)
        if definition:
            return definition
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Metric definition not found: {metric_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metric definition: {str(e)}"
        )

@router.post("/{metric_id}/definition", response_model=MetricResponse)
async def register_metric_definition(
    definition: MetricDefinition,
    metric_id: str = Path(..., description="ID of the metric"),
    metrics_engine = Depends(get_metrics_engine)
):
    """Register a new metric definition."""
    try:
        if definition.metric_id != metric_id:
            raise HTTPException(
                status_code=400,
                detail="Metric ID in path and body must match"
            )
        
        success = await metrics_engine.register_metric_definition(definition)
        
        if success:
            return MetricResponse(
                success=True,
                message=f"Metric definition registered successfully: {metric_id}"
            )
        else:
            return MetricResponse(
                success=False,
                message="Failed to register metric definition"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register metric definition: {str(e)}"
        )