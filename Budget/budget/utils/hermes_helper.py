"""
Hermes Integration Helper for Budget Component

This module provides utilities for integrating the Budget component
with the Hermes service registry following Tekton's Single Port Architecture pattern.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple

# Try to import debug_utils from shared if available
try:
    from shared.debug.debug_utils import debug_log, log_function
except ImportError:
    # Create a simple fallback if shared module is not available
    class DebugLog:
        def __getattr__(self, name):
            def dummy_log(*args, **kwargs):
                pass
            return dummy_log
    debug_log = DebugLog()
    
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Configure logger
logger = logging.getLogger(__name__)

class HermesRegistrationClient:
    """
    Client for registering the Budget component with Hermes service registry.
    
    This class provides functionality to register the Budget component,
    maintain heartbeats, and gracefully unregister on shutdown.
    """
    
    def __init__(
        self,
        component_id: str = "budget",
        component_name: str = "Budget",
        component_type: str = "budget_manager",
        component_version: str = "0.1.0",
        hermes_url: Optional[str] = None,
        endpoint: Optional[str] = None,
        heartbeat_interval: int = 60
    ):
        """
        Initialize the Hermes registration client.
        
        Args:
            component_id: Unique identifier for this component
            component_name: Human-readable name
            component_type: Type of component
            component_version: Component version
            hermes_url: Hermes API endpoint
            endpoint: Budget component endpoint
            heartbeat_interval: Interval in seconds for sending heartbeats
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.component_version = component_version
        self.endpoint = endpoint
        self.heartbeat_interval = heartbeat_interval
        
        # Process Hermes URL from environment or use default
        self.hermes_url = hermes_url or os.environ.get("HERMES_URL", "http://localhost:8001/api")
        
        # Define component capabilities
        self.capabilities = [
            {
                "name": "budget_management",
                "description": "Manage token and cost budgets for LLM usage",
                "parameters": {
                    "budget_id": "string",
                    "period": "string",
                    "tier": "string",
                    "limit": "integer"
                }
            },
            {
                "name": "allocation",
                "description": "Allocate tokens from a budget",
                "parameters": {
                    "context_id": "string",
                    "tokens": "integer",
                    "tier": "string",
                    "model": "string",
                    "provider": "string"
                }
            },
            {
                "name": "usage_tracking",
                "description": "Track token and cost usage",
                "parameters": {
                    "context_id": "string",
                    "input_tokens": "integer",
                    "output_tokens": "integer",
                    "provider": "string",
                    "model": "string"
                }
            },
            {
                "name": "pricing",
                "description": "Manage and retrieve provider pricing information",
                "parameters": {
                    "provider": "string",
                    "model": "string"
                }
            },
            {
                "name": "reporting",
                "description": "Generate budget usage reports",
                "parameters": {
                    "budget_id": "string",
                    "period": "string",
                    "start_date": "string",
                    "end_date": "string"
                }
            },
            {
                "name": "model_guidance",
                "description": "Provide model recommendations based on budget constraints",
                "parameters": {
                    "task_type": "string",
                    "context_id": "string",
                    "max_cost": "number"
                }
            }
        ]
        
        # Define MCP capabilities
        self.mcp_capabilities = [
            {
                "protocol": "mcp",
                "version": "1.0",
                "message_types": [
                    {
                        "type": "budget.allocate_tokens",
                        "description": "Allocate tokens for a task",
                        "response_type": "budget.allocation_response"
                    },
                    {
                        "type": "budget.check_budget",
                        "description": "Check if a request is within budget",
                        "response_type": "budget.check_response"
                    },
                    {
                        "type": "budget.record_usage",
                        "description": "Record token usage",
                        "response_type": "budget.usage_response"
                    },
                    {
                        "type": "budget.get_budget_status",
                        "description": "Get budget status",
                        "response_type": "budget.status_response"
                    },
                    {
                        "type": "budget.get_model_recommendations",
                        "description": "Get model recommendations",
                        "response_type": "budget.recommendations_response"
                    },
                    {
                        "type": "budget.route_with_budget_awareness",
                        "description": "Route a request based on budget constraints",
                        "response_type": "budget.routing_response"
                    },
                    {
                        "type": "budget.get_usage_analytics",
                        "description": "Get usage analytics",
                        "response_type": "budget.analytics_response"
                    }
                ],
                "events": [
                    {
                        "type": "budget.limit_exceeded",
                        "description": "Budget limit exceeded"
                    },
                    {
                        "type": "budget.limit_approaching",
                        "description": "Budget limit approaching"
                    },
                    {
                        "type": "budget.price_update",
                        "description": "Provider pricing update"
                    }
                ],
                "endpoint": "/api/mcp/message"
            }
        ]
        
        # Define component dependencies
        self.dependencies = []
        
        # Define component metadata
        self.metadata = {
            "description": "Budget management system for token and cost tracking",
            "version": component_version,
            "ui_enabled": True,
            "ui_component": "budget-dashboard",
            "supports_mcp": True,
            "websocket_endpoints": [
                {
                    "path": "/ws/budget/updates",
                    "description": "WebSocket endpoint for real-time budget updates"
                }
            ]
        }
        
        # Runtime variables
        self._is_registered = False
        self._heartbeat_task = None
        self._shutdown_event = asyncio.Event()
        
    @log_function()
    async def register(self) -> bool:
        """
        Register this component with Hermes.
        
        Returns:
            True if registration was successful
        """
        debug_log.info("budget_hermes", "Registering Budget component with Hermes")
        
        try:
            # Try to import HermesClient if available
            try:
                from hermes.api.client import HermesClient
                # Use HermesClient implementation
                # ...
                # This would be implemented with the actual HermesClient
                pass
            except ImportError:
                debug_log.info("budget_hermes", "HermesClient not available, using HTTP implementation")
            
            # Use HTTP API implementation
            import aiohttp
            
            # Prepare registration data
            registration_data = {
                "component_id": self.component_id,
                "name": self.component_name,
                "type": self.component_type,
                "version": self.component_version,
                "capabilities": self.capabilities,
                "mcp_capabilities": self.mcp_capabilities,
                "dependencies": self.dependencies,
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
                        debug_log.info("budget_hermes", f"Successfully registered with Hermes: {data}")
                        self._is_registered = True
                        await self._start_heartbeat()
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to register with Hermes: {error_text}")
                        debug_log.error("budget_hermes", f"Registration failed: {error_text}")
                        
                        # If Hermes is not available, try file-based registration
                        await self._register_via_file()
                        return True
                        
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            debug_log.error("budget_hermes", f"Registration error: {str(e)}")
            
            # Fallback to file-based registration
            success = await self._register_via_file()
            return success
    
    @log_function()
    async def _register_via_file(self) -> bool:
        """
        Register via file-based method (for development environments).
        
        Returns:
            True if registration was successful
        """
        try:
            # Find the Hermes directory
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            parent_dir = os.path.dirname(current_dir)
            hermes_dir = os.path.join(parent_dir, "Hermes")
            
            if not os.path.exists(hermes_dir):
                debug_log.warn("budget_hermes", f"Hermes directory not found at {hermes_dir}")
                return False
            
            # Create registration directory if it doesn't exist
            registration_dir = os.path.join(hermes_dir, "registrations")
            os.makedirs(registration_dir, exist_ok=True)
            
            import uuid
            import time
            
            # Create registration data
            registration_data = {
                "component_id": self.component_id,
                "name": self.component_name,
                "type": self.component_type,
                "version": self.component_version,
                "capabilities": self.capabilities,
                "mcp_capabilities": self.mcp_capabilities,
                "dependencies": self.dependencies,
                "metadata": self.metadata,
                "endpoint": self.endpoint,
                "instance_uuid": str(uuid.uuid4()),
                "registration_time": time.time(),
                "status": "active"
            }
            
            # Write registration to file
            registration_file = os.path.join(registration_dir, f"{self.component_id}.json")
            with open(registration_file, "w") as f:
                json.dump(registration_data, f, indent=2)
                
            logger.info(f"Created registration file for {self.component_name} at {registration_file}")
            debug_log.info("budget_hermes", f"Created registration file at {registration_file}")
            
            self._is_registered = True
            await self._start_heartbeat()
            return True
            
        except Exception as e:
            logger.error(f"Error during file-based registration: {e}")
            debug_log.error("budget_hermes", f"File registration error: {str(e)}")
            return False
    
    @log_function()
    async def unregister(self) -> bool:
        """
        Unregister this component from Hermes.
        
        Returns:
            True if unregistration was successful
        """
        if not self._is_registered:
            debug_log.info("budget_hermes", "Component is not registered")
            return True
            
        debug_log.info("budget_hermes", "Unregistering Budget component from Hermes")
        
        try:
            # Stop heartbeat first
            await self._stop_heartbeat()
            
            try:
                # Try direct client if available
                from hermes.api.client import HermesClient
                # Use HermesClient implementation
                # ...
                pass
            except ImportError:
                # Use HTTP API implementation
                import aiohttp
                
                # Unregister with Hermes
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.hermes_url}/registration/unregister",
                        json={"component_id": self.component_id}
                    ) as response:
                        if response.status == 200:
                            logger.info(f"Successfully unregistered {self.component_name} from Hermes")
                            debug_log.info("budget_hermes", "Successfully unregistered from Hermes")
                            self._is_registered = False
                            return True
                        else:
                            error_text = await response.text()
                            logger.error(f"Failed to unregister with Hermes: {error_text}")
                            debug_log.error("budget_hermes", f"Unregistration failed: {error_text}")
                            
                            # Try to unregister via file
                            return await self._unregister_via_file()
                            
        except Exception as e:
            logger.error(f"Error during unregistration: {e}")
            debug_log.error("budget_hermes", f"Unregistration error: {str(e)}")
            
            # Fallback to file-based unregistration
            return await self._unregister_via_file()
    
    @log_function()
    async def _unregister_via_file(self) -> bool:
        """
        Unregister via file-based method (for development environments).
        
        Returns:
            True if unregistration was successful
        """
        try:
            # Find the Hermes directory
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            parent_dir = os.path.dirname(current_dir)
            hermes_dir = os.path.join(parent_dir, "Hermes")
            
            if not os.path.exists(hermes_dir):
                debug_log.warn("budget_hermes", f"Hermes directory not found at {hermes_dir}")
                return False
            
            # Remove registration file
            registration_file = os.path.join(hermes_dir, "registrations", f"{self.component_id}.json")
            if os.path.exists(registration_file):
                os.remove(registration_file)
                logger.info(f"Removed registration file for {self.component_name}")
                debug_log.info("budget_hermes", f"Removed registration file at {registration_file}")
            
            self._is_registered = False
            return True
            
        except Exception as e:
            logger.error(f"Error during file-based unregistration: {e}")
            debug_log.error("budget_hermes", f"File unregistration error: {str(e)}")
            return False
    
    @log_function()
    async def _heartbeat_loop(self):
        """Continuously send heartbeats to Hermes."""
        try:
            import aiohttp
            
            logger.info(f"Starting heartbeat for {self.component_id} (interval: {self.heartbeat_interval}s)")
            debug_log.info("budget_hermes", f"Starting heartbeat loop (interval: {self.heartbeat_interval}s)")
            
            while not self._shutdown_event.is_set():
                try:
                    # Send heartbeat via HTTP API
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{self.hermes_url}/registration/heartbeat",
                            json={"component_id": self.component_id, "status": "healthy"}
                        ) as response:
                            if response.status != 200:
                                error_text = await response.text()
                                logger.warning(f"Failed to send heartbeat: {error_text}")
                                debug_log.warn("budget_hermes", f"Heartbeat failed: {error_text}")
                            else:
                                debug_log.debug("budget_hermes", "Heartbeat sent successfully")
                
                except Exception as e:
                    logger.error(f"Error sending heartbeat: {e}")
                    debug_log.error("budget_hermes", f"Heartbeat error: {str(e)}")
                
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
            logger.error(f"Heartbeat loop failed: {e}")
            debug_log.error("budget_hermes", f"Heartbeat loop error: {str(e)}")
            
    @log_function()
    async def _start_heartbeat(self):
        """Start the heartbeat task."""
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._shutdown_event.clear()
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            debug_log.debug("budget_hermes", "Heartbeat task started")
            
    @log_function()
    async def _stop_heartbeat(self):
        """Stop the heartbeat task."""
        if self._heartbeat_task is not None and not self._heartbeat_task.done():
            self._shutdown_event.set()
            try:
                await asyncio.wait_for(self._heartbeat_task, timeout=5)
            except asyncio.TimeoutError:
                logger.warning("Heartbeat task did not stop cleanly, cancelling")
                debug_log.warn("budget_hermes", "Heartbeat task timeout, cancelling")
                self._heartbeat_task.cancel()
            debug_log.debug("budget_hermes", "Heartbeat task stopped")
            
    @log_function()
    async def close(self):
        """
        Clean up resources and unregister if necessary.
        
        Call this method when shutting down the component.
        """
        debug_log.info("budget_hermes", "Closing Hermes registration client")
        
        if self._is_registered:
            await self.unregister()

# Simplified function for registering the Budget component
@log_function()
async def register_budget_component(endpoint: Optional[str] = None) -> Optional[HermesRegistrationClient]:
    """
    Register the Budget component with Hermes.
    
    Args:
        endpoint: The Budget component API endpoint
        
    Returns:
        Registration client if successful, None otherwise
    """
    # Get component version from package or environment
    version = os.environ.get("BUDGET_VERSION", "0.1.0")
    
    # Create client
    client = HermesRegistrationClient(
        component_version=version,
        endpoint=endpoint
    )
    
    # Register component
    success = await client.register()
    if success:
        debug_log.info("budget_hermes", "Budget component registered successfully")
        return client
    else:
        debug_log.error("budget_hermes", "Failed to register Budget component")
        await client.close()
        return None