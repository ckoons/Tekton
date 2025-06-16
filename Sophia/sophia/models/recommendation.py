"""
Recommendation data models for Sophia API.

This module defines the Pydantic models for recommendation-related API requests and responses.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import Field
from tekton.models.base import TektonBaseModel


class RecommendationStatus(str, Enum):
    """Status of a recommendation."""
    
    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class RecommendationPriority(str, Enum):
    """Priority level of a recommendation."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationType(str, Enum):
    """Type of recommendation."""
    
    PERFORMANCE = "performance"
    EFFICIENCY = "efficiency"
    ACCURACY = "accuracy"
    RELIABILITY = "reliability"
    SECURITY = "security"
    USABILITY = "usability"
    ARCHITECTURE = "architecture"
    INTEGRATION = "integration"
    CAPABILITY = "capability"


class RecommendationCreate(TektonBaseModel):
    """Model for creating a new recommendation."""
    
    title: str = Field(..., description="Title of the recommendation")
    description: str = Field(..., description="Detailed description of the recommendation")
    recommendation_type: RecommendationType = Field(..., description="Type of recommendation")
    target_components: List[str] = Field(..., description="List of components this recommendation applies to")
    priority: RecommendationPriority = Field(..., description="Priority level")
    rationale: str = Field(..., description="Rationale behind the recommendation")
    expected_impact: Dict[str, Any] = Field(..., description="Expected impact of implementing the recommendation")
    implementation_complexity: str = Field(..., description="Estimated complexity of implementation")
    supporting_evidence: Optional[Dict[str, Any]] = Field(None, description="Evidence supporting the recommendation")
    experiment_ids: Optional[List[str]] = Field(None, description="Associated experiment IDs")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the recommendation")


class RecommendationUpdate(TektonBaseModel):
    """Model for updating a recommendation."""
    
    title: Optional[str] = Field(None, description="Title of the recommendation")
    description: Optional[str] = Field(None, description="Detailed description of the recommendation")
    status: Optional[RecommendationStatus] = Field(None, description="Status of the recommendation")
    priority: Optional[RecommendationPriority] = Field(None, description="Priority level")
    expected_impact: Optional[Dict[str, Any]] = Field(None, description="Expected impact of implementing the recommendation")
    implementation_notes: Optional[str] = Field(None, description="Notes on the implementation process")
    verification_results: Optional[Dict[str, Any]] = Field(None, description="Results of verification after implementation")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the recommendation")


class RecommendationQuery(TektonBaseModel):
    """Model for querying recommendations."""
    
    status: Optional[RecommendationStatus] = Field(None, description="Filter by status")
    recommendation_type: Optional[RecommendationType] = Field(None, description="Filter by recommendation type")
    priority: Optional[RecommendationPriority] = Field(None, description="Filter by priority")
    target_components: Optional[List[str]] = Field(None, description="Filter by target components")
    experiment_ids: Optional[List[str]] = Field(None, description="Filter by associated experiment IDs")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    created_after: Optional[str] = Field(None, description="Filter by creation time after (ISO format)")
    created_before: Optional[str] = Field(None, description="Filter by creation time before (ISO format)")
    limit: int = Field(100, description="Maximum number of results to return")
    offset: int = Field(0, description="Offset for pagination")


class RecommendationResponse(TektonBaseModel):
    """Model for generic recommendation operation response."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")


class RecommendationVerification(TektonBaseModel):
    """Model for verifying implementation of a recommendation."""
    
    recommendation_id: str = Field(..., description="ID of the recommendation")
    verification_metrics: Dict[str, Any] = Field(..., description="Metrics used for verification")
    observed_impact: Dict[str, Any] = Field(..., description="Observed impact after implementation")
    verification_status: str = Field(..., description="Result of verification (success/partial/failure)")
    verification_notes: Optional[str] = Field(None, description="Notes on the verification process")
    follow_up_actions: Optional[List[str]] = Field(None, description="Suggested follow-up actions if needed")