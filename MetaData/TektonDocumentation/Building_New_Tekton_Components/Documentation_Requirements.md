# Documentation Requirements

This guide outlines the documentation required for each new Tekton component. Complete documentation ensures proper integration, maintenance, and usage of your component within the Tekton ecosystem.

## Required Documentation Files

### 1. README.md (Component Root)

**Location**: `/ComponentName/README.md`

**Required Sections**:
- **Overview** - Brief description of what the component does
- **Installation** - How to set up the component
- **Usage** - Basic usage examples
- **Configuration** - Environment variables and settings
- **API Documentation** - Link to API docs
- **MCP Tools** - List of available MCP tools
- **Dependencies** - External requirements

**Template**:
```markdown
# ComponentName

Brief description of the component's purpose and role in Tekton.

## Overview

Detailed description of functionality and key features.

## Installation

```bash
./setup.sh
```

## Usage

### Starting the Server
```bash
./run_componentname.sh
```

### CLI Usage
```bash
componentname status
componentname [command] [options]
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| COMPONENTNAME_PORT | API server port | 80XX |
| COMPONENTNAME_LOG_LEVEL | Logging level | INFO |

## API Documentation

Once running, visit http://localhost:80XX/docs for interactive API documentation.

## MCP Tools

- `tool_name` - Tool description
- `another_tool` - Another description

## Dependencies

- Python 3.8+
- FastAPI
- [Other dependencies]
```

### 2. Component Documentation (MetaData)

**Location**: `/MetaData/ComponentDocumentation/ComponentName/`

Create the following files:

#### INDEX.md
Entry point for component documentation:
```markdown
# ComponentName Documentation

## Overview
[Component purpose and role]

## Documentation
- [API Reference](./API_REFERENCE.md)
- [Technical Documentation](./TECHNICAL_DOCUMENTATION.md)
- [User Guide](./USER_GUIDE.md)
- [Integration Guide](./INTEGRATION_GUIDE.md)

## Quick Links
- [Component README](/ComponentName/README.md)
- [MCP Integration](/ComponentName/MCP_INTEGRATION.md)
```

#### API_REFERENCE.md
Complete API documentation:
```markdown
# ComponentName API Reference

## Base URL
`http://localhost:80XX`

## Endpoints

### Health Check
`GET /health`

Returns component health status.

**Response:**
```json
{
  "status": "healthy",
  "component": "componentname",
  "version": "0.1.0",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### MCP Tools
`POST /mcp/v2/tools/list`

Lists available MCP tools.

[Continue with all endpoints...]
```

#### TECHNICAL_DOCUMENTATION.md
Architecture and implementation details:
```markdown
# ComponentName Technical Documentation

## Architecture

### Overview
[High-level architecture description]

### Components
- **API Layer** - FastAPI server handling HTTP/WebSocket
- **Core Logic** - Business logic implementation
- **MCP Integration** - Tool definitions and handlers
- **CLI** - Command-line interface

### Data Flow
[Describe how data flows through the component]

### Dependencies
[List and explain key dependencies]

## Implementation Details

### Key Classes
- `ServiceClass` - Main service implementation
- `ModelClass` - Data models

### Algorithms
[Describe any important algorithms]

### Performance Considerations
[Performance notes and optimizations]
```

#### USER_GUIDE.md
End-user documentation:
```markdown
# ComponentName User Guide

## Getting Started

### Prerequisites
- Tekton environment set up
- Python 3.8+

### Installation
1. Navigate to component directory
2. Run `./setup.sh`
3. Configure environment variables

## Using the CLI

### Basic Commands
```bash
# Check status
componentname status

# Process data
componentname process [options]
```

### Advanced Usage
[Examples of complex operations]

## Using the UI

### Accessing the Interface
1. Start Hephaestus UI
2. Navigate to ComponentName tab
3. [UI usage instructions]

### Features
- Feature 1 description
- Feature 2 description

## Troubleshooting

### Common Issues
- **Issue**: Component won't start
  **Solution**: Check port availability

[More troubleshooting items...]
```

#### INTEGRATION_GUIDE.md
How to integrate with other components:
```markdown
# ComponentName Integration Guide

## Overview
How ComponentName integrates with other Tekton components.

## Hermes Integration

### Registration
ComponentName automatically registers with Hermes on startup.

### Discovery
Other components can discover ComponentName through Hermes.

## MCP Integration

### Available Tools
- `tool_name` - Description and usage

### Tool Examples
```python
# Calling ComponentName tools
response = await mcp_client.call_tool(
    "tool_name",
    {"param": "value"}
)
```

## Component Dependencies

### Required Components
- Hermes (port 8001) - Service registry

### Optional Integrations
- Engram - For memory storage
- [Other components]

## API Integration

### REST API
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:80XX/api/endpoint")
```

