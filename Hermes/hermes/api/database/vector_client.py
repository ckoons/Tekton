"""
Vector Database Client - Client interface for vector database operations.

This module provides a client for accessing vector database services.
"""

from typing import Dict, List, Any, Optional, Union
from hermes.api.database.client_base import BaseRequest


class VectorDatabaseClient:
    """
    Client for interacting with vector database services.
    
    This class provides methods for vector storage, search, and deletion.
    """
    
    def __init__(self, request_handler: BaseRequest):
        """
        Initialize the vector database client.
        
        Args:
            request_handler: Base request handler for API communication
        """
        self.request_handler = request_handler
    
    async def store(self,
                  vectors: List[List[float]],
                  metadatas: Optional[List[Dict[str, Any]]] = None,
                  ids: Optional[List[str]] = None,
                  namespace: str = "default",
                  backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Store vectors in the database.
        
        Args:
            vectors: List of vector embeddings
            metadatas: Optional list of metadata for each vector
            ids: Optional list of IDs for each vector
            namespace: Namespace for the vectors
            backend: Optional specific backend to use
            
        Returns:
            Result of the storage operation
        """
        parameters = {
            "vectors": vectors,
            "namespace": namespace
        }
        
        if metadatas:
            parameters["metadatas"] = metadatas
        if ids:
            parameters["ids"] = ids
        if backend:
            parameters["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="vector_store",
            api_path=f"vector/{namespace}/store",
            parameters=parameters
        )
    
    async def search(self,
                   query_vector: List[float],
                   top_k: int = 5,
                   namespace: str = "default",
                   filter_dict: Optional[Dict[str, Any]] = None,
                   backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Vector to search for
            top_k: Number of results to return
            namespace: Namespace to search in
            filter_dict: Optional metadata filter
            backend: Optional specific backend to use
            
        Returns:
            Search results with scores and metadata
        """
        parameters = {
            "query_vector": query_vector,
            "top_k": top_k,
            "namespace": namespace
        }
        
        if filter_dict:
            parameters["filter"] = filter_dict
        if backend:
            parameters["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="vector_search",
            api_path=f"vector/{namespace}/search",
            parameters=parameters
        )
    
    async def delete(self,
                   ids: List[str],
                   namespace: str = "default",
                   backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete vectors from the database.
        
        Args:
            ids: List of vector IDs to delete
            namespace: Namespace containing the vectors
            backend: Optional specific backend to use
            
        Returns:
            Result of the delete operation
        """
        parameters = {
            "ids": ids,
            "namespace": namespace
        }
        
        if backend:
            parameters["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="vector_delete",
            api_path=f"vector/{namespace}/delete",
            method="DELETE",
            parameters=parameters
        )