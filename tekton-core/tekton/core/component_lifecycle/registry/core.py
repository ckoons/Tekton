#!/usr/bin/env python3
"""
Core Component Registry Module

This module provides the main ComponentRegistry class for handling component
lifecycle management.
"""

import os
import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Set, Callable, Awaitable, Tuple

from ...lifecycle import (
    ComponentState,
    ReadinessCondition, 
    ComponentRegistration
)
from ...graceful_degradation import GracefulDegradationManager
from ..readiness import (
    register_readiness_condition,
    check_readiness_conditions,
    mark_component_ready,
    wait_for_dependencies
)
from ..healthcheck import attempt_component_recovery
from .persistence import load_registrations, save_registrations
from .components import get_component_info, get_all_components
from .operations import (
    register_component,
    update_component_state,
    monitor_components,
    process_heartbeat_internal,
    register_capability_internal,
    register_fallback_handler_internal,
    execute_with_fallback_internal,
    get_fallback_status_internal,
    get_fallback_handler_internal
)

logger = logging.getLogger("tekton.component_lifecycle.registry")


class ComponentRegistry:
    """
    Registry for tracking component registrations and instances.
    
    Manages component registrations, detects duplicate instances, and 
    handles component lifecycle state transitions.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the component registry.
        
        Args:
            data_dir: Optional directory for persistent storage
        """
        if data_dir:
            self.data_dir = data_dir
        else:
            # Use $TEKTON_DATA_DIR/registry by default
            from shared.env import TektonEnviron
            default_data_dir = os.path.join(
                TektonEnviron.get('TEKTON_DATA_DIR') or 
                              os.path.join(TektonEnviron.get('TEKTON_ROOT') or os.path.expanduser('~'), '.tekton', 'data'),
                'registry'
            )
            self.data_dir = default_data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Internal storage
        self.components: Dict[str, ComponentRegistration] = {}
        self.instances: Dict[str, Dict[str, Any]] = {}
        self.readiness_conditions: Dict[str, Dict[str, ReadinessCondition]] = {}
        
        # Graceful degradation support
        self.degradation_manager = GracefulDegradationManager()
        self.fallback_handlers: Dict[str, Dict[str, Callable]] = {}
        
        self.lock = asyncio.Lock()
        
        # Use default values until async load is performed
        self.components = {}
        self.instances = {}
        
        # Start async load of registrations in the background
        asyncio.create_task(self._load_registrations_async())
        
    async def _load_registrations_async(self):
        """Asynchronously load registrations from disk."""
        try:
            components, instances = await load_registrations(self.data_dir)
            async with self.lock:
                self.components = components
                self.instances = instances
                logger.debug("Loaded registrations asynchronously")
        except Exception as e:
            logger.error(f"Failed to load registrations: {e}")
    
    async def register_component(self, registration: ComponentRegistration) -> Tuple[bool, str]:
        """
        Register a component with the registry.
        
        Args:
            registration: ComponentRegistration object
            
        Returns:
            Tuple of (success, message)
        """
        async with self.lock:
            return await register_component(
                self.components, 
                self.instances, 
                registration, 
                self.data_dir
            )
    
    async def update_component_state(self, 
                            component_id: str, 
                            instance_uuid: str,
                            state: str,
                            metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Update the state of a component.
        
        Args:
            component_id: Component ID
            instance_uuid: Instance UUID
            state: ComponentState value
            metadata: Optional additional metadata
            
        Returns:
            Tuple of (success, message)
        """
        async with self.lock:
            return await update_component_state(
                self.components,
                self.instances,
                component_id,
                instance_uuid,
                state,
                metadata,
                self.data_dir
            )
    
    async def register_readiness_condition(self,
                                component_id: str,
                                condition_name: str,
                                check_func: Callable[[], Awaitable[bool]],
                                description: Optional[str] = None,
                                timeout: Optional[float] = 60.0) -> Tuple[bool, str]:
        """
        Register a readiness condition for a component.
        
        Args:
            component_id: Component ID
            condition_name: Condition name
            check_func: Async function that returns True if condition is satisfied
            description: Optional description
            timeout: Optional timeout in seconds
            
        Returns:
            Tuple of (success, message)
        """
        async with self.lock:
            # Check if component is registered
            if component_id not in self.components:
                return False, "Component not registered"
            
            return await register_readiness_condition(
                self.readiness_conditions,
                component_id,
                condition_name,
                check_func,
                description,
                timeout
            )
    
    async def check_readiness_conditions(self, component_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check all readiness conditions for a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Tuple of (all_satisfied, condition_results)
        """
        async with self.lock:
            return await check_readiness_conditions(self.readiness_conditions, component_id)
    
    async def mark_component_ready(self, 
                        component_id: str, 
                        instance_uuid: str,
                        metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Mark a component as ready after checking all readiness conditions.
        
        Args:
            component_id: Component ID
            instance_uuid: Instance UUID
            metadata: Optional additional metadata
            
        Returns:
            Tuple of (success, message)
        """
        async with self.lock:
            return await mark_component_ready(
                self.components,
                self.instances,
                self.readiness_conditions,
                component_id,
                instance_uuid,
                metadata,
                self.data_dir
            )
    
    async def wait_for_component_ready(self, 
                            component_id: str, 
                            timeout: float = 60.0,
                            check_interval: float = 0.5) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Wait for a component to become ready.
        
        Args:
            component_id: Component ID to wait for
            timeout: Timeout in seconds
            check_interval: Interval between checks
            
        Returns:
            Tuple of (success, component_info)
        """
        # Initial check with lock
        async with self.lock:
            if component_id in self.components:
                state = self.components[component_id].state
                if state == ComponentState.READY.value:
                    return True, await self.get_component_info(component_id)
        
        # Periodic checking without holding lock for the entire duration
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check with lock
            async with self.lock:
                if component_id in self.components:
                    state = self.components[component_id].state
                    if state == ComponentState.READY.value:
                        return True, await self.get_component_info(component_id)
                    elif state == ComponentState.FAILED.value:
                        return False, await self.get_component_info(component_id)
            
            # Wait without holding lock
            await asyncio.sleep(check_interval)
            
            # Increase check interval with a cap
            check_interval = min(check_interval * 1.5, 5)
        
        # Final check with lock
        async with self.lock:
            return False, await self.get_component_info(component_id)
    
    async def wait_for_dependencies(self, 
                        dependencies: List[str], 
                        timeout: float = 60.0,
                        check_interval: float = 0.5) -> Tuple[bool, List[str]]:
        """
        Wait for multiple dependencies to become ready.
        
        Args:
            dependencies: List of component IDs to wait for
            timeout: Timeout in seconds
            check_interval: Interval between checks
            
        Returns:
            Tuple of (all_ready, failed_dependencies)
        """
        # Fast path for no dependencies
        if not dependencies:
            return True, []
        
        # Initial check with lock
        async with self.lock:
            components_copy = self.components.copy()
        
        # Use the copied state to minimize lock contention
        return await wait_for_dependencies(
            components_copy,
            dependencies,
            timeout,
            check_interval
        )
    
    async def process_heartbeat(self, 
                    component_id: str, 
                    instance_uuid: str, 
                    sequence: int,
                    state: Optional[str] = None,
                    health_metrics: Optional[Dict[str, float]] = None,
                    metadata: Optional[Dict[str, Any]] = None,
                    reason: Optional[str] = None,
                    details: Optional[str] = None) -> Tuple[bool, str]:
        """
        Process a heartbeat from a component with enhanced health metrics.
        
        Args:
            component_id: Component ID
            instance_uuid: Instance UUID
            sequence: Heartbeat sequence number
            state: Optional current state
            health_metrics: Optional health metrics (CPU, memory, latency, etc.)
            metadata: Optional additional metadata
            reason: Optional reason for state change
            details: Optional details about component status
            
        Returns:
            Tuple of (success, message)
        """
        async with self.lock:
            return await process_heartbeat_internal(
                self.components,
                self.instances,
                component_id,
                instance_uuid,
                sequence,
                state,
                health_metrics,
                metadata,
                reason,
                details,
                self.data_dir
            )
    
    async def attempt_component_recovery(self, 
                                component_id: str,
                                max_attempts: int = 3,
                                recovery_strategy: str = "restart") -> bool:
        """
        Attempt to recover a failed or degraded component.
        
        Args:
            component_id: Component ID
            max_attempts: Maximum recovery attempts
            recovery_strategy: Recovery strategy (restart, reset, failover)
            
        Returns:
            True if recovery was successful
        """
        async with self.lock:
            return await attempt_component_recovery(
                self.components,
                self.instances,
                component_id,
                max_attempts,
                recovery_strategy,
                self.data_dir
            )
    
    async def get_component_info(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component information or None if not found
        """
        async with self.lock:
            return await get_component_info(self.components, self.instances, component_id)
    
    async def get_all_components(self) -> List[Dict[str, Any]]:
        """
        Get information about all components.
        
        Returns:
            List of component information dictionaries
        """
        async with self.lock:
            return await get_all_components(self.components, self.instances)
    
    async def monitor_components(self, heartbeat_timeout: int = 30) -> None:
        """
        Monitor component health and mark failed components with enhanced degradation.
        
        Args:
            heartbeat_timeout: Timeout in seconds before marking a component as failed
        """
        while True:
            try:
                # Monitor health with lock
                async with self.lock:
                    recovery_candidates = await monitor_components(
                        self.components,
                        self.instances,
                        self.data_dir,
                        heartbeat_timeout
                    )
                
                    # Attempt recovery for candidates
                    for component_id in recovery_candidates:
                        await self.attempt_component_recovery(component_id)
            
            except Exception as e:
                logger.error(f"Error in component monitor: {e}")
            
            # Wait before next check
            await asyncio.sleep(5)
    
    async def register_capability(self,
                        component_id: str,
                        capability_name: str,
                        capability_level: int = 100,
                        description: Optional[str] = None,
                        parameters: Optional[Dict[str, Any]] = None,
                        handler: Optional[Callable] = None) -> bool:
        """
        Register a capability for a component.
        
        Args:
            component_id: Component ID
            capability_name: Name of the capability
            capability_level: Level of capability (higher is better)
            description: Optional description
            parameters: Optional parameters for the capability
            handler: Optional handler function
            
        Returns:
            True if registered successfully
        """
        async with self.lock:
            return await register_capability_internal(
                self.components,
                self.degradation_manager,
                component_id,
                capability_name,
                capability_level,
                description,
                parameters,
                handler,
                self.data_dir
            )
    
    async def register_fallback_handler(self, 
                            component_id: str,
                            capability_name: str,
                            provider_id: str,
                            fallback_handler: Callable,
                            capability_level: int = 50) -> bool:
        """
        Register a fallback handler for a capability.
        
        Args:
            component_id: Component ID that requires the capability
            capability_name: Name of the capability
            provider_id: ID of the component providing the fallback
            fallback_handler: Function to call for fallback
            capability_level: Level of capability (higher is better)
            
        Returns:
            True if registered successfully
        """
        async with self.lock:
            return await register_fallback_handler_internal(
                self.components,
                self.degradation_manager,
                self.fallback_handlers,
                component_id,
                capability_name,
                provider_id,
                fallback_handler,
                capability_level
            )
    
    async def execute_with_fallback(self,
                        component_id: str,
                        capability_name: str,
                        *args, **kwargs) -> Any:
        """
        Execute a capability with fallback support.
        
        Args:
            component_id: ID of the component
            capability_name: Name of the capability
            *args: Arguments for the handler
            **kwargs: Keyword arguments for the handler
            
        Returns:
            Result from handler
            
        Raises:
            NoFallbackAvailableError: If no fallback is available
        """
        return await execute_with_fallback_internal(
            self.degradation_manager,
            self.fallback_handlers,
            component_id,
            capability_name,
            *args, **kwargs
        )
    
    async def get_fallback_status(self,
                        component_id: Optional[str] = None,
                        capability_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of registered fallbacks.
        
        Args:
            component_id: Optional component ID filter
            capability_name: Optional capability name filter
            
        Returns:
            Status information for fallbacks
        """
        return get_fallback_status_internal(
            self.degradation_manager,
            component_id,
            capability_name
        )
    
    async def get_fallback_handler(self, component_id: str, capability_name: str) -> Optional[Callable]:
        """
        Get a fallback handler for a capability (legacy method).
        
        Args:
            component_id: Component ID
            capability_name: Name of the capability
            
        Returns:
            Fallback handler or None
        """
        return get_fallback_handler_internal(
            self.fallback_handlers,
            component_id,
            capability_name
        )