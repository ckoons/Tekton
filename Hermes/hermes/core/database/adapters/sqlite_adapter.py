"""
SQLite Database Adapter - Implementation for SQLite relational database.

This module provides a concrete implementation of the RelationalDatabaseAdapter
interface for SQLite, supporting all SQL operations with async/await.
"""

import os
import json
import aiosqlite
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from hermes.core.database.adapters.relational import RelationalDatabaseAdapter
from hermes.core.database.database_types import DatabaseBackend

logger = logging.getLogger("hermes.database.sqlite")


class SQLiteAdapter(RelationalDatabaseAdapter):
    """
    SQLite adapter for relational database operations.
    
    Provides full SQL support with transactions, schema management,
    and prepared statements. Uses aiosqlite for async operations.
    """
    
    def __init__(self, namespace: str = "default", config: Optional[Dict[str, Any]] = None):
        """
        Initialize SQLite adapter.
        
        Args:
            namespace: Namespace for data isolation
            config: Optional configuration (db_path, etc.)
        """
        self.namespace = namespace
        self.config = config or {}
        
        # Set database path - use namespace-specific file
        base_path = self.config.get('db_path', '/tmp/tekton/hermes/sqlite')
        os.makedirs(base_path, exist_ok=True)
        self.db_path = Path(base_path) / f"{namespace}.db"
        
        self.connection = None
        self.transaction_active = False
        
        logger.info(f"SQLite adapter initialized for namespace '{namespace}' at {self.db_path}")
    
    @property
    def backend(self) -> DatabaseBackend:
        """Get the database backend."""
        return DatabaseBackend.SQLITE
    
    async def is_connected(self) -> bool:
        """
        Check if connected to database.
        
        Returns:
            True if connected
        """
        return self.connection is not None
    
    async def connect(self) -> bool:
        """
        Connect to SQLite database.
        
        Returns:
            True if connection successful
        """
        try:
            if self.connection:
                await self.disconnect()
            
            # Create connection with row factory for dict results
            self.connection = await aiosqlite.connect(
                self.db_path,
                isolation_level=None  # Autocommit mode by default
            )
            self.connection.row_factory = aiosqlite.Row
            
            # Enable foreign keys and WAL mode for better concurrency
            await self.connection.execute("PRAGMA foreign_keys = ON")
            await self.connection.execute("PRAGMA journal_mode = WAL")
            
            # Create metadata table if it doesn't exist
            await self._create_metadata_table()
            
            logger.info(f"Connected to SQLite database at {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from SQLite database.
        
        Returns:
            True if disconnection successful
        """
        try:
            if self.connection:
                await self.connection.close()
                self.connection = None
                logger.info("Disconnected from SQLite database")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from SQLite: {e}")
            return False
    
    async def execute(self, query: str, params: Optional[List[Any]] = None) -> Any:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            
        Returns:
            Query results (list of dicts for SELECT, rowcount for others)
        """
        if not self.connection:
            await self.connect()
        
        try:
            cursor = await self.connection.execute(query, params or [])
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                rows = await cursor.fetchall()
                # Convert Row objects to dicts
                return [dict(row) for row in rows]
            else:
                await self.connection.commit()
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"Error executing query: {e}\nQuery: {query}\nParams: {params}")
            raise
    
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
        if not self.connection:
            await self.connect()
        
        results = []
        params_list = params_list or [[] for _ in queries]
        
        try:
            for query, params in zip(queries, params_list):
                result = await self.execute(query, params)
                results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error executing batch queries: {e}")
            raise
    
    async def begin_transaction(self) -> bool:
        """
        Begin a transaction.
        
        Returns:
            True if transaction started successfully
        """
        if not self.connection:
            await self.connect()
        
        try:
            await self.connection.execute("BEGIN")
            self.transaction_active = True
            logger.debug("Transaction started")
            return True
        except Exception as e:
            logger.error(f"Error beginning transaction: {e}")
            return False
    
    async def commit_transaction(self) -> bool:
        """
        Commit the current transaction.
        
        Returns:
            True if commit successful
        """
        if not self.transaction_active:
            logger.warning("No active transaction to commit")
            return False
        
        try:
            await self.connection.commit()
            self.transaction_active = False
            logger.debug("Transaction committed")
            return True
        except Exception as e:
            logger.error(f"Error committing transaction: {e}")
            return False
    
    async def rollback_transaction(self) -> bool:
        """
        Rollback the current transaction.
        
        Returns:
            True if rollback successful
        """
        if not self.transaction_active:
            logger.warning("No active transaction to rollback")
            return False
        
        try:
            await self.connection.rollback()
            self.transaction_active = False
            logger.debug("Transaction rolled back")
            return True
        except Exception as e:
            logger.error(f"Error rolling back transaction: {e}")
            return False
    
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
        if not self.connection:
            await self.connect()
        
        try:
            # Build column definitions
            col_defs = []
            for col_name, col_type in columns.items():
                col_def = f"{col_name} {col_type}"
                if col_name == primary_key:
                    col_def += " PRIMARY KEY"
                col_defs.append(col_def)
            
            # Build CREATE TABLE query
            existence = "IF NOT EXISTS " if if_not_exists else ""
            query = f"CREATE TABLE {existence}{table_name} ({', '.join(col_defs)})"
            
            await self.connection.execute(query)
            await self.connection.commit()
            
            logger.info(f"Created table '{table_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error creating table '{table_name}': {e}")
            return False
    
    async def drop_table(self, table_name: str, if_exists: bool = True) -> bool:
        """
        Drop a database table.
        
        Args:
            table_name: Name of the table to drop
            if_exists: Whether to use IF EXISTS
            
        Returns:
            True if table dropped successfully
        """
        if not self.connection:
            await self.connect()
        
        try:
            existence = "IF EXISTS " if if_exists else ""
            query = f"DROP TABLE {existence}{table_name}"
            
            await self.connection.execute(query)
            await self.connection.commit()
            
            logger.info(f"Dropped table '{table_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error dropping table '{table_name}': {e}")
            return False
    
    # Additional utility methods specific to SQLite
    
    async def _create_metadata_table(self):
        """Create metadata table for tracking schema versions and info."""
        await self.create_table(
            "_hermes_metadata",
            {
                "key": "TEXT",
                "value": "TEXT",
                "created_at": "TIMESTAMP",
                "updated_at": "TIMESTAMP"
            },
            primary_key="key"
        )
        
        # Store adapter info
        await self.execute(
            """INSERT OR REPLACE INTO _hermes_metadata (key, value, created_at, updated_at)
               VALUES (?, ?, ?, ?)""",
            ["adapter_type", "sqlite", datetime.now(), datetime.now()]
        )
        await self.execute(
            """INSERT OR REPLACE INTO _hermes_metadata (key, value, created_at, updated_at)
               VALUES (?, ?, ?, ?)""",
            ["namespace", self.namespace, datetime.now(), datetime.now()]
        )
    
    async def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists
        """
        result = await self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            [table_name]
        )
        return len(result) > 0
    
    async def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get schema information for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column definitions
        """
        return await self.execute(f"PRAGMA table_info({table_name})")
    
    async def vacuum(self) -> bool:
        """
        Vacuum the database to reclaim space.
        
        Returns:
            True if vacuum successful
        """
        try:
            await self.connection.execute("VACUUM")
            logger.info("Database vacuumed successfully")
            return True
        except Exception as e:
            logger.error(f"Error vacuuming database: {e}")
            return False