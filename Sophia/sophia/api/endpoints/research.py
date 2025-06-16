"""
Research API endpoints for Sophia.

This module defines the API endpoints for AI research capabilities in Sophia.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from datetime import datetime

from sophia.core.ml_engine import get_ml_engine
from sophia.models.research import (
    ResearchProjectCreate,
    ResearchProjectUpdate,
    ResearchProjectQuery,
    ResearchProjectResponse,
    CSAConfigCreate,
    CSAResult,
    CatastropheTheoryAnalysisCreate,
    CatastropheTheoryResult,
    ResearchApproach,
    ResearchStatus
)

# Create router
router = APIRouter()

# ------------------------
# Research API Routes
# ------------------------

@router.post("/projects", response_model=ResearchProjectResponse)
async def create_research_project(
    project: ResearchProjectCreate,
    ml_engine = Depends(get_ml_engine)
):
    """Create a new research project."""
    try:
        project_id = await ml_engine.create_research_project(
            title=project.title,
            description=project.description,
            approach=project.approach,
            research_questions=project.research_questions,
            hypothesis=project.hypothesis,
            target_components=project.target_components,
            data_requirements=project.data_requirements,
            expected_outcomes=project.expected_outcomes,
            estimated_duration=project.estimated_duration,
            tags=project.tags
        )
        
        return ResearchProjectResponse(
            success=True,
            message="Research project created successfully",
            data={"project_id": project_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create research project: {str(e)}"
        )

@router.get("/projects", response_model=List[Dict[str, Any]])
async def query_research_projects(
    status: Optional[ResearchStatus] = None,
    approach: Optional[ResearchApproach] = None,
    target_components: Optional[str] = Query(None, description="Comma-separated list of component IDs"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags"),
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    ml_engine = Depends(get_ml_engine)
):
    """Query research projects with filtering."""
    try:
        # Parse lists from comma-separated strings
        target_component_list = target_components.split(",") if target_components else None
        tag_list = tags.split(",") if tags else None
        
        # Create query object
        query = ResearchProjectQuery(
            status=status,
            approach=approach,
            target_components=target_component_list,
            tags=tag_list,
            created_after=created_after,
            created_before=created_before,
            limit=limit,
            offset=offset
        )
        
        # Execute query
        projects = await ml_engine.query_research_projects(query)
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query research projects: {str(e)}"
        )

@router.get("/projects/{project_id}", response_model=Dict[str, Any])
async def get_research_project(
    project_id: str = Path(..., description="ID of the research project"),
    ml_engine = Depends(get_ml_engine)
):
    """Get details of a specific research project."""
    try:
        project = await ml_engine.get_research_project(project_id)
        
        if project:
            return project
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Research project not found: {project_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get research project: {str(e)}"
        )

@router.put("/projects/{project_id}", response_model=ResearchProjectResponse)
async def update_research_project(
    project_update: ResearchProjectUpdate,
    project_id: str = Path(..., description="ID of the research project"),
    ml_engine = Depends(get_ml_engine)
):
    """Update an existing research project."""
    try:
        success = await ml_engine.update_research_project(
            project_id=project_id,
            updates=project_update.dict(exclude_unset=True)
        )
        
        if success:
            return ResearchProjectResponse(
                success=True,
                message="Research project updated successfully"
            )
        else:
            return ResearchProjectResponse(
                success=False,
                message="Failed to update research project"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update research project: {str(e)}"
        )

@router.post("/csa", response_model=ResearchProjectResponse)
async def create_csa_analysis(
    config: CSAConfigCreate,
    ml_engine = Depends(get_ml_engine)
):
    """Create a new Computational Spectral Analysis."""
    try:
        analysis_id = await ml_engine.create_csa_analysis(
            network_id=config.network_id,
            layer_ids=config.layer_ids,
            activation_samples=config.activation_samples,
            input_data_source=config.input_data_source,
            analysis_dimensions=config.analysis_dimensions,
            spectral_methods=config.spectral_methods,
            visualization_options=config.visualization_options
        )
        
        return ResearchProjectResponse(
            success=True,
            message="CSA analysis created successfully",
            data={"analysis_id": analysis_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create CSA analysis: {str(e)}"
        )

@router.get("/csa/{analysis_id}", response_model=CSAResult)
async def get_csa_result(
    analysis_id: str = Path(..., description="ID of the CSA analysis"),
    ml_engine = Depends(get_ml_engine)
):
    """Get results of a Computational Spectral Analysis."""
    try:
        result = await ml_engine.get_csa_result(analysis_id)
        
        if result:
            return result
        else:
            raise HTTPException(
                status_code=404,
                detail=f"CSA analysis result not found: {analysis_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get CSA analysis result: {str(e)}"
        )

@router.post("/catastrophe-theory", response_model=ResearchProjectResponse)
async def create_catastrophe_theory_analysis(
    config: CatastropheTheoryAnalysisCreate,
    ml_engine = Depends(get_ml_engine)
):
    """Create a new Catastrophe Theory analysis."""
    try:
        analysis_id = await ml_engine.create_catastrophe_theory_analysis(
            capability_dimension=config.capability_dimension,
            component_ids=config.component_ids,
            control_parameters=config.control_parameters,
            parameter_ranges=config.parameter_ranges,
            measurement_metrics=config.measurement_metrics,
            sampling_strategy=config.sampling_strategy,
            analysis_methods=config.analysis_methods
        )
        
        return ResearchProjectResponse(
            success=True,
            message="Catastrophe Theory analysis created successfully",
            data={"analysis_id": analysis_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Catastrophe Theory analysis: {str(e)}"
        )

@router.get("/catastrophe-theory/{analysis_id}", response_model=CatastropheTheoryResult)
async def get_catastrophe_theory_result(
    analysis_id: str = Path(..., description="ID of the Catastrophe Theory analysis"),
    ml_engine = Depends(get_ml_engine)
):
    """Get results of a Catastrophe Theory analysis."""
    try:
        result = await ml_engine.get_catastrophe_theory_result(analysis_id)
        
        if result:
            return result
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Catastrophe Theory analysis result not found: {analysis_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Catastrophe Theory analysis result: {str(e)}"
        )

@router.get("/approaches", response_model=Dict[str, Dict[str, Any]])
async def get_research_approaches(
    ml_engine = Depends(get_ml_engine)
):
    """Get information about all research approaches."""
    try:
        return await ml_engine.get_research_approaches()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get research approaches: {str(e)}"
        )

@router.delete("/projects/{project_id}", response_model=ResearchProjectResponse)
async def delete_research_project(
    project_id: str = Path(..., description="ID of the research project"),
    ml_engine = Depends(get_ml_engine)
):
    """Delete a research project."""
    try:
        success = await ml_engine.delete_research_project(project_id)
        
        if success:
            return ResearchProjectResponse(
                success=True,
                message="Research project deleted successfully"
            )
        else:
            return ResearchProjectResponse(
                success=False,
                message="Failed to delete research project"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete research project: {str(e)}"
        )