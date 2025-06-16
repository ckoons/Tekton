"""
Hermes integration helper for Metis

This module provides utilities for integrating with Hermes,
the service registry and messaging system for Tekton.
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from metis.config import config


class HermesClient:
    """
    Client for interacting with the Hermes service registry.
    
    This class provides methods for registering with Hermes,
    discovering other services, and sending/receiving messages.
    """
    
    def __init__(self, service_name: str = "Metis"):
        """
        Initialize the Hermes client.
        
        Args:
            service_name: Name of this service
        """
        self.service_name = service_name
        self.hermes_url = config["HERMES_URL"]
        self.port = config["METIS_PORT"]
        self.host = "localhost"  # Default to localhost
        self.service_id = None  # Assigned by Hermes on registration
        self.registered = False
        self.capabilities = []
        self.last_heartbeat = None
        self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session for HTTP requests."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def register(self) -> bool:
        """
        Register the service with Hermes.
        
        Returns:
            bool: True if registration succeeded, False otherwise
        """
        try:
            session = await self._get_session()
            
            # Define service capabilities
            self.capabilities = [
                "task_management",
                "dependency_management",
                "task_tracking",
                "websocket_updates"
            ]
            
            # Create registration payload
            payload = {
                "name": self.service_name,
                "host": self.host,
                "port": self.port,
                "protocol": "http",
                "health_endpoint": "/health",
                "capabilities": self.capabilities,
                "metadata": {
                    "version": config["SERVICE_VERSION"],
                    "description": config["SERVICE_DESCRIPTION"]
                }
            }
            
            # Send registration request
            async with session.post(
                f"{self.hermes_url}/api/v1/registry/services",
                json=payload
            ) as response:
                if response.status == 200 or response.status == 201:
                    data = await response.json()
                    self.service_id = data.get("service_id")
                    self.registered = True
                    self.last_heartbeat = datetime.now()
                    print(f"Registered with Hermes as {self.service_name} (ID: {self.service_id})")
                    return True
                else:
                    print(f"Failed to register with Hermes: {response.status}")
                    return False
        
        except Exception as e:
            print(f"Error registering with Hermes: {e}")
            return False
    
    async def deregister(self) -> bool:
        """
        Deregister the service from Hermes.
        
        Returns:
            bool: True if deregistration succeeded, False otherwise
        """
        if not self.service_id:
            print("Not registered with Hermes")
            return False
        
        try:
            session = await self._get_session()
            
            # Send deregistration request
            async with session.delete(
                f"{self.hermes_url}/api/v1/registry/services/{self.service_id}"
            ) as response:
                if response.status == 200 or response.status == 204:
                    self.service_id = None
                    self.registered = False
                    print(f"Deregistered {self.service_name} from Hermes")
                    return True
                else:
                    print(f"Failed to deregister from Hermes: {response.status}")
                    return False
        
        except Exception as e:
            print(f"Error deregistering from Hermes: {e}")
            return False
    
    async def send_heartbeat(self) -> bool:
        """
        Send a heartbeat to Hermes to indicate the service is still alive.
        
        Returns:
            bool: True if heartbeat succeeded, False otherwise
        """
        if not self.service_id:
            print("Not registered with Hermes")
            return False
        
        try:
            session = await self._get_session()
            
            # Send heartbeat request
            async with session.put(
                f"{self.hermes_url}/api/v1/registry/services/{self.service_id}/heartbeat"
            ) as response:
                if response.status == 200:
                    self.last_heartbeat = datetime.now()
                    return True
                else:
                    print(f"Failed to send heartbeat to Hermes: {response.status}")
                    return False
        
        except Exception as e:
            print(f"Error sending heartbeat to Hermes: {e}")
            return False
    
    async def get_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific service from Hermes.
        
        Args:
            service_name: Name of the service to get
            
        Returns:
            Optional[Dict[str, Any]]: Service information if found, None otherwise
        """
        try:
            session = await self._get_session()
            
            # Get service information
            async with session.get(
                f"{self.hermes_url}/api/v1/registry/services",
                params={"name": service_name}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    for service in data.get("services", []):
                        if service.get("name") == service_name:
                            return service
                    return None
                else:
                    print(f"Failed to get service {service_name}: {response.status}")
                    return None
        
        except Exception as e:
            print(f"Error getting service {service_name}: {e}")
            return None
    
    async def discover_services(self, capability: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover services registered with Hermes.
        
        Args:
            capability: Optional capability to filter services
            
        Returns:
            List[Dict[str, Any]]: List of service information
        """
        try:
            session = await self._get_session()
            
            # Set request parameters
            params = {}
            if capability:
                params["capability"] = capability
            
            # Discover services
            async with session.get(
                f"{self.hermes_url}/api/v1/registry/services",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("services", [])
                else:
                    print(f"Failed to discover services: {response.status}")
                    return []
        
        except Exception as e:
            print(f"Error discovering services: {e}")
            return []
    
    async def get_service_url(self, service_name: str) -> Optional[str]:
        """
        Get the base URL for a service by name.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Optional[str]: Service URL if found, None otherwise
        """
        service = await self.get_service(service_name)
        if service:
            protocol = service.get("protocol", "http")
            host = service.get("host", "localhost")
            port = service.get("port")
            if host and port:
                return f"{protocol}://{host}:{port}"
        return None
    
    async def heartbeat_task(self) -> None:
        """
        Background task to send periodic heartbeats to Hermes.
        
        This method should be run as a background task to maintain
        registration with Hermes.
        """
        while True:
            # Send heartbeat if registered
            if self.registered:
                await self.send_heartbeat()
            
            # Wait for next heartbeat
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None


# Global Hermes client instance
hermes_client = HermesClient()