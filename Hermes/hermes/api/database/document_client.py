"""
Document Database Client - Client interface for document database operations.

This module provides a client for accessing document database services.
"""

from typing import Dict, List, Any, Optional, Union
from hermes.api.database.client_base import BaseRequest


class DocumentDatabaseClient:
    """
    Client for interacting with document database services.
    
    This class provides methods for document operations like inserting,
    finding, and updating documents.
    """
    
    def __init__(self, request_handler: BaseRequest):
        """
        Initialize the document database client.
        
        Args:
            request_handler: Base request handler for API communication
        """
        self.request_handler = request_handler
    
    async def insert(self,
                   collection: str,
                   document: Dict[str, Any],
                   namespace: str = "default",
                   backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Insert a document.
        
        Args:
            collection: Collection to insert into
            document: Document to insert
            namespace: Namespace for the data
            backend: Optional specific backend to use
            
        Returns:
            Result with document ID
        """
        parameters = {
            "collection": collection,
            "document": document,
            "namespace": namespace
        }
        
        if backend:
            parameters["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="document_insert",
            api_path=f"document/{namespace}/{collection}",
            parameters=parameters
        )
    
    async def find(self,
                 collection: str,
                 query: Dict[str, Any],
                 limit: int = 10,
                 namespace: str = "default",
                 backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Find documents matching a query.
        
        Args:
            collection: Collection to search in
            query: Query filter
            limit: Maximum number of results
            namespace: Namespace for the data
            backend: Optional specific backend to use
            
        Returns:
            Matching documents
        """
        parameters = {
            "collection": collection,
            "query": query,
            "limit": limit,
            "namespace": namespace
        }
        
        if backend:
            parameters["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="document_find",
            api_path=f"document/{namespace}/{collection}/find",
            parameters=parameters
        )
    
    async def update(self,
                   collection: str,
                   query: Dict[str, Any],
                   update: Dict[str, Any],
                   namespace: str = "default",
                   backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Update documents matching a query.
        
        Args:
            collection: Collection to update in
            query: Query filter
            update: Update operations
            namespace: Namespace for the data
            backend: Optional specific backend to use
            
        Returns:
            Result of the update operation
        """
        parameters = {
            "collection": collection,
            "query": query,
            "update": update,
            "namespace": namespace
        }
        
        if backend:
            parameters["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="document_update",
            api_path=f"document/{namespace}/{collection}",
            method="PUT",
            parameters=parameters
        )