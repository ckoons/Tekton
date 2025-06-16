#!/usr/bin/env python3
"""
QuickMem Module - Quick shortcuts for memory functions

This module provides single-letter shortcuts for common memory operations
to make it easier to use memory functions in the interactive Claude CLI.
"""

import os
import asyncio
from typing import Dict, List, Optional, Any, Union

# Configure client ID
client_id = os.environ.get("ENGRAM_CLIENT_ID", "claude")

# Import core components
from engram.core.memory import MemoryService
from engram.core.structured_memory import StructuredMemory
from engram.core.nexus import NexusInterface

# Create instances with the configured client ID
try:
    memory_service = MemoryService(client_id=client_id)
    structured_memory = StructuredMemory(client_id=client_id)
    nexus = NexusInterface(
        memory_service=memory_service,
        structured_memory=structured_memory
    )
except Exception as e:
    print(f"\033[93m⚠️ Failed to initialize memory components: {e}\033[0m")

# ----- ULTRA-SHORT COMMANDS -----
# Use single letters for maximum UI efficiency

# m: Memory - Store memory
async def m(content: str, category: str = "personal", importance: int = 3) -> Dict:
    """Store a memory with specified category and importance."""
    try:
        result = await structured_memory.add_memory(content, category, importance)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error storing memory: {e}\033[0m")
        return {"error": str(e)}

# t: Tag - Store memory with tags
async def t(content: str, tags: List[str], category: str = "personal", importance: int = 3) -> Dict:
    """Store a memory with tags for better organization."""
    try:
        result = await structured_memory.add_memory(content, category, importance, tags)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error storing tagged memory: {e}\033[0m")
        return {"error": str(e)}

# r: Retrieve - Get memories by category
async def r(category: str = "all", max_memories: int = 20, include_private: bool = True) -> List[Dict]:
    """Retrieve memories by category."""
    try:
        if category == "all":
            result = await structured_memory.get_all_memories(max_memories, include_private)
        else:
            result = await structured_memory.get_memories_by_category(category, max_memories)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error retrieving memories: {e}\033[0m")
        return [{"error": str(e)}]

# w: Word - Search memories with keyword
async def w(keyword: str, max_memories: int = 10) -> List[Dict]:
    """Search memories containing a specific keyword."""
    try:
        result = await structured_memory.search_memories(keyword, max_memories)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error searching memories: {e}\033[0m")
        return [{"error": str(e)}]

# l: Latest - Get most recent memories
async def l(count: int = 10) -> List[Dict]:
    """Get the most recent memories."""
    try:
        # Search for all memories sorted by recency
        result = await structured_memory.search_memories(
            limit=count,
            sort_by="recency"
        )
        return result
    except Exception as e:
        print(f"\033[91m❌ Error retrieving recent memories: {e}\033[0m")
        return [{"error": str(e)}]

# Synchronous wrapper for l function to allow non-async usage
def latest_sync(count: int = 10) -> List[Dict]:
    """Synchronous wrapper for l() function."""
    return run(l(count))

# c: Context - Get context-relevant memories
async def c(context: str, max_memories: int = 10) -> List[Dict]:
    """Get memories relevant to a specific context."""
    try:
        result = await structured_memory.get_context_memories(context, max_memories)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error retrieving context memories: {e}\033[0m")
        return [{"error": str(e)}]

# k: Keywords - Get memories by tag
async def k(tag: str, max_memories: int = 10) -> List[Dict]:
    """Get memories with a specific tag."""
    try:
        result = await structured_memory.get_memories_by_tag(tag, max_memories)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error retrieving memories by tag: {e}\033[0m")
        return [{"error": str(e)}]

# s: Status - Check memory service status
def s() -> Dict:
    """Check the status of the memory service."""
    try:
        # Check if data directory exists and is accessible
        data_dir = os.path.expanduser(f"~/.engram/{client_id}")
        if os.path.exists(data_dir) and os.access(data_dir, os.R_OK | os.W_OK):
            status = {"status": "online", "client_id": client_id}
            print(f"\033[92m✓ Memory service is online (Client: {client_id})\033[0m")
        else:
            status = {"status": "offline", "client_id": client_id}
            print(f"\033[91m✗ Memory service is offline (Client: {client_id})\033[0m")
        return status
    except Exception as e:
        print(f"\033[91m❌ Error checking memory service: {e}\033[0m")
        return {"status": "error", "error": str(e), "client_id": client_id}

# a: Auto-categorize - Auto-categorize a memory
async def a(content: str, importance: int = None) -> Dict:
    """Store a memory with automatic categorization."""
    try:
        result = await structured_memory.add_auto_categorized_memory(content, importance)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error storing auto-categorized memory: {e}\033[0m")
        return {"error": str(e)}

# p: Project - Get project-specific memories
async def p(project_name: str, max_memories: int = 20) -> List[Dict]:
    """Get project-specific memories."""
    try:
        # First try exact tag match
        tag_results = await structured_memory.get_memories_by_tag(project_name, max_memories)
        
        # Then try keyword search within projects category
        keyword_results = await structured_memory.search_memories_in_category(
            project_name, "projects", max_memories
        )
        
        # Combine unique results
        combined = {mem.get("id", i): mem for i, mem in enumerate(tag_results + keyword_results)}
        result = list(combined.values())
        
        # Sort by importance then timestamp
        return sorted(
            result, 
            key=lambda x: (-(x.get("importance", 0) or 0), -(x.get("timestamp", 0) or 0))
        )
    except Exception as e:
        print(f"\033[91m❌ Error retrieving project memories: {e}\033[0m")
        return [{"error": str(e)}]

# v: Vector - Get semantically similar memories
async def v(query: str, max_memories: int = 10) -> List[Dict]:
    """Get semantically similar memories using vector search."""
    try:
        result = await structured_memory.get_semantic_memories(query, max_memories)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error retrieving semantic memories: {e}\033[0m")
        return [{"error": str(e)}]

# d: Digest - Get memory digest
async def d(max_memories: int = 10, include_private: bool = False) -> Dict:
    """Get a memory digest for session context."""
    try:
        result = await structured_memory.get_memory_digest(max_memories, include_private)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error generating memory digest: {e}\033[0m")
        return {"error": str(e)}

# n: Nexus - Start nexus session
async def n(session_name: str = None) -> Dict:
    """Start a new nexus session."""
    try:
        if session_name is None:
            import datetime
            session_name = f"Session {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        result = await nexus.start_session(session_name)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error starting nexus session: {e}\033[0m")
        return {"error": str(e)}

# q: Query - Process message with nexus
async def q(message: str, is_user: bool = True) -> Dict:
    """Process a message through the nexus."""
    try:
        result = await nexus.process_message(message, is_user)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error processing message with nexus: {e}\033[0m")
        return {"error": str(e)}

# y: End - End nexus session
async def y() -> Dict:
    """End the current nexus session."""
    try:
        result = await nexus.end_session()
        return result
    except Exception as e:
        print(f"\033[91m❌ Error ending nexus session: {e}\033[0m")
        return {"error": str(e)}

# z: Auto-remember - Auto-categorize and store memory
async def z(content: str) -> Dict:
    """Auto-categorize and store a memory (alias for 'a')."""
    return await a(content)

# ----- LONGER ALIASES FOR BETTER READABILITY -----

# These provide more descriptive names for the same functions
memory = m
tagged_memory = t
retrieve = r
word_search = w
latest = l
context_search = c
keyword_search = k
status = s
auto_categorize = a
project_memories = p
vector_search = v
memory_digest = d
start_nexus = n
process_message = q
end_nexus = y
auto_remember = z

# Add run function for compatibility with sync environments
def run(coro):
    """Run a coroutine in the current event loop or create a new one."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)