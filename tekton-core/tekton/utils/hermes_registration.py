"""
Standardized Hermes Registration Utilities for Tekton Components.

This module provides a standardized interface for all Tekton components to
register with the Hermes service registry, maintain heartbeats, and handle
component capabilities registration.
"""

import os
import sys
import asyncio
import signal
import logging
import json
from typing import Dict, List, Any, Optional, Callable, Union, Tuple

# Configure logger
logger = logging.getLogger(__name__)

class HermesRegistrationClient:
    """
    Standardized client for Tekton component registration with Hermes.
    
    This class provides a consistent interface for all Tekton components
    to register with Hermes, manage their lifecycle, and maintain heartbeats.
    """
    
    def __init__(self,
                 component_id: str,
                 component_name: str,
                 component_type: str,
                 component_version: str,
                 capabilities: List[Dict[str, Any]],
                 hermes_url: Optional[str] = None,
                 dependencies: Optional[List[str]] = None,
                 endpoint: Optional[str] = None,
                 additional_metadata: Optional[Dict[str, Any]] = None,
                 heartbeat_interval: int = 60):
        """
        Initialize the registration client.
        
        Args:
            component_id: Unique identifier for this component (e.g., "athena.knowledge")
            component_name: Human-readable name (e.g., "Athena Knowledge Graph")
            component_type: Type of component (e.g., "knowledge_graph", "workflow_engine")
            component_version: Component version (e.g., "0.1.0")
            capabilities: List of component capabilities with their parameters
            hermes_url: Hermes API endpoint (reads from HERMES_URL env var if not provided)
            dependencies: List of component IDs this component depends on
            endpoint: Component API endpoint (for direct component access)
            additional_metadata: Additional component metadata
            heartbeat_interval: Interval in seconds for sending heartbeats
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.component_version = component_version
        self.capabilities = capabilities
        self.dependencies = dependencies or []
        self.endpoint = endpoint
        self.heartbeat_interval = heartbeat_interval
        
        # Process Hermes URL from environment if not provided
        from shared.urls import hermes_url as get_hermes_url
        self.hermes_url = hermes_url or get_hermes_url("/api")
        
        # Prepare metadata
        self.metadata = {
            "description": f"{component_name} component",
            "version": component_version,
            "component_type": component_type,
            "dependencies": self.dependencies
        }
        
        # Update with additional metadata if provided
        if additional_metadata:
            self.metadata.update(additional_metadata)
        
        # Runtime variables
        self._is_registered = False
        self._heartbeat_task = None
        self._shutdown_event = asyncio.Event()
        self._hermes_client = None
        
    async def _initialize_client(self):
        """Initialize the Hermes client."""
        try:
            # Try to import from direct Hermes path
            try:
                from hermes.api.client import HermesClient
                self._hermes_client = HermesClient(
                    component_id=self.component_id,
                    component_name=self.component_name,
                    component_type=self.component_type,
                    component_version=self.component_version,
                    hermes_endpoint=self.hermes_url,
                    capabilities=self.capabilities
                )
                return True
            except ImportError:
                logger.debug("Could not import HermesClient directly, falling back to HTTP interface")
                
            # Fallback to HTTP client (implemented below)
            import aiohttp
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Hermes client: {e}")
            return False
    
    async def register(self) -> bool:
        """
        Register this component with Hermes.
        
        Returns:
            True if registration was successful
        """
        if not await self._initialize_client():
            return False
            
        try:
            # If we have a direct client, use it
            if self._hermes_client:
                success = await self._hermes_client.register()
                if success:
                    self._is_registered = True
                    await self._start_heartbeat()
                return success
                
            # Otherwise use HTTP API
            import aiohttp
            
            # Prepare registration data
            registration_data = {
                "component_id": self.component_id,
                "name": self.component_name,
                "type": self.component_type,
                "version": self.component_version,
                "capabilities": self.capabilities,
                "metadata": self.metadata
            }
            
            if self.endpoint:
                registration_data["endpoint"] = self.endpoint
                
            # Register with Hermes
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/registration/register",
                    json=registration_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully registered {self.component_name} with Hermes")
                        self._is_registered = True
                        await self._start_heartbeat()
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to register with Hermes: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            return False
            
    async def unregister(self) -> bool:
        """
        Unregister this component from Hermes.
        
        Returns:
            True if unregistration was successful
        """
        if not self._is_registered:
            logger.info(f"Component {self.component_id} is not registered")
            return True
            
        try:
            # Stop heartbeat first
            await self._stop_heartbeat()
            
            # If we have a direct client, use it
            if self._hermes_client:
                success = await self._hermes_client.unregister()
                if success:
                    self._is_registered = False
                return success
                
            # Otherwise use HTTP API
            import aiohttp
            
            # Unregister with Hermes
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/registration/unregister",
                    json={"component_id": self.component_id}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Successfully unregistered {self.component_name} from Hermes")
                        self._is_registered = False
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to unregister with Hermes: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error during unregistration: {e}")
            return False
            
    async def _heartbeat_loop(self):
        """Continuously send heartbeats to Hermes."""
        try:
            import aiohttp
            
            logger.info(f"Starting heartbeat for {self.component_id} (interval: {self.heartbeat_interval}s)")
            
            while not self._shutdown_event.is_set():
                try:
                    # If we have a direct client, use it
                    if self._hermes_client:
                        await self._hermes_client.send_heartbeat()
                    else:
                        # Use HTTP API
                        async with aiohttp.ClientSession() as session:
                            async with session.post(
                                f"{self.hermes_url}/registration/heartbeat",
                                json={"component_id": self.component_id, "status": "healthy"}
                            ) as response:
                                if response.status != 200:
                                    error_text = await response.text()
                                    logger.warning(f"Failed to send heartbeat: {error_text}")
                    
                    # Wait for the next interval or until shutdown
                    try:
                        await asyncio.wait_for(
                            self._shutdown_event.wait(),
                            timeout=self.heartbeat_interval
                        )
                    except asyncio.TimeoutError:
                        # This is expected - it just means the interval elapsed
                        pass
                        
                except Exception as e:
                    logger.error(f"Error sending heartbeat: {e}")
                    # Wait a bit and try again
                    await asyncio.sleep(min(5, self.heartbeat_interval))
                    
        except Exception as e:
            logger.error(f"Heartbeat loop failed: {e}")
            
    async def _start_heartbeat(self):
        """Start the heartbeat task."""
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._shutdown_event.clear()
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.debug("Heartbeat task started")
            
    async def _stop_heartbeat(self):
        """Stop the heartbeat task."""
        if self._heartbeat_task is not None and not self._heartbeat_task.done():
            self._shutdown_event.set()
            try:
                await asyncio.wait_for(self._heartbeat_task, timeout=5)
            except asyncio.TimeoutError:
                logger.warning("Heartbeat task did not stop cleanly, cancelling")
                self._heartbeat_task.cancel()
            logger.debug("Heartbeat task stopped")
            
    async def close(self):
        """
        Clean up resources and unregister if necessary.
        
        Call this method when shutting down the component.
        """
        if self._is_registered:
            await self.unregister()
            
        # Clean up client if needed
        if self._hermes_client:
            try:
                await self._hermes_client.close()
            except Exception as e:
                logger.error(f"Error closing Hermes client: {e}")
                
    def setup_signal_handlers(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        """
        Set up signal handlers for graceful shutdown.
        
        Args:
            loop: Event loop to register handlers with (uses current loop if None)
        """
        def handle_signal(sig):
            logger.info(f"Received signal {sig}, initiating shutdown")
            asyncio.create_task(self.close())
            
        loop = loop or asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))

# Function-based interface for simplified usage
async def register_component(
    component_id: str,
    component_name: str,
    component_type: str,
    component_version: str,
    capabilities: List[Dict[str, Any]],
    hermes_url: Optional[str] = None,
    dependencies: Optional[List[str]] = None,
    endpoint: Optional[str] = None,
    additional_metadata: Optional[Dict[str, Any]] = None,
    heartbeat_interval: int = 60
) -> Optional[HermesRegistrationClient]:
    """
    Register a component with Hermes.
    
    This is a convenience function that creates a HermesRegistrationClient,
    registers the component, and returns the client for heartbeat management.
    
    Args:
        component_id: Unique identifier for this component
        component_name: Human-readable name
        component_type: Type of component
        component_version: Component version
        capabilities: List of component capabilities
        hermes_url: Hermes API endpoint
        dependencies: List of component IDs this component depends on
        endpoint: Component API endpoint
        additional_metadata: Additional component metadata
        heartbeat_interval: Interval in seconds for sending heartbeats
        
    Returns:
        Registration client if successful, None otherwise
    """
    client = HermesRegistrationClient(
        component_id=component_id,
        component_name=component_name,
        component_type=component_type,
        component_version=component_version,
        capabilities=capabilities,
        hermes_url=hermes_url,
        dependencies=dependencies,
        endpoint=endpoint,
        additional_metadata=additional_metadata,
        heartbeat_interval=heartbeat_interval
    )
    
    success = await client.register()
    if success:
        return client
    else:
        await client.close()
        return None

# Helper function for loading and parsing startup instructions
def load_startup_instructions(file_path: str) -> Dict[str, Any]:
    """
    Load startup instructions from a JSON file.
    
    Args:
        file_path: Path to the startup instructions file
        
    Returns:
        Startup instructions as a dictionary
    """
    try:
        with open(file_path, 'r') as f:
            instructions = json.load(f)
        return instructions
    except Exception as e:
        logger.error(f"Error loading startup instructions from {file_path}: {e}")
        return {}