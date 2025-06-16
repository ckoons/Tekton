#!/usr/bin/env python3
"""
Component recovery functionality.

This module provides functionality for attempting to recover failed or
degraded components through various strategies (restart, reset, failover).
"""

import time
import logging
from typing import Dict, List, Any, Optional, Set, Tuple

from ..lifecycle import ComponentState
from ..registry import _save_registrations

logger = logging.getLogger("tekton.component_lifecycle.recovery")


async def attempt_component_recovery(
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]],
    component_id: str,
    max_attempts: int = 3,
    recovery_strategy: str = "auto",
    data_dir: Optional[str] = None
) -> bool:
    """
    Attempt to recover a failed or degraded component.
    
    Args:
        components: Component registrations
        instances: Component instances
        component_id: Component ID
        max_attempts: Maximum recovery attempts
        recovery_strategy: Recovery strategy (restart, reset, failover, auto)
        data_dir: Optional directory for persistent storage
        
    Returns:
        True if recovery was successful
    """
    # Check if component is registered
    if component_id not in components:
        logger.error(f"Cannot recover unregistered component: {component_id}")
        return False
        
    component = components[component_id]
    
    # Check if component is in a state that needs recovery
    if not ComponentState.is_degraded(component.state) and component.state != ComponentState.FAILED.value:
        logger.info(f"Component {component_id} does not need recovery (state: {component.state})")
        return True
        
    # Check if exceeded max recovery attempts
    if component.recovery_attempts >= max_attempts:
        logger.warning(f"Component {component_id} exceeded maximum recovery attempts ({max_attempts})")
        return False
        
    # Record recovery attempt
    component.record_recovery_attempt(f"Strategy: {recovery_strategy}")
    
    # If auto strategy, determine best recovery approach based on component state and history
    if recovery_strategy == "auto":
        failure_count = component.recovery_attempts
        if failure_count > 5:
            recovery_strategy = "failover"
        elif failure_count > 2:
            recovery_strategy = "restart"
        else:
            recovery_strategy = "reset"
        logger.info(f"Auto-selected recovery strategy for {component_id}: {recovery_strategy}")
    
    # Implement recovery strategy
    if recovery_strategy == "restart":
        return await _implement_restart_recovery(component_id, component, components, instances, data_dir)
    elif recovery_strategy == "reset":
        return await _implement_reset_recovery(component_id, component, components, instances, data_dir)
    elif recovery_strategy == "failover":
        return await _implement_failover_recovery(component_id, component, components, instances, data_dir)
    else:
        logger.error(f"Unknown recovery strategy: {recovery_strategy}")
        return False


async def _implement_restart_recovery(
    component_id: str,
    component: Any,
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]],
    data_dir: Optional[str] = None
) -> bool:
    """
    Implement restart recovery strategy for a component.
    
    Args:
        component_id: Component ID
        component: Component registration
        components: All component registrations
        instances: Component instances
        data_dir: Optional directory for persistent storage
        
    Returns:
        True if recovery was successful
    """
    # Transition to RESTARTING
    component.update_state(
        ComponentState.RESTARTING.value, 
        "recovery.restart", 
        f"Recovery attempt {component.recovery_attempts}"
    )
    
    # Save state change
    instances[component_id]["state"] = ComponentState.RESTARTING.value
    if data_dir:
        await _save_registrations(components, data_dir)
    
    try:
        # 1. Signal component to save state if possible
        await _signal_component_save_state(component_id, component, instances)
        
        # 2. Prepare for restart
        metadata = {
            "restart_reason": "recovery",
            "restart_timestamp": time.time(),
            "restart_attempt": component.recovery_attempts
        }
        instances[component_id].setdefault("metadata", {}).update(metadata)
        
        # 3. Perform restart operation
        restart_success = await _perform_component_restart(component_id, component, instances)
        
        if restart_success:
            # 4. Update component state to indicate restart success
            component.update_state(
                ComponentState.INITIALIZING.value,
                "recovery.restarting.success",
                "Component is initializing after successful restart"
            )
            
            instances[component_id]["state"] = ComponentState.INITIALIZING.value
            if data_dir:
                await _save_registrations(components, data_dir)
                
            logger.info(f"Recovery restart successful for component {component_id}")
            return True
        else:
            # Update component state to indicate restart failure
            component.update_state(
                ComponentState.FAILED.value,
                "recovery.restarting.failed",
                "Failed to restart component"
            )
            
            instances[component_id]["state"] = ComponentState.FAILED.value
            if data_dir:
                await _save_registrations(components, data_dir)
                
            logger.error(f"Recovery restart failed for component {component_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error during restart recovery of {component_id}: {e}")
        
        # Update component state to indicate restart error
        component.update_state(
            ComponentState.FAILED.value,
            "recovery.restarting.error",
            f"Error during restart: {str(e)}"
        )
        
        instances[component_id]["state"] = ComponentState.FAILED.value
        if data_dir:
            await _save_registrations(components, data_dir)
            
        return False


