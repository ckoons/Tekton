"""
Architectural elasticity analysis.

This module provides functions for calculating architectural elasticity.
"""

import numpy as np
from typing import Dict, List, Any, Optional

from ..utils import sessions_to_dicts

def find_architectural_elasticity(sessions: List[Any]) -> Dict[str, Any]:
    """Calculate architectural elasticity from session data.
    
    Architectural Elasticity (AE) = Δ(performance) / Δ(architectural_complexity)
    
    Args:
        sessions: List of session data objects
        
    Returns:
        Dict of elasticity metrics
    """
    if len(sessions) < 2:
        return {"error": "Need at least 2 sessions to calculate elasticity"}
    
    # Convert to list of dicts
    session_dicts = sessions_to_dicts(sessions)
    
    # Sort by start time
    session_dicts.sort(key=lambda x: x.get('start_time', 0))
    
    # Calculate changes between consecutive sessions
    elasticity_points = []
    
    for i in range(1, len(session_dicts)):
        prev = session_dicts[i-1]
        curr = session_dicts[i]
        
        # Extract performance metric (accuracy, success rate, etc.)
        prev_perf = prev.get('performance', {}).get('accuracy', 0)
        curr_perf = curr.get('performance', {}).get('accuracy', 0)
        
        # Extract complexity metrics
        prev_complexity = _calculate_complexity(prev)
        curr_complexity = _calculate_complexity(curr)
        
        # Calculate elasticity if complexity changed
        if abs(curr_complexity - prev_complexity) > 0.001:
            elasticity = (curr_perf - prev_perf) / (curr_complexity - prev_complexity)
            
            elasticity_points.append({
                "from_session": prev['id'],
                "to_session": curr['id'],
                "performance_delta": curr_perf - prev_perf,
                "complexity_delta": curr_complexity - prev_complexity,
                "elasticity": elasticity
            })
    
    # Calculate overall elasticity
    if elasticity_points:
        avg_elasticity = np.mean([p["elasticity"] for p in elasticity_points])
        max_elasticity = max([p["elasticity"] for p in elasticity_points])
        min_elasticity = min([p["elasticity"] for p in elasticity_points])
    else:
        avg_elasticity = 0
        max_elasticity = 0
        min_elasticity = 0
    
    return {
        "points": elasticity_points,
        "average": avg_elasticity,
        "maximum": max_elasticity,
        "minimum": min_elasticity
    }

def _calculate_complexity(session_data: Dict[str, Any]) -> float:
    """Calculate architectural complexity metric.
    
    Args:
        session_data: Session data dict
        
    Returns:
        Complexity score
    """
    # Count components
    component_count = len(session_data.get('component_activations', {}))
    
    # Count total parameters
    total_params = sum(data.get('total', 0) for data in session_data.get('parameter_usage', {}).values())
    
    # Count propagation steps
    prop_steps = len(session_data.get('propagation_path', []))
    
    # Calculate modularity
    mq = session_data.get('spectral_metrics', {}).get('modularity_quotient', 0.5)
    
    # Combine into complexity score
    # Higher complexity for more components, more parameters, more propagation steps, lower modularity
    complexity = (
        component_count * 0.3 + 
        np.log1p(total_params) * 0.3 + 
        prop_steps * 0.2 + 
        (1 - mq) * 0.2
    )
    
    return complexity