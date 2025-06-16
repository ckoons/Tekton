# Ergon Component

## Overview

Ergon is the agent framework for the Tekton ecosystem, enabling the creation, management, and orchestration of specialized AI agents that can perform a wide range of tasks. Ergon provides infrastructure for building, deploying, and executing intelligent agents with various capabilities, including tools, workflows, and integrations with other Tekton components.

## Key Features

- **Agent Creation and Management**: Generate and configure AI agents for specific tasks and domains.
- **Tool Integration**: Register, discover, and utilize tools across the Tekton ecosystem.
- **Workflow Execution**: Define and run complex workflows that coordinate multiple agents.
- **MCP (Model Control Protocol) Implementation**: Standardized protocol for multimodal content processing.
- **Multi-agent Collaboration**: Enable agents to work together on complex tasks.
- **Memory Integration**: Persistent memory storage and retrieval for agents.

## Component Architecture

### Core Modules

- **API Layer**: FastAPI server providing HTTP, WebSocket, and Event-based interfaces
- **Agent Framework**: Core logic for agent generation and execution
- **Database Layer**: SQLAlchemy models for persistent storage
- **Memory Service**: Integration with the Tekton memory ecosystem
- **LLM Client**: Unified interface to multiple language models
- **MCP Client**: Client for Multimodal Cognitive Protocol
- **Tool Registry**: Registration and discovery of available tools

### Core Components

#### Agent Generator

The `AgentGenerator` class is responsible for creating new agents based on user specifications. It:
- Generates appropriate system prompts based on agent descriptions
- Creates necessary files for agent implementation
- Configures specialized agents for specific domains (GitHub, Browser, etc.)
- Searches for relevant documentation to assist in agent creation

#### Agent Runner

The `AgentRunner` class handles the execution of agents:
- Manages tool integration and invocation
- Implements streaming responses for real-time interaction
- Provides memory integration for context-aware agents
- Handles timeouts and graceful error recovery
- Supports various agent types with specialized workflows

#### LLM Client

The `LLMClient` provides a unified interface to multiple LLM providers:
- Supports OpenAI, Anthropic, and Ollama models
- Integrates with Rhetor for advanced LLM routing
- Handles both synchronous and asynchronous completion
- Supports streaming interfaces for real-time responses

#### MCP Client

The `MCPClient` implements the Multimodal Cognitive Protocol:
- Processes multimodal content (text, images, structured data)
- Registers and executes tools via a standardized interface
- Creates and enhances contexts for state management
- Integrates with the Hermes messaging system

### Database Schema

Ergon uses a relational database with SQLAlchemy ORM:

- **Agent**: Core model representing AI agent instances
- **Tool**: Reusable functions that agents can invoke
- **Component**: Extensible unit of functionality
- **AgentFile**: Source files associated with agents
- **AgentExecution**: Execution records for tracking and analytics
- **AgentMessage**: Messages exchanged during agent execution
- **DocumentationPage**: Knowledge base for agent creation and execution
- **Memory**: Persistent memory for agents

## Integration Points

### Hermes Integration

Ergon integrates with Hermes (messaging system) for:
- Component registration
- Service discovery
- Inter-component communication

### MCP Protocol Implementation

Ergon implements the MCP protocol for standardized:
- Tool registration and invocation
- Multimodal content processing
- Context management
- Agent-to-agent communication

### LLM Integration through Rhetor

Ergon uses the Rhetor component for:
- LLM model selection and routing
- Template management
- Budget-aware model usage
- Context optimization

### Memory Integration with Engram

Ergon utilizes Engram for:
- Persistent memory storage
- Semantic search
- Structured memory organization
- Context building

## API Reference

### REST API Endpoints

- `/api/agents` - CRUD operations for agents
- `/api/agents/{agent_id}/run` - Execute an agent
- `/api/docs/crawl` - Crawl and index documentation
- `/api/docs/search` - Search documentation
- `/api/terminal/message` - Interface with terminal UI
- `/api/terminal/stream` - Stream responses to terminal UI

