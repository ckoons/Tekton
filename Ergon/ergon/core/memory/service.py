"""
Core memory service for Ergon.

This module provides the main memory service that manages storage and retrieval
of agent memories using Tekton's shared vector database approach.
"""

import json
import logging
import os
import time
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from ergon.core.database.engine import get_db_session
from ergon.core.database.models import Agent
from ergon.core.memory.models.schema import Memory
from ergon.core.memory.utils.categories import MemoryCategory
from ergon.core.memory.services.embedding import embedding_service
from ergon.core.memory.services.vector_store import MemoryVectorService
from ergon.utils.config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)

class MemoryService:
    """
    Core memory service with persistent storage and retrieval.
    
    This service uses a combination of SQL database for metadata storage
    and Tekton's vector store for embedding storage and semantic search.
    """
    
    def __init__(self, agent_id: Optional[int] = None, agent_name: Optional[str] = None):
        """
        Initialize the memory service.
        
        Args:
            agent_id: The ID of the agent to manage memories for (or None for terminal chat)
            agent_name: Optional name of the agent (for better logging)
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.terminal_contexts = {}
        
        # If agent_id is provided, this is for a specific agent
        if agent_id:
            # Get agent details if name not provided
            if not self.agent_name:
                with get_db_session() as db:
                    agent = db.query(Agent).filter(Agent.id == self.agent_id).first()
                    if agent:
                        self.agent_name = agent.name
                    else:
                        self.agent_name = f"Agent-{self.agent_id}"
            
            # Create namespace for isolation
            self.namespace = f"agent_{self.agent_id}"
        else:
            # Terminal chat mode - use a different namespace
            self.namespace = "terminal_chat"
        
        # Initialize vector store
        self.vector_store = MemoryVectorService(namespace=self.namespace)
        
        if agent_id:
            logger.info(f"Memory service initialized for agent {self.agent_id} ({self.agent_name})")
        else:
            logger.info(f"Memory service initialized for terminal chat")
    
    async def initialize(self):
        """Initialize the memory service and register with Engram."""
        # Register with Engram if it's running
        from ergon.core.memory.services.client import client_manager
        
        try:
            await client_manager.start()
            
            # Check if Engram is running
            engram_info = None
            with client_manager.lock:
                for client_id, info in client_manager.active_clients.items():
                    if info.get("type") == "engram":
                        engram_info = await client_manager.get_client_info(client_id)
                        break
            
            if engram_info:
                # Register this memory service's agent with Engram
                client_id = f"ergon_agent_{self.agent_id}"
                
                # Check if already registered
                existing_client = await client_manager.get_client_info(client_id)
                if not existing_client:
                    await client_manager.register_client(
                        client_id=client_id,
                        client_type="ergon_agent",
                        config={
                            "agent_id": self.agent_id,
                            "agent_name": self.agent_name
                        }
                    )
                    
                    logger.info(f"Registered agent {self.agent_id} ({self.agent_name}) with Engram")
        except Exception as e:
            logger.warning(f"Could not register with Engram: {e}")
            logger.warning("Memory will work locally, but won't be integrated with Engram")
            
        # Initialize vector store connection if needed
        # Nothing to do currently as vector store is initialized in constructor
    
    async def add_memory(self, 
                       content: str, 
                       category: str = None, 
                       importance: int = None,
                       metadata: Dict[str, Any] = None) -> str:
        """
        Add a memory to storage.
        
        Args:
            content: Memory content text
            category: Memory category (auto-detected if not provided)
            importance: Importance score (1-5, auto-assigned if not provided)
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        # Auto-categorize if needed
        if not category or not importance:
            auto_category, auto_importance = MemoryCategory.categorize(content)
            category = category or auto_category
            importance = importance or auto_importance
        
        # Validate importance is in range 1-5
        importance = max(1, min(5, importance))
        
        # Create metadata
        memory_metadata = metadata or {}
        memory_metadata.update({
            "agent_id": self.agent_id,
            "category": category,
            "importance": importance,
            "timestamp": int(time.time())
        })
        
        # Generate embedding
        embedding = await embedding_service.embed_text(content)
        
        # Store in vector database
        memory_id = await self.vector_store.add_memory(
            content=content,
            embedding=embedding,
            metadata=memory_metadata
        )
        
        # Store metadata in SQL database
        with get_db_session() as db:
            memory = Memory(
                id=memory_id,
                agent_id=self.agent_id,
                content=content,
                category=category,
                importance=importance,
                memory_metadata=memory_metadata
            )
            db.add(memory)
            db.commit()
        
        logger.debug(f"Added memory {memory_id} for agent {self.agent_id} with category {category}")
        return memory_id
    
    async def search(self, 
                   query: str, 
                   categories: List[str] = None, 
                   min_importance: int = 1,
                   limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant memories.
        
        Args:
            query: The search query
            categories: Optional list of categories to search in
            min_importance: Minimum importance score
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        # Generate query embedding
        query_embedding = await embedding_service.embed_text(query)
        
        # Build metadata filter
        filter_dict = {}
        if categories:
            filter_dict["category"] = categories  # The vector store will handle this as $in
        if min_importance:
            filter_dict["importance"] = {"gte": min_importance}
        
        # Search vector database
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            filter_dict=filter_dict,
            limit=limit
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result["id"],
                "content": result["content"],
                "category": result["metadata"].get("category", "unknown"),
                "importance": result["metadata"].get("importance", 3),
                "score": result["score"],
                "created_at": datetime.fromtimestamp(result["metadata"].get("timestamp", 0))
            })
        
        return formatted_results
    
    async def get_by_category(self, 
                           category: str, 
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get memories by category.
        
        Args:
            category: Memory category to retrieve
            limit: Maximum number of results
            
        Returns:
            List of memories
        """
        results = await self.vector_store.get_by_category(
            category=category,
            limit=limit
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result["id"],
                "content": result["content"],
                "category": result["metadata"].get("category", "unknown"),
                "importance": result["metadata"].get("importance", 3),
                "created_at": datetime.fromtimestamp(result["metadata"].get("timestamp", 0))
            })
        
        return formatted_results
    
    async def get_recent(self, 
                       categories: List[str] = None,
                       min_importance: int = None,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recent memories.
        
        Args:
            categories: Optional list of categories to filter by
            min_importance: Optional minimum importance to filter by
            limit: Maximum number of results
            
        Returns:
            List of memories
        """
        results = await self.vector_store.get_recent(limit=limit * 2)  # Get more for filtering
        
        # Apply filters
        filtered_results = []
        for result in results:
            metadata = result.get("metadata", {})
            
            # Filter by category if specified
            if categories and metadata.get("category") not in categories:
                continue
                
            # Filter by importance if specified
            if min_importance and metadata.get("importance", 0) < min_importance:
                continue
                
            filtered_results.append(result)
        
        # Format and limit results
        formatted_results = []
        for result in filtered_results[:limit]:
            formatted_results.append({
                "id": result["id"],
                "content": result["content"],
                "category": result["metadata"].get("category", "unknown"),
                "importance": result["metadata"].get("importance", 3),
                "created_at": datetime.fromtimestamp(result["metadata"].get("timestamp", 0))
            })
        
        return formatted_results
    
    async def get_relevant_context(self, 
                                query: str, 
                                categories: List[str] = None,
                                min_importance: int = 2,
                                limit: int = 3) -> str:
        """
        Get relevant context from memories formatted for prompt enhancement.
        
        Args:
            query: The query to find relevant memories for
            categories: Optional list of categories to search in
            min_importance: Minimum importance score
            limit: Maximum number of memories to include
            
        Returns:
            Formatted string with relevant memories for context
        """
        # Search for relevant memories
        memories = await self.search(
            query=query,
            categories=categories,
            min_importance=min_importance,
            limit=limit
        )
        
        if not memories:
            return ""
        
        # Format memories as context
        context = "Here are some relevant memories that might help with your response:\n\n"
        
        for i, memory in enumerate(memories):
            category = memory["category"].capitalize()
            importance = "★" * memory["importance"]
            context += f"{i+1}. [{category}] {memory['content']} ({importance})\n\n"
        
        return context
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful
        """
        # Delete from vector store
        vector_deleted = await self.vector_store.delete([memory_id])
        
        # Delete from SQL database
        with get_db_session() as db:
            memory = db.query(Memory).filter(Memory.id == memory_id).first()
            if memory:
                db.delete(memory)
                db.commit()
                return vector_deleted
            return False
    
    async def clear_category(self, category: str) -> int:
        """
        Clear all memories in a category.
        
        Args:
            category: Category to clear
            
        Returns:
            Number of memories deleted
        """
        # Get all memories in this category
        memories = await self.get_by_category(category=category, limit=1000)
        memory_ids = [memory["id"] for memory in memories]
        
        # Delete from vector store
        await self.vector_store.delete(memory_ids)
        
        # Delete from SQL database
        with get_db_session() as db:
            deleted = db.query(Memory).filter(
                Memory.agent_id == self.agent_id,
                Memory.category == category
            ).delete()
            db.commit()
        
        return deleted
    
    async def clear_all(self) -> int:
        """
        Clear all memories for this agent.
        
        Returns:
            Number of memories deleted
        """
        # Get all memories for this agent
        results = await self.vector_store.get_recent(limit=10000)  # Large limit to get all
        memory_ids = [result["id"] for result in results]
        
        # Delete from vector store
        await self.vector_store.delete(memory_ids)
        
        # Delete from SQL database
        with get_db_session() as db:
            deleted = db.query(Memory).filter(
                Memory.agent_id == self.agent_id
            ).delete()
            db.commit()
        
        return deleted
    
    async def close(self) -> bool:
        """
        Close the memory service and clean up resources.
        
        Returns:
            True if successful
        """
        # Deregister from Engram if registered
        try:
            from ergon.core.memory.services.client import client_manager
            
            # Check if registered with Engram
            client_id = f"ergon_agent_{self.agent_id}"
            client_info = await client_manager.get_client_info(client_id)
            
            if client_info:
                # Deregister from Engram
                success = await client_manager.deregister_client(client_id)
                if success:
                    logger.info(f"Deregistered agent {self.agent_id} ({self.agent_name}) from Engram")
                else:
                    logger.warning(f"Failed to deregister agent {self.agent_id} from Engram")
        except Exception as e:
            logger.warning(f"Error during deregistration from Engram: {e}")
        
        return True
        
    # Terminal chat methods
    
    async def add_message(self, context_id: str, message: str, role: str) -> str:
        """
        Add a message to the terminal chat memory.
        
        Args:
            context_id: The context ID (e.g., 'ergon', 'awt-team')
            message: The message content
            role: The message role ('user' or 'assistant')
            
        Returns:
            Message ID
        """
        # Initialize context if needed
        if context_id not in self.terminal_contexts:
            self.terminal_contexts[context_id] = []
        
        # Create message object
        message_id = str(uuid.uuid4())
        timestamp = int(time.time())
        
        message_obj = {
            "id": message_id,
            "content": message,
            "role": role,
            "context_id": context_id,
            "timestamp": timestamp
        }
        
        # Add to in-memory context
        self.terminal_contexts[context_id].append(message_obj)
        
        # Trim context if too long
        max_context_length = 50
        if len(self.terminal_contexts[context_id]) > max_context_length:
            self.terminal_contexts[context_id] = self.terminal_contexts[context_id][-max_context_length:]
        
        # For persistence, also add as a memory
        category = "terminal_chat"
        importance = 3
        
        # Create metadata
        memory_metadata = {
            "context_id": context_id,
            "role": role,
            "category": category,
            "importance": importance,
            "timestamp": timestamp
        }
        
        # Generate embedding
        embedding = await embedding_service.embed_text(message)
        
        # Store in vector database
        memory_id = await self.vector_store.add_memory(
            content=message,
            embedding=embedding,
            metadata=memory_metadata
        )
        
        logger.debug(f"Added terminal message to context {context_id}, role {role}")
        return message_id
    
    def get_recent_messages(self, context_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get recent messages from the terminal chat memory.
        
        Args:
            context_id: The context ID (e.g., 'ergon', 'awt-team')
            limit: Maximum number of messages to return
            
        Returns:
            List of messages in format expected by LLM client
        """
        # Check if context exists
        if context_id not in self.terminal_contexts:
            return []
        
        # Get most recent messages up to the limit
        recent_messages = self.terminal_contexts[context_id][-limit:]
        
        # Format for LLM client (which expects role and content keys)
        return [{"role": msg["role"], "content": msg["content"]} for msg in recent_messages]
    
    async def clear_context(self, context_id: str) -> bool:
        """
        Clear all messages for a context.
        
        Args:
            context_id: The context ID to clear
            
        Returns:
            True if successful
        """
        if context_id in self.terminal_contexts:
            self.terminal_contexts[context_id] = []
            
            # Delete from vector store - we'd need a better filter here in a real implementation
            # This is just a placeholder
            try:
                # Find all memories with this context_id and delete them
                # This would be cleaner with a proper filter system in the vector store
                pass
            except Exception as e:
                logger.error(f"Error clearing context from vector store: {e}")
            
            return True
        return False