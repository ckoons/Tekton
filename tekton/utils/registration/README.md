# Tekton Component Registration Utilities

## Overview

This library provides utilities for registering Tekton components with the Hermes service registry. It loads component configurations from YAML files and handles registration, heartbeat, and unregistration.

## Usage

### Command-Line Interface

The `tekton-register` command-line tool simplifies component registration:

```bash
# Register a component
tekton-register register --component rhetor

# Check registration status
tekton-register status --component rhetor

# Generate a template configuration
tekton-register generate --component my-component --port 8123 --output my-component.yaml

# List all registered components
tekton-register list

# Unregister a component
tekton-register unregister --component rhetor
```

### Python API

```python
import asyncio
from tekton.utils.registration import (
    load_component_config,
    register_component,
    unregister_component,
    get_registration_status
)

async def main():
    # Load component configuration
    config = load_component_config("rhetor")
    
    # Register component
    success, client = await register_component("rhetor", config)
    
    if success:
        print("Component registered successfully")
        
        # Use the client for other operations
        await client.heartbeat()
        
        # When done, unregister and close the client
        await client.unregister()
        await client.close()
    else:
        print("Failed to register component")

# Run the main function
asyncio.run(main())
```

## Component Configuration

Components are configured using YAML files with the following structure:

```yaml
component:
  id: component_id
  name: Component Name
  version: 0.1.0
  description: Component description
  port: 8000

capabilities:
  - id: capability_id
    name: Capability Name
    description: Capability description
    methods:
      - id: method_id
        name: Method Name
        description: Method description
        parameters:
          - name: param_name
            type: string
            required: true
            description: Parameter description
        returns:
          type: object
          description: Return description

config:
  key: value
```

## Configuration Resolution

The library searches for component configuration files in the following locations:

1. Current directory: `component_id.yaml` or `component_id.yml`
2. Tekton configuration directory: `$TEKTON_ROOT/config/components/component_id.yaml`
3. Component directory: `$TEKTON_ROOT/component_id/component_id.yaml`
4. Component configuration directory: `$TEKTON_ROOT/component_id/config/component_id.yaml`

## Heartbeat Management

The registration client automatically sends heartbeats to keep the component registration active:

```python
# Register with heartbeat
success, client = await register_component("component_id", config, start_heartbeat=True)

# Control heartbeat manually
await client.start_heartbeat(interval=30)  # Send heartbeat every 30 seconds
await client.stop_heartbeat()
```

## Environment Variables

- `HERMES_URL`: URL of the Hermes API (defaults to `http://localhost:8001/api`)
- `TEKTON_ROOT`: Path to the Tekton directory (used for configuration resolution)

## Error Handling

The library provides detailed error messages for common issues:

- Configuration file not found
- Invalid configuration format
- Connection errors to Hermes
- Registration failures
- Component not found

## Integration with Component Scripts

To integrate with component scripts, add the following to your component's startup script:

```bash
#!/bin/bash

# Register component with Hermes
tekton-register register --component my-component &
REGISTER_PID=$!

# Your component startup code here
# ...

# Trap SIGTERM and SIGINT to unregister component
trap "tekton-register unregister --component my-component; exit" SIGTERM SIGINT

# Wait for component to finish
wait
```