#!/usr/bin/env python3
"""
Hermes Integration Example for Engram

This script demonstrates how to use Hermes's centralized database services
with Engram's memory system for enhanced capabilities.
"""

import asyncio
import os
import time
from typing import List, Dict, Any

# Import the Hermes-backed memory service
from engram.integrations.hermes.memory_adapter import HermesMemoryService


async def demonstrate_memory_operations():
    """Demonstrate basic memory operations using Hermes adapter."""
    print("\n=== Demonstrating Hermes Integration with Engram ===\n")
    
    # Initialize the memory service with Hermes backend
    memory = HermesMemoryService(client_id="demo")
    print(f"Initialized memory service with Hermes {'available' if memory.hermes_available else 'unavailable'}")
    
    # Add memories to different namespaces
    print("\nAdding memories to different namespaces...")
    
    await memory.add(
        content="This is a conversation with the user about AI technology.",
        namespace="conversations",
        metadata={"source": "user", "topic": "AI"}
    )
    
    await memory.add(
        content="I should remember to explain vector embeddings in simple terms.",
        namespace="thinking",
        metadata={"priority": "medium", "topic": "AI"}
    )
    
    await memory.add(
        content="Important technical concept: Vector databases store embeddings for semantic search.",
        namespace="longterm",
        metadata={"priority": "high", "topic": "databases"}
    )
    
    # Add a memory to be forgotten
    await memory.add(
        content="FORGET/IGNORE: Incorrect information about vector databases",
        namespace="longterm",
        metadata={"priority": "high", "topic": "databases"}
    )
    
    # Create a compartment for project-specific memories
    print("\nCreating a compartment for project data...")
    compartment_id = await memory.create_compartment(
        name="Vector Database Project",
        description="Information related to vector database implementation"
    )
    
    if compartment_id:
        print(f"Created compartment with ID: {compartment_id}")
        
        # Activate the compartment
        await memory.activate_compartment(compartment_id)
        print(f"Activated compartment: {compartment_id}")
        
        # Add memories to the compartment
        await memory.add(
            content="Project goal: Implement a scalable vector database for semantic search.",
            namespace=f"compartment-{compartment_id}",
            metadata={"type": "goal"}
        )
        
        await memory.add(
            content="Using FAISS for CPU-based vector search with L2 normalization.",
            namespace=f"compartment-{compartment_id}",
            metadata={"type": "implementation"}
        )
    
    # Search for memories
    print("\nSearching for memories about 'vector'...")
    results = await memory.search(query="vector", limit=10)
    
    print(f"Found {results['count']} results:")
    for i, result in enumerate(results["results"]):
        print(f"{i+1}. {result['content']}")
        print(f"   Relevance: {result['relevance']:.4f}")
        print(f"   Namespace: {result.get('metadata', {}).get('namespace', 'unknown')}")
        print()
    
    # Get relevant context
    print("\nGetting relevant context for 'database'...")
    context = await memory.get_relevant_context(query="database", limit=5)
    print(context)
    
    # List compartments
    print("\nListing compartments:")
    compartments = await memory.list_compartments()
    
    for compartment in compartments:
        print(f"- {compartment['name']} (ID: {compartment['id']})")
        print(f"  Description: {compartment.get('description', 'N/A')}")
        print(f"  Active: {compartment.get('active', False)}")
        print()
    
    # Close connections
    await memory.close()
    print("Closed all connections")


if __name__ == "__main__":
    # Run the async demo
    asyncio.run(demonstrate_memory_operations())