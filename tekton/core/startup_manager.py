#!/usr/bin/env python3
"""
Tekton StartUpManager Module

This module provides functions and classes for managing component startup,
including synchronization with service registries.
"""

import logging
import asyncio
import uuid
import time
from typing import Dict, List, Any, Tuple, Optional

from tekton.core.startup_instructions import StartUpInstructions
from tekton.core.lifecycle import (
    ComponentState,
    ComponentRegistration
)
from tekton.core.dependency import DependencyResolver

logger = logging.getLogger("tekton.startup_manager")


async def get_component_status(registry, component_id: str) -> Dict[str, Any]:
    """
    Get the status of a component.
    
    Args:
        registry: Component registry
        component_id: Component ID
        
    Returns:
        Component status dictionary
    """
    return await registry.get_component_info(component_id) or {
        "component_id": component_id,
        "state": ComponentState.UNKNOWN.value,
        "exists": False
    }


async def synchronize_with_service_registry(registry, service_registry) -> bool:
    """
    Synchronize component status with a service registry.
    
    Args:
        registry: Component registry
        service_registry: Service registry interface
    
    Returns:
        True if successful
    """
    if not service_registry:
        logger.warning("Service registry not available for synchronization")
        return False
        
    try:
        # Get all services from registry
        services = await service_registry.get_all_services()
        
        # Register components from service registry
        for service_id, service_info in services.items():
            component_id = service_info.get("metadata", {}).get("component_id")
            if not component_id:
                continue
            
            # Create registration
            registration = ComponentRegistration(
                component_id=component_id,
                component_name=service_info.get("name", component_id),
                component_type=service_info.get("type", "service"),
                instance_uuid=service_info.get("metadata", {}).get("instance_uuid", str(uuid.uuid4())),
                version=service_info.get("version", "0.1.0"),
                capabilities=service_info.get("capabilities", []),
                metadata=service_info.get("metadata", {})
            )
            
            # Register and mark as ready
            await registry.register_component(registration)
            await registry.mark_component_ready(
                component_id=component_id,
                instance_uuid=registration.instance_uuid,
                metadata={
                    "endpoint": service_info.get("endpoint"),
                    "source": "registry_sync"
                }
            )
            
        logger.info(f"Synchronized with service registry")
        return True
        
    except Exception as e:
        logger.error(f"Error synchronizing with service registry: {e}")
        return False


async def start_components_in_order(
        component_configs: Dict[str, Dict[str, Any]],
        start_func,
        resolve_cycles: bool = True) -> Dict[str, bool]:
    """
    Start multiple components in dependency order.
    
    Args:
        component_configs: Dictionary mapping component IDs to configs
        start_func: Function to start a component
        resolve_cycles: Whether to resolve dependency cycles
        
    Returns:
        Dictionary mapping component IDs to success status
    """
    results = {}
    
    # Extract dependency graph
    dependency_graph = {}
    for component_id, config in component_configs.items():
        dependency_graph[component_id] = config.get("dependencies", [])
    
    # Resolve dependencies with cycle detection
    start_order, had_cycles = DependencyResolver.resolve_dependencies(dependency_graph)
    
    if had_cycles and resolve_cycles:
        logger.warning("Detected and resolved circular dependencies in component graph")
        
    logger.info(f"Starting components in order: {start_order}")
    
    # Start components in dependency order
    for component_id in start_order:
        if component_id in component_configs:
            config = component_configs[component_id]
            
            success, _ = await start_func(
                component_id=component_id,
                start_func=config.get("start_func"),
                dependencies=config.get("dependencies", []),
                timeout=config.get("timeout", 60),
                component_type=config.get("type", "component"),
                component_name=config.get("name", component_id),
                version=config.get("version", "0.1.0"),
                capabilities=config.get("capabilities", []),
                metadata=config.get("metadata", {})
            )
            
            results[component_id] = success
            
            # Add delay between component starts
            await asyncio.sleep(1)
    
    return results


async def start_components_parallel(
        component_configs: Dict[str, Dict[str, Any]],
        start_func) -> Dict[str, bool]:
    """
    Start multiple components in parallel.
    
    Args:
        component_configs: Dictionary mapping component IDs to configs
        start_func: Function to start a component
        
    Returns:
        Dictionary mapping component IDs to success status
    """
    results = {}
    tasks = []
    components = []
    
    for component_id, config in component_configs.items():
        task = start_func(
            component_id=component_id,
            start_func=config.get("start_func"),
            dependencies=config.get("dependencies", []),
            timeout=config.get("timeout", 60),
            component_type=config.get("type", "component"),
            component_name=config.get("name", component_id),
            version=config.get("version", "0.1.0"),
            capabilities=config.get("capabilities", []),
            metadata=config.get("metadata", {})
        )
        
        tasks.append(task)
        components.append(component_id)
    
    # Wait for all components to start
    start_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for i, component_id in enumerate(components):
        if isinstance(start_results[i], Exception):
            results[component_id] = False
            logger.error(f"Exception starting {component_id}: {start_results[i]}")
        else:
            success, _ = start_results[i]
            results[component_id] = success
    
    return results