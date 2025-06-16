#!/usr/bin/env python3
"""
Component Registry Module

This module provides the main registry for tracking component registrations and instances.
It re-exports functionality from the modular registry implementation.
"""

# Re-export from modular implementation
from .registry.core import ComponentRegistry
from .registry.components import get_component_info, get_all_components 
from .registry.persistence import load_registrations as _load_registrations
from .registry.persistence import save_registrations as _save_registrations
from .registry.monitoring import check_for_automatic_recovery

# Note: we can't directly assign instance methods to module-level functions
# The original functions are now methods of ComponentRegistry