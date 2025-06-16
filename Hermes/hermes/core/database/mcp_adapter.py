#!/usr/bin/env python3
"""
Database MCP Adapter - Multi-Capability Provider for Hermes Database Services

This module implements the Multi-Capability Provider (MCP) protocol adapter
for Hermes Database Services, allowing database operations to be accessed
through the MCP protocol.
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("hermes.database.mcp_adapter")

# Import Hermes modules
from hermes.core.database.manager import DatabaseManager
from hermes.core.database.database_types import DatabaseType, DatabaseBackend
from hermes.core.database.mcp_capabilities import generate_capabilities
from hermes.core.database.mcp_handlers import (
    handle_vector_request,
    handle_key_value_request,
    handle_graph_request,
    handle_document_request,
    handle_cache_request,
    handle_relational_request
)


class DatabaseMCPAdapter:
    """
    Multi-Capability Provider (MCP) adapter for Hermes Database Services.
    
    This class provides an adapter that implements the MCP protocol
    for Hermes database services, allowing them to be used within
    an MCP ecosystem.
    """
    
    def __init__(self, database_manager: DatabaseManager):
        """
        Initialize the MCP Adapter.
        
        Args:
            database_manager: The database manager instance to use
        """
        self.database_manager = database_manager
        self.capabilities = generate_capabilities()
        logger.info("Database MCP Adapter initialized with capabilities")
    
    async def get_manifest(self) -> Dict[str, Any]:
        """
        Get the MCP capability manifest.
        
        Returns:
            A dictionary containing the MCP manifest
        """
        return {
            "name": "hermes_database",
            "version": "0.1.0",
            "description": "Hermes Database Services MCP Provider",
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
            
            # Validate request
            if not capability:
                return {"error": "Missing capability in request"}
            
            if capability not in self.capabilities:
                return {"error": f"Unknown capability: {capability}"}
            
            # Route to appropriate handler based on capability prefix
            if capability.startswith("vector_"):
                return await handle_vector_request(
                    self.database_manager, capability, parameters
                )
            elif capability.startswith("kv_"):
                return await handle_key_value_request(
                    self.database_manager, capability, parameters
                )
            elif capability.startswith("graph_"):
                return await handle_graph_request(
                    self.database_manager, capability, parameters
                )
            elif capability.startswith("document_"):
                return await handle_document_request(
                    self.database_manager, capability, parameters
                )
            elif capability.startswith("cache_"):
                return await handle_cache_request(
                    self.database_manager, capability, parameters
                )
            elif capability.startswith("sql_"):
                return await handle_relational_request(
                    self.database_manager, capability, parameters
                )
            else:
                return {"error": f"Capability {capability} not implemented"}
        
        except Exception as e:
            logger.error(f"Error processing database MCP request: {e}")
            return {"error": f"Failed to process request: {str(e)}"}