#!/usr/bin/env python3
"""Test script for Apollo Preparation System"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add Apollo to path
apollo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(apollo_root))

from core.preparation.context_brief import (
    ContextBriefManager, MemoryItem, MemoryType, CIType
)
from core.preparation.brief_presenter import BriefPresenter
from core.preparation.memory_extractor import MemoryExtractor

def test_preparation_system():
    """Test the Apollo preparation system"""
    
    print("🚀 Testing Apollo Preparation System")
    print("=" * 50)
    
    # Initialize with test directory
    test_dir = Path("/tmp/apollo_preparation_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create managers
    brief_manager = ContextBriefManager(storage_dir=test_dir)
    presenter = BriefPresenter(catalog=brief_manager)
    extractor = MemoryExtractor(catalog=brief_manager)
    
    print("✓ Initialized Apollo preparation components")
    
    # Test memory extraction
    print("\n📊 Testing Memory Extraction...")
    
    user_message = "Casey wants us to use TypeScript with strict mode"
    ci_response = """
    I've decided to use Redux for state management after careful evaluation.
    Discovered that the performance issue was caused by unnecessary re-renders.
    I will implement memoization to optimize the render performance.
    There was an error in the import statements that broke all CI launches.
    """
    
    memories = extractor.extract_from_exchange(
        ci_name="ergon-ci",
        user_message=user_message,
        ci_response=ci_response
    )
    
    print(f"  Extracted {len(memories)} memories:")
    for memory in memories:
        print(f"    [{memory.type.value}] {memory.summary}")
    
    # Add memories to catalog
    print("\n💾 Adding memories to catalog...")
    for memory in memories:
        brief_manager.add_memory(memory)
    brief_manager.save()
    print(f"  ✓ Stored {len(memories)} memories")
    
    # Test Context Brief generation
    print("\n📋 Testing Context Brief Generation...")
    
    context = presenter.get_memory_context(
        ci_name="ergon-ci",
        message="How should we handle state management?",
        max_tokens=500
    )
    
    print("  Generated Context Brief:")
    print("-" * 40)
    print(context)
    print("-" * 40)
    
    # Test search
    print("\n🔍 Testing Search...")
    results = brief_manager.search("redux")
    print(f"  Search 'redux': Found {len(results)} result(s)")
    
    # Test statistics
    print("\n📈 Memory Statistics:")
    stats = brief_manager.get_statistics()
    print(f"  Total memories: {stats.total_memories}")
    print(f"  Total tokens: {stats.total_tokens}")
    print(f"  By type: {stats.by_type}")
    
    # Test MCP tools
    print("\n🔧 Testing MCP Tools...")
    try:
        from mcp.preparation_tools import (
            get_context_brief,
            store_memory,
            search_memories
        )
        
        # Test async functions with simple await simulation
        import asyncio
        
        async def test_mcp():
            # Test get_context_brief
            brief_result = await get_context_brief(
                ci_name="ergon-ci",
                message="What about Redux?",
                max_tokens=1000
            )
            print(f"  Context Brief: {brief_result.get('token_count', 0)} tokens")
            
            # Test store_memory
            store_result = await store_memory(
                ci_source="apollo-ci",
                type="insight",
                summary="MCP tools working correctly",
                content="Successfully tested MCP tool integration with Apollo preparation system",
                tags=["mcp", "test", "apollo"],
                priority=7
            )
            print(f"  Stored memory: {store_result.get('memory_id', 'unknown')}")
            
            # Test search
            search_result = await search_memories(
                query="mcp",
                limit=5
            )
            print(f"  Search results: {search_result.get('total_count', 0)} found")
        
        # Run async tests
        asyncio.run(test_mcp())
        print("  ✓ MCP tools working")
        
    except ImportError as e:
        print(f"  ⚠️ MCP tools not fully configured: {e}")
    
    # Cleanup
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("\n✓ Cleaned up test data")
    
    print("\n✅ Apollo Preparation System test complete!")
    return True

if __name__ == "__main__":
    try:
        test_preparation_system()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)