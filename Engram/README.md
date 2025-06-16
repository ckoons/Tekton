# Engram

## Overview

Engram is the persistent memory system for the Tekton ecosystem. It provides storage, retrieval, and semantic search capabilities across all components, enabling context preservation and knowledge management.

## Key Features

- Persistent memory storage and retrieval
- Vector database integration for semantic search
- Memory compartmentalization and organization
- Structured memory for complex data
- Latent space operations

## Quick Start

```bash
# Start Engram with Claude integration
./utils/engram_with_claude

# Start Engram with Ollama integration
./utils/engram_with_ollama

# Start Engram with FAISS vector database
./utils/engram_with_faiss_mcp

# Use the quick memory CLI
python -m engram.cli.quickmem store --key "test" --value "test value"
python -m engram.cli.quickmem retrieve --key "test"
```

## Documentation

For detailed documentation, see the following resources in the MetaData directory:

- [Component Summaries](../MetaData/ComponentSummaries.md) - Overview of all Tekton components
- [Tekton Architecture](../MetaData/TektonArchitecture.md) - Overall system architecture
- [Component Integration](../MetaData/ComponentIntegration.md) - How components interact
- [CLI Operations](../MetaData/CLI_Operations.md) - Command-line operations
- [Engram Changelog](../MetaData/Engram_CHANGELOG.md) - Version history