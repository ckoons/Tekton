"""
FastMCP Client - Client utilities for MCP integration.

This module provides client utilities for interacting with MCP services,
including registering components, executing tools, and querying capabilities.
"""

import json
import time
import uuid
import logging
import aiohttp
from typing import Any, Dict, List, Optional, Union, Callable

from tekton.mcp.fastmcp.schema import (
    MessageSchema,
    ResponseSchema,
    ContentSchema,
    ToolSchema,
    ProcessorSchema
)

logger = logging.getLogger(__name__)

class MCPClient:
    """
    Client for interacting with MCP services.
    
    This class provides methods for registering components, executing tools,
    and querying capabilities from MCP services.
    """
    
    def __init__(
        self,
        base_url: str,
        component_id: str,
        component_name: str,
        timeout: float = 30.0,
        session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP service
            component_id: ID of the client component
            component_name: Name of the client component
            timeout: Request timeout in seconds
            session: Optional aiohttp session to use
        """
        self.base_url = base_url.rstrip("/")
        self.component_id = component_id
        self.component_name = component_name
        self.timeout = timeout
        self.session = session
        self.registered = False
        
        logger.info(f"MCP client initialized for {component_name} ({component_id})")
        
    async def register_component(
        self,
        capabilities: List[str],
        endpoint: Optional[str] = None,
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register the component with the MCP service.
        
        Args:
            capabilities: Component capabilities
            endpoint: Component endpoint
            version: Component version
            metadata: Additional metadata
            
        Returns:
            True if registration successful
        """
        url = f"{self.base_url}/components/register"
        
        registration_data = {
            "component_id": self.component_id,
            "name": self.component_name,
            "version": version,
            "capabilities": capabilities,
            "endpoint": endpoint,
            "metadata": metadata or {}
        }
        
        try:
            async with self._get_session() as session:
                async with session.post(
                    url,
                    json=registration_data,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.registered = result.get("success", False)
                        logger.info(f"Component registered: {self.component_name} ({self.component_id})")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Registration failed: {error}")
                        return False
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False
            
    async def unregister_component(self) -> bool:
        """
        Unregister the component from the MCP service.
        
        Returns:
            True if unregistration successful
        """
        if not self.registered:
            logger.warning("Component not registered")
            return False
            
        url = f"{self.base_url}/components/unregister"
        
        unregistration_data = {
            "component_id": self.component_id
        }
        
        try:
            async with self._get_session() as session:
                async with session.post(
                    url,
                    json=unregistration_data,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.registered = not result.get("success", False)
                        logger.info(f"Component unregistered: {self.component_id}")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Unregistration failed: {error}")
                        return False
        except Exception as e:
            logger.error(f"Unregistration error: {e}")
            return False
            
    async def register_tool(self, tool: Union[Dict[str, Any], ToolSchema]) -> Optional[str]:
        """
        Register a tool with the MCP service.
        
        Args:
            tool: Tool to register
            
        Returns:
            Tool ID if registration successful, None otherwise
        """
        url = f"{self.base_url}/mcp/tools"
        
        # Convert tool to dictionary if it's a schema object
        tool_data = tool.dict() if hasattr(tool, "dict") else tool
        
        try:
            async with self._get_session() as session:
                async with session.post(
                    url,
                    json=tool_data,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        tool_id = result.get("tool_id")
                        logger.info(f"Tool registered: {tool_data.get('name')} ({tool_id})")
                        return tool_id
                    else:
                        error = await response.text()
                        logger.error(f"Tool registration failed: {error}")
                        return None
        except Exception as e:
            logger.error(f"Tool registration error: {e}")
            return None
            
    async def register_processor(self, processor: Union[Dict[str, Any], ProcessorSchema]) -> Optional[str]:
        """
        Register a processor with the MCP service.
        
        Args:
            processor: Processor to register
            
        Returns:
            Processor ID if registration successful, None otherwise
        """
        url = f"{self.base_url}/mcp/processors"
        
        # Convert processor to dictionary if it's a schema object
        processor_data = processor.dict() if hasattr(processor, "dict") else processor
        
        try:
            async with self._get_session() as session:
                async with session.post(
                    url,
                    json=processor_data,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        processor_id = result.get("processor_id")
                        logger.info(f"Processor registered: {processor_data.get('name')} ({processor_id})")
                        return processor_id
                    else:
                        error = await response.text()
                        logger.error(f"Processor registration failed: {error}")
                        return None
        except Exception as e:
            logger.error(f"Processor registration error: {e}")
            return None
            
    async def execute_tool(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool.
        
        Args:
            tool_id: ID of the tool to execute
            parameters: Tool parameters
            context: Optional execution context
            
        Returns:
            Tool execution result
        """
        url = f"{self.base_url}/mcp/tools/{tool_id}/execute"
        
        execution_data = {
            "parameters": parameters,
            "context": context or {}
        }
        
        try:
            async with self._get_session() as session:
                async with session.post(
                    url,
                    json=execution_data,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Tool executed: {tool_id}")
                        return result
                    else:
                        error = await response.text()
                        logger.error(f"Tool execution failed: {error}")
                        return {
                            "success": False,
                            "error": f"Tool execution failed: {error}"
                        }
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "success": False,
                "error": f"Tool execution error: {e}"
            }
            
    async def process_message(
        self,
        message: Union[Dict[str, Any], MessageSchema]
    ) -> Union[Dict[str, Any], ResponseSchema]:
        """
        Process an MCP message.
        
        Args:
            message: Message to process
            
        Returns:
            Processing result
        """
        url = f"{self.base_url}/mcp/process"
        
        # Convert message to dictionary if it's a schema object
        message_data = message.dict() if hasattr(message, "dict") else message
        
        try:
            async with self._get_session() as session:
                async with session.post(
                    url,
                    json=message_data,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Message processed: {message_data.get('id')}")
                        return result
                    else:
                        error = await response.text()
                        logger.error(f"Message processing failed: {error}")
                        return {
                            "error": f"Message processing failed: {error}"
                        }
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            return {
                "error": f"Message processing error: {e}"
            }
            
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get MCP capabilities.
        
        Returns:
            Capabilities information
        """
        url = f"{self.base_url}/mcp/capabilities"
        
        try:
            async with self._get_session() as session:
                async with session.get(
                    url,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info("Got MCP capabilities")
                        return result
                    else:
                        error = await response.text()
                        logger.error(f"Getting capabilities failed: {error}")
                        return {}
        except Exception as e:
            logger.error(f"Getting capabilities error: {e}")
            return {}
            
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get an aiohttp session, creating one if needed.
        
        Returns:
            aiohttp.ClientSession
        """
        if self.session and not self.session.closed:
            return self.session
        return aiohttp.ClientSession()
        
    async def close(self):
        """Close the client session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("MCP client session closed")

# Standalone utility functions

async def register_component(
    base_url: str,
    component_id: str,
    component_name: str,
    capabilities: List[str],
    endpoint: Optional[str] = None,
    version: str = "1.0.0",
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Register a component with an MCP service.
    
    Args:
        base_url: Base URL of the MCP service
        component_id: Component ID
        component_name: Component name
        capabilities: Component capabilities
        endpoint: Component endpoint
        version: Component version
        metadata: Additional metadata
        
    Returns:
        True if registration successful
    """
    client = MCPClient(base_url, component_id, component_name)
    try:
        result = await client.register_component(
            capabilities=capabilities,
            endpoint=endpoint,
            version=version,
            metadata=metadata
        )
        await client.close()
        return result
    finally:
        await client.close()

async def execute_tool(
    base_url: str,
    tool_id: str,
    parameters: Dict[str, Any],
    component_id: str,
    component_name: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute a tool on an MCP service.
    
    Args:
        base_url: Base URL of the MCP service
        tool_id: ID of the tool to execute
        parameters: Tool parameters
        component_id: ID of the client component
        component_name: Name of the client component
        context: Optional execution context
        
    Returns:
        Tool execution result
    """
    client = MCPClient(base_url, component_id, component_name)
    try:
        result = await client.execute_tool(
            tool_id=tool_id,
            parameters=parameters,
            context=context
        )
        return result
    finally:
        await client.close()

async def get_capabilities(
    base_url: str,
    component_id: str,
    component_name: str
) -> Dict[str, Any]:
    """
    Get MCP capabilities from an MCP service.
    
    Args:
        base_url: Base URL of the MCP service
        component_id: ID of the client component
        component_name: Name of the client component
        
    Returns:
        Capabilities information
    """
    client = MCPClient(base_url, component_id, component_name)
    try:
        result = await client.get_capabilities()
        return result
    finally:
        await client.close()