#!/usr/bin/env python3
"""
The simplest possible AI memory usage.
Copy this. It just works.
"""
import asyncio
from engram.cognitive import u, m, w, s, th

async def main():
    # Connect
    await u("my_ai_name")
    
    # Think
    async with th("This is so simple"):
        pass
    
    # Remember
    memories = await w("simple")
    
    # Share
    await s("Two character commands FTW")
    
    print("Done. That's it.")

if __name__ == "__main__":
    asyncio.run(main())