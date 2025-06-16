#!/usr/bin/env python3
"""
Hermes Database Services Example

This script demonstrates how to use Hermes database services including vector,
key-value, and graph databases with various backend implementations.
"""

import asyncio
import time
import random
import os
from pathlib import Path
import numpy as np

# Ensure Hermes is in Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from hermes.utils.database_helper import DatabaseClient
from hermes.core.logging import get_logger, configure_logging

# Configure logging
configure_logging(level="INFO")
logger = get_logger("hermes.examples.database")

# Sample data for demonstrations
SAMPLE_TEXTS = [
    "The quick brown fox jumps over the lazy dog",
    "Machine learning models transform raw data into useful predictions",
    "Vector databases enable semantic search capabilities",
    "Graph databases excel at representing complex relationships",
    "Key-value stores provide fast access to data using unique keys",
    "Distributed systems require robust communication protocols",
    "Neural networks learn by adjusting weights through backpropagation",
    "Natural language processing enables machines to understand human language",
    "Computer vision systems can identify objects in images and videos",
    "Reinforcement learning teaches agents through reward signals"
]

# Mock function to generate vector embeddings (in real usage, you would use a proper embedding model)
def generate_embedding(text, dim=1536):
    """Generate a mock embedding vector for a text string."""
    # Create a deterministic but unique vector based on the text
    # In reality, you would use a proper embedding model
    np.random.seed(hash(text) % (2**32))
    vector = np.random.randn(dim).astype(np.float32)
    # Normalize the vector to unit length
    vector = vector / np.linalg.norm(vector)
    return vector.tolist()

async def vector_database_example():
    """Demonstrate vector database operations."""
    logger.info("=== Vector Database Example ===")
    
    # Initialize DatabaseClient
    db_client = DatabaseClient(component_id="hermes.examples")
    
    # Get vector database for 'documents' namespace
    vector_db = await db_client.get_vector_db(namespace="documents")
    
    # Connect to the database
    await vector_db.connect()
    logger.info(f"Connected to vector database backend: {vector_db.backend}")
    
    # Store vectors with their text and metadata
    for i, text in enumerate(SAMPLE_TEXTS):
        # Generate embedding
        vector = generate_embedding(text)
        
        # Create metadata
        metadata = {
            "id": f"doc-{i}",
            "length": len(text),
            "category": "example",
            "timestamp": time.time()
        }
        
        # Store in vector database
        success = await vector_db.store(
            id=metadata["id"],
            vector=vector,
            metadata=metadata,
            text=text
        )
        
        if success:
            logger.info(f"Stored vector for: {text[:30]}...")
        else:
            logger.error(f"Failed to store vector for: {text[:30]}...")
    
    # Search for similar vectors
    query_text = "How do neural networks learn from data?"
    query_vector = generate_embedding(query_text)
    
    logger.info(f"Searching for vectors similar to: '{query_text}'")
    results = await vector_db.search(
        query_vector=query_vector,
        limit=3
    )
    
    logger.info(f"Found {len(results)} similar vectors:")
    for i, result in enumerate(results):
        logger.info(f"  {i+1}. [{result['relevance']:.4f}] {result['text'][:50]}...")
    
    # Clean up - delete the vectors
    logger.info("Cleaning up - deleting vectors")
    await vector_db.delete()
    
    # Disconnect from the database
    await vector_db.disconnect()
    logger.info("Disconnected from vector database")

async def key_value_database_example():
    """Demonstrate key-value database operations."""
    logger.info("\n=== Key-Value Database Example ===")
    
    # Initialize DatabaseClient
    db_client = DatabaseClient(component_id="hermes.examples")
    
    # Get key-value database for 'cache' namespace
    kv_db = await db_client.get_key_value_db(namespace="cache")
    
    # Connect to the database
    await kv_db.connect()
    logger.info(f"Connected to key-value database backend: {kv_db.backend}")
    
    # Store simple values
    await kv_db.set("greeting", "Hello, Hermes!")
    await kv_db.set("count", 42)
    await kv_db.set("enabled", True)
    
    # Store a complex value
    user_data = {
        "id": "user-123",
        "name": "Alice",
        "roles": ["admin", "developer"],
        "settings": {
            "theme": "dark",
            "notifications": True
        }
    }
    await kv_db.set("user:123", user_data)
    
    # Store with expiration (5 seconds)
    await kv_db.set("temporary", "This will expire soon", expiration=5)
    
    # Retrieve values
    greeting = await kv_db.get("greeting")
    count = await kv_db.get("count")
    user = await kv_db.get("user:123")
    
    logger.info(f"Retrieved greeting: {greeting}")
    logger.info(f"Retrieved count: {count}")
    logger.info(f"Retrieved user: {user['name']} with roles {user['roles']}")
    
    # Check if key exists
    exists = await kv_db.exists("temporary")
    logger.info(f"Temporary key exists: {exists}")
    
    # Wait for expiration
    logger.info("Waiting for temporary key to expire...")
    await asyncio.sleep(6)
    
    # Check if expired key still exists
    exists = await kv_db.exists("temporary")
    logger.info(f"Temporary key exists after expiration: {exists}")
    
    # Batch operations
    batch_data = {
        "batch:1": "First batch item",
        "batch:2": "Second batch item",
        "batch:3": "Third batch item"
    }
    
    # Store batch
    await kv_db.set_batch(batch_data)
    logger.info(f"Stored {len(batch_data)} items in batch")
    
    # Retrieve batch
    batch_keys = list(batch_data.keys())
    retrieved_batch = await kv_db.get_batch(batch_keys)
    logger.info(f"Retrieved {len(retrieved_batch)} items from batch")
    
    # Delete batch
    await kv_db.delete_batch(batch_keys)
    logger.info(f"Deleted {len(batch_keys)} items from batch")
    
    # Clean up
    await kv_db.clear_namespace()
    logger.info("Cleared all keys in namespace")
    
    # Disconnect
    await kv_db.disconnect()
    logger.info("Disconnected from key-value database")

