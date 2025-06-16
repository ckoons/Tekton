# Ergon User Guide

## Introduction

Ergon is the agent framework for the Tekton ecosystem, enabling users to create, manage, and execute intelligent AI agents for various tasks. This user guide will help you get started with Ergon and explore its capabilities.

## Getting Started

### Installation

Ergon is typically installed as part of the Tekton ecosystem. To install Ergon individually:

```bash
# Clone the repository
git clone https://github.com/yourusername/Tekton
cd Tekton/Ergon

# Install dependencies
pip install -e .
```

### Initial Setup

Before using Ergon, set up the environment:

```bash
# Initialize the database
ergon db init

# Configure LLM providers (optional)
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Start the API server
uvicorn ergon.api.app:app --host 0.0.0.0 --port 8002
```

### Quick Start

To quickly start using Ergon:

```bash
# Start the Ergon UI
./run_tekton_ui.sh

# Or, for UI without authentication
./run_ui_no_auth.sh

# Run the chatbot interface
./run_chatbot
```

## Using the Command Line Interface

Ergon provides a powerful command-line interface (CLI) for managing agents and other components.

### View Available Commands

```bash
# Show help
ergon --help

# Show help for a specific command
ergon create --help
```

### Create an Agent

```bash
# Create a basic agent
ergon create --name "code_assistant" --description "Helps with coding tasks" --model "gpt-4o-mini"

# Create a specialized GitHub agent
ergon create --name "github_helper" --description "Manages GitHub repositories" --type github

# Create a browser automation agent
ergon create --name "web_searcher" --description "Searches the web for information" --type browser
```

### List Agents

```bash
# List all agents
ergon list

# List agents with type filter
ergon list --type github
```

### Run an Agent

```bash
# Run an agent by ID
ergon run --id 1 --input "Generate a function to calculate prime numbers"

# Run an agent by name
ergon run --name "code_assistant" --input "Write a Python class for a binary tree"
```

### Delete an Agent

```bash
# Delete an agent by ID
ergon delete --id 1

# Delete an agent by name
ergon delete --name "code_assistant"
```

### Working with Memory

```bash
# Add items to memory
ergon memory add --context "user_preferences" --content "User prefers Python over JavaScript"

# Retrieve from memory
ergon memory get --context "user_preferences"

# Search memory
ergon memory search --query "Python preferences"
```

### Repository Management

```bash
# Analyze a code repository
ergon repo analyze --path /path/to/repo

# Generate documentation
ergon repo generate-docs --path /path/to/repo --output /path/to/output

# Generate tools from repository
ergon repo generate-tools --path /path/to/repo --output /path/to/tools
```

## Using the Web Interface

Ergon provides a web-based UI for managing agents and running interactive chat sessions.

### Accessing the UI

Once the Ergon server is running, access the UI at:

```
http://localhost:8080
```

### Creating Agents

1. Navigate to the "Agents" section
2. Click "Create New Agent"
3. Fill in the required information:
   - Name
   - Description
   - Model
   - Agent Type
4. Configure optional parameters:
   - Tools to include
   - Temperature setting
   - System prompt customization
5. Click "Create Agent"

### Running Agents

1. From the "Agents" list, select an agent
2. Click "Chat" or "Run"
3. Enter your question or command
4. View the agent's response
5. Continue the conversation as needed

### Managing Agents

1. From the "Agents" list, use the action menu for each agent
2. Available actions include:
   - Edit: Modify agent configuration
   - Clone: Create a copy with modifications
   - Delete: Remove the agent
   - Export: Save agent definition as JSON

### Using the Chatbot Interface

The chatbot interface provides a simplified way to interact with Ergon agents:

1. Access the chatbot at `http://localhost:8002/chat`
2. Select an agent from the dropdown
3. Type your message and press Enter
4. View the agent's response
5. Continue the conversation as needed

## Agent Types

Ergon supports several specialized agent types:

### Standard Agents

General-purpose agents with customizable system prompts and optional tools.

**Example Use Cases:**
- Code generation and review
- Document summarization
- Data analysis and reporting
- Creative writing assistance

### GitHub Agents

Specialized agents for interacting with GitHub repositories.

**Features:**
- Repository management
- Issue and PR tracking
- Code analysis
- Repository statistics

**Example Commands:**
- "List my repositories"
- "Create a new repository named 'my-project'"
- "Show open issues in repository 'my-project'"
- "Create a pull request from branch 'feature' to 'main'"

### Browser Agents

Agents that can browse the web and interact with websites.

**Features:**
- Web search
- Content extraction
- Form filling
- Screenshot capture

