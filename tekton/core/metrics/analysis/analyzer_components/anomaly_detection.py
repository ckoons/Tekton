#!/usr/bin/env python3
"""
Anomaly detection for spectral analysis.

This module provides anomaly detection capabilities based on spectral metrics.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def detect_anomalies(session_data: Dict[str, Any], current_results: Dict[str, Any], history: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Detect anomalies in the session data compared to historical patterns.
    
    Args:
        session_data: Current session data
        current_results: Analysis results for current session
        history: Historical session data and results
        
    Returns:
        Dict of detected anomalies
    """
    if len(history) < 5:
        return {'detected': False, 'reason': 'Insufficient historical data'}
    
    # Extract baseline statistics from history
    baselines = {}
    for dimension in current_results.keys():
        values = []
        
        for session in history.values():
            if dimension in session['results'] and 'spectral_entropy' in session['results'][dimension]:
                values.append(session['results'][dimension]['spectral_entropy'])
        
        if len(values) >= 5:
            baselines[dimension] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }
    
    # Check for anomalies
    anomalies = []
    for dimension in current_results.keys():
        if dimension not in baselines:
            continue
            
        current = current_results[dimension].get('spectral_entropy')
        if current is None:
            continue
            
        baseline = baselines[dimension]
        z_score = (current - baseline['mean']) / baseline['std'] if baseline['std'] > 0 else 0
        
        # Check if value is significantly different from baseline
        if abs(z_score) > 2.0:  # More than 2 standard deviations
            anomalies.append({
                'dimension': dimension,
                'value': current,
                'baseline': baseline['mean'],
                'z_score': z_score,
                'severity': 'high' if abs(z_score) > 3.0 else 'medium'
            })
    
    # Check for unusual cross-dimensional patterns
    if 'cross_dimensional' in current_results:
        for pair in current_results['cross_dimensional'].get('covarying_dimensions', []):
            dim1, dim2 = pair['dimensions']
            corr = pair['correlation']
            
            # Check if this is unusual based on history
            unusual = True
            for session in history.values():
                if 'cross_dimensional' not in session['results']:
                    continue
                    
                for hist_pair in session['results']['cross_dimensional'].get('covarying_dimensions', []):
                    if set(hist_pair['dimensions']) == set([dim1, dim2]) and hist_pair['relationship'] == pair['relationship']:
                        unusual = False
                        break
                        
                if not unusual:
                    break
            
            if unusual:
                anomalies.append({
                    'dimensions': [dim1, dim2],
                    'correlation': corr,
                    'relationship': pair['relationship'],
                    'type': 'unusual_correlation'
                })
    
    return {
        'detected': len(anomalies) > 0,
        'count': len(anomalies),
        'anomalies': anomalies
    }
