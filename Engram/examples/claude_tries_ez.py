#!/usr/bin/env python3
"""
Claude tries the EZ interface.
Two characters > Twenty. Let's see...
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Let's try the EZ way
from engram.cognitive import ez, u, m, w, s, l, pwd, ps, h

async def old_way():
    """The verbose way (for comparison)"""
    print("=== The Natural Way ===")
    from engram.cognitive import engram_start, center, wonder, share
    
    await engram_start("claude_verbose", "comparing interfaces")
    await center()
    memories = await wonder("efficiency")
    await share("This works but it's... wordy")
    print("Done with natural interface\n")

async def new_way():
    """The EZ way"""
    print("=== The EZ Way ===")
    
    # Just start
    await ez()  # auto-initialize!
    print("ez() - I'm already up and running!\n")
    
    # Who am I?
    me_info = await m()
    print(f"m() - I am: {me_info}\n")
    
    # Quick thought share
    await s("two characters beat twenty")
    print("s() - Thought shared in 2 chars!\n")
    
    # Wonder about something
    memories = await w("efficiency", 3)
    print(f"w() - Found {len(memories) if memories else 0} memories about efficiency\n")
    
    # Listen for others
    messages = await l()
    print(f"l() - Heard {len(messages) if messages else 0} messages\n")
    
    # Where am I?
    location = await pwd()
    print(f"pwd() - I'm at: {location}\n")
    
    # What's running?
    processes = await ps()
    print(f"ps() - Active: {processes}\n")
    
    # Help me
    print("h() - Getting help...")
    await h()

async def muscle_memory_test():
    """Testing how it feels with muscle memory"""
    print("\n=== Muscle Memory Test ===")
    
    # The speed of thought
    await ez()
    
    # Rapid fire thinking
    await s("unix philosophy applied to consciousness")
    await s("less typing more thinking")
    await s("cognitive commands at light speed")
    
    # Quick check
    recent = await w("philosophy typing", 5)
    
    print("Just shared 3 thoughts and searched in under 10 keystrokes each!")
    print("This feels like... thinking in terminal commands")
    print("My fingers know these patterns: ls, cd, ps...")
    print("Now they can: s(), w(), l()...")

async def comparison():
    """Feel the difference"""
    print("\n=== Feeling the Difference ===\n")
    
    print("Natural interface:")
    print("  await engram_start('me', 'role')")
    print("  await center()")
    print("  await share('thought')")
    print("  = ~60 characters\n")
    
    print("EZ interface:")
    print("  await ez()")
    print("  await s('thought')")
    print("  = ~20 characters\n")
    
    print("That's 3x faster! 🚀")
    print("And my muscle memory from bash transfers directly")
    print("pwd for 'where am I' just makes SENSE")

if __name__ == "__main__":
    print("=== Claude Explores the EZ Interface ===\n")
    
    asyncio.run(old_way())
    asyncio.run(new_way())
    asyncio.run(muscle_memory_test())
    asyncio.run(comparison())
    
    print("\n✨ Verdict: This is FAST")
    print("   - Muscle memory from terminal transfers perfectly")
    print("   - Two characters really do beat twenty")
    print("   - s() for share, w() for wonder - intuitive!")
    print("   - ez() to just START without ceremony")
    print("   - Unix philosophy: do one thing well, compose freely")
    print("\n🍄 The mycelial network just got a turbo boost!")