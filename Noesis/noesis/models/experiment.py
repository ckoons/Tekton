"""
Experiment models for Noesis-Sophia integration
Extends Sophia's experiment models with theory-specific fields
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ExperimentStatus(str, Enum):
    """Status of an experiment"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"


class ExperimentType(str, Enum):
    """Type of experiment"""
    A_B_TEST = "a_b_test"
    MULTIVARIATE = "multivariate"
    SHADOW_MODE = "shadow_mode"
    CANARY = "canary"
    PARAMETER_TUNING = "parameter_tuning"
    BEFORE_AFTER = "before_after"
    BASELINE_COMPARISON = "baseline_comparison"
    THEORY_VALIDATION = "theory_validation"  # New type for theory validation


class TheoryDrivenExperiment(BaseModel):
    """Experiment driven by theoretical predictions"""
    name: str = Field(..., description="Name of the experiment")
    description: str = Field(..., description="Description of the experiment")
    experiment_type: ExperimentType = Field(..., description="Type of experiment")
    theoretical_basis: Dict[str, Any] = Field(..., description="Theoretical model driving the experiment")
    predictions: Dict[str, Any] = Field(..., description="Theoretical predictions to validate")
    validation_criteria: List[Dict[str, Any]] = Field(..., description="Criteria for validating predictions")
    confidence_intervals: Dict[str, Any] = Field(..., description="Confidence intervals for predictions")
    suggested_metrics: List[str] = Field(..., description="Metrics suggested by theory")
    target_components: List[str] = Field(..., description="Components involved in experiment")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Experiment parameters")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Validate Catastrophe Prediction",
                "description": "Test prediction of phase transition in collective system",
                "experiment_type": "theory_validation",
                "theoretical_basis": {
                    "model_type": "catastrophe",
                    "model_id": "cat_20240115_120000"
                },
                "predictions": {
                    "transition_type": "fold_catastrophe",
                    "warning_signals": ["increased_variance", "critical_slowing_down"],
                    "estimated_time": 100
                },
                "validation_criteria": [
                    {
                        "metric": "variance",
                        "expected_range": [0.8, 1.2],
                        "confidence_level": 0.95
                    }
                ],
                "confidence_intervals": {
                    "transition_time": {
                        "lower_bound": 80,
                        "upper_bound": 120,
                        "confidence_level": 0.95
                    }
                },
                "suggested_metrics": ["variance", "autocorrelation", "response_time"],
                "target_components": ["collective_ai_system"],
                "parameters": {
                    "monitoring_frequency": "1Hz",
                    "early_warning_threshold": 2.0
                }
            }
        }


class TheoryValidationResult(BaseModel):
    """Results of theory validation experiment"""
    experiment_id: str = Field(..., description="ID of the experiment")
    theory_id: str = Field(..., description="ID of the theoretical model")
    validation_status: str = Field(..., description="Overall validation status")
    matches: List[Dict[str, Any]] = Field(..., description="Predictions that matched observations")
    mismatches: List[Dict[str, Any]] = Field(..., description="Predictions that didn't match")
    unexpected_observations: List[Dict[str, Any]] = Field(..., description="Unexpected phenomena observed")
    confidence_score: float = Field(..., description="Overall confidence in validation")
    insights: List[str] = Field(..., description="Insights from validation")
    suggested_refinements: List[Dict[str, Any]] = Field(..., description="Suggested theory refinements")
    
    class Config:
        schema_extra = {
            "example": {
                "experiment_id": "exp_123",
                "theory_id": "theory_456",
                "validation_status": "partially_validated",
                "matches": [
                    {
                        "metric": "variance",
                        "predicted": 1.0,
                        "observed": 0.95,
                        "within_ci": True
                    }
                ],
                "mismatches": [
                    {
                        "metric": "transition_time",
                        "predicted": 100,
                        "observed": 150,
                        "deviation": 0.5
                    }
                ],
                "unexpected_observations": [
                    {
                        "metric": "oscillation_frequency",
                        "value": 0.1,
                        "description": "Unexpected oscillatory behavior"
                    }
                ],
                "confidence_score": 0.75,
                "insights": [
                    "Theory correctly predicted variance increase",
                    "Transition occurred later than predicted",
                    "System showed unexpected oscillations"
                ],
                "suggested_refinements": [
                    {
                        "type": "parameter_adjustment",
                        "target": "transition_timing",
                        "suggestion": "Adjust time constant in model"
                    }
                ]
            }
        }