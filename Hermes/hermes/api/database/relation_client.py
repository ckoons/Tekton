"""
Relational Database Client - Client interface for SQL database operations.

This module provides a client for accessing relational database services.
"""

from typing import Dict, List, Any, Optional, Union
from hermes.api.database.client_base import BaseRequest


class RelationalDatabaseClient:
    """
    Client for interacting with relational database services.
    
    This class provides methods for SQL operations like executing queries.
    """
    
    def __init__(self, request_handler: BaseRequest):
        """
        Initialize the relational database client.
        
        Args:
            request_handler: Base request handler for API communication
        """
        self.request_handler = request_handler
    
    async def execute(self,
                    query: str,
                    parameters: List[Any] = None,
                    namespace: str = "default",
                    backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute an SQL query.
        
        Args:
            query: SQL query
            parameters: Query parameters
            namespace: Namespace for the data
            backend: Optional specific backend to use
            
        Returns:
            Query results
        """
        request_params = {
            "query": query,
            "namespace": namespace
        }
        
        if parameters:
            request_params["parameters"] = parameters
        if backend:
            request_params["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="sql_execute",
            api_path=f"relation/{namespace}/query",
            parameters=request_params
        )