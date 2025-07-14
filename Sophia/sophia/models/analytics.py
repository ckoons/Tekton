"""
Data models for advanced analytics in Sophia
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PatternDetectionRequest(BaseModel):
    """Request model for pattern detection"""
    component_filter: Optional[str] = Field(
        None,
        description="Filter by component name pattern"
    )
    dimensions: Optional[List[str]] = Field(
        None,
        description="Dimensions to analyze (default: value, timestamp, metric_id)"
    )
    time_window: str = Field(
        "24h",
        description="Time window for analysis (e.g., '24h', '7d')"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "component_filter": "sophia",
                "dimensions": ["value", "timestamp", "metric_id"],
                "time_window": "24h"
            }
        }


class PatternDetectionResponse(BaseModel):
    """Response model for pattern detection"""
    status: str
    patterns: List[Dict[str, Any]]
    analysis_time: datetime
    pattern_count: int


class CausalAnalysisRequest(BaseModel):
    """Request model for causal analysis"""
    target_metric: str = Field(
        ...,
        description="The effect metric to analyze"
    )
    candidate_causes: List[str] = Field(
        ...,
        description="List of potential causal metrics"
    )
    time_window: str = Field(
        "7d",
        description="Time window for analysis"
    )
    max_lag: int = Field(
        10,
        description="Maximum time lag to consider",
        ge=1,
        le=100
    )
    
    class Config:
        schema_extra = {
            "example": {
                "target_metric": "perf.response_time",
                "candidate_causes": ["res.cpu_usage", "res.memory_usage", "api.request_count"],
                "time_window": "7d",
                "max_lag": 10
            }
        }


class CausalAnalysisResponse(BaseModel):
    """Response model for causal analysis"""
    status: str
    target_metric: str
    relationships: List[Dict[str, Any]]
    analysis_time: datetime
    relationship_count: int


class ComplexEventRequest(BaseModel):
    """Request model for complex event detection"""
    event_types: Optional[List[str]] = Field(
        None,
        description="Specific event types to look for"
    )
    time_window: str = Field(
        "24h",
        description="Time window for analysis"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "event_types": ["cascade_failure", "synchronization_event", "emergence_event"],
                "time_window": "24h"
            }
        }


class ComplexEventResponse(BaseModel):
    """Response model for complex event detection"""
    status: str
    events: List[Dict[str, Any]]
    analysis_time: datetime
    event_count: int


class PredictionRequest(BaseModel):
    """Request model for metric predictions"""
    metric_ids: List[str] = Field(
        ...,
        description="List of metric IDs to predict"
    )
    prediction_horizon: int = Field(
        24,
        description="Number of time steps to predict",
        ge=1,
        le=168
    )
    confidence_level: float = Field(
        0.95,
        description="Confidence level for prediction intervals",
        ge=0.5,
        le=0.99
    )
    
    class Config:
        schema_extra = {
            "example": {
                "metric_ids": ["perf.response_time", "res.cpu_usage"],
                "prediction_horizon": 24,
                "confidence_level": 0.95
            }
        }


class PredictionResponse(BaseModel):
    """Response model for metric predictions"""
    status: str
    predictions: Dict[str, Any]
    analysis_time: datetime
    prediction_horizon: int
    confidence_level: float


class NetworkAnalysisRequest(BaseModel):
    """Request model for network analysis"""
    time_window: str = Field(
        "24h",
        description="Time window for analysis"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "time_window": "24h"
            }
        }


class NetworkAnalysisResponse(BaseModel):
    """Response model for network analysis"""
    status: str
    analysis: Dict[str, Any]
    analysis_time: datetime