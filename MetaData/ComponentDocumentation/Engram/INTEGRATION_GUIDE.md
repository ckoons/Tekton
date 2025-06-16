# Engram Integration Guide

## Overview

Engram is designed to serve as the persistent memory system for all Tekton components. This guide explains how to integrate Engram with your applications and other Tekton components to leverage its memory capabilities.

## Integration Architecture

Engram provides multiple integration points:

1. **REST API**: Primary interface for direct memory operations
2. **WebSocket API**: For real-time updates and memory subscriptions
3. **Hermes Registration**: For service discovery and messaging
4. **Client Library**: For programmatic access from Python applications
5. **Single Port Architecture**: Unified endpoint access through standardized paths

## Client Library Usage

The Engram client library provides the easiest way to integrate with Engram from Python applications:

### Installation

```bash
pip install engram-client  # or install from the Tekton repository
```

### Basic Usage

```python
from engram.client import EngramClient

# Initialize client
client = EngramClient(host="localhost", port=8002)

# Store a memory
memory = {
    "content": "Paris is the capital of France.",
    "metadata": {
        "source": "user_input",
        "tags": ["geography", "europe"]
    },
    "compartment": "semantic",
    "type": "semantic"
}

created_memory = client.store_memory(memory)
print(f"Created memory with ID: {created_memory['id']}")

# Search for related memories
search_results = client.search_memories(
    query="What is the capital of France?",
    limit=5
)

for result in search_results['results']:
    print(f"Found: {result['content']} (similarity: {result['similarity']})")
```

### Advanced Client Usage

```python
# Create a memory compartment
new_compartment = {
    "id": "project_data",
    "description": "Project-specific knowledge and facts",
    "policy": {
        "type": "custom",
        "retention": "60d",
        "importance_threshold": 0.3
    }
}

client.create_compartment(new_compartment)

# Store batch memories
batch_memories = [
    {
        "content": "Memory item 1",
        "compartment": "project_data",
        "type": "semantic"
    },
    {
        "content": "Memory item 2",
        "compartment": "project_data",
        "type": "semantic"
    }
]

client.store_batch_memories(batch_memories)

# Update context
client.update_context({
    "active_compartments": ["working", "project_data", "core"],
    "focus": "project_data"
})

# Generate embeddings
embeddings = client.generate_embeddings(["Text 1", "Text 2"])
```

## Hermes Integration

### Registration Process

Engram registers itself with Hermes to enable discovery by other components:

```python
from hermes.api.client import HermesClient

def register_with_hermes(host="localhost", port=8000, api_key="your_api_key"):
    client = HermesClient(host=host, port=port, api_key=api_key)
    
    # Register Engram service
    registration_data = {
        "component": "engram",
        "description": "Memory management system for persistent context",
        "version": "1.0.0",
        "endpoints": [
            {
                "path": "/api/engram/memory",
                "methods": ["GET", "POST", "DELETE"],
                "description": "Memory management endpoints"
            },
            {
                "path": "/api/engram/search",
                "methods": ["POST"],
                "description": "Memory search endpoint"
            },
            # Additional endpoints...
        ],
        "capabilities": [
            "memory_storage",
            "memory_retrieval",
            "context_management",
            "embedding_generation"
        ],
        "host": "localhost",
        "port": 8002,
        "health_check": "/api/engram/health",
        "dependencies": []
    }
    
    response = client.register_component(registration_data)
    return response
```

### Discovery via Hermes

Other components can discover and communicate with Engram through Hermes:

```python
from hermes.api.client import HermesClient

def discover_engram():
    client = HermesClient(host="localhost", port=8000, api_key="your_api_key")
    
    # Find Engram component
    engram = client.discover_component("engram")
    
    return engram
```

## Direct API Integration

If you prefer to integrate directly with the Engram API without using the client library:

### Storing Memories

```python
import requests
import json

def store_memory(content, metadata=None, compartment="working", memory_type="episodic"):
    url = "http://localhost:8002/api/engram/memory"
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "your_api_key"
    }
    
    data = {
        "content": content,
        "metadata": metadata or {},
        "compartment": compartment,
        "type": memory_type
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()
```

### Searching Memories

```python
def search_memories(query, filter_criteria=None, limit=10):
    url = "http://localhost:8002/api/engram/search"
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "your_api_key"
    }
    
    data = {
        "query": query,
        "filter": filter_criteria or {},
        "limit": limit
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()
```

## WebSocket Integration

For real-time updates and continuous memory operations:

