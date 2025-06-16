#!/usr/bin/env python3
"""
Component Integration Adapters - Adapters for specific Tekton components.

This module provides concrete adapters for interacting with specific
components in the Tekton ecosystem.
"""

import asyncio
import importlib
import logging
import os
import time
from typing import Dict, List, Any, Optional, Union, Callable

from synthesis.core.integration_base import ComponentAdapter, HermesAdapter

# Configure logging
logger = logging.getLogger("synthesis.core.integration_adapters")


class PrometheusAdapter(ComponentAdapter):
    """
    Adapter for interacting with the Prometheus planning component.
    
    This adapter allows Synthesis to request and update plans from Prometheus.
    """
    
    def __init__(self, 
                hermes_adapter: Optional[HermesAdapter] = None,
                direct_import: bool = False):
        """
        Initialize the Prometheus adapter.
        
        Args:
            hermes_adapter: Optional HermesAdapter for service discovery
            direct_import: Whether to directly import Prometheus modules
        """
        super().__init__("prometheus")
        self.hermes_adapter = hermes_adapter
        self.direct_import = direct_import
        self.prometheus_engine = None
        self.service_id = None
        
        # Define capabilities
        self.capabilities = {
            "create_plan": {
                "name": "create_plan",
                "description": "Create a plan for an objective",
                "parameters": {
                    "objective": "string",
                    "context": "object (optional)"
                }
            },
            "refine_plan": {
                "name": "refine_plan",
                "description": "Refine an existing plan",
                "parameters": {
                    "plan_id": "string",
                    "feedback": "string"
                }
            }
        }
        
    async def initialize(self) -> bool:
        """
        Initialize the Prometheus adapter.
        
        Returns:
            True if initialization was successful
        """
        # Try direct import if enabled
        if self.direct_import:
            try:
                # Import Prometheus engine
                from prometheus.core.planning_engine import PlanningEngine
                
                # Create engine instance
                self.prometheus_engine = PlanningEngine()
                
                # Initialize engine
                self.initialized = True
                logger.info("Prometheus adapter initialized via direct import")
                return True
                
            except ImportError:
                logger.warning("Failed to import Prometheus directly, falling back to Hermes")
                self.direct_import = False
                
        # Fall back to Hermes adapter
        if self.hermes_adapter:
            try:
                # Initialize Hermes adapter if needed
                if not self.hermes_adapter.initialized:
                    await self.hermes_adapter.initialize()
                    
                # Find Prometheus service
                service = await self.hermes_adapter.find_service_by_component("prometheus")
                if service:
                    self.service_id = service.get("service_id")
                    self.initialized = True
                    logger.info(f"Prometheus adapter initialized via Hermes (service_id: {self.service_id})")
                    return True
                else:
                    logger.error("Prometheus service not found in Hermes registry")
                    return False
                    
            except Exception as e:
                logger.error(f"Error initializing Prometheus adapter via Hermes: {e}")
                return False
                
        logger.error("No method available to initialize Prometheus adapter")
        return False
        
    async def invoke_capability(self, 
                           capability_name: str, 
                           parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Invoke a capability on Prometheus.
        
        Args:
            capability_name: Name of the capability to invoke
            parameters: Parameters for the capability
            
        Returns:
            Result of the capability invocation
        """
        if not self.initialized:
            raise RuntimeError("Prometheus adapter not initialized")
            
        if capability_name not in self.capabilities:
            raise ValueError(f"Capability {capability_name} not supported by Prometheus")
            
        # Use direct import if available
        if self.direct_import and self.prometheus_engine:
            try:
                if capability_name == "create_plan":
                    objective = parameters.get("objective")
                    context = parameters.get("context", {})
                    
                    if not objective:
                        return {
                            "success": False,
                            "error": "No objective specified"
                        }
                        
                    plan = await self.prometheus_engine.create_plan(objective, context)
                    return {
                        "success": True,
                        "plan": plan
                    }
                    
                elif capability_name == "refine_plan":
                    plan_id = parameters.get("plan_id")
                    feedback = parameters.get("feedback")
                    
                    if not plan_id or not feedback:
                        return {
                            "success": False,
                            "error": "Plan ID and feedback required"
                        }
                        
                    refined_plan = await self.prometheus_engine.refine_plan(plan_id, feedback)
                    return {
                        "success": True,
                        "plan": refined_plan
                    }
                    
            except Exception as e:
                logger.error(f"Error invoking Prometheus capability {capability_name}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
                
        # Fall back to Hermes
        if self.hermes_adapter and self.service_id:
            try:
                result = await self.hermes_adapter.invoke_service(
                    self.service_id,
                    capability_name,
                    parameters
                )
                return result
                
            except Exception as e:
                logger.error(f"Error invoking Prometheus capability {capability_name} via Hermes: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
                
        return {
            "success": False,
            "error": "No method available to invoke Prometheus capability"
        }


class AthenaAdapter(ComponentAdapter):
    """
    Adapter for interacting with the Athena knowledge graph component.
    
    This adapter allows Synthesis to query and update knowledge in Athena.
    """
    
    def __init__(self, 
                hermes_adapter: Optional[HermesAdapter] = None,
                direct_import: bool = False):
        """
        Initialize the Athena adapter.
        
        Args:
            hermes_adapter: Optional HermesAdapter for service discovery
            direct_import: Whether to directly import Athena modules
        """
        super().__init__("athena")
        self.hermes_adapter = hermes_adapter
        self.direct_import = direct_import
        self.athena_engine = None
        self.service_id = None
        
        # Define capabilities
        self.capabilities = {
            "create_entity": {
                "name": "create_entity",
                "description": "Create a knowledge entity",
                "parameters": {
                    "type": "string",
                    "properties": "object"
                }
            },
            "create_relationship": {
                "name": "create_relationship",
                "description": "Create a relationship between entities",
                "parameters": {
                    "source_id": "string",
                    "target_id": "string",
                    "type": "string",
                    "properties": "object (optional)"
                }
            },
            "query_knowledge": {
                "name": "query_knowledge",
                "description": "Query the knowledge graph",
                "parameters": {
                    "query": "string",
                    "parameters": "object (optional)"
                }
            }
        }
        
    async def initialize(self) -> bool:
        """
        Initialize the Athena adapter.
        
        Returns:
            True if initialization was successful
        """
        # Try direct import if enabled
        if self.direct_import:
            try:
                # Import Athena engine
                from athena.core.engine import KnowledgeEngine
                
                # Create engine instance
                self.athena_engine = KnowledgeEngine()
                
                # Initialize engine
                await self.athena_engine.initialize()
                
                self.initialized = True
                logger.info("Athena adapter initialized via direct import")
                return True
                
            except ImportError:
                logger.warning("Failed to import Athena directly, falling back to Hermes")
                self.direct_import = False
                
        # Fall back to Hermes adapter
        if self.hermes_adapter:
            try:
                # Initialize Hermes adapter if needed
                if not self.hermes_adapter.initialized:
                    await self.hermes_adapter.initialize()
                    
                # Find Athena service
                service = await self.hermes_adapter.find_service_by_component("athena")
                if service:
                    self.service_id = service.get("service_id")
                    self.initialized = True
                    logger.info(f"Athena adapter initialized via Hermes (service_id: {self.service_id})")
                    return True
                else:
                    logger.error("Athena service not found in Hermes registry")
                    return False
                    
            except Exception as e:
                logger.error(f"Error initializing Athena adapter via Hermes: {e}")
                return False
                
        logger.error("No method available to initialize Athena adapter")
        return False
        
    async def invoke_capability(self, 
                           capability_name: str, 
                           parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Invoke a capability on Athena.
        
        Args:
            capability_name: Name of the capability to invoke
            parameters: Parameters for the capability
            
        Returns:
            Result of the capability invocation
        """
        if not self.initialized:
            raise RuntimeError("Athena adapter not initialized")
            
        if capability_name not in self.capabilities:
            raise ValueError(f"Capability {capability_name} not supported by Athena")
            
        # Use direct import if available
        if self.direct_import and self.athena_engine:
            try:
                if capability_name == "create_entity":
                    entity_type = parameters.get("type")
                    properties = parameters.get("properties", {})
                    
                    if not entity_type:
                        return {
                            "success": False,
                            "error": "Entity type required"
                        }
                        
                    entity = await self.athena_engine.create_entity(entity_type, properties)
                    return {
                        "success": True,
                        "entity": entity
                    }
                    
                elif capability_name == "create_relationship":
                    source_id = parameters.get("source_id")
                    target_id = parameters.get("target_id")
                    rel_type = parameters.get("type")
                    properties = parameters.get("properties", {})
                    
                    if not source_id or not target_id or not rel_type:
                        return {
                            "success": False,
                            "error": "Source ID, target ID, and relationship type required"
                        }
                        
                    relationship = await self.athena_engine.create_relationship(
                        source_id, target_id, rel_type, properties
                    )
                    return {
                        "success": True,
                        "relationship": relationship
                    }
                    
                elif capability_name == "query_knowledge":
                    query = parameters.get("query")
                    query_params = parameters.get("parameters", {})
                    
                    if not query:
                        return {
                            "success": False,
                            "error": "Query required"
                        }
                        
                    results = await self.athena_engine.query(query, query_params)
                    return {
                        "success": True,
                        "results": results
                    }
                    
            except Exception as e:
                logger.error(f"Error invoking Athena capability {capability_name}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
                
        # Fall back to Hermes
        if self.hermes_adapter and self.service_id:
            try:
                result = await self.hermes_adapter.invoke_service(
                    self.service_id,
                    capability_name,
                    parameters
                )
                return result
                
            except Exception as e:
                logger.error(f"Error invoking Athena capability {capability_name} via Hermes: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
                
        return {
            "success": False,
            "error": "No method available to invoke Athena capability"
        }