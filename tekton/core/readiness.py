#!/usr/bin/env python3
"""
Component Readiness Module

This module provides functions for managing readiness conditions and dependencies.
"""

import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Awaitable, Tuple

from .lifecycle import ReadinessCondition, ComponentState

logger = logging.getLogger("tekton.readiness")


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
        readiness_conditions: Dictionary of component readiness conditions
        component_id: Component ID
        condition_name: Condition name
        check_func: Async function that returns True if condition is satisfied
        description: Optional description
        timeout: Optional timeout in seconds
        
    Returns:
        Tuple of (success, message)
    """
    # Create condition
    condition = ReadinessCondition(
        name=condition_name,
        check_func=check_func,
        description=description,
        timeout=timeout
    )
    
    # Add to component's conditions
    if component_id not in readiness_conditions:
        readiness_conditions[component_id] = {}
        
    readiness_conditions[component_id][condition_name] = condition
    
    logger.info(f"Registered readiness condition {condition_name} for {component_id}")
    return True, "Condition registered"


async def check_readiness_conditions(
    readiness_conditions: Dict[str, Dict[str, ReadinessCondition]],
    component_id: str
) -> Tuple[bool, Dict[str, Any]]:
    """
    Check all readiness conditions for a component.
    
    Args:
        readiness_conditions: Dictionary of component readiness conditions
        component_id: Component ID
        
    Returns:
        Tuple of (all_satisfied, condition_results)
    """
    # If no conditions registered, component is ready
    if component_id not in readiness_conditions:
        return True, {}
        
    all_satisfied = True
    results = {}
    
    # Check each condition
    for name, condition in readiness_conditions[component_id].items():
        satisfied = await condition.check()
        results[name] = {
            "satisfied": satisfied,
            "description": condition.description,
            "last_check_time": condition.last_check_time,
            "last_error": condition.last_error
        }
        
        if not satisfied:
            all_satisfied = False
            
    return all_satisfied, results


async def mark_component_ready(
    components, instances, readiness_conditions, component_id, instance_uuid, 
    metadata=None, data_dir=None
) -> Tuple[bool, str]:
    """
    Mark a component as ready after checking all readiness conditions.
    
    Args:
        components: Dictionary of component registrations
        instances: Dictionary of component instances
        readiness_conditions: Dictionary of component readiness conditions
        component_id: Component ID
        instance_uuid: Instance UUID
        metadata: Optional additional metadata
        data_dir: Directory for persistent storage
        
    Returns:
        Tuple of (success, message)
    """
    from .registry import update_component_state
    
    # Check readiness conditions
    all_satisfied, results = await check_readiness_conditions(readiness_conditions, component_id)
    
    if not all_satisfied:
        unsatisfied = [name for name, result in results.items() if not result["satisfied"]]
        logger.warning(f"Component {component_id} not ready - conditions not satisfied: {unsatisfied}")
        return False, f"Not all readiness conditions satisfied: {unsatisfied}"
    
    # Update state to READY
    combined_metadata = metadata or {}
    combined_metadata["readiness_check_results"] = results
    
    success, message = await update_component_state(
        components=components,
        instances=instances,
        component_id=component_id,
        instance_uuid=instance_uuid,
        state=ComponentState.READY.value,
        metadata=combined_metadata,
        data_dir=data_dir
    )
    
    return success, message


async def wait_for_component_ready(
    components, component_id, timeout=60.0, check_interval=0.5
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Wait for a component to become ready.
    
    Args:
        components: Dictionary of component registrations
        component_id: Component ID to wait for
        timeout: Timeout in seconds
        check_interval: Interval between checks
        
    Returns:
        Tuple of (success, component_info)
    """
    from .registry import get_component_info
    
    start_time = time.time()
    
    # Add initial jitter to prevent thundering herd
    jitter = 0.1 * (hash(component_id) % 10) / 10.0
    await asyncio.sleep(jitter)
    
    while time.time() - start_time < timeout:
        # Check if component exists
        if component_id not in components:
            await asyncio.sleep(check_interval)
            continue
        
        # Get current state
        state = components[component_id].state
        
        # Check if ready
        if state == ComponentState.READY.value:
            return True, await get_component_info(components, {}, component_id)
        
        # Check if failed (fail fast)
        if state == ComponentState.FAILED.value:
            logger.error(f"Component {component_id} is in FAILED state")
            return False, await get_component_info(components, {}, component_id)
    
        # Wait before checking again
        await asyncio.sleep(check_interval)
        
        # Increase check interval with a cap
        check_interval = min(check_interval * 1.5, 5)
    
    # Timeout
    logger.error(f"Timeout waiting for component {component_id} to become ready")
    return False, await get_component_info(components, {}, component_id)


async def wait_for_dependencies(
    components, dependencies, timeout=60.0, check_interval=0.5
) -> Tuple[bool, List[str]]:
    """
    Wait for multiple dependencies to become ready.
    
    Args:
        components: Dictionary of component registrations
        dependencies: List of component IDs to wait for
        timeout: Timeout in seconds
        check_interval: Interval between checks
        
    Returns:
        Tuple of (all_ready, failed_dependencies)
    """
    if not dependencies:
        return True, []
    
    logger.info(f"Waiting for dependencies: {dependencies}")
    
    start_time = time.time()
    failed_deps = []
    
    while time.time() - start_time < timeout:
        ready_deps = []
        pending_deps = []
        
        for dep in dependencies:
            if dep in failed_deps:
                continue
                
            if dep in components:
                state = components[dep].state
                
                if state == ComponentState.READY.value:
                    ready_deps.append(dep)
                elif state == ComponentState.FAILED.value:
                    failed_deps.append(dep)
                else:
                    pending_deps.append(dep)
            else:
                pending_deps.append(dep)
        
        # Success if all dependencies are ready
        if len(ready_deps) == len(dependencies):
            logger.info(f"All dependencies ready: {dependencies}")
            return True, []
        
        # Partial failure if any dependencies have failed
        if failed_deps:
            logger.warning(f"Some dependencies failed: {failed_deps}")
            
        # Exit early if all remaining dependencies have failed
        if len(ready_deps) + len(failed_deps) == len(dependencies):
            logger.error(f"All remaining dependencies have failed: {failed_deps}")
            return False, failed_deps
            
        # Wait before checking again
        await asyncio.sleep(check_interval)
    
    # Timeout
    remaining = [dep for dep in dependencies if dep not in ready_deps and dep not in failed_deps]
    logger.error(f"Timeout waiting for dependencies: {remaining}")
    return False, failed_deps + remaining