### WebSocket Endpoints

- `/ws` - Real-time communication for agents
- `/ws/events` - Event streaming for agent activities
- `/ws/monitor` - Monitor agent executions

### MCP API

- `/api/mcp/process` - Process multimodal content
- `/api/mcp/tools/register` - Register MCP tools
- `/api/mcp/tools/execute` - Execute MCP tools

## CLI Commands

Ergon provides a comprehensive CLI interface:

- `ergon create` - Create a new agent
- `ergon list` - List available agents
- `ergon run` - Execute an agent
- `ergon delete` - Delete an agent
- `ergon nexus` - Memory-enabled agent operations
- `ergon repo` - Repository management
- `ergon docs` - Documentation system
- `ergon tools` - Tool generation
- `ergon db` - Database management
- `ergon system` - System information
- `ergon memory` - Memory management
- `ergon latent` - Latent reasoning operations
- `ergon flow` - Workflow execution
- `ergon ui` - Launch the UI interface

## Usage Examples

### Creating an Agent

```python
from ergon.core.agents.generator import generate_agent

# Create a standard agent
agent_data = generate_agent(
    name="code_assistant",
    description="An agent that helps with code review and generation",
    model_name="claude-3-sonnet-20240229",
    tools=[{"name": "search_documentation", "description": "Search documentation"}]
)

# Create a specialized GitHub agent
github_agent = generate_agent(
    name="github_helper",
    description="An agent that interacts with GitHub repositories",
    agent_type="github"
)
```

### Running an Agent

```python
from ergon.core.agents.runner import AgentRunner
from ergon.core.database.engine import get_db_session

with get_db_session() as db:
    agent = db.query(Agent).filter(Agent.name == "code_assistant").first()
    runner = AgentRunner(agent=agent)
    
    # Run synchronously
    response = runner.run("Analyze this code for security vulnerabilities")
    
    # Run with streaming
    async for chunk in runner.arun_stream("Generate a Python script"):
        print(chunk, end="", flush=True)
```

### Using the MCP Client

```python
from ergon.core.mcp_client import MCPClient

# Create MCP client
mcp_client = MCPClient(client_name="Coding Assistant")
await mcp_client.initialize()

# Process text
result = await mcp_client.process_content(
    content="Write a function to sort a list",
    content_type="text",
    processing_options={"temperature": 0.7}
)

# Register tool
await mcp_client.register_tool(
    tool_id="code_analyzer",
    name="Code Analyzer",
    description="Analyzes code for quality and security issues",
    parameters={"code": {"type": "string", "description": "Code to analyze"}},
    returns={"issues": {"type": "array", "description": "List of issues"}}
)
```

## Configuration

Ergon is configured through:

1. **Environment Variables**: Standard configuration for keys and endpoints
2. **`.env` Files**: Local development configuration
3. **Database Settings**: Runtime configuration stored in database
4. **CLI Arguments**: Command-specific configuration

Key configuration options:

- `ERGON_MODEL`: Default LLM model to use
- `HERMES_HOST/PORT`: Connection to Hermes service
- `ERGON_MEMORY_ENABLED`: Enable/disable memory integration
- `DATABASE_URL`: Database connection string

## Deployment

Ergon can be deployed in multiple ways:

### Standard Installation

```bash
# Install Ergon
pip install -e .

# Initialize the database
ergon db init

# Start the API server
uvicorn ergon.api.app:app --host 0.0.0.0 --port 8002
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t ergon .

# Run the container
docker run -p 8002:8002 -v ~/.ergon:/app/.ergon ergon
```

### Docker Compose

```bash
# Launch with other Tekton components
docker-compose up -d
```

## Development

For development:

1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Initialize the database: `ergon db init`
4. Run tests: `pytest tests/`
5. Start in development mode: `uvicorn ergon.api.app:app --reload`