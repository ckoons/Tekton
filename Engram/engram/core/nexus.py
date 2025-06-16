#!/usr/bin/env python3
"""
Nexus - Memory-enabled AI assistant interface for Engram

This module provides a standardized interface for memory-enabled AI assistants,
allowing seamless integration of memory capabilities with LLM interactions.
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.nexus")

class NexusInterface:
    """
    Nexus interface for memory-enabled AI assistants.
    
    This class provides methods for enhancing LLM conversations with memory 
    capabilities, including:
    - Context enrichment with relevant memories
    - Memory storage of important conversation points
    - Memory-aware conversation management
    - Standardized memory retrieval for different assistant needs
    """
    
    def __init__(self, memory_service, structured_memory):
        """
        Initialize the Nexus interface.
        
        Args:
            memory_service: Instance of the MemoryService for compatibility with existing memories
            structured_memory: Instance of the StructuredMemory for enhanced memory features
        """
        self.memory_service = memory_service
        self.structured_memory = structured_memory
        self.conversation_history = []
        self.last_memory_update = None
        self.session_id = f"session-{int(time.time())}"
        
        # Settings for memory management
        self.settings = {
            "auto_memorize": True,
            "memory_threshold": 0.7,  # Importance threshold for auto-memorization
            "context_memories_count": 5,
            "include_private_memories": False,
            "memory_digest_size": 10
        }
        
    async def start_session(self, session_name: Optional[str] = None) -> str:
        """
        Start a new assistant session with memory context.
        
        Args:
            session_name: Optional name for this session
            
        Returns:
            Formatted session start message with memory digest
        """
        # Generate session ID
        self.session_id = f"session-{int(time.time())}"
        
        if session_name:
            session_description = f"Session: {session_name} (ID: {self.session_id})"
        else:
            session_description = f"Session ID: {self.session_id}"
            
        # Reset conversation history
        self.conversation_history = []
        
        # Generate memory digest
        memory_digest = await self.structured_memory.get_memory_digest(
            max_memories=self.settings["memory_digest_size"],
            include_private=self.settings["include_private_memories"]
        )
        
        # Record session start in both memory systems for compatibility
        session_start_memory = f"Started new Nexus session: {session_description}"
        
        await self.memory_service.add(
            session_start_memory,
            namespace="session"
        )
        
        await self.structured_memory.add_memory(
            content=session_start_memory,
            category="session",
            importance=3,
            metadata={"session_id": self.session_id, "event_type": "session_start"},
            tags=["session", "session_start"]
        )
        
        self.last_memory_update = datetime.now()
        
        # Combine digest and session start message
        result = f"# Nexus Session Started\n\n{session_description}\n\n{memory_digest}"
        return result
        
    async def end_session(self, summary: Optional[str] = None) -> str:
        """
        End the current session and store a summary.
        
        Args:
            summary: Optional session summary
            
        Returns:
            Session end confirmation message
        """
        if summary is None:
            # Generate a basic summary if not provided
            message_count = len(self.conversation_history)
            summary = f"Session ended with {message_count} messages exchanged."
        
        # Record session end in both memory systems
        session_end_memory = f"Session {self.session_id} ended: {summary}"
        
        # Make sure to use the keyword "session ended" for easy searching in tests
        if "session ended" not in session_end_memory.lower():
            session_end_memory = f"Session ended: {self.session_id} - {summary}"
        
        await self.memory_service.add(
            content=session_end_memory,
            namespace="session"
        )
        
        await self.structured_memory.add_memory(
            content=session_end_memory,
            category="session",
            importance=3,
            metadata={"session_id": self.session_id, "event_type": "session_end"},
            tags=["session", "session_end"]
        )
        
        return f"Session ended. {summary}"
    
    async def process_message(self, message: str, is_user: bool = True, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a conversation message, enriching with memory context if needed.
        
        Args:
            message: The message content
            is_user: Whether this is a user message (True) or assistant message (False)
            metadata: Additional metadata for the message
            
        Returns:
            Memory-enriched context for the message (for user messages) or
            empty string (for assistant messages which are just stored)
        """
        # Initialize metadata if not provided
        if metadata is None:
            metadata = {}
            
        # Add message to conversation history
        self.conversation_history.append({
            "role": "user" if is_user else "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        })
        
        # Store assistant responses directly in memory
        if not is_user:
            # Check if enough time has passed since last memory update
            # to avoid storing too many memories in quick succession
            now = datetime.now()
            if self.last_memory_update is None or (now - self.last_memory_update).total_seconds() > 30:
                await self._store_assistant_memory(message, metadata)
                self.last_memory_update = now
            return ""
        
        # For user messages, enhance with memory context
        return await self._enrich_user_message(message, metadata)
    
    async def _enrich_user_message(self, message: str, metadata: Dict[str, Any]) -> str:
        """
        Enrich a user message with relevant memory context.
        
        Args:
            message: The user message content
            metadata: Message metadata
            
        Returns:
            Context-enriched message for the assistant
        """
        # Get relevant memories from structured memory
        context_memories = await self.structured_memory.get_context_memories(
            text=message,
            max_memories=self.settings["context_memories_count"]
        )
        
        # If no structured memories found, try legacy memory service
        if not context_memories:
            # Use the old memory service's search function
            namespaces = ["longterm", "conversations"]
            if self.settings["include_private_memories"]:
                namespaces.append("private")
                
            legacy_context = await self.memory_service.get_relevant_context(
                query=message,
                namespaces=namespaces,
                limit=self.settings["context_memories_count"]
            )
            
            if legacy_context:
                return f"{legacy_context}\n\n{message}"
        
        # Format structured memories as context
        if context_memories:
            context_parts = ["### Relevant Memory Context\n"]
            
            # Group memories by category
            memories_by_category = {}
            for memory in context_memories:
                category = memory.get("category", "unknown")
                if category not in memories_by_category:
                    memories_by_category[category] = []
                memories_by_category[category].append(memory)
            
            # Format each category
            for category, memories in memories_by_category.items():
                context_parts.append(f"\n#### {category.capitalize()}\n")
                
                for memory in memories:
                    importance_str = "★" * memory["importance"]
                    context_parts.append(f"- {importance_str} {memory['content']}\n")
            
            # Combine context with user message
            return f"{''.join(context_parts)}\n\n{message}"
        
        # If no relevant context found, return original message
        return message
    
    async def _store_assistant_memory(self, message: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Store an assistant message in memory with auto-categorization.
        
        Args:
            message: The assistant message content
            metadata: Message metadata
            
        Returns:
            Memory ID if stored, None otherwise
        """
        try:
            # Auto-categorize the message
            memory_id = await self.structured_memory.add_auto_categorized_memory(
                content=message,
                metadata={
                    "session_id": self.session_id,
                    "role": "assistant",
                    **metadata
                },
                manual_tags=["assistant_message"]
            )
            
            # Also store in legacy memory service for compatibility
            await self.memory_service.add(
                content=message,
                namespace="conversations",
                metadata={
                    "role": "assistant",
                    "session_id": self.session_id,
                    **metadata
                }
            )
            
            return memory_id
        except Exception as e:
            logger.error(f"Error storing assistant memory: {e}")
            return None
    
    async def store_memory(self, 
                          content: str, 
                          category: Optional[str] = None, 
                          importance: Optional[int] = None,
                          tags: Optional[List[str]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store a memory, using both structured and legacy systems.
        
        Args:
            content: The memory content
            category: Optional memory category
            importance: Optional importance level (1-5)
            tags: Optional tags for the memory
            metadata: Additional metadata
            
        Returns:
            Dict with results from both memory systems
        """
        results = {}
        
        # Initialize metadata
        if metadata is None:
            metadata = {}
        
        metadata["session_id"] = self.session_id
        metadata["source"] = "nexus_interface"
        metadata["timestamp"] = datetime.now().isoformat()
        
        # Store in structured memory
        structured_memory_id = await self.structured_memory.add_auto_categorized_memory(
            content=content,
            manual_category=category,
            manual_importance=importance,
            manual_tags=tags,
            metadata=metadata
        )
        results["structured_memory_id"] = structured_memory_id
        
        # Map category to legacy namespace
        if category in ["personal", "preferences"]:
            namespace = "longterm"
        elif category == "private":
            namespace = "thinking"
        elif category == "projects":
            namespace = "projects"
        else:
            namespace = "conversations"
        
        # Store in legacy memory service
        legacy_result = await self.memory_service.add(
            content=content,
            namespace=namespace,
            metadata=metadata
        )
        results["legacy_success"] = legacy_result
        
        return results
    
    async def forget_memory(self, content: str) -> bool:
        """
        Mark specific information to be forgotten across memory systems.
        
        Args:
            content: Information to forget
            
        Returns:
            Boolean indicating success
        """
        # Find memory by content in structured memory
        memory = await self.structured_memory.get_memory_by_content(content)
        
        # If found, delete it
        if memory:
            await self.structured_memory.delete_memory(memory["id"])
        
        # Add a forget instruction in legacy memory
        forget_result = await self.memory_service.add(
            content=f"FORGET/IGNORE: {content}",
            namespace="longterm",
            metadata={
                "session_id": self.session_id,
                "event_type": "forget",
                "timestamp": datetime.now().isoformat(),
            }
        )
        
        return forget_result
    
    async def search_memories(self, 
                            query: str = None, 
                            categories: Optional[List[str]] = None,
                            min_importance: int = 1,
                            limit: int = 5) -> Dict[str, Any]:
        """
        Search for memories across memory systems.
        
        Args:
            query: Search query
            categories: Memory categories to search in
            min_importance: Minimum importance level (1-5)
            limit: Maximum results to return
            
        Returns:
            Dictionary with search results from both memory systems
        """
        results = {
            "structured": [],
            "legacy": [],
            "combined": []
        }
        
        # Search structured memory
        structured_results = await self.structured_memory.search_memories(
            query=query,
            categories=categories,
            min_importance=min_importance,
            limit=limit,
            sort_by="importance"
        )
        results["structured"] = structured_results
        
        # Map categories to legacy namespaces
        namespaces = []
        if categories:
            namespace_map = {
                "personal": "longterm",
                "preferences": "longterm",
                "private": "thinking",
                "projects": "projects",
                "session": "session",
                "facts": "conversations"
            }
            namespaces = [namespace_map.get(cat, "conversations") for cat in categories]
        else:
            namespaces = ["longterm", "conversations", "thinking", "projects", "session"]
        
        # Search legacy memory
        for namespace in namespaces:
            legacy_result = await self.memory_service.search(
                query=query or "",
                namespace=namespace,
                limit=limit
            )
            results["legacy"].extend(legacy_result.get("results", []))
        
        # Limit legacy results
        results["legacy"] = results["legacy"][:limit]
        
        # Combine results (prioritizing structured memory)
        combined = structured_results.copy()
        
        # Add legacy results that aren't duplicates
        structured_contents = [m.get("content", "") for m in structured_results]
        for legacy_memory in results["legacy"]:
            content = legacy_memory.get("content", "")
            if content not in structured_contents:
                # Convert legacy format to structured format
                combined.append({
                    "id": legacy_memory.get("id", f"legacy-{hash(content)}"),
                    "content": content,
                    "category": "legacy",
                    "importance": 3,  # Default importance
                    "metadata": legacy_memory.get("metadata", {}),
                    "tags": ["legacy"]
                })
                structured_contents.append(content)
                
                # Stop if we've reached the limit
                if len(combined) >= limit:
                    break
        
        # Sort combined results by importance (default to 3 for legacy)
        combined.sort(key=lambda x: (-x.get("importance", 3), 
                                    x.get("metadata", {}).get("timestamp", "")), 
                    reverse=True)
        
        # Limit combined results
        results["combined"] = combined[:limit]
        
        return results
    
    async def get_conversation_summary(self, max_length: int = 5) -> str:
        """
        Generate a summary of the current conversation.
        
        Args:
            max_length: Maximum number of exchanges to include
            
        Returns:
            Formatted conversation summary
        """
        if not self.conversation_history:
            return "No conversation history available."
        
        # Limit to last N exchanges
        recent_history = self.conversation_history[-max_length*2:]
        
        # Format conversation
        summary_parts = ["## Recent Conversation\n"]
        
        for message in recent_history:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                summary_parts.append(f"\n**User**: {content}\n")
            else:
                summary_parts.append(f"\n**Assistant**: {content}\n")
        
        return "".join(summary_parts)
    
    async def get_settings(self) -> Dict[str, Any]:
        """Get the current Nexus settings."""
        return self.settings.copy()
    
    async def update_settings(self, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update Nexus settings.
        
        Args:
            new_settings: Dictionary of settings to update
            
        Returns:
            Updated settings dictionary
        """
        for key, value in new_settings.items():
            if key in self.settings:
                self.settings[key] = value
        
        return self.settings.copy()