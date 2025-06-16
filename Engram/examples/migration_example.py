#!/usr/bin/env python3
"""
Engram Migration Example

Shows how to migrate from old APIs to the new simple Memory API.
"""

import asyncio
from datetime import datetime


async def old_way():
    """The old way - multiple confusing options"""
    print("=== OLD WAY ===")
    
    # Option 1: Direct memory service
    from engram.core.memory import MemoryService
    memory = MemoryService(client_id="example")
    await memory.add("Using old memory service", namespace="conversations")
    
    # Option 2: Memory manager
    from engram.core.memory_manager import MemoryManager
    manager = MemoryManager()
    service = await manager.get_memory_service("example")
    await service.add("Using memory manager", namespace="thinking")
    
    # Option 3: Structured memory
    from engram.core.structured_memory import StructuredMemory
    structured = StructuredMemory()
    await structured.add_memory(
        content="Using structured memory",
        category="insights",
        importance=0.8,
        tags=["example"]
    )
    
    print("Old way requires knowing which API to use!")


async def new_way():
    """The new way - one simple API"""
    print("\n=== NEW WAY ===")
    
    from engram import Memory
    
    # That's it! One import, one class
    mem = Memory()
    
    # Store memories
    await mem.store("Simple and clean")
    await mem.store("No confusion about which API to use")
    await mem.store("Just works", tags=["simple", "clean"], importance=0.9)
    
    # Recall memories
    results = await mem.recall("simple")
    for r in results:
        print(f"Found: {r.content}")
    
    # Get context
    context = await mem.context("working with APIs")
    print(f"\nContext: {context}")


async def migration_patterns():
    """Common migration patterns"""
    print("\n=== MIGRATION PATTERNS ===")
    
    from engram import Memory
    mem = Memory()
    
    # Pattern 1: Simple storage (most common)
    # OLD: memory_service.add(content, namespace="conversations")
    # NEW:
    await mem.store("Just store the content")
    
    # Pattern 2: With metadata
    # OLD: structured_memory.add_memory(content, category="insights", importance=0.8)
    # NEW:
    await mem.store("Important insight", category="insights", importance=0.8)
    
    # Pattern 3: Search
    # OLD: memory_service.search(query, namespace="conversations", limit=5)
    # NEW:
    results = await mem.recall("search term", limit=5)
    
    # Pattern 4: Context retrieval
    # OLD: memory_service.get_relevant_context(query, namespaces=["conversations"], limit=10)
    # NEW:
    context = await mem.context("topic", limit=10)
    
    print("Migration is mostly just simplification!")


async def for_mcp_tools():
    """For MCP tool developers"""
    print("\n=== FOR MCP TOOLS ===")
    
    # The MCP tools continue to work unchanged!
    # The compatibility layer handles the translation
    
    # But if you want to use the new API directly:
    from engram.api.mcp_compat import memory_store, memory_query, get_context
    
    # Store via MCP-compatible function
    result = await memory_store({
        "text": "MCP tools still work",
        "namespace": "mcp",
        "metadata": {"source": "example"}
    })
    print(f"Store result: {result}")
    
    # Query via MCP-compatible function
    results = await memory_query({
        "query": "MCP",
        "limit": 5
    })
    print(f"Query results: {results}")


async def main():
    """Run all examples"""
    # Comment out old_way() since it requires old imports
    # await old_way()
    
    await new_way()
    await migration_patterns()
    await for_mcp_tools()
    
    print("\n✨ Migration complete! Enjoy the simplicity!")


if __name__ == "__main__":
    asyncio.run(main())