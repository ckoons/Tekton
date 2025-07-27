"""
MCP Client for connecting components to Hermes.

This client allows Tekton components to register their MCP tools with Hermes
and handle tool execution requests.
"""

import logging
import asyncio
import os
import sys
from typing import Dict, Any, Optional, List, Callable
import aiohttp
import json

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config
from shared.env import TektonEnviron
from shared.urls import hermes_url
from tekton.models import TektonBaseModel

logger = logging.getLogger(__name__)


class HermesMCPClient:
    """Client for connecting to Hermes MCP aggregator."""
    
    def __init__(
        self,
        hermes_url: str = None,
        component_name: str = None,
        component_port: int = None,
        component_version: str = "0.1.0",
        auth_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the Hermes MCP client.
        
        Args:
            hermes_url: Base URL of Hermes (defaults to http://localhost:8001)
            component_name: Name of the component
            component_port: Port where component is running (for tool execution callbacks)
            component_version: Version of the component
            auth_token: Optional authentication token
            timeout: Request timeout in seconds
        """
        # Use TektonEnviron pattern for URL resolution
        if hermes_url:
            self.hermes_url = hermes_url.rstrip("/")
        else:
            # Try environment variable first, then use hermes_url() function
            env_url = TektonEnviron.get("HERMES_URL")
            if env_url:
                self.hermes_url = env_url.rstrip("/")
            else:
                # Use the hermes_url() function from shared.urls which respects TektonEnviron
                from shared.urls import hermes_url as get_hermes_url
                self.hermes_url = get_hermes_url("")
        
        self.mcp_base_url = f"{self.hermes_url}/api/mcp/v2"
        self.component_name = component_name
        
        # Get component port from config or environment
        if component_port is None and component_name:
            config = get_component_config()
            component_lower = component_name.lower()
            try:
                component_config = getattr(config, component_lower)
                component_port = component_config.port
            except (AttributeError, TypeError):
                # Use TektonEnviron instead of os.environ
                port_str = TektonEnviron.get(f"{component_name.upper()}_PORT")
                if port_str:
                    component_port = int(port_str)
        
        self.component_port = component_port
        self.component_version = component_version
        self.auth_token = auth_token
        self.timeout = timeout
        
        # Track registered tools for cleanup
        self.registered_tools: List[str] = []
        
        logger.info(f"Initialized Hermes MCP client for {component_name} at {self.hermes_url}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if Hermes MCP service is healthy.
        
        Returns:
            Health status information
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.mcp_base_url}/health",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        return {
                            "status": "unhealthy",
                            "error": f"HTTP {resp.status}",
                            "detail": await resp.text()
                        }
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return {
                    "status": "error",
                    "error": str(e)
                }
    
    async def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        output_schema: Optional[Dict[str, Any]] = None,
        handler: Optional[Callable] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Register a tool with Hermes.
        
        Args:
            name: Tool name (will be prefixed with component name if not already)
            description: Tool description
            input_schema: JSON Schema for tool input
            output_schema: Output schema (currently not used by Hermes)
            handler: Tool handler function (ignored - execution handled via endpoints)
            tags: Optional tags for categorization
            metadata: Optional additional metadata
            
        Returns:
            Tool ID if successful, None otherwise
        """
        # Add component prefix if not already present
        if not name.startswith(f"{self.component_name}_"):
            full_name = f"{self.component_name}_{name}"
        else:
            full_name = name
            
        tool_spec = {
            "name": full_name,
            "description": description,
            "schema": input_schema,  # Note: Using "schema" as expected by Hermes
            "endpoint": f"http://localhost:{self.component_port}/api/tools/{name}/execute",
            "tags": tags or [],
            "metadata": {
                **(metadata or {}),
                "component": self.component_name,
                "component_version": self.component_version,
                "port": self.component_port
            }
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                headers = {}
                if self.auth_token:
                    headers["Authorization"] = f"Bearer {self.auth_token}"
                    
                async with session.post(
                    f"{self.mcp_base_url}/tools",
                    json=tool_spec,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        tool_id = result.get("tool_id")
                        
                        if tool_id:
                            self.registered_tools.append(tool_id)
                            logger.info(f"Registered tool: {full_name} ({tool_id})")
                        
                        return tool_id
                    else:
                        error_text = await resp.text()
                        logger.error(f"Failed to register tool {full_name}: HTTP {resp.status} - {error_text}")
                        return None
            except Exception as e:
                logger.error(f"Error registering tool {full_name}: {e}")
                return None
    
    async def unregister_tool(self, tool_id: str) -> bool:
        """
        Unregister a tool from Hermes.
        
        Args:
            tool_id: Tool ID to unregister
            
        Returns:
            Success status
        """
        async with aiohttp.ClientSession() as session:
            try:
                headers = {}
                if self.auth_token:
                    headers["Authorization"] = f"Bearer {self.auth_token}"
                    
                async with session.delete(
                    f"{self.mcp_base_url}/tools/{tool_id}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status in (200, 204):
                        if tool_id in self.registered_tools:
                            self.registered_tools.remove(tool_id)
                        logger.info(f"Unregistered tool: {tool_id}")
                        return True
                    else:
                        error_text = await resp.text()
                        logger.error(f"Failed to unregister tool {tool_id}: HTTP {resp.status} - {error_text}")
                        return False
            except Exception as e:
                logger.error(f"Error unregistering tool {tool_id}: {e}")
                return False
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all tools registered with Hermes.
        
        Returns:
            List of tool specifications
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.mcp_base_url}/tools",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"Failed to list tools: HTTP {resp.status}")
                        return []
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                return []
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get MCP capabilities from Hermes.
        
        Returns:
            Capabilities information
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.mcp_base_url}/capabilities",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"Failed to get capabilities: HTTP {resp.status}")
                        return {}
            except Exception as e:
                logger.error(f"Error getting capabilities: {e}")
                return {}
    
    async def execute_remote_tool(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool registered with Hermes.
        
        Args:
            tool_id: Tool ID
            parameters: Tool parameters
            context: Optional execution context
            
        Returns:
            Execution result
        """
        request_data = {
            "parameters": parameters,
            "context": context
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.mcp_base_url}/tools/{tool_id}/execute",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        error_text = await resp.text()
                        return {
                            "success": False,
                            "error": f"HTTP {resp.status}: {error_text}"
                        }
            except Exception as e:
                logger.error(f"Error executing tool {tool_id}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to Hermes for processing.
        
        Args:
            message: MCP message to process
            
        Returns:
            Processing result
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.mcp_base_url}/process",
                    json=message,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        error_text = await resp.text()
                        return {
                            "success": False,
                            "error": f"HTTP {resp.status}: {error_text}"
                        }
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def create_context(
        self,
        data: Dict[str, Any],
        context_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a context in Hermes.
        
        Args:
            data: Context data
            context_id: Optional context ID
            
        Returns:
            Context ID if successful
        """
        request_data = {
            "data": data,
            "source": {
                "component": self.component_name,
                "version": self.component_version
            }
        }
        
        if context_id:
            request_data["context_id"] = context_id
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.mcp_base_url}/contexts",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get("context_id")
                    else:
                        error_text = await resp.text()
                        logger.error(f"Failed to create context: HTTP {resp.status} - {error_text}")
                        return None
            except Exception as e:
                logger.error(f"Error creating context: {e}")
                return None
    
    async def update_context(
        self,
        context_id: str,
        updates: Dict[str, Any],
        operation: str = "update"
    ) -> bool:
        """
        Update a context in Hermes.
        
        Args:
            context_id: Context ID
            updates: Updates to apply
            operation: Update operation type
            
        Returns:
            Success status
        """
        request_data = {
            "updates": updates,
            "source": {
                "component": self.component_name,
                "version": self.component_version
            },
            "operation": operation
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.patch(
                    f"{self.mcp_base_url}/contexts/{context_id}",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status == 200:
                        return True
                    else:
                        error_text = await resp.text()
                        logger.error(f"Failed to update context: HTTP {resp.status} - {error_text}")
                        return False
            except Exception as e:
                logger.error(f"Error updating context: {e}")
                return False
    
    async def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a context from Hermes.
        
        Args:
            context_id: Context ID
            
        Returns:
            Context data if found
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.mcp_base_url}/contexts/{context_id}",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"Failed to get context: HTTP {resp.status}")
                        return None
            except Exception as e:
                logger.error(f"Error getting context: {e}")
                return None
    
    async def cleanup(self):
        """
        Cleanup by unregistering all tools registered by this client.
        """
        for tool_id in self.registered_tools.copy():
            await self.unregister_tool(tool_id)
        logger.info(f"Cleaned up {len(self.registered_tools)} registered tools")