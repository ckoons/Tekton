#!/usr/bin/env python3
"""
Component Integration - Handles integration with other Tekton components.

This module provides adapters and interfaces for Synthesis to interact with
other components of the Tekton ecosystem.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable

from synthesis.core.integration_base import ComponentAdapter, HermesAdapter
from synthesis.core.integration_adapters import PrometheusAdapter, AthenaAdapter

# Configure logging
logger = logging.getLogger("synthesis.core.integration")


class IntegrationManager:
    """
    Manages integrations with other Tekton components.
    
    This class discovers, initializes, and coordinates interactions with
    other components in the Tekton ecosystem.
    """
    
    def __init__(self, 
                hermes_url: Optional[str] = None,
                direct_import: bool = False):
        """
        Initialize the integration manager.
        
        Args:
            hermes_url: URL of the Hermes API
            direct_import: Whether to try direct imports
        """
        self.hermes_url = hermes_url
        self.direct_import = direct_import
        self.hermes_adapter = HermesAdapter(hermes_url)
        self.adapters: Dict[str, ComponentAdapter] = {}
        self.initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize the integration manager.
        
        Returns:
            True if initialization was successful
        """
        logger.info("Initializing integration manager")
        
        # Initialize Hermes adapter
        hermes_success = await self.hermes_adapter.initialize()
        
        # Initialize adapters based on what's available
        self.adapters = {
            "hermes": self.hermes_adapter,
            "prometheus": PrometheusAdapter(self.hermes_adapter, self.direct_import),
            "athena": AthenaAdapter(self.hermes_adapter, self.direct_import)
        }
        
        # Initialize all adapters
        initialization_results = {}
        for name, adapter in self.adapters.items():
            if name == "hermes" and not hermes_success:
                # Skip if Hermes failed to initialize
                initialization_results[name] = False
                continue
                
            try:
                result = await adapter.initialize()
                initialization_results[name] = result
                logger.info(f"Adapter {name} initialization: {'success' if result else 'failed'}")
            except Exception as e:
                logger.error(f"Error initializing adapter {name}: {e}")
                initialization_results[name] = False
                
        # Calculate overall success (at least Hermes must succeed)
        success = initialization_results.get("hermes", False)
        
        self.initialized = success
        logger.info(f"Integration manager initialization: {'success' if success else 'failed'}")
        return success
        
    async def shutdown(self) -> bool:
        """
        Shutdown the integration manager.
        
        Returns:
            True if shutdown was successful
        """
        logger.info("Shutting down integration manager")
        
        # Shutdown all adapters
        for name, adapter in self.adapters.items():
            try:
                await adapter.shutdown()
                logger.info(f"Adapter {name} shutdown successful")
            except Exception as e:
                logger.error(f"Error shutting down adapter {name}: {e}")
                
        self.initialized = False
        return True
        
    def get_adapter(self, component_name: str) -> Optional[ComponentAdapter]:
        """
        Get an adapter for a specific component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            ComponentAdapter instance or None if not found
        """
        return self.adapters.get(component_name.lower())
        
    async def invoke_capability(self, 
                            component_name: str, 
                            capability_name: str, 
                            parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Invoke a capability on a component.
        
        Args:
            component_name: Name of the component
            capability_name: Name of the capability
            parameters: Parameters for the capability
            
        Returns:
            Result of the capability invocation
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Integration manager not initialized"
            }
            
        # Get the adapter
        adapter = self.get_adapter(component_name)
        if not adapter:
            return {
                "success": False,
                "error": f"No adapter found for component {component_name}"
            }
            
        # Check if adapter is initialized
        if not adapter.initialized:
            try:
                # Try to initialize the adapter
                success = await adapter.initialize()
                if not success:
                    return {
                        "success": False,
                        "error": f"Failed to initialize adapter for {component_name}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error initializing adapter for {component_name}: {e}"
                }
                
        # Invoke the capability
        try:
            return await adapter.invoke_capability(capability_name, parameters)
        except Exception as e:
            return {
                "success": False,
                "error": f"Error invoking capability {capability_name} on {component_name}: {e}"
            }
            
    async def get_capabilities(self, component_name: str) -> List[Dict[str, Any]]:
        """
        Get a component's capabilities.
        
        Args:
            component_name: Name of the component
            
        Returns:
            List of capability dictionaries
        """
        if not self.initialized:
            return []
            
        # Get the adapter
        adapter = self.get_adapter(component_name)
        if not adapter or not adapter.initialized:
            return []
            
        try:
            return await adapter.get_capabilities()
        except Exception as e:
            logger.error(f"Error getting capabilities for {component_name}: {e}")
            return []
            
    async def get_all_capabilities(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get capabilities for all components.
        
        Returns:
            Dictionary mapping component names to capability lists
        """
        if not self.initialized:
            return {}
            
        capabilities = {}
        for name, adapter in self.adapters.items():
            if adapter.initialized:
                try:
                    capabilities[name] = await adapter.get_capabilities()
                except Exception as e:
                    logger.error(f"Error getting capabilities for {name}: {e}")
                    capabilities[name] = []
                    
        return capabilities
        
    async def discover_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover available services.
        
        Returns:
            Dictionary mapping service IDs to service information
        """
        if not self.initialized or "hermes" not in self.adapters:
            return {}
            
        hermes = self.adapters["hermes"]
        if not hermes.initialized:
            return {}
            
        try:
            return await hermes.discover_services()
        except Exception as e:
            logger.error(f"Error discovering services: {e}")
            return {}
            
    async def create_plan(self, objective: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a plan using Prometheus.
        
        Args:
            objective: Plan objective
            context: Optional planning context
            
        Returns:
            Result containing the created plan
        """
        return await self.invoke_capability(
            "prometheus",
            "create_plan",
            {
                "objective": objective,
                "context": context or {}
            }
        )
        
    async def refine_plan(self, plan_id: str, feedback: str) -> Dict[str, Any]:
        """
        Refine a plan using Prometheus.
        
        Args:
            plan_id: ID of the plan to refine
            feedback: Feedback for refinement
            
        Returns:
            Result containing the refined plan
        """
        return await self.invoke_capability(
            "prometheus",
            "refine_plan",
            {
                "plan_id": plan_id,
                "feedback": feedback
            }
        )
        
    async def create_entity(self, entity_type: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a knowledge entity in Athena.
        
        Args:
            entity_type: Type of entity
            properties: Entity properties
            
        Returns:
            Result containing the created entity
        """
        return await self.invoke_capability(
            "athena",
            "create_entity",
            {
                "type": entity_type,
                "properties": properties
            }
        )
        
    async def create_relationship(self, 
                            source_id: str, 
                            target_id: str, 
                            relationship_type: str,
                            properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a relationship in Athena.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relationship_type: Type of relationship
            properties: Optional relationship properties
            
        Returns:
            Result containing the created relationship
        """
        return await self.invoke_capability(
            "athena",
            "create_relationship",
            {
                "source_id": source_id,
                "target_id": target_id,
                "type": relationship_type,
                "properties": properties or {}
            }
        )
        
    async def query_knowledge(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query the knowledge graph in Athena.
        
        Args:
            query: Knowledge query
            parameters: Optional query parameters
            
        Returns:
            Query results
        """
        return await self.invoke_capability(
            "athena",
            "query_knowledge",
            {
                "query": query,
                "parameters": parameters or {}
            }
        )