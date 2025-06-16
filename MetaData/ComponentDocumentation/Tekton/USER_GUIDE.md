# Tekton User Guide

## Introduction

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This guide will help you understand how to use Tekton effectively for your development workflow.

## Getting Started

### Installation

To install Tekton, follow these steps:

1. Clone the Tekton repository:
   ```bash
   git clone https://github.com/yourusername/Tekton.git
   cd Tekton
   ```

2. Set up the environment:
   ```bash
   # Create a virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. Configure Tekton:
   ```bash
   # Create the configuration directory
   mkdir -p ~/.tekton/data

   # Copy sample configuration
   cp config/tekton.json.sample ~/.tekton/tekton.json
   ```

### Basic Usage

To launch Tekton with the default components:

```bash
# Launch with default components (Engram, Hermes, Rhetor)
./scripts/tekton-launch

# Launch all available components
./scripts/tekton-launch --launch-all

# Launch specific components
./scripts/tekton-launch --components engram,hermes,ergon
```

The Web UI is available at http://localhost:8080 after launching Tekton.

To check the status of Tekton components:

```bash
./scripts/tekton-status
```

To stop all Tekton components:

```bash
./scripts/tekton-kill
```

## Configuration

### Environment Variables

Tekton can be configured through environment variables:

```bash
# Core Configuration
export TEKTON_HOST=0.0.0.0
export TEKTON_PORT=8010
export TEKTON_DEBUG=false

# Component Ports
export HEPHAESTUS_PORT=8080
export ENGRAM_PORT=8000
export HERMES_PORT=8001
export ERGON_PORT=8002
export RHETOR_PORT=8003
export TERMA_PORT=8004
export ATHENA_PORT=8005
export PROMETHEUS_PORT=8006
export HARMONIA_PORT=8007
export TELOS_PORT=8008
export SYNTHESIS_PORT=8009

# Model Configuration
export LLM_MODEL_TYPE=claude
export LLM_MODEL=claude-3-sonnet-20240229
```

### Configuration Files

You can also configure Tekton through JSON configuration files:

**~/.tekton/tekton.json:**
```json
{
  "tekton": {
    "host": "0.0.0.0",
    "port": 8010,
    "data_dir": "/path/to/data",
    "log_level": "info",
    "components": {
      "startup_timeout": 60,
      "heartbeat_interval": 10,
      "heartbeat_timeout": 30
    }
  }
}
```

**config/components.json:**
```json
{
  "components": [
    {
      "component_id": "my_component",
      "component_name": "My Custom Component",
      "component_type": "service",
      "version": "1.0.0",
      "dependencies": ["engram", "rhetor"],
      "launch_command": "python -m my_component.main --port 8500",
      "environment": {
        "MY_COMPONENT_PORT": "8500"
      },
      "health_check": {
        "endpoint": "http://localhost:8500/health",
        "timeout": 30
      }
    }
  ]
}
```

## Tekton Components

Tekton consists of several core components that work together to provide an integrated AI orchestration system:

### Core Components

- **Engram**: Persistent memory system for storing and retrieving context
- **Hermes**: Service registry and messaging system for component communication
- **Rhetor**: LLM management system for coordinating AI model access
- **Ergon**: Agent system for executing tasks and tools
- **Hephaestus**: UI system for user interaction

### Additional Components

- **Athena**: Knowledge graph for maintaining structured data
- **Prometheus**: Planning system for task decomposition and execution planning
- **Harmonia**: Workflow system for orchestrating complex tasks
- **Telos**: Requirements system for managing specifications
- **Terma**: Terminal system for command-line interaction
- **Synthesis**: Execution engine for running complex workflows

## Working with LLMs

Tekton provides a unified interface for working with different LLM providers:

### Selecting a Model

You can specify a model type and specific model when launching Tekton:

```bash
# Use Claude
./scripts/tekton-launch --model-type claude --model claude-3-sonnet-20240229

