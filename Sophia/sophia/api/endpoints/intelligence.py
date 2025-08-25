"""
Intelligence API endpoints for Sophia.

This module defines the API endpoints for intelligence measurement in Sophia.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from datetime import datetime

from sophia.core.intelligence_measurement import get_intelligence_measurement
from sophia.models.intelligence import (
    IntelligenceMeasurementCreate,
    IntelligenceMeasurementQuery,
    IntelligenceMeasurementResponse,
    ComponentIntelligenceProfile,
    IntelligenceComparison,
    IntelligenceDimension,
    MeasurementMethod
)

# Create router
router = APIRouter()

# ------------------------
# Intelligence API Routes
# ------------------------

@router.post("/measurements", response_model=IntelligenceMeasurementResponse)
async def create_intelligence_measurement(
    measurement: IntelligenceMeasurementCreate,
    intelligence_measurement = Depends(get_intelligence_measurement)
):
    """Create a new intelligence measurement."""
    try:
        measurement_id = await intelligence_measurement.record_measurement(
            component_id=measurement.component_id,
            dimension=measurement.dimension,
            measurement_method=measurement.measurement_method,
            score=measurement.score,
            confidence=measurement.confidence,
            context=measurement.context,
            evidence=measurement.evidence,
            evaluator=measurement.evaluator,
            timestamp=measurement.timestamp,
            tags=measurement.tags
        )
        
        return IntelligenceMeasurementResponse(
            success=True,
            message="Intelligence measurement recorded successfully",
            data={"measurement_id": measurement_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record intelligence measurement: {str(e)}"
        )

@router.get("/measurements", response_model=List[Dict[str, Any]])
async def query_intelligence_measurements(
    component_id: Optional[str] = None,
    dimensions: Optional[str] = Query(None, description="Comma-separated list of dimensions"),
    measurement_method: Optional[MeasurementMethod] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    min_confidence: Optional[float] = None,
    evaluator: Optional[str] = None,
    measured_after: Optional[str] = None,
    measured_before: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated list of tags"),
    limit: int = 100,
    offset: int = 0,
    intelligence_measurement = Depends(get_intelligence_measurement)
):
    """Query intelligence measurements with filtering."""
    try:
        # Parse lists from comma-separated strings
        dimension_list = [IntelligenceDimension(d) for d in dimensions.split(",")] if dimensions else None
        tag_list = tags.split(",") if tags else None
        
        # Create query object
        query = IntelligenceMeasurementQuery(
            component_id=component_id,
            dimensions=dimension_list,
            measurement_method=measurement_method,
            min_score=min_score,
            max_score=max_score,
            min_confidence=min_confidence,
            evaluator=evaluator,
            measured_after=measured_after,
            measured_before=measured_before,
            tags=tag_list,
            limit=limit,
            offset=offset
        )
        
        # Execute query
        measurements = await intelligence_measurement.query_measurements(query)
        return measurements
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query intelligence measurements: {str(e)}"
        )

@router.get("/components/{component_id}/profile", response_model=ComponentIntelligenceProfile)
async def get_component_intelligence_profile(
    component_id: str = Path(..., description="ID of the component"),
    timestamp: Optional[str] = None,
    intelligence_measurement = Depends(get_intelligence_measurement)
):
    """Get the intelligence profile of a specific component."""
    try:
        profile = await intelligence_measurement.get_component_profile(
            component_id=component_id,
            timestamp=timestamp
        )
        
        if profile:
            return profile
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Intelligence profile not found for component: {component_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get component intelligence profile: {str(e)}"
        )

@router.post("/components/compare", response_model=IntelligenceComparison)
async def compare_component_intelligence(
    component_ids: List[str],
    dimensions: Optional[List[IntelligenceDimension]] = None,
    intelligence_measurement = Depends(get_intelligence_measurement)
):
    """Compare intelligence between components."""
    try:
        if len(component_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least two components must be provided for comparison"
            )
        
        comparison = await intelligence_measurement.compare_components(
            component_ids=component_ids,
            dimensions=dimensions
        )
        
        if comparison:
            return comparison
        else:
            raise HTTPException(
                status_code=404,
                detail="Failed to generate intelligence comparison"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare component intelligence: {str(e)}"
        )

@router.get("/dimensions", response_model=Dict[str, Dict[str, Any]])
async def get_intelligence_dimensions(
    intelligence_measurement = Depends(get_intelligence_measurement)
):
    """Get information about all intelligence dimensions."""
    try:
        return await intelligence_measurement.get_intelligence_dimensions()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get intelligence dimensions: {str(e)}"
        )

@router.get("/dimensions/{dimension}", response_model=Dict[str, Any])
async def get_intelligence_dimension(
    dimension: IntelligenceDimension = Path(..., description="Intelligence dimension"),
    intelligence_measurement = Depends(get_intelligence_measurement)
):
    """Get detailed information about a specific intelligence dimension."""
    try:
        dimension_info = await intelligence_measurement.get_intelligence_dimension(dimension)
        
        if dimension_info:
            return dimension_info
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Intelligence dimension not found: {dimension}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get intelligence dimension: {str(e)}"
        )

@router.get("/ecosystem/profile", response_model=Dict[str, Any])
async def get_ecosystem_intelligence_profile(
    intelligence_measurement = Depends(get_intelligence_measurement)
):
    """Get an intelligence profile for the entire Tekton ecosystem."""
    try:
        profile = await intelligence_measurement.get_ecosystem_profile()
        
        if profile:
            return profile
        else:
            raise HTTPException(
                status_code=404,
                detail="Ecosystem intelligence profile not available"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get ecosystem intelligence profile: {str(e)}"
        )

# ------------------------
# Theory Validation Routes
# ------------------------

@router.get("/theory-validation/protocols", response_model=List[Dict[str, Any]])
async def get_theory_validation_protocols():
    """Get active theory-experiment protocols."""
    try:
        # For now, return mock data - this would eventually integrate with Noesis
        protocols = [
            {
                "protocol_id": "sophia-intelligence-001",
                "protocol_type": "intelligence_measurement",
                "status": "active",
                "iteration": 1,
                "created_at": datetime.now().isoformat(),
                "theory": "Component intelligence can be measured through performance metrics",
                "experiment_type": "metric_correlation",
                "hypothesis": "Response time and error rate correlate with intelligence scores"
            },
            {
                "protocol_id": "sophia-learning-002", 
                "protocol_type": "adaptive_learning",
                "status": "completed",
                "iteration": 3,
                "created_at": datetime.now().isoformat(),
                "theory": "CI systems improve through feedback loops",
                "experiment_type": "longitudinal_analysis",
                "hypothesis": "Performance improves over time with consistent feedback"
            }
        ]
        return protocols
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get theory validation protocols: {str(e)}"
        )

# ------------------------
# Collective Intelligence Routes
# ------------------------

@router.get("/collective-intelligence/analysis", response_model=Dict[str, Any])
async def get_collective_intelligence_analysis():
    """Get collective intelligence analysis for the Tekton ecosystem."""
    try:
        # For now, return mock data - this would eventually analyze real system performance
        analysis = {
            "performance_metrics": {
                "overall_success_rate": 0.87,
                "component_coordination": 0.92,
                "task_completion_rate": 0.84,
                "error_recovery_rate": 0.78
            },
            "emergence_patterns": {
                "emergence_strength": 0.73,
                "novel_solutions_detected": 12,
                "cross_component_innovations": 8,
                "system_level_behaviors": 5
            },
            "team_dynamics": {
                "best_teams": [
                    (["hermes", "athena", "rhetor"], 0.95),
                    (["sophia", "engram", "prometheus"], 0.89),
                    (["ergon", "synthesis", "harmonia"], 0.86)
                ],
                "collaboration_patterns": {
                    "most_frequent": ["hermes-athena", "sophia-engram", "rhetor-telos"],
                    "most_effective": ["athena-prometheus", "hermes-synthesis", "sophia-metis"]
                }
            },
            "cognitive_evolution": {
                "collective_learning_rate": 0.15,
                "knowledge_transfer_efficiency": 0.68,
                "adaptive_response_time": 2.3,
                "system_intelligence_growth": 0.12
            },
            "recommendations": [
                "Increase communication frequency between Hermes and Athena",
                "Implement cross-training between Sophia and Prometheus",
                "Optimize task distribution for better load balancing"
            ],
            "analysis_timestamp": datetime.now().isoformat(),
            "data_window": "last_30_days"
        }
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get collective intelligence analysis: {str(e)}"
        )