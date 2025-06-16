"""
Component Registration Operations

This module provides functions for component registration and state updates.
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple

from ....lifecycle import ComponentRegistration
from ..persistence import save_registrations

logger = logging.getLogger("tekton.component_lifecycle.registry.operations.registration")


async def register_component(
    components: Dict[str, ComponentRegistration],
    instances: Dict[str, Dict[str, Any]],
    registration: ComponentRegistration,
    data_dir: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Register a component with the registry.
    
    Args:
        components: Component registrations dictionary
        instances: Component instances dictionary
        registration: ComponentRegistration object
        data_dir: Optional directory for persistent storage
        
    Returns:
        Tuple of (success, message)
    """
    if registration.component_id in components:
        existing = components[registration.component_id]
        
        # Check for duplicate but allow re-registration with same UUID
        if existing.instance_uuid != registration.instance_uuid:
            return False, "Component ID already registered with different instance UUID"
            
        # Update registration
        components[registration.component_id] = registration
        instances[registration.component_id] = {
            "instance_uuid": registration.instance_uuid,
            "state": registration.state,
            "registration_time": time.time(),
            "last_update": time.time(),
            "metadata": registration.metadata.copy()
        }
        
        logger.info(f"Updated registration for {registration.component_id}")
        await save_registrations(components, data_dir)
        return True, "Registration updated"
    
    # New registration
    components[registration.component_id] = registration
    instances[registration.component_id] = {
        "instance_uuid": registration.instance_uuid,
        "state": registration.state,
        "registration_time": time.time(),
        "last_update": time.time(),
        "metadata": registration.metadata.copy()
    }
    
    logger.info(f"Registered new component: {registration.component_id} ({registration.component_name})")
    await save_registrations(components, data_dir)
    return True, "Registration successful"


async def update_component_state(
    components: Dict[str, ComponentRegistration], 
    instances: Dict[str, Dict[str, Any]],
    component_id: str, 
    instance_uuid: str,
    state: str,
    metadata: Optional[Dict[str, Any]] = None,
    data_dir: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Update the state of a component.
    
    Args:
        components: Component registrations dictionary
        instances: Component instances dictionary
        component_id: Component ID
        instance_uuid: Instance UUID
        state: ComponentState value
        metadata: Optional additional metadata
        data_dir: Optional directory for persistent storage
        
    Returns:
        Tuple of (success, message)
    """
    # Check if component is registered
    if component_id not in components:
        return False, "Component not registered"
        
    # Check if instance UUID matches
    if components[component_id].instance_uuid != instance_uuid:
        return False, "Instance UUID mismatch"
        
    # Get component registration
    component = components[component_id]
    
    # Update state
    success = component.update_state(state)
    
    if not success:
        return False, f"Invalid state transition: {component.state} -> {state}"
        
    # Update instance data
    instances[component_id]["state"] = state
    instances[component_id]["last_update"] = time.time()
    
    # Update metadata if provided
    if metadata:
        component.metadata.update(metadata)
        instances[component_id].setdefault("metadata", {}).update(metadata)
        
    # Save updated registrations
    await save_registrations(components, data_dir)
    
    return True, f"Updated component state: {state}"