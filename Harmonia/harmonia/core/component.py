"""
Component Registry and Integration - Manages external component connections.

This module provides functionality for registering, managing, and communicating
with external components used within workflows.
"""

import logging
import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union, Callable, Type, Protocol
from dataclasses import dataclass, field

from tekton.utils.tekton_http import HTTPClient
from tekton.utils.tekton_context import ContextManager
from tekton.utils.tekton_errors import ComponentNotFoundError, TektonNotFoundError

# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        state_checkpoint
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

# Define local error class since it's missing from tekton_errors
class ActionNotFoundError(TektonNotFoundError):
    """Raised when an action is not found for a component."""
    pass

# Configure logger
logger = logging.getLogger(__name__)


class ComponentAdapter(Protocol):
    """Protocol defining the interface for component adapters."""
    
    @property
    def component_name(self) -> str:
        """Get the component name."""
        ...
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action on the component.
        
        Args:
            action: Action to execute
            params: Parameters for the action
            
        Returns:
            Action result
        """
        ...

    async def get_actions(self) -> List[str]:
        """
        Get available actions for this component.
        
        Returns:
            List of available action names
        """
        ...

    async def get_action_schema(self, action: str) -> Optional[Dict[str, Any]]:
        """
        Get the schema for an action.
        
        Args:
            action: Action name
            
        Returns:
            Action schema if available
        """
        ...


@dataclass
class StandardComponentAdapter:
    """
    Standard adapter for communicating with external components.
    
    This adapter implements the ComponentAdapter protocol and provides
    a standard way to communicate with external components via HTTP.
    """
    
    component_name: str
    base_url: str
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    context_manager: Optional[ContextManager] = None
    http_client: Optional[HTTPClient] = None
    capabilities: Dict[str, Any] = field(default_factory=dict)
    action_schemas: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the HTTP client if not provided."""
        if not self.http_client:
            self.http_client = HTTPClient(
                base_url=self.base_url,
                timeout=self.timeout
            )
        
        if not self.context_manager:
            self.context_manager = ContextManager()
    
    async def initialize(self) -> None:
        """
        Initialize the adapter by fetching capabilities.
        
        This method should be called before using the adapter.
        """
        try:
            # Fetch component capabilities
            self.capabilities = await self._fetch_capabilities()
            
            # Fetch action schemas
            actions = await self.get_actions()
            for action in actions:
                schema = await self._fetch_action_schema(action)
                if schema:
                    self.action_schemas[action] = schema
            
            logger.info(f"Initialized adapter for component {self.component_name} with {len(actions)} actions")
        
        except Exception as e:
            logger.error(f"Error initializing adapter for {self.component_name}: {e}")
            raise
    
    async def _fetch_capabilities(self) -> Dict[str, Any]:
        """
        Fetch component capabilities from the component.
        
        Returns:
            Component capabilities
        """
        try:
            response = await self.http_client.get("/api/capabilities")
            return response
        except Exception as e:
            logger.warning(f"Failed to fetch capabilities for {self.component_name}: {e}")
            return {}
    
    async def _fetch_action_schema(self, action: str) -> Optional[Dict[str, Any]]:
        """
        Fetch schema for an action.
        
        Args:
            action: Action name
            
        Returns:
            Action schema if available
        """
        try:
            response = await self.http_client.get(f"/api/actions/{action}/schema")
            return response
        except Exception as e:
            logger.warning(f"Failed to fetch schema for action {action} on {self.component_name}: {e}")
            return None
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action on the component.
        
        Args:
            action: Action to execute
            params: Parameters for the action
            
        Returns:
            Action result
        
        Raises:
            ActionNotFoundError: If the action is not available
            ValueError: If the parameters are invalid
            Exception: For other execution errors
        """
        # Check if action exists
        if action not in await self.get_actions():
            raise ActionNotFoundError(f"Action {action} not found for component {self.component_name}")
        
        # Add context information to the request
        context_info = self.context_manager.get_context_info()
        request_data = {
            "action": action,
            "params": params,
            "context": context_info
        }
        
        # Execute with retry logic
        attempt = 0
        last_error = None
        while attempt < self.retry_count:
            try:
                # Send action request
                response = await self.http_client.post(
                    f"/api/actions/{action}",
                    data=request_data
                )
                
                # Log execution
                logger.debug(f"Executed action {action} on {self.component_name}: {response}")
                return response
            
            except Exception as e:
                last_error = e
                attempt += 1
                
                if attempt < self.retry_count:
                    # Exponential backoff with jitter
                    delay = self.retry_delay * (2 ** (attempt - 1))
                    jitter = 0.1 * delay * (2 * (time.time() % 1) - 1)
                    await asyncio.sleep(delay + jitter)
                    logger.warning(
                        f"Retrying action {action} on {self.component_name} "
                        f"({attempt}/{self.retry_count}): {e}"
                    )
                else:
                    logger.error(
                        f"Failed to execute action {action} on {self.component_name} "
                        f"after {attempt} attempts: {e}"
                    )
        
        # All retries failed
        raise last_error
    
    async def get_actions(self) -> List[str]:
        """
        Get available actions for this component.
        
        Returns:
            List of available action names
        """
        if not self.capabilities:
            await self.initialize()
        
        return self.capabilities.get("actions", [])
    
    async def get_action_schema(self, action: str) -> Optional[Dict[str, Any]]:
        """
        Get the schema for an action.
        
        Args:
            action: Action name
            
        Returns:
            Action schema if available
        """
        if action not in self.action_schemas:
            schema = await self._fetch_action_schema(action)
            if schema:
                self.action_schemas[action] = schema
        
        return self.action_schemas.get(action)


@architecture_decision(
    title="Component Registry Pattern",
    description="Central registry for managing connections to all Tekton components",
    rationale="Enables dynamic component discovery and flexible task routing",
    alternatives_considered=["Static configuration", "Service mesh", "Direct coupling"],
    impacts=["workflow_flexibility", "component_decoupling", "system_scalability"],
    decided_by="Casey",
    decision_date="2025-01-29"
)
@state_checkpoint(
    title="Component Registry State",
    description="Maintains registry of available components and their capabilities",
    state_type="registry",
    persistence=False,
    consistency_requirements="Eventually consistent with Hermes service discovery",
    recovery_strategy="Re-discover components from Hermes on restart"
)
class ComponentRegistry:
    """
    Registry for component adapters.
    
    This class manages adapters for external components, providing
    a central point for discovering and accessing component functionality.
    """
    
    def __init__(self):
        """Initialize the component registry."""
        self.components: Dict[str, ComponentAdapter] = {}
        self.discovery_sources: List[str] = []
        self.auto_discovery: bool = True
    
    def register_component(self, adapter: ComponentAdapter) -> None:
        """
        Register a component adapter.
        
        Args:
            adapter: Component adapter to register
        """
        component_name = adapter.component_name
        self.components[component_name] = adapter
        logger.info(f"Registered component {component_name}")
    
    def unregister_component(self, component_name: str) -> bool:
        """
        Unregister a component adapter.
        
        Args:
            component_name: Name of the component to unregister
            
        Returns:
            True if the component was unregistered
        """
        if component_name in self.components:
            del self.components[component_name]
            logger.info(f"Unregistered component {component_name}")
            return True
        
        logger.warning(f"Cannot unregister: Component {component_name} not found")
        return False
    
    def get_component(self, component_name: str) -> ComponentAdapter:
        """
        Get a component adapter by name.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Component adapter
            
        Raises:
            ComponentNotFoundError: If the component is not registered
        """
        if component_name not in self.components:
            raise ComponentNotFoundError(f"Component {component_name} not found")
        
        return self.components[component_name]
    
    def get_components(self) -> List[str]:
        """
        Get a list of registered component names.
        
        Returns:
            List of component names
        """
        return list(self.components.keys())
    
    def has_component(self, component_name: str) -> bool:
        """
        Check if a component is registered.
        
        Args:
            component_name: Name of the component
            
        Returns:
            True if the component is registered
        """
        return component_name in self.components
    
    async def discover_components(self, hermes_url: Optional[str] = None) -> List[str]:
        """
        Discover available components through Hermes.
        
        Args:
            hermes_url: URL of the Hermes service
            
        Returns:
            List of discovered component names
        """
        try:
            if not hermes_url:
                logger.warning("Cannot discover components: No Hermes URL provided")
                return []
            
            # Create HTTP client for Hermes
            client = HTTPClient(base_url=hermes_url)
            
            # Fetch component registry from Hermes
            response = await client.get("/api/components")
            
            # Add discovered components
            discovered = []
            for component_data in response.get("components", []):
                component_name = component_data.get("name")
                component_url = component_data.get("url")
                
                if component_name and component_url and not self.has_component(component_name):
                    # Create adapter for the component
                    adapter = StandardComponentAdapter(
                        component_name=component_name,
                        base_url=component_url
                    )
                    
                    # Initialize the adapter
                    await adapter.initialize()
                    
                    # Register the adapter
                    self.register_component(adapter)
                    discovered.append(component_name)
            
            logger.info(f"Discovered {len(discovered)} components: {', '.join(discovered)}")
            return discovered
        
        except Exception as e:
            logger.error(f"Error discovering components: {e}")
            return []
    
    async def initialize(self, hermes_url: Optional[str] = None) -> None:
        """
        Initialize the component registry.
        
        Args:
            hermes_url: URL of the Hermes service for component discovery
        """
        if hermes_url and self.auto_discovery:
            # Add Hermes as a discovery source
            if hermes_url not in self.discovery_sources:
                self.discovery_sources.append(hermes_url)
            
            # Discover components
            await self.discover_components(hermes_url)
    
    @integration_point(
        title="Component Action Execution",
        description="Routes workflow tasks to appropriate Tekton components",
        target_component="Any Tekton Component",
        protocol="HTTP REST API",
        data_flow="TaskDefinition → ComponentAdapter → Component API → Results",
        integration_date="2025-01-29"
    )
    async def execute_action(
        self,
        component_name: str,
        action: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an action on a component.
        
        Args:
            component_name: Name of the component
            action: Action to execute
            params: Parameters for the action
            
        Returns:
            Action result
            
        Raises:
            ComponentNotFoundError: If the component is not registered
            ActionNotFoundError: If the action is not available
        """
        component = self.get_component(component_name)
        return await component.execute_action(action, params)