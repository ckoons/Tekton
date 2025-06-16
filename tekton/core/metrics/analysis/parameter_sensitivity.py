"""
Parameter sensitivity analysis.

This module provides functions for analyzing parameter sensitivity.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any, Optional, Union

from ..utils import sessions_to_dicts, interpret_parameter_sensitivity

def calculate_control_parameter_sensitivity(sessions: List[Any], parameters: Optional[List[str]] = None) -> Dict[str, Any]:
    """Calculate sensitivity to different control parameters.
    
    Args:
        sessions: List of session data
        parameters: Optional list of parameters to analyze
        
    Returns:
        Dict with parameter sensitivity analysis
    """
    if len(sessions) < 10:
        return {"error": "Need at least 10 sessions for parameter sensitivity analysis"}
    
    # Convert to list of dicts
    session_dicts = sessions_to_dicts(sessions)
    
    # Extract parameters and performance from sessions
    parameter_values = {}
    performances = []
    
    for session in session_dicts:
        performance = session.get('performance', {}).get('accuracy', 0)
        performances.append(performance)
        
        config = session.get('config', {})
        for key, value in config.items():
            if not isinstance(value, (int, float)):
                continue
                
            if key not in parameter_values:
                parameter_values[key] = []
            parameter_values[key].append(value)
    
    # If no specific parameters requested, analyze all numeric parameters
    if parameters is None:
        parameters = list(parameter_values.keys())
    
    # Filter to parameters with sufficient data
    parameters = [p for p in parameters if p in parameter_values and len(parameter_values[p]) == len(performances)]
    
    if not parameters:
        return {"error": "No suitable parameters found for sensitivity analysis"}
    
    # Calculate sensitivity for each parameter
    sensitivity = {}
    
    for param in parameters:
        values = parameter_values[param]
        
        if len(set(values)) <= 1:
            # Skip parameters with no variation
            continue
            
        # Create dataframe for analysis
        df = pd.DataFrame({
            'parameter': values,
            'performance': performances
        })
        
        # Calculate correlation
        correlation = df['parameter'].corr(df['performance'])
        
        # Calculate slope of linear regression
        if len(set(values)) > 1:
            slope, _, _, _, _ = stats.linregress(values, performances)
        else:
            slope = 0
            
        # Normalized sensitivity (partial derivative * parameter / performance)
        mean_param = np.mean(values)
        mean_perf = np.mean(performances)
        
        if mean_perf > 0 and mean_param != 0:
            normalized_sensitivity = slope * (mean_param / mean_perf)
        else:
            normalized_sensitivity = 0
            
        # Non-linearity check: segmented regression test
        non_linearity = 0
        
        if len(values) >= 10:
            # Sort by parameter value
            df = df.sort_values('parameter')
            
            # Split into two segments
            mid = len(df) // 2
            df_low = df.iloc[:mid]
            df_high = df.iloc[mid:]
            
            # Calculate slopes for each segment
            if len(set(df_low['parameter'])) > 1:
                slope_low, _, _, _, _ = stats.linregress(df_low['parameter'], df_low['performance'])
            else:
                slope_low = 0
                
            if len(set(df_high['parameter'])) > 1:
                slope_high, _, _, _, _ = stats.linregress(df_high['parameter'], df_high['performance'])
            else:
                slope_high = 0
            
            # Non-linearity score = difference in slopes
            if max(abs(slope_low), abs(slope_high)) > 0:
                non_linearity = abs(slope_high - slope_low) / max(abs(slope_low), abs(slope_high))
        
        sensitivity[param] = {
            'correlation': correlation,
            'slope': slope,
            'normalized_sensitivity': normalized_sensitivity,
            'non_linearity': non_linearity
        }
    
    # Add interpretation
    for param in sensitivity:
        sens = sensitivity[param]
        sens['interpretation'] = interpret_parameter_sensitivity(
            sens['normalized_sensitivity'], sens['non_linearity']
        )
    
    return sensitivity