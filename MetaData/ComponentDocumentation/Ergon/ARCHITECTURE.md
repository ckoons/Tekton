# Ergon Architecture

## Overview

Ergon follows a modular, layered architecture that emphasizes separation of concerns, extensibility, and integration with other Tekton components. This document provides a detailed overview of the architectural components and their interactions.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            Client Interfaces                            │
├───────────────┬───────────────┬────────────────────┬───────────────────┤
│ REST API      │ WebSocket API │ Command-Line (CLI) │ UI Components     │
└───────┬───────┴───────┬───────┴──────────┬─────────┴─────────┬─────────┘
        │               │                  │                   │
        ▼               ▼                  ▼                   ▼
┌───────────────────────────────────────────────────────────────────────┐
│                            API Layer                                   │
├───────────────┬───────────────┬────────────────────┬─────────────────┤
│ HTTP Endpoints│ WebSocket     │ A2A Protocol       │ MCP Protocol    │
│               │ Handlers      │ Implementation     │ Implementation  │
└───────┬───────┴───────┬───────┴──────────┬─────────┴─────────┬───────┘
        │               │                  │                   │
        ▼               ▼                  ▼                   ▼
┌───────────────────────────────────────────────────────────────────────┐
│                            Core Framework                              │
├───────────────┬───────────────┬────────────────────┬─────────────────┤
│ Agent         │ Tool          │ Workflow           │ Repository      │
│ Framework     │ Registry      │ Engine             │ Manager         │
├───────────────┼───────────────┼────────────────────┼─────────────────┤
│ Agent         │ Agent         │ Memory             │ Document        │
│ Generator     │ Runner        │ Service            │ Store           │
└───────┬───────┴───────┬───────┴──────────┬─────────┴─────────┬───────┘
        │               │                  │                   │
        ▼               ▼                  ▼                   ▼
┌───────────────────────────────────────────────────────────────────────┐
│                         Integration Layer                              │
├───────────────┬───────────────┬────────────────────┬─────────────────┤
│ LLM Client    │ MCP Client    │ Memory             │ Hermes          │
│ (Rhetor)      │               │ Integration        │ Integration     │
└───────┬───────┴───────┬───────┴──────────┬─────────┴─────────┬───────┘
        │               │                  │                   │
        ▼               ▼                  ▼                   ▼
┌───────────────────────────────────────────────────────────────────────┐
│                         Persistence Layer                              │
├───────────────┬───────────────┬────────────────────┬─────────────────┤
│ Database      │ Vector        │ File               │ Memory          │
│ (SQLAlchemy)  │ Store (FAISS) │ Storage            │ Cache           │
└───────────────┴───────────────┴────────────────────┴─────────────────┘
```

## Layer Descriptions

### Client Interfaces

Entry points for users and other systems to interact with Ergon:

- **REST API**: HTTP-based API for synchronous requests
- **WebSocket API**: Real-time bidirectional communication
- **Command-Line Interface (CLI)**: Terminal-based user interface
- **UI Components**: Web-based user interface elements

### API Layer

Handles incoming requests and routes them to appropriate handlers:

- **HTTP Endpoints**: RESTful API endpoints for CRUD operations
- **WebSocket Handlers**: Real-time message processing
- **A2A Protocol Implementation**: Agent-to-agent communication
- **MCP Protocol Implementation**: Multimodal content processing

### Core Framework

Implements the primary business logic:

- **Agent Framework**: Core agent functionality
  - **Agent Generator**: Creates new agents from templates and specifications
  - **Agent Runner**: Executes agents with tools and memory context
- **Tool Registry**: Manages available tools for agents
- **Workflow Engine**: Defines and executes multi-step workflows
- **Repository Manager**: Manages code generation and repository analysis
- **Memory Service**: Provides context-aware memory operations
- **Document Store**: Maintains searchable documentation corpus

### Integration Layer

Connects Ergon to other Tekton components:

- **LLM Client**: Unified interface to language models via Rhetor
- **MCP Client**: Client for the Multimodal Cognitive Protocol
- **Memory Integration**: Connector to Engram memory system
- **Hermes Integration**: Service registration and discovery

### Persistence Layer

Manages data storage and retrieval:

- **Database (SQLAlchemy)**: Relational storage for structured data
- **Vector Store (FAISS)**: Embedding-based search for semantic retrieval
- **File Storage**: Storage for agent code and other artifacts
- **Memory Cache**: Temporary storage for performance optimization

## Component Interactions

### Agent Creation Flow

```
┌─────────┐     ┌────────────────┐     ┌─────────────────┐
│  Client │────▶│ API Controller │────▶│ Agent Generator │
└─────────┘     └────────────────┘     └────────┬────────┘
                                                │
                           ┌──────────────────┐ │ ┌─────────────┐
                           │   Vector Store   │◀┘ │  LLM Client  │
                           └──────────────────┘   │ (via Rhetor) │
                                     ▲            └──────┬───────┘
                                     │                   │
                                     └───────────────────┘
```

1. Client submits agent creation request
2. API controller validates and processes request
3. Agent generator uses LLM client to generate agent code
4. Vector store provides relevant documentation
5. Generated agent is stored in database and returned

### Agent Execution Flow

```
┌─────────┐     ┌────────────────┐     ┌────────────┐
│  Client │────▶│ API Controller │────▶│ Agent Runner│
└─────────┘     └────────────────┘     └──────┬─────┘
                                              │
    ┌───────────────┐   ┌──────────────┐     │    ┌────────────┐
    │   Database    │◀──│ Memory Service│◀────┼───▶│ Tool Registry│
    └───────────────┘   └──────────────┘     │    └────────────┘
                              ▲               │          │
                              │               │          ▼
                        ┌──────────────┐     │    ┌────────────┐
                        │  LLM Client  │◀────┴───▶│  Tool Execution│
                        └──────────────┘          └────────────┘
