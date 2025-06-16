#!/usr/bin/env python3
"""
Core spectral analysis functionality for Tekton metrics.

This module provides the SpectralAnalyzer class that serves as the main interface
for all spectral and catastrophe theory analysis.
"""

import logging
import numpy as np
import time
from typing import Dict, List, Any, Optional, Union, Tuple

from .bifurcation import calculate_bifurcation_proximity
from .parameter_sensitivity import calculate_control_parameter_sensitivity
from .hysteresis import calculate_hysteresis_detection
from .catastrophe_points import identify_catastrophe_points
from .architectural_elasticity import find_architectural_elasticity
from ..utils import session_to_dict
from .analyzer_components.base_analyzer import BaseAnalyzer
from .analyzer_components.metrics import calculate_spectral_metrics
from .analyzer_components.insights import generate_insights
from .analyzer_components.spectral_utils import (
    compute_frequency_components,
    calculate_band_powers,
    calculate_spectral_entropy,
    detect_dominant_frequencies
)
from .analyzer_components.cross_dimensional import (
    analyze_cross_dimensional,
    analyze_time_trends
)
from .analyzer_components.anomaly_detection import detect_anomalies

logger = logging.getLogger(__name__)


class SpectralAnalyzer(BaseAnalyzer):
    """Analyzes metrics data to extract spectral insights."""
    
    def analyze_session(self, session_data):
        """Analyze a single session.
        
        Args:
            session_data: SessionData object or dict
            
        Returns:
            Dict of analysis results
        """
        # Ensure we have dict format
        data = session_to_dict(session_data)
        
        results = {
            "session_id": data["id"],
            "processing_time": data.get("end_time", 0) - data.get("start_time", 0),
            "component_count": len(data.get("component_activations", {})),
            "propagation_steps": len(data.get("propagation_path", [])),
        }
        
        # Include spectral metrics if available
        if "spectral_metrics" in data:
            results["spectral"] = data["spectral_metrics"]
        else:
            # Calculate basic spectral metrics if not already present
            try:
                spectral = calculate_spectral_metrics(data)
                results["spectral"] = spectral
            except Exception as e:
                logger.error(f"Error calculating spectral metrics: {str(e)}")
                results["spectral"] = {}
        
        # Calculate additional insights
        results["insights"] = generate_insights(data, results)
        
        return results
    
    def analyze_sessions(self, sessions, group_by=None):
        """Analyze multiple sessions with optional grouping.
        
        Args:
            sessions: List of SessionData objects or dicts
            group_by: Optional field to group sessions by
            
        Returns:
            Dict of analysis results
        """
        if not sessions:
            return {"sessions": 0, "groups": {}}
        
        # Analyze each session
        session_results = [self.analyze_session(session) for session in sessions]
        
        # Calculate overall statistics
        overall = {
            "sessions": len(session_results),
            "avg_processing_time": np.mean([r["processing_time"] for r in session_results]),
            "avg_component_count": np.mean([r["component_count"] for r in session_results]),
            "avg_propagation_steps": np.mean([r["propagation_steps"] for r in session_results]),
        }
        
        # Calculate average spectral metrics
        spectral_keys = set()
        for result in session_results:
            spectral_keys.update(result.get("spectral", {}).keys())
        
        spectral_avgs = {}
        for key in spectral_keys:
            values = [r.get("spectral", {}).get(key, 0) for r in session_results]
            spectral_avgs[key] = np.mean(values)
        
        overall["spectral_avg"] = spectral_avgs
        
        # Group results if requested
        if group_by:
            groups = {}
            for result in session_results:
                # Get session data to extract group value
                session_id = result["session_id"]
                session = next((s for s in sessions if (s["id"] if isinstance(s, dict) else s.id) == session_id), None)
                
                if not session:
                    continue
                
                # Get group value
                if isinstance(session, dict):
                    group_val = session.get(group_by, "unknown")
                else:
                    group_val = getattr(session, group_by, "unknown")
                
                # Add to group
                if group_val not in groups:
                    groups[group_val] = []
                
                groups[group_val].append(result)
            
            # Calculate group statistics
            group_stats = {}
            for group_val, group_results in groups.items():
                group_stats[group_val] = self.analyze_sessions(group_results)
            
            overall["groups"] = group_stats
        
        return overall
    
    def find_architectural_elasticity(self, sessions):
        """Calculate architectural elasticity from session data."""
        return find_architectural_elasticity(sessions)
    
    def identify_catastrophe_points(self, sessions, window_size=5):
        """Identify potential catastrophe points in model behavior."""
        return identify_catastrophe_points(sessions, window_size)
        
    def calculate_bifurcation_proximity(self, sessions, num_recent=10):
        """Calculate the bifurcation proximity index for recent sessions."""
        return calculate_bifurcation_proximity(sessions, num_recent)
    
    def calculate_control_parameter_sensitivity(self, sessions, parameters=None):
        """Calculate sensitivity to different control parameters."""
        return calculate_control_parameter_sensitivity(sessions, parameters)
        
    def calculate_hysteresis_detection(self, sessions, parameter):
        """Calculate hysteresis in performance as a parameter changes."""
        return calculate_hysteresis_detection(sessions, parameter)


