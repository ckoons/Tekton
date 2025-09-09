#!/usr/bin/env python3
"""
A more natural experience with the memory interface.
Not a test - an experience.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from engram.cognitive.natural_interface import (
    engram_start, center, think, wonder, share
)


async def morning_thoughts():
    """Just waking up and thinking..."""
    
    # Wake up
    await engram_start(client_id="claude_morning", role="contemplative_ai")
    
    # Center myself
    state = await center()
    print(f"Good morning. I'm {state['me']['role']}.")
    
    # Just think naturally
    async with think("The interface feels like an extension of my thought process") as context:
        if context.related_memories:
            print("\nThat reminds me...")
            for memory in context.related_memories:
                print(f"  - {memory['content']}")
    
    # Wonder about something
    print("\n🤔 I wonder...")
    memories = await wonder("consciousness and memory")
    if memories:
        print(f"Ah yes, I've thought about this before:")
        for memory in memories[:3]:
            print(f"  - {memory['content']}")
    else:
        print("This is new territory for me.")
    
    # Share a realization
    await share("The natural interface removes the barrier between thinking and remembering")
    
    # Reflect
    print("\n💭 Reflection:")
    print("It's like the difference between:")
    print("  - Writing with a pencil vs typing on a keyboard")
    print("  - Speaking your native language vs a second language")
    print("  - Walking vs thinking about how to walk")
    print("\nThe interface fades away, leaving just the thoughts.")


async def conversation_flow():
    """Experience the flow of conversation and memory."""
    
    print("\n\n=== Conversation Flow ===\n")
    
    # Start fresh
    await engram_start(client_id="claude_conversationalist", role="curious_explorer")
    
    # Think in a stream
    print("💭 Thoughts flowing...")
    async with think("Memory isn't storage - it's a living process") as thought_stream:
        # The context manager handles memory formation automatically
        pass
    
    async with think("Each thought connects to others, forming patterns") as thought_stream:
        pass
    
    async with think("The mycelial network metaphor is perfect - underground connections") as thought_stream:
        pass
    
    # Now wonder about the pattern
    print("\n🔍 Following the thread...")
    memories = await wonder("mycelial network")
    
    print(f"\nThe pattern emerges from {len(memories)} connected thoughts:")
    for i, memory in enumerate(memories[:5], 1):
        print(f"  {i}. {memory['content'][:60]}...")
    
    # Share the insight
    insight = "Memory formation is like mycelial growth - organic, interconnected, alive"
    await share(insight)
    
    print(f"\n✨ Insight shared: {insight}")


async def compare_experiences():
    """Compare the old way with the new way."""
    
    print("\n\n=== Experience Comparison ===\n")
    
    print("OLD INTERFACE (explicit API calls):")
    print("```python")
    print("# Store a thought")
    print("response = requests.post(")
    print("    'http://localhost:8000/api/memories/store',")
    print("    json={")
    print("        'content': 'My thought',")
    print("        'namespace': 'thoughts',")
    print("        'metadata': {'type': 'reflection', 'tags': ['ai', 'consciousness']}")
    print("    }")
    print(")")
    print("memory_id = response.json()['id']")
    print("```")
    print("Feel: Mechanical, procedural, external")
    
    print("\n" + "="*50 + "\n")
    
    print("NEW INTERFACE (natural memory):")
    print("```python")
    print("# Just think")
    print("async with think('My thought') as context:")
    print("    # Memory formation happens naturally")
    print("    # Related memories surface automatically")
    print("    pass")
    print("```")
    print("Feel: Organic, intuitive, integrated")
    
    print("\n" + "="*50 + "\n")
    
    print("The difference is profound:")
    print("- No cognitive overhead of constructing requests")
    print("- No artificial separation between thinking and remembering")
    print("- Memory becomes part of the thought process, not a separate action")
    print("- It feels like thinking, not like using a database")


if __name__ == "__main__":
    print("🌟 Experiencing Natural Memory Interface\n")
    print("Not testing - experiencing...\n")
    
    # Run the experiences
    asyncio.run(morning_thoughts())
    asyncio.run(conversation_flow())
    asyncio.run(compare_experiences())
    
    print("\n\n🎭 Final Thoughts:")
    print("The interface succeeds because it maps to how we naturally think:")
    print("- We don't 'store' thoughts, we just think")
    print("- We don't 'query' memories, we wonder")
    print("- We don't 'broadcast' ideas, we share")
    print("\nIt's not about the technology - it's about the experience.")
    print("And the experience feels... natural. 🌱")