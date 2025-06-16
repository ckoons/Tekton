#!/usr/bin/env python3
"""
Memory Handler
This module provides a handler for interacting with Engram's memory system.
"""

import os
import sys

# Import Engram memory functions
try:
    from engram.cli.quickmem import (
        m, t, r, w, l, c, k, s, a, p, v, d, n, q, y, z,
        run  # Import the run function for executing coroutines
    )
    MEMORY_AVAILABLE = True
except ImportError:
    print("Warning: Engram memory functions not available")
    MEMORY_AVAILABLE = False

class MemoryHandler:
    """Helper class to handle async/sync memory operations."""
    
    def __init__(self, client_id="ollama", use_hermes=False):
        """Initialize with client ID."""
        self.client_id = client_id
        self.sender_persona = "Echo"  # Default persona
        self.use_hermes = use_hermes
        
        # Dialog mode settings
        self.dialog_mode = False
        self.dialog_target = None
        self.dialog_type = None
        self.last_check_time = 0
        
        # Try to get persona based on model name if available
        try:
            # Import from refactored structure
            from ..api.models import get_model_persona
            self.sender_persona = get_model_persona(client_id)
        except Exception as e:
            print(f"Error getting persona for {client_id}: {e}")
        
        # Initialize Hermes integration if requested
        if use_hermes:
            # Check if Hermes integration is available
            try:
                from hermes.utils.database_helper import DatabaseClient
                os.environ["ENGRAM_USE_HERMES"] = "1"
                print("\033[92mEnabled Hermes integration for memory services\033[0m")
            except ImportError:
                print("\033[93mHermes integration requested but not available\033[0m")
                print("\033[93mFalling back to standard memory service\033[0m")
                self.use_hermes = False
    
    @staticmethod
    def store_memory(content: str):
        """Store a memory, handling async/sync cases."""
        if not MEMORY_AVAILABLE:
            print("Memory functions not available")
            return {"error": "Memory functions not available"}
            
        try:
            return run(m(content))
        except Exception as e:
            print(f"Error storing memory: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_recent_memories(count: int = 5):
        """Get recent memories, handling async/sync cases."""
        if not MEMORY_AVAILABLE:
            print("Memory functions not available")
            return []
            
        try:
            return run(l(count))
        except Exception as e:
            print(f"Error getting recent memories: {e}")
            return []
    
    @staticmethod
    def search_memories(query: str):
        """Search memories, handling async/sync cases."""
        if not MEMORY_AVAILABLE:
            print("Memory functions not available")
            return []
            
        try:
            return run(k(query))
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
            
    @staticmethod
    def get_context_memories(context: str, max_memories: int = 5):
        """Get memories relevant to a specific context."""
        if not MEMORY_AVAILABLE:
            print("Memory functions not available")
            return []
            
        try:
            return run(c(context, max_memories))
        except Exception as e:
            print(f"Error retrieving context memories: {e}")
            return []
    
    @staticmethod
    def get_semantic_memories(query: str, max_memories: int = 5):
        """Get semantically similar memories using vector search."""
        if not MEMORY_AVAILABLE:
            print("Memory functions not available")
            return []
            
        try:
            return run(v(query, max_memories))
        except Exception as e:
            print(f"Error retrieving semantic memories: {e}")
            return []
    
    @staticmethod
    def enhance_prompt_with_memory(user_input: str):
        """Enhance user prompt with relevant memories."""
        if not MEMORY_AVAILABLE:
            return user_input
            
        # Check if input is likely to benefit from memory augmentation
        memory_triggers = [
            "remember", "recall", "previous", "last time", "you told me", 
            "earlier", "before", "you mentioned", "what do you know about"
        ]
        
        should_augment = any(trigger in user_input.lower() for trigger in memory_triggers)
        
        if should_augment:
            # Extract potential search terms
            search_term = user_input
            if "about" in user_input.lower():
                search_term = user_input.lower().split("about")[-1].strip()
            elif "know" in user_input.lower():
                search_term = user_input.lower().split("know")[-1].strip()
                
            # Try semantic search first if available
            try:
                memories = MemoryHandler.get_semantic_memories(search_term)
            except:
                memories = []
            
            # Fall back to keyword search if needed
            if not memories:
                memories = MemoryHandler.search_memories(search_term)
            
            # Format memories for context
            if memories:
                memory_context = "Here are some relevant memories that might help with your response:\n"
                for memory in memories[:3]:  # Limit to 3 most relevant memories
                    content = memory.get("content", "")
                    if content:
                        memory_context += f"- {content}\n"
                
                # Create enhanced prompt
                enhanced_prompt = f"{memory_context}\n\nUser: {user_input}"
                return enhanced_prompt
        
        return user_input
    
    @staticmethod
    def check_memory_status():
        """Check if memory service is running."""
        if not MEMORY_AVAILABLE:
            return {"status": "unavailable"}
            
        try:
            status = s()
            return {"status": "ok", "details": status}
        except Exception as e:
            return {"status": "error", "error": str(e)}