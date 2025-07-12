"""
Tekton Core Module

This module provides the core functionality for the Tekton framework.
"""

from tekton.core.startup_instructions import StartUpInstructions
from tekton.core.startup_process import StartUpProcess, ComponentStatus
from tekton.core.startup_coordinator import StartUpCoordinator, EnhancedStartUpCoordinator
from tekton.core.component_registration import ComponentRegistration
from tekton.core.component_discovery import ComponentDiscovery
from tekton.core.heartbeat_monitor import HeartbeatMonitor, ComponentHeartbeat
from tekton.core.tekton_core_component import TektonCoreComponent

# Import from refactored modules
from tekton.core.lifecycle import (
    ComponentState,
    ReadinessCondition,
    PersistentMessageQueue
)
from tekton.core.dependency import DependencyResolver
from tekton.core.component_lifecycle import ComponentRegistry
from tekton.core.startup_handler import (
    InstructionHandler,
    execute_start_func,
    notify_dependent_components,
    handle_startup_instructions
)
from tekton.core.startup_manager import (
    get_component_status,
    synchronize_with_service_registry,
    start_components_in_order,
    start_components_parallel
)

try:
    from tekton.core.latent_reasoning import LatentReasoningMixin
except ImportError:
    # Latent reasoning might not be available
    pass

__all__ = [
    'StartUpInstructions',
    'StartUpProcess',
    'StartUpCoordinator',
    'EnhancedStartUpCoordinator',
    'ComponentStatus',
    'ComponentRegistration',
    'ComponentDiscovery',
    'HeartbeatMonitor',
    'ComponentHeartbeat',
    'TektonCoreComponent',
    # New components
    'ComponentState',
    'ReadinessCondition',
    'PersistentMessageQueue',
    'DependencyResolver',
    'ComponentRegistry',
    'InstructionHandler',
    'execute_start_func',
    'notify_dependent_components',
    'handle_startup_instructions',
    'get_component_status',
    'synchronize_with_service_registry',
    'start_components_in_order',
    'start_components_parallel'
]