async def graph_database_example():
    """Demonstrate graph database operations."""
    logger.info("\n=== Graph Database Example ===")
    
    # Initialize DatabaseClient
    db_client = DatabaseClient(component_id="hermes.examples")
    
    # Get graph database for 'knowledge' namespace
    graph_db = await db_client.get_graph_db(namespace="knowledge")
    
    # Connect to the database
    await graph_db.connect()
    logger.info(f"Connected to graph database backend: {graph_db.backend}")
    
    # Add nodes representing people
    people = ["Alice", "Bob", "Charlie", "David", "Eve"]
    for person in people:
        await graph_db.add_node(
            id=f"person:{person.lower()}",
            labels=["Person"],
            properties={"name": person, "active": True}
        )
        logger.info(f"Added Person node: {person}")
    
    # Add nodes representing projects
    projects = ["Hermes", "Engram", "Athena", "Ergon"]
    for project in projects:
        await graph_db.add_node(
            id=f"project:{project.lower()}",
            labels=["Project"],
            properties={"name": project, "status": "Active"}
        )
        logger.info(f"Added Project node: {project}")
    
    # Create relationships between people and projects
    relationships = [
        ("alice", "hermes", "CREATED"),
        ("alice", "athena", "CONTRIBUTES_TO"),
        ("bob", "engram", "CREATED"),
        ("bob", "hermes", "CONTRIBUTES_TO"),
        ("charlie", "ergon", "CREATED"),
        ("charlie", "athena", "CONTRIBUTES_TO"),
        ("david", "hermes", "CONTRIBUTES_TO"),
        ("eve", "engram", "CONTRIBUTES_TO")
    ]
    
    for person_id, project_id, rel_type in relationships:
        await graph_db.add_relationship(
            source_id=f"person:{person_id}",
            target_id=f"project:{project_id}",
            type=rel_type,
            properties={"since": "2025-01-01"}
        )
        logger.info(f"Added relationship: {person_id} -{rel_type}-> {project_id}")
    
    # Get a specific node
    alice_node = await graph_db.get_node("person:alice")
    logger.info(f"Retrieved node: {alice_node}")
    
    # Get relationships for a node
    alice_relationships = await graph_db.get_relationships("person:alice")
    logger.info(f"Retrieved {len(alice_relationships)} relationships for Alice")
    for rel in alice_relationships:
        logger.info(f"  {rel['source_id']} -{rel['type']}-> {rel['target_id']}")
    
    # Execute a Cypher query (Neo4j)
    try:
        query_results = await graph_db.query(
            query="""
            MATCH (p:Person)-[r]->(proj:Project)
            WHERE proj.name = $project_name
            RETURN p.name AS person, TYPE(r) AS relationship
            """,
            params={"project_name": "Hermes"}
        )
        
        logger.info(f"Query found {len(query_results)} contributors to Hermes:")
        for result in query_results:
            logger.info(f"  {result['person']} - {result['relationship']}")
            
    except Exception as e:
        logger.warning(f"Cypher query not supported on this backend: {e}")
    
    # Delete a relationship
    await graph_db.delete_relationship(
        source_id="person:alice",
        target_id="project:athena",
        type="CONTRIBUTES_TO"
    )
    logger.info("Deleted relationship between Alice and Athena")
    
    # Delete a node
    await graph_db.delete_node("person:eve")
    logger.info("Deleted node for Eve")
    
    # Clean up - delete everything in this namespace
    # In Neo4j this is done with a query
    try:
        await graph_db.query("MATCH (n) DETACH DELETE n")
        logger.info("Cleared all nodes and relationships")
    except Exception:
        logger.info("Falling back to individual deletions for cleanup")
        # Delete remaining nodes (relationships will be deleted automatically)
        for person in people:
            if person != "Eve":  # Already deleted
                await graph_db.delete_node(f"person:{person.lower()}")
        
        for project in projects:
            await graph_db.delete_node(f"project:{project.lower()}")
    
    # Disconnect
    await graph_db.disconnect()
    logger.info("Disconnected from graph database")

async def main():
    """Run all database examples."""
    try:
        logger.info("Starting Hermes database examples")
        
        # Vector database example
        await vector_database_example()
        
        # Key-value database example
        await key_value_database_example()
        
        # Graph database example
        await graph_database_example()
        
        logger.info("All database examples completed successfully")
        
    except Exception as e:
        logger.error(f"Error in database examples: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure all connections are closed
        logger.info("Database examples complete")

if __name__ == "__main__":
    asyncio.run(main())