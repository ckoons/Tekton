# MCP Tool Registration Guide

## Overview

The Model Context Protocol (MCP) is a standardized way to register, discover, and execute tools across the Tekton ecosystem. This guide explains how to create, register, and use MCP tools in your components.

## What is MCP?

MCP (Model Context Protocol) provides:
- Standardized tool registration and discovery
- Unified execution interface across components
- Type-safe parameter validation
- Automatic documentation generation
- Integration with CI specialists and LLMs

## Tool Registration Methods

### Method 1: Using the @mcp_tool Decorator

The simplest way to register a tool is using the decorator:

```python
from ergon.core.repository.mcp import mcp_tool

@mcp_tool(
    name="analyze_code",
    description="Analyzes code for quality issues",
    schema={
        "name": "analyze_code",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Code to analyze"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language",
                    "enum": ["python", "javascript", "java"]
                },
                "checks": {
                    "type": "array",
                    "description": "Types of checks to perform",
                    "items": {
                        "type": "string",
                        "enum": ["syntax", "style", "security", "performance"]
                    }
                }
            },
            "required": ["code", "language"]
        }
    },
    tags=["code", "analysis", "quality"]
)
def analyze_code(code: str, language: str, checks: list = None) -> dict:
    """Analyze code for various quality issues."""
    if checks is None:
        checks = ["syntax", "style"]
    
    results = {
        "language": language,
        "checks_performed": checks,
        "issues": []
    }
    
    # Perform analysis...
    
    return results
```

### Method 2: Using register_tool Function

For more control or dynamic registration:

```python
from ergon.core.repository.mcp import register_tool

def my_dynamic_tool(input_data: dict) -> dict:
    """Process input data dynamically."""
    # Implementation
    return {"processed": input_data}

# Register at runtime
register_tool(
    name="dynamic_processor",
    description="Processes data based on runtime configuration",
    function=my_dynamic_tool,
    schema={
        "name": "dynamic_processor",
        "parameters": {
            "type": "object",
            "properties": {
                "input_data": {
                    "type": "object",
                    "description": "Data to process"
                }
            },
            "required": ["input_data"]
        }
    },
    tags=["dynamic", "processor"],
    metadata={
        "version": "1.0.0",
        "author": "your_name"
    }
)
```

### Method 3: Class-Based Tools

For complex tools with state:

```python
from ergon.core.repository.mcp import MCPTool

class DataTransformer(MCPTool):
    def __init__(self):
        super().__init__(
            name="data_transformer",
            description="Transform data between formats"
        )
        self.supported_formats = ["json", "yaml", "xml", "csv"]
    
    def get_schema(self):
        return {
            "name": self.name,
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "Data to transform"
                    },
                    "from_format": {
                        "type": "string",
                        "enum": self.supported_formats
                    },
                    "to_format": {
                        "type": "string",
                        "enum": self.supported_formats
                    }
                },
                "required": ["data", "from_format", "to_format"]
            }
        }
    
    def execute(self, data: str, from_format: str, to_format: str) -> dict:
        # Transform logic here
        return {"transformed": data, "format": to_format}

# Register the class-based tool
transformer = DataTransformer()
transformer.register()
```

## Schema Definition

### Basic Schema Structure

```python
schema = {
    "name": "tool_name",
    "description": "Brief description",
    "parameters": {
        "type": "object",
        "properties": {
            # Parameter definitions
        },
        "required": ["param1", "param2"],
        "additionalProperties": False
    }
}
```

### Parameter Types

#### String Parameters
```python
"username": {
    "type": "string",
    "description": "User's name",
    "minLength": 3,
    "maxLength": 50,
    "pattern": "^[a-zA-Z0-9_]+$"
}
```

#### Number Parameters
```python
"temperature": {
    "type": "number",
    "description": "Temperature setting",
    "minimum": 0.0,
    "maximum": 1.0,
    "default": 0.7
}
```

#### Array Parameters
```python
"tags": {
    "type": "array",
    "description": "List of tags",
    "items": {
        "type": "string"
    },
    "minItems": 1,
    "maxItems": 10
}
```

#### Object Parameters
```python
"config": {
    "type": "object",
    "description": "Configuration object",
    "properties": {
        "enabled": {"type": "boolean"},
        "threshold": {"type": "number"}
    },
    "required": ["enabled"]
}
```

#### Enum Parameters
```python
"priority": {
    "type": "string",
    "description": "Task priority",
    "enum": ["low", "medium", "high", "critical"],
    "default": "medium"
}
```

## Tool Discovery

### Listing Available Tools

```python
from ergon.core.repository.mcp import get_registered_tools, get_tool

# Get all registered tools
all_tools = get_registered_tools()
for name, tool_info in all_tools.items():
    print(f"Tool: {name}")
    print(f"  Description: {tool_info['description']}")
    print(f"  Version: {tool_info.get('version', 'N/A')}")
    print(f"  Tags: {', '.join(tool_info.get('tags', []))}")
```

### Finding Tools by Tag

