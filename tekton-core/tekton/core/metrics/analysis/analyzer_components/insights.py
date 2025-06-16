#!/usr/bin/env python3
"""
Insight generation for spectral analysis results.

This module provides functions for generating insights from spectral metrics.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def generate_insights(session_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, str]:
    """Generate insights from session data and analysis.
    
    Args:
        session_data: Session data
        analysis_results: Analysis results
        
    Returns:
        Dict of insights
    """
    insights = {}
    
    # Get spectral metrics
    spectral = analysis_results.get("spectral", {})
    
    # Insight: Efficiency classification
    if "depth_efficiency" in spectral:
        de = spectral["depth_efficiency"]
        if de > 0.8:
            insights["depth_efficiency"] = "Excellent - very high efficiency per layer"
        elif de > 0.5:
            insights["depth_efficiency"] = "Good - efficient use of layers"
        elif de > 0.3:
            insights["depth_efficiency"] = "Moderate - some layer inefficiency"
        else:
            insights["depth_efficiency"] = "Poor - significant layer inefficiency"
    
    # Insight: Parameter utilization
    if "parametric_utilization" in spectral:
        pu = spectral["parametric_utilization"]
        if pu > 0.8:
            insights["parametric_utilization"] = "Excellent - very high parameter utilization"
        elif pu > 0.5:
            insights["parametric_utilization"] = "Good - effective parameter usage"
        elif pu > 0.3:
            insights["parametric_utilization"] = "Moderate - some parameter wastage"
        else:
            insights["parametric_utilization"] = "Poor - significant parameter wastage"
    
    # Insight: Propagation efficiency
    if "min_propagation_threshold" in spectral:
        mpt = spectral["min_propagation_threshold"]
        component_count = analysis_results.get("component_count", 0)
        
        if component_count > 0:
            propagation_ratio = mpt / component_count
            
            if propagation_ratio > 0.9:
                insights["propagation"] = "Excessive - nearly all components involved"
            elif propagation_ratio > 0.7:
                insights["propagation"] = "High - most components involved"
            elif propagation_ratio > 0.4:
                insights["propagation"] = "Moderate - selective component usage"
            else:
                insights["propagation"] = "Efficient - minimal component usage"
    
    # Insight: Modularity assessment
    if "modularity_quotient" in spectral:
        mq = spectral["modularity_quotient"]
        
        if mq > 0.8:
            insights["modularity"] = "Very High - clear module boundaries"
        elif mq > 0.6:
            insights["modularity"] = "High - good module separation"
        elif mq > 0.4:
            insights["modularity"] = "Moderate - some module overlap"
        else:
            insights["modularity"] = "Low - poor module separation"
    
    return insights
