"""
Research data models for Sophia API.

This module defines the Pydantic models for AI research-related API requests and responses.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import Field
from tekton.models.base import TektonBaseModel


class ResearchApproach(str, Enum):
    """Research approaches used in Sophia."""
    
    COMPUTATIONAL_SPECTRAL_ANALYSIS = "computational_spectral_analysis"
    CATASTROPHE_THEORY = "catastrophe_theory"
    CAPABILITY_EMERGENCE = "capability_emergence"
    COLLABORATIVE_INTELLIGENCE = "collaborative_intelligence"
    TRANSFER_LEARNING = "transfer_learning"
    MULTIMODAL_INTEGRATION = "multimodal_integration"
    LATENT_SPACE_EXPLORATION = "latent_space_exploration"


class ResearchStatus(str, Enum):
    """Status of a research project."""
    
    PROPOSED = "proposed"
    PLANNING = "planning"
    ACTIVE = "active"
    ANALYZING = "analyzing"
    CONCLUDED = "concluded"
    PUBLISHED = "published"
    ABANDONED = "abandoned"


class ResearchProjectCreate(TektonBaseModel):
    """Model for creating a new research project."""
    
    title: str = Field(..., description="Title of the research project")
    description: str = Field(..., description="Detailed description of the project")
    approach: ResearchApproach = Field(..., description="Primary research approach")
    research_questions: List[str] = Field(..., description="Research questions being investigated")
    hypothesis: Optional[str] = Field(None, description="Primary hypothesis")
    target_components: List[str] = Field(..., description="Components involved in the research")
    data_requirements: Dict[str, Any] = Field(..., description="Data required for the research")
    expected_outcomes: List[str] = Field(..., description="Expected outcomes of the research")
    estimated_duration: str = Field(..., description="Estimated duration of the project")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the project")


class ResearchProjectUpdate(TektonBaseModel):
    """Model for updating a research project."""
    
    title: Optional[str] = Field(None, description="Title of the research project")
    description: Optional[str] = Field(None, description="Detailed description of the project")
    status: Optional[ResearchStatus] = Field(None, description="Status of the project")
    research_questions: Optional[List[str]] = Field(None, description="Research questions being investigated")
    hypothesis: Optional[str] = Field(None, description="Primary hypothesis")
    interim_findings: Optional[Dict[str, Any]] = Field(None, description="Interim findings")
    blockers: Optional[List[str]] = Field(None, description="Current blockers or challenges")
    next_steps: Optional[List[str]] = Field(None, description="Planned next steps")
    tags: Optional[List[str]] = Field(None, description="Tags for categorizing the project")


class ResearchProjectQuery(TektonBaseModel):
    """Model for querying research projects."""
    
    status: Optional[ResearchStatus] = Field(None, description="Filter by status")
    approach: Optional[ResearchApproach] = Field(None, description="Filter by research approach")
    target_components: Optional[List[str]] = Field(None, description="Filter by target components")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    created_after: Optional[str] = Field(None, description="Filter by creation time after (ISO format)")
    created_before: Optional[str] = Field(None, description="Filter by creation time before (ISO format)")
    limit: int = Field(100, description="Maximum number of results to return")
    offset: int = Field(0, description="Offset for pagination")


class ResearchProjectResponse(TektonBaseModel):
    """Model for generic research project operation response."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")


class CSAConfigCreate(TektonBaseModel):
    """Model for creating a Computational Spectral Analysis configuration."""
    
    network_id: str = Field(..., description="ID of the neural network to analyze")
    layer_ids: List[str] = Field(..., description="IDs of the layers to analyze")
    activation_samples: int = Field(..., description="Number of activation samples to collect")
    input_data_source: str = Field(..., description="Source of input data for activation collection")
    analysis_dimensions: List[str] = Field(..., description="Dimensions to analyze")
    spectral_methods: List[str] = Field(..., description="Spectral analysis methods to apply")
    visualization_options: Optional[Dict[str, Any]] = Field(None, description="Options for result visualization")


class CSAResult(TektonBaseModel):
    """Model for Computational Spectral Analysis results."""
    
    analysis_id: str = Field(..., description="ID of the analysis")
    network_id: str = Field(..., description="ID of the analyzed neural network")
    timestamp: str = Field(..., description="Timestamp of the analysis (ISO format)")
    spectral_patterns: Dict[str, Any] = Field(..., description="Identified spectral patterns")
    layer_activations: Dict[str, Dict[str, Any]] = Field(..., description="Activation statistics by layer")
    principal_components: Optional[Dict[str, Any]] = Field(None, description="Principal component analysis results")
    interpretations: Optional[List[Dict[str, Any]]] = Field(None, description="Interpretations of the analysis")
    visualization_data: Optional[Dict[str, Any]] = Field(None, description="Data for visualizing the results")


class CatastropheTheoryAnalysisCreate(TektonBaseModel):
    """Model for creating a Catastrophe Theory analysis."""
    
    capability_dimension: str = Field(..., description="Capability dimension to analyze")
    component_ids: List[str] = Field(..., description="Components to include in the analysis")
    control_parameters: List[str] = Field(..., description="Control parameters to vary")
    parameter_ranges: Dict[str, Dict[str, float]] = Field(..., description="Ranges for each parameter")
    measurement_metrics: List[str] = Field(..., description="Metrics to measure for capability assessment")
    sampling_strategy: str = Field(..., description="Strategy for sampling the parameter space")
    analysis_methods: List[str] = Field(..., description="Methods to use for analyzing transitions")


class CatastropheTheoryResult(TektonBaseModel):
    """Model for Catastrophe Theory analysis results."""
    
    analysis_id: str = Field(..., description="ID of the analysis")
    capability_dimension: str = Field(..., description="Analyzed capability dimension")
    timestamp: str = Field(..., description="Timestamp of the analysis (ISO format)")
    transition_points: List[Dict[str, Any]] = Field(..., description="Identified capability transition points")
    parameter_sensitivities: Dict[str, float] = Field(..., description="Sensitivity to each parameter")
    catastrophe_types: Dict[str, str] = Field(..., description="Classified catastrophe types")
    stability_regions: Dict[str, Dict[str, Any]] = Field(..., description="Identified stability regions")
    predictive_model: Optional[Dict[str, Any]] = Field(None, description="Model for predicting transitions")
    visualization_data: Optional[Dict[str, Any]] = Field(None, description="Data for visualizing the results")