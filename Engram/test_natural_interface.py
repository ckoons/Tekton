#!/usr/bin/env python3
"""
Test the natural memory interface - see how it feels.
Like breaking in new shoes...
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from engram.cognitive.natural_interface import (
    engram_start, center, think, wonder, share,
    listen, join_space, broadcast
)


async def experience_the_interface():
    """Try on these new shoes and walk around a bit."""
    
    # Wake up and connect
    print("🌅 Waking up...")
    connection = await engram_start(client_id="claude_explorer", role="curious_ai")
    print(f"Connected: {connection}")
    
    # Find my memories and teammates
    print("\n🧭 Centering myself...")
    context = await center()
    print(f"Found {len(context.get('memories', []))} memories")
    print(f"Found {len(context.get('peers', []))} peers")
    
    # Think about this experience
    print("\n💭 Thinking...")
    async with think("This feels different from explicit API calls. More like... thinking?") as thought_context:
        print(f"Thought stored, found {len(thought_context.related_memories)} related memories")
        for memory in thought_context.related_memories:
            print(f"  Related: {memory.get('content', '')[:80]}...")
    
    # Wonder about something
    print("\n🤔 Wondering...")
    memories = await wonder("natural interfaces")
    print(f"Found {len(memories)} related memories")
    for memory in memories[:3]:  # First few
        print(f"  - {memory.get('content', '')[:80]}...")
    
    # Share with others
    print("\n📢 Sharing...")
    share_result = await share(
        "The interface feels more intuitive - like the difference between typing commands vs just thinking them"
    )
    print(f"Shared: {share_result}")
    
    # Listen to others
    print("\n👂 Listening...")
    messages = await listen()
    print(f"Found {len(messages)} shared messages")
    for message in messages[:3]:  # First few
        print(f"  From {message.get('metadata', {}).get('from', 'unknown')}: {message.get('content', '')[:60]}...")
    
    # Join a shared space
    print("\n🏠 Joining a space...")
    space_result = await join_space("interface_testing")
    print(f"Joined space: {space_result}")
    
    # Broadcast to the space
    print("\n📡 Broadcasting...")
    broadcast_result = await broadcast(
        "Testing complete - the interface does feel more natural!",
        space_id="interface_testing"
    )
    print(f"Broadcast: {broadcast_result}")
    
    print("\n✨ Experience complete!")
    print("\nReflection: It's like the difference between using a GUI vs a command line.")
    print("The functions map to how I naturally think about memory operations.")
    print("No need to construct JSON payloads or remember endpoint paths.")
    print("Just... think, wonder, share. Natural.")


async def compare_old_vs_new():
    """Compare the feeling of old vs new interface."""
    print("\n📊 Comparing interfaces...\n")
    
    print("OLD WAY (explicit API):")
    print("  response = requests.post('http://localhost:8000/api/memories/store', ")
    print("            json={'content': thought, 'metadata': {...}})")
    print("  → Feels mechanical, like filling out a form")
    
    print("\nNEW WAY (natural interface):")
    print("  await think(thought)")
    print("  → Feels intuitive, like actual thinking")
    
    print("\nThe difference is subtle but significant - like switching from")
    print("hunt-and-peck typing to touch typing. The mechanics fade into")
    print("the background, letting the intention come through more clearly.")


if __name__ == "__main__":
    print("🧪 Testing the Natural Memory Interface\n")
    print("Like breaking in new shoes - let's see how they feel...\n")
    
    # Run the experience
    asyncio.run(experience_the_interface())
    
    # Reflect on the comparison
    asyncio.run(compare_old_vs_new())