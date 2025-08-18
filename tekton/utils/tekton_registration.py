"""
Tekton Registration Utility

This module provides standardized component registration with Hermes,
including capability declarations, heartbeat management, and dependency tracking.

Usage:
    from tekton.utils.tekton_registration import (
        TektonComponent,
        register_component,
        StandardCapabilities
    )
    
    # Using the class-based interface
    component = TektonComponent(
        component_id="mycomponent",
        component_name="My Component",
        component_type="service",
        version="1.0.0",
        capabilities=[
            StandardCapabilities.memory_storage(),
            StandardCapabilities.memory_query()
        ]
    )
    
    await component.register()
    # ... component runs ...
    await component.unregister()
    
    # Using the function-based interface
    registration_client = await register_component(
        "mycomponent",
        "My Component",
        "service",
        "1.0.0",
        capabilities=[StandardCapabilities.memory_storage()]
    )
"""

import os
import sys
import json
import asyncio
import logging
import signal
from enum import Enum
from typing import Dict, Any, Optional, List, Union, Callable, Set, TypeVar, Type
from datetime import datetime

# Import required utilities
from .tekton_http import HTTPClient, http_request
from .tekton_config import config_from_env, get_component_port
from .tekton_errors import (
    TektonError,
    ConnectionError,
    ServiceUnavailableError,
    ConfigurationError
)

try:
    from shared.urls import hermes_url as get_hermes_url
except ImportError:
    get_hermes_url = None

# Set up logger
logger = logging.getLogger(__name__)

# Hermes registration URL paths
REGISTER_PATH = "/api/registration/register"
UNREGISTER_PATH = "/api/registration/unregister"
HEARTBEAT_PATH = "/api/registration/heartbeat"
CAPABILITIES_PATH = "/api/registration/capabilities"


class ComponentStatus(Enum):
    """Component status values."""
    UNREGISTERED = "unregistered"
    INITIALIZING = "initializing"
    READY = "ready"
    DEGRADED = "degraded"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"


