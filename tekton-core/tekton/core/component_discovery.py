#!/usr/bin/env python3
"""
Component Discovery - Standardized component discovery through Hermes.

This module provides utilities for discovering other components
registered with Hermes.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Set

# Configure logging
logger = logging.getLogger(__name__)


class ComponentDiscovery:
    """
    Handles component discovery through Hermes.
    
    This class provides a standardized way for components to discover
    other components and their capabilities through Hermes.
    """
    
    def __init__(self, hermes_url: Optional[str] = None):
        """
        Initialize component discovery.
        
        Args:
            hermes_url: URL of the Hermes API
        """
        import os
        from shared.urls import hermes_url as get_hermes_url
        self.hermes_url = hermes_url or get_hermes_url("/api")
        self._discovered_services: Dict[str, Dict[str, Any]] = {}
        self._capability_map: Dict[str, Set[str]] = {}
        
    async def discover_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all services registered with Hermes.
        
        Returns:
            Dictionary mapping service IDs to service information
        """
        try:
            import aiohttp
            
            # Query Hermes for all services
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.hermes_url}/registration/services"
                ) as response:
                    if response.status == 200:
                        self._discovered_services = await response.json()
                        # Build capability map
                        await self._build_capability_map()
                        logger.info(f"Discovered {len(self._discovered_services)} services")
                        return self._discovered_services
                    else:
                        error = await response.text()
                        logger.error(f"Error discovering services: {error}")
                        return {}
                        
        except ImportError:
            logger.error("aiohttp module not available for Hermes discovery")
            return {}
        except Exception as e:
            logger.error(f"Error discovering services: {e}")
            return {}
            
    async def _build_capability_map(self) -> None:
        """Build a map of capabilities to services."""
        self._capability_map = {}
        
        for service_id, service_info in self._discovered_services.items():
            for capability in service_info.get("capabilities", []):
                cap_name = capability.get("name")
                if cap_name:
                    if cap_name not in self._capability_map:
                        self._capability_map[cap_name] = set()
                    self._capability_map[cap_name].add(service_id)
                    
    async def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific service.
        
        Args:
            service_id: ID of the service to get
            
        Returns:
            Service information or None if not found
        """
        # Check if we have it cached
        if service_id in self._discovered_services:
            return self._discovered_services[service_id]
            
        try:
            import aiohttp
            
            # Query Hermes for the service
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.hermes_url}/registration/service/{service_id}"
                ) as response:
                    if response.status == 200:
                        service_info = await response.json()
                        self._discovered_services[service_id] = service_info
                        # Update capability map
                        await self._build_capability_map()
                        return service_info
                    elif response.status == 404:
                        logger.warning(f"Service {service_id} not found")
                        return None
                    else:
                        error = await response.text()
                        logger.error(f"Error getting service {service_id}: {error}")
                        return None
                        
        except ImportError:
            logger.error("aiohttp module not available for Hermes discovery")
            return None
        except Exception as e:
            logger.error(f"Error getting service {service_id}: {e}")
            return None
            
    async def find_services_by_capability(self, capability: str) -> List[str]:
        """
        Find services that provide a specific capability.
        
        Args:
            capability: Capability name to search for
            
        Returns:
            List of service IDs
        """
        # Check if we have services cached
        if not self._discovered_services:
            await self.discover_services()
            
        # Check capability map
        return list(self._capability_map.get(capability, set()))
        
    async def find_services_by_type(self, service_type: str) -> List[str]:
        """
        Find services of a specific type.
        
        Args:
            service_type: Type of service to find
            
        Returns:
            List of service IDs
        """
        # Check if we have services cached
        if not self._discovered_services:
            await self.discover_services()
            
        # Filter services by type
        return [
            service_id for service_id, service_info in self._discovered_services.items()
            if service_info.get("metadata", {}).get("type") == service_type
        ]
        
    async def find_tekton_components(self) -> Dict[str, Dict[str, Any]]:
        """
        Find all Tekton components registered with Hermes.
        
        Returns:
            Dictionary mapping component IDs to component information
        """
        # Check if we have services cached
        if not self._discovered_services:
            await self.discover_services()
            
        # Filter services to Tekton components
        return {
            service_id: service_info
            for service_id, service_info in self._discovered_services.items()
            if service_info.get("metadata", {}).get("tekton_component", False)
        }
        
    async def get_capability_info(self, service_id: str, capability: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific capability from a service.
        
        Args:
            service_id: ID of the service
            capability: Name of the capability
            
        Returns:
            Capability information or None if not found
        """
        # Get service information
        service_info = await self.get_service(service_id)
        if not service_info:
            return None
            
        # Find the capability
        for cap in service_info.get("capabilities", []):
            if cap.get("name") == capability:
                return cap
                
        return None
        
    async def invoke_capability(self, 
                             service_id: str, 
                             capability: str, 
                             parameters: Dict[str, Any] = None) -> Any:
        """
        Invoke a capability on a service.
        
        Args:
            service_id: ID of the service
            capability: Name of the capability
            parameters: Parameters for the capability
            
        Returns:
            Result of the capability invocation
        """
        try:
            import aiohttp
            
            # Get service information
            service_info = await self.get_service(service_id)
            if not service_info:
                logger.error(f"Service {service_id} not found")
                return None
                
            # Get endpoint
            endpoint = service_info.get("endpoint")
            if not endpoint:
                logger.error(f"Service {service_id} has no endpoint")
                return None
                
            # Prepare invocation data
            data = {
                "capability": capability,
                "parameters": parameters or {}
            }
            
            # Invoke the capability
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{endpoint}/invoke",
                    json=data
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error = await response.text()
                        logger.error(f"Error invoking capability {capability} on {service_id}: {error}")
                        return None
                        
        except ImportError:
            logger.error("aiohttp module not available for capability invocation")
            return None
        except Exception as e:
            logger.error(f"Error invoking capability {capability} on {service_id}: {e}")
            return None