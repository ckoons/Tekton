#!/usr/bin/env python3
"""
Component Lifecycle Module

This module provides enhanced component state management and lifecycle control
to prevent deadlocks during the startup process.

This file is maintained for backward compatibility.
Use tekton.core.component_lifecycle package instead for new code.
"""

# Re-export from the component_lifecycle package
from .component_lifecycle.registry import ComponentRegistry
from .component_lifecycle.healthcheck import (
    monitor_component_health, 
    process_heartbeat,
    attempt_component_recovery
)
from .component_lifecycle.capability import (
    register_capability,
    register_fallback_handler,
    execute_with_fallback,
    get_fallback_status
)
from .component_lifecycle.readiness import (
    register_readiness_condition,
    check_readiness_conditions,
    mark_component_ready,
    wait_for_component_ready,
    wait_for_dependencies
)

# Re-export dependencies for backward compatibility
from .lifecycle import (
    ComponentState,
    ReadinessCondition,
    ComponentRegistration,
    PersistentMessageQueue
)
from .dependency import DependencyResolver
from .graceful_degradation import (
    GracefulDegradationManager,
    CircuitBreaker,
    CapabilityFallback,
    NoFallbackAvailableError
)

__all__ = [
    # Component lifecycle package
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
    "wait_for_dependencies",
    
    # Dependencies
    "ComponentState",
    "ReadinessCondition",
    "ComponentRegistration",
    "PersistentMessageQueue",
    "DependencyResolver",
    "GracefulDegradationManager",
    "CircuitBreaker",
    "CapabilityFallback",
    "NoFallbackAvailableError"
]