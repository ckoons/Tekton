"""
Models package for Sophia API.

This package contains the Pydantic models used for API request and response validation.
"""

from sophia.models.metrics import (
    MetricSubmission,
    MetricQuery,
    MetricResponse,
    MetricAggregationQuery,
    MetricDefinition
)

from sophia.models.experiment import (
    ExperimentStatus,
    ExperimentType,
    ExperimentCreate,
    ExperimentUpdate,
    ExperimentQuery,
    ExperimentResponse,
    ExperimentResult
)

from sophia.models.recommendation import (
    RecommendationStatus,
    RecommendationPriority,
    RecommendationType,
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationQuery,
    RecommendationResponse,
    RecommendationVerification
)

from sophia.models.intelligence import (
    IntelligenceDimension,
    MeasurementMethod,
    IntelligenceMeasurementCreate,
    IntelligenceMeasurementQuery,
    IntelligenceMeasurementResponse,
    ComponentIntelligenceProfile,
    IntelligenceComparison
)

from sophia.models.component import (
    ComponentType,
    PerformanceCategory,
    ComponentRegister,
    ComponentUpdate,
    ComponentQuery,
    ComponentResponse,
    ComponentPerformanceAnalysis,
    ComponentInteractionAnalysis
)

from sophia.models.research import (
    ResearchApproach,
    ResearchStatus,
    ResearchProjectCreate,
    ResearchProjectUpdate,
    ResearchProjectQuery,
    ResearchProjectResponse,
    CSAConfigCreate,
    CSAResult,
    CatastropheTheoryAnalysisCreate,
    CatastropheTheoryResult
)
