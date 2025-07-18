# Tekton Component Lifecycle

This document describes the lifecycle of Tekton components, including initialization, registration, startup, shutdown, and health monitoring.

## Overview

Tekton components follow a standardized lifecycle to ensure consistent behavior and proper integration with the ecosystem. This includes registration with the Hermes service registry, handling of startup and shutdown events, and health monitoring.

## Component Lifecycle Phases

1. **Initialization**: Loading configuration and preparing resources
2. **Registration**: Registering with the Hermes service registry
3. **Startup**: Starting the component's services
4. **Running**: Normal operation of the component
5. **Shutdown**: Graceful termination of the component's services
6. **Unregistration**: Unregistering from the Hermes service registry

## Standardized Registration

Tekton components register with the Hermes service registry using the `tekton-register` utility, which provides a standardized interface for component registration.

### Component Configuration (YAML)

Each component has a YAML configuration file in the `/config/components/` directory that defines its capabilities and methods:

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

### Registration Process

1. **Configuration Loading**: The component loads its configuration from a YAML file.
2. **Validation**: The configuration is validated for correctness.
3. **Registration**: The component registers with Hermes using the `tekton-register` utility.
4. **Heartbeat**: The component starts sending periodic heartbeats to keep the registration active.

### Example Registration Script

```bash
#!/bin/bash

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/tekton-utils.sh"

# Register with Hermes
tekton-register register --component my-component --config "${SCRIPT_DIR}/../config/components/my-component.yaml" &
REGISTER_PID=$!

# Start the component...

# Trap signals to ensure proper shutdown
trap "tekton-register unregister --component my-component; exit" SIGTERM SIGINT

# Wait for the component to finish
wait
```

## Health Monitoring

Components should implement a health check endpoint that can be used to monitor their status. The standard endpoint is `/health` on the component's port.

```python
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

The `tekton-status` script uses these health checks to monitor the status of all components.

## Startup Sequence

Components should follow this startup sequence:

1. **Parse Arguments**: Parse command-line arguments and environment variables.
2. **Load Configuration**: Load configuration from files and environment variables.
3. **Initialize Resources**: Initialize databases, connections, and other resources.
4. **Register with Hermes**: Register the component with the Hermes service registry.
5. **Start Services**: Start the component's services.
6. **Report Status**: Log the successful startup of the component.

## Shutdown Sequence

Components should follow this shutdown sequence:

1. **Receive Signal**: Handle SIGTERM or SIGINT signals.
2. **Stop Services**: Stop the component's services gracefully.
3. **Release Resources**: Close connections and release resources.
4. **Unregister from Hermes**: Unregister the component from the Hermes service registry.
5. **Report Status**: Log the successful shutdown of the component.

## Lifecycle Management with Hermes

Hermes provides lifecycle management for Tekton components, including:

1. **Registration**: Components register with Hermes to register their capabilities.
2. **Heartbeat**: Components send periodic heartbeats to keep their registration active.
3. **Discovery**: Other components can discover registered components through Hermes.
4. **Shutdown**: Hermes can initiate graceful shutdown of components.

## Single Port Architecture

Tekton uses a Single Port Architecture for all components, which means:

1. Each component uses a single port for all communication methods
2. Different protocols are handled through different URL paths:
   - `/api/` for HTTP API endpoints
   - `/ws/` for WebSocket connections
   - `/events/` for event-based communication

This simplifies component deployment and configuration, as only one port needs to be managed for each component.

## Implementation Guidelines

1. **Use Standardized Registration**: Use the `tekton-register` utility for registration.
2. **Implement Health Checks**: Implement a `/health` endpoint for monitoring.
3. **Handle Signals**: Handle SIGTERM and SIGINT signals for graceful shutdown.
4. **Resource Management**: Properly initialize and release resources.
5. **Error Handling**: Implement proper error handling for all lifecycle phases.
6. **Logging**: Log all lifecycle events for debugging and monitoring.
7. **Single Port**: Follow the Single Port Architecture pattern.

## Integration with tekton-launch and tekton-kill

The `tekton-launch` and `tekton-kill` scripts manage the lifecycle of multiple components:

1. **tekton-launch**:
   - Detects available components
   - Releases ports if needed
   - Starts components in the correct order
   - Registers components with Hermes

2. **tekton-kill**:
   - First attempts to use Hermes for graceful shutdown
   - Falls back to direct process termination if needed
   - Releases ports used by components
   - Ensures all components are properly shut down

## Component Dependencies

Components should define their dependencies in the configuration file to ensure proper startup order. Hermes will ensure that dependencies are available before starting dependent components.

## Migration from Legacy Registration

Legacy components that use individual `register_with_hermes.py` scripts should be migrated to the new registration system using the `update-component-registration.sh` script:

```bash
scripts/bin/update-component-registration.sh
```

This will:
1. Create or update YAML configuration files for components
2. Update startup scripts to use `tekton-register`
3. Create symlinks in ~/utils for easy access to shared utilities

### Manual Migration Steps

1. Create a YAML configuration file for the component in `/config/components/`
2. Update the startup script to use `tekton-register`
3. Remove the old `register_with_hermes.py` script

## Examples

See the `examples` directory for complete examples of implementing the component lifecycle using the shared utilities.