### WebSocket
```javascript
const ws = new WebSocket('ws://localhost:80XX/ws');
ws.onmessage = (event) => {
    // Handle messages
};
```
```

### 3. MCP_INTEGRATION.md

**Location**: `/ComponentName/MCP_INTEGRATION.md`

Document MCP-specific integration:
```markdown
# MCP Integration

ComponentName implements MCP v2 protocol for tool-based interactions.

## Available Tools

### tool_name
**Description**: What this tool does

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "param1": {
      "type": "string",
      "description": "Parameter description"
    }
  },
  "required": ["param1"]
}
```

**Example Usage**:
```bash
curl -X POST http://localhost:80XX/mcp/v2/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tool_name",
    "arguments": {"param1": "value"}
  }'
```

**Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Tool execution result"
    }
  ],
  "isError": false
}
```

## Integration Examples

### Python
```python
from fastmcp import FastMCP

mcp = FastMCP("componentname")
result = await mcp.call_tool("tool_name", {"param1": "value"})
```

### JavaScript
```javascript
const response = await fetch('http://localhost:80XX/mcp/v2/tools/call', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'tool_name',
    arguments: {param1: 'value'}
  })
});
```
```

## Documentation Standards

### Code Documentation

#### Python Docstrings
```python
def process_data(input_data: Dict[str, Any]) -> ProcessResult:
    """
    Process input data according to component logic.
    
    Args:
        input_data: Dictionary containing input parameters
            - key1: Description of key1
            - key2: Description of key2
    
    Returns:
        ProcessResult: Object containing processed results
        
    Raises:
        ValidationError: If input data is invalid
        ProcessingError: If processing fails
    
    Example:
        >>> result = process_data({"key1": "value1"})
        >>> print(result.status)
        'success'
    """
```

#### JavaScript Comments
```javascript
/**
 * Initialize component UI
 * @param {Object} config - Configuration object
 * @param {string} config.apiUrl - API endpoint URL
 * @param {string} config.wsUrl - WebSocket URL
 * @returns {void}
 */
function initializeUI(config) {
    // Implementation
}
```

### API Documentation

Use FastAPI's automatic documentation generation:
```python
@router.post(
    "/process",
    summary="Process input data",
    description="Processes input data according to component logic",
    response_model=ProcessResult,
    responses={
        200: {"description": "Successful processing"},
        400: {"description": "Invalid input"},
        500: {"description": "Processing error"}
    }
)
async def process_endpoint(
    data: ProcessInput = Body(..., description="Input data to process")
) -> ProcessResult:
    """Process endpoint implementation."""
```

## Documentation Maintenance

### Sprint Updates

After each sprint:
1. Update API documentation if endpoints changed
2. Update user guide with new features
3. Update integration guide with new patterns
4. Update technical documentation with architectural changes

### Version Documentation

When releasing new versions:
1. Tag documentation with version number
2. Maintain compatibility notes
3. Document breaking changes
4. Provide migration guides

### Review Checklist

Before completing documentation:
- [ ] All code has docstrings/comments
- [ ] README is complete and accurate
- [ ] API reference covers all endpoints
- [ ] User guide includes all features
- [ ] Integration examples are tested
- [ ] MCP tools are documented
- [ ] Environment variables are listed
- [ ] Troubleshooting section is helpful

## Documentation Tools

### Generating API Docs
```bash
# Generate OpenAPI schema
python -c "from mycomponent.api.app import app; import json; print(json.dumps(app.openapi()))" > openapi.json
```

### Testing Documentation Examples
```bash
# Test all code examples in markdown files
python -m doctest -v docs/*.md
```

### Documentation Linting
```bash
# Check markdown formatting
markdownlint MetaData/ComponentDocumentation/ComponentName/*.md
```

## Best Practices

1. **Keep It Current** - Update docs with code changes
2. **Show, Don't Tell** - Use examples liberally
3. **Be Concise** - Clear and direct language
4. **Think Like a User** - Document from user perspective
5. **Test Your Docs** - Ensure examples actually work
6. **Version Everything** - Track documentation changes
7. **Cross-Reference** - Link between related docs

---

*Remember: Good documentation is as important as good code. It's how others (including future you) understand and use your component.*