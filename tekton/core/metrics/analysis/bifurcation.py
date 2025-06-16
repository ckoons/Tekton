"""
Bifurcation proximity analysis.

This module provides functions for analyzing bifurcation proximity.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

from ..utils import sessions_to_dicts, interpret_bifurcation_proximity

def calculate_bifurcation_proximity(sessions: List[Any], num_recent: int = 10) -> Dict[str, Any]:
    """Calculate the bifurcation proximity index for recent sessions.
    
    BPI indicates how close the system is to a capability bifurcation.
    
    Args:
        sessions: List of session data
        num_recent: Number of recent sessions to consider
        
    Returns:
        Dict with bifurcation proximity analysis
    """
    if len(sessions) < num_recent:
        return {"error": f"Need at least {num_recent} sessions for bifurcation analysis"}
    
    # Convert to list of dicts
    session_dicts = sessions_to_dicts(sessions)
    
    # Sort by start time
    session_dicts.sort(key=lambda x: x.get('start_time', 0))
    
    # Get most recent sessions
    recent_sessions = session_dicts[-num_recent:]
    
    # Extract key metrics
    accuracies = [s.get('performance', {}).get('accuracy', 0) for s in recent_sessions]
    
    # Calculate variance in performance
    variance = np.var(accuracies)
    
    # Calculate autocorrelation at lag 1 (critical slowing down indicator)
    if len(accuracies) > 2:
        autocorr = np.corrcoef(accuracies[:-1], accuracies[1:])[0, 1]
    else:
        autocorr = 0
    
    # Calculate skewness (approaching bifurcation often increases skewness)
    if len(accuracies) > 2:
        skewness = pd.Series(accuracies).skew()
    else:
        skewness = 0
        
    # Combine indicators into Bifurcation Proximity Index
    # Higher values indicate closer proximity to bifurcation
    # Normalized to 0-1 range
    variance_factor = min(1.0, variance * 10)  # Increasing variance near bifurcation
    autocorr_factor = max(0, (autocorr + 1) / 2)  # Increasing autocorrelation near bifurcation
    skewness_factor = min(1.0, abs(skewness) / 2)  # Increasing absolute skewness near bifurcation
    
    # Calculate BPI as weighted sum of indicators
    bpi = (variance_factor * 0.3 + autocorr_factor * 0.5 + skewness_factor * 0.2)
    
    return {
        "bifurcation_proximity_index": bpi,
        "variance": variance,
        "autocorrelation": autocorr,
        "skewness": skewness,
        "interpretation": interpret_bifurcation_proximity(bpi)
    }