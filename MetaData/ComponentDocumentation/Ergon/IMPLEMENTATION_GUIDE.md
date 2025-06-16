# Ergon Implementation Guide

## Introduction

This guide provides detailed implementation information for the Ergon component within the Tekton ecosystem. It covers architecture decisions, implementation patterns, and integration guidelines for developers working with or extending the Ergon framework.

## Architecture Overview

Ergon follows a modular, layered architecture that separates concerns into distinct components:

```
┌────────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                       │
├───────────────┬──────────────────┬───────────────┬─────────────┤
│ HTTP Endpoints│  WebSocket API   │ MCP Endpoints │   A2A API   │
├───────────────┴──────────────────┴───────────────┴─────────────┤
│                      Core Framework                            │
├───────────┬───────────┬────────────┬────────────┬──────────────┤
│  Agents   │   Tools   │ Workflows  │  Memory    │ Repository   │
├───────────┴───────────┴────────────┴────────────┴──────────────┤
│                    Integration Layer                           │
├─────────────┬────────────┬────────────┬─────────────┬──────────┤
│   Hermes    │   Rhetor   │   Engram   │    MCP      │  Tekton  │
├─────────────┴────────────┴────────────┴─────────────┴──────────┤
│                    Persistence Layer                           │
├────────────────────────┬───────────────────────────────────────┤
│       SQLAlchemy       │      Vector Store (FAISS)            │
└────────────────────────┴───────────────────────────────────────┘
```

### Key Components

#### 1. API Layer

The API layer is implemented using FastAPI and provides multiple interfaces:

- **HTTP REST API**: Standard synchronous API endpoints
- **WebSocket API**: Real-time communication and streaming
- **MCP Endpoints**: Multimodal Cognitive Protocol interface
- **A2A Endpoints**: Agent-to-Agent communication protocol

Implementation files:
- `ergon/api/app.py`: Main FastAPI application
- `ergon/api/mcp_endpoints.py`: MCP-specific endpoints
- `ergon/api/a2a_endpoints.py`: Agent-to-Agent endpoints

#### 2. Core Framework

The core framework implements the primary functionality:

- **Agents**: Generation, execution, and lifecycle management
- **Tools**: Registration, discovery, and invocation
- **Workflows**: Definition and execution of agent workflows
- **Memory**: Integration with the Tekton memory system
- **Repository**: Code generation and management

Implementation files:
- `ergon/core/agents/`: Agent-related functionality
- `ergon/core/flow/`: Workflow engine
- `ergon/core/memory/`: Memory integration
- `ergon/core/repository/`: Code generation and analysis

#### 3. Integration Layer

The integration layer connects Ergon to other Tekton components:

- **Hermes**: Service registration and discovery
- **Rhetor**: LLM integration and prompt management
- **Engram**: Memory persistence and retrieval
- **MCP**: Protocol implementation for multimodal processing
- **Tekton**: Core system integration

Implementation files:
- `ergon/utils/hermes_helper.py`: Hermes integration
- `ergon/core/llm/rhetor_adapter.py`: Rhetor integration
- `ergon/core/memory/service.py`: Engram integration
- `ergon/core/mcp_client.py`: MCP client implementation

#### 4. Persistence Layer

The persistence layer handles data storage:

- **SQLAlchemy**: Relational database access
- **Vector Store**: FAISS-based embedding storage

Implementation files:
- `ergon/core/database/`: Database models and engine
- `ergon/core/vector_store/`: Vector storage implementation

## Implementation Patterns

### Agent Generation

Ergon uses a combination of templates and LLM-powered generation to create agents:

1. **Template Selection**: Identify the appropriate base template
2. **LLM Enhancement**: Use LLM to customize and extend the template
3. **Fallback Mechanism**: Built-in fallbacks for LLM generation failures
4. **Tool Integration**: Automatic integration of required tools

```python
# Agent generation pattern
async def generate_agent(name, description, tools=None):
    # 1. Select template based on agent type
    # 2. Use LLM to enhance template with specifics
    # 3. Provide fallbacks for generation failures
    # 4. Integrate tools and create final agent
```