```

1. Client submits agent execution request
2. API controller routes to agent runner
3. Agent runner retrieves memory context
4. LLM client is used for agent reasoning
5. Tools are invoked as needed
6. Results are stored and returned to client

### A2A Communication Flow

```
┌────────────┐    ┌───────────────┐    ┌───────────────┐
│ Agent A    │───▶│ A2A Protocol  │───▶│ Agent B       │
└────────────┘    └───────┬───────┘    └───────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Memory Service│
                  └───────────────┘
```

1. Agent A sends message to Agent B
2. A2A protocol handles message routing
3. Memory service stores conversation for context
4. Agent B receives and processes the message

## Database Schema

```
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│    Agent      │       │  AgentTool    │       │     Tool      │
├───────────────┤       ├───────────────┤       ├───────────────┤
│ id            │       │ id            │       │ id            │
│ name          │       │ agent_id      │       │ name          │
│ description   │       │ tool_id       │       │ description   │
│ agent_type    │       │ config        │       │ function_name │
│ model_name    │       │ enabled       │       │ module_path   │
│ system_prompt │       │ created_at    │       │ is_async      │
│ created_at    │       └───────────────┘       └───────────────┘
│ updated_at    │               │                       ▲
└───────────────┘               │                       │
        │                       └───────────────────────┘
        │
        │                  ┌───────────────┐       ┌───────────────┐
        └─────────────────▶│ AgentFile     │       │ Memory        │
        │                  ├───────────────┤       ├───────────────┤
        │                  │ id            │       │ id            │
        │                  │ agent_id      │       │ agent_id      │
        │                  │ filename      │       │ collection_id │
        │                  │ content       │       │ content       │
        │                  │ created_at    │       │ category      │
        │                  └───────────────┘       │ importance    │
        │                                          │ created_at    │
        └─────────────────┐                        └───────────────┘
                          │
                          ▼
          ┌───────────────┐        ┌───────────────┐
          │ AgentExecution │        │ AgentMessage  │
          ├───────────────┤        ├───────────────┤
          │ id            │        │ id            │
          │ agent_id      │        │ execution_id  │
          │ status        │        │ role          │
          │ start_time    │        │ content       │
          │ end_time      │        │ created_at    │
          │ execution_time│        └───────────────┘
          │ input_data    │                ▲
          │ result        │                │
          │ error         │                │
          └───────────────┘                │
                  │                        │
                  └────────────────────────┘
```

## Core Components Details

### Agent Generator

Responsible for creating new agents from templates and user specifications:

- Determines appropriate agent type
- Generates system prompt
- Creates necessary files
- Configures tools

**Implementation:**
- `ergon/core/agents/generator.py`
- `ergon/core/agents/generators/` (type-specific generators)

### Agent Runner

Executes agents with tools, memory, and proper error handling:

- Prepares message context
- Invokes LLM for reasoning
- Manages tool execution
- Handles streaming responses

**Implementation:**
- `ergon/core/agents/runner/base/runner.py`
- `ergon/core/agents/runner/execution/` (execution handling)
- `ergon/core/agents/runner/tools/` (tool integration)

### Tool Registry

Manages the discovery, registration, and invocation of tools:

- Tool registration
- Parameter validation
- Implementation lookup
- Tool documentation

**Implementation:**
- `ergon/core/agents/runner/tools/registry.py`
- `ergon/core/agents/runner/tools/loader.py`

### Memory Service

Provides context-aware memory operations:

- Memory storage and retrieval
- Vector-based similarity search
- Memory categorization
- Importance-based filtering

**Implementation:**
- `ergon/core/memory/service.py`
- `ergon/core/memory/services/` (backend implementations)

### LLM Client

Unified interface for language model interactions:

- Provider-agnostic API
- Streaming support
- Fallback mechanisms
- Automatic formatting

**Implementation:**
- `ergon/core/llm/client.py`
- `ergon/core/llm/rhetor_adapter.py`

### MCP Client

Client for the Multimodal Cognitive Protocol:

- Content processing
- Tool registration and execution
- Context management
- Streaming support

**Implementation:**
- `ergon/core/mcp_client.py`

## Extension Points

Ergon provides several extension points for customization:

### Agent Types

Add new agent types by:
1. Creating a generator in `ergon/core/agents/generators/`
2. Registering in `ergon/core/agents/generator.py`
3. Adding to `AgentType` enum in `ergon/core/database/models.py`

### Tools

Add new tools by:
1. Implementing tool in `ergon/core/agents/tools/`
2. Creating tool definition
3. Registering with tool registry

### Memory Backends

Add new memory backends by:
1. Implementing adapter in `ergon/core/memory/services/`
2. Registering with service factory

### API Endpoints

Add new API endpoints by:
1. Creating router in `ergon/api/`
2. Implementing endpoint functions
3. Including router in main app

## Security Considerations

Ergon's architecture addresses several security concerns:

- **Tool Permissions**: Tools have limited scope and permissions
- **Input Validation**: All inputs are validated before processing
- **Authentication**: API supports authentication (optional in development)
- **Execution Isolation**: Agent execution is isolated from core system
- **Error Handling**: Robust error handling prevents information leakage