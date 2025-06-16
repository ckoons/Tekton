#!/usr/bin/env python3
"""
Spectral Analysis Module

This module provides functions for running spectral analysis on component metrics.
"""

import time
from typing import Dict, Any

from ..alerts import AlertSeverity
from ...logging_integration import get_logger

# Configure logger
logger = get_logger("tekton.monitoring.dashboard.spectral")


def run_spectral_analysis(dashboard):
    """Run spectral analysis on component metrics.
    
    Args:
        dashboard: The dashboard instance
    """
    if not dashboard.spectral_analyzer:
        return
        
    # Create session data with time series
    try:
        # Extract time series from component metrics
        session_data = {'id': f"dashboard-{int(time.time())}"}
        
        # Add component metrics as time series
        for component_id, status in dashboard.component_status.items():
            metrics = status.get("metrics", {})
            if not metrics:
                continue
                
            # Add to session data
            component_key = f"component.{component_id}"
            session_data[component_key] = {}
            
            for metric_name, value in metrics.items():
                # Skip non-numeric values
                if not isinstance(value, (int, float)):
                    continue
                    
                # Use existing time series if available
                time_series_key = f"{component_key}.{metric_name}"
                
                # Initialize with single value if not exists
                session_data[time_series_key] = [value]
        
        # Run analysis on prepared data
        if len(session_data) > 1:  # Has at least one metric
            try:
                results = dashboard.spectral_analyzer.analyze_session(session_data)
                
                # Look for anomalies
                anomalies = dashboard.spectral_analyzer.detect_anomalies(session_data)
                
                # Generate alerts for significant anomalies
                if anomalies.get('detected', False):
                    for anomaly in anomalies.get('anomalies', []):
                        if anomaly.get('severity') == 'high':
                            dimension = anomaly.get('dimension')
                            if dimension and dimension.startswith('component.'):
                                # Extract component ID from dimension
                                parts = dimension.split('.')
                                if len(parts) >= 2:
                                    component_id = parts[1]
                                    
                                    dashboard._generate_alert(
                                        severity=AlertSeverity.WARNING,
                                        title="Spectral Anomaly Detected",
                                        description=f"Unusual behavior detected in {dimension} (z-score: {anomaly.get('z_score', 0):.1f})",
                                        component_id=component_id
                                    )
                
                # Store results for dashboard
                dashboard.last_spectral_analysis = {
                    'timestamp': time.time(),
                    'results': results,
                    'anomalies': anomalies
                }
                
            except Exception as e:
                logger.error(f"Error running spectral analysis: {e}")
        
    except Exception as e:
        logger.error(f"Error preparing data for spectral analysis: {e}")