```python
from ergon.core.repository.repository import RepositoryService

repo = RepositoryService()

# Search for code-related tools
code_tools = repo.search_components("code", limit=10)
for tool, relevance_score in code_tools:
    print(f"{tool.name}: {tool.description} (score: {relevance_score:.2f})")
```

### Getting Tool Details

```python
# Get specific tool information
tool = get_tool("analyze_code")
if tool:
    print(f"Tool: {tool['name']}")
    print(f"Schema: {tool['schema']}")
    print(f"Metadata: {tool.get('metadata', {})}")
```

## Tool Execution

### Direct Execution

```python
from ergon.core.repository.mcp import execute_tool

# Execute a registered tool
result = execute_tool(
    "analyze_code",
    code="def hello(): print('world')",
    language="python",
    checks=["syntax", "style"]
)

print(result)
```

### Async Execution

```python
from ergon.core.repository.mcp import execute_tool_async

async def run_analysis():
    result = await execute_tool_async(
        "analyze_code",
        code="const hello = () => console.log('world')",
        language="javascript"
    )
    return result

# Run async
import asyncio
result = asyncio.run(run_analysis())
```

### Batch Execution

```python
from ergon.core.repository.mcp import execute_batch

# Execute multiple tools
tasks = [
    {
        "tool": "analyze_code",
        "params": {"code": "...", "language": "python"}
    },
    {
        "tool": "format_code",
        "params": {"code": "...", "style": "black"}
    }
]

results = execute_batch(tasks)
for i, result in enumerate(results):
    print(f"Task {i}: {result}")
```

## Integration with Components

### Hermes Integration

Register tools that can be discovered via Hermes:

```python
from hermes.api.client import HermesClient

class ToolProvider:
    def __init__(self):
        self.hermes = HermesClient()
        self.register_with_hermes()
    
    def register_with_hermes(self):
        # Register component with tool capabilities
        self.hermes.register_component({
            "component": "my_component",
            "capabilities": ["mcp_tools"],
            "tools": get_registered_tools()
        })
```

### CI Specialist Integration

Make tools available to CI specialists:

```python
from shared.ai.simple_ai import ai_send_sync

# Register tool for CI use
@mcp_tool(
    name="weather_forecast",
    description="Get weather forecast for a location",
    ai_enabled=True  # Flag for CI availability
)
def get_weather(location: str, days: int = 7) -> dict:
    # Implementation
    return {"location": location, "forecast": "sunny"}

# CI can now use the tool
response = ai_send_sync(
    "sophia-ai",
    "What's the weather forecast for Paris?",
    tools=["weather_forecast"]
)
```

### Workflow Integration

Use tools in Harmonia workflows:

```python
workflow = {
    "name": "code_quality_pipeline",
    "tasks": [
        {
            "name": "analyze",
            "tool": "analyze_code",
            "input": {
                "code": "${input.source_code}",
                "language": "${input.language}",
                "checks": ["syntax", "security"]
            }
        },
        {
            "name": "format",
            "tool": "format_code",
            "input": {
                "code": "${input.source_code}",
                "style": "black"
            },
            "depends_on": ["analyze"]
        }
    ]
}
```

## Best Practices

### 1. Tool Naming

- Use descriptive, action-oriented names
- Use underscores for multi-word names
- Avoid generic names like "process" or "handle"

```python
# Good
@mcp_tool(name="validate_email_address")
@mcp_tool(name="compress_image")
@mcp_tool(name="parse_markdown")

# Bad
@mcp_tool(name="validate")  # Too generic
@mcp_tool(name="img")       # Too abbreviated
@mcp_tool(name="doWork")    # Not snake_case
```

### 2. Schema Validation

Always validate inputs thoroughly:

```python
@mcp_tool(
    name="safe_file_reader",
    schema={
        "parameters": {
            "properties": {
                "file_path": {
                    "type": "string",
                    "pattern": "^[^/\\\\]+\\.txt$",  # Only .txt files
                    "description": "Path to text file (no directories)"
                }
            }
        }
    }
)
def read_safe_file(file_path: str) -> str:
    # Additional validation
    if ".." in file_path or "/" in file_path:
        raise ValueError("Invalid file path")
    
    # Safe to read
    with open(file_path, 'r') as f:
        return f.read()
```

### 3. Error Handling

Provide clear error messages:

```python
@mcp_tool(name="divide_numbers")
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    
    result = a / b
    
    if math.isnan(result) or math.isinf(result):
        raise ValueError(f"Invalid result: {result}")
    
    return result
```

### 4. Documentation

Include comprehensive documentation:

```python
@mcp_tool(
    name="generate_report",
    description="Generate a formatted report from data",
    schema={
        "parameters": {
            "properties": {
                "data": {
                    "type": "array",
                    "description": "Array of data points to include in report"
                },
                "format": {
                    "type": "string",
                    "description": "Output format for the report",
                    "enum": ["pdf", "html", "markdown"],
                    "default": "markdown"
                },
                "include_charts": {
                    "type": "boolean",
                    "description": "Whether to include visual charts",
                    "default": False
                }
            }
        }
    },
    examples=[
        {
            "input": {"data": [1, 2, 3], "format": "html"},
            "output": "<html>...</html>"
        }
    ]
)
def generate_report(data: list, format: str = "markdown", 
                   include_charts: bool = False) -> str:
    """
    Generate a formatted report from the provided data.
    
    Args:
        data: List of data points to analyze
        format: Output format (pdf, html, markdown)
        include_charts: Whether to generate charts
        
    Returns:
        Formatted report as string
        
    Raises:
        ValueError: If data is empty or format is unsupported
    """
    # Implementation
    pass
```

