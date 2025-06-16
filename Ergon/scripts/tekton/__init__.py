"""
Tekton Suite Launcher - Unified launcher for the Tekton ecosystem.

This package orchestrates the startup of all Tekton components in the correct order,
ensuring that dependencies are properly initialized before dependent services.
"""

# Re-export the main entry point for easier importing
from .main import main

# Re-export core functionality for programmatic access
from .components import COMPONENTS
from .startup import start_component, start_all_components
from .shutdown import stop_component, stop_all_components
from .status import get_component_status

__all__ = [
    'main',
    'COMPONENTS',
    'start_component',
    'start_all_components',
    'stop_component',
    'stop_all_components',
    'get_component_status'
]