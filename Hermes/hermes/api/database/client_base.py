"""
Base Database Client - Common functionality for database clients.

This module provides the base request handler and common functionality
for all database-specific clients.
"""

import logging
import aiohttp
from typing import Dict, List, Any, Optional, Union

# Configure logger
logger = logging.getLogger(__name__)


class BaseRequest:
    """
    Base request handler for database operations.
    
    This class handles the communication with the database services,
    supporting both MCP and REST API protocols.
    """
    
    def __init__(self,
                endpoint: str,
                use_mcp: bool = True,
                component_id: str = None):
        """
        Initialize the request handler.
        
        Args:
            endpoint: API endpoint for database services
            use_mcp: Whether to use the MCP protocol
            component_id: Component identifier
        """
        self.endpoint = endpoint
        self.use_mcp = use_mcp
        self.component_id = component_id
    
    async def mcp_invoke(self, capability: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke an MCP capability.
        
        Args:
            capability: Name of the capability to invoke
            parameters: Parameters for the capability
            
        Returns:
            Response from the capability invocation
        """
        # Add component ID to parameters if available
        if self.component_id:
            parameters["client_id"] = self.component_id
        
        # Create request payload
        payload = {
            "capability": capability,
            "parameters": parameters
        }
        
        # Make HTTP request to MCP endpoint
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.endpoint}/invoke", json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"MCP request failed: {error_text}")
                    return {"error": f"MCP request failed with status {response.status}: {error_text}"}
                
                return await response.json()
    
    async def api_request(self, method: str, path: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a direct API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path
            data: Optional request data
            
        Returns:
            Response from the API
        """
        url = f"{self.endpoint}/{path}"
        
        # Add component ID to data if available and data is provided
        if self.component_id and data:
            data["client_id"] = self.component_id
        
        # Make HTTP request
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, params=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API request failed: {error_text}")
                        return {"error": f"API request failed with status {response.status}: {error_text}"}
                    
                    return await response.json()
            else:
                async with session.request(method, url, json=data) as response:
                    if response.status not in (200, 201, 204):
                        error_text = await response.text()
                        logger.error(f"API request failed: {error_text}")
                        return {"error": f"API request failed with status {response.status}: {error_text}"}
                    
                    if response.status == 204:
                        return {"success": True}
                    
                    return await response.json()
    
    async def execute_request(self, 
                            capability: str, 
                            api_path: str,
                            method: str = "POST",
                            parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a database request using either MCP or REST API.
        
        Args:
            capability: MCP capability name
            api_path: REST API path
            method: HTTP method for REST API
            parameters: Request parameters
            
        Returns:
            Response from the request
        """
        parameters = parameters or {}
        
        if self.use_mcp:
            return await self.mcp_invoke(capability, parameters)
        else:
            return await self.api_request(method, api_path, parameters)