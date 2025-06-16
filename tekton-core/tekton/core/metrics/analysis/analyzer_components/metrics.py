#!/usr/bin/env python3
"""
Spectral metrics calculation for sessions.

This module provides functions for calculating spectral metrics from session data.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def calculate_spectral_metrics(session_data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate spectral metrics for a session.
    
    Args:
        session_data: Session data
        
    Returns:
        Dict of metrics
    """
    metrics = {}
    
    # Calculate Depth Efficiency (DE)
    total_layers = sum(len(data.get("layers", {})) 
                     for data in session_data.get("parameter_usage", {}).values())
    if "accuracy" in session_data.get("performance", {}) and total_layers > 0:
        metrics["depth_efficiency"] = session_data["performance"]["accuracy"] / total_layers
    else:
        metrics["depth_efficiency"] = 0
        
    # Calculate Parametric Utilization (PU)
    total_params = sum(data.get("total", 0) for data in session_data.get("parameter_usage", {}).values())
    active_params = sum(data.get("active", 0) for data in session_data.get("parameter_usage", {}).values())
    
    if total_params > 0:
        metrics["parametric_utilization"] = active_params / total_params
    else:
        metrics["parametric_utilization"] = 0
        
    # Calculate Minimum Propagation Threshold (MPT)
    if session_data.get("propagation_path"):
        # Count unique components in the propagation path
        components = set()
        for step in session_data["propagation_path"]:
            components.add(step.get("source", ""))
            components.add(step.get("destination", ""))
        
        metrics["min_propagation_threshold"] = len(components)
    else:
        metrics["min_propagation_threshold"] = 0
        
    # Calculate Modularity Quotient (MQ)
    cross_module_flow = 0
    within_module_flow = 0
    
    for step in session_data.get("propagation_path", []):
        source = step.get("source", "")
        dest = step.get("destination", "")
        
        # If source and destination are in the same component family
        if source.split('.')[0] == dest.split('.')[0]:
            within_module_flow += step.get("info_content", 1)
        else:
            cross_module_flow += step.get("info_content", 1)
    
    total_flow = cross_module_flow + within_module_flow
    if total_flow > 0:
        metrics["modularity_quotient"] = 1 - (cross_module_flow / total_flow)
    else:
        metrics["modularity_quotient"] = 0
        
    return metrics
