#!/usr/bin/env python3
"""
Component health monitoring functionality.

This module provides functionality for monitoring component health
and identifying components that have missed heartbeats.
"""

import time
import logging
from typing import Dict, List, Any

from ..lifecycle import ComponentState

logger = logging.getLogger("tekton.component_lifecycle.monitor")


async def monitor_component_health(
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]],
    heartbeat_timeout: int = 30
) -> List[str]:
    """
    Monitor component health and identify components that have missed heartbeats.
    
    Args:
        components: Component registrations
        instances: Component instances
        heartbeat_timeout: Timeout in seconds
        
    Returns:
        List of component IDs that have missed heartbeats
    """
    failed_components = []
    current_time = time.time()
    
    for component_id, instance_data in instances.items():
        # Skip components that are not in active states
        if component_id not in components:
            continue
            
        component = components[component_id]
        if not ComponentState.is_active(component.state):
            continue
            
        # Check last heartbeat
        last_heartbeat = instance_data.get("last_heartbeat", 0)
        if last_heartbeat > 0 and current_time - last_heartbeat > heartbeat_timeout:
            logger.warning(f"Component {component_id} has missed heartbeats (last: {current_time - last_heartbeat:.1f}s ago)")
            failed_components.append(component_id)
            
    return failed_components
