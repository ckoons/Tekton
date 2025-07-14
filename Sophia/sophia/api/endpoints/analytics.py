"""
Advanced Analytics API endpoints for Sophia

This module provides endpoints for accessing Sophia's advanced analytics capabilities.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Body, Path
from pydantic import BaseModel, Field

from sophia.core.analysis_engine import get_analysis_engine
from sophia.models.analytics import (
    PatternDetectionRequest,
    PatternDetectionResponse,
    CausalAnalysisRequest,
    CausalAnalysisResponse,
    ComplexEventRequest,
    ComplexEventResponse,
    PredictionRequest,
    PredictionResponse,
    NetworkAnalysisRequest,
    NetworkAnalysisResponse
)

router = APIRouter()


@router.post("/patterns/detect", response_model=PatternDetectionResponse)
async def detect_patterns(
    request: PatternDetectionRequest = Body(
        ...,
        example={
            "component_filter": "sophia",
            "dimensions": ["value", "timestamp", "metric_id"],
            "time_window": "24h"
        }
    )
) -> PatternDetectionResponse:
    """
    Detect multi-dimensional patterns across components and metrics.
    
    This endpoint uses advanced analytics to identify complex patterns
    including clustering, geometric patterns, topological features, and fractals.
    """
    try:
        analysis_engine = await get_analysis_engine()
        
        patterns = await analysis_engine.detect_multi_dimensional_patterns(
            component_filter=request.component_filter,
            dimensions=request.dimensions,
            time_window=request.time_window
        )
        
        return PatternDetectionResponse(
            status="success",
            patterns=patterns,
            analysis_time=datetime.utcnow(),
            pattern_count=len(patterns)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect patterns: {str(e)}"
        )


@router.post("/causality/analyze", response_model=CausalAnalysisResponse)
async def analyze_causality(
    request: CausalAnalysisRequest = Body(
        ...,
        example={
            "target_metric": "perf.response_time",
            "candidate_causes": ["res.cpu_usage", "res.memory_usage", "api.request_count"],
            "time_window": "7d",
            "max_lag": 10
        }
    )
) -> CausalAnalysisResponse:
    """
    Analyze causal relationships between metrics.
    
    This endpoint identifies which metrics causally influence a target metric,
    including the time lag, strength, and mechanism of causation.
    """
    try:
        analysis_engine = await get_analysis_engine()
        
        relationships = await analysis_engine.analyze_causal_relationships(
            target_metric=request.target_metric,
            candidate_causes=request.candidate_causes,
            time_window=request.time_window,
            max_lag=request.max_lag
        )
        
        return CausalAnalysisResponse(
            status="success",
            target_metric=request.target_metric,
            relationships=relationships,
            analysis_time=datetime.utcnow(),
            relationship_count=len(relationships)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze causal relationships: {str(e)}"
        )


@router.post("/events/detect", response_model=ComplexEventResponse)
async def detect_complex_events(
    request: ComplexEventRequest = Body(
        ...,
        example={
            "event_types": ["cascade_failure", "synchronization_event", "emergence_event"],
            "time_window": "24h"
        }
    )
) -> ComplexEventResponse:
    """
    Detect complex multi-component event patterns.
    
    This endpoint identifies complex events that span multiple components,
    including cascading failures, synchronization events, and emergent behaviors.
    """
    try:
        analysis_engine = await get_analysis_engine()
        
        events = await analysis_engine.detect_complex_events(
            event_types=request.event_types,
            time_window=request.time_window
        )
        
        return ComplexEventResponse(
            status="success",
            events=events,
            analysis_time=datetime.utcnow(),
            event_count=len(events)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect complex events: {str(e)}"
        )


@router.post("/predict", response_model=PredictionResponse)
async def predict_metrics(
    request: PredictionRequest = Body(
        ...,
        example={
            "metric_ids": ["perf.response_time", "res.cpu_usage"],
            "prediction_horizon": 24,
            "confidence_level": 0.95
        }
    )
) -> PredictionResponse:
    """
    Generate predictions for specified metrics.
    
    This endpoint uses ensemble methods (ARIMA, LSTM, Prophet) to predict
    future values with confidence intervals.
    """
    try:
        analysis_engine = await get_analysis_engine()
        
        predictions = await analysis_engine.predict_metrics(
            metric_ids=request.metric_ids,
            prediction_horizon=request.prediction_horizon,
            confidence_level=request.confidence_level
        )
        
        return PredictionResponse(
            status="success",
            predictions=predictions,
            analysis_time=datetime.utcnow(),
            prediction_horizon=request.prediction_horizon,
            confidence_level=request.confidence_level
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate predictions: {str(e)}"
        )


@router.post("/network/analyze", response_model=NetworkAnalysisResponse)
async def analyze_network_effects(
    request: NetworkAnalysisRequest = Body(
        ...,
        example={
            "time_window": "24h"
        }
    )
) -> NetworkAnalysisResponse:
    """
    Analyze network effects and information flow between components.
    
    This endpoint analyzes the network structure of component interactions,
    identifying centrality, clustering, bottlenecks, and communities.
    """
    try:
        analysis_engine = await get_analysis_engine()
        
        network_analysis = await analysis_engine.analyze_network_effects(
            time_window=request.time_window
        )
        
        return NetworkAnalysisResponse(
            status="success",
            analysis=network_analysis,
            analysis_time=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze network effects: {str(e)}"
        )


@router.get("/capabilities")
async def get_analytics_capabilities() -> Dict[str, Any]:
    """
    Get information about available analytics capabilities.
    
    Returns details about pattern detection types, causal analysis methods,
    event detection capabilities, and prediction methods.
    """
    return {
        "pattern_detection": {
            "types": ["clustering", "geometric", "topological", "fractal"],
            "dimensions": ["value", "timestamp", "metric_id", "component", "tags"],
            "description": "Detect complex patterns across multiple dimensions"
        },
        "causal_analysis": {
            "methods": ["granger_causality", "transfer_entropy"],
            "mechanisms": ["linear", "threshold", "oscillatory", "nonlinear"],
            "description": "Identify causal relationships between metrics"
        },
        "complex_events": {
            "types": ["cascade_failure", "synchronization_event", "emergence_event"],
            "description": "Detect multi-component event patterns"
        },
        "predictions": {
            "methods": ["arima", "lstm", "prophet", "ensemble"],
            "horizons": "1-168 time steps",
            "description": "Predict future metric values with confidence intervals"
        },
        "network_analysis": {
            "metrics": ["centrality", "clustering", "communities", "flow"],
            "description": "Analyze component interaction networks"
        }
    }