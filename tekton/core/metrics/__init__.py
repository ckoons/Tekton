"""
Metrics collection and analysis for Tekton architecture.

This module provides tools for collecting, analyzing, and visualizing
performance metrics related to computational spectral analysis and catastrophe theory.
"""

# Core metrics types
from .metric_types import MetricType, MetricCategory, MetricUnit
from .metrics import Metric, Counter, Gauge, Histogram, Timer
from .metrics_registry import MetricsRegistry
from .metrics_manager import MetricsManager
from .prometheus import (
    get_metrics_manager,
    start_all_metrics_managers,
    stop_all_metrics_managers,
    get_all_metrics,
    get_prometheus_metrics
)

# Existing imports
from .collector import MetricsCollector, SessionData
from .storage.base import MetricsStorage
from .storage.sqlite import SQLiteMetricsStorage
from .storage.json_file import JSONFileMetricsStorage
from .analysis.spectral_analyzer import SpectralAnalyzer
from .integration import MetricsManager as SpectralMetricsManager
from .utils import (
    session_to_dict,
    sessions_to_dicts,
    interpret_bifurcation_proximity,
    interpret_parameter_sensitivity,
    interpret_hysteresis
)

# Analysis specific imports for direct access
from .analysis.bifurcation import calculate_bifurcation_proximity
from .analysis.parameter_sensitivity import calculate_control_parameter_sensitivity
from .analysis.hysteresis import calculate_hysteresis_detection
from .analysis.catastrophe_points import identify_catastrophe_points
from .analysis.architectural_elasticity import find_architectural_elasticity

__all__ = [
    # Core metric classes
    "MetricType",
    "MetricCategory",
    "MetricUnit",
    "Metric",
    "Counter",
    "Gauge",
    "Histogram",
    "Timer",
    "MetricsRegistry",
    "MetricsManager",
    
    # Prometheus integration
    "get_metrics_manager",
    "start_all_metrics_managers",
    "stop_all_metrics_managers",
    "get_all_metrics",
    "get_prometheus_metrics",
    
    # Core classes
    "MetricsCollector",
    "SessionData",
    "MetricsStorage",
    "SQLiteMetricsStorage",
    "JSONFileMetricsStorage",
    "SpectralAnalyzer",
    "SpectralMetricsManager",
    
    # Utility functions
    "session_to_dict",
    "sessions_to_dicts",
    "interpret_bifurcation_proximity",
    "interpret_parameter_sensitivity",
    "interpret_hysteresis",
    
    # Analysis functions
    "calculate_bifurcation_proximity",
    "calculate_control_parameter_sensitivity",
    "calculate_hysteresis_detection",
    "identify_catastrophe_points",
    "find_architectural_elasticity"
]