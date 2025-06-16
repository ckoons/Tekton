"""
Intelligence measurement data models for Sophia API.

This module defines the Pydantic models for intelligence-related API requests and responses.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import Field
from tekton.models.base import TektonBaseModel


class IntelligenceDimension(str, Enum):
    """Intelligence dimensions as defined in the Intelligence Dimensions Framework."""
    
    LANGUAGE_PROCESSING = "language_processing"
    REASONING = "reasoning"
    KNOWLEDGE = "knowledge"
    LEARNING = "learning"
    CREATIVITY = "creativity"
    PLANNING = "planning"
    PROBLEM_SOLVING = "problem_solving"
    ADAPTATION = "adaptation"
    COLLABORATION = "collaboration"
    METACOGNITION = "metacognition"


class MeasurementMethod(str, Enum):
    """Method used for intelligence measurement."""
    
    CAPABILITY_TEST = "capability_test"
    METRICS_ANALYSIS = "metrics_analysis"
    OUTPUT_EVALUATION = "output_evaluation"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    USER_FEEDBACK = "user_feedback"
    EXPERT_ASSESSMENT = "expert_assessment"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    SELF_ASSESSMENT = "self_assessment"


class IntelligenceMeasurementCreate(TektonBaseModel):
    """Model for creating a new intelligence measurement."""
    
    component_id: str = Field(..., description="ID of the component being measured")
    dimension: IntelligenceDimension = Field(..., description="Intelligence dimension being measured")
    measurement_method: MeasurementMethod = Field(..., description="Method used for measurement")
    score: float = Field(..., description="Measurement score (0.0-1.0)")
    confidence: float = Field(..., description="Confidence in the measurement (0.0-1.0)")
    context: Dict[str, Any] = Field(..., description="Context of the measurement")
    evidence: Dict[str, Any] = Field(..., description="Evidence supporting the measurement")
    evaluator: Optional[str] = Field(None, description="Entity performing the evaluation")
    timestamp: Optional[str] = Field(None, description="Timestamp of the measurement (ISO format)")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the measurement")


class IntelligenceMeasurementQuery(TektonBaseModel):
    """Model for querying intelligence measurements."""
    
    component_id: Optional[str] = Field(None, description="Filter by component ID")
    dimensions: Optional[List[IntelligenceDimension]] = Field(None, description="Filter by dimensions")
    measurement_method: Optional[MeasurementMethod] = Field(None, description="Filter by measurement method")
    min_score: Optional[float] = Field(None, description="Filter by minimum score")
    max_score: Optional[float] = Field(None, description="Filter by maximum score")
    min_confidence: Optional[float] = Field(None, description="Filter by minimum confidence")
    evaluator: Optional[str] = Field(None, description="Filter by evaluator")
    measured_after: Optional[str] = Field(None, description="Filter by measurement time after (ISO format)")
    measured_before: Optional[str] = Field(None, description="Filter by measurement time before (ISO format)")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    limit: int = Field(100, description="Maximum number of results to return")
    offset: int = Field(0, description="Offset for pagination")


class IntelligenceMeasurementResponse(TektonBaseModel):
    """Model for generic intelligence measurement operation response."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")


class ComponentIntelligenceProfile(TektonBaseModel):
    """Model for a component's intelligence profile."""
    
    component_id: str = Field(..., description="ID of the component")
    timestamp: str = Field(..., description="Timestamp of the profile generation (ISO format)")
    dimensions: Dict[IntelligenceDimension, float] = Field(..., description="Scores for each dimension")
    overall_score: float = Field(..., description="Overall intelligence score")
    confidence: Dict[IntelligenceDimension, float] = Field(..., description="Confidence for each dimension score")
    strengths: List[IntelligenceDimension] = Field(..., description="Identified strengths")
    improvement_areas: List[IntelligenceDimension] = Field(..., description="Areas for improvement")
    comparison: Optional[Dict[str, Any]] = Field(None, description="Comparison with other components or benchmarks")
    historical_trend: Optional[Dict[str, Any]] = Field(None, description="Historical trend data")


class IntelligenceComparison(TektonBaseModel):
    """Model for comparing intelligence between components."""
    
    component_ids: List[str] = Field(..., description="List of component IDs to compare")
    dimensions: Optional[List[IntelligenceDimension]] = Field(None, description="Dimensions to compare (all if None)")
    timestamp: str = Field(..., description="Timestamp of the comparison (ISO format)")
    scores: Dict[str, Dict[IntelligenceDimension, float]] = Field(..., description="Scores by component and dimension")
    relative_strengths: Dict[str, List[IntelligenceDimension]] = Field(..., description="Relative strengths by component")
    collaboration_potential: Dict[str, Dict[str, float]] = Field(..., description="Potential collaboration scores")
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Recommendations based on comparison")