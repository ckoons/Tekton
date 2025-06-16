#!/usr/bin/env python3
"""
Component Readiness Module

This module provides functionality for tracking and checking component readiness.
"""

import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Awaitable, Tuple

from ..lifecycle import ComponentState, ReadinessCondition
from ..registry import _save_registrations

logger = logging.getLogger("tekton.component_lifecycle.readiness")


async def register_readiness_condition(
    readiness_conditions: Dict[str, Dict[str, ReadinessCondition]],
    component_id: str,
    condition_name: str,
    check_func: Callable[[], Awaitable[bool]],
    description: Optional[str] = None,
    timeout: Optional[float] = 60.0
) -> Tuple[bool, str]:
    """
    Register a readiness condition for a component.
    
    Args:
        readiness_conditions: Dictionary of readiness conditions
        component_id: Component ID
        condition_name: Condition name
        check_func: Async function that returns True if condition is satisfied
        description: Optional description
        timeout: Optional timeout in seconds
        
    Returns:
        Tuple of (success, message)
    """
    # Create component entry if it doesn't exist
    if component_id not in readiness_conditions:
        readiness_conditions[component_id] = {}
        
    # Create condition
    condition = ReadinessCondition(
        name=condition_name,
        check_func=check_func,
        description=description,
        timeout=timeout
    )
    
    # Store condition
    readiness_conditions[component_id][condition_name] = condition
    
    return True, f"Registered readiness condition: {condition_name}"


async def check_readiness_conditions(
    readiness_conditions: Dict[str, Dict[str, ReadinessCondition]],
    component_id: str
) -> Tuple[bool, Dict[str, Any]]:
    """
    Check all readiness conditions for a component.
    
    Args:
        readiness_conditions: Dictionary of readiness conditions
        component_id: Component ID
        
    Returns:
        Tuple of (all_satisfied, condition_results)
    """
    # Check if component has any conditions
    if component_id not in readiness_conditions:
        return True, {}
        
    # Check conditions
    conditions = readiness_conditions[component_id]
    results = {}
    all_satisfied = True
    
    for name, condition in conditions.items():
        try:
            satisfied = await condition.check()
            results[name] = {
                "satisfied": satisfied,
                "description": condition.description,
                "last_check_time": condition.last_check_time
            }
            
            if not satisfied:
                all_satisfied = False
                
        except Exception as e:
            logger.error(f"Error checking readiness condition {name}: {e}")
            results[name] = {
                "satisfied": False,
                "description": condition.description,
                "last_check_time": condition.last_check_time,
                "error": str(e)
            }
            all_satisfied = False
            
    return all_satisfied, results


async def mark_component_ready(
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]],
    readiness_conditions: Dict[str, Dict[str, ReadinessCondition]],
    component_id: str,
    instance_uuid: str,
    metadata: Optional[Dict[str, Any]] = None,
    data_dir: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Mark a component as ready after checking all readiness conditions.
    
    Args:
        components: Component registrations
        instances: Component instances
        readiness_conditions: Dictionary of readiness conditions
        component_id: Component ID
        instance_uuid: Instance UUID
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
        
    # Check readiness conditions
    all_satisfied, results = await check_readiness_conditions(readiness_conditions, component_id)
    
    if not all_satisfied:
        # Format unsatisfied conditions
        unsatisfied = []
        for name, result in results.items():
            if not result.get("satisfied", False):
                unsatisfied.append(name)
                
        msg = f"Not all readiness conditions satisfied: {', '.join(unsatisfied)}"
        return False, msg
        
    # Get component registration
    component = components[component_id]
    
    # Update state to READY
    success = component.update_state(
        ComponentState.READY.value,
        "startup.readiness_complete",
        "All readiness conditions satisfied"
    )
    
    if not success:
        return False, f"Failed to transition to READY state from {component.state}"
        
    # Update instance data
    instances[component_id]["state"] = ComponentState.READY.value
    instances[component_id]["ready_time"] = time.time()
    
    # Update metadata if provided
    if metadata:
        component.metadata.update(metadata)
        instances[component_id].setdefault("metadata", {}).update(metadata)
        
    # Persist state update
    if data_dir:
        await _save_registrations(components, data_dir)
        
    return True, "Component marked as ready"


