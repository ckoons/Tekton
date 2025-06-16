"""
Relational Database Adapter - Interface for relational database interactions.

This module defines the interface for relational database operations,
supporting SQL queries, transactions, and schema management.
"""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Union

from hermes.core.database.database_types import DatabaseType
from hermes.core.database.adapters.base import DatabaseAdapter


class RelationalDatabaseAdapter(DatabaseAdapter):
    """
    Adapter for relational databases.
    
    This class provides methods for executing SQL queries,
    with support for transactions and schema management.
    """
    
    @property
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.RELATION
    
    @abstractmethod
    async def execute(self,
                    query: str,
                    params: Optional[List[Any]] = None) -> Any:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            
        Returns:
            Query results
        """
        pass
    
    @abstractmethod
    async def execute_batch(self,
                          queries: List[str],
                          params_list: Optional[List[List[Any]]] = None) -> List[Any]:
        """
        Execute multiple SQL queries.
        
        Args:
            queries: List of SQL queries to execute
            params_list: Optional list of query parameters
            
        Returns:
            List of query results
        """
        pass
    
    @abstractmethod
    async def begin_transaction(self) -> bool:
        """
        Begin a transaction.
        
        Returns:
            True if transaction started successfully
        """
        pass
    
    @abstractmethod
    async def commit_transaction(self) -> bool:
        """
        Commit the current transaction.
        
        Returns:
            True if commit successful
        """
        pass
    
    @abstractmethod
    async def rollback_transaction(self) -> bool:
        """
        Rollback the current transaction.
        
        Returns:
            True if rollback successful
        """
        pass
    
    @abstractmethod
    async def create_table(self,
                         table_name: str,
                         columns: Dict[str, str],
                         primary_key: Optional[str] = None,
                         if_not_exists: bool = True) -> bool:
        """
        Create a database table.
        
        Args:
            table_name: Name of the table to create
            columns: Dictionary mapping column names to types
            primary_key: Optional primary key column
            if_not_exists: Whether to use IF NOT EXISTS
            
        Returns:
            True if table created successfully
        """
        pass
    
    @abstractmethod
    async def drop_table(self,
                       table_name: str,
                       if_exists: bool = True) -> bool:
        """
        Drop a database table.
        
        Args:
            table_name: Name of the table to drop
            if_exists: Whether to use IF EXISTS
            
        Returns:
            True if table dropped successfully
        """
        pass