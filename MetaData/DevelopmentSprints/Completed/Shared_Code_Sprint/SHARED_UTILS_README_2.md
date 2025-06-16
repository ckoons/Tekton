# Tekton Shared Utilities

## Overview

Tekton Shared Utilities provide a set of standardized, reusable components that ensure consistent behavior across the Tekton ecosystem. This implementation includes shell utilities, component registration, and enhanced LLM client functionality.

## Key Components

### 1. Shell Utilities

Located in `/scripts/lib/`:

- **tekton-utils.sh**: Core functions for logging, directory detection, and common operations
- **tekton-ports.sh**: Port management following the Single Port Architecture
- **tekton-process.sh**: Process management for starting, stopping, and monitoring components
- **tekton-config.sh**: Configuration management from environment variables and files

### 2. Component Registration

A unified system for registering components with the Hermes service registry:

- **tekton-register**: Command-line utility for component registration
- **YAML configuration**: Standardized format for defining component capabilities
- **Component directory**: All component configurations stored in `/config/components/`

### 3. Enhanced LLM Client

A comprehensive client for interacting with LLMs through Rhetor:

- **Prompt templates**: Standardized system for managing and rendering templates
- **Response handlers**: Utilities for parsing different output formats
- **Configuration management**: Settings and environment variable utilities

## Usage Examples

### Shell Utilities

```bash
#!/bin/bash

# Source utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/tekton-utils.sh"
source "${SCRIPT_DIR}/../lib/tekton-ports.sh"

# Use logging functions
tekton_info "Starting component..."
tekton_success "Component started successfully"

# Check port availability
if tekton_is_port_used 8080; then
    tekton_warn "Port 8080 is already in use"
    tekton_release_port 8080 "My Component"
fi

# Get standard port
PORT=$(tekton_get_component_port "my-component")
```

### Component Registration

```bash
# Register a component
tekton-register register --component my-component

# Check status
tekton-register status --component my-component

# Generate a template configuration
tekton-register generate --component my-component --output my-component.yaml

# Unregister
tekton-register unregister --component my-component
```

### Enhanced LLM Client

```python
import asyncio
from tekton_llm_client import (
    TektonLLMClient, 
    PromptTemplateRegistry, 
    parse_json,
    StructuredOutputParser, 
    OutputFormat
)

async def main():
    # Initialize client
    client = TektonLLMClient(component_id="my-component")
    await client.initialize()
    
    # Use prompt templates
    registry = PromptTemplateRegistry()
    prompt = registry.render(
        "code_review",
        language="python",
        code="def hello(): pass",
        focus_area="best practices"
    )
    
    # Generate and parse response
    response = await client.generate_text(prompt=prompt)
    data = parse_json(response.content)
    
    # Clean up
    await client.shutdown()

asyncio.run(main())
```

## New Features in LLM Client

### Prompt Templates

```python
from tekton_llm_client import PromptTemplateRegistry, PromptTemplate

# Create a registry
registry = PromptTemplateRegistry()

# Register a custom template
registry.register({
    "name": "api_design",
    "template": "Design a REST API for {{ service_name }}:\n{{ requirements }}",
    "description": "Template for API design tasks"
})

# Render with variables
prompt = registry.render(
    "api_design",
    service_name="User Management",
    requirements="- User registration\n- Login\n- Profile management"
)
```

### Response Handlers

```python
from tekton_llm_client import (
    parse_json, 
    StructuredOutputParser, 
    OutputFormat,
    StreamHandler
)

# Parse JSON
data = parse_json("```json\n{\"key\": \"value\"}\n```")

# Parse structured formats
parser = StructuredOutputParser(format=OutputFormat.LIST)
items = parser.parse("1. First item\n2. Second item\n3. Third item")

# Handle streaming
async def process_stream():
    stream = client.generate_text(prompt="Write a story", streaming=True)
    handler = StreamHandler()
    result = await handler.process_stream(stream)
    print(f"Complete text: {result}")
```

### Configuration

```python
from tekton_llm_client.config import (
    get_env, 
    load_settings, 
    ClientSettings, 
    LLMSettings
)

# Environment variables
debug = get_env_bool("DEBUG", default=False)

# Load settings
settings = load_settings(
    component_id="my-component",
    file_path="/path/to/settings.json",
    load_from_env=True
)

# Create settings
my_settings = ClientSettings(
    component_id="my-component",
    llm=LLMSettings(
        provider="anthropic",
        model="claude-3-haiku-20240307"
    )
)
```

## Migration Guide

To migrate existing components to use these shared utilities:

1. **Shell Utilities**:
   - Source the shared libraries at the top of your scripts
   - Replace custom logging and utility functions with the shared ones

2. **Component Registration**:
   - Create a YAML configuration file in `/config/components/`
   - Update your startup script to use `tekton-register`
   - Remove your custom `register_with_hermes.py` script

3. **LLM Integration**:
   - Update to use the `tekton_llm_client` package
   - Replace custom prompt templates with the shared system
   - Use the response handlers for parsing LLM outputs

You can use the `update-component-registration.sh` script to automate part of this process:

```bash
scripts/bin/update-component-registration.sh
```

## Documentation

For more detailed information, see:

- **COMPONENT_LIFECYCLE.md**: Component lifecycle and registration
- **SHARED_COMPONENT_UTILITIES.md**: Detailed usage of all shared utilities
- **tekton-llm-client/README.md**: Documentation for the LLM client

## Examples

See the `examples/` directory for complete examples of using these shared utilities.