### 5. Performance Considerations

For resource-intensive tools:

```python
@mcp_tool(
    name="process_large_dataset",
    metadata={
        "timeout": 300,  # 5 minutes
        "memory_limit": "2GB",
        "cpu_intensive": True
    }
)
async def process_dataset(dataset_id: str) -> dict:
    # Use async for I/O operations
    data = await fetch_dataset(dataset_id)
    
    # Process in chunks for memory efficiency
    results = []
    for chunk in chunked(data, 1000):
        result = await process_chunk(chunk)
        results.append(result)
    
    return {"processed": len(results), "status": "complete"}
```

## Testing MCP Tools

### Unit Testing

```python
import pytest
from ergon.core.repository.mcp import get_tool, execute_tool

def test_analyze_code_tool():
    # Test registration
    tool = get_tool("analyze_code")
    assert tool is not None
    assert tool["name"] == "analyze_code"
    
    # Test execution
    result = execute_tool(
        "analyze_code",
        code="def test(): pass",
        language="python"
    )
    assert "issues" in result
    assert result["language"] == "python"

def test_invalid_parameters():
    with pytest.raises(ValueError):
        execute_tool(
            "analyze_code",
            code="test",
            language="unsupported_language"
        )
```

### Integration Testing

```python
async def test_tool_with_hermes():
    # Register tool
    register_tool(...)
    
    # Verify discovery via Hermes
    hermes = HermesClient()
    components = hermes.discover_components(capability="mcp_tools")
    
    assert any(c["tools"].get("my_tool") for c in components)
```

## Troubleshooting

### Common Issues

#### Tool Not Found
```python
# Check if tool is registered
from ergon.core.repository.mcp import get_registered_tools

tools = get_registered_tools()
if "my_tool" not in tools:
    print("Tool not registered!")
    
# Check for typos
print(f"Available tools: {list(tools.keys())}")
```

#### Schema Validation Errors
```python
# Debug schema issues
try:
    execute_tool("my_tool", **params)
except ValueError as e:
    print(f"Validation error: {e}")
    
    # Check schema
    tool = get_tool("my_tool")
    print(f"Expected schema: {tool['schema']}")
```

#### Performance Issues
```python
# Profile tool execution
import time

start = time.time()
result = execute_tool("slow_tool", **params)
duration = time.time() - start

if duration > 5.0:
    print(f"Tool took {duration:.2f}s - consider optimization")
```

## Advanced Topics

### Dynamic Tool Generation

Create tools programmatically:

```python
def create_api_tool(endpoint: str, method: str = "GET"):
    @mcp_tool(
        name=f"api_{endpoint.replace('/', '_')}",
        description=f"Call {method} {endpoint}"
    )
    def api_caller(**params):
        import requests
        response = requests.request(method, endpoint, **params)
        return response.json()
    
    return api_caller

# Generate tools for multiple endpoints
for endpoint in ["/users", "/posts", "/comments"]:
    tool = create_api_tool(endpoint)
    # Tool is automatically registered
```

### Tool Composition

Combine multiple tools:

```python
@mcp_tool(name="analyze_and_fix_code")
def analyze_and_fix(code: str, language: str) -> dict:
    # First analyze
    analysis = execute_tool(
        "analyze_code",
        code=code,
        language=language
    )
    
    # Then fix issues
    if analysis["issues"]:
        fixed_code = execute_tool(
            "auto_fix_code",
            code=code,
            issues=analysis["issues"]
        )
        return {"original": code, "fixed": fixed_code}
    
    return {"original": code, "fixed": code}
```

### Tool Versioning

Support multiple versions:

```python
@mcp_tool(
    name="process_data",
    version="2.0.0",
    deprecated_versions=["1.0.0", "1.5.0"]
)
def process_data_v2(data: dict) -> dict:
    # New implementation
    pass

# Maintain backward compatibility
@mcp_tool(
    name="process_data_v1",
    version="1.0.0",
    deprecated=True,
    deprecation_message="Use process_data v2.0.0"
)
def process_data_v1(data: dict) -> dict:
    # Old implementation
    pass
```

## Related Documentation

- [Ergon Component Documentation](/MetaData/ComponentDocumentation/Ergon/README.md)
- [Component Integration Patterns](/MetaData/TektonDocumentation/Guides/ComponentIntegrationPatterns.md)
- [API Development Guide](/MetaData/TektonDocumentation/Guides/APIDevelopment.md)
- [Testing Best Practices](/MetaData/TektonDocumentation/Guides/TestingGuide.md)