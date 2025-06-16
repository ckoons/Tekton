# MCP Protocol Implementation Guide for Tekton Components

This guide provides standardized instructions for understanding and working with the Multimodal Cognitive Protocol (MCP) in Tekton components following the Single Port Architecture pattern.

## Overview

The Multimodal Cognitive Protocol (MCP) enables Tekton components to exchange rich, structured information across different modalities. During the Launch Testing Sprint, we identified that Hermes serves as the central hub for MCP services, providing access to other components' capabilities through its MCP endpoints. Additionally, Engram has its own dedicated MCP implementation. This architecture allows for centralized access while still enabling individual components to have specialized MCP capabilities when needed.

## What is MCP?

MCP is a protocol for exchanging semantic information across modalities:

- **Modalities**: Text, code, images, audio, structured data
- **Content Items**: Discrete units of information in a specific modality
- **Processing Instructions**: How the content should be processed
- **Security & Authentication**: Verification and authorization mechanisms

## Required Endpoints

Each component should implement the following MCP-related endpoints:

```
/api/mcp/capabilities     - Returns supported modalities and capabilities
/api/mcp/process          - Processes a multimodal request
/api/mcp/contexts/{id}    - Manages conversation/processing contexts
/api/mcp/tools            - Lists available tools (if applicable)
```

## MCP Architecture in Tekton

Tekton's MCP architecture follows a hub-and-spoke model:

1. **Hermes as the Central Hub**:
   - Acts as the centralized MCP gateway
   - Provides unified access to capabilities of all components
   - Routes MCP requests to appropriate components
   - Handles cross-component coordination

2. **Component-Specific MCP Implementation (Engram)**:
   - Engram has its own direct MCP implementation
   - Specialized for memory and knowledge management
   - Can be accessed directly or through Hermes

3. **Other Components**:
   - Access provided through Hermes MCP endpoints
   - No need for direct MCP endpoint implementation
   - Register capabilities with Hermes upon startup

## Accessing MCP Capabilities

### Hermes MCP Endpoints

```python
from fastapi import APIRouter

mcp_router = APIRouter(prefix="/api/mcp", tags=["mcp"])

@mcp_router.post("/capabilities")
async def get_mcp_capabilities():
    """Return the MCP capabilities of the entire Tekton system."""
    return {
        "version": "mcp/1.0",
        "modalities": ["text", "code", "image", "structured"],  # All supported modalities
        "supported_formats": {
            "text": ["text/plain", "text/markdown"],
            "code": ["text/x-python", "text/javascript"],
            "image": ["image/png", "image/jpeg"],
            "structured": ["application/json", "application/x-yaml"]
        },
        "processing_capabilities": ["text_analysis", "code_analysis", 
                                   "image_analysis", "context_management"]
    }
```

2. **Process Endpoint Implementation**

```python
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ContentItem(BaseModel):
    type: str
    format: str
    data: Any
    metadata: Optional[Dict[str, Any]] = None

class MCPRequest(BaseModel):
    content: List[ContentItem]
    context_id: Optional[str] = None
    processing: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None

@mcp_router.post("/process")
async def process_mcp_request(request: MCPRequest):
    """Process a multimodal request."""
    # Handle different modalities
    results = []
    for item in request.content:
        if item.type == "text":
            # Process text
            pass
        elif item.type == "code":
            # Process code
            pass
        # Add more modality handlers
    
    return {
        "status": "success",
        "results": results
    }
```

3. **Context Management**

```python
@mcp_router.post("/contexts")
async def create_context():
    """Create a new processing context."""
    context_id = str(uuid.uuid4())
    # Initialize context storage
    return {"context_id": context_id}

@mcp_router.get("/contexts/{context_id}")
async def get_context(context_id: str):
    """Get a specific context."""
    # Retrieve context
    return {"context_id": context_id, "items": []}

@mcp_router.delete("/contexts/{context_id}")
async def delete_context(context_id: str):
    """Delete a context."""
    # Delete context
    return {"status": "success"}
```

4. **Mount in Main App**

```python
from fastapi import FastAPI
from .routers import mcp_router

app = FastAPI()

# Mount MCP router
app.include_router(mcp_router)
```

## Implementation Details

### 1. Hermes as Central MCP Hub

Hermes acts as the centralized MCP gateway for all Tekton components:

- **Capability Aggregation**: Collects and exposes capabilities from all registered components
- **Request Routing**: Routes MCP requests to appropriate component based on capability
- **Response Aggregation**: Combines responses from multiple components when needed
- **Cross-Component Coordination**: Manages communication between components

```python
@mcp_router.post("/process")
async def process_mcp_request(request: MCPRequest):
    """Process a multimodal request by routing to appropriate components."""
    # Determine which component(s) can handle this request
    target_components = []
    
    for item in request.content:
        if item.type == "text" and "text_analysis" in item.metadata.get("processing", []):
            target_components.append("rhetor")  # Text processing → Rhetor
        elif item.type == "code":
            target_components.append("codex")   # Code processing → Codex
        elif item.type == "image":
            target_components.append("athena")  # Image processing → Athena
    
    # Route to appropriate components and aggregate responses
    results = []
    for component in target_components:
        component_response = await forward_to_component(component, item)
        results.extend(component_response)
    
    return {
        "status": "success",
        "results": results
    }
```

### 2. Component Registration for MCP

When components start up, they register their MCP capabilities with Hermes:

```python
async def register_mcp_capabilities():
    """Register component MCP capabilities with Hermes."""
    capabilities = {
        "component_id": "rhetor",
        "capabilities": {
            "modalities": ["text"],
            "formats": ["text/plain", "text/markdown"],
            "processing": ["text_analysis", "text_generation"]
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8001/api/registry/capabilities",
            json=capabilities
        ) as response:
            return await response.json()
```

## Testing MCP Endpoints

Use the following curl commands to test MCP implementation:

```bash
# Test capabilities
curl -X POST http://localhost:{PORT}/api/mcp/capabilities \
  -H "Content-Type: application/json" \
  -d '{}'

# Test processing
curl -X POST http://localhost:{PORT}/api/mcp/process \
  -H "Content-Type: application/json" \
  -d '{
    "content": [
      {
        "type": "text",
        "format": "text/plain",
        "data": "Hello world"
      }
    ]
  }'
```

## Standardized Response Format

All MCP endpoints should follow a consistent response format:

1. **Capabilities Response**: Include version, modalities, supported formats
2. **Process Response**: Return status and array of result items
3. **Error Response**: Use HTTP status codes with descriptive error messages

## Integration with Component Health Checks

Update component health checks to report MCP protocol availability:

```python
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    
    # Check component health and add MCP status
    return {
        "status": "healthy",
        "version": "1.0.0",
        "capabilities": {
            "mcp": True  # Indicate MCP support
        }
    }
```

## Next Steps

1. Document the current hub-and-spoke MCP architecture in detail
2. Create client libraries for accessing Hermes MCP endpoints
3. Add automated tests for verifying MCP functionality
4. Develop monitoring tools for MCP request routing and performance
5. Document component-specific capabilities available through the MCP hub

By leveraging the centralized MCP architecture with Hermes as the hub, we can maintain a streamlined and efficient approach to multimodal communication throughout the Tekton system while allowing specialized components like Engram to have their own MCP implementations when needed.