"""
MCP Client - Client for Multimodal Cognitive Protocol in Ergon.

This module provides a client for the MCP protocol, allowing Ergon
components to process multimodal content through the MCP service.
"""

import os
import sys
import uuid
import base64
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, BinaryIO, Callable

import aiohttp
from aiohttp import ClientSession, ClientResponseError, ClientConnectorError

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config

logger = logging.getLogger(__name__)

class MCPClient:
    """
    Client for Multimodal Cognitive Protocol (MCP).
    
    This class provides methods for processing multimodal content
    and registering tools with the MCP service.
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_name: str = "Ergon MCP Client",
        hermes_url: Optional[str] = None
    ):
        """
        Initialize the MCP client.
        
        Args:
            client_id: Unique identifier for the client (generated if not provided)
            client_name: Human-readable name for the client
            hermes_url: URL of the Hermes API server
        """
        self.client_id = client_id or f"mcp-client-{uuid.uuid4()}"
        self.client_name = client_name
        self.hermes_url = hermes_url or self._get_hermes_url()
        
        # Internal state
        self.session: Optional[ClientSession] = None
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        
        logger.info(f"MCP client initialized: {self.client_id}")
    
    def _get_hermes_url(self) -> str:
        """
        Get the Hermes URL from environment variables or use the default.
        
        Returns:
            Hermes API URL
        """
        hermes_host = os.environ.get("HERMES_HOST", "localhost")
        config = get_component_config()
        hermes_port = config.hermes.port if hasattr(config, 'hermes') else int(os.environ.get("HERMES_PORT"))
        return f"http://{hermes_host}:{hermes_port}/api"
    
    async def initialize(self) -> bool:
        """
        Initialize the client.
        
        Returns:
            True if initialization was successful
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        # Register any tools that were defined before initialization
        for tool_id, tool_info in self.tools.items():
            if not await self.register_tool(
                tool_id=tool_id,
                **tool_info
            ):
                logger.warning(f"Failed to register tool: {tool_id}")
            
        return True
    
    async def close(self) -> None:
        """Close the client session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def process_content(
        self,
        content: Union[str, Dict[str, Any], bytes],
        content_type: str,
        context: Optional[Dict[str, Any]] = None,
        processing_options: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Process content using the MCP service.
        
        Args:
            content: Content to process (text, structured data, or binary)
            content_type: Type of content (text, code, image, structured)
            context: Optional context for processing
            processing_options: Optional processing options
            tools: List of tools to use for processing
            stream: Whether to stream the response
            
        Returns:
            Processing result
        """
        # Ensure client is initialized
        if self.session is None:
            self.session = aiohttp.ClientSession()
            
        # Prepare content based on its type
        prepared_content = self._prepare_content(content, content_type)
        
        # Create message
        message = {
            "id": f"mcp-msg-{uuid.uuid4()}",
            "client_id": self.client_id,
            "client_name": self.client_name,
            "content": prepared_content,
            "content_type": content_type,
            "context": context or {},
            "processing_options": processing_options or {},
            "tools": tools or []
        }
        
        try:
            # Send processing request
            endpoint = f"{self.hermes_url}/mcp/process"
            if stream:
                endpoint += "/stream"
                
            async with self.session.post(
                endpoint,
                json=message
            ) as response:
                response.raise_for_status()
                if stream:
                    # Return a stream of processing results
                    return {"stream": response.content}
                else:
                    # Return the full response
                    return await response.json()
                    
        except (ClientResponseError, ClientConnectorError) as e:
            logger.error(f"Error connecting to MCP service: {e}")
            return {"error": f"Connection error: {str(e)}"}
            
        except Exception as e:
            logger.error(f"Unexpected error processing content: {e}")
            return {"error": f"Unexpected error: {str(e)}"}
    
    async def register_tool(
        self,
        tool_id: str,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        returns: Dict[str, Any],
        handler: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a tool with the MCP service.
        
        Args:
            tool_id: Unique identifier for the tool
            name: Human-readable name for the tool
            description: Tool description
            parameters: Tool parameters
            returns: Tool return value description
            handler: Function to handle tool invocations
            metadata: Additional metadata
            
        Returns:
            True if registration was successful
        """
        # Store the tool info and handler for later use
        self.tools[tool_id] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "returns": returns,
            "metadata": metadata or {}
        }
        
        if handler:
            self.tool_handlers[tool_id] = handler
            
        # If client isn't initialized yet, defer registration
        if self.session is None:
            logger.info(f"Tool {tool_id} queued for registration")
            return True
            
        # Create tool specification
        tool_spec = {
            "tool_id": tool_id,
            "name": name,
            "description": description,
            "parameters": parameters,
            "returns": returns,
            "client_id": self.client_id,
            "client_name": self.client_name,
            "metadata": metadata or {}
        }
        
        try:
            # Send registration request
            async with self.session.post(
                f"{self.hermes_url}/mcp/tools/register",
                json=tool_spec
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                if result.get("success"):
                    logger.info(f"Tool {tool_id} successfully registered with MCP service")
                    return True
                else:
                    logger.error(f"Tool registration failed: {result}")
                    return False
                    
        except (ClientResponseError, ClientConnectorError) as e:
            logger.error(f"Error connecting to MCP service: {e}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error registering tool: {e}")
            return False
    
    async def unregister_tool(self, tool_id: str) -> bool:
        """
        Unregister a tool from the MCP service.
        
        Args:
            tool_id: ID of the tool to unregister
            
        Returns:
            True if unregistration was successful
        """
        # Remove the tool from local storage
        if tool_id in self.tools:
            del self.tools[tool_id]
            
        if tool_id in self.tool_handlers:
            del self.tool_handlers[tool_id]
            
        # If client isn't initialized, no need to call the service
        if self.session is None:
            return True
            
        try:
            # Send unregistration request
            async with self.session.delete(
                f"{self.hermes_url}/mcp/tools/unregister",
                params={"tool_id": tool_id, "client_id": self.client_id}
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                if result.get("success"):
                    logger.info(f"Tool {tool_id} successfully unregistered from MCP service")
                    return True
                else:
                    logger.error(f"Tool unregistration failed: {result}")
                    return False
                    
        except (ClientResponseError, ClientConnectorError) as e:
            logger.error(f"Error connecting to MCP service: {e}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error unregistering tool: {e}")
            return False
    
    async def execute_tool(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool registered with the MCP service.
        
        Args:
            tool_id: ID of the tool to execute
            parameters: Tool parameters
            context: Optional execution context
            
        Returns:
            Tool execution result
        """
        # Check if we have a local handler for this tool
        if tool_id in self.tool_handlers:
            try:
                # Execute the tool locally
                handler = self.tool_handlers[tool_id]
                result = await handler(parameters, context or {})
                return {"success": True, "result": result}
            except Exception as e:
                logger.error(f"Error executing tool {tool_id} locally: {e}")
                return {"success": False, "error": str(e)}
                
        # Otherwise, call the MCP service
        if self.session is None:
            self.session = aiohttp.ClientSession()
            
        # Create execution request
        execution_req = {
            "tool_id": tool_id,
            "parameters": parameters,
            "client_id": self.client_id,
            "context": context or {}
        }
        
        try:
            # Send execution request
            async with self.session.post(
                f"{self.hermes_url}/mcp/tools/execute",
                json=execution_req
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except (ClientResponseError, ClientConnectorError) as e:
            logger.error(f"Error connecting to MCP service: {e}")
            return {"success": False, "error": f"Connection error: {str(e)}"}
            
        except Exception as e:
            logger.error(f"Unexpected error executing tool: {e}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    async def create_context(
        self,
        context_type: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a new context in the MCP service.
        
        Args:
            context_type: Type of context
            content: Context content
            metadata: Optional metadata
            
        Returns:
            Context ID if created successfully, None otherwise
        """
        # Ensure client is initialized
        if self.session is None:
            self.session = aiohttp.ClientSession()
            
        # Create context request
        context_req = {
            "context_type": context_type,
            "content": content,
            "client_id": self.client_id,
            "metadata": metadata or {}
        }
        
        try:
            # Send context creation request
            async with self.session.post(
                f"{self.hermes_url}/mcp/contexts",
                json=context_req
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                if "context_id" in result:
                    logger.info(f"Context created: {result.get('context_id')}")
                    return result.get("context_id")
                else:
                    logger.error(f"Context creation failed: {result}")
                    return None
                    
        except (ClientResponseError, ClientConnectorError) as e:
            logger.error(f"Error connecting to MCP service: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error creating context: {e}")
            return None
    
    async def enhance_context(
        self,
        context_id: str,
        content: Dict[str, Any],
        operation: str = "add"
    ) -> bool:
        """
        Enhance an existing context.
        
        Args:
            context_id: ID of the context to enhance
            content: Content to add to the context
            operation: Operation to perform (add, update, remove)
            
        Returns:
            True if enhancement was successful
        """
        # Ensure client is initialized
        if self.session is None:
            self.session = aiohttp.ClientSession()
            
        # Create enhancement request
        enhancement_req = {
            "client_id": self.client_id,
            "content": content,
            "operation": operation
        }
        
        try:
            # Send enhancement request
            async with self.session.post(
                f"{self.hermes_url}/mcp/contexts/{context_id}/enhance",
                json=enhancement_req
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                if result.get("success"):
                    logger.info(f"Context {context_id} enhanced with operation {operation}")
                    return True
                else:
                    logger.error(f"Context enhancement failed: {result}")
                    return False
                    
        except (ClientResponseError, ClientConnectorError) as e:
            logger.error(f"Error connecting to MCP service: {e}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error enhancing context: {e}")
            return False
    
    def _prepare_content(
        self,
        content: Union[str, Dict[str, Any], bytes, BinaryIO],
        content_type: str
    ) -> Dict[str, Any]:
        """
        Prepare content for processing.
        
        Args:
            content: Content to prepare
            content_type: Type of content
            
        Returns:
            Prepared content
        """
        if content_type == "text" or content_type == "code":
            if isinstance(content, str):
                return {"text": content}
            else:
                raise ValueError(f"Invalid content type for {content_type}: {type(content)}")
                
        elif content_type == "structured":
            if isinstance(content, dict):
                return {"data": content}
            else:
                raise ValueError(f"Invalid content type for structured data: {type(content)}")
                
        elif content_type == "image":
            # Handle binary content for images
            if isinstance(content, bytes):
                encoded = base64.b64encode(content).decode("utf-8")
                return {"image": encoded, "format": "base64"}
            elif hasattr(content, "read"):
                # File-like object
                data = content.read()
                if isinstance(data, bytes):
                    encoded = base64.b64encode(data).decode("utf-8")
                    return {"image": encoded, "format": "base64"}
                else:
                    raise ValueError("File-like object must contain binary data")
            else:
                raise ValueError(f"Invalid content type for image: {type(content)}")
                
        else:
            # Generic fallback
            return {"content": str(content)}
    
    # Context manager support
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()