# Use Ollama
./scripts/tekton-launch --model-type ollama --model llama3
```

### Model Tiers

Tekton organizes models into tiers based on their capabilities:

1. **Tier 1 (Local Lightweight)**
   - File operations, codebase navigation, simple edits
   - Models: CodeLlama, Deepseek Coder
   - Preferred for: Quick operations, searching, basic analysis

2. **Tier 2 (Local Midweight)**
   - Code understanding, simple debugging, refactoring
   - Models: Local Claude Haiku, Qwen
   - Preferred for: More complex code tasks, initial problem analysis

3. **Tier 3 (Remote Heavyweight)**
   - Complex reasoning, architectural design, difficult debugging
   - Models: Claude 3.7 Sonnet, GPT-4
   - Preferred for: Tasks requiring deep reasoning or cross-domain knowledge

### Setting API Keys

To use remote LLM providers, you need to set API keys:

```bash
# Set Anthropic API key for Claude
export ANTHROPIC_API_KEY=your_api_key_here

# Set OpenAI API key for GPT models
export OPENAI_API_KEY=your_api_key_here
```

## Web UI (Hephaestus)

Tekton includes a web-based user interface through the Hephaestus component:

### Dashboard

The Dashboard provides an overview of the Tekton system:

- **Component Status**: View the status of all components
- **System Resources**: Monitor CPU, memory, and GPU usage
- **Recent Activity**: See recent tasks and their status
- **Model Usage**: Track which models are being used and their performance

### Terminal (Terma)

The Terminal interface allows you to interact with Tekton via a chat interface:

1. **Text Input**: Enter text prompts in the input box
2. **Code Input**: Use triple backticks for code blocks
3. **File Management**: Upload and download files
4. **Tool Usage**: Access to various tools through the terminal

### Memory Explorer (Engram)

The Memory Explorer allows you to browse and search the memory system:

1. **Collections**: Browse different memory collections
2. **Search**: Search for specific entries by keyword or vector similarity
3. **Visualization**: View relationships between memory entries
4. **Edit**: Modify or delete memory entries

### Knowledge Graph (Athena)

The Knowledge Graph visualizer allows you to explore structured data:

1. **Graph View**: Visualize entities and relationships
2. **Query Interface**: Run graph queries
3. **Entity Management**: Create, update, and delete entities
4. **Relationship Management**: Define and modify relationships

## Command Line Interface

Tekton provides a command line interface for various operations:

### Component Management

```bash
# Start a specific component
./scripts/tekton-launch --components rhetor

# Check component status
./scripts/tekton-status

# Stop a specific component
./scripts/tekton-kill --component rhetor
```

### Model Management

```bash
# List available models
curl http://localhost:8010/api/tekton/models

# Get model capabilities
curl http://localhost:8010/api/tekton/capabilities
```

### Resource Monitoring

```bash
# Get system resource usage
curl http://localhost:8010/api/tekton/resources

# Get component resource usage
curl http://localhost:8010/api/tekton/components/rhetor/resources
```

## Integrating Custom Components

You can integrate your own components with Tekton:

### Component Registration

Create a Python component that registers with Tekton:

```python
from tekton.utils.tekton_registration import register_with_tekton

async def start_my_component():
    # Register with Tekton
    success = await register_with_tekton(
        component_id="my_component",
        component_name="My Custom Component",
        component_type="service",
        version="1.0.0",
        capabilities=["data_processing", "visualization"],
        dependencies=["engram", "rhetor"],
        port=8500
    )
    
    if success:
        print("Component registered successfully")
    else:
        print("Failed to register component")
```

### Component Communications

Components can communicate with each other through Hermes:

```python
from tekton.utils.component_client import find_component

async def use_other_components():
    # Find the Engram component
    engram = await find_component("engram")
    
    if engram:
        # Use Engram's API
        response = await engram.call_api("/api/memory/store", method="POST", data={
            "key": "my_data",
            "value": {"some": "data"}
        })
        print(f"Engram response: {response}")
```

### Component Lifecycle

Implement the component lifecycle methods:

```python
from tekton.core.lifecycle import ComponentState

class MyComponent:
    async def initialize(self):
        # Initialize resources
        pass
    
    async def start(self):
        # Start services
        pass
    
    async def stop(self):
        # Clean up resources
        pass
    
    async def send_heartbeat(self):
        # Send heartbeat to Tekton
        await send_heartbeat(
            component_id="my_component",
            instance_uuid=self.instance_uuid,
            state=ComponentState.READY.value,
            metrics={
                "cpu_percent": 15.2,
                "memory_percent": 12.5,
                "active_connections": 5
            }
        )
```

## Using Memory (Engram)

Tekton provides persistent memory through the Engram component:

### Storing Data

```python
from tekton.utils.component_client import find_component

