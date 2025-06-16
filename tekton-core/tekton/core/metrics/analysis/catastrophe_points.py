"""
Catastrophe points detection.

This module provides functions for identifying catastrophe points in model behavior.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Union

from ..utils import sessions_to_dicts

def identify_catastrophe_points(sessions: List[Any], window_size: int = 5) -> List[Dict[str, Any]]:
    """Identify potential catastrophe points in model behavior.
    
    Args:
        sessions: List of session data
        window_size: Window size for detecting sudden changes
        
    Returns:
        List of potential catastrophe points
    """
    if len(sessions) < window_size * 2:
        return {"error": f"Need at least {window_size*2} sessions to identify catastrophe points"}
    
    # Convert to list of dicts
    session_dicts = sessions_to_dicts(sessions)
    
    # Sort by start time
    session_dicts.sort(key=lambda x: x.get('start_time', 0))
    
    # Extract metrics series
    times = [s.get('start_time', 0) for s in session_dicts]
    accuracies = [s.get('performance', {}).get('accuracy', 0) for s in session_dicts]
    
    # Extract spectral metrics
    de_values = [s.get('spectral_metrics', {}).get('depth_efficiency', 0) for s in session_dicts]
    pu_values = [s.get('spectral_metrics', {}).get('parametric_utilization', 0) for s in session_dicts]
    mq_values = [s.get('spectral_metrics', {}).get('modularity_quotient', 0) for s in session_dicts]
    
    # Extract new metrics if available
    ccr_values = [s.get('spectral_metrics', {}).get('cognitive_convergence_rate', 0) for s in session_dicts]
    lsne_values = [s.get('spectral_metrics', {}).get('latent_space_navigation_efficiency', 0) for s in session_dicts]
    cmii_values = [s.get('spectral_metrics', {}).get('cross_modal_integration_index', 0) for s in session_dicts]
    csc_values = [s.get('spectral_metrics', {}).get('conceptual_stability_coefficient', 0) for s in session_dicts]
    
    # Detect sudden changes in metrics
    catastrophe_points = []
    
    for i in range(window_size, len(session_dicts) - window_size):
        # Calculate before/after averages
        before_acc = np.mean(accuracies[i-window_size:i])
        after_acc = np.mean(accuracies[i:i+window_size])
        acc_change = after_acc - before_acc
        
        before_de = np.mean(de_values[i-window_size:i])
        after_de = np.mean(de_values[i:i+window_size])
        de_change = after_de - before_de
        
        before_pu = np.mean(pu_values[i-window_size:i])
        after_pu = np.mean(pu_values[i:i+window_size])
        pu_change = after_pu - before_pu
        
        before_mq = np.mean(mq_values[i-window_size:i])
        after_mq = np.mean(mq_values[i:i+window_size])
        mq_change = after_mq - before_mq
        
        # New metrics
        before_ccr = np.mean(ccr_values[i-window_size:i])
        after_ccr = np.mean(ccr_values[i:i+window_size])
        ccr_change = after_ccr - before_ccr
        
        before_lsne = np.mean(lsne_values[i-window_size:i])
        after_lsne = np.mean(lsne_values[i:i+window_size])
        lsne_change = after_lsne - before_lsne
        
        before_cmii = np.mean(cmii_values[i-window_size:i])
        after_cmii = np.mean(cmii_values[i:i+window_size])
        cmii_change = after_cmii - before_cmii
        
        before_csc = np.mean(csc_values[i-window_size:i])
        after_csc = np.mean(csc_values[i:i+window_size])
        csc_change = after_csc - before_csc
        
        # Calculate change magnitudes
        acc_magnitude = abs(acc_change) / max(before_acc, 0.001)
        de_magnitude = abs(de_change) / max(before_de, 0.001)
        pu_magnitude = abs(pu_change) / max(before_pu, 0.001)
        mq_magnitude = abs(mq_change) / max(before_mq, 0.001)
        
        # New metrics magnitudes
        ccr_magnitude = abs(ccr_change) / max(before_ccr, 0.001)
        lsne_magnitude = abs(lsne_change) / max(before_lsne, 0.001)
        cmii_magnitude = abs(cmii_change) / max(before_cmii, 0.001)
        csc_magnitude = abs(csc_change) / max(before_csc, 0.001)
        
        # Check for significant changes
        significant_changes = []
        
        if acc_magnitude > 0.2:  # 20% change threshold
            significant_changes.append(("accuracy", acc_change, acc_magnitude))
        
        if de_magnitude > 0.2:
            significant_changes.append(("depth_efficiency", de_change, de_magnitude))
        
        if pu_magnitude > 0.2:
            significant_changes.append(("parametric_utilization", pu_change, pu_magnitude))
        
        if mq_magnitude > 0.2:
            significant_changes.append(("modularity_quotient", mq_change, mq_magnitude))
            
        # New metrics changes
        if ccr_magnitude > 0.2:
            significant_changes.append(("cognitive_convergence_rate", ccr_change, ccr_magnitude))
            
        if lsne_magnitude > 0.2:
            significant_changes.append(("latent_space_navigation_efficiency", lsne_change, lsne_magnitude))
            
        if cmii_magnitude > 0.2:
            significant_changes.append(("cross_modal_integration_index", cmii_change, cmii_magnitude))
            
        if csc_magnitude > 0.2:
            significant_changes.append(("conceptual_stability_coefficient", csc_change, csc_magnitude))
        
        if significant_changes:
            catastrophe_points.append({
                "session_id": session_dicts[i]['id'],
                "time": times[i],
                "changes": significant_changes,
                "magnitude": max(c[2] for c in significant_changes)
            })
    
    # Sort by magnitude (descending)
    catastrophe_points.sort(key=lambda x: x["magnitude"], reverse=True)
    
    return catastrophe_points