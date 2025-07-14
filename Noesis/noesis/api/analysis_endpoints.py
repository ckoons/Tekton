"""
API endpoints for theoretical analysis capabilities
Exposes Noesis mathematical framework via REST API
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ..core.theoretical import (
    ManifoldAnalyzer, DynamicsAnalyzer, CatastropheAnalyzer, SynthesisAnalyzer
)
from ..core.integration.data_models import CollectiveState
from .mcp_tools import NoesisMCPTools

logger = logging.getLogger(__name__)

# Create router for analysis endpoints
router = APIRouter(prefix="/api/analysis", tags=["theoretical_analysis"])

# Initialize analyzers
manifold_analyzer = ManifoldAnalyzer()
dynamics_analyzer = DynamicsAnalyzer()
catastrophe_analyzer = CatastropheAnalyzer()
synthesis_analyzer = SynthesisAnalyzer()
mcp_tools = NoesisMCPTools()


# Request/Response models
class ManifoldAnalysisRequest(BaseModel):
    """Request for manifold analysis"""
    collective_states: List[Dict[str, Any]] = Field(
        description="List of collective CI states to analyze"
    )
    n_components: Optional[int] = Field(
        None,
        description="Number of principal components for reduction"
    )
    analysis_depth: str = Field(
        "detailed",
        description="Level of analysis depth",
        pattern="^(basic|detailed|comprehensive)$"
    )


class DynamicsAnalysisRequest(BaseModel):
    """Request for dynamics analysis"""
    time_series_data: List[Dict[str, Any]] = Field(
        description="Temporal sequence of collective states"
    )
    n_regimes: int = Field(
        4,
        description="Number of regimes to identify",
        ge=2,
        le=10
    )
    analysis_window: Optional[int] = Field(
        None,
        description="Window size for dynamics analysis"
    )


class CatastropheAnalysisRequest(BaseModel):
    """Request for catastrophe analysis"""
    trajectory_data: List[Dict[str, Any]] = Field(
        description="System trajectory for analysis"
    )
    current_state: Optional[Dict[str, Any]] = Field(
        None,
        description="Current state for prediction"
    )
    lookahead_steps: int = Field(
        10,
        description="Steps to look ahead for transitions",
        ge=1,
        le=100
    )


class SynthesisAnalysisRequest(BaseModel):
    """Request for synthesis analysis"""
    multi_scale_data: Dict[str, Any] = Field(
        description="Data from multiple scales/systems"
    )
    principle_types: List[str] = Field(
        default=["scaling", "fractal", "emergent"],
        description="Types of principles to extract"
    )
    confidence_threshold: float = Field(
        0.8,
        description="Minimum confidence for principles",
        ge=0.0,
        le=1.0
    )


class TheoryValidationRequest(BaseModel):
    """Request for theory validation with experiments"""
    theoretical_prediction: Dict[str, Any] = Field(
        description="Theoretical model predictions"
    )
    experiment_design: Dict[str, Any] = Field(
        description="Proposed experimental setup"
    )
    validation_metrics: Optional[List[str]] = Field(
        None,
        description="Specific metrics to validate"
    )


class AnalysisResponse(BaseModel):
    """Standard response for analysis endpoints"""
    status: str
    analysis_type: str
    results: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    warnings: Optional[List[str]] = None


# Endpoints
@router.post("/manifold", response_model=AnalysisResponse)
async def analyze_manifold(request: ManifoldAnalysisRequest):
    """
    Perform manifold analysis on collective states
    
    Analyzes the geometric structure of collective AI states,
    reduces dimensionality, and identifies key patterns.
    """
    try:
        # Use MCP tools for comprehensive analysis
        result = await mcp_tools.analyze_cognitive_manifold(
            collective_states=request.collective_states,
            analysis_depth=request.analysis_depth
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return AnalysisResponse(
            status="success",
            analysis_type="manifold_analysis",
            results=result["results"],
            metadata=result.get("metadata"),
            timestamp=datetime.fromisoformat(result["timestamp"])
        )
        
    except Exception as e:
        logger.error(f"Manifold analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dynamics", response_model=AnalysisResponse)
async def analyze_dynamics(request: DynamicsAnalysisRequest):
    """
    Analyze dynamics using SLDS modeling
    
    Identifies cognitive regimes, transitions, and stability
    in collective AI systems over time.
    """
    try:
        result = await mcp_tools.identify_regime_dynamics(
            time_series_data=request.time_series_data,
            expected_regimes=request.n_regimes
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return AnalysisResponse(
            status="success",
            analysis_type="dynamics_analysis",
            results={
                "current_regime": result["current_regime"],
                "regime_sequence": result["regime_sequence"],
                "transition_points": result["transition_points"],
                "stability_scores": result["stability_scores"],
                "predicted_transitions": result["predicted_transitions"],
                "full_analysis": result.get("full_results", {})
            },
            timestamp=datetime.fromisoformat(result["timestamp"])
        )
        
    except Exception as e:
        logger.error(f"Dynamics analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/catastrophe", response_model=AnalysisResponse)
async def analyze_catastrophe(request: CatastropheAnalysisRequest):
    """
    Detect and predict critical transitions
    
    Uses catastrophe theory to identify bifurcations,
    phase transitions, and early warning signals.
    """
    try:
        # Prepare current state with trajectory
        current_state = request.current_state or {}
        current_state["recent_trajectory"] = request.trajectory_data
        
        result = await mcp_tools.predict_phase_transitions(
            current_state=current_state,
            lookahead_window=request.lookahead_steps
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return AnalysisResponse(
            status="success",
            analysis_type="catastrophe_analysis",
            results={
                "predictions": result["predictions"],
                "warning_level": result["warning_level"],
                "warning_signals": result["warning_signals"],
                "critical_points_detected": result["critical_points_detected"]
            },
            timestamp=datetime.fromisoformat(result["timestamp"])
        )
        
    except Exception as e:
        logger.error(f"Catastrophe analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesis", response_model=AnalysisResponse)
async def analyze_synthesis(request: SynthesisAnalysisRequest):
    """
    Extract universal principles across scales
    
    Identifies patterns that hold across different scales
    and systems in collective AI behavior.
    """
    try:
        result = await mcp_tools.extract_universal_principles(
            multi_scale_data=request.multi_scale_data,
            principle_types=request.principle_types
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return AnalysisResponse(
            status="success",
            analysis_type="synthesis_analysis",
            results={
                "principles": result["principles"],
                "total_found": result["total_found"],
                "filtered_count": result["filtered_count"],
                "scaling_analysis": result.get("scaling_analysis"),
                "emergent_properties": result.get("emergent_properties", []),
                "cross_scale_patterns": result.get("cross_scale_patterns", [])
            },
            timestamp=datetime.fromisoformat(result["timestamp"])
        )
        
    except Exception as e:
        logger.error(f"Synthesis analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-theory", response_model=AnalysisResponse)
async def validate_theory(request: TheoryValidationRequest):
    """
    Create validation protocol for Sophia experiments
    
    Interfaces theoretical predictions with experimental
    validation through Sophia.
    """
    try:
        result = await mcp_tools.validate_with_experiment(
            theoretical_prediction=request.theoretical_prediction,
            experiment_design=request.experiment_design
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return AnalysisResponse(
            status="success",
            analysis_type="theory_validation",
            results={
                "validation_protocol": result["validation_protocol"],
                "sophia_integration": result["sophia_integration"],
                "instructions": result["instructions"]
            },
            timestamp=datetime.fromisoformat(result["timestamp"])
        )
        
    except Exception as e:
        logger.error(f"Theory validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trajectory", response_model=AnalysisResponse)
async def analyze_trajectory(
    trajectory_data: List[Dict[str, Any]],
    analysis_methods: Optional[List[str]] = None
):
    """
    Analyze collective trajectory evolution
    
    Time-series analysis of CI collective behavior using
    various methods (Fourier, wavelet, recurrence).
    """
    try:
        result = await mcp_tools.analyze_collective_trajectory(
            trajectory_data=trajectory_data,
            analysis_methods=analysis_methods
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return AnalysisResponse(
            status="success",
            analysis_type="trajectory_analysis",
            results=result["results"],
            metadata={
                "trajectory_length": result["trajectory_length"],
                "dimensionality": result["dimensionality"],
                "methods_applied": result["results"]["methods_applied"]
            },
            timestamp=datetime.fromisoformat(result["timestamp"])
        )
        
    except Exception as e:
        logger.error(f"Trajectory analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/criticality", response_model=AnalysisResponse)
async def compute_criticality(
    state_space: List[Dict[str, Any]],
    criticality_indicators: Optional[List[str]] = None
):
    """
    Compute criticality metrics
    
    Identifies lines of criticality in the collective
    state manifold using various indicators.
    """
    try:
        result = await mcp_tools.compute_criticality_metrics(
            state_space=state_space,
            criticality_indicators=criticality_indicators
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return AnalysisResponse(
            status="success",
            analysis_type="criticality_analysis",
            results={
                "metrics": result["metrics"],
                "critical_regions": result["critical_regions"],
                "indicators_computed": result["indicators_computed"]
            },
            metadata={
                "state_space_size": result["state_space_size"]
            },
            timestamp=datetime.fromisoformat(result["timestamp"])
        )
        
    except Exception as e:
        logger.error(f"Criticality analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-model", response_model=AnalysisResponse)
async def generate_theoretical_model(
    training_data: List[Dict[str, Any]],
    model_type: str = "hybrid",
    background_tasks: BackgroundTasks = None
):
    """
    Generate theoretical model from observations
    
    Creates predictive models (geometric, dynamic, or hybrid)
    from historical collective behavior data.
    """
    try:
        if model_type not in ["geometric", "dynamic", "hybrid"]:
            raise HTTPException(
                status_code=400, 
                detail="Model type must be 'geometric', 'dynamic', or 'hybrid'"
            )
        
        result = await mcp_tools.generate_theoretical_model(
            training_data=training_data,
            model_type=model_type
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Optionally save model in background
        if background_tasks:
            background_tasks.add_task(
                save_model_to_storage,
                model_id=result["model_id"],
                model_data=result
            )
        
        return AnalysisResponse(
            status="success",
            analysis_type="model_generation",
            results={
                "model_id": result["model_id"],
                "model_type": result["model_type"],
                "components": result["components"],
                "model_summary": result["model_summary"],
                "training_samples": result["training_samples"]
            },
            timestamp=datetime.fromisoformat(result["timestamp"])
        )
        
    except Exception as e:
        logger.error(f"Model generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_analysis_status():
    """Get status of theoretical analysis capabilities"""
    return {
        "status": "active",
        "analyzers": {
            "manifold": "ready",
            "dynamics": "ready",
            "catastrophe": "ready",
            "synthesis": "ready"
        },
        "mcp_tools": "initialized",
        "available_endpoints": [
            "/manifold",
            "/dynamics",
            "/catastrophe",
            "/synthesis",
            "/validate-theory",
            "/trajectory",
            "/criticality",
            "/generate-model"
        ],
        "timestamp": datetime.now().isoformat()
    }


# Helper functions
async def save_model_to_storage(model_id: str, model_data: Dict[str, Any]):
    """Save generated model to storage (placeholder)"""
    logger.info(f"Saving model {model_id} to storage")
    # TODO: Implement actual storage mechanism
    pass