async def store_data():
    engram = await find_component("engram")
    
    # Store data
    await engram.call_api("/api/memory/store", method="POST", data={
        "collection": "projects",
        "key": "project_123",
        "value": {
            "name": "Sample Project",
            "description": "A project for testing Tekton",
            "created_at": "2025-04-30T15:20:30Z"
        },
        "metadata": {
            "tags": ["sample", "test"],
            "owner": "user123"
        }
    })
```

### Retrieving Data

```python
async def retrieve_data():
    engram = await find_component("engram")
    
    # Retrieve data by key
    response = await engram.call_api("/api/memory/retrieve", method="GET", params={
        "collection": "projects",
        "key": "project_123"
    })
    
    project = response["value"]
    print(f"Project name: {project['name']}")
```

### Searching

```python
async def search_data():
    engram = await find_component("engram")
    
    # Search by metadata
    response = await engram.call_api("/api/memory/search", method="POST", data={
        "collection": "projects",
        "query": {
            "metadata.tags": "sample"
        }
    })
    
    for item in response["results"]:
        print(f"Found: {item['value']['name']}")
    
    # Vector search
    response = await engram.call_api("/api/memory/vector_search", method="POST", data={
        "collection": "projects",
        "text": "sample project description",
        "limit": 5
    })
    
    for item in response["results"]:
        print(f"Similar: {item['value']['name']} (score: {item['score']})")
```

## Using LLMs (Rhetor)

Interact with LLMs through the Rhetor component:

### Text Generation

```python
from tekton.utils.component_client import find_component

async def generate_text():
    rhetor = await find_component("rhetor")
    
    # Generate text
    response = await rhetor.call_api("/api/generate", method="POST", data={
        "prompt": "Explain what Tekton is in one paragraph.",
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 100
    })
    
    print(f"Generated text: {response['text']}")
```

### Chat Completion

```python
async def chat_completion():
    rhetor = await find_component("rhetor")
    
    # Chat completion
    response = await rhetor.call_api("/api/chat", method="POST", data={
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Tekton?"}
        ],
        "model": "claude-3-sonnet-20240229",
        "temperature": 0.7
    })
    
    print(f"Assistant response: {response['message']['content']}")
```

### Streaming Responses

For streaming responses, use WebSockets:

```python
import asyncio
import websockets
import json

async def stream_chat():
    rhetor = await find_component("rhetor")
    port = rhetor.port
    
    # Create WebSocket connection
    uri = f"ws://localhost:{port}/ws/chat"
    
    async with websockets.connect(uri) as websocket:
        # Send request
        await websocket.send(json.dumps({
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Write a short poem about programming."}
            ],
            "model": "claude-3-sonnet-20240229",
            "stream": True
        }))
        
        # Receive streaming response
        full_response = ""
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "content":
                chunk = data["content"]
                full_response += chunk
                print(chunk, end="", flush=True)
            elif data["type"] == "end":
                break
        
        print("\nFull response:", full_response)
```

## Working with Agents (Ergon)

Tekton provides agent functionality through the Ergon component:

### Creating an Agent

```python
from tekton.utils.component_client import find_component

async def create_agent():
    ergon = await find_component("ergon")
    
    # Create an agent
    response = await ergon.call_api("/api/agents", method="POST", data={
        "agent_id": "code_assistant",
        "agent_name": "Code Assistant",
        "description": "An agent that helps with coding tasks",
        "capabilities": ["code_generation", "code_review", "code_explanation"],
        "system_prompt": "You are a helpful coding assistant. Your goal is to help the user with coding tasks."
    })
    
    agent_id = response["agent_id"]
    print(f"Created agent with ID: {agent_id}")
```

### Running Agent Tasks

```python
async def run_agent_task():
    ergon = await find_component("ergon")
    
    # Create a task
    response = await ergon.call_api("/api/agents/code_assistant/tasks", method="POST", data={
        "task_type": "code_generation",
        "inputs": {
            "language": "python",
            "description": "Write a function that calculates the fibonacci sequence"
        },
        "tools": ["code_search", "code_execution"],
        "system_context": "The user needs help generating a Python function."
    })
    
    task_id = response["task_id"]
    print(f"Created task with ID: {task_id}")
    
    # Poll for task completion
    while True:
        status = await ergon.call_api(f"/api/tasks/{task_id}/status", method="GET")
        
        if status["state"] == "completed":
            result = await ergon.call_api(f"/api/tasks/{task_id}/result", method="GET")
            print(f"Task completed with result: {result['output']}")
            break
        elif status["state"] == "failed":
            print(f"Task failed with error: {status['error']}")
            break
        
        await asyncio.sleep(1)
