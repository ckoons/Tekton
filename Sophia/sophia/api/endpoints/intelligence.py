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