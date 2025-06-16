#!/usr/bin/env python3
"""
Component heartbeat processing functionality.

This module provides functionality for processing heartbeats from components
and updating their state and health metrics.
"""

import time
import logging
from typing import Dict, Optional, Tuple, Any

from ..lifecycle import ComponentState
from ..registry import _save_registrations

logger = logging.getLogger("tekton.component_lifecycle.heartbeat")


async def process_heartbeat(
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
        health_metrics: Optional health metrics (CPU, memory, latency, etc.)
        metadata: Optional additional metadata
        reason: Optional reason for state change
        details: Optional details about component status
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
    
    # Update last heartbeat time
    instances[component_id]["last_heartbeat"] = time.time()
    
    # Check and update sequence number
    last_sequence = instances[component_id].get("last_sequence", -1)
    
    if sequence <= last_sequence and sequence != 0:
        logger.warning(f"Out-of-order heartbeat for {component_id}: {sequence} <= {last_sequence}")
        
    instances[component_id]["last_sequence"] = sequence
    
    # Update health metrics if provided
    if health_metrics:
        # Update component health metrics
        component.update_health_metrics(health_metrics)
        
        # Store in instance data
        instances[component_id].setdefault("health_metrics", {}).update(health_metrics)
        
        # Check for automatic state transition based on metrics
        if _should_degrade_from_metrics(component_id, components, health_metrics):
            if component.state == ComponentState.READY.value or component.state == ComponentState.ACTIVE.value:
                # Auto-transition to DEGRADED due to metrics
                auto_reason = "degradation.metric_threshold"
                auto_details = "Automatic transition to DEGRADED based on health metrics"
                success = component.update_state(ComponentState.DEGRADED.value, auto_reason, auto_details)
                
                if success:
                    instances[component_id]["state"] = ComponentState.DEGRADED.value
                    logger.warning(f"Auto-degraded {component_id} based on health metrics")
    
    # Update state if provided
    if state and state != component.state:
        # Use the component's state transition method
        success = component.update_state(state, reason, details)
        
        if success:
            instances[component_id]["state"] = state
            logger.info(f"Updated component {component_id} state from heartbeat: {component.state} -> {state}")
            
            # Persist state update
            if data_dir:
                await _save_registrations(components, data_dir)
        else:
            logger.warning(f"Invalid state transition in heartbeat: {component.state} -> {state}")
    
    # Update metadata if provided
    if metadata:
        component.metadata.update(metadata)
        instances[component_id].setdefault("metadata", {}).update(metadata)
        
    return True, "Heartbeat processed"


def _should_degrade_from_metrics(
    component_id: str,
    components: Dict[str, Any],
    health_metrics: Dict[str, float]
) -> bool:
    """
    Determine if a component should be degraded based on health metrics.
    
    Args:
        component_id: Component ID
        components: Component registrations
        health_metrics: Health metrics
        
    Returns:
        True if component should be degraded
    """
    # Define thresholds for auto-degradation
    thresholds = {
        "cpu_usage": 0.9,        # 90% CPU usage
        "memory_usage": 0.85,    # 85% memory usage
        "error_rate": 0.1,       # 10% error rate
        "request_latency": 2000  # 2000ms latency
    }
    
    # Get component type-specific thresholds
    component_type = components[component_id].component_type
    
    type_thresholds = {
        "compute": {"cpu_usage": 0.95, "memory_usage": 0.9},
        "database": {"cpu_usage": 0.8, "memory_usage": 0.8},
        "api": {"request_latency": 1000, "error_rate": 0.05},
        "web": {"request_latency": 3000, "error_rate": 0.15}
    }
    
    # Override default thresholds with type-specific ones
    if component_type in type_thresholds:
        for metric, value in type_thresholds[component_type].items():
            thresholds[metric] = value
    
    # Check if any threshold is exceeded
    for metric, threshold in thresholds.items():
        if metric in health_metrics and health_metrics[metric] > threshold:
            logger.info(f"Component {component_id} exceeds {metric} threshold: {health_metrics[metric]} > {threshold}")
            return True
            
    return False