```

## Single Port Architecture

All Tekton components follow a Single Port Architecture with standardized endpoints:

### HTTP Endpoints

```
# Component Base URL
http://localhost:{PORT}/

# API Endpoints
http://localhost:{PORT}/api/...

# Health Check
http://localhost:{PORT}/api/health

# Ready Check
http://localhost:{PORT}/api/ready

# Component-Specific Endpoints
http://localhost:{PORT}/api/component-specific/...
```

### WebSocket Endpoints

```
# WebSocket Base URL
ws://localhost:{PORT}/ws/

# Component-Specific WebSocket Endpoints
ws://localhost:{PORT}/ws/component-specific/...
```

### Event Endpoints

```
# Event Base URL
http://localhost:{PORT}/events/

# Component-Specific Event Endpoints
http://localhost:{PORT}/events/component-specific/...
```

## Troubleshooting

### Common Issues

#### Component Fails to Start

If a component fails to start:

1. Check the component logs:
   ```bash
   cat ~/.tekton/logs/{component_name}.log
   ```

2. Verify dependencies are running:
   ```bash
   ./scripts/tekton-status
   ```

3. Check port availability:
   ```bash
   lsof -i :{PORT}
   ```

4. Restart the component:
   ```bash
   ./scripts/tekton-kill --component {component_name}
   ./scripts/tekton-launch --components {component_name}
   ```

#### Connection Issues

If components can't connect to each other:

1. Verify components are registered:
   ```bash
   curl http://localhost:8001/api/registry/services
   ```

2. Check environment variables:
   ```bash
   env | grep TEKTON
   ```

3. Restart Hermes:
   ```bash
   ./scripts/tekton-kill --component hermes
   ./scripts/tekton-launch --components hermes
   ```

#### Memory Issues

If you encounter memory-related errors:

1. Check Engram status:
   ```bash
   curl http://localhost:8000/health
   ```

2. Reset Engram:
   ```bash
   ./scripts/tekton-kill --component engram
   rm -rf ~/.tekton/data/engram/*
   ./scripts/tekton-launch --components engram
   ```

### Logging

Tekton logs are stored in `~/.tekton/logs/`:

```bash
# View logs for a specific component
cat ~/.tekton/logs/engram.log

# View logs for Tekton core
cat ~/.tekton/logs/tekton.log

# Follow logs in real-time
tail -f ~/.tekton/logs/rhetor.log
```

### Monitoring

You can monitor Tekton components through the Web UI or command line:

```bash
# Check component status
./scripts/tekton-status

# Monitor resource usage
watch -n 5 './scripts/tekton-status | grep Resource'

# Check system health
curl http://localhost:8010/api/tekton/health
```

## Best Practices

### System Configuration

- **Memory Allocation**: Allocate enough memory for vector operations (at least 8GB RAM)
- **GPU Acceleration**: Use GPU for embedding and large model inference
- **Storage Planning**: Allocate sufficient disk space for persistent storage
- **Network Configuration**: Ensure ports 8000-8010 and 8080 are available

### Component Usage

- **Start Order**: Always start Hermes first, followed by Engram and other components
- **Dependency Management**: Ensure required components are running before dependent ones
- **Resource Monitoring**: Regularly check resource usage and scale as needed
- **Heartbeat Monitoring**: Set up alerts for missed heartbeats

### Performance Optimization

- **Tiered Processing**: Use the simplest model that can handle the task
- **Memory Caching**: Configure Engram with appropriate caching settings
- **Batch Operations**: Batch similar operations together for efficiency
- **Result Caching**: Cache frequent queries and generations

## Advanced Topics

### Custom Model Integration

To integrate a custom model:

```python
from tekton.core.models.adapters import BaseModelAdapter

class CustomModelAdapter(BaseModelAdapter):
    def __init__(self, model_id, api_key=None, **kwargs):
        super().__init__(model_id)
        self.api_key = api_key
        self.endpoint = kwargs.get("endpoint", "https://api.example.com/model")
    
    async def generate(self, prompt, **kwargs):
        # Implement custom model inference
        pass
    
    async def chat(self, messages, **kwargs):
        # Implement custom chat completion
        pass
    
    async def embed(self, text, **kwargs):
        # Implement custom text embedding
        pass
```

Register the adapter:

```python
from tekton.core.models.manager import ModelManager

# Create a model manager
manager = ModelManager()

# Register the custom adapter
manager.register_adapter("custom", CustomModelAdapter)

# Add a model
manager.add_model(
    model_id="custom-model",
    provider="custom",
    capabilities=["text_generation", "chat"],
    tier=2,
    context_window=4000
)
```

### Custom Component Development

To develop a custom component:

1. Create a directory structure:
   ```
   my_component/
   ├── __init__.py
   ├── api/
   │   ├── __init__.py
   │   └── app.py
   ├── core/
   │   ├── __init__.py
   │   └── main.py
   ├── utils/
   │   ├── __init__.py
   │   └── hermes_helper.py
   └── register_with_hermes.py
   ```

2. Implement the API server (app.py):
   ```python
   from fastapi import FastAPI
   import uvicorn

   app = FastAPI()

   @app.get("/")
   async def root():
       return {"message": "My Custom Component API"}

   @app.get("/api/health")
   async def health():
       return {"status": "healthy"}

   if __name__ == "__main__":
       uvicorn.run("app:app", host="0.0.0.0", port=8500)
   ```

3. Implement Hermes registration (register_with_hermes.py):
   ```python
   import asyncio
   import aiohttp

   async def register_with_hermes(hermes_url="http://localhost:8001/api"):
       registration_data = {
           "component": "my_component",
           "description": "My Custom Component",
           "version": "1.0.0",
           "endpoints": [
               {
                   "path": "/api/custom",
                   "methods": ["GET", "POST"],
                   "description": "Custom endpoint"
               }
           ],
           "capabilities": ["custom_capability"],
           "host": "localhost",
           "port": 8500,
           "health_check": "/api/health"
       }
       
       async with aiohttp.ClientSession() as session:
           async with session.post(
               f"{hermes_url}/registry/components",
               json=registration_data
           ) as response:
               return await response.json()

   if __name__ == "__main__":
       asyncio.run(register_with_hermes())
   ```

4. Create a launch script (launch.sh):
   ```bash
   #!/bin/bash
   
   # Start the API server
   python -m my_component.api.app &
   
   # Wait for server to start
   sleep 2
   
   # Register with Hermes
   python -m my_component.register_with_hermes
   
   # Keep script running
   wait
   ```

### Custom UI Integration

To integrate a custom UI with Hephaestus:

1. Create a component template (my-component.html):
   ```html
   <template id="my-component-template">
     <div class="my-component">
       <h1>My Custom Component</h1>
       <div class="content">
         <!-- Component content -->
       </div>
     </div>

     <style>
       .my-component {
         padding: 20px;
         background-color: #f5f5f5;
       }
     </style>
   </template>
   ```

2. Create a component script (my-component.js):
   ```javascript
   class MyComponent extends HTMLElement {
     constructor() {
       super();
       this.attachShadow({ mode: 'open' });
       const template = document.getElementById('my-component-template');
       this.shadowRoot.appendChild(template.content.cloneNode(true));
     }

     connectedCallback() {
       // Initialize the component
       this.init();
     }

     async init() {
       // Set up component logic
     }
   }

   // Register the component
   customElements.define('my-component', MyComponent);
   ```

3. Register with Hephaestus:
   ```javascript
   // In your component script
   window.tektonComponents = window.tektonComponents || {};
   window.tektonComponents.myComponent = {
     name: "My Component",
     description: "A custom component for Tekton",
     icon: "custom-icon",
     path: "/my-component",
     element: "my-component",
     scripts: ["/components/my-component.js"],
     styles: ["/styles/my-component.css"]
   };
   ```

## Glossary

- **Component**: A modular part of the Tekton system with specific functionality
- **Capability**: A specific function or feature that a component provides
- **Dependency**: A component that another component requires to function
- **Heartbeat**: A periodic signal that indicates a component is functioning
- **LLM**: Large Language Model, such as Claude or GPT-4
- **Port**: A network endpoint used for communication between components
- **Registry**: A central database of registered components
- **Resource**: System resources like CPU, memory, or GPU
- **Service**: A running instance of a component
- **Task**: A unit of work to be performed by the system