class StandardCapabilities:
    """
    Standard capability definitions for Tekton components.
    
    This class provides factory methods for common capabilities
    to ensure consistent declaration across components.
    """
    
    @staticmethod
    def memory_storage(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Memory storage capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "memory.storage",
            "name": "Memory Storage",
            "description": "Store data in memory system",
            "parameters": params or {
                "formats": ["text", "structured", "vector"],
                "persistence": True
            }
        }
        return capability
    
    @staticmethod
    def memory_query(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Memory query capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "memory.query",
            "name": "Memory Query",
            "description": "Query data from memory system",
            "parameters": params or {
                "query_types": ["exact", "semantic", "hybrid"],
                "filters": True
            }
        }
        return capability
    
    @staticmethod
    def llm_inference(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        LLM inference capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "llm.inference",
            "name": "LLM Inference",
            "description": "Run inference with language models",
            "parameters": params or {
                "models": ["default"],
                "streaming": True,
                "max_tokens": 4096
            }
        }
        return capability
    
    @staticmethod
    def llm_routing(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        LLM routing capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "llm.routing",
            "name": "LLM Routing",
            "description": "Route requests to appropriate language models",
            "parameters": params or {
                "routing_strategies": ["cost", "performance", "capability"],
                "fallback": True
            }
        }
        return capability
    
    @staticmethod
    def workflow_execution(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Workflow execution capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "workflow.execution",
            "name": "Workflow Execution",
            "description": "Execute defined workflows",
            "parameters": params or {
                "parallel": True,
                "monitoring": True,
                "max_steps": 100
            }
        }
        return capability
    
    @staticmethod
    def workflow_definition(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Workflow definition capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "workflow.definition",
            "name": "Workflow Definition",
            "description": "Define and manage workflows",
            "parameters": params or {
                "formats": ["json", "yaml"],
                "validation": True
            }
        }
        return capability
    
    @staticmethod
    def knowledge_graph(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Knowledge graph capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "knowledge.graph",
            "name": "Knowledge Graph",
            "description": "Store and query knowledge graph data",
            "parameters": params or {
                "entity_types": ["any"],
                "relationship_types": ["any"],
                "query_language": "cypher"
            }
        }
        return capability
    
    @staticmethod
    def knowledge_extraction(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Knowledge extraction capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "knowledge.extraction",
            "name": "Knowledge Extraction",
            "description": "Extract knowledge from unstructured data",
            "parameters": params or {
                "source_types": ["text", "documents"],
                "extraction_types": ["entities", "relationships", "concepts"]
            }
        }
        return capability
    
    @staticmethod
    def agent_execution(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Agent execution capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "agent.execution",
            "name": "Agent Execution",
            "description": "Execute agent actions",
            "parameters": params or {
                "tool_access": True,
                "monitoring": True,
                "sandboxed": True
            }
        }
        return capability
    
    @staticmethod
    def agent_definition(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Agent definition capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "agent.definition",
            "name": "Agent Definition",
            "description": "Define and manage agents",
            "parameters": params or {
                "formats": ["json", "yaml"],
                "validation": True
            }
        }
        return capability
    
    @staticmethod
    def planning(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Planning capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "planning",
            "name": "Planning",
            "description": "Create and manage plans",
            "parameters": params or {
                "hierarchical": True,
                "revision": True,
                "monitoring": True
            }
        }
        return capability
    
    @staticmethod
    def requirements_management(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Requirements management capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "requirements.management",
            "name": "Requirements Management",
            "description": "Manage project requirements",
            "parameters": params or {
                "tracing": True,
                "validation": True,
                "history": True
            }
        }
        return capability
    
    @staticmethod
    def terminal(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Terminal capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "terminal",
            "name": "Terminal",
            "description": "Interactive terminal sessions",
            "parameters": params or {
                "interactive": True,
                "history": True,
                "completion": True
            }
        }
        return capability
    
    @staticmethod
    def websocket(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        WebSocket capability.
        
        Args:
            params: Optional parameters for the capability
            
        Returns:
            Capability definition
        """
        capability = {
            "id": "websocket",
            "name": "WebSocket",
            "description": "Real-time WebSocket communication",
            "parameters": params or {
                "protocol": "json",
                "authentication": True
            }
        }
        return capability
    
    @staticmethod
    def custom(
        capability_id: str,
        name: str,
        description: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a custom capability.
        
        Args:
            capability_id: Capability identifier
            name: Human-readable name
            description: Capability description
            parameters: Optional parameters
            
        Returns:
            Capability definition
        """
        return {
            "id": capability_id,
            "name": name,
            "description": description,
            "parameters": parameters or {}
        }


class TektonComponent:
    """
    Base class for Tekton components with Hermes registration.
    
    This class provides a standardized interface for components to
    register with Hermes, maintain heartbeats, and manage their lifecycle.
    """
    
    def __init__(
        self,
        component_id: str,
        component_name: str,
        component_type: str,
        version: str,
        capabilities: Optional[List[Dict[str, Any]]] = None,
        endpoint: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        hermes_url: Optional[str] = None,
        description: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None,
        heartbeat_interval: int = 60,
        status: ComponentStatus = ComponentStatus.UNREGISTERED
    ):
        """
        Initialize a Tekton component.
        
        Args:
            component_id: Unique identifier (e.g., "athena")
            component_name: Human-readable name (e.g., "Athena Knowledge Graph")
            component_type: Type of component (e.g., "knowledge_graph")
            version: Component version (e.g., "1.0.0")
            capabilities: List of component capabilities
            endpoint: Component API endpoint for direct access
            dependencies: List of component IDs this component depends on
            hermes_url: Hermes API endpoint (from env var if not provided)
            description: Component description
            additional_metadata: Additional component metadata
            heartbeat_interval: Interval in seconds for sending heartbeats
            status: Initial component status
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.version = version
        self.capabilities = capabilities or []
        self.dependencies = dependencies or []
        self.heartbeat_interval = heartbeat_interval
        self.status = status
        
        # Set up endpoint if not provided
        if endpoint is None:
            try:
                # Get component port
                port = get_component_port(component_id)
                endpoint = f"http://localhost:{port}"
            except Exception as e:
                logger.warning(f"Failed to determine endpoint automatically: {e}")
                endpoint = None
        
        self.endpoint = endpoint
        
        # Process Hermes URL
        self.hermes_url = hermes_url or os.environ.get("HERMES_URL")
        if self.hermes_url is None:
            # Try standard port
            try:
                port = get_component_port("hermes")
                self.hermes_url = f"http://localhost:{port}"
            except Exception:
                if get_hermes_url:
                    self.hermes_url = get_hermes_url("")
                else:
                    self.hermes_url = "http://localhost:8001"
        
        # Make sure the URL points to the base and not a specific endpoint
        if self.hermes_url.endswith('/api'):
            # Remove /api
            self.hermes_url = self.hermes_url[:-4]
        elif not self.hermes_url.endswith('/'):
            # Add trailing slash
            self.hermes_url = f"{self.hermes_url}/"
        
        # Set up metadata
        self.metadata = {
            "description": description or f"{component_name} component",
            "version": version,
            "component_type": component_type,
            "dependencies": self.dependencies,
            "status": self.status.value
        }
        
        # Update with additional metadata if provided
        if additional_metadata:
            self.metadata.update(additional_metadata)
        
        # Runtime variables
        self._is_registered = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._http_client: Optional[HTTPClient] = None
    
    async def initialize_client(self) -> bool:
        """
        Initialize the HTTP client for Hermes communication.
        
        Returns:
            True if initialization was successful
        """
        if self._http_client is None:
            try:
                self._http_client = HTTPClient(
                    base_url=self.hermes_url,
                    component_id=self.component_id,
                    retries=3,
                    timeout=10
                )
                await self._http_client.initialize()
                return True
            except Exception as e:
                logger.error(f"Failed to initialize HTTP client: {e}")
                return False
        
        return True
    
    async def register(self) -> bool:
        """
        Register this component with Hermes.
        
        Returns:
            True if registration was successful
        """
        # Initialize client if needed
        if not await self.initialize_client():
            return False
        
        try:
            # Prepare registration data
            registration_data = {
                "component_id": self.component_id,
                "name": self.component_name,
                "type": self.component_type,
                "version": self.version,
                "capabilities": self.capabilities,
                "metadata": self.metadata
            }
            
            if self.endpoint:
                registration_data["endpoint"] = self.endpoint
            
            # Register with Hermes
            response = await self._http_client.post(
                REGISTER_PATH,
                json_data=registration_data
            )
            
            # Check response
            if isinstance(response, dict) and response.get("status") == "success":
                logger.info(f"Successfully registered {self.component_name} with Hermes")
                self._is_registered = True
                await self._start_heartbeat()
                return True
            else:
                logger.error(f"Failed to register with Hermes: {response}")
                return False
        
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            return False
    
    async def unregister(self) -> bool:
        """
        Unregister this component from Hermes.
        
        Returns:
            True if unregistration was successful
        """
        if not self._is_registered:
            logger.info(f"Component {self.component_id} is not registered")
            return True
        
        try:
            # Stop heartbeat first
            await self._stop_heartbeat()
            
            # Unregister from Hermes
            if self._http_client:
                response = await self._http_client.post(
                    UNREGISTER_PATH,
                    json_data={"component_id": self.component_id}
                )
                
                # Check response
                if isinstance(response, dict) and response.get("status") == "success":
                    logger.info(f"Successfully unregistered {self.component_name} from Hermes")
                    self._is_registered = False
                    return True
                else:
                    logger.error(f"Failed to unregister with Hermes: {response}")
                    return False
            
            return False
        
        except Exception as e:
            logger.error(f"Error during unregistration: {e}")
            return False
    
    async def update_status(self, status: ComponentStatus) -> bool:
        """
        Update the component's status in Hermes.
        
        Args:
            status: New component status
            
        Returns:
            True if status update was successful
        """
        if not self._is_registered:
            logger.info(f"Component {self.component_id} is not registered, can't update status")
            self.status = status
            return False
        
        try:
            # Update status in metadata
            self.status = status
            self.metadata["status"] = status.value
            
            # Send heartbeat with updated status
            if self._http_client:
                response = await self._http_client.post(
                    HEARTBEAT_PATH,
                    json_data={
                        "component_id": self.component_id,
                        "status": status.value,
                        "metadata": self.metadata
                    }
                )
                
                # Check response
                if isinstance(response, dict) and response.get("status") == "success":
                    logger.info(f"Successfully updated {self.component_name} status to {status.value}")
                    return True
                else:
                    logger.error(f"Failed to update status with Hermes: {response}")
                    return False
            
            return False
        
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return False
    
    async def update_capabilities(self, capabilities: List[Dict[str, Any]]) -> bool:
        """
        Update the component's capabilities in Hermes.
        
        Args:
            capabilities: New list of capabilities
            
        Returns:
            True if capability update was successful
        """
        if not self._is_registered:
            logger.info(f"Component {self.component_id} is not registered, can't update capabilities")
            self.capabilities = capabilities
            return False
        
        try:
            # Update capabilities
            self.capabilities = capabilities
            
            # Send update to Hermes
            if self._http_client:
                response = await self._http_client.post(
                    CAPABILITIES_PATH,
                    json_data={
                        "component_id": self.component_id,
                        "capabilities": capabilities
                    }
                )
                
                # Check response
                if isinstance(response, dict) and response.get("status") == "success":
                    logger.info(f"Successfully updated {self.component_name} capabilities")
                    return True
                else:
                    logger.error(f"Failed to update capabilities with Hermes: {response}")
                    return False
            
            return False
        
        except Exception as e:
            logger.error(f"Error updating capabilities: {e}")
            return False
    
    async def _heartbeat_loop(self) -> None:
        """Continuously send heartbeats to Hermes."""
        try:
            logger.info(
                f"Starting heartbeat for {self.component_id} (interval: {self.heartbeat_interval}s)"
            )
            
            while not self._shutdown_event.is_set():
                try:
                    # Send heartbeat to Hermes
                    if self._http_client:
                        await self._http_client.post(
                            HEARTBEAT_PATH,
                            json_data={
                                "component_id": self.component_id,
                                "status": self.status.value,
                                "metadata": self.metadata
                            }
                        )
                        logger.debug(f"Sent heartbeat for {self.component_id}")
                    
                    # Wait for the next interval or until shutdown
                    try:
                        await asyncio.wait_for(
                            self._shutdown_event.wait(),
                            timeout=self.heartbeat_interval
                        )
                    except asyncio.TimeoutError:
                        # This is expected - it just means the interval elapsed
                        pass
                
                except Exception as e:
                    logger.error(f"Error sending heartbeat: {e}")
                    # Wait a bit and try again
                    await asyncio.sleep(min(5, self.heartbeat_interval))
        
        except Exception as e:
            logger.error(f"Heartbeat loop failed: {e}")
    
    async def _start_heartbeat(self) -> None:
        """Start the heartbeat task."""
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._shutdown_event.clear()
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.debug("Heartbeat task started")
    
    async def _stop_heartbeat(self) -> None:
        """Stop the heartbeat task."""
        if self._heartbeat_task is not None and not self._heartbeat_task.done():
            self._shutdown_event.set()
            try:
                await asyncio.wait_for(self._heartbeat_task, timeout=5)
            except asyncio.TimeoutError:
                logger.warning("Heartbeat task did not stop cleanly, cancelling")
                self._heartbeat_task.cancel()
            logger.debug("Heartbeat task stopped")
    
    async def check_hermes_health(self) -> bool:
        """
        Check if Hermes is healthy.
        
        Returns:
            True if Hermes is healthy
        """
        try:
            # Check Hermes health endpoint
            if self._http_client:
                response = await self._http_client.get("/api/health")
                
                # Check response
                if isinstance(response, dict) and response.get("status") == "healthy":
                    return True
                else:
                    logger.warning(f"Hermes health check failed: {response}")
                    return False
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking Hermes health: {e}")
            return False
    
    async def check_dependency_health(self) -> Dict[str, bool]:
        """
        Check if dependencies are healthy.
        
        Returns:
            Dictionary mapping dependency IDs to their health status
        """
        results = {}
        
        for dependency in self.dependencies:
            try:
                # Query Hermes for dependency status
                if self._http_client:
                    response = await self._http_client.get(
                        f"/api/components/{dependency}"
                    )
                    
                    # Check response
                    if isinstance(response, dict) and response.get("status") not in (
                        "error", "shutdown", "unregistered"
                    ):
                        results[dependency] = True
                    else:
                        results[dependency] = False
            
            except Exception:
                results[dependency] = False
        
        return results
    
    async def close(self) -> None:
        """
        Clean up resources and unregister if necessary.
        
        Call this method when shutting down the component.
        """
        if self._is_registered:
            await self.unregister()
        
        # Clean up HTTP client
        if self._http_client:
            await self._http_client.close()
            self._http_client = None
    
    def setup_signal_handlers(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        """
        Set up signal handlers for graceful shutdown.
        
        Args:
            loop: Event loop to register handlers with (uses current loop if None)
        """
        def handle_signal(sig):
            logger.info(f"Received signal {sig}, initiating shutdown")
            asyncio.create_task(self.close())
        
        loop = loop or asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
    
    async def __aenter__(self) -> 'TektonComponent':
        """
        Async context manager entry.
        
        Returns:
            The component instance
        """
        await self.register()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Async context manager exit.
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        await self.close()


# Function-based interface for simplified usage

async def register_component(
    component_id: str,
    component_name: str,
    component_type: str,
    version: str,
    capabilities: Optional[List[Dict[str, Any]]] = None,
    endpoint: Optional[str] = None,
    dependencies: Optional[List[str]] = None,
    hermes_url: Optional[str] = None,
    description: Optional[str] = None,
    additional_metadata: Optional[Dict[str, Any]] = None,
    heartbeat_interval: int = 60
) -> Optional[TektonComponent]:
    """
    Register a component with Hermes.
    
    This is a convenience function that creates a TektonComponent,
    registers it, and returns it for lifecycle management.
    
    Args:
        component_id: Component identifier
        component_name: Human-readable name
        component_type: Component type
        version: Component version
        capabilities: Component capabilities
        endpoint: Component API endpoint
        dependencies: Component dependencies
        hermes_url: Hermes URL
        description: Component description
        additional_metadata: Additional metadata
        heartbeat_interval: Heartbeat interval in seconds
        
    Returns:
        Registered component if successful, None otherwise
    """
    component = TektonComponent(
        component_id=component_id,
        component_name=component_name,
        component_type=component_type,
        version=version,
        capabilities=capabilities,
        endpoint=endpoint,
        dependencies=dependencies,
        hermes_url=hermes_url,
        description=description,
        additional_metadata=additional_metadata,
        heartbeat_interval=heartbeat_interval
    )
    
    success = await component.register()
    if success:
        return component
    else:
        await component.close()
        return None


# Utility functions

def load_registration_file(file_path: str) -> Dict[str, Any]:
    """
    Load registration information from a JSON file.
    
    Args:
        file_path: Path to the registration file
        
    Returns:
        Registration data
        
    Raises:
        ConfigurationError: If file loading fails
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigurationError(f"Registration file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON in registration file: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error loading registration file: {e}")


def save_registration_file(file_path: str, data: Dict[str, Any]) -> None:
    """
    Save registration information to a JSON file.
    
    Args:
        file_path: Path to the registration file
        data: Registration data
        
    Raises:
        ConfigurationError: If file saving fails
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise ConfigurationError(f"Error saving registration file: {e}")