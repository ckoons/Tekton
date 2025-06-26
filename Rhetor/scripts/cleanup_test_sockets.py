#!/usr/bin/env python3
"""Clean up test sockets from the registry."""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rhetor.core.ai_socket_registry import get_socket_registry


async def cleanup_test_sockets():
    """Remove all test sockets."""
    print("🧹 Cleaning up test sockets...")
    
    registry = await get_socket_registry()
    
    # List of test socket patterns to remove
    test_patterns = [
        "local-test",
        "persist-test", 
        "debug-test",
        "test-model",
        "athena-001",  # From early tests
        "health-test"
    ]
    
    removed = []
    for socket_id in list(registry.sockets.keys()):
        # Check if it's a test socket
        if any(pattern in socket_id for pattern in test_patterns):
            if await registry.delete(socket_id):
                removed.append(socket_id)
                print(f"  ✅ Removed: {socket_id}")
    
    # List remaining sockets
    remaining = await registry.list_sockets()
    print(f"\n📋 Remaining sockets: {len(remaining)}")
    for sock in remaining:
        print(f"  - {sock['socket_id']} ({sock['model']})")
    
    print(f"\n✅ Cleanup complete! Removed {len(removed)} test sockets")


if __name__ == "__main__":
    asyncio.run(cleanup_test_sockets())