**Example Commands:**
- "Search for 'Python machine learning tutorials'"
- "Extract text from https://example.com"
- "Fill out the contact form at https://example.com/contact"
- "Take a screenshot of https://example.com"

### Mail Agents

Agents for email management and automation.

**Features:**
- Email reading and sending
- Inbox organization
- Email content analysis
- Automated responses

**Example Commands:**
- "Summarize my unread emails"
- "Send an email to john@example.com about the project status"
- "Find emails from alice@example.com"
- "Create a draft reply to the latest email"

### Nexus Agents

Memory-enabled agents that can remember conversations and context.

**Features:**
- Persistent memory
- Context-aware responses
- Personalized interactions
- Memory search and recall

**Example Commands:**
- "What do you remember about our last conversation?"
- "Remember that I prefer dark mode in applications"
- "What do you know about my project preferences?"
- "Forget the information about project XYZ"

## Working with Tools

Agents can use various tools to enhance their capabilities.

### Available Tool Categories

1. **System Tools**
   - File operations
   - Environment information
   - Process management

2. **Data Tools**
   - JSON parsing
   - CSV manipulation
   - Data analysis

3. **Web Tools**
   - URL fetching
   - Web scraping
   - API requests

4. **Code Tools**
   - Code parsing
   - Static analysis
   - Code generation

### Adding Tools to Agents

**Via CLI:**
```bash
ergon create --name "data_agent" --tools json_parser,csv_reader,data_analyzer
```

**Via API:**
```python
import requests

requests.post("http://localhost:8002/api/agents", json={
    "name": "data_agent",
    "description": "Agent for data analysis",
    "model_name": "claude-3-sonnet-20240229",
    "tools": [
        {"name": "json_parser", "description": "Parse JSON data"},
        {"name": "csv_reader", "description": "Read CSV files"},
        {"name": "data_analyzer", "description": "Analyze data"}
    ]
})
```

**Via UI:**
1. In the agent creation form, go to the "Tools" section
2. Select tools from the available list
3. Configure tool-specific parameters if needed

### Creating Custom Tools

**Define a Tool Function:**
```python
def custom_tool(parameter1, parameter2):
    """
    A custom tool for specific operations.
    
    Args:
        parameter1: Description of parameter1
        parameter2: Description of parameter2
        
    Returns:
        Result of the operation
    """
    # Tool implementation
    result = do_something(parameter1, parameter2)
    return result
```

**Register the Tool:**
```python
from ergon.core.agents.tools.registry import tool_registry

tool_registry.register(
    "custom_tool",
    custom_tool,
    {
        "name": "custom_tool",
        "description": "A custom tool for specific operations",
        "parameters": {
            "parameter1": {"type": "string", "description": "Description of parameter1"},
            "parameter2": {"type": "integer", "description": "Description of parameter2"}
        }
    }
)
```

## Working with Workflows

Ergon supports defining and executing workflows that coordinate multiple agents.

### Defining a Workflow

**Create a workflow definition:**
```python
from ergon.core.flow.base import Workflow, Step

workflow = Workflow(
    name="data_processing",
    description="Process and analyze data",
    steps=[
        Step(
            name="fetch_data",
            agent="data_fetcher",
            input_template="Fetch data from {source}",
            output_variable="raw_data"
        ),
        Step(
            name="process_data",
            agent="data_processor",
            input_template="Process this data: {raw_data}",
            output_variable="processed_data"
        ),
        Step(
            name="analyze_data",
            agent="data_analyzer",
            input_template="Analyze this processed data: {processed_data}",
            output_variable="analysis"
        )
    ]
)
```

### Running a Workflow

**Via CLI:**
```bash
ergon flow run --name "data_processing" --params '{"source": "https://example.com/data.csv"}'
```

**Via API:**
```python
import requests

requests.post("http://localhost:8002/api/flow/run", json={
    "workflow_name": "data_processing",
    "parameters": {
        "source": "https://example.com/data.csv"
    }
})
```

**Via UI:**
1. Go to the "Workflows" section
2. Select a workflow
3. Fill in the required parameters
4. Click "Run Workflow"
5. Monitor progress and results

## Memory System

Ergon includes a memory system for agents to store and retrieve information.

### Memory Categories

- **Short-term**: Recent conversation context
- **Long-term**: Persistent information across sessions
- **Semantic**: Conceptual knowledge and associations
- **Episodic**: Past interactions and events
- **Procedural**: How to perform specific tasks

### Using Memory Commands

**Add to Memory:**
```bash
ergon memory add --category "user_preference" --content "User prefers dark mode"
```

