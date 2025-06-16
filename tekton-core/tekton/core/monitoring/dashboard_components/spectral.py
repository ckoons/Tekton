#!/usr/bin/env python3
"""
Spectral Analysis Component

This module provides spectral analysis integration for the dashboard.
"""

import time
from typing import Dict, List, Any, Optional, Callable

from ...logging_integration import get_logger, LogCategory

# Configure logger
logger = get_logger("tekton.monitoring.dashboard.spectral")


class SpectralAnalyzer:
    """
    Spectral analysis integration for the dashboard.
    
    Provides advanced metrics analysis using spectral decomposition and
    time-series analysis techniques.
    """
    
    def __init__(self, dashboard=None):
        """
        Initialize spectral analyzer.
        
        Args:
            dashboard: Dashboard instance
        """
        self.dashboard = dashboard
        self.analyzer = None
        
        # Try to import spectral analyzer
        try:
            from ...metrics.analysis.spectral_analyzer import EnhancedSpectralAnalyzer
            self.analyzer = EnhancedSpectralAnalyzer()
            logger.info("Enhanced spectral analyzer initialized successfully")
        except ImportError:
            logger.warning("Enhanced spectral analyzer not available")
    
    def run_analysis(self):
        """Run spectral analysis on component metrics."""
        if not self.analyzer or not self.dashboard:
            return None
            
        try:
            # Get component metrics
            component_metrics = {}
            for component_id, component in self.dashboard.component_status.items():
                if "metrics" in component and component["metrics"]:
                    component_metrics[component_id] = component["metrics"]
            
            # Run spectral analysis
            results = self.analyzer.analyze_component_metrics(component_metrics)
            
            # Update dashboard with results
            if results and hasattr(self.dashboard, "system_health"):
                spectral_metrics = extract_spectral_metrics(results)
                if spectral_metrics:
                    if not hasattr(self.dashboard.system_health, "spectral_metrics"):
                        self.dashboard.system_health.spectral_metrics = {}
                    self.dashboard.system_health.spectral_metrics.update(spectral_metrics)
            
            # Check for spectral anomalies
            if results and "anomalies" in results and results["anomalies"]:
                for anomaly in results["anomalies"]:
                    component_id = anomaly.get("component_id")
                    metric_name = anomaly.get("metric")
                    score = anomaly.get("score", 0.0)
                    description = anomaly.get("description", "")
                    
                    # Generate alert if score is significant
                    if score > 0.7 and hasattr(self.dashboard, "_generate_alert"):
                        from ..alerts import AlertSeverity
                        self.dashboard._generate_alert(
                            severity=AlertSeverity.WARNING,
                            title=f"Spectral Anomaly: {metric_name}",
                            description=f"Anomaly detected in {metric_name} for component {component_id}: {description}",
                            component_id=component_id
                        )
            
            return results
        
        except Exception as e:
            logger.error(f"Error running spectral analysis: {e}", exception=e)
            return None


def run_spectral_analysis(dashboard) -> Optional[Dict[str, Any]]:
    """Run spectral analysis on dashboard metrics.
    
    Args:
        dashboard: Dashboard instance
        
    Returns:
        Analysis results or None if not available
    """
    try:
        # Try to import spectral analyzer
        from ...metrics.analysis.spectral_analyzer import EnhancedSpectralAnalyzer
        
        # Get component metrics
        component_metrics = {}
        for component_id, component in dashboard.component_status.items():
            if "metrics" in component and component["metrics"]:
                component_metrics[component_id] = component["metrics"]
        
        # Create analyzer
        analyzer = EnhancedSpectralAnalyzer()
        
        # Run analysis
        results = analyzer.analyze_component_metrics(component_metrics)
        
        # Update dashboard with results
        if results:
            spectral_metrics = extract_spectral_metrics(results)
            if spectral_metrics:
                if not hasattr(dashboard.system_health, "spectral_metrics"):
                    dashboard.system_health.spectral_metrics = {}
                dashboard.system_health.spectral_metrics.update(spectral_metrics)
        
        return results
    
    except ImportError:
        logger.debug("Enhanced spectral analyzer not available")
        return None
    except Exception as e:
        logger.error(f"Error running spectral analysis: {e}", exception=e)
        return None


def extract_spectral_metrics(results: Dict[str, Any]) -> Dict[str, float]:
    """Extract metrics from spectral analysis results.
    
    Args:
        results: Spectral analysis results
        
    Returns:
        Extracted metrics dictionary
    """
    metrics = {}
    
    # Extract key metrics
    if "system" in results:
        system = results["system"]
        metrics["spectral_entropy"] = system.get("entropy", 0.0)
        metrics["spectral_energy"] = system.get("energy", 0.0)
        metrics["spectral_density"] = system.get("density", 0.0)
        
        if "eigenvalues" in system:
            eigenvalues = system["eigenvalues"]
            metrics["principal_eigenvalue"] = eigenvalues[0] if eigenvalues else 0.0
            metrics["eigenvalue_spread"] = (max(eigenvalues) - min(eigenvalues)) if len(eigenvalues) > 1 else 0.0
    
    # Extract anomaly metrics
    if "anomalies" in results:
        anomalies = results["anomalies"]
        metrics["anomaly_count"] = len(anomalies)
        metrics["max_anomaly_score"] = max([a.get("score", 0.0) for a in anomalies]) if anomalies else 0.0
    
    # Extract bifurcation metrics
    if "bifurcations" in results:
        bifurcations = results["bifurcations"]
        metrics["bifurcation_count"] = len(bifurcations)
        metrics["max_bifurcation_intensity"] = max([b.get("intensity", 0.0) for b in bifurcations]) if bifurcations else 0.0
    
    return metrics
