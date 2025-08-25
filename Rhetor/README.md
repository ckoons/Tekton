# Rhetor

## Overview

Rhetor is the LLM management system for the Tekton ecosystem. It handles prompt engineering, LLM selection, context management, and serves as the central interface for all CI interactions across components. Rhetor replaces the previous LLM Adapter component with a more comprehensive solution.

## Key Features

- Single API gateway for all LLM interactions (HTTP and WebSocket on a single port)
- **FastMCP Integration** - Full Model Context Protocol support with 16 specialized tools
- Intelligent model selection and routing based on task requirements
- Support for multiple LLM providers (Anthropic, OpenAI, Ollama, etc.)
- Advanced context tracking and persistence
- System prompt management for all Tekton components
- Graceful fallback mechanisms between providers
- Standardized interface for all Tekton components
- **LLM Management Tools** - Model testing, performance analysis, and rotation
- **Prompt Engineering Tools** - Template creation, optimization, and validation
- **Context Management Tools** - Usage analysis, optimization, and compression

## Architecture

Rhetor is built around a unified architecture that combines multiple features:

1. **Single-Port API**: Exposes both HTTP endpoints and WebSockets on the same port 
2. **FastMCP Integration**: Full Model Context Protocol with 16+ specialized tools
3. **Provider Abstraction**: Supports multiple LLM providers through a consistent interface
4. **Context Management**: Tracks and persists conversation history
5. **Model Router**: Intelligently selects the best model for different task types
6. **System Prompts**: Manages component-specific system prompts

### MCP Capabilities

- **LLM Management**: Model discovery, testing, performance analysis, and rotation
- **Prompt Engineering**: Template creation, optimization, validation, and library management  
- **Context Management**: Usage analysis, window optimization, and compression

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the Rhetor server
./run_rhetor.sh

# Register with Hermes (if using Hermes)
python register_with_hermes.py

# Alternatively, start with Tekton
./scripts/tekton-launch --components rhetor
```

## API Endpoints

- `GET /`: Basic information about the server
- `GET /health`: Health check endpoint
- `GET /providers`: Get available LLM providers and models
- `POST /provider`: Set the active provider and model
- `POST /message`: Send a message to the LLM
- `POST /stream`: Send a message and get a streaming response
- `POST /chat`: Send a chat conversation to the LLM
- `WebSocket /ws`: Real-time bidirectional communication

### MCP Endpoints

- `GET /api/mcp/v2/health`: MCP health check and status
- `GET /api/mcp/v2/capabilities`: List MCP capabilities  
- `GET /api/mcp/v2/tools`: List available MCP tools
- `POST /api/mcp/v2/process`: Execute MCP tools
- `GET /api/mcp/v2/llm-status`: LLM system status
- `POST /api/mcp/v2/execute-llm-workflow`: Execute LLM workflows

## Testing

### MCP Integration Tests

```bash
# Run comprehensive MCP tests
cd examples
./run_fastmcp_test.sh

# Or manually
python test_fastmcp.py
```

Tests cover all 16 MCP tools across three capabilities:
- LLM Management (6 tools)
- Prompt Engineering (6 tools)  
- Context Management (4 tools)

## Documentation

### Local Documentation

- [MCP Integration Guide](MCP_INTEGRATION.md) - Comprehensive MCP implementation details
- [FastMCP Test Suite](examples/test_fastmcp.py) - Complete test coverage for MCP tools

### MetaData Documentation

For detailed documentation, see the following resources in the MetaData directory:

- [Component Summaries](../MetaData/ComponentSummaries.md) - Overview of all Tekton components
- [Tekton Architecture](../MetaData/TektonArchitecture.md) - Overall system architecture
- [Component Integration](../MetaData/ComponentIntegration.md) - How components interact
- [CLI Operations](../MetaData/CLI_Operations.md) - Command-line operations
- [Rhetor Implementation](../MetaData/Implementation/RhetorImplementation.md) - Detailed implementation plan