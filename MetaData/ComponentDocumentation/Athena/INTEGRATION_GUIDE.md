# Athena Integration Guide

## Overview

Athena is designed to integrate seamlessly with other Tekton components. This guide explains how to connect Athena to the Tekton ecosystem and leverage its knowledge graph capabilities in your applications.

## Integration Architecture

Athena provides multiple integration points:

1. **REST API**: Primary interface for direct integration
2. **WebSocket**: For real-time updates and streaming queries
3. **Hermes Registration**: For service discovery and messaging
4. **Client Libraries**: For programmatic access from Python applications
5. **UI Components**: For embedding visualizations in web interfaces

## Hermes Integration

### Registration Process

Athena registers itself with Hermes to enable discovery by other components:

```python
from hermes.api.client import HermesClient

def register_with_hermes(host="localhost", port=8000, api_key="your_api_key"):
    client = HermesClient(host=host, port=port, api_key=api_key)
    
    # Register Athena service
    registration_data = {
        "component": "athena",
        "description": "Knowledge graph system for entity relationships",
        "version": "1.0.0",
        "endpoints": [
            {
                "path": "/api/athena/entities",
                "methods": ["GET", "POST"],
                "description": "Entity management endpoints"
            },
            # Additional endpoints...
        ],
        "capabilities": [
            "knowledge_graph",
            "entity_management",
            "relationship_queries",
            "visualization"
        ],
        "host": "localhost",
        "port": 8001,
        "health_check": "/api/athena/health",
        "dependencies": ["engram"]
    }
    
    response = client.register_component(registration_data)
    return response
```

### Communication via Hermes

Other components can discover and communicate with Athena through Hermes:

```python
from hermes.api.client import HermesClient

def discover_athena():
    client = HermesClient(host="localhost", port=8000, api_key="your_api_key")
    
    # Find Athena component
    athena = client.discover_component("athena")
    
    return athena
```

## Engram Integration

Athena can store entity knowledge in Engram's memory system for persistence and retrieval:

### Memory Adapter

```python
from engram.api.client import EngramClient

class EngramMemoryAdapter:
    def __init__(self, host="localhost", port=8002):
        self.client = EngramClient(host=host, port=port)
    
    def store_entity(self, entity):
        # Convert entity to memory format
        memory_item = {
            "type": "entity",
            "content": entity.to_dict(),
            "metadata": {
                "entity_id": entity.id,
                "entity_type": entity.type
            }
        }
        
        # Store in Engram
        result = self.client.store_memory(memory_item)
        return result
    
    def retrieve_entity(self, entity_id):
        # Query Engram for the entity
        query = {
            "type": "entity",
            "metadata": {
                "entity_id": entity_id
            }
        }
        
        result = self.client.query_memory(query)
        if result and result.get("items"):
            return result["items"][0]["content"]
        return None
```

## Rhetor Integration

Athena can leverage Rhetor's LLM capabilities for entity extraction and relationship discovery:

```python
from rhetor.client import RhetorClient

class RhetorLLMAdapter:
    def __init__(self, host="localhost", port=8005):
        self.client = RhetorClient(host=host, port=port)
    
    async def extract_entities(self, text):
        prompt = f"""Extract entities from the following text. 
        Identify people, organizations, projects, locations, and other important entities.
        For each entity, provide its type, name, and any relevant properties.
        
        Text: {text}
        """
        
        response = await self.client.generate(prompt, temperature=0.2)
        # Process the response to extract structured entity data
        # ... parsing code ...
        
        return extracted_entities
    
    async def suggest_relationships(self, entity1, entity2):
        prompt = f"""Consider these two entities:
        Entity 1: {entity1.to_dict()}
        Entity 2: {entity2.to_dict()}
        
        What potential relationships might exist between them? 
        Suggest relationship types, directions, and confidence levels.
        """
        
        response = await self.client.generate(prompt, temperature=0.3)
        # Process the response to extract relationship suggestions
        # ... parsing code ...
        
        return suggested_relationships
```

## Hephaestus UI Integration

Integrate Athena's knowledge graph visualizations into the Hephaestus UI:

### Web Component

```javascript
// athena-graph-component.js
class AthenaGraphComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.render();
    this.setupEventListeners();
  }
  
  async render() {
    // Fetch component HTML template
    const response = await fetch('/ui/components/athena-graph.html');
    const template = await response.text();
    
    // Render the component
    this.shadowRoot.innerHTML = template;
    
    // Initialize the graph visualization
    this.initGraph();
  }
  
  async initGraph() {
    const graphContainer = this.shadowRoot.querySelector('#graph-container');
    const entityId = this.getAttribute('entity-id');
    const depth = this.getAttribute('depth') || 2;
    
    // Fetch graph data from Athena API
    const response = await fetch(`/api/athena/visualization/graph`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        root_entity: entityId,
        depth: parseInt(depth),
        layout: 'force-directed'
      })
    });
    
    const graphData = await response.json();
    
    // Render graph using D3.js or other visualization library
    // ... visualization code ...
  }
  
  setupEventListeners() {
    // Add event listeners for user interactions
  }
}

customElements.define('athena-graph', AthenaGraphComponent);
```

