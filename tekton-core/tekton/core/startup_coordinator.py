#!/usr/bin/env python3
"""
Tekton StartUpCoordinator Module

This module provides the StartUpCoordinator class to manage dependency-based
component launching and coordination with enhanced deadlock prevention.
"""

import os
import asyncio
import logging
import time
from typing import Dict, List, Any, Callable, Optional, Set, Tuple

from tekton.core.startup_instructions import StartUpInstructions
from tekton.core.lifecycle import (
    ComponentState,
    ReadinessCondition,
    ComponentRegistration,
    PersistentMessageQueue
)
from tekton.core.dependency import DependencyResolver
from tekton.core.component_lifecycle import ComponentRegistry
from tekton.core.startup_handler import (
    InstructionHandler,
    execute_start_func,
    notify_dependent_components,
    handle_startup_instructions
)
from tekton.core.startup_manager import (
    get_component_status,
    synchronize_with_service_registry,
    start_components_in_order,
    start_components_parallel
)

logger = logging.getLogger("tekton.startup_coordinator")


class EnhancedStartUpCoordinator:
    """
    Coordinates the startup of multiple Tekton components with deadlock prevention.
    
    This class handles dependency resolution with cycle detection, manages component
    state transitions, and ensures reliable communication during startup.
    """
    
    def __init__(self, 
                registry: Optional[ComponentRegistry] = None,
                data_dir: Optional[str] = None,
                message_bus_provider = None):
        """
        Initialize the startup coordinator.
        
        Args:
            registry: Optional ComponentRegistry instance
            data_dir: Optional data directory for persistent storage
            message_bus_provider: Optional message bus provider
        """
        self.registry = registry
        from shared.env import TektonEnviron
        tekton_root = TektonEnviron.get('TEKTON_ROOT') or '/Users/cskoons/projects/github/Tekton'
        self.data_dir = data_dir or os.path.join(tekton_root, ".tekton", "startup")
        self.message_bus_provider = message_bus_provider
        self.message_bus = None
        self.service_registry = None
        
        # Message queues for reliable communication
        self.message_queues = {}
        
        # Component handlers
        self.component_handlers = {}
        
        # Instruction handler
        self.instruction_handler = None
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def initialize(self) -> bool:
        """
        Initialize the coordinator.
        
        Returns:
            True if successful
        """
        # Create component registry if not provided
        if not self.registry:
            self.registry = ComponentRegistry(data_dir=self.data_dir)
        
        # Initialize message bus if provider available
        if self.message_bus_provider:
            try:
                logger.info("Initializing message bus...")
                self.message_bus = await self.message_bus_provider.get_message_bus()
                
                # Create message queues for key topics
                self.message_queues["tekton.component.lifecycle"] = PersistentMessageQueue("tekton.component.lifecycle")
                self.message_queues["tekton.component.startup"] = PersistentMessageQueue("tekton.component.startup")
                
                # Create instruction handler
                self.instruction_handler = InstructionHandler(
                    registry=self.registry,
                    message_queues=self.message_queues,
                    message_bus=self.message_bus
                )
                self.instruction_handler.set_start_component_func(self.start_component)
                
                # Subscribe to component lifecycle events
                await self.message_bus.subscribe(
                    "tekton.component.lifecycle",
                    self.instruction_handler.handle_component_lifecycle
                )
                
                # Subscribe to startup instructions
                await self.message_bus.subscribe(
                    "tekton.component.startup",
                    self.instruction_handler.handle_startup_instructions_message
                )
                
                logger.info("Message bus initialized")
                
                # Get service registry if available
                self.service_registry = await self.message_bus_provider.get_service_registry()
                if self.service_registry:
                    logger.info("Service registry initialized")
                
            except Exception as e:
                logger.error(f"Error initializing message bus: {e}")
                self.message_bus_provider = None
        
        return True
    
    async def register_component_handler(self, 
                                    component_id: str, 
                                    start_func: Callable[[], Any],
                                    dependencies: Optional[List[str]] = None,
                                    timeout: int = 60) -> bool:
        """
        Register a handler for a component.
        
        Args:
            component_id: Component ID
            start_func: Function to start the component
            dependencies: Optional list of dependencies
            timeout: Timeout in seconds
            
        Returns:
            True if registered successfully
        """
        self.component_handlers[component_id] = {
            "start_func": start_func,
            "dependencies": dependencies or [],
            "timeout": timeout
        }
        
        # Update instruction handler's component handlers
        if self.instruction_handler:
            self.instruction_handler.set_component_handlers(self.component_handlers)
        
        # Subscribe to component-specific startup topic if message bus is available
        if self.message_bus:
            try:
                topic = f"tekton.component.{component_id}.startup"
                
                await self.message_bus.subscribe(
                    topic,
                    self.instruction_handler.handle_startup_instructions_message
                )
                
                logger.info(f"Subscribed to startup instructions for {component_id}")
            except Exception as e:
                logger.error(f"Error subscribing to component topic: {e}")
        
        logger.info(f"Registered handler for component {component_id}")
        return True
    
    async def start_component(self, 
                          component_id: str, 
                          start_func: Callable[[], Any],
                          dependencies: Optional[List[str]] = None,
                          timeout: int = 60,
                          component_type: str = "component",
                          component_name: Optional[str] = None,
                          version: str = "0.1.0",
                          capabilities: Optional[List[Dict[str, Any]]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        """
        Start a component with enhanced deadlock prevention.
        
        Args:
            component_id: Component ID
            start_func: Function to start the component
            dependencies: Optional list of dependencies
            timeout: Timeout in seconds
            component_type: Type of component
            component_name: Human-readable name
            version: Component version
            capabilities: Optional capabilities
            metadata: Optional metadata
            
        Returns:
            Tuple of (success, error_message)
        """
        # Create registration for this component
        registration = ComponentRegistration(
            component_id=component_id,
            component_name=component_name or component_id,
            component_type=component_type,
            version=version,
            capabilities=capabilities,
            metadata=metadata
        )
        
        # Register component
        success, message = await self.registry.register_component(registration)
        if not success:
            logger.error(f"Failed to register component {component_id}: {message}")
            return False, message
        
        # Wait for dependencies if any
        if dependencies:
            logger.info(f"Waiting for dependencies of {component_id}: {dependencies}")
            
            # Add jitter to prevent thundering herd
            jitter = 0.1 * (hash(component_id) % 10) / 10.0
            await asyncio.sleep(jitter)
            
            # Wait for dependencies to be ready
            success, failed_deps = await self.registry.wait_for_dependencies(
                dependencies=dependencies,
                timeout=timeout,
                check_interval=0.5
            )
            
            if not success:
                # Update component state to FAILED
                await self.registry.update_component_state(
                    component_id=component_id,
                    instance_uuid=registration.instance_uuid,
                    state=ComponentState.FAILED.value,
                    metadata={
                        "error": f"Dependencies failed or timed out: {failed_deps}",
                        "failure_reason": "dependency_failure"
                    }
                )
                
                logger.error(f"Dependencies for {component_id} failed: {failed_deps}")
                return False, f"Dependencies failed: {failed_deps}"
        
        # Start the component
        try:
            # Update state to INITIALIZING
            await self.registry.update_component_state(
                component_id=component_id,
                instance_uuid=registration.instance_uuid,
                state=ComponentState.INITIALIZING.value
            )
            
            # Call the start function
            logger.info(f"Starting component {component_id}")
            start_time = time.time()
            
            # Execute with timeout
            try:
                result = await asyncio.wait_for(
                    execute_start_func(start_func),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"Timeout starting component {component_id}")
                
                # Update component state to FAILED
                await self.registry.update_component_state(
                    component_id=component_id,
                    instance_uuid=registration.instance_uuid,
                    state=ComponentState.FAILED.value,
                    metadata={
                        "error": f"Timeout executing start function",
                        "failure_reason": "start_timeout",
                        "elapsed_time": time.time() - start_time
                    }
                )
                
                return False, "Timeout starting component"
            
            # Check result
            if result:
                # Mark component as ready
                success, message = await self.registry.mark_component_ready(
                    component_id=component_id,
                    instance_uuid=registration.instance_uuid,
                    metadata={
                        "start_time": start_time,
                        "startup_duration": time.time() - start_time
                    }
                )
                
                if success:
                    logger.info(f"Component {component_id} started successfully")
                    
                    # Notify dependent components if using message bus
                    if self.message_bus:
                        await notify_dependent_components(component_id, self.message_bus)
                    
                    return True, None
                else:
                    logger.error(f"Failed to mark component {component_id} as ready: {message}")
                    return False, message
            else:
                # Update component state to FAILED
                await self.registry.update_component_state(
                    component_id=component_id,
                    instance_uuid=registration.instance_uuid,
                    state=ComponentState.FAILED.value,
                    metadata={
                        "error": "Start function returned False",
                        "failure_reason": "start_function_failed"
                    }
                )
                
                logger.error(f"Component {component_id} start function returned False")
                return False, "Start function returned False"
                
        except Exception as e:
            logger.error(f"Error starting component {component_id}: {e}")
            
            # Update component state to FAILED
            await self.registry.update_component_state(
                component_id=component_id,
                instance_uuid=registration.instance_uuid,
                state=ComponentState.FAILED.value,
                metadata={
                    "error": str(e),
                    "failure_reason": "exception"
                }
            )
            
            return False, str(e)
    
    async def start_components(self, 
                           component_configs: Dict[str, Dict[str, Any]],
                           resolve_dependencies: bool = True) -> Dict[str, bool]:
        """
        Start multiple components with deadlock prevention.
        
        Args:
            component_configs: Dictionary mapping component IDs to configs
            resolve_dependencies: Whether to resolve dependencies and order components
            
        Returns:
            Dictionary mapping component IDs to success status
        """
        if resolve_dependencies:
            # Start components in dependency order
            return await start_components_in_order(
                component_configs=component_configs,
                start_func=self.start_component,
                resolve_cycles=True
            )
        else:
            # Start components in parallel
            return await start_components_parallel(
                component_configs=component_configs,
                start_func=self.start_component
            )
    
    async def handle_startup_instructions(self, 
                                    instructions: StartUpInstructions,
                                    component_handlers: Dict[str, Dict[str, Any]]) -> bool:
        """
        Handle startup instructions for a component.
        
        Args:
            instructions: Startup instructions
            component_handlers: Map of component IDs to handler configs
            
        Returns:
            True if handled successfully
        """
        return await handle_startup_instructions(
            instructions=instructions,
            component_handlers=component_handlers,
            start_component_func=self.start_component,
            message_bus=self.message_bus
        )
    
    async def listen_for_startup_instructions(self, 
                                        component_handlers: Dict[str, Dict[str, Any]],
                                        timeout: Optional[int] = None) -> None:
        """
        Listen for startup instructions and handle them.
        
        Args:
            component_handlers: Map of component IDs to handler configs
            timeout: Optional timeout in seconds
        """
        if not self.message_bus:
            logger.warning("Message bus not available for listening")
            return
            
        # Store component handlers
        self.component_handlers = component_handlers
        if self.instruction_handler:
            self.instruction_handler.set_component_handlers(component_handlers)
        
        # Subscribe to the startup instructions topic
        try:
            logger.info(f"Listening for startup instructions for {len(component_handlers)} components")
            
            # Wait until timeout or forever
            if timeout:
                await asyncio.sleep(timeout)
            else:
                # Run indefinitely
                while True:
                    await asyncio.sleep(3600)  # Sleep for an hour at a time
                    
        except Exception as e:
            logger.error(f"Error in startup instruction listener: {e}")
            
    async def wait_for_component_ready(self, 
                                  component_id: str, 
                                  timeout: int = 60,
                                  check_interval: float = 0.5) -> bool:
        """
        Wait for a component to be in the ready state.
        
        Args:
            component_id: Component ID to wait for
            timeout: Timeout in seconds
            check_interval: Interval between status checks
            
        Returns:
            True if component is ready, False if timeout or failure
        """
        success, _ = await self.registry.wait_for_component_ready(
            component_id=component_id,
            timeout=timeout,
            check_interval=check_interval
        )
        
        return success
    
    async def synchronize_with_hermes(self) -> bool:
        """
        Synchronize component status with Hermes service registry.
        
        Returns:
            True if successful
        """
        return await synchronize_with_service_registry(
            registry=self.registry,
            service_registry=self.service_registry
        )
    
    async def get_component_status(self, component_id: str) -> Dict[str, Any]:
        """
        Get the status of a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component status dictionary
        """
        return await get_component_status(self.registry, component_id)
    
    async def get_all_component_status(self) -> List[Dict[str, Any]]:
        """
        Get the status of all components.
        
        Returns:
            List of component status dictionaries
        """
        return await self.registry.get_all_components()
    
    async def start_component_monitoring(self, heartbeat_timeout: int = 30) -> None:
        """
        Start monitoring component health.
        
        Args:
            heartbeat_timeout: Timeout in seconds before marking a component as failed
        """
        # Start registry monitoring task
        asyncio.create_task(self.registry.monitor_components(heartbeat_timeout))
        logger.info(f"Started component health monitoring with timeout {heartbeat_timeout}s")
    
    async def shutdown(self) -> None:
        """Shutdown the coordinator and release resources."""
        # Close message bus if available
        if self.message_bus:
            try:
                await self.message_bus.close()
                logger.info("Closed message bus connection")
            except Exception as e:
                logger.error(f"Error closing message bus: {e}")
        
        logger.info("Shutdown complete")


# Legacy compatibility wrapper
class StartUpCoordinator(EnhancedStartUpCoordinator):
    """Legacy compatibility wrapper for the enhanced coordinator."""
    
    async def start_component(self, 
                           component_id: str, 
                           start_func: Callable[[], Any],
                           dependencies: List[str] = None,
                           timeout: int = 30) -> bool:
        """Legacy method to start a component."""
        success, _ = await super().start_component(
            component_id=component_id,
            start_func=start_func,
            dependencies=dependencies,
            timeout=timeout
        )
        return success
    
    def topological_sort(self, dependency_graph: Dict[str, List[str]]) -> List[str]:
        """Legacy method for topological sorting."""
        result, _ = DependencyResolver.resolve_dependencies(dependency_graph)
        return result