async def _implement_reset_recovery(
    component_id: str,
    component: Any,
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]],
    data_dir: Optional[str] = None
) -> bool:
    """
    Implement state reset recovery for a component without full restart.
    
    Args:
        component_id: Component ID
        component: Component registration
        components: All component registrations
        instances: Component instances
        data_dir: Optional directory for persistent storage
        
    Returns:
        True if recovery was successful
    """
    try:
        # 1. Signal component to reset internal state
        await _signal_component_reset(component_id, component, instances)
        
        # 2. Clear error conditions
        if "error_conditions" in instances[component_id]:
            instances[component_id]["error_conditions"] = []
        
        # 3. Update metadata
        metadata = {
            "reset_reason": "recovery",
            "reset_timestamp": time.time(),
            "reset_attempt": component.recovery_attempts
        }
        instances[component_id].setdefault("metadata", {}).update(metadata)
        
        # 4. Update component state
        component.update_state(
            ComponentState.INITIALIZING.value,
            "recovery.reset",
            "Component state reset for recovery"
        )
        
        instances[component_id]["state"] = ComponentState.INITIALIZING.value
        if data_dir:
            await _save_registrations(components, data_dir)
            
        logger.info(f"Recovery reset successful for component {component_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error during state reset recovery of {component_id}: {e}")
        
        # Update component state to indicate reset error
        component.update_state(
            ComponentState.FAILED.value,
            "recovery.reset.error",
            f"Error during state reset: {str(e)}"
        )
        
        instances[component_id]["state"] = ComponentState.FAILED.value
        if data_dir:
            await _save_registrations(components, data_dir)
            
        return False


async def _implement_failover_recovery(
    component_id: str,
    component: Any,
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]],
    data_dir: Optional[str] = None
) -> bool:
    """
    Implement failover to redundant component instance.
    
    Args:
        component_id: Component ID
        component: Component registration
        components: All component registrations
        instances: Component instances
        data_dir: Optional directory for persistent storage
        
    Returns:
        True if recovery was successful
    """
    try:
        # 1. Identify available failover targets
        failover_targets = await _identify_failover_targets(component_id, component, components)
        
        if not failover_targets:
            logger.warning(f"No failover targets available for {component_id}")
            return False
            
        # 2. Select appropriate target based on health/capacity
        selected_target = await _select_best_failover_target(failover_targets, components, instances)
        
        if not selected_target:
            logger.warning(f"Could not select a suitable failover target for {component_id}")
            return False
            
        # 3. Update component state
        component.update_state(
            ComponentState.FAILED.value,
            "recovery.failover",
            f"Failing over to {selected_target}"
        )
        
        instances[component_id]["state"] = ComponentState.FAILED.value
        if data_dir:
            await _save_registrations(components, data_dir)
            
        # 4. Perform failover
        failover_success = await _perform_failover(
            component_id, 
            selected_target, 
            component, 
            components, 
            instances
        )
        
        if failover_success:
            logger.info(f"Successfully failed over {component_id} to {selected_target}")
            
            # Update metadata
            metadata = {
                "failover_reason": "recovery",
                "failover_timestamp": time.time(),
                "failover_target": selected_target,
                "primary_status": "inactive"
            }
            instances[component_id].setdefault("metadata", {}).update(metadata)
            
            # Mark original as inactive
            component.update_state(
                ComponentState.INACTIVE.value,
                "recovery.failover.success",
                f"Successfully failed over to {selected_target}"
            )
            
            instances[component_id]["state"] = ComponentState.INACTIVE.value
            if data_dir:
                await _save_registrations(components, data_dir)
                
            return True
        else:
            logger.error(f"Failed to failover {component_id} to {selected_target}")
            return False
            
    except Exception as e:
        logger.error(f"Error during failover recovery of {component_id}: {e}")
        return False


