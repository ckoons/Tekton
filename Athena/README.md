# Athena Knowledge Graph

## Overview

Athena is the knowledge graph system for the Tekton ecosystem. It manages entity relationships, provides reasoning capabilities, and enables structured knowledge representation and retrieval. Athena serves as the long-term memory and knowledge repository for the entire platform, allowing context-aware AI interactions across components.

## Key Features

- **Knowledge Graph Management**: Create, read, update, and delete entities and relationships
- **Entity Extraction**: Extract entities from text using LLM capabilities
- **Relationship Inference**: Infer relationships between entities using pattern matching and LLM reasoning
- **Graph Visualization**: Interactive visualizations for exploring the knowledge graph
- **Knowledge-Enhanced Chat**: AI chat capabilities augmented with graph knowledge
- **Graph Querying**: Powerful querying capabilities using both Cypher and natural language
- **LLM Integration**: Standardized integration with the Tekton LLM adapter
- **Hermes Integration**: Registration with the Hermes service discovery system

## Architecture

Athena follows a layered architecture:

1. **Storage Layer**: Graph database (Neo4j) for efficient graph operations
2. **Core Layer**: Entity and relationship management, query engine, graph operations
3. **Integration Layer**: Adapters for other Tekton components (e.g., Engram, Rhetor)
4. **API Layer**: RESTful API for all knowledge graph operations
5. **UI Layer**: Web components for visualization and interaction

## Quick Start

```bash
# Install dependencies
cd Athena
pip install -r requirements.txt

# Start Athena
../scripts/tekton-launch --components athena

# Register with Hermes
python register_with_hermes.py
```

## API Endpoints

Athena provides a comprehensive API for knowledge graph operations:

- `/api/entities` - Entity management
- `/api/relationships` - Relationship management
- `/api/query` - Graph querying
- `/api/llm` - LLM-enhanced operations
- `/api/visualization` - Graph visualization

## UI Components

Athena includes a web component for integration with the Hephaestus UI system:

- `<athena-component>` - Main component for knowledge graph visualization and interaction
- `<graph-visualization>` - Interactive graph visualization
- `<knowledge-chat>` - Knowledge-enhanced chat interface

## Integration with Other Components

- **Engram**: Bidirectional integration for memory and knowledge synchronization
- **Rhetor**: LLM integration for entity extraction and relationship inference
- **Hermes**: Component registration and service discovery
- **Hephaestus**: UI integration for visualization and interaction

## Documentation

For detailed documentation, see the following resources:

- [Component Summaries](../MetaData/ComponentSummaries.md) - Overview of all Tekton components
- [Tekton Architecture](../MetaData/TektonArchitecture.md) - Overall system architecture
- [Component Integration](../MetaData/ComponentIntegration.md) - How components interact
- [CLI Operations](../MetaData/CLI_Operations.md) - Command-line operations
- [Single Port Architecture](../docs/SINGLE_PORT_ARCHITECTURE.md) - Communication pattern
- [LLM Integration Guide](../docs/llm_integration_guide.md) - LLM integration pattern