"""
Model Management API Endpoints for Rhetor.
These endpoints power the UI matrix and provide model selection for all components.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Literal
import logging

from rhetor.core.model_registry import (
    ModelRegistry,
    get_model_registry,
    CapabilityType,
    ModelInfo
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/models", tags=["Model Management"])


# Request/Response Models

class ModelAssignment(BaseModel):
    """Model assignment for a component and capability."""
    component: str = Field(..., description="Component name (e.g., ergon)")
    capability: CapabilityType = Field(..., description="Capability (code, planning, reasoning, chat)")
    model_id: str = Field(..., description="Model ID or 'use_default'")


class DefaultAssignment(BaseModel):
    """Default model assignment for a capability."""
    capability: CapabilityType = Field(..., description="Capability type")
    model_id: str = Field(..., description="Model ID")


class ModelSelectionRequest(BaseModel):
    """Request for model selection."""
    component: str = Field(..., description="Component requesting model")
    capability: CapabilityType = Field(..., description="Required capability")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Additional requirements")


class ModelInfoResponse(BaseModel):
    """Response with model information."""
    id: str
    provider: str
    name: str
    aliases: List[str]
    capabilities: List[str]
    context_window: int
    max_output: int
    deprecated: bool
    fallback: Optional[str] = None


class AssignmentMatrixResponse(BaseModel):
    """Complete assignment matrix response."""
    defaults: Dict[str, str]
    components: Dict[str, Dict[str, str]]


class ProviderStatusResponse(BaseModel):
    """Provider status information."""
    name: str
    status: str
    model_count: int


class ValidationIssue(BaseModel):
    """Validation issue found in assignments."""
    issue: str
    severity: Literal["error", "warning"]


# Dependency to get registry
async def get_registry() -> ModelRegistry:
    """Dependency to get model registry."""
    return get_model_registry()


# Endpoints

@router.get("/", summary="Get available models")
async def get_models(
    provider: Optional[str] = None,
    capability: Optional[str] = None,
    include_deprecated: bool = False,
    registry: ModelRegistry = Depends(get_registry)
) -> List[ModelInfoResponse]:
    """
    Get all available models with optional filtering.
    
    Args:
        provider: Filter by provider (anthropic, openai, ollama)
        capability: Filter by capability (code, planning, reasoning, chat)
        include_deprecated: Include deprecated models
    """
    models = registry.get_available_models(provider, capability, include_deprecated)
    return [
        ModelInfoResponse(
            id=m.id,
            provider=m.provider,
            name=m.name,
            aliases=m.aliases,
            capabilities=m.capabilities,
            context_window=m.context_window,
            max_output=m.max_output,
            deprecated=m.deprecated,
            fallback=m.fallback
        )
        for m in models
    ]


@router.get("/providers", summary="Get provider status")
async def get_providers(
    registry: ModelRegistry = Depends(get_registry)
) -> Dict[str, ProviderStatusResponse]:
    """Get status information for all providers."""
    providers = registry.get_providers()
    return {
        name: ProviderStatusResponse(
            name=info["name"],
            status=info["status"],
            model_count=info["model_count"]
        )
        for name, info in providers.items()
    }


@router.get("/assignments", summary="Get assignment matrix")
async def get_assignments(
    registry: ModelRegistry = Depends(get_registry)
) -> AssignmentMatrixResponse:
    """Get the complete model assignment matrix for UI display."""
    matrix = registry.get_assignments_matrix()
    return AssignmentMatrixResponse(
        defaults=matrix["defaults"],
        components=matrix["components"]
    )


@router.post("/assignments/component", summary="Update component assignment")
async def update_component_assignment(
    assignment: ModelAssignment,
    registry: ModelRegistry = Depends(get_registry)
) -> Dict[str, str]:
    """
    Update model assignment for a specific component and capability.
    This is called when the UI matrix is changed.
    """
    success = registry.update_component_assignment(
        assignment.component,
        assignment.capability,
        assignment.model_id
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update assignment")
    
    return {"status": "success", "message": f"Updated {assignment.component}/{assignment.capability}"}


@router.post("/assignments/default", summary="Update default assignment")
async def update_default_assignment(
    assignment: DefaultAssignment,
    registry: ModelRegistry = Depends(get_registry)
) -> Dict[str, str]:
    """Update default model assignment for a capability."""
    success = registry.update_default_assignment(
        assignment.capability,
        assignment.model_id
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update default")
    
    return {"status": "success", "message": f"Updated default for {assignment.capability}"}


@router.post("/select", summary="Select model for component")
async def select_model(
    request: ModelSelectionRequest,
    registry: ModelRegistry = Depends(get_registry)
) -> Dict[str, Any]:
    """
    Select the appropriate model for a component and capability.
    This is the main endpoint that components call to get their model.
    """
    model_id = registry.get_model_for_component(
        request.component,
        request.capability
    )
    
    if not model_id:
        # Try automatic selection
        model_id = registry.select_best_model(
            request.capability,
            request.requirements
        )
    
    if not model_id:
        raise HTTPException(status_code=404, detail="No suitable model found")
    
    # Get full model info
    model_info = registry.get_model_info(model_id)
    if not model_info:
        raise HTTPException(status_code=500, detail="Model info not found")
    
    return {
        "model_id": model_id,
        "provider": model_info.provider,
        "name": model_info.name,
        "context_window": model_info.context_window,
        "max_output": model_info.max_output
    }


@router.get("/resolve/{alias}", summary="Resolve model alias")
async def resolve_alias(
    alias: str,
    registry: ModelRegistry = Depends(get_registry)
) -> Dict[str, str]:
    """Resolve a model alias to its actual model ID."""
    model_id = registry.resolve_model_alias(alias)
    
    if not model_id:
        raise HTTPException(status_code=404, detail=f"Alias '{alias}' not found")
    
    return {"alias": alias, "model_id": model_id}


@router.get("/info/{model_id}", summary="Get model information")
async def get_model_info(
    model_id: str,
    registry: ModelRegistry = Depends(get_registry)
) -> ModelInfoResponse:
    """Get complete information about a specific model."""
    model = registry.get_model_info(model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    
    return ModelInfoResponse(
        id=model.id,
        provider=model.provider,
        name=model.name,
        aliases=model.aliases,
        capabilities=model.capabilities,
        context_window=model.context_window,
        max_output=model.max_output,
        deprecated=model.deprecated,
        fallback=model.fallback
    )


@router.post("/validate", summary="Validate all assignments")
async def validate_assignments(
    registry: ModelRegistry = Depends(get_registry)
) -> List[ValidationIssue]:
    """
    Validate all current model assignments.
    Returns list of issues found (empty if all valid).
    """
    issues = registry.validate_all_assignments()
    
    # Convert to structured response
    validation_issues = []
    for issue in issues:
        severity = "error" if "not found" in issue else "warning"
        validation_issues.append(ValidationIssue(issue=issue, severity=severity))
    
    return validation_issues


@router.post("/reload", summary="Reload configurations")
async def reload_configurations(
    registry: ModelRegistry = Depends(get_registry)
) -> Dict[str, str]:
    """Reload model configurations from disk."""
    registry.reload_configurations()
    return {"status": "success", "message": "Configurations reloaded"}


# Legacy compatibility endpoint
@router.get("/legacy/get_model", summary="Legacy model selection")
async def legacy_get_model(
    component: str,
    task_type: Optional[str] = "general",
    registry: ModelRegistry = Depends(get_registry)
) -> Dict[str, str]:
    """
    Legacy endpoint for components still using old model selection.
    Maps old task_type to new capability system.
    """
    # Map legacy task types to capabilities
    capability_map = {
        "code": "code",
        "coding": "code",
        "planning": "planning",
        "plan": "planning",
        "reasoning": "reasoning",
        "analysis": "reasoning",
        "chat": "chat",
        "conversation": "chat",
        "general": "reasoning"  # Default to reasoning
    }
    
    capability = capability_map.get(task_type.lower(), "reasoning")
    
    model_id = registry.get_model_for_component(component, capability)
    if not model_id:
        model_id = registry.select_best_model(capability)
    
    if not model_id:
        raise HTTPException(status_code=404, detail="No model available")
    
    return {
        "model": model_id,
        "component": component,
        "capability": capability
    }