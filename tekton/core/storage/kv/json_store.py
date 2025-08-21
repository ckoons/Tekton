"""
JSON-based key-value storage adapter for Tekton.

This module provides a simple file-based implementation of the BaseKVStorage
interface using JSON for persistence.
"""

import os
from shared.env import TektonEnviron
import json
import logging
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Union
from datetime import datetime

from tekton.core.storage.base import BaseKVStorage, StorageNamespace

# Configure logger
logger = logging.getLogger(__name__)

class JsonKVStore(BaseKVStorage):
    """
    JSON file-based implementation of BaseKVStorage.
    
    Provides simple key-value storage capabilities using JSON files
    for persistence.
    """
    
    def __init__(
        self,
        namespace: str = "default",
        data_path: Optional[str] = None,
        filename: Optional[str] = None,
        auto_flush: bool = True,
        cache_size: int = 10000,
        **kwargs
    ):
        """
        Initialize the JSON key-value store.
        
        Args:
            namespace: Namespace for the KV store
            data_path: Directory to store data files
            filename: Specific filename for the JSON file
            auto_flush: Whether to automatically flush to disk on changes
            cache_size: Maximum number of items to keep in memory cache
            **kwargs: Additional configuration parameters
        """
        self.namespace = StorageNamespace(namespace)
        
        # Define data path
        self.data_path = data_path or TektonEnviron.get(
            "TEKTON_KV_DB_PATH", 
            os.path.expanduser(f"~/.tekton/kv_stores/{namespace}")
        )
        
        # Define filename
        self.filename = filename or f"{namespace}.json"
        self.file_path = os.path.join(self.data_path, self.filename)
        
        # Set options
        self.auto_flush = auto_flush
        self.cache_size = cache_size
        
        # State
        self.data = {}
        self.metadata = {
            "namespace": namespace,
            "created_at": None,
            "updated_at": None,
            "item_count": 0
        }
        self.write_lock = threading.RLock()
        self._initialized = False
        self._flush_scheduled = False
        
    async def initialize(self) -> None:
        """
        Initialize the JSON KV storage backend.
        
        This method handles file creation/loading.
        """
        if self._initialized:
            return
            
        logger.info(f"Initializing JSON KV store with namespace: {self.namespace.namespace}")
        
        try:
            # Create directories if they don't exist
            os.makedirs(self.data_path, exist_ok=True)
            
            # Load data if file exists
            if os.path.exists(self.file_path):
                await self._load_data()
            else:
                # Initialize with empty data
                self.data = {}
                self.metadata["created_at"] = datetime.now().isoformat()
                self.metadata["updated_at"] = self.metadata["created_at"]
                self.metadata["item_count"] = 0
                
                # Save initial file
                await self._save_data()
                
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing JSON KV store: {e}")
            raise
            
    async def _load_data(self) -> None:
        """Load data from JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                
            self.data = data.get("data", {})
            self.metadata = data.get("metadata", {
                "namespace": self.namespace.namespace,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "item_count": len(self.data)
            })
            
            # Update item count if not accurate
            if self.metadata.get("item_count", 0) != len(self.data):
                self.metadata["item_count"] = len(self.data)
                
            logger.info(f"Loaded {len(self.data)} items from JSON store")
            
        except Exception as e:
            logger.error(f"Error loading data from {self.file_path}: {e}")
            self.data = {}
            self.metadata = {
                "namespace": self.namespace.namespace,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "item_count": 0
            }
            
    async def _save_data(self) -> None:
        """Save data to JSON file."""
        with self.write_lock:
            try:
                # Update metadata
                self.metadata["updated_at"] = datetime.now().isoformat()
                self.metadata["item_count"] = len(self.data)
                
                # Prepare data structure
                save_data = {
                    "data": self.data,
                    "metadata": self.metadata
                }
                
                # Write to temporary file first to prevent corruption
                temp_path = f"{self.file_path}.tmp"
                with open(temp_path, 'w') as f:
                    json.dump(save_data, f, indent=2)
                    
                # Atomic replacement
                os.replace(temp_path, self.file_path)
                
                logger.debug(f"Saved {len(self.data)} items to JSON store")
                
            except Exception as e:
                logger.error(f"Error saving data to {self.file_path}: {e}")
                raise
            
    async def _schedule_flush(self) -> None:
        """Schedule a flush to disk with debouncing."""
        if self._flush_scheduled or not self.auto_flush:
            return
            
        self._flush_scheduled = True
        
        # Use asyncio to schedule a delayed flush
        async def delayed_flush():
            await asyncio.sleep(0.5)  # Debounce for 500ms
            await self._save_data()
            self._flush_scheduled = False
            
        asyncio.create_task(delayed_flush())
    
    async def finalize(self) -> None:
        """
        Finalize and clean up the JSON storage backend.
        
        This method handles flushing unsaved changes to disk.
        """
        logger.info("Finalizing JSON KV store")
        
        if self._initialized:
            await self._save_data()
            
        self._initialized = False
        logger.info("JSON KV store finalized")
    
    async def drop(self) -> Dict[str, str]:
        """
        Drop all data from storage.
        
        Returns:
            Dictionary with status and message
        """
        logger.warning(f"Dropping all data for namespace: {self.namespace.namespace}")
        
        with self.write_lock:
            try:
                # Clear data
                self.data = {}
                
                # Update metadata
                self.metadata["updated_at"] = datetime.now().isoformat()
                self.metadata["item_count"] = 0
                
                # Save empty data
                await self._save_data()
                
                return {
                    "status": "success",
                    "message": f"All data for namespace {self.namespace.namespace} has been dropped"
                }
            except Exception as e:
                logger.error(f"Error dropping JSON KV store: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to drop data: {str(e)}"
                }
    
    async def index_done_callback(self) -> None:
        """
        Callback invoked when indexing operations are complete.
        
        For JSON store, this ensures all data is flushed to disk.
        """
        await self._save_data()
    
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get value by ID.
        
        Args:
            id: The key to retrieve
            
        Returns:
            Value dictionary or None if not found
        """
        if not self._initialized:
            logger.error("JSON KV store not initialized")
            return None
            
        return self.data.get(id)
    
    async def get_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple values by IDs.
        
        Args:
            ids: List of keys to retrieve
            
        Returns:
            List of value dictionaries that were found
        """
        if not self._initialized:
            logger.error("JSON KV store not initialized")
            return []
            
        result = []
        for id in ids:
            value = self.data.get(id)
            if value is not None:
                result.append(value)
                
        return result
    
    async def filter_keys(self, keys: Set[str]) -> Set[str]:
        """
        Find which keys don't exist in storage.
        
        Args:
            keys: Set of keys to check
            
        Returns:
            Set of keys that don't exist in storage
        """
        if not self._initialized:
            logger.error("JSON KV store not initialized")
            return keys
            
        return {key for key in keys if key not in self.data}
    
    async def upsert(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Insert or update data.
        
        Args:
            data: Dictionary mapping keys to value dictionaries
        """
        if not self._initialized:
            logger.error("JSON KV store not initialized")
            raise RuntimeError("JSON KV store not initialized")
            
        if not data:
            return
            
        with self.write_lock:
            # Update data
            self.data.update(data)
            
            # Check if we need to trim cache
            if self.cache_size > 0 and len(self.data) > self.cache_size:
                # Get keys sorted by age (if available) or just take arbitrary ones
                keys_to_remove = list(self.data.keys())[:(len(self.data) - self.cache_size)]
                for key in keys_to_remove:
                    del self.data[key]
                    
            # Schedule a flush to disk
            await self._schedule_flush()
    
    async def delete(self, ids: List[str]) -> None:
        """
        Delete data by IDs.
        
        Args:
            ids: List of keys to delete
        """
        if not self._initialized:
            logger.error("JSON KV store not initialized")
            raise RuntimeError("JSON KV store not initialized")
            
        if not ids:
            return
            
        with self.write_lock:
            # Delete keys
            for id in ids:
                if id in self.data:
                    del self.data[id]
                    
            # Schedule a flush to disk
            await self._schedule_flush()
    
    async def clear_cache(self, cache_types: Optional[List[str]] = None) -> bool:
        """
        Clear cached data.
        
        Args:
            cache_types: Optional list of cache types to clear
            
        Returns:
            True if cache was cleared successfully, False otherwise
        """
        # For JSON store, cache types are not supported
        # Simply reload the data from disk
        try:
            await self._load_data()
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False