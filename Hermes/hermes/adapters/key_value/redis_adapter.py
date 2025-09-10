"""
Redis Key-Value Adapter - High-performance key-value storage using Redis.

This module provides a KeyValueDatabaseAdapter implementation that uses Redis
for fast and efficient key-value operations with optional expiration.
"""

import os
import json
import time
import asyncio
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

import redis.asyncio as redis

from hermes.core.logging import get_logger
from hermes.core.database.adapters.key_value import KeyValueDatabaseAdapter
from hermes.core.database.database_types import DatabaseBackend

# Logger for this module
logger = get_logger("hermes.adapters.key_value.redis")


class RedisKeyValueAdapter(KeyValueDatabaseAdapter):
    """
    Redis key-value database adapter.
    
    This adapter provides fast key-value operations using Redis,
    with support for expiration and batch operations.
    """
    
    def __init__(self, 
                namespace: str,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Redis key-value adapter.
        
        Args:
            namespace: Namespace for data isolation
            config: Optional configuration parameters
        """
        super().__init__(namespace, config)
        
        # Redis connection settings
        self.host = self.config.get("host", "localhost")
        self.port = self.config.get("port", 6379)
        self.db = self.config.get("db", 0)
        self.password = self.config.get("password")
        
        # Namespace will be used as a prefix for all keys
        self.namespace_prefix = f"{namespace}:"
        
        # Client instance
        self.client = None
        
        # Internal state
        self._connected = False
    
    @property
    def backend(self) -> DatabaseBackend:
        """Get the database backend."""
        return DatabaseBackend.REDIS
    
    async def connect(self) -> bool:
        """
        Connect to the database.
        
        Returns:
            True if connection successful
        """
        try:
            # Create Redis client
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=False  # We'll handle encoding/decoding ourselves
            )
            
            # Verify connection
            await self.client.ping()
            
            self._connected = True
            
            logger.info(f"Connected to Redis key-value database for namespace {self.namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Redis: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the database.
        
        Returns:
            True if disconnection successful
        """
        try:
            if self.client:
                await self.client.close()
                self.client = None
            
            self._connected = False
            
            logger.info(f"Disconnected from Redis key-value database for namespace {self.namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """
        Check if connected to the database.
        
        Returns:
            True if connected
        """
        if not self._connected or not self.client:
            return False
        
        try:
            # Check connection
            await self.client.ping()
            return True
        except:
            self._connected = False
            return False
    
    async def set(self,
                key: str,
                value: Any,
                expiration: Optional[int] = None) -> bool:
        """
        Set a key-value pair.
        
        Args:
            key: The key
            value: The value
            expiration: Optional expiration time in seconds
            
        Returns:
            True if operation successful
        """
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        try:
            # Add namespace prefix to key
            prefixed_key = f"{self.namespace_prefix}{key}"
            
            # Serialize value
            serialized = self._serialize(value)
            
            # Store in Redis
            if expiration:
                await self.client.setex(prefixed_key, expiration, serialized)
            else:
                await self.client.set(prefixed_key, serialized)
            
            logger.debug(f"Set key {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting key: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value by key.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value if found, None otherwise
        """
        if not self._connected:
            logger.error("Not connected to database")
            return None
        
        try:
            # Add namespace prefix to key
            prefixed_key = f"{self.namespace_prefix}{key}"
            
            # Get from Redis
            serialized = await self.client.get(prefixed_key)
            
            if serialized is None:
                logger.debug(f"Key {key} not found")
                return None
            
            # Deserialize value
            value = self._deserialize(serialized)
            
            logger.debug(f"Retrieved key {key}")
            return value
            
        except Exception as e:
            logger.error(f"Error getting key: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """
        Delete a key-value pair.
        
        Args:
            key: The key to delete
            
        Returns:
            True if deletion successful
        """
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        try:
            # Add namespace prefix to key
            prefixed_key = f"{self.namespace_prefix}{key}"
            
            # Delete from Redis
            result = await self.client.delete(prefixed_key)
            
            if result > 0:
                logger.debug(f"Deleted key {key}")
                return True
            else:
                logger.debug(f"Key {key} not found")
                return False
            
        except Exception as e:
            logger.error(f"Error deleting key: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists.
        
        Args:
            key: The key to check
            
        Returns:
            True if the key exists
        """
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        try:
            # Add namespace prefix to key
            prefixed_key = f"{self.namespace_prefix}{key}"
            
            # Check in Redis
            result = await self.client.exists(prefixed_key)
            
            exists = result > 0
            logger.debug(f"Key {key} {'exists' if exists else 'does not exist'}")
            return exists
            
        except Exception as e:
            logger.error(f"Error checking key existence: {e}")
            return False
    
    async def set_batch(self,
                       items: Dict[str, Any],
                       expiration: Optional[int] = None) -> bool:
        """
        Set multiple key-value pairs.
        
        Args:
            items: Dictionary of key-value pairs
            expiration: Optional expiration time in seconds
            
        Returns:
            True if operation successful
        """
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        if not items:
            return True
        
        try:
            # Use pipeline for better performance
            async with self.client.pipeline() as pipe:
                for key, value in items.items():
                    # Add namespace prefix to key
                    prefixed_key = f"{self.namespace_prefix}{key}"
                    
                    # Serialize value
                    serialized = self._serialize(value)
                    
                    # Add to pipeline
                    if expiration:
                        pipe.setex(prefixed_key, expiration, serialized)
                    else:
                        pipe.set(prefixed_key, serialized)
                
                # Execute all commands
                await pipe.execute()
            
            logger.debug(f"Set {len(items)} keys in batch")
            return True
            
        except Exception as e:
            logger.error(f"Error setting batch keys: {e}")
            return False
    
    async def get_batch(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values by keys.
        
        Args:
            keys: List of keys to retrieve
            
        Returns:
            Dictionary of key-value pairs for found keys
        """
        if not self._connected:
            logger.error("Not connected to database")
            return {}
        
        if not keys:
            return {}
        
        try:
            # Add namespace prefix to all keys
            prefixed_keys = [f"{self.namespace_prefix}{key}" for key in keys]
            
            # Get multiple values
            values = await self.client.mget(prefixed_keys)
            
            # Create result dictionary
            result = {}
            
            for i, key in enumerate(keys):
                if values[i] is not None:
                    # Deserialize value
                    result[key] = self._deserialize(values[i])
            
            logger.debug(f"Retrieved {len(result)} keys in batch")
            return result
            
        except Exception as e:
            logger.error(f"Error getting batch keys: {e}")
            return {}
    
    async def delete_batch(self, keys: List[str]) -> bool:
        """
        Delete multiple key-value pairs.
        
        Args:
            keys: List of keys to delete
            
        Returns:
            True if operation successful
        """
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        if not keys:
            return True
        
        try:
            # Add namespace prefix to all keys
            prefixed_keys = [f"{self.namespace_prefix}{key}" for key in keys]
            
            # Delete multiple keys
            result = await self.client.delete(*prefixed_keys)
            
            logger.debug(f"Deleted {result} keys in batch")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting batch keys: {e}")
            return False
    
    async def clear_namespace(self) -> bool:
        """
        Clear all keys in the namespace.
        
        Returns:
            True if operation successful
        """
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        try:
            # Get all keys with namespace prefix
            cursor = b"0"
            all_keys = []
            
            while cursor:
                cursor, keys = await self.client.scan(
                    cursor=cursor,
                    match=f"{self.namespace_prefix}*",
                    count=1000
                )
                
                if keys:
                    all_keys.extend(keys)
                
                if cursor == b"0":
                    break
            
            # Delete all keys
            if all_keys:
                await self.client.delete(*all_keys)
            
            logger.debug(f"Cleared {len(all_keys)} keys in namespace {self.namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing namespace: {e}")
            return False
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize a value to bytes."""
        try:
            return pickle.dumps(value)
        except Exception as e:
            logger.error(f"Error serializing value: {e}")
            raise
    
    def _deserialize(self, serialized: bytes) -> Any:
        """Deserialize bytes to a value."""
        try:
            return pickle.loads(serialized)
        except Exception as e:
            logger.error(f"Error deserializing value: {e}")
            raise