async def _signal_component_save_state(component_id: str, component: Any, instances: Dict[str, Dict[str, Any]]) -> bool:
    """Signal component to save its state before restarting."""
    try:
        # This would typically send a message to the component or invoke an API
        # For now, we'll just log and return success
        logger.info(f"Signaling component {component_id} to save state")
        return True
    except Exception as e:
        logger.warning(f"Failed to signal component {component_id} to save state: {e}")
        return False


async def _perform_component_restart(component_id: str, component: Any, instances: Dict[str, Dict[str, Any]]) -> bool:
    """Perform the actual restart operation on a component."""
    try:
        # In a real implementation, this would:
        # 1. Signal the process manager or container orchestrator
        # 2. Verify the component was stopped properly
        # 3. Start a new instance with the original configuration
        
        # For now, simulate a restart
        logger.info(f"Simulating restart of component {component_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to restart component {component_id}: {e}")
        return False


async def _signal_component_reset(component_id: str, component: Any, instances: Dict[str, Dict[str, Any]]) -> bool:
    """Signal component to reset its internal state."""
    try:
        # This would typically send a message to the component API
        # For now, we'll just log and return success
        logger.info(f"Signaling component {component_id} to reset internal state")
        return True
    except Exception as e:
        logger.warning(f"Failed to signal component {component_id} to reset state: {e}")
        return False


async def _identify_failover_targets(component_id: str, component: Any, components: Dict[str, Any]) -> List[str]:
    """Identify potential failover targets for a component."""
    # For actual implementation, this would:
    # 1. Look for similarly-typed components
    # 2. Check for components with matching capabilities
    # 3. Check for components that explicitly declare as failover targets
    
    # For now, return an empty list
    logger.info(f"Identifying failover targets for {component_id}")
    
    # Look for components with the same type and compatible capabilities
    component_type = component.component_type
    targets = []
    
    for other_id, other in components.items():
        # Skip the original component and non-ready components
        if other_id == component_id or other.state != ComponentState.READY.value:
            continue
            
        # Check if types match
        if other.component_type == component_type:
            # Check for failover capability
            for capability in other.capabilities:
                if capability.get("type") == "failover" and component_id in capability.get("targets", []):
                    targets.append(other_id)
                    break
    
    logger.info(f"Found {len(targets)} potential failover targets for {component_id}")
    return targets


async def _select_best_failover_target(
    targets: List[str],
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]]
) -> Optional[str]:
    """Select the best failover target based on health and capacity."""
    if not targets:
        return None
    
    # For a real implementation, this would evaluate:
    # 1. Current load on each target
    # 2. Health metrics
    # 3. Geographic proximity if relevant
    # 4. Capability compatibility score
    
    # For now, just return the first target
    return targets[0]


async def _perform_failover(
    component_id: str,
    target_id: str,
    component: Any,
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]]
) -> bool:
    """Perform failover to the target component."""
    try:
        # In a real implementation, this would:
        # 1. Signal the target to prepare for taking over
        # 2. Transfer state if possible
        # 3. Update routing configuration
        # 4. Verify successful transfer
        
        # For now, simulate a successful failover
        logger.info(f"Simulating failover from {component_id} to {target_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to perform failover from {component_id} to {target_id}: {e}")
        return False
