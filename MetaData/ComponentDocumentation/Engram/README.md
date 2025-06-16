# Engram

## Overview

Engram is Tekton's memory management system, designed to provide persistent, structured memory capabilities across all components. It serves as the central memory repository, handling storage, retrieval, contextualization, and semantic search of information, enabling components to maintain context and knowledge across sessions.

## Key Features

- **Persistent Memory**: Long-term storage for information across sessions and interactions
- **Structured Memory**: Organized memory with categorization, tagging, and metadata
- **Vector-Based Storage**: Semantic similarity search using vector embeddings
- **Memory Compartments**: Logical separation of different memory types and contexts
- **Latent Space Interface**: Abstract representation of memory for advanced reasoning
- **Multi-Backend Support**: Flexible storage with adapters for different vector databases
- **Memory Context Management**: Automatic organization and retrieval based on context
- **Single Port Architecture**: Unified API access through standardized endpoints

## Architecture

Engram follows a layered architecture with the following components:

1. **Core Memory System**: The foundation that handles basic memory operations
   - Memory Manager: Coordinates memory operations across the system
   - Vector Store: Handles vector-based storage and retrieval
   - Memory Adapters: Interfaces with different storage backends

2. **Structured Memory**: Organizes memory into meaningful structures
   - Categorization: Classifies memories by type and relevance
   - Compartments: Separates memories into logical spaces
   - Latent Space: Abstract representation of memory concepts

3. **API Layer**: Exposes RESTful and WebSocket interfaces
   - Query Endpoints: Search and retrieve memories
   - Storage Endpoints: Create and update memories
   - Context Management: Handle context-aware memory operations

4. **Integration Layer**: Connects with other Tekton components
   - Hermes Integration: Service registration and discovery
   - Client Libraries: Easy access for other components

## Memory Types

Engram supports several memory types:

- **Core Memory**: Foundational, long-term information
- **Episodic Memory**: Time-based records of interactions and events
- **Semantic Memory**: Conceptual knowledge and relationships
- **Procedural Memory**: Information about processes and actions
- **Working Memory**: Temporary, active context information

## Integration Points

Engram integrates with:

- **Hermes**: For service registration and message routing
- **Rhetor**: For natural language processing of memory content
- **Athena**: For knowledge graph construction from memories
- **Terma**: For terminal session context persistence
- **LLM Adapter**: For embedding generation and semantic processing

## Getting Started

See the [Installation Guide](./INSTALLATION_GUIDE.md) for setup instructions and the [Integration Guide](./INTEGRATION_GUIDE.md) for details on connecting Engram with other Tekton components.

## API Reference

Refer to the [API Reference](./API_REFERENCE.md) for comprehensive documentation of available endpoints and operations.

## Technical Details

For in-depth information about Engram's implementation, see the [Technical Documentation](./TECHNICAL_DOCUMENTATION.md).