"""
Retrieval Augmented Generation (RAG) utility for Ergon.

This module provides RAG capabilities for agents and tools,
making it easy to incorporate memory in any LLM interaction.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple

from ergon.core.memory.service import MemoryService
from ergon.core.memory.utils.categories import MemoryCategory
from ergon.utils.config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)

class RAGService:
    """
    Retrieval Augmented Generation service for Ergon.
    
    This service provides high-level RAG utilities for enhancing
    LLM prompts with relevant memories and managing memory storage.
    """
    
    def __init__(self, agent_id: int, agent_name: Optional[str] = None):
        """
        Initialize the RAG service.
        
        Args:
            agent_id: Agent ID for the memory context
            agent_name: Optional agent name for better logging
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        
        # Initialize memory service
        self.memory_service = MemoryService(agent_id=agent_id, agent_name=agent_name)
        
        logger.info(f"RAG service initialized for agent {agent_id}")
    
    async def initialize(self):
        """Initialize the RAG service."""
        await self.memory_service.initialize()
    
    async def augment_prompt(self, 
                           system_prompt: str, 
                           user_query: str,
                           categories: List[str] = None,
                           min_importance: int = 2,
                           limit: int = 3) -> str:
        """
        Augment a system prompt with relevant memories.
        
        Args:
            system_prompt: Original system prompt
            user_query: User query to find relevant memories for
            categories: Optional list of categories to search in
            min_importance: Minimum importance score
            limit: Maximum number of memories to include
            
        Returns:
            Augmented prompt with relevant memories
        """
        # Get relevant context
        context = await self.memory_service.get_relevant_context(
            query=user_query,
            categories=categories,
            min_importance=min_importance,
            limit=limit
        )
        
        # If no context found, return original prompt
        if not context:
            return system_prompt
        
        # Combine with original prompt
        return f"{system_prompt}\n\n{context}"
    
    async def store_interaction(self, 
                              user_message: str, 
                              assistant_response: str,
                              interaction_importance: int = 2) -> Tuple[str, str]:
        """
        Store a user-assistant interaction in memory.
        
        Args:
            user_message: User message
            assistant_response: Assistant response
            interaction_importance: Importance score for the interaction
            
        Returns:
            Tuple of (user_memory_id, assistant_memory_id)
        """
        # Store user message with default category and importance
        user_memory_id = await self.memory_service.add_memory(
            content=user_message,
            category=MemoryCategory.SESSION,
            importance=interaction_importance
        )
        
        # Store assistant response with default category and importance
        assistant_memory_id = await self.memory_service.add_memory(
            content=assistant_response,
            category=MemoryCategory.SESSION,
            importance=interaction_importance
        )
        
        return user_memory_id, assistant_memory_id
    
    async def store_memory(self, 
                         content: str, 
                         category: str = None, 
                         importance: int = None) -> str:
        """
        Store a memory with optional category and importance.
        
        Args:
            content: Memory content
            category: Optional category (auto-detected if not provided)
            importance: Optional importance (auto-assigned if not provided)
            
        Returns:
            Memory ID
        """
        return await self.memory_service.add_memory(
            content=content,
            category=category,
            importance=importance
        )
    
    async def search_memories(self, 
                           query: str, 
                           categories: List[str] = None,
                           min_importance: int = 1,
                           limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant memories.
        
        Args:
            query: Search query
            categories: Optional list of categories to search in
            min_importance: Minimum importance score
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        return await self.memory_service.search(
            query=query,
            categories=categories,
            min_importance=min_importance,
            limit=limit
        )
    
    async def get_recent_memories(self, 
                               categories: List[str] = None,
                               min_importance: int = None,
                               limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get most recent memories.
        
        Args:
            categories: Optional list of categories to filter by
            min_importance: Optional minimum importance to filter by
            limit: Maximum number of results
            
        Returns:
            List of memories
        """
        return await self.memory_service.get_recent(
            categories=categories,
            min_importance=min_importance,
            limit=limit
        )
    
    async def close(self) -> bool:
        """
        Close the RAG service and clean up resources.
        
        Returns:
            True if successful
        """
        return await self.memory_service.close()


class RAGToolFunctions:
    """
    Memory-related tool functions for agents.
    
    This class provides tool functions that can be registered with
    agents to give them memory capabilities.
    """
    
    def __init__(self, agent_id: int, agent_name: Optional[str] = None):
        """
        Initialize memory tool functions.
        
        Args:
            agent_id: Agent ID for the memory context
            agent_name: Optional agent name for better logging
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.rag_service = RAGService(agent_id=agent_id, agent_name=agent_name)
    
    async def initialize(self):
        """Initialize the tool functions."""
        await self.rag_service.initialize()
    
    async def search_memory(self, query: str, category: Optional[str] = None) -> str:
        """
        Tool function to search memories by query.
        
        Args:
            query: Search query
            category: Optional category to search in
            
        Returns:
            Formatted string with search results
        """
        categories = [category] if category else None
        
        try:
            # Search memories
            memories = await self.rag_service.search_memories(
                query=query,
                categories=categories,
                limit=5
            )
            
            if not memories:
                return "No relevant memories found."
            
            # Format results
            result = "Here are the memories I found:\n\n"
            for i, memory in enumerate(memories):
                category_str = memory["category"].capitalize()
                importance_str = "★" * memory["importance"]
                result += f"{i+1}. [{category_str}] {memory['content']}\n"
                result += f"   Importance: {importance_str} ({memory['importance']}/5), "
                result += f"Relevance: {memory['score']:.2f}\n\n"
            
            return result
        except Exception as e:
            logger.error(f"Error in search_memory tool: {e}")
            return f"Error searching memories: {str(e)}"
    
    async def store_important_fact(self, content: str, importance: int = 4) -> str:
        """
        Tool function to store an important fact in memory.
        
        Args:
            content: Fact to remember
            importance: Importance score (1-5)
            
        Returns:
            Confirmation message
        """
        try:
            # Validate importance
            importance = max(1, min(5, importance))
            
            # Store memory
            memory_id = await self.rag_service.store_memory(
                content=content,
                category=MemoryCategory.FACTUAL,
                importance=importance
            )
            
            return f"I've stored this important fact in my memory with importance level {importance}/5."
        except Exception as e:
            logger.error(f"Error in store_important_fact tool: {e}")
            return f"Error storing fact: {str(e)}"
    
    async def remember_preference(self, preference: str) -> str:
        """
        Tool function to store a user preference in memory.
        
        Args:
            preference: User preference to remember
            
        Returns:
            Confirmation message
        """
        try:
            # Store with high importance
            memory_id = await self.rag_service.store_memory(
                content=preference,
                category=MemoryCategory.PREFERENCE,
                importance=4  # Preferences are important by default
            )
            
            return f"I'll remember your preference: {preference}"
        except Exception as e:
            logger.error(f"Error in remember_preference tool: {e}")
            return f"Error remembering preference: {str(e)}"
    
    async def get_recent_memories(self, category: Optional[str] = None, limit: int = 5) -> str:
        """
        Tool function to retrieve recent memories.
        
        Args:
            category: Optional category to filter by
            limit: Maximum number of memories to retrieve
            
        Returns:
            Formatted string with recent memories
        """
        try:
            # Validate limit
            limit = min(20, max(1, limit))  # Between 1 and 20
            
            # Get recent memories
            categories = [category] if category else None
            memories = await self.rag_service.get_recent_memories(
                categories=categories,
                limit=limit
            )
            
            if not memories:
                return "No memories found."
            
            # Format results
            result = f"Here are your {limit} most recent memories:\n\n"
            for i, memory in enumerate(memories):
                category_str = memory["category"].capitalize()
                importance_str = "★" * memory["importance"]
                created_at = memory["created_at"].strftime("%Y-%m-%d %H:%M")
                result += f"{i+1}. [{category_str}] {memory['content']}\n"
                result += f"   Importance: {importance_str} ({memory['importance']}/5), "
                result += f"Created: {created_at}\n\n"
            
            return result
        except Exception as e:
            logger.error(f"Error in get_recent_memories tool: {e}")
            return f"Error retrieving recent memories: {str(e)}"
    
    def register_tools(self, tools_dict: Dict[str, callable]) -> None:
        """
        Register all memory tool functions.
        
        Args:
            tools_dict: Dictionary to register tools in
        """
        tools_dict["search_memory"] = self.search_memory
        tools_dict["store_important_fact"] = self.store_important_fact
        tools_dict["remember_preference"] = self.remember_preference
        tools_dict["get_recent_memories"] = self.get_recent_memories