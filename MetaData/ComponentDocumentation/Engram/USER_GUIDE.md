# Engram User Guide

This guide provides practical instructions for users of the Engram memory management component, focusing on day-to-day usage rather than technical implementation details.

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [Memory Fundamentals](#memory-fundamentals)
- [Creating and Storing Memories](#creating-and-storing-memories)
- [Retrieving Memories](#retrieving-memories)
- [Searching for Memories](#searching-for-memories)
- [Working with Collections](#working-with-collections)
- [Structured Memory](#structured-memory)
- [Memory Management](#memory-management)
- [CLI Tools](#cli-tools)
- [Integration with Tekton Components](#integration-with-tekton-components)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Introduction

Engram is the memory management component of the Tekton ecosystem, providing persistent, searchable storage for information across all components. It enables contextual recall, semantic search, and structured memory organization, allowing the system to learn from past experiences and maintain context over time.

## Getting Started

### Installation and Setup

Engram is typically installed as part of the Tekton ecosystem:

```bash
# Launch Engram using the Tekton launcher
./scripts/tekton-launch --components engram

# Verify Engram is running
./scripts/tekton-status | grep engram
```

### Accessing Engram

Engram provides multiple interfaces:

1. **REST API**: For programmatic access
   ```
   http://localhost:8003/api/
   ```

2. **Web UI**: Through the Hephaestus component
   ```
   http://localhost:8080/
   ```
   Then navigate to the Engram component in the sidebar.

3. **CLI**: For command-line operations
   ```bash
   python -m engram.cli
   ```

4. **Python Client**: For application integration
   ```python
   from engram.client import EngramClient
   
   client = EngramClient("http://localhost:8003")
   ```

## Memory Fundamentals

### Understanding Memories

In Engram, memories are structured data units with:

- **Content**: The actual information being stored (text, data, objects)
- **Metadata**: Information about the memory (type, tags, source, timestamp)
- **Memory ID**: Unique identifier for the memory
- **Embeddings**: Vector representations for semantic search
- **Collections**: Organizational units for grouping related memories

### Memory Types

Common memory types include:

- **Text**: Plain text content (notes, summaries, observations)
- **Conversation**: Dialog between users and components
- **Code**: Programming code snippets or files
- **Knowledge**: Structured information and facts
- **Task**: Task descriptions and outcomes
- **Experience**: Records of system activities and results

## Creating and Storing Memories

### Storing Basic Memories

#### Using the API:
```bash
curl -X POST http://localhost:8003/api/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Tekton is an intelligent orchestration system for AI models.",
    "memory_type": "knowledge",
    "tags": ["tekton", "overview"]
  }'
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def store_memory_example():
    client = EngramClient("http://localhost:8003")
    
    memory_id = await client.store_memory(
        content="Tekton is an intelligent orchestration system for AI models.",
        memory_type="knowledge",
        tags=["tekton", "overview"]
    )
    
    print(f"Stored memory with ID: {memory_id}")
```

#### Using the CLI:
```bash
python -m engram.cli store \
  --content "Tekton is an intelligent orchestration system for AI models." \
  --type knowledge \
  --tags tekton,overview
```

### Storing Structured Memories

#### Using the API:
```bash
curl -X POST http://localhost:8003/api/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "title": "Tekton Overview",
      "description": "Intelligent orchestration system for AI models",
      "components": ["Engram", "Hermes", "Athena"],
      "version": "1.0.0"
    },
    "memory_type": "structured_knowledge",
    "collection": "documentation",
    "tags": ["tekton", "architecture"]
  }'
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def store_structured_memory_example():
    client = EngramClient("http://localhost:8003")
    
    content = {
        "title": "Tekton Overview",
        "description": "Intelligent orchestration system for AI models",
        "components": ["Engram", "Hermes", "Athena"],
        "version": "1.0.0"
    }
    
    memory_id = await client.store_memory(
        content=content,
        memory_type="structured_knowledge",
        collection="documentation",
        tags=["tekton", "architecture"]
    )
    
    print(f"Stored structured memory with ID: {memory_id}")
```

### Storing Memories with Custom Metadata

#### Using the API:
```bash
curl -X POST http://localhost:8003/api/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The latent space visualization shows clustering of similar concepts.",
    "memory_type": "observation",
    "tags": ["latent-space", "visualization"],
    "metadata": {
      "source": "research_experiment",
      "importance": "high",
      "author": "researcher_1",
      "project": "concept_clustering",
      "date": "2025-04-15"
    }
  }'
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def store_memory_with_metadata_example():
    client = EngramClient("http://localhost:8003")
    
    memory_id = await client.store_memory(
        content="The latent space visualization shows clustering of similar concepts.",
        memory_type="observation",
        tags=["latent-space", "visualization"],
        metadata={
            "source": "research_experiment",
            "importance": "high",
            "author": "researcher_1",
            "project": "concept_clustering",
            "date": "2025-04-15"
        }
    )
    
    print(f"Stored memory with custom metadata, ID: {memory_id}")
```

## Retrieving Memories

### Retrieving by ID

#### Using the API:
```bash
curl http://localhost:8003/api/memories/memory_id_here
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def retrieve_memory_example():
    client = EngramClient("http://localhost:8003")
    
    memory = await client.retrieve_memory("memory_id_here")
    
    if memory:
        print(f"Retrieved memory: {memory.content}")
        print(f"Type: {memory.memory_type}")
        print(f"Tags: {memory.tags}")
    else:
        print("Memory not found")
```

#### Using the CLI:
```bash
python -m engram.cli get memory_id_here
```

### Retrieving Recent Memories

#### Using the API:
```bash
curl "http://localhost:8003/api/memories/recent?limit=10&memory_type=knowledge"
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def retrieve_recent_memories_example():
    client = EngramClient("http://localhost:8003")
    
    memories = await client.get_recent_memories(
        limit=10,
        memory_type="knowledge"
    )
    
    print(f"Retrieved {len(memories)} recent memories")
    for memory in memories:
        print(f"- {memory.memory_id}: {memory.content[:50]}...")
```

## Searching for Memories

### Text-Based Search

#### Using the API:
```bash
curl "http://localhost:8003/api/memories/search?q=tekton%20architecture&limit=5"
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def text_search_example():
    client = EngramClient("http://localhost:8003")
    
    results = await client.search_memories(
        query="tekton architecture",
        limit=5
    )
    
    print(f"Found {len(results)} results")
    for memory in results:
        print(f"- {memory.memory_id}: {memory.content[:50]}...")
        print(f"  Relevance: {memory.relevance}")
```

### Semantic Search

#### Using the API:
```bash
curl -X POST http://localhost:8003/api/memories/semantic_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does memory persistence work in Tekton?",
    "limit": 5,
    "min_relevance": 0.7
  }'
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def semantic_search_example():
    client = EngramClient("http://localhost:8003")
    
    results = await client.semantic_search(
        query="How does memory persistence work in Tekton?",
        limit=5,
        min_relevance=0.7
    )
    
    print(f"Found {len(results)} semantically relevant results")
    for memory in results:
        print(f"- {memory.memory_id}: {memory.content[:50]}...")
        print(f"  Relevance: {memory.relevance}")
```

### Filtering by Tags and Types

#### Using the API:
```bash
curl "http://localhost:8003/api/memories/search?tags=architecture,documentation&memory_type=knowledge&limit=10"
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def filtered_search_example():
    client = EngramClient("http://localhost:8003")
    
    results = await client.search_memories(
        tags=["architecture", "documentation"],
        memory_type="knowledge",
        limit=10
    )
    
    print(f"Found {len(results)} filtered results")
    for memory in results:
        print(f"- {memory.memory_id}: {memory.content[:50]}...")
```

### Advanced Query

#### Using the API:
```bash
curl -X POST http://localhost:8003/api/memories/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "memory_type": "observation",
      "tags": {"$in": ["latent-space", "visualization"]},
      "metadata.importance": "high",
      "created_at": {"$gt": "2025-01-01T00:00:00Z"}
    },
    "sort": {"created_at": -1},
    "limit": 20
  }'
```

#### Using the Python Client:
```python
from engram.client import EngramClient
from datetime import datetime

async def advanced_query_example():
    client = EngramClient("http://localhost:8003")
    
    query = {
        "memory_type": "observation",
        "tags": {"$in": ["latent-space", "visualization"]},
        "metadata.importance": "high",
        "created_at": {"$gt": "2025-01-01T00:00:00Z"}
    }
    
    results = await client.query_memories(
        query=query,
        sort={"created_at": -1},
        limit=20
    )
    
    print(f"Found {len(results)} results matching complex query")
    for memory in results:
        print(f"- {memory.memory_id}: {memory.content[:50]}...")
        print(f"  Created: {memory.created_at}")
```

## Working with Collections

### Creating a Collection

#### Using the API:
```bash
curl -X POST http://localhost:8003/api/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "project_documentation",
    "description": "Documentation and knowledge for the current project"
  }'
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def create_collection_example():
    client = EngramClient("http://localhost:8003")
    
    collection_id = await client.create_collection(
        name="project_documentation",
        description="Documentation and knowledge for the current project"
    )
    
    print(f"Created collection with ID: {collection_id}")
```

### Storing Memories in a Collection

#### Using the API:
```bash
curl -X POST http://localhost:8003/api/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The project architecture follows a modular design pattern.",
    "memory_type": "documentation",
    "collection": "project_documentation",
    "tags": ["architecture", "design"]
  }'
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def store_in_collection_example():
    client = EngramClient("http://localhost:8003")
    
    memory_id = await client.store_memory(
        content="The project architecture follows a modular design pattern.",
        memory_type="documentation",
        collection="project_documentation",
        tags=["architecture", "design"]
    )
    
    print(f"Stored memory in collection, ID: {memory_id}")
```

### Retrieving Memories from a Collection

#### Using the API:
```bash
curl "http://localhost:8003/api/collections/project_documentation/memories?limit=20"
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def retrieve_collection_memories_example():
    client = EngramClient("http://localhost:8003")
    
    memories = await client.get_collection_memories(
        collection="project_documentation",
        limit=20
    )
    
    print(f"Retrieved {len(memories)} memories from collection")
    for memory in memories:
        print(f"- {memory.memory_id}: {memory.content[:50]}...")
```

### Searching Within a Collection

#### Using the API:
```bash
curl "http://localhost:8003/api/collections/project_documentation/search?q=architecture&limit=10"
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def search_collection_example():
    client = EngramClient("http://localhost:8003")
    
    results = await client.search_collection(
        collection="project_documentation",
        query="architecture",
        limit=10
    )
    
    print(f"Found {len(results)} results in the collection")
    for memory in results:
        print(f"- {memory.memory_id}: {memory.content[:50]}...")
```

## Structured Memory

### Creating a Memory Schema

#### Using the API:
```bash
curl -X POST http://localhost:8003/api/schemas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "project",
    "description": "Schema for project information",
    "properties": {
      "title": {"type": "string", "required": true},
      "description": {"type": "string", "required": true},
      "status": {"type": "string", "enum": ["planned", "active", "completed", "cancelled"]},
      "start_date": {"type": "date"},
      "end_date": {"type": "date"},
      "team_members": {"type": "array", "items": {"type": "string"}},
      "priority": {"type": "integer", "minimum": 1, "maximum": 5}
    }
  }'
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def create_schema_example():
    client = EngramClient("http://localhost:8003")
    
    schema_id = await client.create_schema(
        name="project",
        description="Schema for project information",
        properties={
            "title": {"type": "string", "required": True},
            "description": {"type": "string", "required": True},
            "status": {"type": "string", "enum": ["planned", "active", "completed", "cancelled"]},
            "start_date": {"type": "date"},
            "end_date": {"type": "date"},
            "team_members": {"type": "array", "items": {"type": "string"}},
            "priority": {"type": "integer", "minimum": 1, "maximum": 5}
        }
    )
    
    print(f"Created schema with ID: {schema_id}")
```

### Storing Structured Memories with Schema

#### Using the API:
```bash
curl -X POST http://localhost:8003/api/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "title": "Tekton Documentation Project",
      "description": "Create comprehensive documentation for all Tekton components",
      "status": "active",
      "start_date": "2025-01-15",
      "team_members": ["Alice", "Bob", "Charlie"],
      "priority": 2
    },
    "memory_type": "project",
    "schema": "project",
    "tags": ["documentation", "project"]
  }'
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def store_structured_memory_with_schema_example():
    client = EngramClient("http://localhost:8003")
    
    content = {
        "title": "Tekton Documentation Project",
        "description": "Create comprehensive documentation for all Tekton components",
        "status": "active",
        "start_date": "2025-01-15",
        "team_members": ["Alice", "Bob", "Charlie"],
        "priority": 2
    }
    
    memory_id = await client.store_memory(
        content=content,
        memory_type="project",
        schema="project",
        tags=["documentation", "project"]
    )
    
    print(f"Stored structured memory with schema, ID: {memory_id}")
```

### Querying Structured Memories

#### Using the API:
```bash
curl -X POST http://localhost:8003/api/memories/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "memory_type": "project",
      "content.status": "active",
      "content.priority": {"$lte": 3}
    },
    "sort": {"content.priority": 1},
    "limit": 10
  }'
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def query_structured_memories_example():
    client = EngramClient("http://localhost:8003")
    
    query = {
        "memory_type": "project",
        "content.status": "active",
        "content.priority": {"$lte": 3}
    }
    
    results = await client.query_memories(
        query=query,
        sort={"content.priority": 1},
        limit=10
    )
    
    print(f"Found {len(results)} active projects with priority <= 3")
    for memory in results:
        project = memory.content
        print(f"- {project['title']} (Priority: {project['priority']})")
        print(f"  Status: {project['status']}")
        print(f"  Team: {', '.join(project['team_members'])}")
```

## Memory Management

### Updating Memories

#### Using the API:
```bash
curl -X PUT http://localhost:8003/api/memories/memory_id_here \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated memory content with additional information",
    "tags": ["updated", "information"]
  }'
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def update_memory_example():
    client = EngramClient("http://localhost:8003")
    
    success = await client.update_memory(
        memory_id="memory_id_here",
        content="Updated memory content with additional information",
        tags=["updated", "information"]
    )
    
    if success:
        print("Memory updated successfully")
    else:
        print("Failed to update memory")
```

### Deleting Memories

#### Using the API:
```bash
curl -X DELETE http://localhost:8003/api/memories/memory_id_here
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def delete_memory_example():
    client = EngramClient("http://localhost:8003")
    
    success = await client.delete_memory("memory_id_here")
    
    if success:
        print("Memory deleted successfully")
    else:
        print("Failed to delete memory")
```

### Memory Statistics

#### Using the API:
```bash
curl http://localhost:8003/api/stats
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def get_stats_example():
    client = EngramClient("http://localhost:8003")
    
    stats = await client.get_stats()
    
    print("Memory Statistics:")
    print(f"Total memories: {stats['total_memories']}")
    print(f"Collections: {stats['total_collections']}")
    print(f"Memory types: {', '.join(stats['memory_types'])}")
    print(f"Total size: {stats['total_size_mb']} MB")
    print("\nMemory counts by type:")
    for mem_type, count in stats["counts_by_type"].items():
        print(f"- {mem_type}: {count}")
```

### Memory Maintenance

#### Using the API:
```bash
# Archive old memories
curl -X POST http://localhost:8003/api/maintenance/archive \
  -H "Content-Type: application/json" \
  -d '{
    "older_than": "2024-12-31",
    "memory_types": ["log", "debug"],
    "target_collection": "archive_2024"
  }'

# Optimize database
curl -X POST http://localhost:8003/api/maintenance/optimize
```

#### Using the Python Client:
```python
from engram.client import EngramClient

async def maintenance_example():
    client = EngramClient("http://localhost:8003")
    
    # Archive old memories
    archived = await client.archive_memories(
        older_than="2024-12-31",
        memory_types=["log", "debug"],
        target_collection="archive_2024"
    )
    
    print(f"Archived {archived} memories")
    
    # Optimize database
    success = await client.optimize_database()
    
    if success:
        print("Database optimization completed")
    else:
        print("Database optimization failed")
```

## CLI Tools

Engram provides a command-line interface for common operations:

### Basic Operations

```bash
# Store a memory
python -m engram.cli store \
  --content "This is a memory to store" \
  --type note \
  --tags cli,example

# Retrieve a memory
python -m engram.cli get memory_id_here

# Search memories
python -m engram.cli search "memory query here" \
  --limit 10 \
  --type note

# Delete a memory
python -m engram.cli delete memory_id_here
```

### Collection Management

```bash
# Create a collection
python -m engram.cli collection create \
  --name my_collection \
  --description "My collection description"

# List collections
python -m engram.cli collection list

# List memories in a collection
python -m engram.cli collection get my_collection \
  --limit 20
```

### Backup and Restore

```bash
# Backup all memories
python -m engram.cli backup \
  --output /path/to/backup.json

# Backup a specific collection
python -m engram.cli backup \
  --collection my_collection \
  --output /path/to/collection_backup.json

# Restore memories
python -m engram.cli restore \
  --input /path/to/backup.json
```

### System Management

```bash
# Show system statistics
python -m engram.cli stats

# Run maintenance
python -m engram.cli maintenance \
  --archive-older-than 2024-12-31 \
  --optimize
```

## Integration with Tekton Components

### Integration with Athena

Engram integrates with Athena for knowledge graph storage:

```python
from engram.client import EngramClient
from athena.client import AthenaClient

async def store_knowledge_graph_entity():
    engram_client = EngramClient("http://localhost:8003")
    athena_client = AthenaClient("http://localhost:8002")
    
    # Get entity from Athena
    entity = await athena_client.get_entity("entity_id_here")
    
    # Store entity in Engram
    memory_id = await engram_client.store_memory(
        content=entity,
        memory_type="knowledge_entity",
        metadata={
            "entity_id": entity["id"],
            "entity_type": entity["type"]
        },
        tags=["knowledge_graph", entity["type"]]
    )
    
    print(f"Stored knowledge graph entity in Engram: {memory_id}")
```

### Integration with Ergon

Engram integrates with Ergon for task memory:

```python
from engram.client import EngramClient
from ergon.client import ErgonClient

async def store_task_completion():
    engram_client = EngramClient("http://localhost:8003")
    ergon_client = ErgonClient("http://localhost:8004")
    
    # Get task from Ergon
    task = await ergon_client.get_task("task_id_here")
    
    # Store task completion memory
    memory_id = await engram_client.store_memory(
        content={
            "task_id": task["task_id"],
            "title": task["title"],
            "outcome": "Successfully completed the task with results X, Y, Z",
            "duration_minutes": 45
        },
        memory_type="task_completion",
        metadata={
            "task_id": task["task_id"],
            "status": task["status"]
        },
        tags=["task", "completion", task["status"]]
    )
    
    print(f"Stored task completion memory: {memory_id}")
```

### Integration with LLM Systems

Engram integrates with the Tekton LLM client for context enrichment:

```python
from engram.client import EngramClient
from tekton_llm_client import TektonLLMClient

async def generate_context_for_prompt():
    engram_client = EngramClient("http://localhost:8003")
    llm_client = TektonLLMClient()
    
    # Retrieve relevant memories for a topic
    memories = await engram_client.semantic_search(
        query="Tekton architecture design patterns",
        limit=5,
        min_relevance=0.7
    )
    
    # Format memories as context
    context = "\n\n".join([
        f"Memory {i+1}:\n{memory.content}"
        for i, memory in enumerate(memories)
    ])
    
    # Create prompt with context
    prompt = f"""Context information:
{context}

Based on the above context, please explain the key design patterns used in the Tekton architecture.
"""
    
    # Generate response with LLM
    response = await llm_client.generate_text(prompt)
    
    print("Generated response using memory context:")
    print(response)
```

## Troubleshooting

### Common Issues

**Issue**: Memories not appearing in search results
**Solution**:
1. Check if the memory was stored correctly
2. Verify the search terms match memory content
3. Ensure you're searching in the correct collection
4. Try semantic search instead of keyword search

**Issue**: Vector search not working properly
**Solution**:
1. Ensure the vector database is running
2. Check if embeddings were generated correctly
3. Verify the query is specific enough
4. Adjust the minimum relevance threshold

**Issue**: Performance issues with large memory stores
**Solution**:
1. Use more specific queries to reduce result set size
2. Archive old or infrequently accessed memories
3. Optimize the database
4. Consider upgrading hardware resources

### Log Checking

```bash
# View Engram logs
tail -f /path/to/tekton/logs/engram.log

# Check for specific error patterns
grep "ERROR" /path/to/tekton/logs/engram.log
```

### Health Check

```bash
# Check Engram health
curl http://localhost:8003/health

# Check vector database health
curl http://localhost:8003/health/vector_db
```

## Best Practices

### Memory Organization

1. **Use collections**: Organize related memories into collections
2. **Apply consistent tags**: Develop a tagging convention and stick to it
3. **Define memory types**: Create specific memory types for different content
4. **Use schemas**: Define schemas for structured data to ensure consistency
5. **Include metadata**: Add relevant metadata to facilitate filtering and retrieval

### Search Strategies

1. **Start specific**: Begin with specific queries and broaden as needed
2. **Try different approaches**: Use both keyword and semantic search
3. **Filter results**: Use tags, memory types, and collections to narrow results
4. **Combine queries**: Use advanced queries to combine multiple search criteria
5. **Evaluate relevance**: Check the relevance scores of semantic search results

### Performance Optimization

1. **Batch operations**: Use batch APIs for multiple memory operations
2. **Archive old data**: Move infrequently accessed memories to archives
3. **Index important fields**: Ensure commonly searched fields are indexed
4. **Limit result sizes**: Only request the number of results you need
5. **Use pagination**: For large result sets, retrieve pages of results

### Integration Patterns

1. **Memory reflection**: Store component states and decisions as memories
2. **Context enrichment**: Use relevant memories to provide context for operations
3. **Experience learning**: Record outcomes and results to learn from past experiences
4. **Cross-component knowledge**: Share memories between different components
5. **Periodic summarization**: Create summary memories to consolidate information