async def wait_for_component_ready(
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]],
    component_id: str,
    timeout: float = 60.0,
    check_interval: float = 0.5
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Wait for a component to become ready.
    
    Args:
        components: Component registrations
        instances: Component instances
        component_id: Component ID to wait for
        timeout: Timeout in seconds
        check_interval: Interval between checks
        
    Returns:
        Tuple of (success, component_info)
    """
    # Check if component exists
    if component_id not in components:
        return False, None
        
    # Get component
    component = components[component_id]
    
    # Fast path if already ready
    if component.state == ComponentState.READY.value:
        return True, {
            "component_id": component_id,
            "component_name": component.component_name,
            "component_type": component.component_type,
            "state": component.state,
            "instance_uuid": component.instance_uuid,
            "metadata": component.metadata,
            "ready_time": instances[component_id].get("ready_time", 0)
        }
        
    # Wait for ready state
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Check state
        if component.state == ComponentState.READY.value:
            return True, {
                "component_id": component_id,
                "component_name": component.component_name,
                "component_type": component.component_type,
                "state": component.state,
                "instance_uuid": component.instance_uuid,
                "metadata": component.metadata,
                "ready_time": instances[component_id].get("ready_time", 0)
            }
        elif component.state == ComponentState.FAILED.value:
            return False, {
                "component_id": component_id,
                "component_name": component.component_name,
                "component_type": component.component_type,
                "state": component.state,
                "instance_uuid": component.instance_uuid,
                "metadata": component.metadata,
                "error": component.metadata.get("error", "Unknown error")
            }
            
        # Wait before next check
        await asyncio.sleep(check_interval)
        
    # Timeout, return current state
    return False, {
        "component_id": component_id,
        "component_name": component.component_name,
        "component_type": component.component_type,
        "state": component.state,
        "instance_uuid": component.instance_uuid,
        "metadata": component.metadata,
        "timeout": True
    }


async def wait_for_dependencies(
    components: Dict[str, Any],
    dependencies: List[str],
    timeout: float = 60.0,
    check_interval: float = 0.5
) -> Tuple[bool, List[str]]:
    """
    Wait for multiple dependencies to become ready.
    
    Args:
        components: Component registrations
        dependencies: List of component IDs to wait for
        timeout: Timeout in seconds
        check_interval: Interval between checks
        
    Returns:
        Tuple of (all_ready, failed_dependencies)
    """
    # Fast path for no dependencies
    if not dependencies:
        return True, []
        
    # Check for unknown dependencies
    unknown = [d for d in dependencies if d not in components]
    if unknown:
        logger.warning(f"Unknown dependencies: {unknown}")
        return False, unknown
        
    # Wait for dependencies to become ready
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Check if all dependencies are ready
        failed = []
        
        for dep_id in dependencies:
            if dep_id not in components:
                failed.append(dep_id)
                continue
                
            dep = components[dep_id]
            
            if dep.state != ComponentState.READY.value:
                # Check for failed state
                if dep.state == ComponentState.FAILED.value:
                    logger.error(f"Dependency {dep_id} in FAILED state")
                    failed.append(dep_id)
                else:
                    # Still waiting
                    break
        else:
            # All dependencies ready
            if not failed:
                return True, []
            
        # If we have any failed dependencies, return early
        if failed:
            return False, failed
            
        # Wait before next check
        await asyncio.sleep(check_interval)
        
    # Timeout, return failed dependencies
    failed = []
    for dep_id in dependencies:
        if dep_id not in components or components[dep_id].state != ComponentState.READY.value:
            failed.append(dep_id)
            
    return len(failed) == 0, failed