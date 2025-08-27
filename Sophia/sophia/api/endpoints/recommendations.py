"""
Recommendations API endpoints for Sophia.

This module defines the API endpoints for managing recommendations in Sophia.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from datetime import datetime

from sophia.core.recommendation_system import get_recommendation_system
from sophia.models.recommendation import (
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationQuery,
    RecommendationResponse,
    RecommendationVerification,
    RecommendationStatus,
    RecommendationPriority,
    RecommendationType
)

# Create router
router = APIRouter()

# ------------------------
# Recommendations API Routes
# ------------------------

@router.post("/llm/analyze", response_model=Dict[str, Any])
async def analyze_with_llm(
    analysis_data: Dict[str, Any],
    component_id: Optional[str] = Query(None, description="Optional component ID to focus analysis on"),
    llm_adapter = Depends(get_llm_adapter)
):
    """
    Analyze data with LLM to generate insights.
    Useful for getting deeper understanding of metrics or patterns.
    """
    try:
        analysis_result = await # llm_adapter.analyze_metrics(
            metrics_data=analysis_data,
            component_id=component_id
        )
        return analysis_result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze with LLM: {str(e)}"
        )

@router.post("/llm/generate", response_model=List[Dict[str, Any]])
async def generate_recommendations_with_llm(
    analysis_results: Dict[str, Any],
    component_id: Optional[str] = Query(None, description="Optional component ID to focus recommendations on"),
    count: int = Query(3, description="Number of recommendations to generate"),
    llm_adapter = Depends(get_llm_adapter)
):
    """
    Generate recommendations using LLM based on analysis results.
    Produces structured, actionable recommendations with implementation steps.
    """
    try:
        recommendations = await # llm_adapter.generate_recommendations(
            analysis_results=analysis_results,
            target_component=component_id,
            count=count
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations with LLM: {str(e)}"
        )

@router.post("/generate/component/{component_id}", response_model=RecommendationResponse)
async def generate_component_recommendations(
    component_id: str = Path(..., description="ID of the component to analyze"),
    time_window: str = Query("7d", description="Time window for analysis (e.g., 1h, 24h, 7d)"),
    use_llm: bool = Query(True, description="Whether to use LLM for enhanced recommendations"),
    recommendation_system = Depends(get_recommendation_system)
):
    """
    Analyze a component and automatically generate recommendations.
    Integrates rule-based and LLM-powered recommendation generation.
    """
    try:
        recommendations = await recommendation_system.generate_recommendations_from_analysis(
            component_id=component_id,
            time_window=time_window,
            use_llm=use_llm
        )
        
        return RecommendationResponse(
            success=True,
            message=f"Generated {len(recommendations)} recommendations for component {component_id}",
            data={"recommendations": recommendations, "count": len(recommendations)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate component recommendations: {str(e)}"
        )

@router.post("/", response_model=RecommendationResponse)
async def create_recommendation(
    recommendation: RecommendationCreate,
    recommendation_system = Depends(get_recommendation_system)
):
    """Create a new recommendation."""
    try:
        recommendation_id = await recommendation_system.create_recommendation(
            title=recommendation.title,
            description=recommendation.description,
            recommendation_type=recommendation.recommendation_type,
            target_components=recommendation.target_components,
            priority=recommendation.priority,
            rationale=recommendation.rationale,
            expected_impact=recommendation.expected_impact,
            implementation_complexity=recommendation.implementation_complexity,
            supporting_evidence=recommendation.supporting_evidence,
            experiment_ids=recommendation.experiment_ids,
            tags=recommendation.tags
        )
        
        return RecommendationResponse(
            success=True,
            message="Recommendation created successfully",
            data={"recommendation_id": recommendation_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create recommendation: {str(e)}"
        )

@router.get("/", response_model=List[Dict[str, Any]])
async def query_recommendations(
    status: Optional[RecommendationStatus] = None,
    recommendation_type: Optional[RecommendationType] = None,
    priority: Optional[RecommendationPriority] = None,
    target_components: Optional[str] = Query(None, description="Comma-separated list of component IDs"),
    experiment_ids: Optional[str] = Query(None, description="Comma-separated list of experiment IDs"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags"),
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    recommendation_system = Depends(get_recommendation_system)
):
    """Query recommendations with filtering."""
    try:
        # Parse lists from comma-separated strings
        target_component_list = target_components.split(",") if target_components else None
        experiment_id_list = experiment_ids.split(",") if experiment_ids else None
        tag_list = tags.split(",") if tags else None
        
        # Create query object
        query = RecommendationQuery(
            status=status,
            recommendation_type=recommendation_type,
            priority=priority,
            target_components=target_component_list,
            experiment_ids=experiment_id_list,
            tags=tag_list,
            created_after=created_after,
            created_before=created_before,
            limit=limit,
            offset=offset
        )
        
        # Execute query
        recommendations = await recommendation_system.query_recommendations(query)
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query recommendations: {str(e)}"
        )

@router.get("/{recommendation_id}", response_model=Dict[str, Any])
async def get_recommendation(
    recommendation_id: str = Path(..., description="ID of the recommendation"),
    recommendation_system = Depends(get_recommendation_system)
):
    """Get details of a specific recommendation."""
    try:
        recommendation = await recommendation_system.get_recommendation(recommendation_id)
        if recommendation:
            return recommendation
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Recommendation not found: {recommendation_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recommendation: {str(e)}"
        )

@router.put("/{recommendation_id}", response_model=RecommendationResponse)
async def update_recommendation(
    recommendation_update: RecommendationUpdate,
    recommendation_id: str = Path(..., description="ID of the recommendation"),
    recommendation_system = Depends(get_recommendation_system)
):
    """Update an existing recommendation."""
    try:
        success = await recommendation_system.update_recommendation(
            recommendation_id=recommendation_id,
            updates=recommendation_update.dict(exclude_unset=True)
        )
        
        if success:
            return RecommendationResponse(
                success=True,
                message="Recommendation updated successfully"
            )
        else:
            return RecommendationResponse(
                success=False,
                message="Failed to update recommendation"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update recommendation: {str(e)}"
        )

@router.post("/{recommendation_id}/status/{status}", response_model=RecommendationResponse)
async def update_recommendation_status(
    recommendation_id: str = Path(..., description="ID of the recommendation"),
    status: RecommendationStatus = Path(..., description="New status for the recommendation"),
    notes: Optional[str] = None,
    recommendation_system = Depends(get_recommendation_system)
):
    """Update the status of a recommendation."""
    try:
        success = await recommendation_system.update_recommendation_status(
            recommendation_id=recommendation_id,
            status=status,
            notes=notes
        )
        
        if success:
            return RecommendationResponse(
                success=True,
                message=f"Recommendation status updated to {status}"
            )
        else:
            return RecommendationResponse(
                success=False,
                message="Failed to update recommendation status"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update recommendation status: {str(e)}"
        )

@router.post("/{recommendation_id}/verify", response_model=RecommendationResponse)
async def verify_recommendation_implementation(
    verification: RecommendationVerification,
    recommendation_id: str = Path(..., description="ID of the recommendation"),
    recommendation_system = Depends(get_recommendation_system)
):
    """Verify the implementation of a recommendation."""
    try:
        if verification.recommendation_id != recommendation_id:
            raise HTTPException(
                status_code=400,
                detail="Recommendation ID in path and body must match"
            )
        
        success = await recommendation_system.verify_recommendation(
            recommendation_id=recommendation_id,
            verification_metrics=verification.verification_metrics,
            observed_impact=verification.observed_impact,
            verification_status=verification.verification_status,
            verification_notes=verification.verification_notes,
            follow_up_actions=verification.follow_up_actions
        )
        
        if success:
            return RecommendationResponse(
                success=True,
                message="Recommendation verification completed successfully"
            )
        else:
            return RecommendationResponse(
                success=False,
                message="Failed to verify recommendation"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify recommendation: {str(e)}"
        )

@router.get("/component/{component_id}", response_model=List[Dict[str, Any]])
async def get_recommendations_for_component(
    component_id: str = Path(..., description="ID of the component"),
    status: Optional[RecommendationStatus] = None,
    priority: Optional[RecommendationPriority] = None,
    limit: int = 100,
    offset: int = 0,
    recommendation_system = Depends(get_recommendation_system)
):
    """Get recommendations for a specific component."""
    try:
        recommendations = await recommendation_system.get_recommendations_for_component(
            component_id=component_id,
            status=status,
            priority=priority,
            limit=limit,
            offset=offset
        )
        
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recommendations for component: {str(e)}"
        )

@router.delete("/{recommendation_id}", response_model=RecommendationResponse)
async def delete_recommendation(
    recommendation_id: str = Path(..., description="ID of the recommendation"),
    recommendation_system = Depends(get_recommendation_system)
):
    """Delete a recommendation."""
    try:
        success = await recommendation_system.delete_recommendation(recommendation_id)
        
        if success:
            return RecommendationResponse(
                success=True,
                message="Recommendation deleted successfully"
            )
        else:
            return RecommendationResponse(
                success=False,
                message="Failed to delete recommendation"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete recommendation: {str(e)}"
        )