```python
import websocket
import json
import threading
import time

class EngramWebSocketClient:
    def __init__(self, host="localhost", port=8002, api_key="your_api_key"):
        self.url = f"ws://{host}:{port}/ws/engram?api_key={api_key}"
        self.ws = None
        self.connected = False
        self.callbacks = {}
        self.subscriptions = {}
        
    def connect(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.daemon = True
        self.thread.start()
        
        # Wait for connection
        timeout = 5
        start_time = time.time()
        while not self.connected and time.time() - start_time < timeout:
            time.sleep(0.1)
            
        return self.connected
    
    def _on_open(self, ws):
        self.connected = True
        print("Connected to Engram WebSocket")
    
    def _on_message(self, ws, message):
        data = json.loads(message)
        msg_type = data.get("type")
        msg_id = data.get("id")
        
        # Handle subscription messages
        if msg_type == "memory_updated" and "subscription_id" in data.get("data", {}):
            sub_id = data["data"]["subscription_id"]
            if sub_id in self.subscriptions and self.subscriptions[sub_id]:
                self.subscriptions[sub_id](data["data"])
        # Handle response callbacks
        elif msg_id in self.callbacks:
            self.callbacks[msg_id](data)
            
            # Clean up one-time callbacks
            if msg_type.endswith("_complete"):
                del self.callbacks[msg_id]
    
    def _on_error(self, ws, error):
        print(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        print("Disconnected from Engram WebSocket")
    
    def send_request(self, req_type, data, callback=None):
        if not self.connected:
            raise ConnectionError("Not connected to WebSocket")
        
        req_id = f"req-{time.time()}"
        request = {
            "type": req_type,
            "id": req_id,
            "data": data
        }
        
        if callback:
            self.callbacks[req_id] = callback
            
        self.ws.send(json.dumps(request))
        return req_id
    
    def subscribe_to_memories(self, compartments=None, types=None, callback=None):
        def handle_subscription_confirmed(data):
            sub_id = data["data"]["subscription_id"]
            if callback:
                self.subscriptions[sub_id] = callback
        
        return self.send_request(
            "subscribe",
            {
                "compartments": compartments or ["working"],
                "types": types or ["episodic", "semantic"]
            },
            handle_subscription_confirmed
        )
    
    def search_stream(self, query, filter_criteria=None, result_callback=None, complete_callback=None):
        results = []
        
        def handle_search_message(data):
            msg_type = data.get("type")
            
            if msg_type == "search_result":
                if result_callback:
                    result_callback(data["data"])
                results.append(data["data"]["memory"])
            elif msg_type == "search_complete" and complete_callback:
                complete_callback(results, data["data"])
        
        return self.send_request(
            "search",
            {
                "query": query,
                "filter": filter_criteria or {}
            },
            handle_search_message
        )
    
    def close(self):
        if self.ws:
            self.ws.close()
```

### Example Usage of WebSocket Client

```python
# Initialize and connect
client = EngramWebSocketClient(api_key="your_api_key")
client.connect()

# Subscribe to memory updates
def on_memory_update(data):
    memory = data["memory"]
    print(f"Memory update: {data['operation']} - {memory['id']}")
    print(f"Content: {memory['content']}")

client.subscribe_to_memories(
    compartments=["working", "project_data"],
    callback=on_memory_update
)

# Search with streaming results
def on_search_result(result):
    print(f"Found memory: {result['memory']['content']}")
    print(f"Similarity: {result['similarity']}")

def on_search_complete(results, metadata):
    print(f"Search complete. Found {len(results)} results")
    print(f"Total matches: {metadata['total_results']}")

client.search_stream(
    "What technologies are used in the project?",
    filter_criteria={"compartment": ["project_data"]},
    result_callback=on_search_result,
    complete_callback=on_search_complete
)

# Keep the main thread running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.close()
```

## Integration with Other Tekton Components

### Athena Integration

Integrate Engram with Athena for knowledge graph persistence:

```python
from athena.client import AthenaClient
from engram.client import EngramClient

def sync_knowledge_to_memory():
    athena_client = AthenaClient(host="localhost", port=8001)
    engram_client = EngramClient(host="localhost", port=8002)
    
    # Fetch entities from Athena
    entities = athena_client.list_entities({
        "type": "concept",
        "limit": 100
    })
    
    # Store in Engram as semantic memories
    for entity in entities["items"]:
        memory_item = {
            "content": entity["name"],
            "metadata": {
                "entity_id": entity["id"],
                "entity_type": entity["type"],
                "properties": entity["properties"],
                "source": "athena"
            },
            "compartment": "semantic",
            "type": "semantic",
            "importance": 0.8
        }
        
        engram_client.store_memory(memory_item)
```

### Rhetor Integration

Integrate with Rhetor for LLM-enhanced memory operations:

