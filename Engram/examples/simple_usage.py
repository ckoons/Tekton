#!/usr/bin/env python3
"""
Engram Simple Usage Example

This shows how easy it is to use Engram's new simplified API.
"""

import asyncio
from engram import Memory


async def main():
    # Create a memory instance - that's it!
    mem = Memory()
    
    # Store some thoughts
    await mem.store("Casey taught me about keeping things simple")
    await mem.store("Complex code is a liability, not an asset")
    await mem.store("The best interface is no interface")
    
    # Store with metadata
    await mem.store("Silent by default is respectful", 
                    tags=["design", "philosophy"],
                    importance=0.9)
    
    # Recall memories
    print("=== Searching for 'simple' ===")
    memories = await mem.recall("simple")
    for m in memories:
        print(f"- {m.content}")
    
    print("\n=== Searching for 'interface' ===")
    memories = await mem.recall("interface")
    for m in memories:
        print(f"- {m.content}")
    
    # Get context for a task
    print("\n=== Context for 'designing APIs' ===")
    context = await mem.context("designing APIs")
    print(context)


if __name__ == "__main__":
    # Run without any logging noise (unless ENGRAM_DEBUG=true)
    asyncio.run(main())