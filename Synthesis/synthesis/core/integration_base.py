#!/usr/bin/env python3
"""
Component Integration Base - Base classes for component integration.

This module provides the base classes and interfaces for integrating
with other Tekton components.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logging
logger = logging.getLogger("synthesis.core.integration_base")


class ComponentAdapter:
    """
    Base class for component adapters.
    
    Component adapters provide a standardized interface for interacting
    with other Tekton components.
    """
    
    def __init__(self, component_name: str):
        """
        Initialize the component adapter.
        
        Args:
            component_name: Name of the component
        """
        self.component_name = component_name
        self.initialized = False
        self.capabilities = {}
    
    async def initialize(self) -> bool:
        """
        Initialize the component adapter.
        
        Returns:
            True if initialization was successful
        """
        self.initialized = True
        return True
        
    async def shutdown(self) -> bool:
        """
        Shutdown the component adapter.
        
        Returns:
            True if shutdown was successful
        """
        self.initialized = False
        return True
        
    async def ping(self) -> bool:
        """
        Check if the component is available.
        
        Returns:
            True if the component is available
        """
        return self.initialized
        
    async def invoke_capability(self, 
                           capability_name: str, 
                           parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Invoke a capability on the component.
        
        Args:
            capability_name: Name of the capability to invoke
            parameters: Parameters for the capability
            
        Returns:
            Result of the capability invocation
        """
        if not self.initialized:
            raise RuntimeError(f"Component {self.component_name} not initialized")
            
        if capability_name not in self.capabilities:
            raise ValueError(f"Capability {capability_name} not supported by {self.component_name}")
            
        raise NotImplementedError("invoke_capability must be implemented by subclasses")
        
    async def get_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the component's capabilities.
        
        Returns:
            List of capability dictionaries
        """
        if not self.initialized:
            raise RuntimeError(f"Component {self.component_name} not initialized")
            
        return list(self.capabilities.values())
        
    def has_capability(self, capability_name: str) -> bool:
        """
        Check if the component has a specific capability.
        
        Args:
            capability_name: Name of the capability
            
        Returns:
            True if the component has the capability
        """
        return capability_name in self.capabilities
        
    @property
    def component_status(self) -> str:
        """
        Get the component status.
        
        Returns:
            Status string ('initialized', 'uninitialized')
        """
        return "initialized" if self.initialized else "uninitialized"


class HermesAdapter(ComponentAdapter):
    """
    Adapter for interacting with Hermes services.
    
    This adapter uses the Hermes API to discover and interact with
    services registered with Hermes.
    """
    
    def __init__(self, hermes_url: Optional[str] = None):
        """
        Initialize the Hermes adapter.
        
        Args:
            hermes_url: URL of the Hermes API
        """
        super().__init__("hermes")
        import os
        self.hermes_url = hermes_url or os.environ.get("HERMES_URL", "http://localhost:5000/api")
        self.service_registry = {}
        self.session = None
        
    async def initialize(self) -> bool:
        """
        Initialize the Hermes adapter.
        
        Returns:
            True if initialization was successful
        """
        try:
            import aiohttp
            
            # Create HTTP session
            self.session = aiohttp.ClientSession()
            
            # Check if Hermes is available
            async with self.session.get(f"{self.hermes_url}/health") as response:
                if response.status == 200:
                    self.initialized = True
                    logger.info("Hermes adapter initialized successfully")
                    
                    # Discover services
                    await self.discover_services()
                    
                    return True
                else:
                    logger.error(f"Failed to connect to Hermes: {response.status}")
                    return False
        
        except ImportError:
            logger.error("aiohttp module not available for Hermes communication")
            return False
        except Exception as e:
            logger.error(f"Error initializing Hermes adapter: {e}")
            return False
            
    async def shutdown(self) -> bool:
        """
        Shutdown the Hermes adapter.
        
        Returns:
            True if shutdown was successful
        """
        try:
            if self.session:
                await self.session.close()
                self.session = None
                
            self.initialized = False
            logger.info("Hermes adapter shut down successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down Hermes adapter: {e}")
            return False
            
    async def discover_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover services registered with Hermes.
        
        Returns:
            Dictionary mapping service IDs to service information
        """
        if not self.initialized or not self.session:
            raise RuntimeError("Hermes adapter not initialized")
            
        try:
            # Query Hermes for all services
            async with self.session.get(f"{self.hermes_url}/registration/services") as response:
                if response.status == 200:
                    self.service_registry = await response.json()
                    logger.info(f"Discovered {len(self.service_registry)} services")
                    return self.service_registry
                else:
                    error = await response.text()
                    logger.error(f"Error discovering services: {error}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error discovering services: {e}")
            return {}
            
    async def find_service_by_component(self, component_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a service by component name.
        
        Args:
            component_name: Component name to search for
            
        Returns:
            Service information or None if not found
        """
        # Ensure registry is up to date
        if not self.service_registry:
            await self.discover_services()
            
        # Search for services with matching component name
        for service_id, service_info in self.service_registry.items():
            metadata = service_info.get("metadata", {})
            if metadata.get("component") == component_name or service_info.get("name", "").lower() == component_name.lower():
                return service_info
                
        return None
        
    async def invoke_service(self, 
                         service_id: str, 
                         capability: str, 
                         parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Invoke a capability on a service.
        
        Args:
            service_id: ID of the service
            capability: Name of the capability
            parameters: Parameters for the capability
            
        Returns:
            Result of the capability invocation
        """
        if not self.initialized or not self.session:
            raise RuntimeError("Hermes adapter not initialized")
            
        # Get service information
        service_info = self.service_registry.get(service_id)
        if not service_info:
            # Try to discover services again
            await self.discover_services()
            service_info = self.service_registry.get(service_id)
            
        if not service_info:
            raise ValueError(f"Service {service_id} not found")
            
        # Get endpoint
        endpoint = service_info.get("endpoint")
        if not endpoint:
            raise ValueError(f"Service {service_id} has no endpoint")
            
        try:
            # Prepare invocation data
            data = {
                "capability": capability,
                "parameters": parameters or {}
            }
            
            # Invoke the capability
            async with self.session.post(f"{endpoint}/invoke", json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    logger.error(f"Error invoking capability {capability} on {service_id}: {error}")
                    return {
                        "success": False,
                        "error": error
                    }
                    
        except Exception as e:
            logger.error(f"Error invoking capability {capability} on {service_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }