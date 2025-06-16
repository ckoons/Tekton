#!/usr/bin/env python3
"""
Component Registry Package

This package provides modular implementations of registry functionality.
"""

from .core import ComponentRegistry
from .components import (
    get_component_info,
    get_all_components
)
from .persistence import (
    load_registrations,
    save_registrations
)
from .monitoring import (
    check_for_automatic_recovery
)

__all__ = [
    "ComponentRegistry",
    "get_component_info",
    "get_all_components",
    "load_registrations",
    "save_registrations",
    "check_for_automatic_recovery"
]