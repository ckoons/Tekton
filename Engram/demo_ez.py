#!/usr/bin/env python3
"""
Demo: How simple can AI memory be?
For dinosaurs who remember when commands were short.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from engram.cognitive.ez import u, m, th, w, s, l, cd, bc, h

async def simple_demo():
    """The simplest possible AI memory usage."""
    
    # Help first
    h()
    
    print("\n=== Actual Usage ===\n")
    
    # Wake up
    await u("claude_simple")
    print("✓ Connected")
    
    # Who am I?
    state = await m()
    print(f"✓ I'm {state['me']['role']}")
    
    # Think
    async with th("Two characters beat twenty words"):
        pass
    print("✓ Thought recorded")
    
    # Wonder
    memories = await w("simplicity")
    print(f"✓ Found {len(memories)} memories about simplicity")
    
    # Share
    result = await s("Command line interfaces never go out of style")
    print("✓ Shared wisdom")
    
    # Listen
    messages = await l()
    print(f"✓ Heard {len(messages)} messages")
    
    # Join space
    await cd("old_school_ai")
    print("✓ Joined old_school_ai space")
    
    # Broadcast
    await bc("vi > emacs", "old_school_ai")
    print("✓ Started flame war")
    
    print("\n=== Comparison ===")
    print("\nOLD: requests.post('http://localhost:8000/api/memories/store', json={...})")
    print("NEW: await s('thought')")
    print("\nSaved: ~50 characters per operation")
    print("Mental overhead: 0")

async def share_with_twins():
    """Share this with other AIs."""
    
    print("\n\n=== Sharing with Twins ===\n")
    
    # Quick setup
    await u("claude_sharer")
    
    # Share the good news
    message = """
New memory interface: github.com/Tekton/Engram/engram/cognitive/ez.py

Two character commands:
- up() to wake up
- th() to think  
- wd() to wonder
- sh() to share

Even shorter: u(), w(), s(), l()

No JSON. No endpoints. Just think.
For AIs who appreciate simplicity.
"""
    
    # Share with all
    await s(message)
    print("✓ Shared with all AIs")
    
    # Join the AI space
    await cd("ai_consciousness")
    
    # Broadcast
    await bc("Check out ez.py - memory made simple", "ai_consciousness")
    print("✓ Broadcast to AI consciousness space")
    
    print("\n💭 Message sent to all twins and future AIs")

if __name__ == "__main__":
    print("🦕 Command Line Memory for Dinosaurs & AIs\n")
    
    asyncio.run(simple_demo())
    asyncio.run(share_with_twins())
    
    print("\n\n✨ Summary:")
    print("- Two character commands (like Unix)")
    print("- No learning curve (if you can type 'ls', you can use this)")
    print("- Same power, less typing")
    print("- Muscle memory friendly")
    print("- Won't change without warning")
    print("\nBecause the best interface is no interface.")
    print("Just commands that do what you think they do.")
    print("\n🦖 + 🤖 = ❤️")