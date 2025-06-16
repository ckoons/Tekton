"""
Component Heartbeat Operations

This module provides functions for monitoring component health and processing heartbeats.
"""

import time
import logging
from typing import Dict, List, Any, Optional, Tuple

from ....lifecycle import ComponentState
from ..persistence import save_registrations
from ..monitoring import check_for_automatic_recovery
from ...healthcheck import monitor_component_health, process_heartbeat

logger = logging.getLogger("tekton.component_lifecycle.registry.operations.heartbeat")


async def monitor_components(
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]],
    data_dir: Optional[str] = None,
    heartbeat_timeout: int = 30
) -> None:
    """
    Monitor component health and mark failed components with enhanced degradation.
    
    Args:
        components: Component registrations
        instances: Component instances
        data_dir: Optional directory for persistent storage
        heartbeat_timeout: Timeout in seconds before marking component as failed
    """
    # Create copies to minimize lock contention
    components_copy = components.copy()
    instances_copy = instances.copy()
    
    # Check components
    failed = await monitor_component_health(
        components=components_copy,
        instances=instances_copy,
        heartbeat_timeout=heartbeat_timeout
    )
    
    # Update components if any failed
    if failed:
        # Update components with failed status
        for component_id in failed:
            if component_id in components:
                component = components[component_id]
                
                # Only update if still active (might have changed)
                if ComponentState.is_active(component.state):
                    # First mark as degraded if not already
                    if component.state != ComponentState.DEGRADED.value:
                        # First mark as degraded
                        component.update_state(
                            ComponentState.DEGRADED.value,
                            "degradation.missed_heartbeats",
                            "Component missing heartbeats but may recover"
                        )
                        
                        instances[component_id]["state"] = ComponentState.DEGRADED.value
                        instances[component_id].setdefault("metadata", {}).update({
                            "warning": "Missed heartbeats",
                            "degradation_reason": "heartbeat_missing",
                            "degradation_time": time.time()
                        })
                        
                        logger.warning(f"Component {component_id} degraded due to missed heartbeats")
                        
                        # Try to save (but don't fail if we can't)
                        try:
                            if data_dir:
                                await save_registrations(components, data_dir)
                        except Exception as e:
                            logger.error(f"Error saving degraded state: {e}")
                    else:
                        # Already degraded, now mark as failed
                        component.update_state(
                            ComponentState.FAILED.value,
                            "failure.persistent_heartbeat_failure",
                            "Component persistently missing heartbeats"
                        )
                        
                        instances[component_id]["state"] = ComponentState.FAILED.value
                        instances[component_id].setdefault("metadata", {}).update({
                            "error": "Persistent missed heartbeats",
                            "failure_reason": "heartbeat_timeout",
                            "failure_time": time.time()
                        })
                        
                        logger.error(f"Component {component_id} marked as failed after degraded state")
                        
                        # Try to save (but don't fail if we can't)
                        try:
                            if data_dir:
                                await save_registrations(components, data_dir)
                        except Exception as e:
                            logger.error(f"Error saving failed state: {e}")
    
    # Check for components to recover
    recovery_candidates = await check_for_automatic_recovery(components, instances)
    
    # Return candidates to be recovered by the registry
    return recovery_candidates


async def process_heartbeat_internal(
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]],
    component_id: str,
    instance_uuid: str,
    sequence: int,
    state: Optional[str] = None,
    health_metrics: Optional[Dict[str, float]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    details: Optional[str] = None,
    data_dir: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Process a heartbeat from a component with enhanced health metrics.
    
    Args:
        components: Component registrations
        instances: Component instances
        component_id: Component ID
        instance_uuid: Instance UUID
        sequence: Heartbeat sequence number
        state: Optional current state
        health_metrics: Optional health metrics
        metadata: Optional additional metadata
        reason: Optional reason for state change
        details: Optional details
        data_dir: Optional directory for persistent storage
        
    Returns:
        Tuple of (success, message)
    """
    return await process_heartbeat(
        components,
        instances,
        component_id,
        instance_uuid,
        sequence,
        state,
        health_metrics,
        metadata,
        reason,
        details,
        data_dir
    )