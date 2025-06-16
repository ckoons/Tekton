"""Dashboard components package.

This package contains modular components for the Tekton monitoring dashboard.
"""

# Import components for easy access
from .resource_integration import ResourceIntegration, get_resource_integration
from .health_metrics import HealthMetrics, generate_component_health, calculate_health_score
from .dependency import DependencyManager, build_dependency_graph, detect_dependency_cycles
from .spectral import SpectralAnalyzer, run_spectral_analysis, extract_spectral_metrics
from .server import DashboardServer, start_server, register_routes

__all__ = [
    # Resource integration
    'ResourceIntegration',
    'get_resource_integration',
    
    # Health metrics
    'HealthMetrics',
    'generate_component_health',
    'calculate_health_score',
    
    # Dependency management
    'DependencyManager',
    'build_dependency_graph',
    'detect_dependency_cycles',
    
    # Spectral analysis
    'SpectralAnalyzer',
    'run_spectral_analysis',
    'extract_spectral_metrics',
    
    # Server
    'DashboardServer',
    'start_server',
    'register_routes'
]