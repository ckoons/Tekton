"""
Component data models for Sophia API.

This module defines the Pydantic models for component-related API requests and responses.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import Field
from tekton.models.base import TektonBaseModel


class ComponentType(str, Enum):
    """Type of Tekton component."""
    
    CORE = "core"
    API = "api"
    UI = "ui"
    INTEGRATION = "integration"
    UTILITY = "utility"
    SERVICE = "service"


class PerformanceCategory(str, Enum):
    """Performance categorization of a component."""
    
    EXCELLENT = "excellent"
    GOOD = "good"
    ADEQUATE = "adequate"
    UNDERPERFORMING = "underperforming"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentRegister(TektonBaseModel):
    """Model for registering a component with Sophia."""
    
    component_id: str = Field(..., description="Unique identifier for the component")
    name: str = Field(..., description="Human-readable name of the component")
    description: str = Field(..., description="Description of the component's purpose")
    component_type: ComponentType = Field(..., description="Type of component")
    version: str = Field(..., description="Version of the component")
    api_endpoints: Optional[List[str]] = Field(None, description="List of API endpoints provided by the component")
    capabilities: Optional[List[str]] = Field(None, description="List of capabilities provided by the component")
    dependencies: Optional[List[str]] = Field(None, description="List of dependencies required by the component")
    metrics_provided: Optional[List[str]] = Field(None, description="List of metrics provided by the component")
    port: Optional[int] = Field(None, description="Port on which the component runs")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the component")


class ComponentUpdate(TektonBaseModel):
    """Model for updating a component's registration information."""
    
    name: Optional[str] = Field(None, description="Human-readable name of the component")
    description: Optional[str] = Field(None, description="Description of the component's purpose")
    version: Optional[str] = Field(None, description="Version of the component")
    api_endpoints: Optional[List[str]] = Field(None, description="List of API endpoints provided by the component")
    capabilities: Optional[List[str]] = Field(None, description="List of capabilities provided by the component")
    dependencies: Optional[List[str]] = Field(None, description="List of dependencies required by the component")
    metrics_provided: Optional[List[str]] = Field(None, description="List of metrics provided by the component")
    port: Optional[int] = Field(None, description="Port on which the component runs")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the component")
    status: Optional[str] = Field(None, description="Current status of the component")


class ComponentQuery(TektonBaseModel):
    """Model for querying components."""
    
    component_type: Optional[ComponentType] = Field(None, description="Filter by component type")
    capabilities: Optional[List[str]] = Field(None, description="Filter by capabilities")
    dependencies: Optional[List[str]] = Field(None, description="Filter by dependencies")
    metrics_provided: Optional[List[str]] = Field(None, description="Filter by provided metrics")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    status: Optional[str] = Field(None, description="Filter by status")
    limit: int = Field(100, description="Maximum number of results to return")
    offset: int = Field(0, description="Offset for pagination")


class ComponentResponse(TektonBaseModel):
    """Model for generic component operation response."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")


class ComponentPerformanceAnalysis(TektonBaseModel):
    """Model for component performance analysis."""
    
    component_id: str = Field(..., description="ID of the component")
    timestamp: str = Field(..., description="Timestamp of the analysis (ISO format)")
    performance_category: PerformanceCategory = Field(..., description="Overall performance categorization")
    metrics_summary: Dict[str, Any] = Field(..., description="Summary of key performance metrics")
    identified_issues: Optional[List[Dict[str, Any]]] = Field(None, description="Issues identified in the analysis")
    optimization_opportunities: Optional[List[Dict[str, Any]]] = Field(None, description="Potential optimization opportunities")
    historical_trend: Optional[Dict[str, Any]] = Field(None, description="Historical performance trend")
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Recommendations for improvement")


class ComponentInteractionAnalysis(TektonBaseModel):
    """Model for analyzing interactions between components."""
    
    component_ids: List[str] = Field(..., description="IDs of the components in the interaction")
    timestamp: str = Field(..., description="Timestamp of the analysis (ISO format)")
    interaction_metrics: Dict[str, Any] = Field(..., description="Metrics related to the interaction")
    efficiency_score: float = Field(..., description="Efficiency score of the interaction (0.0-1.0)")
    bottlenecks: Optional[List[Dict[str, Any]]] = Field(None, description="Identified bottlenecks")
    communication_patterns: Optional[Dict[str, Any]] = Field(None, description="Patterns in component communication")
    optimization_opportunities: Optional[List[Dict[str, Any]]] = Field(None, description="Opportunities for optimizing interaction")
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Recommendations for improvement")