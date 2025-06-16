"""Helper for Hermes integration.

This module provides helper functions for integrating with Hermes
and interacting with other Tekton components.
"""

import os
import sys
import json
import logging
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List, Union

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config

logger = logging.getLogger(__name__)

class HermesHelper:
    """Helper for Hermes integration."""
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Initialize the Hermes helper.
        
        Args:
            api_url: Optional URL for the Hermes API
        """
        # Get configuration
        config = get_component_config()
        hermes_port = config.hermes.port if hasattr(config, 'hermes') else int(os.environ.get("HERMES_PORT"))
        self.api_url = api_url or os.environ.get("HERMES_API_URL", f"http://localhost:{hermes_port}/api")
        self.is_registered = False
        self.services = {}
        
    async def register_service(
        self,
        service_id: str,
        name: str,
        version: str,
        capabilities: List[str],
        endpoint: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a service with Hermes.
        
        Args:
            service_id: Service identifier
            name: Human-readable name
            version: Service version
            capabilities: List of service capabilities
            endpoint: Service endpoint URL
            metadata: Additional service metadata
            
        Returns:
            Registration success status
        """
        try:
            # Try to use the direct Hermes ServiceRegistry API if available
            try:
                # Find the Hermes directory by looking in the parent of the current directory
                current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                parent_dir = os.path.dirname(current_dir)
                hermes_dir = os.path.join(parent_dir, "Hermes")
                
                if os.path.exists(hermes_dir):
                    # Add Hermes to path if not already there
                    if hermes_dir not in sys.path:
                        sys.path.insert(0, hermes_dir)
                    
                    # Import Hermes service registry
                    from hermes.core.service_discovery import ServiceRegistry
                    
                    # Create service registry client
                    registry = ServiceRegistry()
                    await registry.start()
                    
                    # Register the service
                    success = await registry.register(
                        service_id=service_id,
                        name=name,
                        version=version,
                        endpoint=endpoint,
                        capabilities=capabilities,
                        metadata=metadata or {}
                    )
                    
                    if success:
                        logger.info(f"Successfully registered {name} with Hermes (direct API)")
                        self.is_registered = True
                    else:
                        logger.warning(f"Failed to register {name} with Hermes (direct API)")
                    
                    await registry.stop()
                    return success
            except ImportError:
                logger.info("Hermes ServiceRegistry API not available, using HTTP API")
            
            # Fall back to HTTP API
            # Prepare registration data
            registration_data = {
                "service_id": service_id,
                "name": name,
                "version": version,
                "capabilities": capabilities,
                "endpoint": endpoint,
                "metadata": metadata or {}
            }
            
            # Register with Hermes
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/register",
                    json=registration_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            logger.info(f"Successfully registered {service_id} with Hermes (HTTP API)")
                            self.is_registered = True
                            return True
                        else:
                            logger.error(f"Failed to register with Hermes: {result.get('message')}")
                            return False
                    else:
                        logger.error(f"Failed to register with Hermes: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error registering with Hermes: {e}")
            return False
    
    async def discover_services(self) -> Dict[str, Any]:
        """
        Discover available services from Hermes.
        
        Returns:
            Dictionary of services
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/services") as response:
                    if response.status == 200:
                        result = await response.json()
                        self.services = result.get("services", {})
                        return self.services
                    else:
                        logger.error(f"Failed to discover services: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"Error discovering services: {e}")
            return {}
    
    async def find_service(self, capability: str) -> Optional[Dict[str, Any]]:
        """
        Find a service with a specific capability.
        
        Args:
            capability: Capability to look for
            
        Returns:
            Service information or None if not found
        """
        # Try to discover services if we haven't already
        if not self.services:
            await self.discover_services()
        
        # Find service with the requested capability
        for service_id, service in self.services.items():
            if capability in service.get("capabilities", []):
                return {
                    "service_id": service_id,
                    "endpoint": service.get("endpoint"),
                    "name": service.get("name"),
                    "version": service.get("version")
                }
        
        return None
    
    async def invoke_capability(
        self,
        service_id: str,
        capability: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Invoke a capability on a service.
        
        Args:
            service_id: Service identifier
            capability: Capability to invoke
            parameters: Parameters for the capability
            
        Returns:
            Result from the capability invocation
        """
        try:
            # Try to discover services if we haven't already
            if not self.services:
                await self.discover_services()
            
            # Check if service exists
            if service_id not in self.services:
                return {
                    "success": False,
                    "error": f"Service {service_id} not found"
                }
            
            # Get service endpoint
            service = self.services[service_id]
            endpoint = service.get("endpoint")
            
            if not endpoint:
                return {
                    "success": False,
                    "error": f"No endpoint found for service {service_id}"
                }
            
            # Invoke capability
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{endpoint}/invoke/{capability}",
                    json=parameters
                ) as response:
                    result = await response.json()
                    return result
        except Exception as e:
            logger.error(f"Error invoking capability {capability} on {service_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source: str = "telos"
    ) -> bool:
        """
        Publish an event to Hermes.
        
        Args:
            event_type: Type of event
            payload: Event payload
            source: Event source
            
        Returns:
            Success status
        """
        try:
            # Prepare event data
            event_data = {
                "event_type": event_type,
                "source": source,
                "payload": payload
            }
            
            # Publish event
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/events",
                    json=event_data
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        logger.error(f"Failed to publish event: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False


async def register_with_hermes(
    service_id: str,
    name: str,
    capabilities: List[str],
    metadata: Optional[Dict[str, Any]] = None,
    version: str = "0.1.0",
    endpoint: Optional[str] = None
) -> bool:
    """Register a service with the Hermes service registry.
    
    Args:
        service_id: Unique identifier for the service
        name: Human-readable name for the service
        capabilities: List of service capabilities
        metadata: Additional metadata for the service
        version: Service version
        endpoint: Service endpoint URL
        
    Returns:
        Success status
    """
    # Use environment variable for endpoint if not provided
    if not endpoint:
        config = get_component_config()
        telos_port = config.telos.port if hasattr(config, 'telos') else int(os.environ.get("TELOS_PORT"))
        endpoint = f"http://localhost:{telos_port}/api"
    
    # Create a helper and use it to register
    helper = HermesHelper()
    return await helper.register_service(
        service_id=service_id,
        name=name,
        version=version,
        capabilities=capabilities,
        endpoint=endpoint,
        metadata=metadata or {}
    )