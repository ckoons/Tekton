"""
Analysis tools for Tekton metrics.

This module provides tools for analyzing metrics data collected 
during system operation, including spectral analysis and catastrophe theory metrics.
"""

from .spectral_analyzer import SpectralAnalyzer, EnhancedSpectralAnalyzer
from .bifurcation import calculate_bifurcation_proximity
from .parameter_sensitivity import calculate_control_parameter_sensitivity
from .hysteresis import calculate_hysteresis_detection
from .catastrophe_points import identify_catastrophe_points
from .architectural_elasticity import find_architectural_elasticity

__all__ = [
    "SpectralAnalyzer",
    "EnhancedSpectralAnalyzer",
    "calculate_bifurcation_proximity",
    "calculate_control_parameter_sensitivity",
    "calculate_hysteresis_detection",
    "identify_catastrophe_points",
    "find_architectural_elasticity",
]