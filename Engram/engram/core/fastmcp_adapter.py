#!/usr/bin/env python3
"""
FastMCP Adapter for Engram Memory System

This module implements the Model Context Protocol (MCP) using the FastMCP
decorator-based approach for the Engram memory system.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.fastmcp_adapter")

# Import FastMCP if available
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        MCPClient
    )
    from tekton.mcp.fastmcp.schema import (
        MCPTool,
        MCPCapability,
        MCPRequest,
        MCPResponse
    )
    fastmcp_available = True
except ImportError:
    logger.warning("FastMCP not available")
    fastmcp_available = False

# Import Engram modules
from engram.core.memory import MemoryService
from engram.core.structured_memory import StructuredMemory
from engram.core.nexus import NexusInterface
from engram.core.memory_manager import MemoryManager

# Import FastMCP tools
if fastmcp_available:
    from engram.core.mcp import (
        memory_store,
        memory_query,
        get_context,
        structured_memory_add,
        structured_memory_get,
        structured_memory_update,
        structured_memory_delete,
        structured_memory_search,
        nexus_process,
        get_all_tools,
        get_all_capabilities
    )


class FastMCPAdapter:
    """
    FastMCP adapter for Engram Memory System.
    
    This class provides an adapter that implements the MCP protocol
    using the FastMCP decorator-based approach for Engram's memory services.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the FastMCP Adapter.
        
        Args:
            memory_manager: The memory manager instance to use
        """
        self.memory_manager = memory_manager
        
        # Set default client ID from environment or use "claude"
        self.default_client_id = os.environ.get("ENGRAM_CLIENT_ID", "claude")
        
        # Check if FastMCP is available
        if not fastmcp_available:
            logger.warning("FastMCP not available, adapter will be limited")
            
        logger.info("FastMCP Adapter initialized")
    
    async def get_tools(self) -> List[Any]:
        """
        Get all available FastMCP tools.
        
        Returns:
            A list of tools
        """
        if not fastmcp_available:
            return []
            
        return get_all_tools(self.memory_manager)
    
    async def get_capabilities(self) -> List[Any]:
        """
        Get all available FastMCP capabilities.
        
        Returns:
            A list of capabilities
        """
        if not fastmcp_available:
            return []
            
        return get_all_capabilities(self.memory_manager)
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an MCP request using FastMCP.
        
        Args:
            request: The FastMCP request object
            
        Returns:
            The FastMCP response object
        """
        if not fastmcp_available:
            return {
                "status": "error",
                "error": "FastMCP not available",
                "result": None
            }
            
        try:
            # Convert dict to MCPRequest if needed
            if isinstance(request, dict):
                request = MCPRequest(**request)
                
            # Get client ID from request or use default
            client_id = request.client_id or self.default_client_id
            
            # Get tool name
            tool_name = request.tool
            
            # Define tool handlers
            tool_handlers = {
                # Memory Operations
                "MemoryStore": memory_store,
                "MemoryQuery": memory_query,
                "GetContext": get_context,
                
                # Structured Memory Operations
                "StructuredMemoryAdd": structured_memory_add,
                "StructuredMemoryGet": structured_memory_get,
                "StructuredMemoryUpdate": structured_memory_update,
                "StructuredMemoryDelete": structured_memory_delete,
                "StructuredMemorySearch": structured_memory_search,
                
                # Nexus Operations
                "NexusProcess": nexus_process
            }
            
            # Check if tool is supported
            if tool_name not in tool_handlers:
                return MCPResponse(
                    status="error",
                    error=f"Unsupported tool: {tool_name}",
                    result=None
                )
                
            # Get the handler
            handler = tool_handlers[tool_name]
            
            # Get parameters
            parameters = request.parameters or {}
            
            # Initialize services based on tool type
            if tool_name in ["MemoryStore", "MemoryQuery", "GetContext"]:
                memory_service = await self.memory_manager.get_memory_service(client_id)
                parameters["memory_service"] = memory_service
            elif tool_name.startswith("StructuredMemory"):
                structured_memory = await self.memory_manager.get_structured_memory(client_id)
                parameters["structured_memory"] = structured_memory
            elif tool_name == "NexusProcess":
                nexus = await self.memory_manager.get_nexus_interface(client_id)
                parameters["nexus"] = nexus
                
            # Execute handler
            result = await handler(**parameters)
            
            # Return response
            return MCPResponse(
                status="success",
                result=result,
                error=None
            )
            
        except Exception as e:
            logger.error(f"Error processing FastMCP request: {e}")
            return MCPResponse(
                status="error",
                error=f"Error processing request: {str(e)}",
                result=None
            )
            
    async def initialize_services(self, client_id: Optional[str] = None):
        """
        Pre-initialize services for a client.
        
        Args:
            client_id: Client ID to initialize services for
        """
        client_id = client_id or self.default_client_id
        
        try:
            # Initialize core services
            await self.memory_manager.get_memory_service(client_id)
            await self.memory_manager.get_structured_memory(client_id)
            await self.memory_manager.get_nexus_interface(client_id)
            
            logger.info(f"Pre-initialized services for client: {client_id}")
        except Exception as e:
            logger.error(f"Error initializing services: {e}")