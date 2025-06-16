"""
Cache Database Client - Client interface for cache database operations.

This module provides a client for accessing cache database services.
"""

from typing import Dict, List, Any, Optional, Union
from hermes.api.database.client_base import BaseRequest


class CacheDatabaseClient:
    """
    Client for interacting with cache database services.
    
    This class provides methods for cache operations like setting and
    retrieving values with expiration.
    """
    
    def __init__(self, request_handler: BaseRequest):
        """
        Initialize the cache database client.
        
        Args:
            request_handler: Base request handler for API communication
        """
        self.request_handler = request_handler
    
    async def set(self,
                key: str,
                value: Any,
                ttl: int = 3600,
                namespace: str = "default",
                backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            namespace: Namespace for the data
            backend: Optional specific backend to use
            
        Returns:
            Result of the cache operation
        """
        parameters = {
            "key": key,
            "value": value,
            "ttl": ttl,
            "namespace": namespace
        }
        
        if backend:
            parameters["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="cache_set",
            api_path=f"cache/{namespace}/{key}",
            method="PUT",
            parameters=parameters
        )
    
    async def get(self,
                key: str,
                namespace: str = "default",
                backend: Optional[str] = None) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            namespace: Namespace for the data
            backend: Optional specific backend to use
            
        Returns:
            Cached value or None if not found
        """
        parameters = {
            "key": key,
            "namespace": namespace
        }
        
        if backend:
            parameters["backend"] = backend
        
        result = await self.request_handler.execute_request(
            capability="cache_get",
            api_path=f"cache/{namespace}/{key}",
            method="GET",
            parameters=parameters
        )
        
        return result.get("value")