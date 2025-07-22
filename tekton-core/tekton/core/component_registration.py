#!/usr/bin/env python3
"""
Component Registration - Standardized component registration with Hermes.

This module provides utilities for components to register with Hermes.
"""

import asyncio
import json
import logging
import os
import socket
import time
from typing import Dict, List, Any, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)


class ComponentRegistration:
    """
    Handles component registration with Hermes.
    
    This class provides a standardized way for components to register their
    services with Hermes.
    """
    
    def __init__(self,
                component_id: str,
                component_name: str,
                hermes_url: Optional[str] = None,
                version: str = "0.1.0",
                capabilities: Optional[List[Dict[str, Any]]] = None,
                metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize component registration.
        
        Args:
            component_id: Unique identifier for the component
            component_name: Human-readable name
            hermes_url: URL of the Hermes API
            version: Component version
            capabilities: List of component capabilities
            metadata: Additional metadata about the component
        """
        self.component_id = component_id
        self.component_name = component_name
        from shared.urls import hermes_url as get_hermes_url
        self.hermes_url = hermes_url or get_hermes_url("/api")
        self.version = version
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        
        # Add hostname to metadata
        if "hostname" not in self.metadata:
            self.metadata["hostname"] = socket.gethostname()
            
        # Add component as metadata
        if "component" not in self.metadata:
            self.metadata["component"] = component_id
            
        # Internal state
        self._registered = False
        self._registration_token = None
        
    async def register(self) -> bool:
        """
        Register the component with Hermes.
        
        Returns:
            True if registration was successful
        """
        try:
            import aiohttp
            
            # Prepare registration data
            data = {
                "service_id": self.component_id,
                "name": self.component_name,
                "version": self.version,
                "capabilities": self.capabilities,
                "metadata": self.metadata
            }
            
            # If we have an endpoint, include it
            if "endpoint" in self.metadata:
                data["endpoint"] = self.metadata["endpoint"]
                
            # Register with Hermes
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/registration/register",
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self._registration_token = result.get("token")
                        self._registered = True
                        logger.info(f"Successfully registered {self.component_id} with Hermes")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Failed to register {self.component_id}: {error}")
                        return False
                        
        except ImportError:
            logger.error("aiohttp module not available for Hermes registration")
            return False
        except Exception as e:
            logger.error(f"Error registering {self.component_id}: {e}")
            return False
            
    async def unregister(self) -> bool:
        """
        Unregister the component from Hermes.
        
        Returns:
            True if unregistration was successful
        """
        if not self._registered:
            logger.info(f"Component {self.component_id} not registered, nothing to unregister")
            return True
            
        try:
            import aiohttp
            
            # Prepare unregistration data
            data = {
                "service_id": self.component_id,
                "token": self._registration_token
            }
            
            # Unregister from Hermes
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/registration/unregister",
                    json=data
                ) as response:
                    if response.status == 200:
                        self._registered = False
                        self._registration_token = None
                        logger.info(f"Successfully unregistered {self.component_id} from Hermes")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Failed to unregister {self.component_id}: {error}")
                        return False
                        
        except ImportError:
            logger.error("aiohttp module not available for Hermes unregistration")
            return False
        except Exception as e:
            logger.error(f"Error unregistering {self.component_id}: {e}")
            return False
            
    async def send_heartbeat(self) -> bool:
        """
        Send a heartbeat to Hermes to indicate the component is still alive.
        
        Returns:
            True if heartbeat was successful
        """
        if not self._registered:
            logger.debug(f"Component {self.component_id} not registered, can't send heartbeat")
            return False
            
        try:
            import aiohttp
            
            # Prepare heartbeat data
            data = {
                "component": self.component_id,
                "status": "active",
                "timestamp": time.time()
            }
            
            # Send heartbeat to Hermes
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/registration/heartbeat",
                    json=data
                ) as response:
                    if response.status == 200:
                        logger.debug(f"Sent heartbeat for {self.component_id}")
                        return True
                    else:
                        error = await response.text()
                        logger.warning(f"Failed to send heartbeat for {self.component_id}: {error}")
                        return False
                        
        except ImportError:
            logger.error("aiohttp module not available for Hermes heartbeat")
            return False
        except Exception as e:
            logger.warning(f"Error sending heartbeat for {self.component_id}: {e}")
            return False
            
    async def check_registration(self) -> bool:
        """
        Check if the component is still registered with Hermes.
        
        Returns:
            True if the component is registered
        """
        try:
            import aiohttp
            
            # Query Hermes for registration status
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.hermes_url}/registration/service/{self.component_id}"
                ) as response:
                    if response.status == 200:
                        # The service is registered
                        logger.debug(f"Component {self.component_id} is registered with Hermes")
                        return True
                    elif response.status == 404:
                        # The service is not registered
                        logger.warning(f"Component {self.component_id} is not registered with Hermes")
                        self._registered = False
                        return False
                    else:
                        error = await response.text()
                        logger.warning(f"Error checking registration for {self.component_id}: {error}")
                        return False
                        
        except ImportError:
            logger.error("aiohttp module not available for Hermes registration check")
            return False
        except Exception as e:
            logger.warning(f"Error checking registration for {self.component_id}: {e}")
            return False
            
    @property
    def is_registered(self) -> bool:
        """
        Check if the component is registered.
        
        Returns:
            True if the component is registered
        """
        return self._registered
        
    async def update_capabilities(self, capabilities: List[Dict[str, Any]]) -> bool:
        """
        Update the component's capabilities with Hermes.
        
        Args:
            capabilities: New list of capabilities
            
        Returns:
            True if update was successful
        """
        if not self._registered:
            logger.warning(f"Component {self.component_id} not registered, can't update capabilities")
            return False
            
        try:
            import aiohttp
            
            # Update local capabilities
            self.capabilities = capabilities
            
            # Prepare update data
            data = {
                "service_id": self.component_id,
                "capabilities": capabilities,
                "token": self._registration_token
            }
            
            # Update capabilities with Hermes
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/registration/update",
                    json=data
                ) as response:
                    if response.status == 200:
                        logger.info(f"Updated capabilities for {self.component_id}")
                        return True
                    else:
                        error = await response.text()
                        logger.warning(f"Failed to update capabilities for {self.component_id}: {error}")
                        return False
                        
        except ImportError:
            logger.error("aiohttp module not available for Hermes capability update")
            return False
        except Exception as e:
            logger.warning(f"Error updating capabilities for {self.component_id}: {e}")
            return False
            
    async def update_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Update the component's metadata with Hermes.
        
        Args:
            metadata: New metadata dictionary
            
        Returns:
            True if update was successful
        """
        if not self._registered:
            logger.warning(f"Component {self.component_id} not registered, can't update metadata")
            return False
            
        try:
            import aiohttp
            
            # Merge with existing metadata
            self.metadata = {**self.metadata, **metadata}
            
            # Prepare update data
            data = {
                "service_id": self.component_id,
                "metadata": self.metadata,
                "token": self._registration_token
            }
            
            # Update metadata with Hermes
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/registration/update",
                    json=data
                ) as response:
                    if response.status == 200:
                        logger.info(f"Updated metadata for {self.component_id}")
                        return True
                    else:
                        error = await response.text()
                        logger.warning(f"Failed to update metadata for {self.component_id}: {error}")
                        return False
                        
        except ImportError:
            logger.error("aiohttp module not available for Hermes metadata update")
            return False
        except Exception as e:
            logger.warning(f"Error updating metadata for {self.component_id}: {e}")
            return False