# Engram Quick Start Guide

## Installation

Engram is part of the Tekton ecosystem but can be installed and used independently:

```bash
# Clone the repository
git clone https://github.com/yourusername/Tekton.git
cd Tekton/Engram

# Install dependencies
pip install -r requirements.txt

# Install Engram in development mode
pip install -e .
```

## Basic Usage

### Starting the Engram Server

```bash
# Start with default settings (file-based storage)
python -m engram.api.server

# Start with vector database (if available)
python -m engram.api.server --data-dir ~/engram_data

# Start with Hermes integration
ENGRAM_MODE=hermes python -m engram.api.server
```

The server will start on `http://127.0.0.1:8000` by default.

### Command-Line Memory Operations

Engram includes a CLI for quick memory operations:

```bash
# Store a memory
python -m engram.cli.quickmem store --key "project_notes" --value "This is a note about the project"

# Retrieve a memory
python -m engram.cli.quickmem retrieve --key "project_notes"

# List all keys
python -m engram.cli.quickmem list
```

### Using the Python API

```python
import asyncio
from engram.core.memory import MemoryService

async def memory_example():
    # Initialize memory service
    memory = MemoryService(client_id="example")
    
    # Add a memory
    await memory.add(
        content="This is an important fact to remember",
        namespace="longterm",
        metadata={"source": "user", "importance": "high"}
    )
    
    # Search for relevant memories
    results = await memory.search(
        query="important fact",
        namespace="longterm",
        limit=5
    )
    
    # Print results
    for result in results.get("results", []):
        print(f"Memory: {result['content']}")
        print(f"Relevance: {result['relevance']}")
        print("---")
    
    # Get context from multiple namespaces
    context = await memory.get_relevant_context(
        query="What should I remember?",
        namespaces=["longterm", "conversations"]
    )
    print(f"Context:\n{context}")

# Run the example
asyncio.run(memory_example())
```

### Using the REST API

```bash
# Add a memory
curl -X POST "http://localhost:8000/memory" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is a test memory", "namespace": "conversations"}'

# Search memories
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "test memory", "namespace": "conversations", "limit": 5}'

# Get context
curl -X POST "http://localhost:8000/context" \
  -H "Content-Type: application/json" \
  -d '{"query": "What was our conversation about?", "namespaces": ["conversations", "thinking"]}'
```

## Using Compartments

Memory compartments provide organized storage for different contexts:

```python
import asyncio
from engram.core.memory import MemoryService

async def compartment_example():
    # Initialize memory service
    memory = MemoryService(client_id="example")
    
    # Create a compartment
    compartment_id = await memory.create_compartment(
        name="Project X",
        description="All memories related to Project X"
    )
    print(f"Created compartment with ID: {compartment_id}")
    
    # Activate the compartment
    await memory.activate_compartment(compartment_id)
    
    # Add memory to the compartment
    await memory.add(
        content="Project X design notes: The system should use a modular architecture",
        namespace=f"compartment-{compartment_id}",
        metadata={"type": "design"}
    )
    
    # Search within the compartment
    results = await memory.search(
        query="modular architecture",
        namespace=f"compartment-{compartment_id}"
    )
    
    # Print results
    for result in results.get("results", []):
        print(f"Memory: {result['content']}")
    
    # Deactivate when done
    await memory.deactivate_compartment(compartment_id)

# Run the example
asyncio.run(compartment_example())
```

## Using Latent Space for Iterative Reasoning

Latent space enables iterative thought refinement:

```python
import asyncio
from engram.core.latent_space import LatentMemorySpace, ConvergenceDetector

async def latent_space_example():
    # Initialize latent memory space
    latent_space = LatentMemorySpace(component_id="example", namespace="problem_solving")
    
    # Initialize a thought
    thought_id = await latent_space.initialize_thought(
        thought_seed="Initial thoughts on solving the performance issue: The system might be slow due to database queries."
    )
    print(f"Created thought with ID: {thought_id}")
    
    # Refine the thought through iterations
    for i in range(3):
        # Simulate refinement process
        refinement = f"Iteration {i+1}: After analysis, the issue appears to be related to " + \
                    f"{'database indexing' if i == 0 else 'connection pooling' if i == 1 else 'inefficient query patterns'}."
        
        # Update the thought
        thought_data = await latent_space.refine_thought(
            thought_id=thought_id,
            refinement=refinement
        )
        
        # Check for convergence
        if i >= 1:
            iterations = thought_data["iterations"]
            converged = await ConvergenceDetector.detect_convergence(iterations)
            
            if converged:
                print("Thought has converged, finalizing...")
                break
    
    # Finalize the thought
    final_thought = await latent_space.finalize_thought(
        thought_id=thought_id,
        final_content="Final analysis: The performance issue is caused by inefficient query patterns. " + 
                      "Recommend implementing query optimization and adding appropriate indexes.",
        persist=True
    )
    
    # Get the reasoning trace
    trace = await latent_space.get_reasoning_trace(
        thought_id=thought_id,
        include_iterations=True
    )
    
    print("Reasoning trace:")
    for iteration in trace["iterations"]:
        print(f"Iteration {iteration['iteration']}: {iteration['content']}")

# Run the example
asyncio.run(latent_space_example())
```

## Integrating with Hermes

For Tekton ecosystem integration, connect Engram with Hermes:

```python
import asyncio
from engram.integrations.hermes.memory_adapter import HermesMemoryService

async def hermes_integration_example():
    # Initialize Hermes memory service
    memory = HermesMemoryService(client_id="example")
    
    # The API is the same as standard MemoryService
    await memory.add(
        content="This memory is stored through Hermes",
        namespace="conversations"
    )
    
    # Search using Hermes's vector capabilities
    results = await memory.search(
        query="stored through Hermes",
        namespace="conversations"
    )
    
    # Clean up connections when done
    await memory.close()

# Run the example
asyncio.run(hermes_integration_example())
```

## Configuration

Engram can be configured through environment variables:

```bash
# Set data directory
export ENGRAM_DATA_DIR=~/engram_data

# Use fallback mode (file-based storage)
export ENGRAM_USE_FALLBACK=1

# Enable debug logging
export ENGRAM_DEBUG=1

# Set client ID
export ENGRAM_CLIENT_ID=my_application

# Use Hermes integration
export ENGRAM_MODE=hermes

# Set port
export ENGRAM_PORT=8001
```

## Next Steps

- Explore the [Technical Documentation](./engram_technical_documentation.md) for detailed architecture
- Check the [Architecture Diagrams](./engram_architecture.md) for visual representation
- Set up a vector database for improved semantic search capabilities
- Integrate with other Tekton components through Hermes