```python
from rhetor.client import RhetorClient
from engram.client import EngramClient

class EnhancedMemoryProcessor:
    def __init__(self):
        self.rhetor = RhetorClient(host="localhost", port=8005)
        self.engram = EngramClient(host="localhost", port=8002)
    
    async def enhance_memory(self, content):
        # Use Rhetor to generate metadata and categorization
        prompt = f"""Analyze the following content and provide:
        1. Key topics (up to 5 tags)
        2. Importance score (0.0 to 1.0)
        3. Suggested memory compartment (core, semantic, episodic, or working)
        4. Brief summary (1-2 sentences)
        
        Content: {content}
        """
        
        response = await self.rhetor.generate(prompt, temperature=0.3)
        
        # Parse the response to extract metadata
        # ... parsing code ...
        
        # Store enhanced memory
        memory = {
            "content": content,
            "metadata": {
                "tags": parsed_tags,
                "summary": parsed_summary,
                "source": "enhanced"
            },
            "compartment": parsed_compartment,
            "type": parsed_memory_type,
            "importance": parsed_importance
        }
        
        return self.engram.store_memory(memory)
```

### Terma Integration

Integrate with Terma for terminal session memory:

```python
from engram.client import EngramClient

class TermaSessionMemory:
    def __init__(self, session_id):
        self.client = EngramClient(host="localhost", port=8002)
        self.session_id = session_id
        
        # Create a session-specific context
        self.client.update_context({
            "active_compartments": ["working", "core"],
            "focus": "working",
            "metadata": {
                "session_id": session_id,
                "application": "terma"
            }
        })
    
    def store_command(self, command, output, working_directory):
        memory = {
            "content": f"Command: {command}\nOutput: {output}",
            "metadata": {
                "session_id": self.session_id,
                "command": command,
                "working_directory": working_directory,
                "timestamp": datetime.utcnow().isoformat()
            },
            "compartment": "working",
            "type": "episodic"
        }
        
        return self.client.store_memory(memory)
    
    def get_relevant_history(self, current_command, limit=5):
        search_results = self.client.search_memories(
            query=current_command,
            filter_criteria={
                "compartment": ["working"],
                "metadata": {
                    "session_id": self.session_id
                }
            },
            limit=limit
        )
        
        return search_results["results"]
```

## Single Port Architecture Integration

Engram implements the Single Port Architecture pattern for standardized access:

### URL Construction

```
http://localhost:8002/api/engram/[endpoint]  # HTTP API
ws://localhost:8002/ws/engram  # WebSocket API
```

### Environment Variable Configuration

In your component, use environment variables for Engram connection:

```python
import os
from engram.client import EngramClient

def get_engram_client():
    host = os.environ.get("ENGRAM_HOST", "localhost")
    port = int(os.environ.get("ENGRAM_PORT", 8002))
    api_key = os.environ.get("ENGRAM_API_KEY")
    
    return EngramClient(host=host, port=port, api_key=api_key)
```

## Authentication and Security

Implement secure integration with API keys and optional JWT authentication:

```python
# Using API Key authentication
client = EngramClient(
    host="localhost",
    port=8002,
    auth_type="api_key",
    api_key="your_api_key_here"
)

# Using JWT authentication
client = EngramClient(
    host="localhost",
    port=8002,
    auth_type="jwt",
    token="your_jwt_token_here"
)
```

## Best Practices

1. **Compartmentalization**: Use appropriate memory compartments for different types of information
2. **Memory Lifecycle**: Implement proper lifecycle management for temporary vs. persistent memories
3. **Batch Operations**: Use batch endpoints for creating or retrieving multiple memories
4. **Contextual Searching**: Include relevant context when searching to improve results
5. **Error Handling**: Implement robust error handling for API communication failures
6. **Caching**: Consider local caching for frequently accessed memories
7. **Memory Hygiene**: Periodically clean up or archive outdated memories
8. **Structured Metadata**: Use consistent metadata schemas for better organization

## Troubleshooting

### Common Integration Issues

1. **Connection Refused**: Ensure Engram is running and accessible from your client
2. **Authentication Errors**: Verify API keys or JWT tokens are correct
3. **Search Quality Issues**: Check embedding configuration and query formulation
4. **Performance Problems**: Consider batch operations and connection pooling

### Debugging Tips

- Enable debug logging in the client library:
  ```python
  client = EngramClient(host="localhost", port=8002, debug=True)
  ```
- Use the `/api/engram/debug` endpoint for system status information
- Check Engram server logs for error messages
- Try direct API calls using tools like curl or Postman to isolate issues

## Additional Resources

- [Engram API Reference](./API_REFERENCE.md)
- [Technical Documentation](./TECHNICAL_DOCUMENTATION.md)
- [Client Library Repository](https://github.com/yourusername/engram-client)