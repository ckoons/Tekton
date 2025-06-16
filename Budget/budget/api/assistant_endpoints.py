"""
Budget LLM Assistant API Endpoints

This module provides API endpoints for the Budget LLM Assistant,
which uses LLMs to provide budget analysis and recommendations.
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field

# Add the parent directory to sys.path to ensure package imports work correctly
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Try to import debug_utils from shared if available
try:
    from shared.debug.debug_utils import debug_log, log_function
except ImportError:
    # Create a simple fallback if shared module is not available
    class DebugLog:
        def __getattr__(self, name):
            def dummy_log(*args, **kwargs):
                pass
            return dummy_log
    debug_log = DebugLog()
    
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Import budget models
from budget.data.models import BudgetPeriod, BudgetTier
from budget.service.assistant import create_budget_assistant

# API Router
router = APIRouter(prefix="/assistant", tags=["assistant"])

# Request and Response Models
class AnalysisRequest(BaseModel):
    """Request model for budget analysis."""
    period: BudgetPeriod = Field(default=BudgetPeriod.DAILY, description="Budget period to analyze")
    days: int = Field(default=30, description="Number of days to analyze", ge=1, le=365)
    include_raw_data: bool = Field(default=False, description="Include raw data in response")

class OptimizationRequest(BaseModel):
    """Request model for optimization recommendations."""
    period: BudgetPeriod = Field(default=BudgetPeriod.DAILY, description="Budget period to analyze")
    days: int = Field(default=30, description="Number of days to analyze", ge=1, le=365)
    include_raw_data: bool = Field(default=False, description="Include raw data in response")

class ModelRecommendationRequest(BaseModel):
    """Request model for model recommendations."""
    task_description: str = Field(..., description="Description of the task to perform")
    input_length: int = Field(..., description="Expected input length in tokens", ge=1)
    output_length: int = Field(..., description="Expected output length in tokens", ge=1)
    usage_frequency: int = Field(..., description="Number of times the task will be performed daily", ge=1)
    budget_limit: float = Field(..., description="Maximum budget in USD", gt=0)
    priority_areas: str = Field(..., description="Areas of importance (e.g., accuracy, speed)")
    include_raw_data: bool = Field(default=False, description="Include raw data in response")

class AnalysisResponse(BaseModel):
    """Response model for budget analysis."""
    success: bool = Field(..., description="Whether the request was successful")
    analysis: Optional[str] = Field(None, description="Budget analysis text")
    error: Optional[str] = Field(None, description="Error message if any")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw data used for analysis")

class OptimizationResponse(BaseModel):
    """Response model for optimization recommendations."""
    success: bool = Field(..., description="Whether the request was successful")
    recommendations: Optional[str] = Field(None, description="Optimization recommendations text")
    error: Optional[str] = Field(None, description="Error message if any")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw data used for recommendations")

class ModelRecommendationResponse(BaseModel):
    """Response model for model recommendations."""
    success: bool = Field(..., description="Whether the request was successful")
    recommendations: Optional[str] = Field(None, description="Model recommendations text")
    error: Optional[str] = Field(None, description="Error message if any")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw data used for recommendations")

# Dependency to get budget assistant
async def get_assistant():
    """
    Dependency to get budget assistant.
    
    Returns:
        BudgetAssistant: Budget assistant instance
    """
    assistant = await create_budget_assistant()
    if not assistant:
        raise HTTPException(status_code=500, detail="Failed to create budget assistant")
    return assistant

# Endpoints
@router.post("/analyze", response_model=AnalysisResponse)
@log_function()
async def analyze_budget(
    request: AnalysisRequest,
    assistant = Depends(get_assistant)
):
    """
    Analyze budget usage patterns and provide insights.
    
    Args:
        request: Analysis request
        assistant: Budget assistant instance
        
    Returns:
        AnalysisResponse: Analysis response
    """
    debug_log.info("budget_assistant_api", "Analyzing budget")
    
    try:
        result = await assistant.analyze_budget(
            period=request.period,
            days=request.days
        )
        
        response = AnalysisResponse(
            success=result.get("success", False),
            analysis=result.get("analysis"),
            error=result.get("error")
        )
        
        if request.include_raw_data and "raw_data" in result:
            response.raw_data = result["raw_data"]
        
        return response
    
    except Exception as e:
        debug_log.error("budget_assistant_api", f"Error analyzing budget: {str(e)}")
        return AnalysisResponse(
            success=False,
            error=f"Error analyzing budget: {str(e)}"
        )

@router.post("/optimize", response_model=OptimizationResponse)
@log_function()
async def get_optimization_recommendations(
    request: OptimizationRequest,
    assistant = Depends(get_assistant)
):
    """
    Get cost optimization recommendations.
    
    Args:
        request: Optimization request
        assistant: Budget assistant instance
        
    Returns:
        OptimizationResponse: Optimization response
    """
    debug_log.info("budget_assistant_api", "Getting optimization recommendations")
    
    try:
        result = await assistant.get_optimization_recommendations(
            period=request.period,
            days=request.days
        )
        
        response = OptimizationResponse(
            success=result.get("success", False),
            recommendations=result.get("recommendations"),
            error=result.get("error")
        )
        
        if request.include_raw_data and "raw_data" in result:
            response.raw_data = result["raw_data"]
        
        return response
    
    except Exception as e:
        debug_log.error("budget_assistant_api", f"Error getting optimization recommendations: {str(e)}")
        return OptimizationResponse(
            success=False,
            error=f"Error getting optimization recommendations: {str(e)}"
        )

@router.post("/recommend-model", response_model=ModelRecommendationResponse)
@log_function()
async def recommend_model(
    request: ModelRecommendationRequest,
    assistant = Depends(get_assistant)
):
    """
    Recommend the best model for a specific task.
    
    Args:
        request: Model recommendation request
        assistant: Budget assistant instance
        
    Returns:
        ModelRecommendationResponse: Model recommendation response
    """
    debug_log.info("budget_assistant_api", "Getting model recommendations")
    
    try:
        result = await assistant.recommend_model(
            task_description=request.task_description,
            input_length=request.input_length,
            output_length=request.output_length,
            usage_frequency=request.usage_frequency,
            budget_limit=request.budget_limit,
            priority_areas=request.priority_areas
        )
        
        response = ModelRecommendationResponse(
            success=result.get("success", False),
            recommendations=result.get("recommendations"),
            error=result.get("error")
        )
        
        if request.include_raw_data and "raw_data" in result:
            response.raw_data = result["raw_data"]
        
        return response
    
    except Exception as e:
        debug_log.error("budget_assistant_api", f"Error getting model recommendations: {str(e)}")
        return ModelRecommendationResponse(
            success=False,
            error=f"Error getting model recommendations: {str(e)}"
        )