### HTML Usage

```html
<!-- In Hephaestus UI -->
<div class="component-container">
  <h2>Knowledge Graph Visualization</h2>
  <athena-graph entity-id="entity-123" depth="2"></athena-graph>
</div>
```

## Client Library Usage

Use the Athena client library for programmatic access from Python applications:

```python
from athena.client import AthenaClient

# Initialize client
client = AthenaClient(host="localhost", port=8001)

# Create an entity
new_entity = {
    "type": "person",
    "name": "John Doe",
    "properties": {
        "age": 30,
        "email": "john@example.com"
    }
}

created_entity = client.create_entity(new_entity)
print(f"Created entity with ID: {created_entity['id']}")

# Create a relationship
new_relationship = {
    "type": "works_at",
    "source_id": created_entity['id'],
    "target_id": "entity-company-456",
    "properties": {
        "role": "Software Engineer",
        "since": "2023-01-15"
    }
}

created_relationship = client.create_relationship(new_relationship)

# Execute a query
query = {
    "query_type": "pattern",
    "patterns": [
        {
            "entity": { "type": "person" },
            "relationship": { "type": "works_at" },
            "entity": { "type": "organization" }
        }
    ]
}

results = client.execute_query(query)
for entity in results["results"]:
    print(f"Entity: {entity['name']} ({entity['type']})")
```

## Telos Integration

Integrate with Telos for requirements tracing and project context:

```python
from telos.client import TelosClient
from athena.client import AthenaClient

def sync_requirements_to_knowledge_graph():
    telos_client = TelosClient(host="localhost", port=8006)
    athena_client = AthenaClient(host="localhost", port=8001)
    
    # Fetch requirements from Telos
    requirements = telos_client.get_all_requirements()
    
    for req in requirements:
        # Create or update requirement entity
        req_entity = {
            "type": "requirement",
            "name": req["title"],
            "properties": {
                "description": req["description"],
                "priority": req["priority"],
                "status": req["status"],
                "telos_id": req["id"]
            }
        }
        
        # Check if entity already exists
        existing = athena_client.find_entities({
            "type": "requirement",
            "property.telos_id": req["id"]
        })
        
        if existing and existing.get("items"):
            # Update existing entity
            entity_id = existing["items"][0]["id"]
            athena_client.update_entity(entity_id, req_entity)
        else:
            # Create new entity
            athena_client.create_entity(req_entity)
```

## Webhooks and Event Integration

Set up webhooks to notify other systems of changes in the knowledge graph:

```python
# In Athena's API layer
class WebhookManager:
    def __init__(self):
        self.webhooks = {}
    
    def register_webhook(self, event_type, url, secret=None):
        if event_type not in self.webhooks:
            self.webhooks[event_type] = []
        
        self.webhooks[event_type].append({
            "url": url,
            "secret": secret
        })
    
    async def trigger_event(self, event_type, data):
        if event_type not in self.webhooks:
            return
        
        for webhook in self.webhooks[event_type]:
            try:
                # Add signature if secret is provided
                headers = {"Content-Type": "application/json"}
                if webhook["secret"]:
                    signature = generate_signature(data, webhook["secret"])
                    headers["X-Athena-Signature"] = signature
                
                # Send webhook notification
                async with aiohttp.ClientSession() as session:
                    await session.post(
                        webhook["url"],
                        json={
                            "event_type": event_type,
                            "data": data,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        headers=headers
                    )
            except Exception as e:
                # Log webhook delivery failure
                print(f"Failed to deliver webhook: {str(e)}")
```

## Authentication and Security

Implement secure integration with API keys and JWT authentication:

```python
# In client code
from athena.client import AthenaClient

# Using API Key authentication
client = AthenaClient(
    host="localhost",
    port=8001,
    auth_type="api_key",
    api_key="your_api_key_here"
)

# Using JWT authentication
client = AthenaClient(
    host="localhost",
    port=8001,
    auth_type="jwt",
    token="your_jwt_token_here"
)
```

## Best Practices

1. **Error Handling**: Implement robust error handling for API communication failures
2. **Rate Limiting**: Respect rate limits when making frequent API calls
3. **Caching**: Cache frequently accessed entities and query results
4. **Bulk Operations**: Use batch endpoints for creating or updating multiple entities
5. **Versioning**: Pay attention to API version compatibility
6. **Authentication**: Securely manage API keys and tokens
7. **Event-Based Updates**: Use webhooks for real-time updates instead of polling

## Troubleshooting

### Common Integration Issues

1. **Connection Refused**: Ensure Athena is running and accessible from the client
2. **Authentication Errors**: Verify API keys or JWT tokens are correct
3. **Missing Data**: Check that entity IDs are correct and entities exist
4. **Performance Issues**: Consider query optimization and caching strategies

### Debugging Tools

- Use the `/api/athena/debug` endpoint for system status information
- Enable debug logging in the client library for detailed request/response logs
- Check Athena logs for error messages related to your integration

## Additional Resources

- [Athena API Reference](./API_REFERENCE.md)
- [Technical Documentation](./TECHNICAL_DOCUMENTATION.md)
- [Client Library Repository](https://github.com/yourusername/athena-client)