#!/usr/bin/env python3
"""
Tekton StartUpProcess Module

This module provides the StartUpProcess class that manages component 
initialization and coordinates the startup sequence.
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable, Set, TypedDict
from pathlib import Path
from datetime import datetime, timedelta

from tekton.core.startup_instructions import StartUpInstructions

try:
    from hermes.core.message_bus import MessageBus
    from hermes.core.service_discovery import ServiceRegistry
    HERMES_AVAILABLE = True
except ImportError:
    HERMES_AVAILABLE = False

logger = logging.getLogger("tekton.startup_process")

class ComponentStatus(TypedDict, total=False):
    """Component status information."""
    component_id: str
    status: str  # 'starting', 'running', 'stopped', 'failed'
    start_time: Optional[str]
    pid: Optional[int]
    hostname: Optional[str]
    endpoint: Optional[str]
    last_heartbeat: Optional[str]
    error: Optional[str]

class StartUpProcess:
    """
    Manages the startup process for Tekton components.
    
    This class coordinates the startup of components, ensuring dependencies
    are satisfied and handling activation triggers.
    """
    
    def __init__(self, 
                data_dir: Optional[str] = None,
                use_message_bus: bool = True):
        """
        Initialize the startup process.
        
        Args:
            data_dir: Directory for storing startup state
            use_message_bus: Whether to use the message bus for communication
        """
        from shared.env import TektonEnviron
        tekton_root = TektonEnviron.get('TEKTON_ROOT') or '/Users/cskoons/projects/github/Tekton'
        self.data_dir = data_dir or os.path.join(tekton_root, ".tekton", "startup")
        self.status_file = os.path.join(self.data_dir, "component_status.json")
        self.use_message_bus = use_message_bus and HERMES_AVAILABLE
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Component status tracking
        self.component_status: Dict[str, ComponentStatus] = {}
        self.pending_components: Set[str] = set()
        self.running_components: Set[str] = set()
        self.failed_components: Set[str] = set()
        
        # Message bus
        self.message_bus = None
        self.service_registry = None
        
    async def initialize(self) -> bool:
        """
        Initialize the startup process.
        
        Returns:
            True if successful
        """
        logger.info("Initializing Tekton startup process")
        
        # Load existing component status if available
        await self._load_status()
        
        # Initialize message bus if using it
        if self.use_message_bus:
            try:
                # Initialize the message bus
                self.message_bus = MessageBus()
                await self.message_bus.connect()
                
                # Initialize the service registry
                self.service_registry = ServiceRegistry()
                await self.service_registry.start()
                
                # Subscribe to component status updates
                await self.message_bus.subscribe(
                    "tekton.component.status", 
                    self._handle_status_update
                )
                
                # Subscribe to startup completion topic
                await self.message_bus.subscribe(
                    "tekton.component.startup_complete",
                    self._handle_startup_complete
                )
                
                logger.info("Connected to message bus")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize message bus: {e}")
                self.use_message_bus = False
                # Continue without message bus
        
        return True
        
    async def shutdown(self) -> bool:
        """
        Shutdown the startup process.
        
        Returns:
            True if successful
        """
        logger.info("Shutting down Tekton startup process")
        
        # Save current component status
        await self._save_status()
        
        # Disconnect from message bus if connected
        if self.use_message_bus and self.message_bus:
            try:
                await self.message_bus.disconnect()
                logger.info("Disconnected from message bus")
            except Exception as e:
                logger.error(f"Error disconnecting from message bus: {e}")
        
        return True
        
    async def _load_status(self) -> None:
        """Load component status from the status file."""
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, 'r') as f:
                    status_data = json.load(f)
                    
                self.component_status = status_data.get("components", {})
                
                # Update component sets based on status
                for component_id, status in self.component_status.items():
                    if status.get("status") == "running":
                        self.running_components.add(component_id)
                    elif status.get("status") == "starting":
                        self.pending_components.add(component_id)
                    elif status.get("status") == "failed":
                        self.failed_components.add(component_id)
                        
                logger.info(f"Loaded status for {len(self.component_status)} components")
            except Exception as e:
                logger.error(f"Error loading component status: {e}")
                # Initialize with empty status
                self.component_status = {}
                
    async def _save_status(self) -> None:
        """Save component status to the status file."""
        try:
            with open(self.status_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.utcnow().isoformat(),
                    "components": self.component_status
                }, f, indent=2)
                
            logger.info(f"Saved status for {len(self.component_status)} components")
        except Exception as e:
            logger.error(f"Error saving component status: {e}")
            
    async def _handle_status_update(self, message: Dict[str, Any]) -> None:
        """
        Handle a component status update message.
        
        Args:
            message: Status update message
        """
        component_id = message.get("component_id")
        status = message.get("status")
        
        if not component_id or not status:
            logger.warning(f"Received invalid status update: {message}")
            return
            
        # Update component status
        self.component_status[component_id] = {
            **message,
            "last_heartbeat": datetime.utcnow().isoformat()
        }
        
        # Update component sets
        self._update_component_status_sets(component_id, status)
        
        # Save status to file
        await self._save_status()
        
    def _update_component_status_sets(self, component_id: str, status: str) -> None:
        """
        Update the component status sets based on a status change.
        
        Args:
            component_id: The component ID being updated
            status: The new status
        """
        if status == "running":
            self.running_components.add(component_id)
            self.pending_components.discard(component_id)
            self.failed_components.discard(component_id)
        elif status == "starting":
            self.pending_components.add(component_id)
            self.running_components.discard(component_id)
            self.failed_components.discard(component_id)
        elif status == "failed":
            self.failed_components.add(component_id)
            self.pending_components.discard(component_id)
            self.running_components.discard(component_id)
        elif status == "stopped":
            self.running_components.discard(component_id)
            self.pending_components.discard(component_id)
            self.failed_components.discard(component_id)
            
    async def _handle_startup_complete(self, message: Dict[str, Any]) -> None:
        """
        Handle a component startup completion message.
        
        Args:
            message: Startup completion message
        """
        component_id = message.get("component_id")
        success = message.get("success", False)
        
        if not component_id:
            logger.warning(f"Received invalid startup completion message: {message}")
            return
            
        # Update component status
        if success:
            await self.set_component_status(
                component_id=component_id,
                status="running",
                endpoint=message.get("endpoint"),
                hostname=message.get("hostname")
            )
            logger.info(f"Component {component_id} startup completed successfully")
        else:
            await self.set_component_status(
                component_id=component_id,
                status="failed",
                error=message.get("error", "Unknown startup error")
            )
            logger.error(f"Component {component_id} startup failed: {message.get('error')}")
            
    async def set_component_status(self, 
                                component_id: str, 
                                status: str, 
                                **kwargs) -> None:
        """
        Set the status of a component.
        
        Args:
            component_id: Component ID
            status: Status value ('starting', 'running', 'stopped', 'failed')
            **kwargs: Additional status information
        """
        # Update local status
        current_status = self.component_status.get(component_id, {})
        updated_status = {
            **current_status,
            "component_id": component_id,
            "status": status,
            "last_heartbeat": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        # If starting, set start time
        if status == "starting" and "start_time" not in updated_status:
            updated_status["start_time"] = datetime.utcnow().isoformat()
            
        self.component_status[component_id] = updated_status
        
        # Update component sets
        self._update_component_status_sets(component_id, status)
        
        # Save status to file
        await self._save_status()
        
        # Publish status update if using message bus
        if self.use_message_bus and self.message_bus:
            try:
                await self.message_bus.publish(
                    "tekton.component.status",
                    updated_status
                )
            except Exception as e:
                logger.error(f"Error publishing status update: {e}")
                
    async def send_startup_instructions(self, 
                                    instructions: StartUpInstructions) -> bool:
        """
        Send startup instructions to a component.
        
        Args:
            instructions: Startup instructions
            
        Returns:
            True if instructions were sent successfully
        """
        # Check if component is already running
        if instructions.component_id in self.running_components:
            logger.info(f"Component {instructions.component_id} is already running")
            return True
            
        # Set component status to starting
        await self.set_component_status(
            component_id=instructions.component_id,
            status="starting"
        )
        
        # Send instructions via message bus if available
        if self.use_message_bus and self.message_bus:
            try:
                # Send instructions to component-specific topic
                topic = f"tekton.component.{instructions.component_id}.startup"
                await self.message_bus.publish(topic, instructions.to_dict())
                
                # Also send to general startup topic
                await self.message_bus.publish(
                    "tekton.component.startup",
                    instructions.to_dict()
                )
                
                logger.info(f"Sent startup instructions to {instructions.component_id}")
                return True
            except Exception as e:
                logger.error(f"Error sending startup instructions: {e}")
                return False
        else:
            # Save instructions to file for components that poll
            try:
                instructions_file = os.path.join(
                    self.data_dir, 
                    f"{instructions.component_id}_instructions.json"
                )
                with open(instructions_file, 'w') as f:
                    json.dump(instructions.to_dict(), f, indent=2)
                    
                logger.info(f"Saved startup instructions for {instructions.component_id}")
                return True
            except Exception as e:
                logger.error(f"Error saving startup instructions: {e}")
                return False