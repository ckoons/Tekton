"""
Component Capabilities Operations

This module provides functions for managing component capabilities.
"""

import logging
from typing import Dict, Any, Optional, List, Callable, Awaitable

from tekton.core.graceful_degradation import GracefulDegradationManager
from ...capability import (
    register_capability,
    register_fallback_handler,
    execute_with_fallback,
    get_fallback_status,
    get_fallback_handler
)

logger = logging.getLogger("tekton.component_lifecycle.registry.operations.capabilities")


async def register_capability_internal(
    components: Dict[str, Any],
    degradation_manager: GracefulDegradationManager,
    component_id: str,
    capability_name: str,
    capability_level: int = 100,
    description: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    handler: Optional[Callable] = None,
    data_dir: Optional[str] = None
) -> bool:
    """
    Register a capability for a component.
    
    Args:
        components: Component registrations
        degradation_manager: Graceful degradation manager
        component_id: Component ID
        capability_name: Name of the capability
        capability_level: Level of capability (higher is better)
        description: Optional description
        parameters: Optional parameters for the capability
        handler: Optional handler function
        data_dir: Optional directory for persistent storage
        
    Returns:
        True if registered successfully
    """
    return await register_capability(
        components,
        degradation_manager,
        component_id,
        capability_name,
        capability_level,
        description,
        parameters,
        handler,
        data_dir
    )


async def register_fallback_handler_internal(
    components: Dict[str, Any],
    degradation_manager: GracefulDegradationManager,
    fallback_handlers: Dict[str, Dict[str, Callable]],
    component_id: str,
    capability_name: str,
    provider_id: str,
    fallback_handler: Callable,
    capability_level: int = 50
) -> bool:
    """
    Register a fallback handler for a capability.
    
    Args:
        components: Component registrations
        degradation_manager: Graceful degradation manager
        fallback_handlers: Dictionary of fallback handlers
        component_id: Component ID that requires the capability
        capability_name: Name of the capability
        provider_id: ID of the component providing the fallback
        fallback_handler: Function to call for fallback
        capability_level: Level of capability (higher is better)
        
    Returns:
        True if registered successfully
    """
    return await register_fallback_handler(
        components,
        degradation_manager,
        fallback_handlers,
        component_id,
        capability_name,
        provider_id,
        fallback_handler,
        capability_level
    )


async def execute_with_fallback_internal(
    degradation_manager: GracefulDegradationManager,
    fallback_handlers: Dict[str, Dict[str, Callable]],
    component_id: str,
    capability_name: str,
    *args, **kwargs
) -> Any:
    """
    Execute a capability with fallback support.
    
    Args:
        degradation_manager: Graceful degradation manager
        fallback_handlers: Dictionary of fallback handlers
        component_id: ID of the component
        capability_name: Name of the capability
        *args: Arguments for the handler
        **kwargs: Keyword arguments for the handler
        
    Returns:
        Result from handler
    """
    return await execute_with_fallback(
        degradation_manager,
        fallback_handlers,
        component_id,
        capability_name,
        *args, **kwargs
    )


def get_fallback_status_internal(
    degradation_manager: GracefulDegradationManager,
    component_id: Optional[str] = None,
    capability_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get status of registered fallbacks.
    
    Args:
        degradation_manager: Graceful degradation manager
        component_id: Optional component ID filter
        capability_name: Optional capability name filter
        
    Returns:
        Status information for fallbacks
    """
    return get_fallback_status(
        degradation_manager,
        component_id,
        capability_name
    )


def get_fallback_handler_internal(
    fallback_handlers: Dict[str, Dict[str, Callable]],
    component_id: str,
    capability_name: str
) -> Optional[Callable]:
    """
    Get a fallback handler for a capability.
    
    Args:
        fallback_handlers: Dictionary of fallback handlers
        component_id: Component ID
        capability_name: Name of the capability
        
    Returns:
        Fallback handler or None
    """
    return get_fallback_handler(
        fallback_handlers,
        component_id,
        capability_name
    )