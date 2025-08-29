"""
Engram Memory Wrapper
Provides a simplified interface to Engram's MemoryManager for CI memory operations.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class EngramMemoryWrapper:
    """
    Wrapper around Engram's MemoryManager to provide the interface expected by memory_injector.
    
    This class bridges between the memory injection system and Engram's actual API.
    """
    
    def __init__(self, engram_manager=None):
        """
        Initialize wrapper with an Engram MemoryManager instance.
        
        Args:
            engram_manager: Instance of Engram.MemoryManager
        """
        self.manager = engram_manager
        self._memory_service_cache = {}
        
    async def get_recent_memories(self, ci_name: str, limit: int = 5, compartment: str = 'session') -> List[Dict]:
        """
        Get recent memories for a CI.
        
        Args:
            ci_name: Name of the CI
            limit: Number of memories to retrieve
            compartment: Memory compartment to search
            
        Returns:
            List of memory dictionaries
        """
        if not self.manager:
            return []
            
        try:
            # Get memory service for this CI
            service = await self._get_memory_service(ci_name)
            if not service:
                return []
            
            # For now, return empty list as we need to implement the actual retrieval
            # This would typically call service.search() or similar
            logger.debug(f"Getting {limit} recent memories for {ci_name} from {compartment}")
            return []
            
        except Exception as e:
            logger.error(f"Failed to get recent memories: {e}")
            return []
    
    async def search_memories(self, ci_name: str, query: str, compartment: str = 'all', limit: int = 5) -> List[Dict]:
        """
        Search memories for a CI.
        
        Args:
            ci_name: Name of the CI
            query: Search query
            compartment: Memory compartment to search
            limit: Number of results
            
        Returns:
            List of memory dictionaries
        """
        if not self.manager:
            return []
            
        try:
            # Get memory service for this CI
            service = await self._get_memory_service(ci_name)
            if not service:
                return []
            
            # For now, return empty list as we need to implement the actual search
            logger.debug(f"Searching {compartment} for '{query}' (CI: {ci_name}, limit: {limit})")
            return []
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    async def find_similar_memories(self, ci_name: str, content: str, limit: int = 5) -> List[Dict]:
        """
        Find memories similar to given content.
        
        Args:
            ci_name: Name of the CI
            content: Content to find similar memories for
            limit: Number of results
            
        Returns:
            List of memory dictionaries
        """
        if not self.manager:
            return []
            
        try:
            # Get memory service for this CI
            service = await self._get_memory_service(ci_name)
            if not service:
                return []
            
            # For now, return empty list as we need to implement the actual similarity search
            logger.debug(f"Finding {limit} similar memories for {ci_name}")
            return []
            
        except Exception as e:
            logger.error(f"Failed to find similar memories: {e}")
            return []
    
    async def _get_memory_service(self, ci_name: str):
        """
        Get or create a memory service for a CI.
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            Memory service instance or None
        """
        if ci_name not in self._memory_service_cache:
            try:
                # Get memory service from manager
                self._memory_service_cache[ci_name] = await self.manager.get_memory_service(ci_name)
            except Exception as e:
                logger.error(f"Failed to get memory service for {ci_name}: {e}")
                return None
                
        return self._memory_service_cache.get(ci_name)