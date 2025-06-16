#!/usr/bin/env python3
"""
MCP Adapter for Engram Memory System

This module implements the Multi-Capability Provider (MCP) protocol adapter
for Engram, allowing it to be used as an MCP service or capability provider.
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
logger = logging.getLogger("engram.mcp_adapter")

# Import Engram modules
from engram.core.memory import MemoryService
from engram.core.structured_memory import StructuredMemory
from engram.core.nexus import NexusInterface
from engram.core.memory_manager import MemoryManager


class MCPAdapter:
    """
    Multi-Capability Provider (MCP) adapter for Engram Memory System.
    
    This class provides an adapter that implements the MCP protocol
    for Engram's memory services, allowing them to be used within
    an MCP ecosystem.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the MCP Adapter.
        
        Args:
            memory_manager: The memory manager instance to use
        """
        self.memory_manager = memory_manager
        self.capabilities = self._generate_capabilities()
        logger.info("MCP Adapter initialized with capabilities")
    
    def _generate_capabilities(self) -> Dict[str, Any]:
        """
        Generate the capability manifest for Engram's memory services.
        
        Returns:
            A dictionary describing available capabilities
        """
        return {
            "memory_store": {
                "description": "Store information in Engram's memory system",
                "parameters": {
                    "content": {"type": "string", "description": "Content to store in memory"},
                    "namespace": {"type": "string", "description": "Namespace to store memory in", "default": "conversations"},
                    "metadata": {"type": "object", "description": "Additional metadata for the memory", "optional": True}
                },
                "returns": {"type": "object", "description": "Result of memory storage operation"}
            },
            "memory_query": {
                "description": "Query Engram's memory system for relevant information",
                "parameters": {
                    "query": {"type": "string", "description": "Query text to search for"},
                    "namespace": {"type": "string", "description": "Namespace to search in", "default": "conversations"},
                    "limit": {"type": "integer", "description": "Maximum number of results to return", "default": 5}
                },
                "returns": {"type": "object", "description": "Search results"}
            },
            "context": {
                "description": "Get formatted memory context across multiple namespaces",
                "parameters": {
                    "query": {"type": "string", "description": "Query to use for context retrieval"},
                    "namespaces": {"type": "array", "description": "Namespaces to include", "default": ["conversations", "thinking", "longterm"]},
                    "limit": {"type": "integer", "description": "Results per namespace", "default": 3}
                },
                "returns": {"type": "object", "description": "Formatted context from memory"}
            },
            "structured_memory_add": {
                "description": "Add a memory to the structured memory system",
                "parameters": {
                    "content": {"type": "string", "description": "Content to store"},
                    "category": {"type": "string", "description": "Category for the memory", "default": "session"},
                    "importance": {"type": "integer", "description": "Importance level (1-5)", "optional": True},
                    "tags": {"type": "array", "description": "Tags for the memory", "optional": True},
                    "metadata": {"type": "object", "description": "Additional metadata", "optional": True}
                },
                "returns": {"type": "object", "description": "Result with memory ID"}
            },
            "nexus_process": {
                "description": "Process a message through the Nexus interface",
                "parameters": {
                    "message": {"type": "string", "description": "Message to process"},
                    "is_user": {"type": "boolean", "description": "Whether the message is from the user", "default": True},
                    "metadata": {"type": "object", "description": "Additional message metadata", "optional": True},
                    "auto_agency": {"type": "boolean", "description": "Whether to use automatic agency", "optional": True}
                },
                "returns": {"type": "object", "description": "Processing result"}
            }
        }
    
    async def get_manifest(self) -> Dict[str, Any]:
        """
        Get the MCP capability manifest.
        
        Returns:
            A dictionary containing the MCP manifest
        """
        return {
            "name": "engram",
            "version": "0.8.0",
            "description": "Engram Memory System for AI assistants",
            "capabilities": self.capabilities
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an MCP request.
        
        Args:
            request: The MCP request dictionary
            
        Returns:
            The response dictionary
        """
        try:
            # Extract request elements
            capability = request.get("capability")
            parameters = request.get("parameters", {})
            client_id = request.get("client_id") or parameters.get("client_id")
            
            # Validate request
            if not capability:
                return {"error": "Missing capability in request"}
            
            if capability not in self.capabilities:
                return {"error": f"Unknown capability: {capability}"}
            
            # Route to appropriate handler
            if capability == "memory_store":
                return await self._handle_memory_store(client_id, parameters)
            elif capability == "memory_query":
                return await self._handle_memory_query(client_id, parameters)
            elif capability == "context":
                return await self._handle_context(client_id, parameters)
            elif capability == "structured_memory_add":
                return await self._handle_structured_memory_add(client_id, parameters)
            elif capability == "nexus_process":
                return await self._handle_nexus_process(client_id, parameters)
            else:
                return {"error": f"Capability {capability} not implemented"}
        
        except Exception as e:
            logger.error(f"Error processing MCP request: {e}")
            return {"error": f"Failed to process request: {str(e)}"}
    
    async def _handle_memory_store(self, client_id: Optional[str], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a memory store capability request.
        
        Args:
            client_id: The client identifier
            parameters: Request parameters
            
        Returns:
            Result of the memory store operation
        """
        # Extract parameters
        content = parameters.get("content")
        namespace = parameters.get("namespace", "conversations")
        metadata = parameters.get("metadata")
        
        # Validate required parameters
        if not content:
            return {"error": "Missing required parameter: content"}
        
        # Get memory service for client
        memory_service = await self.memory_manager.get_memory_service(client_id)
        
        # Store the memory
        success = await memory_service.add(
            content=content,
            namespace=namespace,
            metadata=metadata
        )
        
        # Return result
        return {
            "success": success,
            "namespace": namespace,
        }
    
    async def _handle_memory_query(self, client_id: Optional[str], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a memory query capability request.
        
        Args:
            client_id: The client identifier
            parameters: Request parameters
            
        Returns:
            Search results
        """
        # Extract parameters
        query = parameters.get("query")
        namespace = parameters.get("namespace", "conversations")
        limit = parameters.get("limit", 5)
        
        # Validate required parameters
        if not query:
            return {"error": "Missing required parameter: query"}
        
        # Get memory service for client
        memory_service = await self.memory_manager.get_memory_service(client_id)
        
        # Query memory
        results = await memory_service.search(
            query=query,
            namespace=namespace,
            limit=limit
        )
        
        # Return results
        return results
    
    async def _handle_context(self, client_id: Optional[str], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a context capability request.
        
        Args:
            client_id: The client identifier
            parameters: Request parameters
            
        Returns:
            Formatted context from memory
        """
        # Extract parameters
        query = parameters.get("query")
        namespaces = parameters.get("namespaces", ["conversations", "thinking", "longterm"])
        limit = parameters.get("limit", 3)
        
        # Validate required parameters
        if not query:
            return {"error": "Missing required parameter: query"}
        
        # Get memory service for client
        memory_service = await self.memory_manager.get_memory_service(client_id)
        
        # Get context
        context = await memory_service.get_relevant_context(
            query=query,
            namespaces=namespaces,
            limit=limit
        )
        
        # Return context
        return {"context": context}
    
    async def _handle_structured_memory_add(self, client_id: Optional[str], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a structured memory add capability request.
        
        Args:
            client_id: The client identifier
            parameters: Request parameters
            
        Returns:
            Result of the memory add operation
        """
        # Extract parameters
        content = parameters.get("content")
        category = parameters.get("category", "session")
        importance = parameters.get("importance")
        tags = parameters.get("tags")
        metadata = parameters.get("metadata")
        
        # Validate required parameters
        if not content:
            return {"error": "Missing required parameter: content"}
        
        # Get structured memory for client
        structured_memory = await self.memory_manager.get_structured_memory(client_id)
        
        # Add memory
        memory_id = await structured_memory.add_memory(
            content=content,
            category=category,
            importance=importance,
            tags=tags,
            metadata=metadata
        )
        
        # Return result
        return {"success": bool(memory_id), "memory_id": memory_id}
    
    async def _handle_nexus_process(self, client_id: Optional[str], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a nexus process capability request.
        
        Args:
            client_id: The client identifier
            parameters: Request parameters
            
        Returns:
            Result of message processing
        """
        # Extract parameters
        message = parameters.get("message")
        is_user = parameters.get("is_user", True)
        metadata = parameters.get("metadata")
        auto_agency = parameters.get("auto_agency")
        
        # Validate required parameters
        if not message:
            return {"error": "Missing required parameter: message"}
        
        # Get nexus interface for client
        nexus = await self.memory_manager.get_nexus_interface(client_id)
        
        # Process message
        result = await nexus.process_message(message, is_user, metadata)
        
        # Return result
        return {"success": True, "result": result}
