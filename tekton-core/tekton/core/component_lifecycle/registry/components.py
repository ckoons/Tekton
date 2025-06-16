#!/usr/bin/env python3
"""
Component Information Module

This module provides functions for retrieving component information.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("tekton.component_lifecycle.registry.components")


async def get_component_info(components: Dict[str, Any], instances: Dict[str, Dict[str, Any]], component_id: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a component.
    
    Args:
        components: Component registrations
        instances: Component instances
        component_id: Component ID
        
    Returns:
        Component information or None if not found
    """
    if component_id not in components:
        return None
        
    component = components[component_id]
    instance_data = instances.get(component_id, {})
    
    # Combine component registration and instance data
    return {
        "component_id": component_id,
        "component_name": component.component_name,
        "component_type": component.component_type,
        "version": component.version,
        "state": component.state,
        "instance_uuid": component.instance_uuid,
        "capabilities": component.capabilities,
        "dependencies": component.dependencies,
        "metadata": component.metadata,
        "recovery_attempts": component.recovery_attempts,
        "health_metrics": instance_data.get("health_metrics", {}),
        "registration_time": instance_data.get("registration_time", 0),
        "last_update": instance_data.get("last_update", 0),
        "last_heartbeat": instance_data.get("last_heartbeat", 0),
        "ready_time": instance_data.get("ready_time", 0)
    }


async def get_all_components(components: Dict[str, Any], instances: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get information about all components.
    
    Args:
        components: Component registrations
        instances: Component instances
        
    Returns:
        List of component information dictionaries
    """
    result = []
    
    for component_id in components:
        info = await get_component_info(components, instances, component_id)
        if info:
            result.append(info)
            
    return result