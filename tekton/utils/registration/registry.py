"""
Component registration with Hermes service registry.
"""

import os
from shared.env import TektonEnviron
import json
import logging
import asyncio
import signal
import aiohttp
from typing import Dict, Any, Optional, List, Tuple

from .models import ComponentConfig, CapabilityConfig, MethodConfig

logger = logging.getLogger(__name__)


class HermesRegistrationClient:
    """Client for Hermes registration service."""
    
    def __init__(self, component_id: str, hermes_url: Optional[str] = None):
        """
        Initialize the client.
        
        Args:
            component_id: The ID of the component
            hermes_url: URL of the Hermes API (defaults to http://localhost:8001/api)
        """
        self.component_id = component_id
        self.hermes_url = hermes_url or TektonEnviron.get("HERMES_URL", "http://localhost:8001/api")
        self.session = None
        self.heartbeat_task = None
        self.running = False
    
    async def _ensure_session(self) -> None:
        """Ensure that an HTTP session exists."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def register(self, config: ComponentConfig) -> bool:
        """
        Register the component with Hermes.
        
        Args:
            config: The component configuration
            
        Returns:
            True if successful, False otherwise
        """
        await self._ensure_session()
        
        # Convert capabilities to the format expected by Hermes
        capabilities = self._format_capabilities(config.capabilities)
        
        # Registration payload
        payload = {
            "component_id": config.id,
            "name": config.name,
            "version": config.version,
            "description": config.description or f"The {config.name} component",
            "host": "localhost",
            "port": config.port,
            "capabilities": capabilities,
            "metadata": config.config
        }
        
        # Send registration request
        try:
            url = f"{self.hermes_url}/register"
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        logger.info(f"Registered component {config.id} with Hermes")
                        return True
                    else:
                        logger.error(f"Failed to register component: {data.get('message')}")
                        return False
                else:
                    logger.error(f"Failed to register component: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error registering component: {e}")
            return False
    
    async def unregister(self) -> bool:
        """
        Unregister the component from Hermes.
        
        Returns:
            True if successful, False otherwise
        """
        await self._ensure_session()
        
        # Unregister payload
        payload = {
            "component_id": self.component_id
        }
        
        # Send unregister request
        try:
            url = f"{self.hermes_url}/unregister"
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        logger.info(f"Unregistered component {self.component_id} from Hermes")
                        return True
                    else:
                        logger.error(f"Failed to unregister component: {data.get('message')}")
                        return False
                else:
                    logger.error(f"Failed to unregister component: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error unregistering component: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the registration status of the component.
        
        Returns:
            A dictionary with the registration status
        """
        await self._ensure_session()
        
        # Query status
        try:
            url = f"{self.hermes_url}/registry/components/{self.component_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "registered": True,
                        "status": "active",
                        "details": data
                    }
                elif response.status == 404:
                    return {
                        "registered": False,
                        "status": "not_found",
                        "details": {}
                    }
                else:
                    logger.error(f"Failed to get component status: {response.status}")
                    return {
                        "registered": False,
                        "status": "unknown",
                        "details": {"error": f"HTTP {response.status}"}
                    }
        except Exception as e:
            logger.error(f"Error getting component status: {e}")
            return {
                "registered": False,
                "status": "error",
                "details": {"error": str(e)}
            }
    
    async def heartbeat(self) -> None:
        """Send heartbeat to Hermes."""
        await self._ensure_session()
        
        # Heartbeat payload
        payload = {
            "component_id": self.component_id
        }
        
        # Send heartbeat request
        try:
            url = f"{self.hermes_url}/heartbeat"
            async with self.session.post(url, json=payload) as response:
                if response.status != 200:
                    logger.warning(f"Heartbeat failed: {response.status}")
        except Exception as e:
            logger.warning(f"Error sending heartbeat: {e}")
    
    async def start_heartbeat(self, interval: int = 30) -> None:
        """
        Start sending heartbeats to Hermes.
        
        Args:
            interval: Heartbeat interval in seconds
        """
        self.running = True
        
        # Define the heartbeat loop
        async def heartbeat_loop():
            while self.running:
                await self.heartbeat()
                await asyncio.sleep(interval)
        
        # Create the heartbeat task
        self.heartbeat_task = asyncio.create_task(heartbeat_loop())
    
    async def stop_heartbeat(self) -> None:
        """Stop sending heartbeats to Hermes."""
        self.running = False
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            self.heartbeat_task = None
    
    async def close(self) -> None:
        """Close the client."""
        await self.stop_heartbeat()
        
        if self.session:
            await self.session.close()
            self.session = None
    
    def _format_capabilities(self, capabilities: List[CapabilityConfig]) -> List[Dict[str, Any]]:
        """
        Format capabilities for the Hermes API.
        
        Args:
            capabilities: List of capabilities
            
        Returns:
            List of formatted capabilities
        """
        formatted_capabilities = []
        
        for capability in capabilities:
            formatted_methods = []
            
            for method in capability.methods:
                formatted_parameters = []
                
                for param in method.parameters:
                    formatted_parameters.append({
                        "name": param.name,
                        "type": param.type,
                        "required": param.required,
                        "description": param.description or "",
                        "default": param.default
                    })
                
                formatted_returns = None
                if method.returns:
                    formatted_returns = {
                        "type": method.returns.type,
                        "description": method.returns.description or ""
                    }
                
                formatted_methods.append({
                    "id": method.id,
                    "name": method.name,
                    "description": method.description or "",
                    "parameters": formatted_parameters,
                    "returns": formatted_returns
                })
            
            formatted_capabilities.append({
                "id": capability.id,
                "name": capability.name,
                "description": capability.description or "",
                "methods": formatted_methods
            })
        
        return formatted_capabilities


async def register_component(
    component_id: str,
    config: ComponentConfig,
    hermes_url: Optional[str] = None,
    start_heartbeat: bool = True
) -> Tuple[bool, HermesRegistrationClient]:
    """
    Register a component with Hermes.
    
    Args:
        component_id: The ID of the component
        config: The component configuration
        hermes_url: URL of the Hermes API
        start_heartbeat: Whether to start the heartbeat
        
    Returns:
        A tuple of (success, client)
    """
    # Create registration client
    client = HermesRegistrationClient(component_id, hermes_url)
    
    # Register the component
    success = await client.register(config)
    
    # Start heartbeat if requested and registration was successful
    if success and start_heartbeat:
        await client.start_heartbeat()
    
    return success, client


async def unregister_component(
    component_id: str,
    hermes_url: Optional[str] = None
) -> bool:
    """
    Unregister a component from Hermes.
    
    Args:
        component_id: The ID of the component
        hermes_url: URL of the Hermes API
        
    Returns:
        True if successful, False otherwise
    """
    # Create registration client
    client = HermesRegistrationClient(component_id, hermes_url)
    
    # Unregister the component
    success = await client.unregister()
    
    # Close the client
    await client.close()
    
    return success


async def get_registration_status(
    component_id: str,
    hermes_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the registration status of a component.
    
    Args:
        component_id: The ID of the component
        hermes_url: URL of the Hermes API
        
    Returns:
        A dictionary with the registration status
    """
    # Create registration client
    client = HermesRegistrationClient(component_id, hermes_url)
    
    # Get the status
    status = await client.get_status()
    
    # Close the client
    await client.close()
    
    return status