**Retrieve from Memory:**
```bash
ergon memory get --category "user_preference"
```

**Search Memory:**
```bash
ergon memory search --query "user preferences"
```

**Delete from Memory:**
```bash
ergon memory delete --id "mem_12345"
```

### Agent Memory Context

Agents automatically receive relevant memory context based on the conversation:

1. The user input is analyzed for relevant topics
2. Related memories are retrieved
3. Memories are injected into the conversation context
4. The agent responds with awareness of this context

## Integration with Other Tekton Components

Ergon integrates with other Tekton components:

### Rhetor Integration

Ergon uses Rhetor for LLM management:

- Model selection
- Prompt templates
- Token budget management

### Engram Integration

Ergon uses Engram for memory management:

- Vector storage for semantic search
- Memory persistence
- Context retrieval

### Hermes Integration

Ergon registers with Hermes for:

- Service discovery
- Component communication
- Event broadcasting

### Synthesis Integration

Ergon can participate in Synthesis workflows:

- Multi-component processes
- Conditional execution
- Parallel processing

## Advanced Usage

### Custom Agent Templates

Create custom agent templates for specific use cases:

1. Define a template in `ergon/core/agents/generators/`
2. Implement the generator function
3. Register the template type
4. Use the template with `--type` parameter

### Tool Chaining

Build complex capabilities by chaining multiple tools:

1. Create a composite tool that uses multiple base tools
2. Define clear input/output interfaces
3. Handle data transformation between tools

### Agent-to-Agent Communication

Enable agents to collaborate:

1. Use the A2A protocol to connect agents
2. Define message formats for collaboration
3. Manage communication through the A2A API

### Memory Optimization

Optimize agent memory for better performance:

1. Use importance scoring to prioritize memories
2. Set appropriate retention policies
3. Categorize memories for efficient retrieval

## Troubleshooting

### Common Issues

#### Agent Creation Fails
- Check model availability
- Verify API keys are configured
- Ensure Hermes is running if integrated

#### Agent Execution Timeout
- Increase timeout setting
- Simplify the task
- Break into multiple smaller tasks

#### Memory Retrieval Issues
- Check vector store status
- Verify memory service is running
- Optimize search query

#### Tool Execution Errors
- Verify tool implementation
- Check parameter types
- Ensure dependencies are installed

### Logging

Enable detailed logging for troubleshooting:

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG

# Run with logging
ergon --log-level DEBUG run --name "agent_name" --input "test input"
```

### Diagnostics

Run diagnostics to check system health:

```bash
# Check system status
ergon system status

# Verify component connectivity
ergon system check-connections

# Test LLM connectivity
ergon system test-llm
```

## Best Practices

### Agent Design

- **Clear Purpose**: Define a focused purpose for each agent
- **Effective System Prompts**: Craft clear, specific system prompts
- **Tool Selection**: Include only relevant tools for the task
- **Temperature Setting**: Adjust based on creativity vs precision needed

### Performance Optimization

- **Minimize Context**: Keep conversation context focused
- **Use Tools**: Delegate complex operations to tools rather than LLM
- **Memory Management**: Regularly clean up unused memories
- **Batch Operations**: Group similar operations for efficiency

### Security Considerations

- **API Key Protection**: Store API keys securely
- **Tool Permissions**: Limit tool capabilities to necessary functions
- **Input Validation**: Validate user inputs before processing
- **Output Sanitization**: Sanitize agent outputs if needed

## Examples

### Code Assistant Agent

```bash
# Create a code assistant
ergon create --name "code_helper" --description "Helps with Python coding tasks" --type code

# Run specific coding tasks
ergon run --name "code_helper" --input "Write a Python function to find the most frequent element in a list"
```

### GitHub Operations Agent

```bash
# Create a GitHub agent
ergon create --name "github_manager" --description "Manages GitHub repositories" --type github

# Perform GitHub operations
ergon run --name "github_manager" --input "Create a new repository named 'my-project' with Python .gitignore"
```

### Data Analysis Workflow

```bash
# Create a workflow for data analysis
ergon flow create --file data_analysis_workflow.json

# Run the workflow with parameters
ergon flow run --name "data_analysis" --params '{"data_source": "sales_data.csv", "analysis_type": "trend"}'
```

### Browser Automation Agent

```bash
# Create a browser agent
ergon create --name "web_assistant" --description "Browses the web and extracts information" --type browser

# Perform web tasks
ergon run --name "web_assistant" --input "Search for the latest machine learning papers and summarize the top 3 results"
```