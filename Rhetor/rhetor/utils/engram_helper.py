"""Engram integration for Rhetor.

This module provides helper functions and classes for integrating with Engram,
the memory system for the Tekton ecosystem.
"""

import os
from shared.env import TektonEnviron
from shared.urls import engram_url as get_engram_url
import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import aiohttp

logger = logging.getLogger(__name__)

class EngramClient:
    """Client for connecting to Engram memory service."""
    
    def __init__(
        self,
        engram_url: Optional[str] = None,
        engram_api_key: Optional[str] = None,
        offline_mode: bool = False
    ):
        """Initialize connection to Engram.
        
        Args:
            engram_url: URL for the Engram API (uses tekton_url if not provided)
            engram_api_key: API key for authentication (if required)
            offline_mode: Whether to operate in offline mode
        """
        self.engram_url = engram_url or get_engram_url()
        self.engram_api_key = engram_api_key or TektonEnviron.get("ENGRAM_API_KEY")
        self.offline_mode = offline_mode
        self.session = None
        self.connected = False
        
        # Backup storage for offline mode
        self.backup_dir = os.path.join(
            TektonEnviron.get('TEKTON_DATA_DIR', 
                          os.path.join(TektonEnviron.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')),
            'rhetor', 'engram_backup'
        )
        os.makedirs(self.backup_dir, exist_ok=True)
    
    async def connect(self) -> bool:
        """Connect to the Engram service.
        
        Returns:
            Success status
        """
        if self.offline_mode:
            logger.info("Engram client running in offline mode")
            self.connected = False
            return False
        
        if self.connected and self.session:
            return True
        
        try:
            # Create client session
            self.session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            
            # Test the connection
            async with self.session.get(f"{self.engram_url}/health") as response:
                if response.status == 200:
                    self.connected = True
                    logger.info(f"Connected to Engram at {self.engram_url}")
                    return True
                else:
                    logger.warning(f"Failed to connect to Engram: {response.status} {await response.text()}")
                    self.connected = False
                    await self.session.close()
                    self.session = None
                    return False
        
        except Exception as e:
            logger.warning(f"Error connecting to Engram: {e}")
            self.connected = False
            if self.session:
                await self.session.close()
                self.session = None
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the Engram service."""
        if self.session:
            await self.session.close()
            self.session = None
        self.connected = False
    
    async def ensure_connected(self) -> bool:
        """Ensure the client is connected.
        
        Returns:
            True if connected, False if offline or failed to connect
        """
        if self.offline_mode:
            return False
        
        if not self.connected or not self.session:
            return await self.connect()
        
        return True
    
    async def store_memory(
        self,
        namespace: str,
        key: str,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store data in Engram.
        
        Args:
            namespace: Memory namespace
            key: Memory key
            data: Data to store
            metadata: Optional metadata for the memory
            
        Returns:
            Success status
        """
        # Try to connect to Engram
        connected = await self.ensure_connected()
        
        if connected:
            # Store in Engram
            try:
                payload = {
                    "key": key,
                    "data": data,
                    "metadata": metadata or {}
                }
                
                async with self.session.post(
                    f"{self.engram_url}/memory/{namespace}",
                    json=payload
                ) as response:
                    success = response.status == 200
                    if not success:
                        logger.warning(f"Failed to store memory in Engram: {response.status} {await response.text()}")
                        # Fall back to local storage
                        await self._store_local(namespace, key, data, metadata)
                    return success
            
            except Exception as e:
                logger.warning(f"Error storing memory in Engram: {e}")
                # Fall back to local storage
                return await self._store_local(namespace, key, data, metadata)
        
        else:
            # Use local storage
            return await self._store_local(namespace, key, data, metadata)
    
    async def get_memory(
        self,
        namespace: str,
        key: str
    ) -> Optional[Any]:
        """Retrieve data from Engram.
        
        Args:
            namespace: Memory namespace
            key: Memory key
            
        Returns:
            Retrieved data or None if not found
        """
        # Try to connect to Engram
        connected = await self.ensure_connected()
        
        if connected:
            # Get from Engram
            try:
                async with self.session.get(
                    f"{self.engram_url}/memory/{namespace}/{key}"
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data")
                    elif response.status == 404:
                        # Try local storage as fallback
                        return await self._get_local(namespace, key)
                    else:
                        logger.warning(f"Failed to get memory from Engram: {response.status} {await response.text()}")
                        # Fall back to local storage
                        return await self._get_local(namespace, key)
            
            except Exception as e:
                logger.warning(f"Error getting memory from Engram: {e}")
                # Fall back to local storage
                return await self._get_local(namespace, key)
        
        else:
            # Use local storage
            return await self._get_local(namespace, key)
    
    async def delete_memory(
        self,
        namespace: str,
        key: str
    ) -> bool:
        """Delete data from Engram.
        
        Args:
            namespace: Memory namespace
            key: Memory key
            
        Returns:
            Success status
        """
        # Try to connect to Engram
        connected = await self.ensure_connected()
        
        # Delete local backup
        local_success = await self._delete_local(namespace, key)
        
        if connected:
            # Delete from Engram
            try:
                async with self.session.delete(
                    f"{self.engram_url}/memory/{namespace}/{key}"
                ) as response:
                    return response.status == 200 or response.status == 404
            
            except Exception as e:
                logger.warning(f"Error deleting memory from Engram: {e}")
                return local_success
        
        return local_success
    
    async def search_memory(
        self,
        namespace: str,
        query: str,
        limit: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search memories in Engram.
        
        Args:
            namespace: Memory namespace
            query: Search query
            limit: Maximum number of results
            metadata_filter: Optional metadata filter
            
        Returns:
            List of matching memories
        """
        # Try to connect to Engram
        connected = await self.ensure_connected()
        
        if connected:
            # Search in Engram
            try:
                params = {
                    "query": query,
                    "limit": limit
                }
                
                if metadata_filter:
                    params["metadata"] = json.dumps(metadata_filter)
                
                async with self.session.get(
                    f"{self.engram_url}/memory/{namespace}/search",
                    params=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("results", [])
                    else:
                        logger.warning(f"Failed to search memory in Engram: {response.status} {await response.text()}")
                        # Fall back to local search
                        return await self._search_local(namespace, query, limit, metadata_filter)
            
            except Exception as e:
                logger.warning(f"Error searching memory in Engram: {e}")
                # Fall back to local search
                return await self._search_local(namespace, query, limit, metadata_filter)
        
        else:
            # Use local search
            return await self._search_local(namespace, query, limit, metadata_filter)
    
    async def list_memories(
        self,
        namespace: str,
        limit: int = 100,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List memories in Engram.
        
        Args:
            namespace: Memory namespace
            limit: Maximum number of results
            metadata_filter: Optional metadata filter
            
        Returns:
            List of memory summaries
        """
        # Try to connect to Engram
        connected = await self.ensure_connected()
        
        if connected:
            # List in Engram
            try:
                params = {"limit": limit}
                
                if metadata_filter:
                    params["metadata"] = json.dumps(metadata_filter)
                
                async with self.session.get(
                    f"{self.engram_url}/memory/{namespace}",
                    params=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("memories", [])
                    else:
                        logger.warning(f"Failed to list memories in Engram: {response.status} {await response.text()}")
                        # Fall back to local list
                        return await self._list_local(namespace, limit, metadata_filter)
            
            except Exception as e:
                logger.warning(f"Error listing memories in Engram: {e}")
                # Fall back to local list
                return await self._list_local(namespace, limit, metadata_filter)
        
        else:
            # Use local list
            return await self._list_local(namespace, limit, metadata_filter)
    
    # Local storage methods (for offline mode or fallback)
    
    async def _store_local(
        self,
        namespace: str,
        key: str,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store data in local backup.
        
        Args:
            namespace: Memory namespace
            key: Memory key
            data: Data to store
            metadata: Optional metadata for the memory
            
        Returns:
            Success status
        """
        try:
            # Create namespace directory if it doesn't exist
            namespace_dir = os.path.join(self.backup_dir, namespace)
            os.makedirs(namespace_dir, exist_ok=True)
            
            # Create memory object
            memory = {
                "key": key,
                "data": data,
                "metadata": metadata or {},
                "namespace": namespace
            }
            
            # Save to file
            file_path = os.path.join(namespace_dir, f"{key}.json")
            with open(file_path, 'w') as f:
                json.dump(memory, f, indent=2)
            
            return True
        
        except Exception as e:
            logger.error(f"Error storing memory in local backup: {e}")
            return False
    
    async def _get_local(
        self,
        namespace: str,
        key: str
    ) -> Optional[Any]:
        """Retrieve data from local backup.
        
        Args:
            namespace: Memory namespace
            key: Memory key
            
        Returns:
            Retrieved data or None if not found
        """
        try:
            # Check if file exists
            file_path = os.path.join(self.backup_dir, namespace, f"{key}.json")
            if not os.path.exists(file_path):
                return None
            
            # Load from file
            with open(file_path, 'r') as f:
                memory = json.load(f)
            
            return memory.get("data")
        
        except Exception as e:
            logger.error(f"Error getting memory from local backup: {e}")
            return None
    
    async def _delete_local(
        self,
        namespace: str,
        key: str
    ) -> bool:
        """Delete data from local backup.
        
        Args:
            namespace: Memory namespace
            key: Memory key
            
        Returns:
            Success status
        """
        try:
            # Check if file exists
            file_path = os.path.join(self.backup_dir, namespace, f"{key}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return True
        
        except Exception as e:
            logger.error(f"Error deleting memory from local backup: {e}")
            return False
    
    async def _search_local(
        self,
        namespace: str,
        query: str,
        limit: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search memories in local backup.
        
        Args:
            namespace: Memory namespace
            query: Search query
            limit: Maximum number of results
            metadata_filter: Optional metadata filter
            
        Returns:
            List of matching memories
        """
        try:
            results = []
            namespace_dir = os.path.join(self.backup_dir, namespace)
            
            # Check if namespace directory exists
            if not os.path.exists(namespace_dir):
                return []
            
            # Very basic search implementation
            for filename in os.listdir(namespace_dir):
                if not filename.endswith(".json"):
                    continue
                
                try:
                    file_path = os.path.join(namespace_dir, filename)
                    with open(file_path, 'r') as f:
                        memory = json.load(f)
                    
                    # Apply metadata filter if provided
                    if metadata_filter:
                        match = True
                        for key, value in metadata_filter.items():
                            if memory.get("metadata", {}).get(key) != value:
                                match = False
                                break
                        
                        if not match:
                            continue
                    
                    # Check for query match in data (very simple)
                    if not query or query == "*":
                        # Add to results if no query
                        results.append({
                            "key": memory.get("key"),
                            "metadata": memory.get("metadata", {}),
                            "score": 1.0
                        })
                    else:
                        # Convert data to string for simple text search
                        data_str = json.dumps(memory.get("data", {}))
                        if query.lower() in data_str.lower():
                            results.append({
                                "key": memory.get("key"),
                                "metadata": memory.get("metadata", {}),
                                "score": 0.5  # Arbitrary score for simple match
                            })
                
                except Exception as e:
                    logger.warning(f"Error processing memory file {filename}: {e}")
            
            # Sort by score and limit results
            results.sort(key=lambda x: x.get("score", 0), reverse=True)
            return results[:limit]
        
        except Exception as e:
            logger.error(f"Error searching memories in local backup: {e}")
            return []
    
    async def _list_local(
        self,
        namespace: str,
        limit: int = 100,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List memories in local backup.
        
        Args:
            namespace: Memory namespace
            limit: Maximum number of results
            metadata_filter: Optional metadata filter
            
        Returns:
            List of memory summaries
        """
        try:
            results = []
            namespace_dir = os.path.join(self.backup_dir, namespace)
            
            # Check if namespace directory exists
            if not os.path.exists(namespace_dir):
                return []
            
            # List all memory files
            for filename in os.listdir(namespace_dir):
                if not filename.endswith(".json"):
                    continue
                
                try:
                    file_path = os.path.join(namespace_dir, filename)
                    with open(file_path, 'r') as f:
                        memory = json.load(f)
                    
                    # Apply metadata filter if provided
                    if metadata_filter:
                        match = True
                        for key, value in metadata_filter.items():
                            if memory.get("metadata", {}).get(key) != value:
                                match = False
                                break
                        
                        if not match:
                            continue
                    
                    # Add to results
                    results.append({
                        "key": memory.get("key"),
                        "metadata": memory.get("metadata", {})
                    })
                
                except Exception as e:
                    logger.warning(f"Error processing memory file {filename}: {e}")
            
            # Sort by key
            results.sort(key=lambda x: x.get("key", ""))
            return results[:limit]
        
        except Exception as e:
            logger.error(f"Error listing memories in local backup: {e}")
            return []

async def get_engram_client() -> EngramClient:
    """Get a configured Engram client instance.
    
    Returns:
        Configured EngramClient
    """
    # Read configuration from environment
    offline_mode = TektonEnviron.get("RHETOR_ENGRAM_OFFLINE", "").lower() in ("true", "1", "yes")
    engram_url = get_engram_url()
    engram_api_key = TektonEnviron.get("ENGRAM_API_KEY")
    
    # Create client
    client = EngramClient(
        engram_url=engram_url,
        engram_api_key=engram_api_key,
        offline_mode=offline_mode
    )
    
    # Try to connect
    await client.connect()
    
    return client