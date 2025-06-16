"""
Context data models for Apollo.

This module defines the data models used for context monitoring and management.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import Field
from tekton.models import TektonBaseModel


class ContextHealth(str, Enum):
    """Health status of an LLM context."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class ContextMetrics(TektonBaseModel):
    """Metrics for an LLM context."""
    # Basic token metrics
    input_tokens: int
    output_tokens: int
    total_tokens: int
    max_tokens: int
    token_utilization: float  # percentage of max_tokens used
    
    # Token rate metrics
    input_token_rate: float  # tokens per second
    output_token_rate: float
    token_rate_change: float  # acceleration/deceleration
    
    # Context quality metrics
    repetition_score: float = 0.0  # Higher is worse
    self_reference_score: float = 0.0  # Higher is worse
    coherence_score: float = 1.0  # Higher is better
    
    # Temporal metrics
    latency: float  # seconds
    processing_time: float  # seconds
    timestamp: datetime = Field(default_factory=datetime.now)


class ContextState(TektonBaseModel):
    """State of an LLM context."""
    context_id: str
    component_id: str
    provider: str
    model: str
    task_type: str
    metrics: ContextMetrics
    health: ContextHealth
    health_score: float  # 0.0 to 1.0
    creation_time: datetime
    last_updated: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContextHistoryRecord(TektonBaseModel):
    """Historical record of context metrics."""
    context_id: str
    metrics: ContextMetrics
    health: ContextHealth
    health_score: float
    timestamp: datetime = Field(default_factory=datetime.now)


class ContextPrediction(TektonBaseModel):
    """Prediction for future context state."""
    context_id: str
    predicted_metrics: ContextMetrics
    predicted_health: ContextHealth
    predicted_health_score: float
    confidence: float  # 0.0 to 1.0
    prediction_timestamp: datetime = Field(default_factory=datetime.now)
    prediction_horizon: float  # seconds into the future
    basis: str  # heuristic, statistical, hybrid


class ContextAction(TektonBaseModel):
    """Action to take on a context."""
    context_id: str
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str  # refresh, compress, reset, etc.
    priority: int  # 0-10, higher is more important
    reason: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    suggested_time: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)