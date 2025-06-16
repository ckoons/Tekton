"""
Hysteresis detection in parameter-performance relationships.

This module provides functions for analyzing hysteresis in model behavior.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union

from ..utils import sessions_to_dicts, interpret_hysteresis

def calculate_hysteresis_detection(sessions: List[Any], parameter: str) -> Dict[str, Any]:
    """Calculate hysteresis in performance as a parameter changes.
    
    Args:
        sessions: List of session data
        parameter: The parameter to analyze
        
    Returns:
        Dict with hysteresis analysis
    """
    if len(sessions) < 10:
        return {"error": "Need at least 10 sessions for hysteresis detection"}
    
    # Convert to list of dicts
    session_dicts = sessions_to_dicts(sessions)
    
    # Extract parameter values and performance
    param_values = []
    performances = []
    
    for session in session_dicts:
        config = session.get('config', {})
        
        if parameter not in config or not isinstance(config[parameter], (int, float)):
            continue
            
        param_values.append(config[parameter])
        performances.append(session.get('performance', {}).get('accuracy', 0))
    
    if len(param_values) < 10:
        return {"error": f"Not enough data with parameter {parameter}"}
    
    # Create dataframe
    df = pd.DataFrame({
        'parameter': param_values,
        'performance': performances
    })
    
    # Sort by parameter value
    df = df.sort_values('parameter')
    
    # Detect if parameter values increase then decrease
    increasing_phase = []
    decreasing_phase = []
    
    # Find the peak parameter value
    peak_idx = df['parameter'].idxmax()
    
    # Split data into increasing and decreasing phases
    increasing_phase = df.loc[:peak_idx]
    decreasing_phase = df.loc[peak_idx:]
    
    # Check if we have sufficient data in both phases
    if len(increasing_phase) < 3 or len(decreasing_phase) < 3:
        return {"error": "Insufficient data for both increasing and decreasing parameter values"}
    
    # Interpolate performance values at common parameter points
    # This allows us to compare performance between phases
    min_param = max(min(increasing_phase['parameter']), min(decreasing_phase['parameter']))
    max_param = min(max(increasing_phase['parameter']), max(decreasing_phase['parameter']))
    
    if min_param >= max_param:
        return {"error": "No overlap between increasing and decreasing parameter ranges"}
    
    # Create common parameter points for comparison
    common_params = np.linspace(min_param, max_param, 10)
    
    # Interpolate performance values
    try:
        increasing_interp = np.interp(common_params, 
                                    increasing_phase['parameter'], 
                                    increasing_phase['performance'])
        
        decreasing_interp = np.interp(common_params, 
                                    decreasing_phase['parameter'][::-1], 
                                    decreasing_phase['performance'][::-1])
    except Exception as e:
        return {"error": f"Error in interpolation: {str(e)}"}
    
    # Calculate hysteresis metrics
    performance_diffs = decreasing_interp - increasing_interp
    
    # Hysteresis metrics
    mean_diff = np.mean(performance_diffs)
    max_diff = np.max(performance_diffs)
    min_diff = np.min(performance_diffs)
    
    # Hysteresis index = average absolute difference normalized by performance range
    performance_range = max(df['performance']) - min(df['performance'])
    
    if performance_range > 0:
        hysteresis_index = np.mean(np.abs(performance_diffs)) / performance_range
    else:
        hysteresis_index = 0
    
    return {
        "parameter": parameter,
        "hysteresis_index": hysteresis_index,
        "mean_difference": mean_diff,
        "max_difference": max_diff,
        "min_difference": min_diff,
        "common_parameter_points": common_params.tolist(),
        "increasing_performance": increasing_interp.tolist(),
        "decreasing_performance": decreasing_interp.tolist(),
        "interpretation": interpret_hysteresis(hysteresis_index)
    }