"""
Experiments API endpoints for Sophia.

This module defines the API endpoints for managing experiments in Sophia.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from datetime import datetime

from sophia.core.experiment_framework import get_experiment_framework
from sophia.models.experiment import (
    ExperimentCreate,
    ExperimentUpdate,
    ExperimentQuery,
    ExperimentResponse,
    ExperimentResult,
    ExperimentStatus,
    ExperimentType
)

# Create router
router = APIRouter()

# ------------------------
# Experiments API Routes
# ------------------------

@router.post("/llm/design", response_model=Dict[str, Any])
async def design_experiment_with_llm(
    hypothesis: str = Body(..., description="The hypothesis to test in the experiment"),
    available_components: Optional[List[str]] = Body(None, description="List of components available for the experiment"),
    metrics_summary: Optional[Dict[str, Any]] = Body(None, description="Summary of recent metrics relevant to the experiment"),
    llm_adapter = Depends(get_llm_adapter)
):
    """
    Design an experiment using LLM to test a specified hypothesis.
    Generates detailed experiment methodology, variables, and success criteria.
    """
    try:
        experiment_design = await # llm_adapter.design_experiment(
            hypothesis=hypothesis,
            available_components=available_components,
            metrics_summary=metrics_summary
        )
        return experiment_design
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to design experiment with LLM: {str(e)}"
        )

@router.post("/", response_model=ExperimentResponse)
async def create_experiment(
    experiment: ExperimentCreate,
    experiment_framework = Depends(get_experiment_framework)
):
    """Create a new experiment."""
    try:
        experiment_id = await experiment_framework.create_experiment(
            name=experiment.name,
            description=experiment.description,
            experiment_type=experiment.experiment_type,
            target_components=experiment.target_components,
            hypothesis=experiment.hypothesis,
            metrics=experiment.metrics,
            parameters=experiment.parameters,
            start_time=experiment.start_time,
            end_time=experiment.end_time,
            sample_size=experiment.sample_size,
            min_confidence=experiment.min_confidence,
            tags=experiment.tags
        )
        
        return ExperimentResponse(
            success=True,
            message="Experiment created successfully",
            data={"experiment_id": experiment_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create experiment: {str(e)}"
        )

@router.get("/", response_model=List[Dict[str, Any]])
async def query_experiments(
    status: Optional[ExperimentStatus] = None,
    experiment_type: Optional[ExperimentType] = None,
    target_components: Optional[str] = Query(None, description="Comma-separated list of component IDs"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags"),
    start_after: Optional[str] = None,
    start_before: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    experiment_framework = Depends(get_experiment_framework)
):
    """Query experiments with filtering."""
    try:
        # Parse lists from comma-separated strings
        target_component_list = target_components.split(",") if target_components else None
        tag_list = tags.split(",") if tags else None
        
        # Create query object
        query = ExperimentQuery(
            status=status,
            experiment_type=experiment_type,
            target_components=target_component_list,
            tags=tag_list,
            start_after=start_after,
            start_before=start_before,
            limit=limit,
            offset=offset
        )
        
        # Execute query
        experiments = await experiment_framework.query_experiments(query)
        return experiments
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query experiments: {str(e)}"
        )

@router.get("/{experiment_id}", response_model=Dict[str, Any])
async def get_experiment(
    experiment_id: str = Path(..., description="ID of the experiment"),
    experiment_framework = Depends(get_experiment_framework)
):
    """Get details of a specific experiment."""
    try:
        experiment = await experiment_framework.get_experiment(experiment_id)
        if experiment:
            return experiment
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Experiment not found: {experiment_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get experiment: {str(e)}"
        )

@router.put("/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(
    experiment_update: ExperimentUpdate,
    experiment_id: str = Path(..., description="ID of the experiment"),
    experiment_framework = Depends(get_experiment_framework)
):
    """Update an existing experiment."""
    try:
        success = await experiment_framework.update_experiment(
            experiment_id=experiment_id,
            updates=experiment_update.dict(exclude_unset=True)
        )
        
        if success:
            return ExperimentResponse(
                success=True,
                message="Experiment updated successfully"
            )
        else:
            return ExperimentResponse(
                success=False,
                message="Failed to update experiment"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update experiment: {str(e)}"
        )

@router.post("/{experiment_id}/start", response_model=ExperimentResponse)
async def start_experiment(
    experiment_id: str = Path(..., description="ID of the experiment"),
    experiment_framework = Depends(get_experiment_framework)
):
    """Start an experiment."""
    try:
        success = await experiment_framework.start_experiment(experiment_id)
        
        if success:
            return ExperimentResponse(
                success=True,
                message="Experiment started successfully"
            )
        else:
            return ExperimentResponse(
                success=False,
                message="Failed to start experiment"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start experiment: {str(e)}"
        )

@router.post("/{experiment_id}/stop", response_model=ExperimentResponse)
async def stop_experiment(
    experiment_id: str = Path(..., description="ID of the experiment"),
    experiment_framework = Depends(get_experiment_framework)
):
    """Stop an experiment."""
    try:
        success = await experiment_framework.stop_experiment(experiment_id)
        
        if success:
            return ExperimentResponse(
                success=True,
                message="Experiment stopped successfully"
            )
        else:
            return ExperimentResponse(
                success=False,
                message="Failed to stop experiment"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop experiment: {str(e)}"
        )

@router.post("/{experiment_id}/analyze", response_model=ExperimentResponse)
async def analyze_experiment(
    experiment_id: str = Path(..., description="ID of the experiment"),
    experiment_framework = Depends(get_experiment_framework)
):
    """Analyze an experiment's results."""
    try:
        success = await experiment_framework.analyze_experiment(experiment_id)
        
        if success:
            return ExperimentResponse(
                success=True,
                message="Experiment analysis started successfully"
            )
        else:
            return ExperimentResponse(
                success=False,
                message="Failed to start experiment analysis"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze experiment: {str(e)}"
        )

@router.get("/{experiment_id}/results", response_model=ExperimentResult)
async def get_experiment_results(
    experiment_id: str = Path(..., description="ID of the experiment"),
    experiment_framework = Depends(get_experiment_framework)
):
    """Get results of a completed experiment."""
    try:
        results = await experiment_framework.get_experiment_results(experiment_id)
        
        if results:
            return results
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Experiment results not found: {experiment_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get experiment results: {str(e)}"
        )

@router.delete("/{experiment_id}", response_model=ExperimentResponse)
async def delete_experiment(
    experiment_id: str = Path(..., description="ID of the experiment"),
    experiment_framework = Depends(get_experiment_framework)
):
    """Delete an experiment."""
    try:
        success = await experiment_framework.delete_experiment(experiment_id)
        
        if success:
            return ExperimentResponse(
                success=True,
                message="Experiment deleted successfully"
            )
        else:
            return ExperimentResponse(
                success=False,
                message="Failed to delete experiment"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete experiment: {str(e)}"
        )