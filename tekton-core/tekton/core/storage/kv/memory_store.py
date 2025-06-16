"""
In-memory key-value storage adapter for Tekton.

This module provides an in-memory implementation of the BaseKVStorage
interface, suitable for testing or temporary storage.
"""

import logging
import copy
from typing import Dict, List, Any, Optional, Set, Union
from datetime import datetime

from tekton.core.storage.base import BaseKVStorage, StorageNamespace

# Configure logger
logger = logging.getLogger(__name__)

class MemoryKVStore(BaseKVStorage):
    """
    In-memory implementation of BaseKVStorage.
    
    Provides key-value storage capabilities using Python dictionaries.
    Useful for testing or temporary storage where persistence is not required.
    """
    
    def __init__(
        self,
        namespace: str = "default",
        cache_size: int = 10000,
        **kwargs
    ):
        """
        Initialize the in-memory KV store.
        
        Args:
            namespace: Namespace for the KV store
            cache_size: Maximum number of items to store
            **kwargs: Additional configuration parameters
        """
        self.namespace = StorageNamespace(namespace)
        self.cache_size = cache_size
        
        # State
        self.data = {}
        self.metadata = {
            "namespace": namespace,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "item_count": 0
        }
        self._initialized = False
        
    async def initialize(self) -> None:
        """
        Initialize the memory KV storage backend.
        """
        if self._initialized:
            return
            
        logger.info(f"Initializing memory KV store with namespace: {self.namespace.namespace}")
        self._initialized = True
        
    async def finalize(self) -> None:
        """
        Finalize and clean up the memory KV storage backend.
        """
        logger.info("Finalizing memory KV store")
        self._initialized = False
        logger.info("Memory KV store finalized")
    
    async def drop(self) -> Dict[str, str]:
        """
        Drop all data from storage.
        
        Returns:
            Dictionary with status and message
        """
        logger.warning(f"Dropping all data for namespace: {self.namespace.namespace}")
        
        try:
            # Clear data
            self.data = {}
            self.metadata["updated_at"] = datetime.now().isoformat()
            self.metadata["item_count"] = 0
            
            return {
                "status": "success",
                "message": f"All data for namespace {self.namespace.namespace} has been dropped"
            }
        except Exception as e:
            logger.error(f"Error dropping memory KV store: {e}")
            return {
                "status": "error",
                "message": f"Failed to drop data: {str(e)}"
            }
    
    async def index_done_callback(self) -> None:
        """
        Callback invoked when indexing operations are complete.
        
        No-op for memory KV store.
        """
        pass
    
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get value by ID.
        
        Args:
            id: The key to retrieve
            
        Returns:
            Value dictionary or None if not found
        """
        if not self._initialized:
            logger.error("Memory KV store not initialized")
            return None
            
        # Return a copy to avoid modifying internal state
        value = self.data.get(id)
        return copy.deepcopy(value) if value is not None else None
    
    async def get_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple values by IDs.
        
        Args:
            ids: List of keys to retrieve
            
        Returns:
            List of value dictionaries that were found
        """
        if not self._initialized:
            logger.error("Memory KV store not initialized")
            return []
            
        result = []
        for id in ids:
            value = self.data.get(id)
            if value is not None:
                result.append(copy.deepcopy(value))
                
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
            logger.error("Memory KV store not initialized")
            return keys
            
        return {key for key in keys if key not in self.data}
    
    async def upsert(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Insert or update data.
        
        Args:
            data: Dictionary mapping keys to value dictionaries
        """
        if not self._initialized:
            logger.error("Memory KV store not initialized")
            raise RuntimeError("Memory KV store not initialized")
            
        if not data:
            return
            
        # Update data (using deep copy to avoid reference issues)
        for key, value in data.items():
            self.data[key] = copy.deepcopy(value)
            
        # Check if we need to trim cache
        if self.cache_size > 0 and len(self.data) > self.cache_size:
            # Simple LRU: just remove oldest keys based on insertion order
            keys_to_remove = list(self.data.keys())[:(len(self.data) - self.cache_size)]
            for key in keys_to_remove:
                del self.data[key]
                
        # Update metadata
        self.metadata["updated_at"] = datetime.now().isoformat()
        self.metadata["item_count"] = len(self.data)
    
    async def delete(self, ids: List[str]) -> None:
        """
        Delete data by IDs.
        
        Args:
            ids: List of keys to delete
        """
        if not self._initialized:
            logger.error("Memory KV store not initialized")
            raise RuntimeError("Memory KV store not initialized")
            
        if not ids:
            return
            
        # Delete keys
        for id in ids:
            if id in self.data:
                del self.data[id]
                
        # Update metadata
        self.metadata["updated_at"] = datetime.now().isoformat()
        self.metadata["item_count"] = len(self.data)
    
    async def clear_cache(self, cache_types: Optional[List[str]] = None) -> bool:
        """
        Clear cached data.
        
        Args:
            cache_types: Optional list of cache types to clear
            
        Returns:
            True if cache was cleared successfully, False otherwise
        """
        # Memory store is already fully in-memory, so we just return True
        return True