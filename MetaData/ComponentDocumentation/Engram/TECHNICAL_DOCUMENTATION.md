# Engram Technical Documentation

## System Architecture

Engram's architecture is built around a core memory management system with specialized layers for different memory functions. The system is designed to be modular, extensible, and to support multiple storage backends.

### Core Layer

The foundation of Engram consists of these key modules:

#### Memory Manager (`memory_manager.py`)

The central coordinator for all memory operations, responsible for:

- Routing memory operations to appropriate handlers
- Managing memory lifecycle (creation, retrieval, update, archive)
- Coordinating between different memory types and compartments
- Handling memory context transitions

#### Vector Store (`vector_store.py`)

Responsible for vector-based storage and retrieval:

- Embedding generation and storage
- Semantic similarity search
- Vector clustering and organization
- Dimension reduction for visualization

#### Memory Adapters

Pluggable backends for different storage engines:

- `memory_faiss.py`: FAISS-based vector storage for efficient similarity search
- `lancedb_adapter.py`: LanceDB adapter for persistent vector storage
- `simple_embedding.py`: Lightweight embedding generation

### Structured Memory Layer

#### Memory Compartments (`compartments.py`)

Logical separation of memory spaces:

- Isolation between different contexts and topics
- Custom retrieval policies per compartment
- Targeted search within specific compartments
- Cross-compartment relationships and references

#### Latent Space (`latent_space.py`)

Abstract representation of memory concepts:

- Conceptual mapping of memory items
- Relationship tracking between concepts
- Semantic drift detection and correction
- Abstract reasoning interfaces

#### Categorization (`categorization.py`)

Automatic organization of memories:

- Memory type classification
- Relevance scoring and prioritization
- Temporal organization
- Topic clustering and tagging

### API Layer

#### HTTP Server (`server.py`)

Exposes RESTful endpoints for synchronous operations:

- Memory creation and update
- Explicit memory retrieval
- System configuration and status
- Batch operations for efficiency

#### WebSocket Server (`mcp_server.py`)

Provides real-time, streaming interfaces:

- Continuous memory updates
- Streaming search results
- Event notifications for memory changes
- Interactive context management

#### Consolidated Server (`consolidated_server.py`)

Implements the Single Port Architecture pattern:

- Unified endpoint handling for HTTP and WebSocket
- Path-based routing for different protocols
- Standardized authentication and authorization
- Centralized request logging and monitoring

## Memory Model

Engram's memory model is designed to represent diverse types of information while maintaining semantic relationships:

### Base Memory Item

```python
class MemoryItem:
    id: str  # Unique identifier
    content: Any  # The actual memory content (text, structured data, etc.)
    embedding: List[float]  # Vector representation for semantic search
    metadata: Dict[str, Any]  # Additional information about this memory
    importance: float  # Relevance score (0.0 to 1.0)
    created_at: datetime
    accessed_at: datetime
    compartment: str  # The logical memory space this belongs to
    type: str  # The memory type classification
    references: List[str]  # IDs of related memory items
    version: int  # For tracking updates to the same memory
```

### Specialized Memory Types

#### Core Memory

Fundamental, long-term information that provides a stable foundation for the system's understanding:

- Persistent across all sessions
- High importance weighting
- Typically manually created or explicitly marked
- Resistant to automatic pruning

#### Episodic Memory

Time-based records of interactions, events, and experiences:

- Strongly tied to temporal context
- Contains sequence information
- Often includes session identifiers
- May decay in importance over time

#### Semantic Memory

Conceptual knowledge, facts, and relationships between concepts:

- Abstract representations of knowledge
- Highly interconnected with other memories
- Often generated through inference and learning
- Regularly updated as new information is acquired

#### Working Memory

Temporary, active context information in current use:

- Short-lived by design
- High priority during active sessions
- Automatically archived when context changes
- Often used to influence retrieval of other memories

## Vector Embedding System

Engram uses vector embeddings to enable semantic search and similarity matching:

### Embedding Generation

- Supports multiple embedding models (OpenAI, HuggingFace, etc.)
- Contextual embedding generation based on content type
- Multi-modal embedding support for different content types
- Configurable embedding dimensions and parameters

### Similarity Search

- k-Nearest Neighbors search for semantically similar items
- Configurable distance metrics (cosine, Euclidean, etc.)
- Hybrid search combining vector and metadata filtering
- Optional pre-filtering to improve search efficiency

### Vector Storage

- FAISS for high-performance in-memory vector operations
- LanceDB for persistent storage with efficient querying
- Indexing optimizations for different workload patterns
- Automatic index rebuilding and optimization

## Memory Context Management

Engram maintains context awareness to improve memory retrieval relevance:

### Context Tracking

- Active session context monitoring
- Topic and theme identification
- User/component intent recognition
- Temporal context preservation

### Retrieval Strategies

- Context-weighted retrieval scoring
- Recency vs. relevance balancing
- Importance-based prioritization
- Diversity sampling for comprehensive results

### Memory Pruning

- Automatic importance decay for old memories
- Deduplication of similar information
- Archiving of outdated or superseded memories
- Selective retention based on importance scoring

## Performance Optimizations

Engram implements several optimizations for efficient memory operations:

- **Caching**: Frequently accessed memories are cached in memory
- **Batched Operations**: Support for bulk embeddings and retrieval
- **Asynchronous Processing**: Non-blocking operations for embedding generation
- **Incremental Indexing**: Efficient updates to vector indexes
- **Query Compilation**: Optimized query execution plans
- **Result Pagination**: Efficient handling of large result sets

## Security Model

- **Authentication**: API key and token-based access control
- **Authorization**: Component-specific access permissions
- **Isolation**: Memory compartments with access controls
- **Encryption**: Optional encryption for sensitive memories
- **Audit Logging**: Tracking of all memory operations
- **Data Validation**: Input sanitization and schema enforcement