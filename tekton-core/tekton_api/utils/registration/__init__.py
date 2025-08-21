"""
Tekton Component Registration Utilities

This module provides utilities for registering Tekton components with the
Hermes service registry. It loads component configurations from YAML files
and handles registration, heartbeat, and unregistration.
"""

from .registry import register_component, unregister_component, get_registration_status
from .config import load_component_config, validate_component_config
from .models import ComponentConfig, CapabilityConfig, MethodConfig, ParameterConfig

__all__ = [
    'register_component',
    'unregister_component',
    'get_registration_status',
    'load_component_config',
    'validate_component_config',
    'ComponentConfig',
    'CapabilityConfig',
    'MethodConfig',
    'ParameterConfig',
]