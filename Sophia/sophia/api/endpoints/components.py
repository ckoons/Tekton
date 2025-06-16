"""
Components API endpoints for Sophia.

This module defines the API endpoints for component registration and analysis in Sophia.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from datetime import datetime

from sophia.core.ml_engine import get_ml_engine
from sophia.models.component import (
    ComponentRegister,
    ComponentUpdate,
    ComponentQuery,
    ComponentResponse,
    ComponentPerformanceAnalysis,
    ComponentInteractionAnalysis,
    ComponentType,
    PerformanceCategory
)

# Create router
router = APIRouter()

# ------------------------
# Components API Routes
# ------------------------

@router.post("/register", response_model=ComponentResponse)
async def register_component(
    component: ComponentRegister,
    ml_engine = Depends(get_ml_engine)
):
    """Register a component with Sophia."""
    try:
        success = await ml_engine.register_component(
            component_id=component.component_id,
            name=component.name,
            description=component.description,
            component_type=component.component_type,
            version=component.version,
            api_endpoints=component.api_endpoints,
            capabilities=component.capabilities,
            dependencies=component.dependencies,
            metrics_provided=component.metrics_provided,
            port=component.port,
            tags=component.tags
        )
        
        if success:
            return ComponentResponse(
                success=True,
                message=f"Component registered successfully: {component.component_id}"
            )
        else:
            return ComponentResponse(
                success=False,
                message="Failed to register component"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register component: {str(e)}"
        )

@router.get("/", response_model=List[Dict[str, Any]])
async def query_components(
    component_type: Optional[ComponentType] = None,
    capabilities: Optional[str] = Query(None, description="Comma-separated list of capabilities"),
    dependencies: Optional[str] = Query(None, description="Comma-separated list of dependencies"),
    metrics_provided: Optional[str] = Query(None, description="Comma-separated list of metrics"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags"),
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    ml_engine = Depends(get_ml_engine)
):
    """Query registered components with filtering."""
    try:
        # Parse lists from comma-separated strings
        capabilities_list = capabilities.split(",") if capabilities else None
        dependencies_list = dependencies.split(",") if dependencies else None
        metrics_list = metrics_provided.split(",") if metrics_provided else None
        tag_list = tags.split(",") if tags else None
        
        # Create query object
        query = ComponentQuery(
            component_type=component_type,
            capabilities=capabilities_list,
            dependencies=dependencies_list,
            metrics_provided=metrics_list,
            tags=tag_list,
            status=status,
            limit=limit,
            offset=offset
        )
        
        # Execute query
        components = await ml_engine.query_components(query)
        return components
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query components: {str(e)}"
        )

@router.get("/{component_id}", response_model=Dict[str, Any])
async def get_component(
    component_id: str = Path(..., description="ID of the component"),
    ml_engine = Depends(get_ml_engine)
):
    """Get details of a specific registered component."""
    try:
        component = await ml_engine.get_component(component_id)
        
        if component:
            return component
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Component not found: {component_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get component: {str(e)}"
        )

@router.put("/{component_id}", response_model=ComponentResponse)
async def update_component(
    component_update: ComponentUpdate,
    component_id: str = Path(..., description="ID of the component"),
    ml_engine = Depends(get_ml_engine)
):
    """Update a registered component."""
    try:
        success = await ml_engine.update_component(
            component_id=component_id,
            updates=component_update.dict(exclude_unset=True)
        )
        
        if success:
            return ComponentResponse(
                success=True,
                message="Component updated successfully"
            )
        else:
            return ComponentResponse(
                success=False,
                message="Failed to update component"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update component: {str(e)}"
        )

@router.get("/{component_id}/performance", response_model=ComponentPerformanceAnalysis)
async def analyze_component_performance(
    component_id: str = Path(..., description="ID of the component"),
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    metrics: Optional[str] = Query(None, description="Comma-separated list of metrics to include"),
    ml_engine = Depends(get_ml_engine)
):
    """Analyze the performance of a component."""
    try:
        # Parse metrics list
        metrics_list = metrics.split(",") if metrics else None
        
        analysis = await ml_engine.analyze_component_performance(
            component_id=component_id,
            start_time=start_time,
            end_time=end_time,
            metrics=metrics_list
        )
        
        if analysis:
            return analysis
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Performance analysis not available for component: {component_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze component performance: {str(e)}"
        )

@router.post("/interaction", response_model=ComponentInteractionAnalysis)
async def analyze_component_interaction(
    component_ids: List[str],
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    ml_engine = Depends(get_ml_engine)
):
    """Analyze the interaction between components."""
    try:
        if len(component_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least two components must be provided for interaction analysis"
            )
        
        analysis = await ml_engine.analyze_component_interaction(
            component_ids=component_ids,
            start_time=start_time,
            end_time=end_time
        )
        
        if analysis:
            return analysis
        else:
            raise HTTPException(
                status_code=404,
                detail="Component interaction analysis not available"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze component interaction: {str(e)}"
        )

@router.get("/{component_id}/dependencies", response_model=Dict[str, Any])
async def analyze_component_dependencies(
    component_id: str = Path(..., description="ID of the component"),
    include_indirect: bool = False,
    ml_engine = Depends(get_ml_engine)
):
    """Analyze the dependencies of a component."""
    try:
        analysis = await ml_engine.analyze_component_dependencies(
            component_id=component_id,
            include_indirect=include_indirect
        )
        
        if analysis:
            return analysis
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Dependency analysis not available for component: {component_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze component dependencies: {str(e)}"
        )

@router.delete("/{component_id}", response_model=ComponentResponse)
async def unregister_component(
    component_id: str = Path(..., description="ID of the component"),
    ml_engine = Depends(get_ml_engine)
):
    """Unregister a component from Sophia."""
    try:
        success = await ml_engine.unregister_component(component_id)
        
        if success:
            return ComponentResponse(
                success=True,
                message="Component unregistered successfully"
            )
        else:
            return ComponentResponse(
                success=False,
                message="Failed to unregister component"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to unregister component: {str(e)}"
        )