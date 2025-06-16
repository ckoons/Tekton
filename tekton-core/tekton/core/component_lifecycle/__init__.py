"""
Component Lifecycle Module

This package provides enhanced component state management and lifecycle control
to prevent deadlocks during the startup process.
"""

from .registry import ComponentRegistry
from .monitor import monitor_component_health
from .heartbeat import process_heartbeat
from .recovery import attempt_component_recovery
from .capability import (
    register_capability,
    register_fallback_handler,
    execute_with_fallback,
    get_fallback_status
)
from .readiness import (
    register_readiness_condition,
    check_readiness_conditions,
    mark_component_ready,
    wait_for_component_ready,
    wait_for_dependencies
)

__all__ = [
    "ComponentRegistry",
    "monitor_component_health",
    "process_heartbeat",
    "attempt_component_recovery",
    "register_capability",
    "register_fallback_handler",
    "execute_with_fallback",
    "get_fallback_status",
    "register_readiness_condition",
    "check_readiness_conditions",
    "mark_component_ready",
    "wait_for_component_ready",
    "wait_for_dependencies"
]