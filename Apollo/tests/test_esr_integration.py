#!/usr/bin/env python3
"""
Test Apollo-ESR Integration

Tests the integration of Apollo with the ESR (Encoding Storage Retrieval) system.
Verifies that memories are stored in ESR and can be retrieved with semantic search.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project roots to path
sys.path.insert(0, os.path.join(os.environ.get('TEKTON_ROOT', '.'), 'Apollo'))
sys.path.insert(0, os.path.join(os.environ.get('TEKTON_ROOT', '.'), 'Engram'))

from apollo.core.apollo_manager import ApolloManager
from apollo.core.preparation.context_brief import MemoryType
from apollo.core.storage_interface import StorageMode


async def test_apollo_esr_integration():
    """Test Apollo with ESR integration."""
    
    print("=" * 60)
    print("Apollo-ESR Integration Test")
    print("=" * 60)
    
    # Create Apollo manager with ESR enabled
    print("\n1. Initializing Apollo with ESR...")
    
    apollo = ApolloManager(
        data_dir="/tmp/apollo_esr_test",
        enable_esr=True,
        esr_config={
            'cache_size': 1000,
            'enable_backends': ['kv', 'document'],  # Simple backends for testing
            'namespace': 'apollo_test'
        }
    )
    
    # Check ESR availability
    if apollo.esr_system:
        print("✓ ESR system initialized")
    else:
        print("✗ ESR system not available")
        return
    
    if apollo.storage_interface:
        print(f"✓ Storage interface initialized (mode: {apollo.storage_interface.mode})")
    else:
        print("✗ Storage interface not available")
        return
    
    # Get ContextBriefManager with ESR
    print("\n2. Creating ContextBriefManager with ESR...")
    brief_manager = apollo.get_context_brief_manager()
    
    if brief_manager.use_esr:
        print("✓ ContextBriefManager using ESR")
    else:
        print("✗ ContextBriefManager not using ESR")
    
    # Test storing memories
    print("\n3. Storing test memories...")
    
    memories = [
        {
            'ci_name': 'apollo',
            'type': MemoryType.INSIGHT,
            'summary': 'Python is versatile',
            'content': 'Python is a versatile programming language used for web development, data science, and automation.',
            'tags': ['python', 'programming', 'language']
        },
        {
            'ci_name': 'athena',
            'type': MemoryType.DECISION,
            'summary': 'Use async for performance',
            'content': 'Decision to use async/await patterns for better performance in I/O bound operations.',
            'tags': ['async', 'performance', 'architecture']
        },
        {
            'ci_name': 'rhetor',
            'type': MemoryType.CONTEXT,
            'summary': 'User prefers concise responses',
            'content': 'The user has indicated a preference for concise, direct responses without unnecessary elaboration.',
            'tags': ['user', 'preferences', 'communication']
        }
    ]
    
    stored_memories = []
    for mem_data in memories:
        try:
            memory = await brief_manager.store_async(
                ci_name=mem_data['ci_name'],
                memory_type=mem_data['type'],
                summary=mem_data['summary'],
                content=mem_data['content'],
                tags=mem_data['tags']
            )
            stored_memories.append(memory)
            print(f"  ✓ Stored: {memory.summary} (ID: {memory.id[:8]}...)")
        except Exception as e:
            print(f"  ✗ Failed to store memory: {e}")
    
    # Test searching memories
    print("\n4. Testing semantic search...")
    
    search_queries = [
        "Python programming",
        "performance optimization",
        "user preferences"
    ]
    
    for query in search_queries:
        print(f"\n  Searching for: '{query}'")
        try:
            results = await brief_manager.search_async(query, limit=5)
            print(f"  Found {len(results)} results:")
            for result in results[:3]:
                print(f"    - {result.summary}")
        except Exception as e:
            print(f"  ✗ Search failed: {e}")
    
    # Test building context
    print("\n5. Testing context building...")
    
    try:
        context = await brief_manager.build_context_async(
            topic="programming languages",
            ci_name="apollo"
        )
        
        print(f"  ✓ Built context for 'programming languages'")
        print(f"    - Source: {context.get('source', 'unknown')}")
        
        if 'memories' in context:
            print(f"    - Found {len(context['memories'])} related memories")
        elif 'primary_thoughts' in context:
            print(f"    - Found {len(context.get('primary_thoughts', []))} primary thoughts")
            print(f"    - Found {len(context.get('associated_thoughts', []))} associated thoughts")
        
    except Exception as e:
        print(f"  ✗ Context building failed: {e}")
    
    # Test cognitive workflows if available
    if apollo.cognitive_workflows:
        print("\n6. Testing cognitive workflows...")
        
        try:
            # Store a thought directly
            from engram.core.storage.cognitive_workflows import ThoughtType
            
            thought_key = await apollo.cognitive_workflows.store_thought(
                content="ESR integration with Apollo is working well",
                thought_type=ThoughtType.OBSERVATION,
                context={'test': True},
                ci_id="apollo_test"
            )
            
            print(f"  ✓ Stored thought: {thought_key[:8]}...")
            
            # Recall the thought
            thought = await apollo.cognitive_workflows.recall_thought(
                key=thought_key,
                ci_id="apollo_test"
            )
            
            if thought:
                print(f"  ✓ Recalled thought: {thought.content}")
            else:
                print("  ✗ Could not recall thought")
                
        except Exception as e:
            print(f"  ✗ Cognitive workflow test failed: {e}")
    
    # Get storage statistics
    print("\n7. Storage Statistics:")
    
    if apollo.storage_interface:
        stats = apollo.storage_interface.get_storage_stats()
        print(f"  - Mode: {stats.get('mode')}")
        print(f"  - Has ESR: {stats.get('has_esr')}")
        print(f"  - Has Cognitive: {stats.get('has_cognitive')}")
        
        if 'esr_stats' in stats:
            esr_stats = stats['esr_stats']
            print(f"  - Cache size: {esr_stats.get('cache_size', 0)}")
            print(f"  - Thought chains: {esr_stats.get('thought_chains', 0)}")
    
    print("\n" + "=" * 60)
    print("Apollo-ESR Integration Test Complete")
    print("=" * 60)


async def test_migration():
    """Test migrating legacy memories to ESR."""
    
    print("\n" + "=" * 60)
    print("Testing Legacy to ESR Migration")
    print("=" * 60)
    
    apollo = ApolloManager(
        data_dir="/tmp/apollo_migration_test",
        enable_esr=True
    )
    
    if not apollo.storage_interface:
        print("Storage interface not available")
        return
    
    brief_manager = apollo.get_context_brief_manager()
    
    # Create some legacy memories first
    print("\n1. Creating legacy memories...")
    
    for i in range(5):
        brief_manager.store(
            ci_name=f"ci_{i}",
            memory_type=MemoryType.INSIGHT,
            summary=f"Legacy memory {i}",
            content=f"This is legacy memory content number {i}",
            tags=[f"legacy", f"test_{i}"]
        )
    
    brief_manager.save()
    print(f"  Created {len(brief_manager.memories)} legacy memories")
    
    # Migrate to ESR
    print("\n2. Migrating to ESR...")
    
    migrated = await brief_manager.migrate_to_esr()
    print(f"  ✓ Migrated {migrated} memories to ESR")
    
    # Verify migration
    print("\n3. Verifying migration...")
    
    results = await brief_manager.search_async("legacy", limit=10)
    print(f"  ✓ Found {len(results)} migrated memories via ESR search")
    
    print("\nMigration test complete!")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_apollo_esr_integration())
    
    # Optionally test migration
    # asyncio.run(test_migration())