#!/usr/bin/env python3
"""
Cross-dimensional analysis for spectral metrics.

This module analyzes relationships between different dimensions in spectral data.
"""

import logging
import numpy as np
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def analyze_cross_dimensional(session_data: Dict[str, Any], dimensions: List[str]) -> Dict[str, Any]:
    """Analyze relationships between different dimensions.
    
    Args:
        session_data: Session data containing time series
        dimensions: Dimensions to analyze
        
    Returns:
        Dict of cross-dimensional analysis results
    """
    results = {
        'correlation_matrix': {},
        'variance_ratios': {},
        'covarying_dimensions': []
    }
    
    # Get dimensions that actually have data
    available_dims = [dim for dim in dimensions if dim in session_data]
    if len(available_dims) < 2:
        return results
    
    # Calculate correlation matrix
    for dim1 in available_dims:
        results['correlation_matrix'][dim1] = {}
        series1 = np.array(session_data[dim1])
        
        for dim2 in available_dims:
            if dim1 == dim2:
                results['correlation_matrix'][dim1][dim2] = 1.0
                continue
                
            series2 = np.array(session_data[dim2])
            
            # Ensure same length
            min_length = min(len(series1), len(series2))
            if min_length < 2:
                results['correlation_matrix'][dim1][dim2] = 0.0
                continue
            
            try:
                # Calculate correlation
                correlation = np.corrcoef(series1[:min_length], series2[:min_length])[0, 1]
                results['correlation_matrix'][dim1][dim2] = correlation
            except Exception as e:
                logger.error(f"Error calculating correlation for {dim1}-{dim2}: {str(e)}")
                results['correlation_matrix'][dim1][dim2] = 0.0
    
    # Find strongly correlated dimension pairs
    for dim1 in available_dims:
        for dim2 in available_dims:
            if dim1 >= dim2:  # Skip self and duplicates
                continue
                
            corr = results['correlation_matrix'][dim1][dim2]
            if abs(corr) > 0.7:  # Strong correlation threshold
                results['covarying_dimensions'].append({
                    'dimensions': [dim1, dim2],
                    'correlation': corr,
                    'relationship': 'positive' if corr > 0 else 'negative'
                })
    
    # Calculate variance ratios
    for dim in available_dims:
        series = np.array(session_data[dim])
        if len(series) > 1:
            # Calculate ratio of variance to mean
            mean = np.mean(series)
            if mean != 0:
                variance = np.var(series)
                results['variance_ratios'][dim] = variance / abs(mean)
            else:
                results['variance_ratios'][dim] = 0.0
    
    return results


def analyze_time_trends(sessions: List[Dict[str, Any]], dimensions: List[str]) -> Dict[str, Any]:
    """Analyze trends over time across multiple sessions.
    
    Args:
        sessions: List of sessions sorted by timestamp
        dimensions: Dimensions to analyze
        
    Returns:
        Dict of trend analysis results
    """
    if len(sessions) < 2:
        return {'error': 'Not enough historical data for trend analysis'}
    
    # Extract dimension data across sessions
    dimension_trends = {}
    for dimension in dimensions:
        values = []
        timestamps = []
        
        for session in sessions:
            if dimension in session['results']:
                # Extract key metrics
                entry = session['results'][dimension]
                if 'spectral_entropy' in entry:
                    values.append(entry['spectral_entropy'])
                    timestamps.append(session['timestamp'])
        
        if len(values) >= 2:
            # Calculate trend direction
            slope, intercept = np.polyfit(range(len(values)), values, 1)
            
            dimension_trends[dimension] = {
                'values': values,
                'timestamps': timestamps,
                'trend_slope': slope,
                'trend_direction': 'increasing' if slope > 0.01 else 'decreasing' if slope < -0.01 else 'stable',
                'variability': np.std(values)
            }
    
    # Analyze cross-dimensional trends
    cross_dim_trends = []
    for dim1, trend1 in dimension_trends.items():
        for dim2, trend2 in dimension_trends.items():
            if dim1 >= dim2:  # Skip self and duplicates
                continue
            
            # Check if trends go in opposite directions
            if trend1['trend_direction'] != 'stable' and trend2['trend_direction'] != 'stable':
                if trend1['trend_direction'] != trend2['trend_direction']:
                    cross_dim_trends.append({
                        'dimensions': [dim1, dim2],
                        'relationship': f"{dim1} {trend1['trend_direction']} while {dim2} {trend2['trend_direction']}"
                    })
    
    return {
        'session_count': len(sessions),
        'time_span': sessions[-1]['timestamp'] - sessions[0]['timestamp'],
        'dimension_trends': dimension_trends,
        'cross_dimensional_trends': cross_dim_trends
    }
