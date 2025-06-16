#!/usr/bin/env python3
"""
Tekton StartUp Handler Module

This module provides functions and classes for handling component startup
instructions, including event handling and instruction processing.
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Callable, Optional

from tekton.core.startup_instructions import StartUpInstructions
from tekton.core.lifecycle import (
    ComponentState,
    ComponentRegistration
)

logger = logging.getLogger("tekton.startup_handler")


async def handle_startup_instructions(
        instructions: StartUpInstructions,
        component_handlers: Dict[str, Dict[str, Any]],
        start_component_func: Callable,
        message_bus=None) -> bool:
    """
    Handle startup instructions for a component.
    
    Args:
        instructions: Startup instructions
        component_handlers: Map of component IDs to handler configs
        start_component_func: Function to start a component
        message_bus: Optional message bus for triggering
        
    Returns:
        True if handled successfully
    """
    component_id = instructions.component_id
    
    # Check if we have a handler for this component
    if component_id not in component_handlers:
        logger.warning(f"No handler for component {component_id}")
        return False
        
    config = component_handlers[component_id]
    
    # Handle different activation modes
    if instructions.activation_mode == "immediate":
        # Start immediately
        success, _ = await start_component_func(
            component_id=component_id,
            start_func=config.get("start_func"),
            dependencies=instructions.dependencies,
            timeout=instructions.timeout or 60,
            component_type=instructions.component_type,
            component_name=instructions.component_name or component_id,
            version=instructions.version or "0.1.0",
            capabilities=instructions.capabilities,
            metadata=instructions.metadata
        )
        
        return success
        
    elif instructions.activation_mode == "trigger":
        # Store the instructions for later triggering
        trigger = instructions.activation_trigger
        if not trigger:
            logger.error(f"No activation trigger specified for {component_id}")
            return False
            
        # Subscribe to the trigger topic if message bus is available
        if message_bus:
            try:
                # Create a handler for this specific trigger
                async def trigger_handler(message):
                    await start_component_func(
                        component_id=component_id,
                        start_func=config.get("start_func"),
                        dependencies=instructions.dependencies,
                        timeout=instructions.timeout or 60,
                        component_type=instructions.component_type,
                        component_name=instructions.component_name or component_id,
                        version=instructions.version or "0.1.0",
                        capabilities=instructions.capabilities,
                        metadata=instructions.metadata
                    )
                    
                # Subscribe to the trigger topic
                await message_bus.subscribe(trigger, trigger_handler)
                logger.info(f"Subscribed to trigger {trigger} for {component_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error subscribing to trigger: {e}")
                return False
        else:
            logger.warning(f"Message bus not available for trigger mode")
            return False
            
    elif instructions.activation_mode == "manual":
        # Do nothing, component will be started manually
        logger.info(f"Component {component_id} set to manual activation")
        return True
        
    else:
        logger.error(f"Unknown activation mode: {instructions.activation_mode}")
        return False


async def execute_start_func(start_func: Callable[[], Any]) -> Any:
    """
    Execute a start function, handling both sync and async functions.
    
    Args:
        start_func: Function to execute
        
    Returns:
        Function result
    """
    result = start_func()
    
    # Handle async functions
    if asyncio.iscoroutine(result):
        result = await result
        
    return result


async def notify_dependent_components(component_id: str, message_bus=None) -> None:
    """
    Notify components that depend on a component that is now ready.
    
    Args:
        component_id: ID of the component that is now ready
        message_bus: Optional message bus for publishing notifications
    """
    # If message bus is available, publish notification
    if message_bus:
        try:
            await message_bus.publish(
                f"tekton.component.{component_id}.ready",
                {
                    "event": "dependency_ready",
                    "component_id": component_id,
                    "timestamp": time.time()
                }
            )
            logger.debug(f"Published ready notification for {component_id}")
        except Exception as e:
            logger.error(f"Error publishing ready notification: {e}")


class InstructionHandler:
    """
    Handles lifecycle and startup instruction events for component coordination.
    """
    
    def __init__(self, registry, message_queues=None, message_bus=None):
        """
        Initialize the instruction handler.
        
        Args:
            registry: Component registry
            message_queues: Optional message queues
            message_bus: Optional message bus
        """
        self.registry = registry
        self.message_queues = message_queues or {}
        self.message_bus = message_bus
        self.component_handlers = {}
        
    async def handle_component_lifecycle(self, message: Dict[str, Any]) -> None:
        """
        Handle a component lifecycle event.
        
        Args:
            message: Lifecycle event message
        """
        event = message.get("event")
        component_id = message.get("component_id")
        
        if not event or not component_id:
            logger.warning(f"Received invalid lifecycle message: {message}")
            return
        
        # Handle different lifecycle events
        if event == "registered":
            logger.info(f"Component {component_id} registered")
            
            # Add message to persistent queue
            queue = self.message_queues.get("tekton.component.lifecycle")
            if queue:
                await queue.add_message(message, "coordinator")
                
        elif event == "state_changed":
            old_state = message.get("old_state")
            new_state = message.get("state")
            logger.info(f"Component {component_id} state changed: {old_state} -> {new_state}")
            
            # Add message to persistent queue
            queue = self.message_queues.get("tekton.component.lifecycle")
            if queue:
                await queue.add_message(message, "coordinator")
                
        elif event == "ready":
            logger.info(f"Component {component_id} is ready")
            
            # Notify any components waiting for this one
            await notify_dependent_components(component_id, self.message_bus)
    
    async def handle_startup_instructions_message(self, message: Dict[str, Any]) -> None:
        """
        Handle startup instructions message.
        
        Args:
            message: Startup instructions message
        """
        try:
            # Parse startup instructions
            instructions = StartUpInstructions.from_dict(message)
            component_id = instructions.component_id
            
            # Check if we have a handler for this component
            if component_id in self.component_handlers:
                logger.info(f"Processing startup instructions for {component_id}")
                
                # Handle the instructions
                await handle_startup_instructions(
                    instructions,
                    self.component_handlers,
                    self.start_component_func,
                    self.message_bus
                )
            else:
                logger.warning(f"No handler registered for component {component_id}")
                
            # Add message to persistent queue
            queue = self.message_queues.get("tekton.component.startup")
            if queue:
                await queue.add_message(message, "coordinator")
                
        except Exception as e:
            logger.error(f"Error handling startup instructions: {e}")
            
    def set_start_component_func(self, func):
        """Set the start component function."""
        self.start_component_func = func
    
    def set_component_handlers(self, handlers):
        """Set component handlers map."""
        self.component_handlers = handlers