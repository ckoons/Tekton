"""
A2A Client - JSON-RPC 2.0 Client for Agent-to-Agent Protocol v0.2.1

This module provides a client for the A2A protocol v0.2.1, allowing Ergon
agents to communicate with other agents using JSON-RPC 2.0.
"""

import os
import sys
import time
import uuid
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable

import aiohttp
from aiohttp import ClientSession, ClientResponseError, ClientConnectorError

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config
from ergon.utils.hermes_helper import register_with_hermes

logger = logging.getLogger(__name__)


class A2AClient:
    """
    Client for Agent-to-Agent communication using JSON-RPC 2.0.
    
    This class provides methods for communicating with the A2A service
    using the standard A2A Protocol v0.2.1.
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        agent_name: str = "Ergon Agent",
        agent_version: str = "0.1.0",
        capabilities: Optional[List[str]] = None,
        supported_methods: Optional[List[str]] = None,
        hermes_url: Optional[str] = None
    ):
        """
        Initialize the A2A client.
        
        Args:
            agent_id: Unique identifier for the agent (generated if not provided)
            agent_name: Human-readable name for the agent
            agent_version: Agent version
            capabilities: List of agent capabilities
            supported_methods: List of JSON-RPC methods this agent supports
            hermes_url: URL of the Hermes A2A service
        """
        self.agent_id = agent_id or f"ergon-agent-{uuid.uuid4()}"
        self.agent_name = agent_name
        self.agent_version = agent_version
        self.capabilities = capabilities or ["task_execution", "workflow_management"]
        self.supported_methods = supported_methods or []
        self.hermes_url = hermes_url or self._get_hermes_url()
        
        # A2A endpoint
        self.a2a_endpoint = f"{self.hermes_url}/a2a/v1"
        
        # Internal state
        self.session: Optional[ClientSession] = None
        self.registered = False
        
        logger.info(f"A2A client initialized for agent {self.agent_id}")
    
    def _get_hermes_url(self) -> str:
        """Get the Hermes URL from environment variables or use the default."""
        hermes_host = os.environ.get("HERMES_HOST", "localhost")
        config = get_component_config()
        hermes_port = config.hermes.port if hasattr(config, 'hermes') else int(os.environ.get("HERMES_PORT"))
        return f"http://{hermes_host}:{hermes_port}/api"
    
    async def initialize(self) -> bool:
        """Initialize the client and register with A2A service."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        # Register with A2A service
        if not self.registered:
            return await self.register()
        
        return True
    
    async def close(self) -> None:
        """Close the client session and unregister."""
        if self.registered:
            await self.unregister()
        
        if self.session:
            await self.session.close()
            self.session = None
    
    def _get_ergon_port(self) -> int:
        """Get Ergon port from configuration."""
        config = get_component_config()
        try:
            return config.ergon.port
        except (AttributeError, TypeError):
            return int(os.environ.get('ERGON_PORT'))
    
    async def _send_jsonrpc(
        self,
        method: str,
        params: Optional[Union[Dict[str, Any], List[Any]]] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to the A2A service.
        
        Args:
            method: The JSON-RPC method to call
            params: Method parameters
            request_id: Request ID (generated if not provided)
            
        Returns:
            The JSON-RPC response
            
        Raises:
            Exception: If the request fails or returns an error
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        # Create JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id or str(uuid.uuid4())
        }
        
        if params is not None:
            request["params"] = params
        
        try:
            # Log the request
            logger.debug(f"Sending JSON-RPC request to {self.a2a_endpoint}/: {request}")
            
            # Send request
            async with self.session.post(
                f"{self.a2a_endpoint}/",
                json=request,
                headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                text = await response.text()
                logger.debug(f"Received response text: {text}")
                
                # Try to parse JSON
                try:
                    result = json.loads(text) if text else None
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.error(f"Response text was: {text}")
                    return {}
                
                # Handle None response
                if result is None:
                    logger.error(f"Received None response from A2A endpoint for method {method}")
                    return {}
                
                # Check for JSON-RPC error
                if "error" in result and result["error"] is not None:
                    error = result["error"]
                    # Check if error dict has the expected fields
                    if isinstance(error, dict) and "code" in error and "message" in error:
                        raise Exception(f"JSON-RPC Error {error['code']}: {error['message']}")
                    else:
                        raise Exception(f"JSON-RPC Error (malformed): {error}")
                
                # Return the result field if present, otherwise return empty dict
                return result.get("result", {})
        
        except ClientResponseError as e:
            logger.error(f"HTTP error in JSON-RPC request: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in JSON-RPC request: {e}")
            logger.error(f"Request was: {request}")
            logger.error(f"A2A endpoint: {self.a2a_endpoint}/")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    async def register(self) -> bool:
        """Register this agent with the A2A service."""
        try:
            # Create agent card (using camelCase for JSON fields)
            agent_card = {
                "id": self.agent_id,
                "name": self.agent_name,
                "description": f"{self.agent_name} - Workflow and task execution agent",
                "version": self.agent_version,
                "capabilities": self.capabilities,
                "supportedMethods": self.supported_methods,  # camelCase for JSON
                "endpoint": f"http://localhost:{self._get_ergon_port()}/api/a2a/v1/",
                "tags": ["ergon", "workflow", "task"],
                "metadata": {
                    "component": "ergon",
                    "protocolVersion": "0.2.1"  # camelCase for JSON
                }
            }
            
            # Register via JSON-RPC
            result = await self._send_jsonrpc(
                "agent.register",
                {"agent_card": agent_card}
            )
            
            if result and result.get("success"):
                self.registered = True
                logger.info(f"Agent {self.agent_id} registered with A2A service")
                
                # Also register with Hermes component registry
                await register_with_hermes(
                    service_id=self.agent_id,
                    name=self.agent_name,
                    capabilities=["a2a"] + self.capabilities,
                    metadata={
                        "a2a_agent": True,
                        "agent_card": agent_card
                    }
                )
                
                return True
            else:
                logger.error(f"A2A registration failed: {result}")
                return False
        
        except Exception as e:
            logger.error(f"Error registering with A2A service: {e}")
            return False
    
    async def unregister(self) -> bool:
        """Unregister from the A2A service."""
        if not self.registered:
            return True
        
        try:
            result = await self._send_jsonrpc(
                "agent.unregister",
                {"agent_id": self.agent_id}
            )
            
            if result.get("success"):
                self.registered = False
                logger.info(f"Agent {self.agent_id} unregistered from A2A service")
                return True
            else:
                logger.error(f"A2A unregistration failed: {result}")
                return False
        
        except Exception as e:
            logger.error(f"Error unregistering from A2A service: {e}")
            return False
    
    async def heartbeat(self) -> bool:
        """Send heartbeat to maintain agent registration."""
        try:
            result = await self._send_jsonrpc(
                "agent.heartbeat",
                {"agent_id": self.agent_id}
            )
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
            return False
    
    async def update_status(self, status: str) -> bool:
        """Update agent status (active, idle, busy, etc.)."""
        try:
            result = await self._send_jsonrpc(
                "agent.update_status",
                {
                    "agent_id": self.agent_id,
                    "status": status
                }
            )
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return False
    
    async def discover_agents(
        self,
        capabilities: Optional[List[str]] = None,
        methods: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Discover other agents based on criteria."""
        try:
            query = {}
            if capabilities:
                query["capabilities"] = capabilities
            if methods:
                query["methods"] = methods
            if tags:
                query["tags"] = tags
            
            result = await self._send_jsonrpc(
                "discovery.query",
                {"query": query}
            )
            
            return result.get("agents", [])
        except Exception as e:
            logger.error(f"Error discovering agents: {e}")
            return []
    
    async def create_task(
        self,
        name: str,
        description: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        priority: str = "normal"
    ) -> Optional[Dict[str, Any]]:
        """Create a new task."""
        try:
            result = await self._send_jsonrpc(
                "task.create",
                {
                    "name": name,
                    "created_by": self.agent_id,
                    "description": description,
                    "input_data": input_data,
                    "priority": priority
                }
            )
            
            logger.info(f"Created task: {result.get('id')}")
            return result
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task information."""
        try:
            return await self._send_jsonrpc(
                "task.get",
                {"task_id": task_id}
            )
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return None
    
    async def update_task_progress(
        self,
        task_id: str,
        progress: float,
        message: Optional[str] = None
    ) -> bool:
        """Update task progress."""
        try:
            result = await self._send_jsonrpc(
                "task.update_progress",
                {
                    "task_id": task_id,
                    "progress": progress,
                    "message": message
                }
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error updating task progress: {e}")
            return False
    
    async def complete_task(
        self,
        task_id: str,
        output_data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ) -> bool:
        """Complete a task."""
        try:
            result = await self._send_jsonrpc(
                "task.complete",
                {
                    "task_id": task_id,
                    "output_data": output_data,
                    "message": message
                }
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return False
    
    async def fail_task(
        self,
        task_id: str,
        error_data: Dict[str, Any],
        message: Optional[str] = None
    ) -> bool:
        """Fail a task."""
        try:
            result = await self._send_jsonrpc(
                "task.fail",
                {
                    "task_id": task_id,
                    "error_data": error_data,
                    "message": message
                }
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error failing task: {e}")
            return False
    
    async def forward_to_agent(
        self,
        agent_id: str,
        method: str,
        params: Dict[str, Any]
    ) -> Any:
        """Forward a method call to a specific agent via Hermes."""
        try:
            return await self._send_jsonrpc(
                "agent.forward",
                {
                    "agent_id": agent_id,
                    "method": method,
                    "params": params
                }
            )
        except Exception as e:
            logger.error(f"Error forwarding to agent: {e}")
            return None
    
    async def subscribe_to_channel(self, channel: str) -> bool:
        """Subscribe to a message channel."""
        try:
            result = await self._send_jsonrpc(
                "channel.subscribe",
                {
                    "agent_id": self.agent_id,
                    "channel": channel
                }
            )
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error subscribing to channel: {e}")
            return False
    
    async def publish_to_channel(
        self,
        channel: str,
        message: Dict[str, Any]
    ) -> bool:
        """Publish a message to a channel."""
        try:
            result = await self._send_jsonrpc(
                "channel.publish",
                {
                    "channel": channel,
                    "message": message
                }
            )
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error publishing to channel: {e}")
            return False