"""
API data models for Apollo.

This module defines the Pydantic models used for the Apollo API.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pydantic import Field, field_validator
from enum import Enum
from tekton.models import TektonBaseModel


class ResponseStatus(str, Enum):
    """Response status values."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class APIResponse(TektonBaseModel):
    """Base API response model."""
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[List[str]] = None


class MonitoringStatus(str, Enum):
    """Monitoring status values."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class MonitoringMetrics(TektonBaseModel):
    """Metrics for context monitoring."""
    status: MonitoringStatus
    token_usage: Dict[str, Any]
    token_limit: int
    token_percentage: float
    context_size: int
    context_health: float
    last_updated: datetime


class SessionInfo(TektonBaseModel):
    """LLM session information."""
    session_id: str
    component: str
    model: str
    provider: str
    metrics: MonitoringMetrics
    predictions: Optional[Dict[str, Any]] = None
    last_action: Optional[Dict[str, Any]] = None


class BudgetRequest(TektonBaseModel):
    """Budget allocation request."""
    context_id: str
    task_type: str = "default"
    component: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    priority: int = Field(0, ge=0, le=10)
    token_count: Optional[int] = None


class BudgetResponse(TektonBaseModel):
    """Budget allocation response."""
    context_id: str
    allocated_tokens: int
    expiration: datetime
    policy: Dict[str, Any]


class ProtocolRule(TektonBaseModel):
    """Protocol rule definition."""
    rule_id: str
    name: str
    description: Optional[str] = None
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int = Field(0, ge=0, le=10)
    target_components: List[str]


class DirectiveMessage(TektonBaseModel):
    """Directive message for components."""
    directive_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    directive_type: str
    target_component: str
    content: Dict[str, Any]
    priority: int = Field(0, ge=0, le=10)
    expiration: Optional[datetime] = None


class ComponentMessage(TektonBaseModel):
    """Message from a component to Apollo."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    component: str
    message_type: str
    content: Dict[str, Any]
    requires_response: bool = False


class PredictionRequest(TektonBaseModel):
    """Request for context prediction."""
    context_id: str
    component: str
    current_metrics: Dict[str, Any]
    history_length: int = 10
    prediction_horizon: int = 3