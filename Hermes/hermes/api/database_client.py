"""
Database Client Library - Client interface for Hermes Database Services.

This module provides a client library for accessing Hermes database services,
either through direct API calls or using the MCP protocol.
"""

import os
import logging
import aiohttp
import json
from typing import Dict, List, Any, Optional, Union, Tuple

# Import specific client implementations
from hermes.api.database.vector_client import VectorDatabaseClient
from hermes.api.database.key_value_client import KeyValueDatabaseClient
from hermes.api.database.graph_client import GraphDatabaseClient
from hermes.api.database.document_client import DocumentDatabaseClient
from hermes.api.database.cache_client import CacheDatabaseClient
from hermes.api.database.relation_client import RelationalDatabaseClient
from hermes.api.database.client_base import BaseRequest

# Configure logger
logger = logging.getLogger(__name__)


class DatabaseClient:
    """
    Client for interacting with Hermes database services.
    
    This class provides a unified interface for Tekton components to
    access database services provided by Hermes.
    """
    
    def __init__(self,
                endpoint: str = None,
                use_mcp: bool = True,
                component_id: str = None):
        """
        Initialize the database client.
        
        Args:
            endpoint: Endpoint for database services (defaults to environment variable or localhost)
            use_mcp: Whether to use the MCP protocol (True) or direct API calls (False)
            component_id: Component identifier for client-specific operations
        """
        self.component_id = component_id
        self.use_mcp = use_mcp
        
        # Set default endpoint based on MCP mode
        if endpoint:
            self.endpoint = endpoint
        elif use_mcp:
            self.endpoint = os.environ.get("HERMES_DB_MCP_ENDPOINT", "http://localhost:8002")
        else:
            self.endpoint = os.environ.get("HERMES_DB_API_ENDPOINT", "http://localhost:8000/api")
        
        # Create the request handler
        self.request_handler = BaseRequest(
            endpoint=self.endpoint,
            use_mcp=self.use_mcp,
            component_id=self.component_id
        )
        
        # Initialize database-specific clients
        self.vector = VectorDatabaseClient(self.request_handler)
        self.kv = KeyValueDatabaseClient(self.request_handler)
        self.graph = GraphDatabaseClient(self.request_handler)
        self.document = DocumentDatabaseClient(self.request_handler)
        self.cache = CacheDatabaseClient(self.request_handler)
        self.sql = RelationalDatabaseClient(self.request_handler)
        
        logger.info(f"Database client initialized with endpoint {self.endpoint}, MCP mode: {use_mcp}")
    
    # Vector database operations - direct methods for backwards compatibility
    
    async def vector_store(self, **kwargs):
        """Store vectors in the database."""
        return await self.vector.store(**kwargs)
    
    async def vector_search(self, **kwargs):
        """Search for similar vectors."""
        return await self.vector.search(**kwargs)
    
    async def vector_delete(self, **kwargs):
        """Delete vectors from the database."""
        return await self.vector.delete(**kwargs)
    
    # Key-value database operations - direct methods for backwards compatibility
    
    async def kv_set(self, **kwargs):
        """Set a key-value pair."""
        return await self.kv.set(**kwargs)
    
    async def kv_get(self, **kwargs):
        """Get a value by key."""
        return await self.kv.get(**kwargs)
    
    async def kv_delete(self, **kwargs):
        """Delete a key-value pair."""
        return await self.kv.delete(**kwargs)
    
    # Graph database operations - direct methods for backwards compatibility
    
    async def graph_add_node(self, **kwargs):
        """Add a node to the graph."""
        return await self.graph.add_node(**kwargs)
    
    async def graph_add_relationship(self, **kwargs):
        """Add a relationship between nodes."""
        return await self.graph.add_relationship(**kwargs)
    
    async def graph_query(self, **kwargs):
        """Execute a graph query."""
        return await self.graph.query(**kwargs)
    
    # Document database operations - direct methods for backwards compatibility
    
    async def document_insert(self, **kwargs):
        """Insert a document."""
        return await self.document.insert(**kwargs)
    
    async def document_find(self, **kwargs):
        """Find documents matching a query."""
        return await self.document.find(**kwargs)
    
    async def document_update(self, **kwargs):
        """Update documents matching a query."""
        return await self.document.update(**kwargs)
    
    # Cache operations - direct methods for backwards compatibility
    
    async def cache_set(self, **kwargs):
        """Set a value in the cache."""
        return await self.cache.set(**kwargs)
    
    async def cache_get(self, **kwargs):
        """Get a value from the cache."""
        return await self.cache.get(**kwargs)
    
    # SQL operations - direct methods for backwards compatibility
    
    async def sql_execute(self, **kwargs):
        """Execute an SQL query."""
        return await self.sql.execute(**kwargs)