class EnhancedSpectralAnalyzer(BaseAnalyzer):
    """
    Enhanced spectral analyzer with complete implementation of spectral metrics.
    
    This analyzer implements advanced techniques for detecting patterns in
    component behavior across multiple dimensions.
    """

    def __init__(self, dimensions=None, sampling_rate=1.0):
        """
        Initialize enhanced spectral analyzer.
        
        Args:
            dimensions: List of dimensions to analyze
            sampling_rate: Sampling rate in Hz
        """
        super().__init__()
        self.dimensions = dimensions or ['latency', 'throughput', 'error_rate', 'memory_usage', 'cpu_usage']
        self.sampling_rate = sampling_rate
        self.frequency_bands = {
            'ultra_low': (0.0, 0.01),  # long-term trends (hours)
            'very_low': (0.01, 0.1),   # medium-term trends (minutes)
            'low': (0.1, 1.0),         # short-term trends (seconds)
            'medium': (1.0, 10.0),     # transient behavior
            'high': (10.0, 100.0)      # rapid fluctuations
        }
        self.history = {}
    
    def analyze_session(self, session_data):
        """Perform comprehensive spectral analysis on session data.
        
        Args:
            session_data: Session data containing time series for each dimension
            
        Returns:
            Dict of analysis results
        """
        results = {}

        # Convert session_data to format with time series if needed
        data = self._prepare_session_data(session_data)
        
        # Extract time series for each dimension
        for dimension in self.dimensions:
            if dimension in data:
                try:
                    # Apply FFT to get frequency components
                    freq_components = compute_frequency_components(data[dimension], self.sampling_rate)
                    
                    # Calculate power in each frequency band
                    band_powers = calculate_band_powers(freq_components, self.frequency_bands)
                    
                    # Calculate spectral entropy
                    spectral_entropy = calculate_spectral_entropy(freq_components)
                    
                    # Detect dominant frequencies
                    dominant_freqs = detect_dominant_frequencies(freq_components)
                    
                    # Calculate coherence with other dimensions
                    coherence = self._calculate_coherence(data, dimension)
                    
                    # Store results for this dimension
                    results[dimension] = {
                        'band_powers': band_powers,
                        'spectral_entropy': spectral_entropy,
                        'dominant_frequencies': dominant_freqs,
                        'coherence': coherence
                    }
                except Exception as e:
                    logger.error(f"Error analyzing dimension {dimension}: {str(e)}")
        
        # Cross-dimensional analysis
        try:
            results['cross_dimensional'] = analyze_cross_dimensional(data, self.dimensions)
        except Exception as e:
            logger.error(f"Error in cross-dimensional analysis: {str(e)}")
        
        # Store in history for trend analysis
        session_id = session_data.get('id', str(time.time()))
        self.history[session_id] = {
            'timestamp': time.time(),
            'results': results
        }
        
        # Trim history if too large
        if len(self.history) > 100:
            oldest = min(self.history.keys(), key=lambda k: self.history[k]['timestamp'])
            del self.history[oldest]
        
        return results

    def _prepare_session_data(self, session_data):
        """Prepare session data for spectral analysis.
        
        Args:
            session_data: Raw session data
            
        Returns:
            Dict with time series for each dimension
        """
        # If data is already in the right format, return it
        if any(dim in session_data for dim in self.dimensions):
            return session_data
        
        # Otherwise, try to extract time series from component activations/metrics
        prepared_data = {}
        
        # Extract from component metrics if available
        if 'component_metrics' in session_data:
            for component_id, metrics in session_data['component_metrics'].items():
                for metric_name, values in metrics.items():
                    if not isinstance(values, list):
                        continue
                    
                    dim_name = f"{component_id}.{metric_name}"
                    prepared_data[dim_name] = values
        
        # Extract from performance timeline if available
        if 'performance' in session_data and 'timeline' in session_data['performance']:
            for metric_name, values in session_data['performance']['timeline'].items():
                prepared_data[metric_name] = values
        
        # Map to standard dimensions if possible
        for std_dim in self.dimensions:
            for dim_name in list(prepared_data.keys()):
                if std_dim in dim_name.lower():
                    if std_dim not in prepared_data:
                        prepared_data[std_dim] = prepared_data[dim_name]
        
        return prepared_data

    def _calculate_coherence(self, session_data, dimension):
        """Calculate coherence between this dimension and others.
        
        Args:
            session_data: Session data containing time series
            dimension: Current dimension
            
        Returns:
            Dict mapping dimension names to coherence values
        """
        coherence = {}
        
        # Skip if we don't have the current dimension
        if dimension not in session_data:
            return coherence
        
        current_series = np.array(session_data[dimension])
        
        # Calculate coherence with other dimensions
        for other_dim in self.dimensions:
            if other_dim == dimension or other_dim not in session_data:
                continue
                
            other_series = np.array(session_data[other_dim])
            
            # Both series must be the same length
            min_length = min(len(current_series), len(other_series))
            if min_length < 2:
                coherence[other_dim] = 0.0
                continue
                
            current = current_series[:min_length]
            other = other_series[:min_length]
            
            try:
                # Calculate correlation (simplified coherence)
                # In a full implementation, we would use proper frequency-domain coherence
                correlation = np.corrcoef(current, other)[0, 1]
                coherence[other_dim] = abs(correlation)  # Use absolute value for coherence
            except Exception as e:
                logger.error(f"Error calculating coherence for {dimension}-{other_dim}: {str(e)}")
                coherence[other_dim] = 0.0
        
        return coherence

    def analyze_time_trends(self, session_ids=None):
        """Analyze trends over time across multiple sessions.
        
        Args:
            session_ids: Optional list of session IDs to include
            
        Returns:
            Dict of trend analysis results
        """
        if len(self.history) < 2:
            return {'error': 'Not enough historical data for trend analysis'}
        
        # Use all sessions if not specified
        if session_ids is None:
            sessions = list(self.history.values())
        else:
            sessions = [self.history[sid] for sid in session_ids if sid in self.history]
            if len(sessions) < 2:
                return {'error': 'Not enough matching sessions for trend analysis'}
        
        # Sort by timestamp
        sessions.sort(key=lambda s: s['timestamp'])
        
        return analyze_time_trends(sessions, self.dimensions)

    def detect_anomalies(self, session_data):
        """Detect anomalies in the session data compared to historical patterns.
        
        Args:
            session_data: Current session data
            
        Returns:
            Dict of detected anomalies
        """
        # Analyze the current session
        current_results = self.analyze_session(session_data)
        
        return detect_anomalies(session_data, current_results, self.history)
