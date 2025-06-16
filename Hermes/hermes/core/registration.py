"""
Unified Registration Protocol - Central registration for all Tekton components.

This module implements the Unified Registration Protocol (URP) for Tekton components,
providing a single entry point for component registration, authentication, and
propagation of registration information to other Tekton systems.

Note: This module is maintained for backward compatibility.
For new code, please import directly from hermes.core.registration.
"""

# Re-export all classes for backward compatibility
from hermes.core.registration.tokens import RegistrationToken
from hermes.core.registration.manager import RegistrationManager
from hermes.core.registration.client import RegistrationClient
from hermes.core.registration.utils import (
    generate_component_id,
    is_token_valid,
    format_component_info,
    calculate_token_lifetime
)

__all__ = [
    "RegistrationToken",
    "RegistrationManager",
    "RegistrationClient",
    "generate_component_id",
    "is_token_valid", 
    "format_component_info",
    "calculate_token_lifetime"
]