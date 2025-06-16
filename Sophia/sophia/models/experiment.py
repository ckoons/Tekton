"""
Experiment data models for Sophia API.

This module defines the Pydantic models for experiment-related API requests and responses.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import Field
from tekton.models.base import TektonBaseModel


class ExperimentStatus(str, Enum):
    """Status of an experiment."""
    
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"


class ExperimentType(str, Enum):
    """Type of experiment."""
    
    A_B_TEST = "a_b_test"
    MULTIVARIATE = "multivariate"
    SHADOW_MODE = "shadow_mode"
    CANARY = "canary"
    PARAMETER_TUNING = "parameter_tuning"
    BEFORE_AFTER = "before_after"
    BASELINE_COMPARISON = "baseline_comparison"


class ExperimentCreate(TektonBaseModel):
    """Model for creating a new experiment."""
    
    name: str = Field(..., description="Name of the experiment")
    description: str = Field(..., description="Description of the experiment")
    experiment_type: ExperimentType = Field(..., description="Type of experiment")
    target_components: List[str] = Field(..., description="List of components involved in the experiment")
    hypothesis: str = Field(..., description="Hypothesis being tested")
    metrics: List[str] = Field(..., description="List of metrics to be tracked")
    parameters: Dict[str, Any] = Field(..., description="Parameters for the experiment")
    start_time: Optional[str] = Field(None, description="Scheduled start time (ISO format)")
    end_time: Optional[str] = Field(None, description="Scheduled end time (ISO format)")
    sample_size: Optional[int] = Field(None, description="Target sample size")
    min_confidence: Optional[float] = Field(None, description="Minimum confidence level required")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the experiment")


class ExperimentUpdate(TektonBaseModel):
    """Model for updating an experiment."""
    
    name: Optional[str] = Field(None, description="Name of the experiment")
    description: Optional[str] = Field(None, description="Description of the experiment")
    status: Optional[ExperimentStatus] = Field(None, description="Status of the experiment")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for the experiment")
    start_time: Optional[str] = Field(None, description="Scheduled start time (ISO format)")
    end_time: Optional[str] = Field(None, description="Scheduled end time (ISO format)")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the experiment")


class ExperimentQuery(TektonBaseModel):
    """Model for querying experiments."""
    
    status: Optional[ExperimentStatus] = Field(None, description="Filter by status")
    experiment_type: Optional[ExperimentType] = Field(None, description="Filter by experiment type")
    target_components: Optional[List[str]] = Field(None, description="Filter by target components")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    start_after: Optional[str] = Field(None, description="Filter by start time after (ISO format)")
    start_before: Optional[str] = Field(None, description="Filter by start time before (ISO format)")
    limit: int = Field(100, description="Maximum number of results to return")
    offset: int = Field(0, description="Offset for pagination")


class ExperimentResponse(TektonBaseModel):
    """Model for generic experiment operation response."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")


class ExperimentResult(TektonBaseModel):
    """Model for experiment results."""
    
    experiment_id: str = Field(..., description="ID of the experiment")
    status: ExperimentStatus = Field(..., description="Status of the experiment")
    metrics_summary: Dict[str, Dict[str, Any]] = Field(..., description="Summary of metrics collected")
    confidence_level: Optional[float] = Field(None, description="Confidence level of the results")
    conclusion: Optional[str] = Field(None, description="Conclusion from the experiment")
    recommended_action: Optional[str] = Field(None, description="Recommended action based on results")
    insights: Optional[List[str]] = Field(None, description="Insights derived from the results")
    raw_data_reference: Optional[str] = Field(None, description="Reference to raw data location")