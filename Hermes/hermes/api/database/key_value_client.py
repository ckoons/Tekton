"""
Key-Value Database Client - Client interface for key-value database operations.

This module provides a client for accessing key-value database services.
"""

from typing import Dict, List, Any, Optional, Union
from hermes.api.database.client_base import BaseRequest


class KeyValueDatabaseClient:
    """
    Client for interacting with key-value database services.
    
    This class provides methods for key-value operations like set, get, and delete.
    """
    
    def __init__(self, request_handler: BaseRequest):
        """
        Initialize the key-value database client.
        
        Args:
            request_handler: Base request handler for API communication
        """
        self.request_handler = request_handler
    
    async def set(self,
                key: str,
                value: Any,
                namespace: str = "default",
                ttl: Optional[int] = None,
                backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Set a key-value pair.
        
        Args:
            key: Key to set
            value: Value to store
            namespace: Namespace for the data
            ttl: Optional time-to-live in seconds
            backend: Optional specific backend to use
            
        Returns:
            Result of the set operation
        """
        parameters = {
            "key": key,
            "value": value,
            "namespace": namespace
        }
        
        if ttl:
            parameters["ttl"] = ttl
        if backend:
            parameters["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="kv_set",
            api_path=f"kv/{namespace}/{key}",
            method="PUT",
            parameters=parameters
        )
    
    async def get(self,
                key: str,
                namespace: str = "default",
                backend: Optional[str] = None) -> Any:
        """
        Get a value by key.
        
        Args:
            key: Key to retrieve
            namespace: Namespace for the data
            backend: Optional specific backend to use
            
        Returns:
            Retrieved value or None if not found
        """
        parameters = {
            "key": key,
            "namespace": namespace
        }
        
        if backend:
            parameters["backend"] = backend
        
        result = await self.request_handler.execute_request(
            capability="kv_get",
            api_path=f"kv/{namespace}/{key}",
            method="GET",
            parameters=parameters
        )
        
        return result.get("value")
    
    async def delete(self,
                   key: str,
                   namespace: str = "default",
                   backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a key-value pair.
        
        Args:
            key: Key to delete
            namespace: Namespace for the data
            backend: Optional specific backend to use
            
        Returns:
            Result of the delete operation
        """
        parameters = {
            "key": key,
            "namespace": namespace
        }
        
        if backend:
            parameters["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="kv_delete",
            api_path=f"kv/{namespace}/{key}",
            method="DELETE",
            parameters=parameters
        )