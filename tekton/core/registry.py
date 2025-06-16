#!/usr/bin/env python3
"""
Component Registry Operations Module

This module provides functions for registry operations like
loading, saving and tracking component registrations.
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple

from .lifecycle import (
    ComponentState, 
    ComponentRegistration
)

logger = logging.getLogger("tekton.registry")


def _load_registrations(data_dir: str) -> Dict[str, ComponentRegistration]:
    """
    Load component registrations from disk.
    
    Args:
        data_dir: Directory to load from
        
    Returns:
        Dictionary of component registrations
    """
    components = {}
    instances = {}
    
    registry_file = os.path.join(data_dir, "registry.json")
    if os.path.exists(registry_file):
        try:
            with open(registry_file, 'r') as f:
                data = json.load(f)
            
            for component_data in data.get("components", []):
                try:
                    component = ComponentRegistration.from_dict(component_data)
                    components[component.component_id] = component
                    instances[component.component_id] = {
                        "instance_uuid": component.instance_uuid,
                        "last_heartbeat": time.time(),
                        "state": component.state
                    }
                except Exception as e:
                    logger.error(f"Error loading component registration: {e}")
            
            logger.info(f"Loaded {len(components)} component registrations")
        except Exception as e:
            logger.error(f"Error loading registry file: {e}")
    
    return components, instances


async def _save_registrations(components: Dict[str, ComponentRegistration], data_dir: str) -> None:
    """
    Save component registrations to disk.
    
    Args:
        components: Dictionary of component registrations
        data_dir: Directory to save to
    """
    registry_file = os.path.join(data_dir, "registry.json")
    try:
        with open(registry_file, 'w') as f:
            data = {
                "timestamp": time.time(),
                "components": [comp.to_dict() for comp in components.values()]
            }
            json.dump(data, f, indent=2)
            
        logger.debug(f"Saved {len(components)} component registrations")
    except Exception as e:
        logger.error(f"Error saving registry file: {e}")


async def register_component(
    components: Dict[str, ComponentRegistration],
    instances: Dict[str, Dict[str, Any]],
    registration: ComponentRegistration,
    data_dir: str
) -> Tuple[bool, str]:
    """
    Register a component with the registry.
    
    Args:
        components: Dictionary of component registrations
        instances: Dictionary of component instances
        registration: ComponentRegistration object 
        data_dir: Directory for persistent storage
        
    Returns:
        Tuple of (success, message)
    """
    component_id = registration.component_id
    instance_uuid = registration.instance_uuid
    
    # Check for existing registration
    if component_id in components:
        existing = components[component_id]
        
        # If existing instance is different
        if existing.instance_uuid != instance_uuid:
            # Check if more recent
            if existing.start_time > registration.start_time:
                logger.warning(f"Rejecting registration for {component_id} - newer instance exists")
                return False, "A newer instance is already registered"
            else:
                # This is a newer instance, stop tracking the old one
                logger.info(f"Replacing instance of {component_id} with newer instance")
        
    # Register the component
    components[component_id] = registration
    instances[component_id] = {
        "instance_uuid": instance_uuid,
        "last_heartbeat": time.time(),
        "state": registration.state
    }
    
    # Save updated registrations
    await _save_registrations(components, data_dir)
    
    logger.info(f"Registered component {component_id} (instance {instance_uuid})")
    return True, "Registration successful"


async def update_component_state(
    components: Dict[str, ComponentRegistration],
    instances: Dict[str, Dict[str, Any]],
    component_id: str,
    instance_uuid: str,
    state: str,
    metadata: Optional[Dict[str, Any]] = None,
    data_dir: str = None
) -> Tuple[bool, str]:
    """
    Update the state of a component.
    
    Args:
        components: Dictionary of component registrations
        instances: Dictionary of component instances
        component_id: Component ID
        instance_uuid: Instance UUID
        state: ComponentState value
        metadata: Optional additional metadata
        data_dir: Directory for persistent storage
        
    Returns:
        Tuple of (success, message)
    """
    # Check if component is registered
    if component_id not in components:
        return False, "Component not registered"
        
    # Check if instance UUID matches
    if components[component_id].instance_uuid != instance_uuid:
        return False, "Instance UUID mismatch"
        
    # Get current state
    current_state = components[component_id].state
    
    # Validate state transition
    if not ComponentState.validate_transition(current_state, state):
        logger.warning(f"Invalid state transition for {component_id}: {current_state} -> {state}")
        return False, f"Invalid state transition: {current_state} -> {state}"
        
    # Update state
    components[component_id].state = state
    instances[component_id]["state"] = state
    instances[component_id]["last_heartbeat"] = time.time()
    
    if metadata:
        instances[component_id].setdefault("metadata", {}).update(metadata)
        
    # Save updated registrations if data dir provided
    if data_dir:
        await _save_registrations(components, data_dir)
    
    logger.info(f"Updated component {component_id} state: {current_state} -> {state}")
    return True, "State updated"


async def get_component_info(
    components: Dict[str, ComponentRegistration],
    instances: Dict[str, Dict[str, Any]],
    component_id: str
) -> Optional[Dict[str, Any]]:
    """
    Get information about a component.
    
    Args:
        components: Dictionary of component registrations
        instances: Dictionary of component instances
        component_id: Component ID
        
    Returns:
        Component information or None if not found
    """
    if component_id not in components:
        return None
        
    component = components[component_id]
    instance = instances.get(component_id, {})
    
    return {
        "component_id": component.component_id,
        "component_name": component.component_name,
        "component_type": component.component_type,
        "instance_uuid": component.instance_uuid,
        "version": component.version,
        "capabilities": component.capabilities,
        "state": component.state,
        "start_time": component.start_time,
        "last_heartbeat": instance.get("last_heartbeat"),
        "metadata": {
            **component.metadata,
            **(instance.get("metadata", {}))
        }
    }


async def monitor_component_health(
    components: Dict[str, ComponentRegistration],
    instances: Dict[str, Dict[str, Any]],
    heartbeat_timeout: int = 30,
    data_dir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Check component health and mark failed components.
    
    Args:
        components: Dictionary of component registrations
        instances: Dictionary of component instances
        heartbeat_timeout: Timeout in seconds
        data_dir: Directory for persistent storage
        
    Returns:
        List of components marked as failed
    """
    now = time.time()
    failed_components = []
    
    # Check active components
    for component_id, component in list(components.items()):
        # Skip components that are not active
        if component.state not in [ComponentState.READY.value, ComponentState.DEGRADED.value]:
            continue
            
        instance = instances.get(component_id, {})
        last_heartbeat = instance.get("last_heartbeat", 0)
        
        if now - last_heartbeat > heartbeat_timeout:
            logger.warning(f"Component {component_id} missed heartbeats, marking as failed")
            
            # Mark as failed
            await update_component_state(
                components=components,
                instances=instances,
                component_id=component_id,
                instance_uuid=component.instance_uuid,
                state=ComponentState.FAILED.value,
                metadata={
                    "error": f"Missed heartbeats (last: {last_heartbeat})",
                    "failure_reason": "heartbeat_timeout"
                },
                data_dir=data_dir
            )
            
            failed_components.append(component_id)
    
    return failed_components