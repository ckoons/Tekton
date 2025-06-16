"""
Registration Helper - Simplified integration with Unified Registration Protocol.

This module provides helper functions and utilities for Tekton components to
easily integrate with the Unified Registration Protocol.
"""

import os
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Callable

from hermes.api.client import HermesClient

# Configure logger
logger = logging.getLogger(__name__)


class ComponentRegistration:
    """
    Helper class for Tekton component registration.
    
    This class provides a simplified interface for Tekton components to
    register with the Tekton ecosystem using the Unified Registration Protocol.
    """
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                component_type: str,
                component_version: str,
                capabilities: List[str] = None,
                hermes_endpoint: Optional[str] = None):
        """
        Initialize the component registration.
        
        Args:
            component_id: Unique identifier for the component
            component_name: Human-readable name
            component_type: Type of component (e.g., "engram", "ergon", "athena")
            component_version: Component version
            capabilities: List of component capabilities
            hermes_endpoint: Optional Hermes endpoint (read from env if not provided)
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.component_version = component_version
        self.capabilities = capabilities or []
        
        # Get Hermes endpoint from environment if not provided
        self.hermes_endpoint = hermes_endpoint or os.environ.get(
            "TEKTON_HERMES_ENDPOINT", "localhost:5555"
        )
        
        # Initialize Hermes client
        self.client = HermesClient(
            component_id=component_id,
            component_name=component_name,
            component_type=component_type,
            component_version=component_version,
            hermes_endpoint=self.hermes_endpoint,
            capabilities=capabilities
        )
        
        logger.info(f"Component registration initialized for {component_id}")
    
    async def register(self) -> bool:
        """
        Register the component with the Tekton ecosystem.
        
        Returns:
            True if registration successful
        """
        return await self.client.register()
    
    async def unregister(self) -> bool:
        """
        Unregister the component from the Tekton ecosystem.
        
        Returns:
            True if unregistration successful
        """
        return await self.client.unregister()
    
    def publish_message(self,
                     topic: str,
                     message: Any,
                     headers: Optional[Dict[str, Any]] = None) -> bool:
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            message: Message to publish
            headers: Optional message headers
            
        Returns:
            True if publication successful
        """
        return self.client.publish_message(
            topic=topic,
            message=message,
            headers=headers
        )
    
    def subscribe_to_topic(self,
                       topic: str,
                       callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Subscribe to a topic.
        
        Args:
            topic: Topic to subscribe to
            callback: Function to call when a message is received
            
        Returns:
            True if subscription successful
        """
        return self.client.subscribe_to_topic(
            topic=topic,
            callback=callback
        )
    
    async def close(self) -> None:
        """
        Close the connection to Hermes services.
        """
        await self.client.close()


async def register_component(
    component_id: str,
    component_name: str,
    component_type: str,
    component_version: str,
    capabilities: List[str] = None,
    hermes_endpoint: Optional[str] = None
) -> ComponentRegistration:
    """
    Register a component with the Tekton ecosystem.
    
    This is a convenience function that creates a ComponentRegistration
    instance, registers the component, and returns the instance.
    
    Args:
        component_id: Unique identifier for the component
        component_name: Human-readable name
        component_type: Type of component (e.g., "engram", "ergon", "athena")
        component_version: Component version
        capabilities: List of component capabilities
        hermes_endpoint: Optional Hermes endpoint (read from env if not provided)
        
    Returns:
        ComponentRegistration instance
    """
    # Create component registration
    registration = ComponentRegistration(
        component_id=component_id,
        component_name=component_name,
        component_type=component_type,
        component_version=component_version,
        capabilities=capabilities,
        hermes_endpoint=hermes_endpoint
    )
    
    # Register component
    success = await registration.register()
    
    if not success:
        logger.error(f"Failed to register component {component_id}")
        await registration.close()
        return None
    
    return registration