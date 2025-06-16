#!/usr/bin/env python3
"""
Simple, clean memory interface for AI assistants.

Usage:
    from engram import Memory
    
    mem = Memory()
    await mem.store("Important insight about code")
    results = await mem.recall("insight")
    context = await mem.context("working on code")
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
from pathlib import Path

# Debug mode - silent by default
DEBUG = os.getenv('ENGRAM_DEBUG', '').lower() == 'true'
logger = logging.getLogger(__name__)

# Only show errors by default
if not DEBUG:
    logging.getLogger().setLevel(logging.ERROR)


def debug_log(message: str, level=logging.INFO):
    """Log only if debug mode is enabled"""
    if DEBUG:
        logger.log(level, message)


@dataclass
class MemoryItem:
    """A single memory with metadata"""
    id: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    relevance: float = 1.0


class Memory:
    """
    Simple memory interface for AI assistants.
    
    Three methods:
    - store(): Save a thought
    - recall(): Find memories
    - context(): Get relevant background
    """
    
    def __init__(self, namespace: str = "default"):
        """Initialize memory system with optional namespace"""
        self.namespace = namespace
        self._storage = None
        self._initialized = False
        
    async def _ensure_initialized(self):
        """Lazy initialization of storage backend"""
        if self._initialized:
            return
            
        debug_log(f"Initializing Memory with namespace: {self.namespace}")
        
        try:
            # Try to use existing storage infrastructure
            from engram.core.memory.base import MemoryService
            self._storage = MemoryService(client_id=self.namespace)
            debug_log("Using MemoryService backend")
        except ImportError:
            # Fallback to simple in-memory storage
            debug_log("Using in-memory storage (MemoryService not available)")
            self._storage = SimpleInMemoryStorage()
            
        self._initialized = True
    
    async def store(self, content: str, **metadata) -> str:
        """
        Store a memory with optional metadata.
        
        Args:
            content: The text content to store
            **metadata: Optional metadata (tags, category, importance, etc.)
            
        Returns:
            Memory ID for reference
            
        Example:
            await mem.store("Learned about async/await", 
                          tags=["python", "async"],
                          importance=0.8)
        """
        await self._ensure_initialized()
        
        # Auto-add useful metadata
        if 'timestamp' not in metadata:
            metadata['timestamp'] = datetime.now()
        if 'namespace' not in metadata:
            metadata['namespace'] = self.namespace
            
        debug_log(f"Storing memory: {content[:50]}...")
        
        try:
            # Use existing storage
            memory_id = await self._storage.add(
                content=content,
                namespace=self.namespace,
                metadata=metadata
            )
            debug_log(f"Stored with ID: {memory_id}")
            return memory_id
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise
    
    async def recall(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """
        Recall memories similar to the query.
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of relevant memories, sorted by relevance
            
        Example:
            memories = await mem.recall("async programming")
        """
        await self._ensure_initialized()
        
        debug_log(f"Recalling memories for: {query}")
        
        try:
            # Use existing search
            results = await self._storage.search(
                query=query,
                namespace=self.namespace,
                limit=limit
            )
            
            # Convert to simple MemoryItem format
            memories = []
            for r in results:
                # Handle different result formats
                if isinstance(r, str):
                    # Simple string result
                    mem_item = MemoryItem(
                        id=f"mem_{hash(r)}",
                        content=r,
                        timestamp=datetime.now(),
                        metadata={},
                        relevance=1.0
                    )
                elif hasattr(r, 'id'):
                    # Structured result
                    mem_item = MemoryItem(
                        id=r.id,
                        content=getattr(r, 'text', getattr(r, 'content', str(r))),
                        timestamp=getattr(r, 'timestamp', datetime.now()),
                        metadata=getattr(r, 'metadata', {}),
                        relevance=getattr(r, 'score', 1.0)
                    )
                else:
                    # Unknown format - convert to string
                    mem_item = MemoryItem(
                        id=f"mem_{hash(str(r))}",
                        content=str(r),
                        timestamp=datetime.now(),
                        metadata={},
                        relevance=1.0
                    )
                memories.append(mem_item)
            
            debug_log(f"Found {len(memories)} memories")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to recall memories: {e}")
            return []
    
    async def context(self, query: str, limit: int = 10) -> str:
        """
        Get relevant context as a single string.
        
        Useful for providing background to LLMs.
        
        Args:
            query: What context is needed for
            limit: Maximum memories to include
            
        Returns:
            Formatted context string
            
        Example:
            context = await mem.context("debugging async issues")
            # Use context in prompts
        """
        await self._ensure_initialized()
        
        debug_log(f"Getting context for: {query}")
        
        memories = await self.recall(query, limit=limit)
        
        if not memories:
            return "No relevant context found."
        
        # Format memories into context
        context_parts = ["Relevant context:"]
        for mem in memories:
            # Format with timestamp if available
            timestamp = mem.timestamp.strftime("%Y-%m-%d %H:%M") if mem.timestamp else "Unknown time"
            context_parts.append(f"\n[{timestamp}] {mem.content}")
        
        context = "\n".join(context_parts)
        debug_log(f"Generated context with {len(memories)} memories")
        
        return context


class SimpleInMemoryStorage:
    """Fallback storage when Engram storage isn't available"""
    
    def __init__(self):
        self.memories = []
        self.next_id = 1
    
    async def add(self, content: str, namespace: str, metadata: dict) -> str:
        """Add a memory"""
        memory_id = f"mem_{self.next_id}"
        self.next_id += 1
        
        self.memories.append({
            'id': memory_id,
            'text': content,
            'namespace': namespace,
            'metadata': metadata,
            'timestamp': metadata.get('timestamp', datetime.now())
        })
        
        return memory_id
    
    async def search(self, query: str, namespace: str, limit: int) -> list:
        """Simple substring search"""
        query_lower = query.lower()
        results = []
        
        for mem in self.memories:
            if mem['namespace'] == namespace and query_lower in mem['text'].lower():
                results.append(type('Memory', (), mem))
        
        # Sort by most recent
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:limit]


# Convenience function for even simpler usage
async def quick_memory():
    """Get a default memory instance"""
    return Memory()


# Example usage
if __name__ == "__main__":
    async def example():
        # Just 3 lines to use memory!
        mem = Memory()
        await mem.store("Engram is now simple to use")
        print(await mem.recall("simple"))
    
    asyncio.run(example())