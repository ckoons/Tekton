#!/usr/bin/env python3
"""
Component Capability Module

This module provides functionality for registering and managing
component capabilities and fallback handlers.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable

from ..graceful_degradation import GracefulDegradationManager, NoFallbackAvailableError
from ..registry import _save_registrations

logger = logging.getLogger("tekton.component_lifecycle.capability")


async def register_capability(
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
    if component_id not in components:
        logger.error(f"Cannot register capability for unknown component: {component_id}")
        return False
    
    # Get component registration
    component = components[component_id]
    
    # Check if capability already exists
    existing_capability = None
    for capability in component.capabilities:
        if capability.get("name") == capability_name:
            existing_capability = capability
            break
    
    # Create or update capability
    if existing_capability:
        # Update existing capability
        existing_capability.update({
            "level": capability_level,
            "description": description or existing_capability.get("description", ""),
            "parameters": parameters or existing_capability.get("parameters", {})
        })
        logger.info(f"Updated capability {capability_name} for component {component_id}")
    else:
        # Add new capability
        component.capabilities.append({
            "name": capability_name,
            "level": capability_level,
            "description": description or f"Capability: {capability_name}",
            "parameters": parameters or {}
        })
        logger.info(f"Added capability {capability_name} for component {component_id}")
    
    # Register handler if provided
    if handler:
        degradation_manager.register_capability_fallback(
            component_id=component_id,
            capability_name=capability_name,
            provider_id=component_id,  # Self as provider
            handler=handler,
            level=capability_level
        )
    
    # Save updated registrations
    if data_dir:
        await _save_registrations(components, data_dir)
    
    return True


async def register_fallback_handler(
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
    if component_id not in components:
        logger.error(f"Cannot register fallback for unknown component: {component_id}")
        return False
    
    # Register with graceful degradation manager
    degradation_manager.register_capability_fallback(
        component_id=component_id,
        capability_name=capability_name,
        provider_id=provider_id,
        handler=fallback_handler,
        level=capability_level
    )
    
    # Legacy fallback registry for backward compatibility
    if component_id not in fallback_handlers:
        fallback_handlers[component_id] = {}
    
    fallback_handlers[component_id][capability_name] = fallback_handler
    logger.info(f"Registered fallback for {component_id}.{capability_name} from {provider_id} (level {capability_level})")
    
    return True


async def execute_with_fallback(
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
        
    Raises:
        NoFallbackAvailableError: If no fallback is available
    """
    try:
        return await degradation_manager.execute_with_fallback(
            component_id=component_id,
            capability_name=capability_name,
            *args, **kwargs
        )
    except NoFallbackAvailableError:
        # Try legacy fallback as a last resort
        if component_id in fallback_handlers and capability_name in fallback_handlers[component_id]:
            handler = fallback_handlers[component_id][capability_name]
            if asyncio.iscoroutinefunction(handler):
                return await handler(*args, **kwargs)
            else:
                return handler(*args, **kwargs)
        else:
            raise


def get_fallback_status(
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
    return degradation_manager.get_fallback_status(
        component_id=component_id,
        capability_name=capability_name
    )


def get_fallback_handler(
    fallback_handlers: Dict[str, Dict[str, Callable]],
    component_id: str,
    capability_name: str
) -> Optional[Callable]:
    """
    Get a fallback handler for a capability (legacy method).
    
    Args:
        fallback_handlers: Dictionary of fallback handlers
        component_id: Component ID
        capability_name: Name of the capability
        
    Returns:
        Fallback handler or None
    """
    return fallback_handlers.get(component_id, {}).get(capability_name)