### Agent Execution

Agents are executed through a robust runner infrastructure:

1. **Message Preparation**: Format user input
2. **Context Enhancement**: Add memory and context
3. **Tool Selection**: Determine if tools are needed
4. **Execution**: Run with or without tools
5. **Result Processing**: Format and store results

```python
# Agent execution pattern
async def run_agent(agent, input_text):
    # 1. Prepare messages with user input
    # 2. Add memory context for continuity
    # 3. Check if agent has tools
    # 4. Execute the agent with appropriate method
    # 5. Process and return results
```

### LLM Abstraction

The LLM client provides a unified interface for model access:

1. **Provider Detection**: Identify model provider
2. **Adapter Selection**: Choose appropriate adapter
3. **Format Conversion**: Convert messages to provider format
4. **Streaming Support**: Standard interface for streaming
5. **Fallback Mechanisms**: Graceful degradation when primary provider fails

```python
# LLM abstraction pattern
async def complete(messages):
    # 1. Detect provider based on model name
    # 2. Select Rhetor adapter or direct provider
    # 3. Format messages for chosen provider
    # 4. Make API call with appropriate parameters
    # 5. Process and return response
```

### Tool Registration

Tools follow a consistent registration pattern:

1. **Tool Definition**: Define name, description, parameters
2. **Handler Association**: Connect to implementation function
3. **Registration**: Register with the tool registry
4. **Discovery**: Make available to agents

```python
# Tool registration pattern
async def register_tool(tool_id, name, description, parameters, handler):
    # 1. Format tool definition
    # 2. Associate with handler function
    # 3. Register with tool registry
    # 4. Make discoverable to agents
```

## Integration Guidelines

### Adding a New Agent Type

To add a new agent type:

1. Create a new generator in `ergon/core/agents/generators/`
2. Add specialized tools in `ergon/core/agents/tools/`
3. Update the agent type enum in `ergon/core/database/models.py`
4. Implement any specialized handlers in `ergon/core/agents/runner/handlers/`
5. Update UI components if needed

Example:
```python
# 1. Create generator
def generate_custom_agent(name, description, model_name):
    # Implementation
    
# 2. Add to generator.py
elif agent_type == "custom":
    from .generators.custom_generator import generate_custom_agent
    return generate_custom_agent(name, description, model_name)
```

### Adding New Tools

To add new tools:

1. Create a tool implementation in `ergon/core/agents/tools/`
2. Define the tool schema in JSON format
3. Create a registration function
4. Add to tool registry

Example:
```python
# Tool implementation
def analyze_data(data):
    # Implementation
    
# Tool registration
tool_definition = {
    "name": "analyze_data",
    "description": "Analyzes provided data",
    "parameters": {
        "data": {"type": "object", "description": "Data to analyze"}
    }
}

# Register with registry
tool_registry.register("analyze_data", analyze_data, tool_definition)
```

### Integrating with Other Components

To integrate with other Tekton components:

1. Import and use the component's client library
2. Configure environment variables
3. Use dependency injection for testing
4. Register capabilities with Hermes

Example:
```python
# Rhetor integration
from rhetor.client import RhetorClient

rhetor_client = RhetorClient()
await rhetor_client.initialize()

# Use the client
response = await rhetor_client.generate_prompt(template_name, variables)
```

## Extending the Framework

### Creating Custom Agent Runners

To create a custom agent runner:

1. Subclass `BaseRunner` in `ergon/core/agents/runner/base/runner.py`
2. Override the `arun` method
3. Register the runner with the runner registry

Example:
```python
from ergon.core.agents.runner.base.runner import BaseRunner

class CustomRunner(BaseRunner):
    async def arun(self, input_text):
        # Custom implementation
        return result
```

### Implementing New Memory Services

To add a new memory backend:

1. Create an adapter in `ergon/core/memory/services/`
2. Implement required interface methods
3. Register with the memory service factory

Example:
```python
from ergon.core.memory.services.base import BaseMemoryService

class CustomMemoryService(BaseMemoryService):
    async def add(self, key, value):
        # Implementation
    
    async def get(self, key):
        # Implementation
```

### Adding New API Endpoints

To add new API endpoints:

1. Create a router in `ergon/api/`
2. Implement endpoint functions
3. Include the router in the main app

Example:
```python
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/custom", tags=["custom"])

@router.get("/endpoint")
async def custom_endpoint():
    # Implementation
    return {"result": "success"}
    
# In app.py
app.include_router(custom_router)
```

## Performance Considerations

### LLM Efficiency

- **Prompt Engineering**: Carefully design system prompts for efficiency
- **Context Management**: Minimize context size for faster processing
- **Tool Usage**: Prefer tools over asking the LLM to perform complex tasks
- **Caching**: Implement result caching for repeated operations

### Database Optimization

- **Indexing**: Create appropriate indexes for common queries
- **Connection Pooling**: Use connection pools for efficiency
- **Batch Operations**: Group database operations where possible
- **Query Optimization**: Use select_from and join clauses properly

### Memory Management

- **Vector Pruning**: Implement regular vector store pruning
- **Importance Filtering**: Filter memories by importance
- **Chunking**: Split large documents into manageable chunks
- **Embedding Reuse**: Cache embeddings for similar content

## Testing Guidelines

### Unit Testing

Unit tests should focus on isolated components:

- **Agent Generation**: Test template generation
- **Tool Functionality**: Test individual tools
- **Database Models**: Test model relationships

Example:
```python
def test_agent_generator():
    # Test agent generation
    agent = generate_agent("test", "Test agent")
    assert agent["name"] == "test"
    assert "system_prompt" in agent
```

### Integration Testing

Integration tests should verify component interactions:

- **API Endpoints**: Test HTTP responses
- **Tool Invocation**: Test tool execution through agents
- **Database Operations**: Test full CRUD operations

Example:
```python
async def test_api_create_agent():
    # Test API endpoint
    response = await client.post("/api/agents", json={
        "name": "test",
        "description": "Test agent"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test"
```

### Mock LLM Testing

Use mock LLM responses for deterministic testing:

- **Mock Responses**: Predefined responses for known inputs
- **Error Simulation**: Test error handling
- **Timeout Testing**: Verify timeout behavior

Example:
```python
class MockLLMClient:
    async def acomplete(self, messages):
        # Return predefined response based on input
        return "Mock response"
```

## Deployment Guidelines

### Configuration

Configure Ergon using environment variables or .env files:

- **Database**: `DATABASE_URL`
- **LLM Keys**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- **Integration URLs**: `HERMES_URL`, `RHETOR_URL`
- **Settings**: `LOG_LEVEL`, `DEBUG_MODE`

### Docker Deployment

Deploy using Docker with proper volume mapping:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .
RUN pip install -e .

VOLUME /app/.ergon
VOLUME /app/data

EXPOSE 8002

CMD ["uvicorn", "ergon.api.app:app", "--host", "0.0.0.0", "--port", "8002"]
```

### Scaling Considerations

For scaling in production:

- **Connection Pooling**: Configure database connection pools
- **Load Balancing**: Deploy multiple instances with load balancing
- **Caching**: Implement Redis or similar for caching
- **Background Processing**: Use Celery for long-running tasks
- **Monitoring**: Add Prometheus metrics and logging

## Troubleshooting

Common issues and solutions:

### Database Issues

- **Connection Issues**: Check DATABASE_URL environment variable
- **Migration Failures**: Run `ergon db reset` to rebuild the database
- **Performance Problems**: Check for missing indexes

### LLM Integration

- **API Key Errors**: Verify API keys in environment variables
- **Timeout Issues**: Increase timeout settings
- **Model Availability**: Check if selected models are available

### Tool Execution

- **Tool Not Found**: Verify tool registration
- **Parameter Errors**: Check tool parameter definitions
- **Execution Failures**: Enable debug logging for tool execution

### Memory Integration

- **Vector Store Issues**: Check vector store configuration
- **Embedding Errors**: Verify embedding model availability
- **Memory Retrieval Problems**: Check similarity threshold settings